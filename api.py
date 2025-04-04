from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI News Warehouse API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/news")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ChromaDB setup
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="chroma_db"
))

# Database Models
class NewsSummary(Base):
    __tablename__ = "news_summaries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text)
    topic = Column(String, index=True)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class RawNews(BaseModel):
    title: str
    content: str
    source: str
    topic: str

class NewsSummaryCreate(BaseModel):
    title: str
    content: str
    summary: str
    topic: str
    source: str

class NewsSummaryResponse(NewsSummaryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/news/raw", response_model=dict)
async def receive_raw_news(news: RawNews, db: Session = Depends(get_db)):
    """Endpoint to receive raw news data from fetch_news.py"""
    try:
        # Store raw news data temporarily
        db_news = NewsSummary(
            title=news.title,
            content=news.content,
            source=news.source,
            topic=news.topic
        )
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        
        return {
            "message": "Raw news received successfully",
            "id": db_news.id,
            "status": "pending_summary"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing raw news: {str(e)}")

@app.post("/news/summarize/{news_id}", response_model=NewsSummaryResponse)
async def receive_summary(news_id: int, summary: str, db: Session = Depends(get_db)):
    """Endpoint to receive summary from summarize.py"""
    try:
        news = db.query(NewsSummary).filter(NewsSummary.id == news_id).first()
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
        
        news.summary = summary
        db.commit()
        db.refresh(news)
        
        # Store in ChromaDB
        collection = chroma_client.get_or_create_collection(name="news_summaries")
        collection.add(
            documents=[summary],
            metadatas=[{"id": str(news.id), "topic": news.topic}],
            ids=[str(news.id)]
        )
        
        return news
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing summary: {str(e)}")

@app.get("/summaries", response_model=List[NewsSummaryResponse])
async def get_summaries(
    topic: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Retrieve stored summaries with optional filtering"""
    try:
        query = db.query(NewsSummary)
        
        if topic:
            query = query.filter(NewsSummary.topic == topic)
        if start_date:
            query = query.filter(NewsSummary.created_at >= start_date)
        if end_date:
            query = query.filter(NewsSummary.created_at <= end_date)
        
        return query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summaries: {str(e)}")

@app.get("/query")
async def query_summaries(
    query: str,
    n_results: int = 5,
    db: Session = Depends(get_db)
):
    """Search summaries using semantic search"""
    try:
        collection = chroma_client.get_collection(name="news_summaries")
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        summary_ids = [int(id) for id in results['ids'][0]]
        summaries = db.query(NewsSummary).filter(NewsSummary.id.in_(summary_ids)).all()
        
        return {
            "query": query,
            "results": [
                {
                    "id": summary.id,
                    "title": summary.title,
                    "summary": summary.summary,
                    "topic": summary.topic,
                    "created_at": summary.created_at
                }
                for summary in summaries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
