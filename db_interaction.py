import os
import asyncpg
from datetime import datetime
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from config import APIConfig

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = APIConfig()
        self.pool = None

    async def connect(self):
        """Create a connection pool to the database"""
        try:
            self.pool = await asyncpg.create_pool(
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME,
                host=self.config.DB_HOST,
                port=self.config.DB_PORT
            )
            print("Successfully connected to the database")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            print("Database connection closed")

    async def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS news_articles (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS article_summaries (
                        id SERIAL PRIMARY KEY,
                        article_id INTEGER REFERENCES news_articles(id),
                        summary TEXT NOT NULL,
                        insights TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX IF NOT EXISTS idx_news_articles_topic ON news_articles(topic);
                    CREATE INDEX IF NOT EXISTS idx_news_articles_created_at ON news_articles(created_at);
                    CREATE INDEX IF NOT EXISTS idx_article_summaries_article_id ON article_summaries(article_id);
                """)
                print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    async def store_article(self, article: Dict[str, Any]) -> int:
        """Store a new article and return its ID"""
        try:
            async with self.pool.acquire() as conn:
                article_id = await conn.fetchval("""
                    INSERT INTO news_articles (title, content, source, topic)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, article['title'], article['content'], article['source'], article['topic'])
                return article_id
        except Exception as e:
            print(f"Error storing article: {e}")
            raise

    async def store_summary(self, article_id: int, summary: str, insights: List[str]):
        """Store a summary and its insights for an article"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO article_summaries (article_id, summary, insights)
                    VALUES ($1, $2, $3)
                """, article_id, summary, insights)
        except Exception as e:
            print(f"Error storing summary: {e}")
            raise

    async def get_summaries_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        """Retrieve summaries for a specific topic"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT a.title, a.source, a.topic, s.summary, s.insights, a.created_at
                    FROM news_articles a
                    JOIN article_summaries s ON a.id = s.article_id
                    WHERE a.topic = $1
                    ORDER BY a.created_at DESC
                    LIMIT $2
                """, topic, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving summaries by topic: {e}")
            raise

    async def get_summaries_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        limit: int = 10
    ) -> List[Dict]:
        """Retrieve summaries within a date range"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT a.title, a.source, a.topic, s.summary, s.insights, a.created_at
                    FROM news_articles a
                    JOIN article_summaries s ON a.id = s.article_id
                    WHERE a.created_at BETWEEN $1 AND $2
                    ORDER BY a.created_at DESC
                    LIMIT $3
                """, start_date, end_date, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving summaries by date range: {e}")
            raise

    async def search_summaries(self, query: str, limit: int = 10) -> List[Dict]:
        """Search summaries using full-text search"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT a.title, a.source, a.topic, s.summary, s.insights, a.created_at
                    FROM news_articles a
                    JOIN article_summaries s ON a.id = s.article_id
                    WHERE to_tsvector('english', a.title || ' ' || s.summary) @@ to_tsquery('english', $1)
                    ORDER BY ts_rank(to_tsvector('english', a.title || ' ' || s.summary), to_tsquery('english', $1)) DESC
                    LIMIT $2
                """, query, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching summaries: {e}")
            raise

    async def get_article_with_summary(self, article_id: int) -> Optional[Dict]:
        """Retrieve an article with its summary"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT a.title, a.content, a.source, a.topic, s.summary, s.insights, a.created_at
                    FROM news_articles a
                    JOIN article_summaries s ON a.id = s.article_id
                    WHERE a.id = $1
                """, article_id)
                return dict(row) if row else None
        except Exception as e:
            print(f"Error retrieving article with summary: {e}")
            raise

# Example usage
async def main():
    db = DatabaseManager()
    try:
        await db.connect()
        await db.create_tables()
        
        # Example: Store an article and its summary
        article = {
            'title': 'Test Article',
            'content': 'This is a test article content...',
            'source': 'Test Source',
            'topic': 'Test Topic'
        }
        
        article_id = await db.store_article(article)
        await db.store_summary(
            article_id,
            'This is a test summary...',
            ['First insight', 'Second insight']
        )
        
        # Example: Query summaries
        summaries = await db.get_summaries_by_topic('Test Topic')
        print(f"Found {len(summaries)} summaries")
        
    finally:
        await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
