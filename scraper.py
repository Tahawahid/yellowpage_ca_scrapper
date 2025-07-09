"""Core scraping functionality"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from config import Config


class YellowPagesScraper:
    def __init__(self, progress_callback=None, log_callback=None, delay_settings=None):
        self.headers = Config.HEADERS
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.stop_requested = False
        
        # Use custom delay settings or defaults
        if delay_settings:
            self.SEARCH_PAGE_MIN_DELAY = delay_settings.get('search_min', Config.DEFAULT_SEARCH_PAGE_MIN_DELAY)
            self.SEARCH_PAGE_MAX_DELAY = delay_settings.get('search_max', Config.DEFAULT_SEARCH_PAGE_MAX_DELAY)
            self.LISTING_PAGE_MIN_DELAY = delay_settings.get('listing_min', Config.DEFAULT_LISTING_PAGE_MIN_DELAY)
            self.LISTING_PAGE_MAX_DELAY = delay_settings.get('listing_max', Config.DEFAULT_LISTING_PAGE_MAX_DELAY)
            self.WEBSITE_MIN_DELAY = delay_settings.get('website_min', Config.DEFAULT_WEBSITE_MIN_DELAY)
            self.WEBSITE_MAX_DELAY = delay_settings.get('website_max', Config.DEFAULT_WEBSITE_MAX_DELAY)
            self.PAGE_LOAD_MIN_DELAY = delay_settings.get('page_load_min', Config.DEFAULT_PAGE_LOAD_MIN_DELAY)
            self.PAGE_LOAD_MAX_DELAY = delay_settings.get('page_load_max', Config.DEFAULT_PAGE_LOAD_MAX_DELAY)
            self.WEBSITE_TIMEOUT = delay_settings.get('website_timeout', Config.DEFAULT_WEBSITE_TIMEOUT)
            self.MAX_WEBSITE_RETRIES = delay_settings.get('website_retries', Config.DEFAULT_MAX_WEBSITE_RETRIES)
            self.PAGE_LOAD_TIMEOUT = delay_settings.get('page_timeout', Config.DEFAULT_PAGE_LOAD_TIMEOUT)
            self.MAX_PAGE_RETRIES = delay_settings.get('page_retries', Config.DEFAULT_MAX_PAGE_RETRIES)
        else:
            self.SEARCH_PAGE_MIN_DELAY = Config.DEFAULT_SEARCH_PAGE_MIN_DELAY
            self.SEARCH_PAGE_MAX_DELAY = Config.DEFAULT_SEARCH_PAGE_MAX_DELAY
            self.LISTING_PAGE_MIN_DELAY = Config.DEFAULT_LISTING_PAGE_MIN_DELAY
            self.LISTING_PAGE_MAX_DELAY = Config.DEFAULT_LISTING_PAGE_MAX_DELAY
            self.WEBSITE_MIN_DELAY = Config.DEFAULT_WEBSITE_MIN_DELAY
            self.WEBSITE_MAX_DELAY = Config.DEFAULT_WEBSITE_MAX_DELAY
            self.PAGE_LOAD_MIN_DELAY = Config.DEFAULT_PAGE_LOAD_MIN_DELAY
            self.PAGE_LOAD_MAX_DELAY = Config.DEFAULT_PAGE_LOAD_MAX_DELAY
            self.WEBSITE_TIMEOUT = Config.DEFAULT_WEBSITE_TIMEOUT
            self.MAX_WEBSITE_RETRIES = Config.DEFAULT_MAX_WEBSITE_RETRIES
            self.PAGE_LOAD_TIMEOUT = Config.DEFAULT_PAGE_LOAD_TIMEOUT
            self.MAX_PAGE_RETRIES = Config.DEFAULT_MAX_PAGE_RETRIES
        
        # Configuration
        self.BASE_URL = Config.BASE_URL
        self.EMPTY_PAGE_THRESHOLD = Config.EMPTY_PAGE_THRESHOLD
        self.SOCIAL_DOMAINS = Config.SOCIAL_DOMAINS
    
    def clean_text(self, text):
        """Clean and normalize text"""
        return ' '.join(str(text).strip().split()) if text else None

    def get_random_delay(self, delay_type='search'):
        """Get random delay between requests"""
        if delay_type == 'search':
            return random.uniform(self.SEARCH_PAGE_MIN_DELAY, self.SEARCH_PAGE_MAX_DELAY)
        elif delay_type == 'listing':
            return random.uniform(self.LISTING_PAGE_MIN_DELAY, self.LISTING_PAGE_MAX_DELAY)
        elif delay_type == 'website':
            return random.uniform(self.WEBSITE_MIN_DELAY, self.WEBSITE_MAX_DELAY)
        elif delay_type == 'page_load':
            return random.uniform(self.PAGE_LOAD_MIN_DELAY, self.PAGE_LOAD_MAX_DELAY)
        else:
            return random.uniform(self.SEARCH_PAGE_MIN_DELAY, self.SEARCH_PAGE_MAX_DELAY)

    def log_message(self, message):
        """Log message using callback or print"""
        if self.log_callback:
            self.log_callback(message)
        print(message)

    def scrape_page_with_retry(self, url, timeout=None, max_retries=None):
        """Scrape a single page with retry logic and error handling"""
        if timeout is None:
            timeout = self.PAGE_LOAD_TIMEOUT
        if max_retries is None:
            max_retries = self.MAX_PAGE_RETRIES
            
        for attempt in range(max_retries):
            try:
                self.log_message(f"    Attempting to load: {url} (Attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(url, headers=self.headers, timeout=timeout)
                
                if response.status_code == 404:
                    self.log_message(f"    404 Not Found: {url}")
                    return None
                elif response.status_code == 403:
                    self.log_message(f"    403 Forbidden: {url}")
                    return None
                elif response.status_code >= 500:
                    self.log_message(f"    Server error {response.status_code}: {url}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                
                response.raise_for_status()
                
                # Wait for page to "load" (simulate loading time)
                page_load_delay = self.get_random_delay('page_load')
                time.sleep(page_load_delay)
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.Timeout:
                self.log_message(f"    Timeout error for {url}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.exceptions.ConnectionError:
                self.log_message(f"    Connection error for {url}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                self.log_message(f"    Error scraping {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None

    def extract_listing_urls_from_search_results(self, soup):
        """Extract ONLY listing URLs from search results page"""
        listing_urls = []
        
        if not soup:
            return listing_urls
        
        # Find all listing containers
        listings = soup.find_all('div', class_='listing__content')
        
        for listing in listings:
            # Extract listing URL
            name_tag = listing.find('a', class_='listing__name--link')
            if name_tag and name_tag.get('href'):
                listing_url = urljoin('https://www.yellowpages.ca', name_tag['href'])
                listing_urls.append(listing_url)
        
        return listing_urls

    def extract_emails_from_text(self, text):
        """Extract email addresses from text"""
        if not text:
            return []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        # Filter out common false positives
        filtered_emails = []
        for email in emails:
            if not any(skip in email.lower() for skip in ['example.com', 'test.com', 'dummy.com']):
                filtered_emails.append(email)
        return list(set(filtered_emails))

    def extract_social_links(self, soup):
        """Extract social media links from a webpage"""
        social_links = {}
        
        if not soup:
            return social_links
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for domain in self.SOCIAL_DOMAINS:
                if domain in href:
                    platform = domain.split('.')[0]
                    if platform == 'x':
                        platform = 'twitter'
                    elif platform == 'threads':
                        platform = 'threads'
                    
                    if platform not in social_links:
                        social_links[platform] = []
                    
                    # Clean the URL
                    original_href = link['href']
                    full_url = original_href if original_href.startswith(('http://', 'https://')) else f"https://{original_href}"
                    
                    # Avoid duplicates
                    if full_url not in social_links[platform]:
                        social_links[platform].append(full_url)
        
        return social_links

    def scrape_website_for_contacts(self, website_url):
        """Scrape website for social media links and emails"""
        if not website_url:
            return {'emails': [], 'social_links': {}}
        
        # Clean the URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = f"https://{website_url}"
        
        self.log_message(f"    Scraping website: {website_url}")
        
        soup = self.scrape_page_with_retry(website_url, timeout=self.WEBSITE_TIMEOUT, max_retries=self.MAX_WEBSITE_RETRIES)
        if not soup:
            self.log_message(f"    Failed to load website: {website_url}")
            return {'emails': [], 'social_links': {}}
        
        # Extract emails from page text
        page_text = soup.get_text()
        emails = self.extract_emails_from_text(page_text)
        
        # Extract social media links
        social_links = self.extract_social_links(soup)
        
        self.log_message(f"    Found {len(emails)} emails and {len(social_links)} social platforms")
        
        return {
            'emails': emails,
            'social_links': social_links
        }

    def extract_listing_data_from_individual_page(self, listing_url, page_num):
        """Extract complete data from individual listing page"""
        data = {
            "name": None,
            "phone": None,
            "website": None,
            "url": listing_url,
            "address": {
                "street": None,
                "city": None,
                "region": None,
                "postal_code": None
            },
            "categories": [],
            "page_number": page_num,
            "scraped_at": datetime.now().isoformat(),
            "phone_numbers": [],
            "websites": [],
                        "business_hours": None,
            "emails": [],
            "social_links": {},
            "scraping_status": "success"
        }
        
        try:
            self.log_message(f"  Scraping listing: {listing_url}")
            
            soup = self.scrape_page_with_retry(listing_url)
            if not soup:
                data['scraping_status'] = "failed_to_load"
                return data
            
            # Extract business name
            name_elem = soup.find('span', class_='merchantName')
            if name_elem:
                data['name'] = self.clean_text(name_elem.text)
            
            # Extract address
            address_elem = soup.find('div', {'itemprop': 'address'})
            if address_elem:
                street_elem = address_elem.find('span', {'itemprop': 'streetAddress'})
                city_elem = address_elem.find('span', {'itemprop': 'addressLocality'})
                region_elem = address_elem.find('span', {'itemprop': 'addressRegion'})
                postal_elem = address_elem.find('span', {'itemprop': 'postalCode'})
                
                if street_elem:
                    data['address']['street'] = self.clean_text(street_elem.text)
                if city_elem:
                    data['address']['city'] = self.clean_text(city_elem.text)
                if region_elem:
                    data['address']['region'] = self.clean_text(region_elem.text)
                if postal_elem:
                    data['address']['postal_code'] = self.clean_text(postal_elem.text)
            
            # Extract phone numbers
            phone_section = soup.find('li', class_='mlr__item--phone')
            if phone_section:
                phone_submenu = phone_section.find('ul', class_='mlr__submenu')
                if phone_submenu:
                    for phone_item in phone_submenu.find_all('li'):
                        phone_span = phone_item.find('span', class_='mlr__sub-text')
                        label_span = phone_item.find('span', class_='mlr__label')
                        if phone_span and label_span:
                            phone_number = self.clean_text(phone_span.text)
                            phone_type = self.clean_text(label_span.text)
                            data['phone_numbers'].append({
                                'number': phone_number,
                                'type': phone_type
                            })
                            # Set primary phone
                            if phone_type and phone_type.lower() == 'primary' and not data['phone']:
                                data['phone'] = phone_number
            
            # Extract website URLs
            website_section = soup.find('li', class_='mlr__item--website')
            if website_section:
                website_submenu = website_section.find('ul', class_='mlr__submenu')
                if website_submenu:
                    for website_item in website_submenu.find_all('li'):
                        website_link = website_item.find('a')
                        if website_link and website_link.get('href'):
                            href = website_link['href']
                            # Extract the actual URL from the redirect
                            if 'redirect=' in href:
                                actual_url = href.split('redirect=')[1].split('&')[0]
                                from urllib.parse import unquote
                                actual_url = unquote(actual_url)
                                data['websites'].append(actual_url)
                        else:
                            # For print items, extract from text
                            website_span = website_item.find('span', class_='mlr__sub-text')
                            if website_span:
                                website_text = self.clean_text(website_span.text)
                                if website_text:
                                    if not website_text.startswith(('http://', 'https://')):
                                        website_text = f"https://{website_text}"
                                    data['websites'].append(website_text)
            
            # Remove duplicates from websites
            data['websites'] = list(set(data['websites']))
            
            # Set primary website
            if data['websites'] and not data['website']:
                data['website'] = data['websites'][0]
            
            # Extract business hours
            hours_link = soup.find('a', class_='merchant__status-text')
            if hours_link:
                data['business_hours'] = self.clean_text(hours_link.text)
            
            # Extract categories from breadcrumbs or other elements
            breadcrumbs = soup.find_all('a', href=True)
            for breadcrumb in breadcrumbs:
                if '/search/' in breadcrumb.get('href', ''):
                    category_text = self.clean_text(breadcrumb.text)
                    if category_text and category_text not in data['categories']:
                        data['categories'].append(category_text)
            
            # Now scrape websites for social media and emails
            if data['websites'] and not self.stop_requested:
                all_emails = []
                all_social_links = {}
                
                for website in data['websites']:
                    if self.stop_requested:
                        break
                    
                    # Add delay before visiting website
                    delay = self.get_random_delay('website')
                    self.log_message(f"    Waiting {delay:.1f} seconds before visiting website...")
                    time.sleep(delay)
                    
                    contact_info = self.scrape_website_for_contacts(website)
                    
                    # Merge emails
                    all_emails.extend(contact_info.get('emails', []))
                    
                    # Merge social links
                    for platform, links in contact_info.get('social_links', {}).items():
                        if platform not in all_social_links:
                            all_social_links[platform] = []
                        all_social_links[platform].extend(links)
                
                # Remove duplicates
                data['emails'] = list(set(all_emails))
                for platform in all_social_links:
                    all_social_links[platform] = list(set(all_social_links[platform]))
                data['social_links'] = all_social_links
            
            return data
            
        except Exception as e:
            self.log_message(f"  Error extracting listing data: {str(e)}")
            data['scraping_status'] = f"error: {str(e)}"
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
            self.log_message(f"Page {page}: Scraping search results...")
            
            soup = self.scrape_page_with_retry(url)
            if not soup:
                empty_pages += 1
                self.log_message(f"Page {page}: Failed to load search results")
            else:
                # Extract only listing URLs from search results
                listing_urls = self.extract_listing_urls_from_search_results(soup)
                
                if not listing_urls:
                    empty_pages += 1
                    self.log_message(f"Page {page}: No listing URLs found")
                else:
                    empty_pages = 0
                    self.log_message(f"Page {page}: Found {len(listing_urls)} listing URLs")
                    
                    # Process each listing URL
                    for i, listing_url in enumerate(listing_urls):
                        if self.stop_requested:
                            break
                            
                        self.log_message(f"  Processing listing {i+1}/{len(listing_urls)}: {listing_url}")
                        
                        # Add delay before visiting listing page
                        delay = self.get_random_delay('listing')
                        self.log_message(f"  Waiting {delay:.1f} seconds before visiting listing page...")
                        time.sleep(delay)
                        
                        # Extract detailed data from individual listing page
                        detailed_data = self.extract_listing_data_from_individual_page(listing_url, page)
                        
                        if detailed_data:
                            all_data.append(detailed_data)
                            self.log_message(f"  ✓ Successfully scraped: {detailed_data.get('name', 'Unknown')}")
                            
                            # Log summary of extracted data
                            emails_count = len(detailed_data.get('emails', []))
                            social_count = len(detailed_data.get('social_links', {}))
                            websites_count = len(detailed_data.get('websites', []))
                            
                            self.log_message(f"    Data summary: {emails_count} emails, {social_count} social platforms, {websites_count} websites")
                        else:
                            self.log_message(f"  ✗ Failed to scrape listing: {listing_url}")
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(page, len(all_data))
            
            # Stop if we hit empty page threshold (only when not using fixed range)
            if use_empty_page_logic and empty_pages >= self.EMPTY_PAGE_THRESHOLD:
                self.log_message(f"Stopping - {empty_pages} consecutive empty pages")
                break
            
            page += 1
            
            # Polite delay between search result pages (except for the last page)
            if not self.stop_requested and (end_page is None or page <= end_page):
                delay = self.get_random_delay('search')
                self.log_message(f"Waiting {delay:.1f} seconds before next search page...")
                time.sleep(delay)
        
        self.log_message(f"Scraping complete! Found {len(all_data)} listings")
        return all_data

    def stop_scraping(self):
        """Stop the scraping process"""
        self.stop_requested = True
