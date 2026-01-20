from sqlalchemy import create_engine, Column, Integer,String
from sqlalchemy.orm import sessionmaker, declarative_base

AUTH_DATABASE_URL="sqlite:///data/auth.db"

auth_engine=create_engine(AUTH_DATABASE_URL,connect_args={'check_same_thread':False})

AuthSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=auth_engine)
Base=declarative_base()

