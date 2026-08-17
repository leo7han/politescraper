import os
import requests

# Set up the cache directory
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_and_cache(url: str, filename: str) -> str:
    """Fetches a page politely or loads it from the local cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    
    # Check if we already have it saved
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {filename} ({len(html)} bytes)")
        return html

    # If not in cache, fetch it politely (we will build this in Stage 1)
    pass

if __name__ == "__main__":
    print("Scraper initialized.")