import os
import requests
import time
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel, ValidationError

# Set up the cache and output directories
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the precise schema using Pydantic
class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: str
    fetched_at: str

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
    return unique_urls

def normalize_price(price_str: str) -> float:
    """Converts a string like '£51.77' into a clean float 51.77"""
    if not price_str:
        return 0.0
    clean_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def extract_and_validate_books(book_urls):
    """Extracts, normalizes, and validates records before storing them."""
    # Using a dictionary keyed by canonical URL ensures idempotency (no duplicates)
    valid_records = {} 
    errors = []
    
    for url in book_urls:
        safe_name = url.split("/")[-2] + ".html"
        html = fetch_and_cache(url, f"book-{safe_name}")
        
        if not html:
            continue
            
        soup = BeautifulSoup(html, "html.parser")
        product_main = soup.find("div", class_="product_main")
        if not product_main:
            continue
            
        title = product_main.find("h1").text if product_main.find("h1") else None
        
        price_p = product_main.find("p", class_="price_color")
        price_text = price_p.text if price_p else ""
        
        availability_p = product_main.find("p", class_="instock availability")
        availability_text = availability_p.text.strip() if availability_p else ""
        
        rating_p = product_main.find("p", class_="star-rating")
        rating_text = rating_p["class"][1] if rating_p and len(rating_p["class"]) > 1 else None
        
        desc_div = soup.find("div", id="product_description")
        description = None
        if desc_div:
            desc_p = desc_div.find_next_sibling("p")
            if desc_p:
                description = desc_p.text
                
        # 1. Normalize
        raw_record = {
            "title": title,
            "product_url": url,
            "price_text": price_text,
            "price_gbp": normalize_price(price_text),
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": "https://books.toscrape.com/catalogue/page-1.html",
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # 2. Validate
        try:
            validated = BookRecord(**raw_record)
            valid_records[url] = validated.model_dump()
        except ValidationError as e:
            errors.append({"url": url, "error": str(e), "raw_record": raw_record})
            
    # 3. Store
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(list(valid_records.values()), f, indent=2)
        
    if errors:
        with open("errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2)
            
    print(f"Validation complete.")
    print(f"Good records safely stored in output/books.json: {len(valid_records)}")
    if errors:
        print(f"Failed records routed to errors.json: {len(errors)}")

if __name__ == "__main__":
    print("Scraper initialized.")
    book_links = discover_catalogue_pages()
    extract_and_validate_books(book_links)