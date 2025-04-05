import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:
    # NewsAPI Configuration
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"
    

    
    # GitHub API Configuration (example for future use)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    
    # Common settings
    DEFAULT_PAGE_SIZE = 10
    DEFAULT_TWEET_COUNT = 100
    LANGUAGE = "en"
    
    # Output directory
    RAW_DIR = "data/raw_articles"
    
    # Marketaux API Configuration
    MARKETAUX_API_TOKEN = "zARt9dMLLutBSHbXaV9MpaJ3Q8umWgRIwqGtzmW9"
    MARKETAUX_API_ENDPOINT = "https://api.marketaux.com/v1/news/all"
    
    # RapidAPI News API Configuration
    RAPIDAPI_KEY = "1bb93f160cmsh66f7c85c3f0d8c7p1ad3ddjsn5a3acaa1a91c"
    RAPIDAPI_HOST = "news-api14.p.rapidapi.com"
    RAPIDAPI_ENDPOINT = "https://news-api14.p.rapidapi.com/v2/search/articles" 