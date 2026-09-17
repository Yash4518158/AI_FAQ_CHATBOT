from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.connection import get_db, test_connection
from app.auth.routes import router as auth_router
from app.faqs.routes import router as faqs_router
from app.conversations.routes import router as conversations_router
from app.database.connection import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI FAQ Chatbot API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(faqs_router)
app.include_router(conversations_router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify backend and database status."""
    db_status = test_connection(db)
    return {
        "status": "healthy",
        "database": db_status
    }
