import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set up the cache directory
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_and_cache(url: str, filename: str) -> str:
    """Fetches a page politely or loads it from the local cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    
    # Check if we already have it saved
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    # If not in cache, fetch it politely
    print(f"FETCH: Requesting {url}...")
    
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/polite-scraper)"
    }
    
    # Wait at least half a second between real requests to the site
    time.sleep(0.5)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            return html
        else:
            print(f"FETCH FAILED: Status code {response.status_code}")
            return ""
            
    except requests.exceptions.RequestException as e:
        print(f"FETCH ERROR: {e}")
        return ""

def discover_catalogue_pages():
    """Discovers books across the first 3 catalogue pages."""
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    
    catalogue_pages = 0
    all_book_urls = []
    
    # Let the site dictate the next page, stopping after 3 pages
    while current_url and catalogue_pages < 3:
        catalogue_pages += 1
        filename = f"catalogue-page-{catalogue_pages}.html"
        
        html = fetch_and_cache(current_url, filename)
        if not html:
            break
            
        # Parse the saved page with Beautiful Soup
        soup = BeautifulSoup(html, "html.parser")
        
        # Collect the link to every book on the current page
        for h3 in soup.find_all("h3"):
            a_tag = h3.find("a")
            if a_tag and "href" in a_tag.attrs:
                # Turn relative URLs into absolute URLs
                absolute_url = urljoin(current_url, a_tag["href"])
                all_book_urls.append(absolute_url)
                
        # Follow the catalogue's own "next" link
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_a = next_btn.find("a")
            if next_a and "href" in next_a.attrs:
                current_url = urljoin(current_url, next_a["href"])
            else:
                current_url = None
        else:
            current_url = None

    # Remove duplicate links before the next stage
    unique_urls = list(set(all_book_urls))
    
    # Print the exact summary required by the checkpoint
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")
    
    return unique_urls

if __name__ == "__main__":
    print("Scraper initialized.")
    book_links = discover_catalogue_pages()