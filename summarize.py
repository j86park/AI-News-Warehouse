import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from config import APIConfig

# Load environment variables
load_dotenv()

class NewsSummarizer:
    def __init__(self):
        self.config = APIConfig()
        self.api_url = "http://localhost:8000/news/summarize"
        self.headers = {
            "Authorization": f"Bearer {self.config.HF_TOKEN}"
        }
        
    def _chunk_text(self, text: str, max_length: int = 1024) -> List[str]:
        """Split text into chunks that fit within model's context length"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            # Rough estimate: 1 word ≈ 1.3 tokens
            word_length = len(word) * 1.3
            if current_length + word_length > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def _summarize_chunk(self, text: str) -> str:
        """Generate summary for a single chunk using BART model"""
        try:
            response = requests.post(
                self.hf_api_url,
                headers=self.headers,
                json={"inputs": text}
            )
            response.raise_for_status()
            return response.json()[0]['summary_text'].strip()
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            return ""

    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from the text using BART model"""
        try:
            # Use the same model but with a different prompt
            prompt = f"Extract 3-5 key insights from this text: {text}"
            response = requests.post(
                self.hf_api_url,
                headers=self.headers,
                json={"inputs": prompt}
            )
            response.raise_for_status()
            insights = response.json()[0]['summary_text'].strip()
            return [insight.strip() for insight in insights.split("\n") if insight.strip()]
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return []

    def summarize_article(self, article: Dict) -> Dict:
        """Generate summary and insights for an article"""
        try:
            # Combine title and content for better context
            full_text = f"{article['title']}\n\n{article['content']}"
            
            # Split text into chunks if needed
            chunks = self._chunk_text(full_text)
            
            # Generate summaries for each chunk
            chunk_summaries = [self._summarize_chunk(chunk) for chunk in chunks]
            
            # Combine chunk summaries
            combined_summary = " ".join(chunk_summaries)
            
            # Extract key insights
            insights = self._extract_key_insights(full_text)
            
            return {
                "summary": combined_summary,
                "insights": insights,
                "original_title": article["title"],
                "source": article["source"],
                "topic": article["topic"]
            }
            
        except Exception as e:
            print(f"Error summarizing article: {e}")
            return None

    def process_articles(self, articles: List[Dict]):
        """Process multiple articles and send summaries to API"""
        for article in articles:
            try:
                # Generate summary and insights
                result = self.summarize_article(article)
                if not result:
                    continue
                
                # Send to API
                response = requests.post(
                    f"{self.api_url}/{article['id']}",
                    json={"summary": result["summary"]}
                )
                response.raise_for_status()
                
                print(f"Successfully processed article: {article['title']}")
                
            except Exception as e:
                print(f"Error processing article {article['title']}: {e}")

if __name__ == "__main__":
    # Example usage
    summarizer = NewsSummarizer()
    
    # Example article
    test_article = {
        "id": 1,
        "title": "Test Article",
        "content": "This is a test article content...",
        "source": "Test Source",
        "topic": "Test Topic"
    }
    
    summarizer.process_articles([test_article])
