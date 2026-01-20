from model import ChatMessage

def save_assistant_message(db, session_id: int, content: str):
    msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=content
    )
    db.add(msg)
    db.commit()
