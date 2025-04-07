import os
from dotenv import load_dotenv
from config import APIConfig

def test_config():
    # Load environment variables
    load_dotenv()
    
    # Print all environment variables (for debugging)
    print("\nAll Environment Variables:")
    print("-" * 50)
    for key, value in os.environ.items():
        if "KEY" in key or "TOKEN" in key or "PASSWORD" in key:
            print(f"{key}: {'*' * len(value) if value else 'Not set'}")
    
    config = APIConfig()
    
    print("\nTesting API Key Retrieval:")
    print("-" * 50)
    
    # Test each API key
    keys_to_test = [
        ("NEWSAPI_KEY", config.NEWSAPI_KEY),
        ("HF_TOKEN", config.HF_TOKEN),
        ("RAPIDAPI_KEY", config.RAPIDAPI_KEY),
        ("MARKETAUX_API_TOKEN", config.MARKETAUX_API_TOKEN),
        ("DB_USER", config.DB_USER),
        ("DB_PASSWORD", config.DB_PASSWORD)
    ]
    
    for key_name, value in keys_to_test:
        env_value = os.getenv(key_name)
        if env_value:
            print(f"✓ {key_name}: Retrieved from .env")
        elif value and value != f"your_{key_name.lower()}_here":
            print(f"✓ {key_name}: Retrieved from config default")
        else:
            print(f"✗ {key_name}: Not found in .env file or using default value")

if __name__ == "__main__":
    test_config() 