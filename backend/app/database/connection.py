import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback for local non-docker testing or default docker compose setup
    DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/faq_chatbot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection(db):
    try:
        db.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        return f"error: {str(e)}"
