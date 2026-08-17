import os
import requests
import time
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set up the cache directory
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_and_cache(url: str, filename: str) -> str:
    """Fetches a page politely or loads it from the local cache."""
    cache_path = os.path.join(CACHE_DIR, filename)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"FETCH: Requesting {url}...")
    headers = {
        "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/polite-scraper)"
    }
    
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
    
    while current_url and catalogue_pages < 3:
        catalogue_pages += 1
        filename = f"catalogue-page-{catalogue_pages}.html"
        
        html = fetch_and_cache(current_url, filename)
        if not html:
            break
            
        soup = BeautifulSoup(html, "html.parser")
        
        for h3 in soup.find_all("h3"):
            a_tag = h3.find("a")
            if a_tag and "href" in a_tag.attrs:
                absolute_url = urljoin(current_url, a_tag["href"])
                all_book_urls.append(absolute_url)
                
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_a = next_btn.find("a")
            current_url = urljoin(current_url, next_a["href"]) if next_a and "href" in next_a.attrs else None
        else:
            current_url = None

    unique_urls = list(set(all_book_urls))
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")
    
    return unique_urls

def extract_book_details(book_urls):
    """Extracts raw data fields from each individual book page."""
    raw_records = []
    
    for url in book_urls:
        # Create a clean filename based on the book's specific URL segment
        safe_name = url.split("/")[-2] + ".html"
        html = fetch_and_cache(url, f"book-{safe_name}")
        
        if not html:
            continue
            
        soup = BeautifulSoup(html, "html.parser")
        product_main = soup.find("div", class_="product_main")
        
        if not product_main:
            continue
            
        # Extract targeted elements
        title = product_main.find("h1").text if product_main.find("h1") else None
        
        price_p = product_main.find("p", class_="price_color")
        price_text = price_p.text if price_p else None
        
        availability_p = product_main.find("p", class_="instock availability")
        availability_text = availability_p.text.strip() if availability_p else None
        
        rating_p = product_main.find("p", class_="star-rating")
        rating_text = rating_p["class"][1] if rating_p and len(rating_p["class"]) > 1 else None
        
        desc_div = soup.find("div", id="product_description")
        description = None
        if desc_div:
            desc_p = desc_div.find_next_sibling("p")
            if desc_p:
                description = desc_p.text
                
        # Construct the raw record
        record = {
            "title": title,
            "product_url": url,
            "price_text": price_text,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": "https://books.toscrape.com/catalogue/page-1.html",
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        raw_records.append(record)
        
    print(f"detail_pages={len(raw_records)}")
    if raw_records:
        print("\nSample Record:")
        print(json.dumps(raw_records[0], indent=2))
        
    return raw_records

if __name__ == "__main__":
    print("Scraper initialized.")
    book_links = discover_catalogue_pages()
    records = extract_book_details(book_links)