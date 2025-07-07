"""Core scraping functionality"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
from datetime import datetime
from config import Config


class YellowPagesScraper:
    def __init__(self, progress_callback=None, log_callback=None):
        self.headers = Config.HEADERS
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.stop_requested = False
        
        # Configuration
        self.BASE_URL = Config.BASE_URL
        self.MIN_DELAY = Config.MIN_DELAY
        self.MAX_DELAY = Config.MAX_DELAY
        self.EMPTY_PAGE_THRESHOLD = Config.EMPTY_PAGE_THRESHOLD
    
    def clean_text(self, text):
        """Clean and normalize text"""
        return ' '.join(str(text).strip().split()) if text else None

    def get_random_delay(self):
        """Get random delay between requests"""
        return random.uniform(self.MIN_DELAY, self.MAX_DELAY)

    def log_message(self, message):
        """Log message using callback or print"""
        if self.log_callback:
            self.log_callback(message)
        print(message)

    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.log_message(f"Error scraping {url}: {str(e)}")
            return None

    def extract_listing_data(self, listing, page_num):
        """Extract data from a single listing"""
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

        # Website
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

    def run_scraper(self, category, location, start_page=1, end_page=None):
        """Main scraping method with start/end page support"""
        all_data = []
        empty_pages = 0
        
        # Determine page range
        if end_page is None:
            # Original behavior - scrape until empty pages
            page = start_page
            use_empty_page_logic = True
            self.log_message(f"Starting scrape for {category} in {location} from page {start_page}...")
        else:
            # Fixed range scraping
            use_empty_page_logic = False
            if start_page == end_page:
                self.log_message(f"Scraping only page {start_page} for {category} in {location}...")
            else:
                self.log_message(f"Scraping pages {start_page} to {end_page} for {category} in {location}...")
        
        page = start_page
        
        while not self.stop_requested:
            # Check if we've reached the end page
            if end_page is not None and page > end_page:
                self.log_message(f"Reached end page {end_page}")
                break
                
            url = self.BASE_URL.format(page=page, category=category, location=location)
            self.log_message(f"Page {page}: Scraping...")
            
            soup = self.scrape_page(url)
            if not soup:
                empty_pages += 1
                self.log_message(f"Page {page}: Failed to load")
            else:
                listings = soup.find_all('div', class_='listing__content')
                if not listings:
                    empty_pages += 1
                    self.log_message(f"Page {page}: No listings found")
                else:
                    empty_pages = 0
                    for listing in listings:
                        all_data.append(self.extract_listing_data(listing, page))
                    self.log_message(f"Page {page}: Found {len(listings)} listings")
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(page, len(all_data))
            
            # Stop if we hit empty page threshold (only when not using fixed range)
            if use_empty_page_logic and empty_pages >= self.EMPTY_PAGE_THRESHOLD:
                self.log_message(f"Stopping - {empty_pages} consecutive empty pages")
                break
            
            page += 1
            
            # Polite delay (except for the last page)
            if not self.stop_requested and (end_page is None or page <= end_page):
                delay = self.get_random_delay()
                self.log_message(f"Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        self.log_message(f"Scraping complete! Found {len(all_data)} listings")
        return all_data

    def stop_scraping(self):
        """Stop the scraping process"""
        self.stop_requested = True
