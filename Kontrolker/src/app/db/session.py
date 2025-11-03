# src_app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 👇 para dev
SQLALCHEMY_DATABASE_URL = "sqlite:///./kontrolker.db"
# si lo corres desde otro directorio, quizá quieras: "sqlite:///src_app/kontrolker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # 👈 necesario en SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
