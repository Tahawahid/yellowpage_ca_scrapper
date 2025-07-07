import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from urllib.parse import urljoin
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import winsound  # For Windows sound notification
import sys

class YellowPagesScraper:
    def __init__(self, progress_callback=None, log_callback=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.stop_requested = False
        
        # Configuration
        self.BASE_URL = "https://www.yellowpages.ca/search/si/{page}/{category}/{location}"
        self.MIN_DELAY = 8
        self.MAX_DELAY = 12
        self.EMPTY_PAGE_THRESHOLD = 2
    
    def clean_text(self, text):
        return ' '.join(str(text).strip().split()) if text else None

    def get_random_delay(self):
        return random.uniform(self.MIN_DELAY, self.MAX_DELAY)

    def log_message(self, message):
        if self.log_callback:
            self.log_callback(message)
        print(message)

    def scrape_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.log_message(f"Error scraping {url}: {str(e)}")
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

    def run_scraper(self, category, location):
        all_data = []
        empty_pages = 0
        page = 1
        
        self.log_message(f"Starting scrape for {category} in {location}...")
        
        while not self.stop_requested:
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
            
            # Stop if we hit empty page threshold
            if empty_pages >= self.EMPTY_PAGE_THRESHOLD:
                self.log_message(f"Stopping - {empty_pages} consecutive empty pages")
                break
            
            page += 1
            
            # Polite delay
            if not self.stop_requested:
                delay = self.get_random_delay()
                self.log_message(f"Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        self.log_message(f"Scraping complete! Found {len(all_data)} listings from {page} pages")
        return all_data

    def stop_scraping(self):
        self.stop_requested = True


class YellowPagesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yellow Pages Scraper")
        self.root.geometry("800x600")
        
        self.scraper = None
        self.scraped_data = []
        self.scraping_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Scraping Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Category input
        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar(value="dentists")
        ttk.Entry(input_frame, textvariable=self.category_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Location input
        ttk.Label(input_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar(value="Toronto+ON")
        ttk.Entry(input_frame, textvariable=self.location_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Help text
        help_text = "Examples:\nCategory: dentists, restaurants, plumbers, electricians\nLocation: Toronto+ON, Vancouver+BC, Montreal+QC"
        ttk.Label(input_frame, text=help_text, font=("Arial", 8), foreground="gray").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.save_csv_button = ttk.Button(button_frame, text="Save as CSV", command=self.save_as_csv, state=tk.DISABLED)
        self.save_csv_button.grid(row=0, column=2, padx=(0, 10))
        
        self.save_json_button = ttk.Button(button_frame, text="Save as JSON", command=self.save_as_json, state=tk.DISABLED)
        self.save_json_button.grid(row=0, column=3)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollable text widget
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        input_frame.columnconfigure(1, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log_message(self, message):
        """Add message to log text widget"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, page, total_listings):
        """Update progress display"""
        self.progress_label.config(text=f"Page {page} - Total listings found: {total_listings}")
        
    def start_scraping(self):
        """Start the scraping process"""
        category = self.category_var.get().strip()
        location = self.location_var.get().strip()
        
        if not category or not location:
            messagebox.showerror("Error", "Please enter both category and location")
            return
            
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_csv_button.config(state=tk.DISABLED)
        self.save_json_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        # Clear previous data
        self.scraped_data = []
        self.log_text.delete(1.0, tk.END)
        
        # Create scraper instance
        self.scraper = YellowPagesScraper(
            progress_callback=self.update_progress,
            log_callback=self.log_message
        )
        
        # Start scraping in a separate thread
        self.scraping_thread = threading.Thread(
            target=self.run_scraping_thread,
            args=(category, location)
        )
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
        
    def run_scraping_thread(self, category, location):
        """Run scraping in separate thread"""
        try:
            self.scraped_data = self.scraper.run_scraper(category, location)
            self.root.after(0, self.scraping_completed)
        except Exception as e:
            self.root.after(0, lambda: self.scraping_error(str(e)))
            
    def scraping_completed(self):
        """Handle scraping completion"""
        self.progress_bar.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.scraped_data:
            self.save_csv_button.config(state=tk.NORMAL)
            self.save_json_button.config(state=tk.NORMAL)
            
        # Play completion sound
        self.play_completion_sound()
        
        messagebox.showinfo("Complete", f"Scraping completed! Found {len(self.scraped_data)} listings.")
        
    def scraping_error(self, error_message):
        """Handle scraping error"""
        self.progress_bar.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message(f"Error: {error_message}")
        messagebox.showerror("Error", f"Scraping failed: {error_message}")
        
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraper:
            self.scraper.stop_scraping()
            self.log_message("Stop requested...")
        
    def play_completion_sound(self):
        """Play sound when scraping is complete"""
        try:
            # For Windows
            if sys.platform == "win32":
                winsound.MessageBeep(winsound.MB_OK)
            else:
                # For Unix/Linux/Mac - using system bell
                print('\a')  # Bell character
        except Exception as e:
            self.log_message(f"Could not play sound: {e}")
    
    def save_as_csv(self):
        """Save scraped data as CSV file"""
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to save")
            return
            
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV File"
        )

        if file_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Flatten data for CSV
                flat_data = []
                for item in self.scraped_data:
                    flat_item = {**item, **{f"address_{k}": v for k, v in item['address'].items()}}
                    flat_item['categories'] = '|'.join(flat_item['categories'])
                    del flat_item['address']
                    flat_data.append(flat_item)
                
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flat_data)
                
                self.log_message(f"Data saved to {file_path}")
                messagebox.showinfo("Success", f"Data saved successfully to:\n{file_path}")
                
            except Exception as e:
                self.log_message(f"Error saving CSV: {e}")
                messagebox.showerror("Error", f"Failed to save CSV file:\n{e}")
    
    def save_as_json(self):
        """Save scraped data as JSON file"""
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to save")
            return
            
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON File"
        )
        
        if file_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
                
                self.log_message(f"Data saved to {file_path}")
                messagebox.showinfo("Success", f"Data saved successfully to:\n{file_path}")
                
            except Exception as e:
                self.log_message(f"Error saving JSON: {e}")
                messagebox.showerror("Error", f"Failed to save JSON file:\n{e}")


def main():
    root = tk.Tk()
    app = YellowPagesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
