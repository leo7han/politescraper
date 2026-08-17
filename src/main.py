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

    # If not in cache, fetch it politely
    print(f"FETCH: Requesting {url}...")
    
    # Polite scrapers always identify themselves
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/polite-scraper)"
    }
    
    try:
        # Set a 10-second timeout so it never hangs forever
        response = requests.get(url, headers=headers, timeout=10)
        
        # Only status 200 means "here is your page"
        if response.status_code == 200:
            html = response.text
            # Save the HTML to the cache folder
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"FETCH SUCCESS: Saved {filename} ({len(html)} bytes)")
            return html
        else:
            print(f"FETCH FAILED: Status code {response.status_code}")
            return ""
            
    except requests.exceptions.RequestException as e:
        print(f"FETCH ERROR: {e}")
        return ""

if __name__ == "__main__":
    print("Scraper initialized.")
    # Request the first catalogue page
    target_url = "https://books.toscrape.com/catalogue/page-1.html"
    html_content = fetch_and_cache(target_url, "catalogue-page-1.html")