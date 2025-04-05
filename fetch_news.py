import os
import json
import requests
import feedparser
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from config import APIConfig

# Load environment variables
load_dotenv()

class NewsFetcher:
    def __init__(self):
        # Initialize configuration
        self.config = APIConfig()
        
        # Create output directory
        os.makedirs(self.config.RAW_DIR, exist_ok=True)

    def fetch_newsapi(self, query: str, page_size: int = 10) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        try:
            params = {
                "q": query,
                "pageSize": page_size,
                "apiKey": self.config.NEWSAPI_KEY,
                "language": "en"
            }
            response = requests.get(self.config.NEWSAPI_ENDPOINT, params=params)
            response.raise_for_status()
            
            articles = []
            for article in response.json()["articles"]:
                articles.append({
                    "title": article["title"],
                    "content": article["content"] or article["description"],
                    "source": "NewsAPI",
                    "topic": query
                })
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []

    def fetch_rss(self, feed_url: str, topic: str) -> List[Dict]:
        """Fetch articles from RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries:
                articles.append({
                    "title": entry.title,
                    "content": entry.description,
                    "source": "RSS",
                    "topic": topic
                })
            return articles
            
        except Exception as e:
            print(f"Error fetching from RSS: {e}")
            return []

    def fetch_marketaux(self, countries: str = "us", limit: int = 10, published_after: str = "2025-04-03T23:48") -> List[Dict]:
        """Fetch articles from Marketaux API"""
        try:
            params = {
                "countries": countries,
                "filter_entities": "true",
                "limit": limit,
                "published_after": published_after,
                "api_token": self.config.MARKETAUX_API_TOKEN
            }
            response = requests.get(self.config.MARKETAUX_API_ENDPOINT, params=params)
            response.raise_for_status()
            
            articles = []
            for article in response.json().get("data", []):
                articles.append({
                    "title": article.get("title"),
                    "content": article.get("description"),
                    "source": "Marketaux",
                    "topic": "Market News"
                })
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Marketaux: {e}")
            return []

    def fetch_rapidapi(self, query: str = "technology", language: str = "en") -> List[Dict]:
        """Fetch articles from RapidAPI News API"""
        try:
            headers = {
                "x-rapidapi-key": self.config.RAPIDAPI_KEY,
                "x-rapidapi-host": self.config.RAPIDAPI_HOST
            }
            params = {
                "query": query,
                "language": language
            }
            response = requests.get(self.config.RAPIDAPI_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            
            articles = []
            for article in response.json().get("articles", []):
                articles.append({
                    "title": article.get("title"),
                    "content": article.get("description"),
                    "source": "RapidAPI News",
                    "topic": query
                })
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from RapidAPI News: {e}")
            return []

    def save_articles(self, articles: List[Dict]):
        """Save articles to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, article in enumerate(articles):
            filename = f"{self.config.RAW_DIR}/article_{timestamp}_{i}.json"
            with open(filename, "w") as f:
                json.dump(article, f, indent=4)

    def fetch_all(self, topics: List[str], rss_feeds: List[Dict] = None):
        """Fetch articles from all sources"""
        all_articles = []
        
        for topic in topics:
            # Fetch from NewsAPI
            articles = self.fetch_newsapi(topic)
            all_articles.extend(articles)
        
        # Fetch from Marketaux API
        marketaux_articles = self.fetch_marketaux()
        all_articles.extend(marketaux_articles)
        
        # Fetch from RapidAPI News API
        rapidapi_articles = self.fetch_rapidapi()
        all_articles.extend(rapidapi_articles)
        
        # Fetch from RSS feeds if provided
        if rss_feeds:
            for feed in rss_feeds:
                articles = self.fetch_rss(feed["url"], feed["topic"])
                all_articles.extend(articles)
        
        # Save all articles
        self.save_articles(all_articles)
        
        # Send to API
        api_url = "http://localhost:8000/news/raw"
        for article in all_articles:
            try:
                response = requests.post(api_url, json=article)
                response.raise_for_status()
                print(f"Successfully sent article: {article['title']}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending article to API: {e}")

if __name__ == "__main__":
    # Example usage
    fetcher = NewsFetcher()
    topics = ["artificial intelligence", "machine learning", "data science"]
    rss_feeds = [
        {"url": "http://feeds.feedburner.com/TechCrunch", "topic": "technology"},
        {"url": "https://news.mit.edu/rss/feed", "topic": "science"}
    ]
    fetcher.fetch_all(topics, rss_feeds)
