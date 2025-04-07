import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:

    # NewsAPI Configuration
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "your_newsapi_key_here")
    NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "your_github_token_here")
    
    # Hugging Face Configuration
    HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
    HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    
    # RapidAPI Configuration
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "your_rapidapi_key_here")
    RAPIDAPI_HOST = "news-api14.p.rapidapi.com"
    RAPIDAPI_ENDPOINT = "https://news-api14.p.rapidapi.com/v2/search/articles"
    
    # Marketaux API Configuration
    MARKETAUX_API_TOKEN = os.getenv("MARKETAUX_API_TOKEN", "your_marketaux_token_here")
    MARKETAUX_API_ENDPOINT = "https://api.marketaux.com/v1/news/all"
    
    # Output directory
    RAW_DIR = "data/raw_articles"
    
    # Database Configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "news_warehouse")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    