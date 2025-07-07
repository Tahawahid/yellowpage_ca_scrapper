import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from urllib.parse import urljoin
from datetime import datetime

# ===== CONFIGURABLE VARIABLES =====
BASE_URL = "https://www.yellowpages.ca/search/si/{page}/{category}/{location}"
CATEGORY = "dentists"  # Try: restaurants, plumbers, electricians, etc.
LOCATION = "Toronto+ON"  # Format: City+Province or PostalCode
START_PAGE = 1
MAX_PAGES = 100  # Safety limit
MIN_DELAY = 8
MAX_DELAY = 12
EMPTY_PAGE_THRESHOLD = 2  # Stop after this many empty pages

# ===== GENERIC SCRAPER =====
class YellowPagesScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def clean_text(self, text):
        return ' '.join(str(text).strip().split()) if text else None

    def get_random_delay(self):
        return random.uniform(MIN_DELAY, MAX_DELAY)

    def scrape_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def extract_listing_data(self, listing, page_num):
        data = {
            "name": None,
            "phone": None,
            "website": None,
            "url": None,
            "address": {
                "street": None,
                "city": None,
                "region": None,
                "postal_code": None
            },
            "categories": [],
            "page_number": page_num,
            "scraped_at": datetime.now().isoformat()
        }

        # Name and URL
        name_tag = listing.find('a', class_='listing__name--link')
        if name_tag:
            data['name'] = self.clean_text(name_tag.text)
            data['url'] = urljoin('https://www.yellowpages.ca', name_tag['href'])

        # Phone
        phone_tag = listing.find('a', attrs={'data-phone': True})
        if phone_tag:
            data['phone'] = phone_tag['data-phone']

        # Website (more generic approach)
        for a_tag in listing.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith(('http://', 'https://')):
                data['website'] = href
                break

        # Address
        address_fields = {
            'street': ('span', {'itemprop': 'streetAddress'}),
            'city': ('span', {'itemprop': 'addressLocality'}),
            'region': ('span', {'itemprop': 'addressRegion'}),
            'postal_code': ('span', {'itemprop': 'postalCode'})
        }
        for field, (tag, attrs) in address_fields.items():
            elem = listing.find(tag, attrs)
            if elem:
                data['address'][field] = self.clean_text(elem.text)

        # Categories
        for cat_tag in listing.find_all('div', class_='listing__headings'):
            if cat_link := cat_tag.find('a'):
                if cat_text := self.clean_text(cat_link.text):
                    data['categories'].append(cat_text)

        return data

    def run(self):
        all_data = []
        empty_pages = 0
        output_prefix = f"yp_{CATEGORY}_{LOCATION.replace('+', '_')}_{self.timestamp}"
        
        for page in range(START_PAGE, MAX_PAGES + 1):
            url = BASE_URL.format(page=page, category=CATEGORY, location=LOCATION)
            print(f"Page {page}: {url}")
            
            soup = self.scrape_page(url)
            if not soup:
                empty_pages += 1
            else:
                listings = soup.find_all('div', class_='listing__content')
                if not listings:
                    empty_pages += 1
                else:
                    empty_pages = 0
                    for listing in listings:
                        all_data.append(self.extract_listing_data(listing, page))
                    print(f"Found {len(listings)} listings")
            
            # Stop if we hit empty page threshold
            if empty_pages >= EMPTY_PAGE_THRESHOLD:
                print(f"Stopping - {empty_pages} consecutive empty pages")
                break
            
            # Save progress
            if page % 5 == 0 or page == MAX_PAGES:
                self.save_data(all_data, output_prefix)
            
            # Polite delay
            if page < MAX_PAGES:
                time.sleep(self.get_random_delay())
        
        print(f"\nScraped {len(all_data)} listings from {page} pages")
        return all_data

    def save_data(self, data, prefix):
        # JSON
        json_file = f"{prefix}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = f"{prefix}.csv"
        if data:
            # Flatten data for CSV
            flat_data = []
            for item in data:
                flat_item = {**item, **{f"address_{k}": v for k, v in item['address'].items()}}
                flat_item['categories'] = '|'.join(flat_item['categories'])
                del flat_item['address']
                flat_data.append(flat_item)
            
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                writer.writeheader()
                writer.writerows(flat_data)
        
        print(f"Saved current data to {json_file} and {csv_file}")

# ===== RUN THE SCRAPER =====
if __name__ == "__main__":
    scraper = YellowPagesScraper()
    print(f"Starting scrape for {CATEGORY} in {LOCATION}...")
    results = scraper.run()
    print("Scraping complete!")