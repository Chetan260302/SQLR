from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from response_formatter import format_static_response
from chat_utils import save_assistant_message
from sqlalchemy import inspect
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pyodbc
import re



from database import Base,AuthSessionLocal,auth_engine
from model import User,ChatMessage,ChatSession,DatabaseConnection
from auth_utils import get_current_user,create_access_token,verify_password,hash_password,encrypt,decrypt,hash_uri
from llm_utils import generate_answer,generate_sql,execute_sql,repair_sql,prune_schema,generate_answer_stream,generate_chat_title_llm
from db_utils import get_database_schema
from schema_cache import get_schema_for_db
from sql_validator import validate_sql
from semantic_guard import sql_matches_question
from schema_trimmer import trim_schema_for_prompt
from sql_metadata import extract_sql_metadata

Base.metadata.create_all(bind=auth_engine)

load_dotenv()
app=FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    llm=ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
    )

    # llm=ChatOllama(
    #     model="qwen2.5-coder:7b-instruct-q4_K_M",
    #     temperature=0,
    #     num_ctx=4096, # Reduce from default 8192 to 2048
    #     num_gpu=20
    # )
except Exception as e:
    raise RuntimeError(f"startup failed: {e}")

def get_auth_db():
    db = AuthSessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    question:str

class ChatResponse(BaseModel):
    answer:str

# @app.post('/chatbot',response_model=ChatResponse)
# def chat(request:ChatRequest,user_id:int=Depends(get_current_user)):

#     try:
#         response=agent_executor.invoke(
#             {"input":request.question}
#         )
#         return {"answer":response["output"]}
#     except Exception as e:
#         raise HTTPException(status_code=500,detail="Failed to process query")
    
# @app.post('/chatbot/stream')
# def chat_stream(request: ChatRequest,user_id:int=Depends(get_current_user)):
#     if not request.question.strip():
#         raise HTTPException(status_code=400,detail="Question cannot be empty")
#     def event_generator() -> Generator[str,None,None]:
#         try:
#             for chunk in agent_executor.stream(
#                 {"input":request.question}
#             ):
#                 print("degbug chunk:", chunk)
                
#                 if 'output' in chunk:
#                     yield chunk['output']
#         except Exception:
#             yield "\n[Error generating response]"

#     return StreamingResponse(
#         event_generator(),
#         media_type="text/plain"
#     )


class SignupRequest(BaseModel):
    username:str
    password:str
    confirm_password:str

class LoginRequest(BaseModel):
    username:str
    password:str
    

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"

@app.post("/auth/signup")
def signup(user: SignupRequest, db: Session = Depends(get_auth_db)):

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


from fastapi.security import OAuth2PasswordRequestForm

@app.post('/auth/login',response_model=TokenResponse)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_auth_db)):
    
    db_user=db.query(User).filter(User.username==form_data.username).first()
    if not db_user or not verify_password(form_data.password,db_user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    token=create_access_token({"sub":db_user.username,"user":str(db_user.id)})

    return{
        "access_token":token,
        "token_type":"bearer",
        "username":db_user.username
    }

class DatabaseCreate(BaseModel):
    name:str
    dialect:str
    connection_uri:str

@app.post('/databases')
def add_database(
    body:DatabaseCreate,
    db:Session=Depends(get_auth_db),
    user_id:int=Depends(get_current_user)
):
    uri_hash=hash_uri(body.connection_uri)
    encrypted_uri=encrypt(body.connection_uri)

    existing=(db.query(DatabaseConnection)
              .filter(
                  DatabaseConnection.user_id==user_id,
                  DatabaseConnection.connection_uri_hash==uri_hash
              ).first()
            )
    
    if existing:
        existing.name=body.name
        existing.dialect=body.dialect
        existing.connection_uri_enc=encrypted_uri
        db.commit()
        db.refresh(existing)

        return{
            "id":existing.id,
            "name":existing.name,
            "dialect":existing.dialect,
            "updated":True
        }
    
    db_conn=DatabaseConnection(
        user_id=user_id,
        name=body.name,
        dialect=body.dialect,
        connection_uri_enc=encrypted_uri,
        connection_uri_hash=uri_hash
    )

    db.add(db_conn)
    db.commit()
    return {"id":db_conn.id,"name":db_conn.name}

@app.get("/databases")
def list_databases(db:Session=Depends(get_auth_db),user_id:int=Depends(get_current_user)):
    dbs=db.query(DatabaseConnection).filter(DatabaseConnection.user_id==user_id).order_by(DatabaseConnection.created_at.desc()).all()

    return [
        {
            "id":d.id,
            "name":d.name,
            "dialect":d.dialect
        }
        for d in dbs
    ]
class CreateSessionRequest(BaseModel):
    db_id:int


@app.post("/chat/sessions")
def create_session(
    body: CreateSessionRequest,
    db: Session = Depends(get_auth_db),
    user_id: int = Depends(get_current_user),
):
    db_conn = (
        db.query(DatabaseConnection)
        .filter(
            DatabaseConnection.id == body.db_id,
            DatabaseConnection.user_id == user_id
        )
        .first()
    )
    if not db_conn:
        raise HTTPException(status_code=404, detail="Database not found")

    session = ChatSession(
        user_id=user_id,
        db_id=body.db_id,
        title=None,   # IMPORTANT
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def build_chat_title(
    dialect: str,
    db_name: str,
    first_question: str,
    llm_title: str | None = None,
) -> str:
    base = llm_title or first_question
    base = base.strip().replace("\n", " ")[:60]
    return f"[{dialect.upper()}] {db_name} — {base}"


@app.get('/chat/sessions')
def list_sessions(db:Session=Depends(get_auth_db),user_id:int=Depends(get_current_user)):
    sessions=db.query(ChatSession).filter(ChatSession.user_id==user_id).order_by(ChatSession.created_at.desc()).all()
    return sessions

class ChatMessageRequest(BaseModel):
    message:str

@app.post('/chat/{session_id}/messages')
def chat_message(session_id:int,request:ChatMessageRequest,auth_db:Session=Depends(get_auth_db),user_id:int=Depends(get_current_user)):
    chat_session=auth_db.query(ChatSession).filter(ChatSession.id==session_id,ChatSession.user_id==user_id).first()

    print("STEP 1: entered endpoint")
    if not chat_session:
        raise HTTPException(status_code=404,detail="Chat session not found")


    user_msg=ChatMessage(session_id=session_id,role="user",content=request.message)
    print("STEP 2: session OK")
    auth_db.add(user_msg)
    auth_db.commit()

    print("STEP 3: user message saved")

    #Get db schema dynamically
    db_conn = (
        auth_db.query(DatabaseConnection)
        .filter(
            DatabaseConnection.id == chat_session.db_id,
            DatabaseConnection.user_id == user_id
        )
        .first()
    )

    # after saving user message
    if chat_session.title is None:
        llm_title = generate_chat_title_llm(llm, request.message)

        chat_session.title = build_chat_title(
            dialect=db_conn.dialect,
            db_name=db_conn.name,
            first_question=request.message,
            llm_title=llm_title,
        )

        auth_db.commit()

    if not db_conn:
        raise HTTPException(status_code=404, detail="Database not found")
    
    connection_uri=decrypt(db_conn.connection_uri_enc)
    engine=create_engine(connection_uri)
    dialect=engine.dialect.name

    print("STEP 4: engine OK", engine,dialect)
    cache_key = f"db:{db_conn.connection_uri_hash}"
    full_schema = get_schema_for_db(cache_key=cache_key, engine=engine)
    # schema=get_schema_for_db(db_id=chat_session.db_id,engine=engine)
    print("STEP 5: schema extracted",full_schema)

    trimmed_schema = trim_schema_for_prompt(
        full_schema=full_schema,
        user_question=request.message,
        max_tables=15
    )

    print("STEP 5A: trimmed schema", trimmed_schema)

    pruned_schema=prune_schema(
        llm=llm,
        full_schema=trimmed_schema,
        question=request.message
    )

    def single_message_stream(message: str):
        def gen():
            yield message
        return StreamingResponse(gen(), media_type="text/plain")

    print("its working",pruned_schema)
    #generate sql
    try:
        sql=generate_sql(llm=llm,schema=pruned_schema,question=request.message,dialect=dialect)
        print("STEP 6: sql generated", sql)
    except Exception as e:
        print("sql generation failed:",sql,repr(e))
        answer=("I couldn't understand your question well enough to "
                "generate a database query. Please rephrase it.")
        save_assistant_message(auth_db, session_id, answer)

        return single_message_stream(answer)
   
    metadata=extract_sql_metadata(sql=sql,dialect=db_conn.dialect)

    response_meta = {
        "type": "meta",
        "session_title": chat_session.title,
        "database": {
            "name": db_conn.name,
            "dialect": dialect,
        },
        "tables": metadata["tables"],
        "columns": metadata["columns"],
        "sql": sql,
    }

    # after SQL generation
    try:
        validate_sql(sql)
    except ValueError as e:
        answer = (
            "I generated a query that does not match the database schema. "
            "Please try rephrasing your question."
        )

        save_assistant_message(auth_db, session_id, answer)

        return single_message_stream(answer)
    #execute sql
    try:
        columns,rows=execute_sql(engine,sql)
        print("step 7: columns and rows :",columns,rows,sql)
    except Exception as e:
        try:
            repaired_sql=repair_sql(
                llm=llm,
                schema=pruned_schema,
                dialect=dialect,
                sql=sql,
                error=str(e),
                question=request.message
            )
            if repaired_sql.strip()=="SELECT 'NOT_ANSSWERABLE';":
                raise ValueError("Not asnwerable")
            
            validate_sql(repaired_sql)
            columns,rows=execute_sql(engine,repaired_sql)
            sql=repaired_sql
        except Exception:
            print("SQL EXECUTION ERROR:", e)
            answer = (
                "I couldn't run this query on the database. "
                "This usually happens when the question requires "
                "unsupported operations or incompatible SQL syntax.\n\n"
                f"SQL used:\n```sql\n{sql}"
            )

        save_assistant_message(auth_db, session_id, answer)

        return single_message_stream(answer)

    
    if not rows or rows == [(None,)]:
        answer= ("There is no data available in the database.\n\n"
                f"SQL Query:\n```sql\n{sql}"
        )
        save_assistant_message(auth_db, session_id, answer)
        return single_message_stream(answer)
        
    if rows == [("NOT_ANSWERABLE",)]:
        answer=( "I can't answer that question using the available database."
                f"SQL Query:\n```sql\n{sql}"
        )
        save_assistant_message(auth_db, session_id, answer)
        return single_message_stream(answer)

    # def qualify_columns(columns, tables):
    #     if len(tables) == 1:
    #         table = tables[0]
    #         return [f"{table}.{c}" for c in columns]
    #     return list(columns)
    # def extract_tables_from_sql(sql: str):
        
    #     return list(set(
    #         re.findall(r"(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql.lower())
    #     ))
    # tables = extract_tables_from_sql(sql)
    # qualified_columns=qualify_columns(columns,tables)
    
    MAX_ROWS = 10
    total_rows = len(rows)

    display_rows = rows[:MAX_ROWS]

    static_part = format_static_response(
        db_name=db_conn.name,
        dialect=dialect,
        sql=sql,
        tables=metadata["tables"],
        columns=columns,
        rows=display_rows,
        total_rows=total_rows
    )


    has_rows = bool(rows) and display_rows != [(None,)]
    import json
    def event_generator():
        explanation_chunks = []

        yield "__META__" + json.dumps({
            "session_title": chat_session.title
        }) + "__END_META__"

        # send static part immediately
        yield static_part.rstrip() + "\n\n"

        # 🚨 HARD GUARD
        if not has_rows:
            final_answer = static_part
            save_assistant_message(auth_db, session_id, final_answer)
            return
        # stream explanation
        for token in generate_answer_stream(
            llm=llm,
            question=request.message,
            columns=columns,
            rows=display_rows
        ):
            explanation_chunks.append(token)
            yield token

        # save full answer after streaming completes
        final_answer = static_part.rstrip() + "\n\n" + "".join(explanation_chunks).lstrip()
        save_assistant_message(auth_db, session_id, final_answer)
    
    print(
        "DEBUG:",
        "db_id =", chat_session.db_id,
        "uri =", connection_uri
    )
    print("Generated SQL:\n", sql)
    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )

@app.get('/chat/{session_id}/messages')
def get_messages(session_id:int,db: Session = Depends(get_auth_db),user_id:int=Depends(get_current_user)):
    session=db.query(ChatSession).filter(ChatSession.id==session_id,ChatSession.user_id==user_id).first()
    if not session:
        raise HTTPException(status_code=404,detail='Not found')
    messages=db.query(ChatMessage).filter(ChatMessage.session_id==session_id).order_by(ChatMessage.created_at).all()
    return messages

@app.delete("/chat/sessions/{session_id}")
def delete_session(
    session_id:int,
    db:Session=Depends(get_auth_db),
    user_id:int=Depends(get_current_user)
):
    session=(
        db.query(ChatSession).filter(ChatSession.id==session_id,ChatSession.user_id==user_id).first()
    )

    if not session:
        raise HTTPException(status_code=404,detail="Session not found")
    
    db.query(ChatMessage).filter(ChatMessage.session_id==session_id).delete()
    db.delete(session)
    db.commit()

    return {"success":True}


def auto_title(text:str,max_words:int=6)->str:
    words=text.strip().split()
    title=" ".join(words[:max_words])
    return title[:60]

@app.post("/databases/test")
def test_database(
    body:DatabaseCreate,
    user_id:int=Depends(get_current_user)
):
    try:
        engine=create_engine(body.connection_uri)
        with engine.connect() as conn:
            conn.execute(text("Select 1"))
        return {"ok":True}
    except SQLAlchemyError as e:
        return {
            "ok":False,
            "error":f"{type(e).__name__}: {str(e)}"
        }
