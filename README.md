# The Polite Scraper

## Target Classification
* **Target Site:** `https://books.toscrape.com`
* **Why:** Books to Scrape is a public practice sandbox built explicitly for developers to practice web scraping safely.
* **Scope:** I am only collecting the first 3 catalogue pages.
* **Data Collected:** Book title, product URL, price text, availability, rating, and description.
* **Robots.txt Result:** Requested `https://books.toscrape.com/robots.txt` and received a 404 status code (no robots file found).

I will not reuse this code on another site without checking its rules and terms first.

## Installation & Execution
* **Lane:** Python
* **Dependencies:** `pip install requests beautifulsoup4 pydantic`
* **Run Command:** `python src/main.py`

## Record Schema
Every valid record conforms strictly to this structure:
* `title` (string)
* `product_url` (string, absolute URL)
* `price_text` (string, raw text)
* `price_gbp` (float, normalized)
* `availability_text` (string)
* `rating_text` (string or null)
* `description` (string or null)
* `source_page` (string)
* `fetched_at` (ISO 8601 UTC timestamp)

## Politeness Rules
* **User-Agent:** Identifies the scraper and links to this repository so server admins can contact the developer.
* **Delay:** Enforces a strict 500ms sleep between live network requests to prevent server hammering.
* **Timeout:** Aborts hanging requests after 10 seconds.
* **Cache:** Saves fetched HTML locally to bypass the network entirely during reruns and development.

## Limitations & Ethics
* **Limitation:** This scraper processes URLs sequentially. While highly polite, it is not optimized for high-throughput scaling.
* **Browser Note:** A headless browser was entirely unnecessary for this pipeline. The target data is shipped in the initial HTML payload, meaning a browser would only add massive compute and memory costs with zero benefit.
* **Ethics Statement:** Always use official APIs when available. Never bypass authentication, paywalls, or blocks. Only collect the specific data required for the task.

## Sample Run Report
```json
{
  "start_time": "2026-08-17T12:15:56Z",
  "duration_seconds": 2.55,
  "pages_fetched": 1,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}