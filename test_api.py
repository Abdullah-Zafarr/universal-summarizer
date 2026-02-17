
import os
import sys
from dotenv import load_dotenv

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import scrape_article, get_youtube_transcript

def test_apis():
    load_dotenv()
    
    print("Checking Environment Variables...")
    keys = ["GOOGLE_API_KEY", "GROQ_API_KEY", "FIRE_CRAWL_KEY"]
    for key in keys:
        val = os.getenv(key)
        if val and not val.startswith("your_"):
            print(f"✅ {key} is set.")
        else:
            print(f"❌ {key} is NOT set correctly.")

    print("\nTesting Article Scraping Tool (requires Firecrawl)...")
    test_url = "https://example.com"
    result = scrape_article(test_url)
    print(f"Result for {test_url}:")
    print(result[:500] + "..." if len(result) > 500 else result)

    print("\nTesting YouTube Tool...")
    # Using a short public video
    yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    yt_result = get_youtube_transcript(yt_url)
    print(f"Result for YT {yt_url}:")
    print(yt_result[:500] + "..." if len(yt_result) > 500 else yt_result)

if __name__ == "__main__":
    test_apis()
