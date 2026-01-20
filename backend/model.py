from sqlalchemy import Column,ForeignKey,DateTime,Text,String,Integer
from sqlalchemy import UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__='users'

    id =Column(Integer, primary_key=True,index=True)
    username=Column(String,unique=True,nullable=False,index=True)
    hashed_password=Column(String)
    created_at=Column(DateTime,default=datetime.utcnow)

class ChatSession(Base):
    __tablename__='chat_sessions'

    id=Column(Integer, primary_key=True,index=True)
    user_id=Column(Integer, ForeignKey("users.id"),nullable=False)
    title=Column(String(255))
    db_id=Column(Integer,ForeignKey("database_connections.id"))
    created_at=Column(DateTime,default=datetime.utcnow)

    messages=relationship("ChatMessage",back_populates='session',cascade="all, delete")

class ChatMessage(Base):
    __tablename__="chat_messages"

    id=Column(Integer,primary_key=True,index=True)
    session_id=Column(Integer,ForeignKey("chat_sessions.id"),nullable=False)
    role=Column(String(20))
    content=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)
    session=relationship("ChatSession",back_populates='messages')

class DatabaseConnection(Base):
    __tablename__="database_connections"

    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey("users.id"))

    name =Column(String,nullable=False)
    dialect=Column(String,nullable=False)
    connection_uri_enc = Column(Text, nullable=False)
    connection_uri_hash = Column(String(64), nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "connection_uri_hash", name="uq_user_connection"),
    )


