"""Main GUI application"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime

from scraper import YellowPagesScraper
from data_handler import DataHandler
from sound_utils import SoundNotifier
from config import Config


class YellowPagesApp:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(Config.WINDOW_SIZE)
        
        self.scraper = None
        self.scraped_data = []
        self.scraping_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create sections
        self.create_input_section(main_frame)
        self.create_delay_section(main_frame)
        self.create_button_section(main_frame)
        self.create_progress_section(main_frame)
        self.create_summary_section(main_frame)
        self.create_log_section(main_frame)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        self.configure_grid_weights(main_frame)
        
    def create_input_section(self, parent):
        """Create input section"""
        input_frame = ttk.LabelFrame(parent, text="Scraping Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Category input
        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar(value=Config.DEFAULT_CATEGORY)
        ttk.Entry(input_frame, textvariable=self.category_var, width=30).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2
        )
        
        # Location input
        ttk.Label(input_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar(value=Config.DEFAULT_LOCATION)
        ttk.Entry(input_frame, textvariable=self.location_var, width=30).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2
        )
        
        # Page range frame
        page_frame = ttk.Frame(input_frame)
        page_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Start page
        ttk.Label(page_frame, text="Start Page:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_page_var = tk.StringVar(value="1")
        start_page_entry = ttk.Entry(page_frame, textvariable=self.start_page_var, width=10)
        start_page_entry.grid(row=0, column=1, padx=(10, 20), pady=2)
        
                # End page
        ttk.Label(page_frame, text="End Page:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.end_page_var = tk.StringVar(value="")
        end_page_entry = ttk.Entry(page_frame, textvariable=self.end_page_var, width=10)
        end_page_entry.grid(row=0, column=3, padx=(10, 0), pady=2)
        
        # Help text for pages
        page_help = "Leave End Page empty to scrape until no more listings found"
        ttk.Label(page_frame, text=page_help, font=("Arial", 8), foreground="gray").grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0)
        )
        
        # Help text
        help_text = ("Examples:\n"
                    "Category: dentists, restaurants, plumbers, electricians\n"
                    "Location: Toronto+ON, Vancouver+BC, Montreal+QC\n"
                    "Pages: Start=1, End=5 (scrape pages 1-5) or Start=3, End=3 (scrape only page 3)\n"
                    "New Flow: Extract only URLs from search results, get all data from individual pages")
        ttk.Label(input_frame, text=help_text, font=("Arial", 8), foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0)
        )
        
        # Configure input frame grid
        input_frame.columnconfigure(1, weight=1)
        
    def create_delay_section(self, parent):
        """Create delay configuration section"""
        delay_frame = ttk.LabelFrame(parent, text="Delay Settings (seconds)", padding="10")
        delay_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create delay variables with defaults
        self.search_min_var = tk.StringVar(value=str(Config.DEFAULT_SEARCH_PAGE_MIN_DELAY))
        self.search_max_var = tk.StringVar(value=str(Config.DEFAULT_SEARCH_PAGE_MAX_DELAY))
        self.listing_min_var = tk.StringVar(value=str(Config.DEFAULT_LISTING_PAGE_MIN_DELAY))
        self.listing_max_var = tk.StringVar(value=str(Config.DEFAULT_LISTING_PAGE_MAX_DELAY))
        self.website_min_var = tk.StringVar(value=str(Config.DEFAULT_WEBSITE_MIN_DELAY))
        self.website_max_var = tk.StringVar(value=str(Config.DEFAULT_WEBSITE_MAX_DELAY))
        self.page_load_min_var = tk.StringVar(value=str(Config.DEFAULT_PAGE_LOAD_MIN_DELAY))
        self.page_load_max_var = tk.StringVar(value=str(Config.DEFAULT_PAGE_LOAD_MAX_DELAY))
        
        # Timeout and retry variables
        self.website_timeout_var = tk.StringVar(value=str(Config.DEFAULT_WEBSITE_TIMEOUT))
        self.website_retries_var = tk.StringVar(value=str(Config.DEFAULT_MAX_WEBSITE_RETRIES))
        self.page_timeout_var = tk.StringVar(value=str(Config.DEFAULT_PAGE_LOAD_TIMEOUT))
        self.page_retries_var = tk.StringVar(value=str(Config.DEFAULT_MAX_PAGE_RETRIES))
        
        # First row - Search page delays
        ttk.Label(delay_frame, text="Search Pages:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(delay_frame, text="Min:").grid(row=0, column=1, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.search_min_var, width=8).grid(row=0, column=2, pady=2)
        ttk.Label(delay_frame, text="Max:").grid(row=0, column=3, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.search_max_var, width=8).grid(row=0, column=4, pady=2)
        
        # Second row - Listing page delays
        ttk.Label(delay_frame, text="Listing Pages:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(delay_frame, text="Min:").grid(row=1, column=1, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.listing_min_var, width=8).grid(row=1, column=2, pady=2)
        ttk.Label(delay_frame, text="Max:").grid(row=1, column=3, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.listing_max_var, width=8).grid(row=1, column=4, pady=2)
        
        # Third row - Website delays
        ttk.Label(delay_frame, text="Websites:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(delay_frame, text="Min:").grid(row=2, column=1, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.website_min_var, width=8).grid(row=2, column=2, pady=2)
        ttk.Label(delay_frame, text="Max:").grid(row=2, column=3, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.website_max_var, width=8).grid(row=2, column=4, pady=2)
        
        # Fourth row - Page load delays
        ttk.Label(delay_frame, text="Page Load:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(delay_frame, text="Min:").grid(row=3, column=1, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.page_load_min_var, width=8).grid(row=3, column=2, pady=2)
        ttk.Label(delay_frame, text="Max:").grid(row=3, column=3, sticky=tk.W, padx=(10, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.page_load_max_var, width=8).grid(row=3, column=4, pady=2)
        
        # Fifth row - Timeouts
        ttk.Label(delay_frame, text="Website Timeout:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(delay_frame, textvariable=self.website_timeout_var, width=8).grid(row=4, column=1, padx=(10, 0), pady=2)
        ttk.Label(delay_frame, text="Page Timeout:").grid(row=4, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.page_timeout_var, width=8).grid(row=4, column=3, pady=2)
        
        # Sixth row - Retries
        ttk.Label(delay_frame, text="Website Retries:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(delay_frame, textvariable=self.website_retries_var, width=8).grid(row=5, column=1, padx=(10, 0), pady=2)
        ttk.Label(delay_frame, text="Page Retries:").grid(row=5, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        ttk.Entry(delay_frame, textvariable=self.page_retries_var, width=8).grid(row=5, column=3, pady=2)
        
        # Reset button
        ttk.Button(delay_frame, text="Reset to Defaults", command=self.reset_delays).grid(
            row=6, column=0, columnspan=2, pady=(10, 0), sticky=tk.W
        )
        
        # Help text for delays
        delay_help = ("Delay ranges help avoid being blocked. Search: between search result pages, "
                     "Listing: between individual listing pages, Website: between business websites, "
                     "Page Load: simulated loading time after each request")
        ttk.Label(delay_frame, text=delay_help, font=("Arial", 8), foreground="gray", wraplength=600).grid(
            row=7, column=0, columnspan=5, sticky=tk.W, pady=(10, 0)
        )
        
    def reset_delays(self):
        """Reset delay settings to defaults"""
        self.search_min_var.set(str(Config.DEFAULT_SEARCH_PAGE_MIN_DELAY))
        self.search_max_var.set(str(Config.DEFAULT_SEARCH_PAGE_MAX_DELAY))
        self.listing_min_var.set(str(Config.DEFAULT_LISTING_PAGE_MIN_DELAY))
        self.listing_max_var.set(str(Config.DEFAULT_LISTING_PAGE_MAX_DELAY))
        self.website_min_var.set(str(Config.DEFAULT_WEBSITE_MIN_DELAY))
        self.website_max_var.set(str(Config.DEFAULT_WEBSITE_MAX_DELAY))
        self.page_load_min_var.set(str(Config.DEFAULT_PAGE_LOAD_MIN_DELAY))
        self.page_load_max_var.set(str(Config.DEFAULT_PAGE_LOAD_MAX_DELAY))
        self.website_timeout_var.set(str(Config.DEFAULT_WEBSITE_TIMEOUT))
        self.website_retries_var.set(str(Config.DEFAULT_MAX_WEBSITE_RETRIES))
        self.page_timeout_var.set(str(Config.DEFAULT_PAGE_LOAD_TIMEOUT))
        self.page_retries_var.set(str(Config.DEFAULT_MAX_PAGE_RETRIES))
        
    def create_button_section(self, parent):
        """Create button section"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(
            button_frame, text="Start Scraping", command=self.start_scraping
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.save_csv_button = ttk.Button(
            button_frame, text="Save as CSV", command=self.save_as_csv, state=tk.DISABLED
        )
        self.save_csv_button.grid(row=0, column=2, padx=(0, 10))
        
        self.save_json_button = ttk.Button(
            button_frame, text="Save as JSON", command=self.save_as_json, state=tk.DISABLED
        )
        self.save_json_button.grid(row=0, column=3)
        
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        progress_frame.columnconfigure(0, weight=1)
        
    def create_summary_section(self, parent):
        """Create summary section"""
        summary_frame = ttk.LabelFrame(parent, text="Live Summary", padding="10")
        summary_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create summary labels in a grid
        self.summary_labels = {}
        
        # Row 1
        ttk.Label(summary_frame, text="Total Listings:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.summary_labels['total'] = ttk.Label(summary_frame, text="0", foreground="blue")
        self.summary_labels['total'].grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(summary_frame, text="Successful:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.summary_labels['successful'] = ttk.Label(summary_frame, text="0", foreground="green")
        self.summary_labels['successful'].grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(summary_frame, text="Failed:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.summary_labels['failed'] = ttk.Label(summary_frame, text="0", foreground="red")
        self.summary_labels['failed'].grid(row=0, column=5, sticky=tk.W)
        
        # Row 2
        ttk.Label(summary_frame, text="Total Emails:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.summary_labels['emails'] = ttk.Label(summary_frame, text="0", foreground="purple")
        self.summary_labels['emails'].grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(5, 0))
        
        ttk.Label(summary_frame, text="Social Platforms:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.summary_labels['social'] = ttk.Label(summary_frame, text="0", foreground="orange")
        self.summary_labels['social'].grid(row=1, column=3, sticky=tk.W, padx=(0, 20), pady=(5, 0))
        
        ttk.Label(summary_frame, text="Websites:").grid(row=1, column=4, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.summary_labels['websites'] = ttk.Label(summary_frame, text="0", foreground="brown")
        self.summary_labels['websites'].grid(row=1, column=5, sticky=tk.W, pady=(5, 0))
        
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.LabelFrame(parent, text="Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollable text widget
        self.log_text = tk.Text(log_frame, height=20, width=100, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def configure_grid_weights(self, main_frame):
        """Configure grid weights for responsive layout"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def log_message(self, message):
        """Add message to log text widget"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, page, total_listings):
        """Update progress display"""
        self.progress_label.config(text=f"Page {page} - Total listings scraped: {total_listings}")
        self.update_summary()
        
    def update_summary(self):
        """Update summary statistics"""
        if not self.scraped_data:
            return
            
        summary = DataHandler.get_scraping_summary(self.scraped_data)
        
        self.summary_labels['total'].config(text=str(summary.get('total_listings', 0)))
        self.summary_labels['successful'].config(text=str(summary.get('successful_scrapes', 0)))
        self.summary_labels['failed'].config(text=str(summary.get('failed_scrapes', 0)))
        self.summary_labels['emails'].config(text=str(summary.get('total_emails', 0)))
        self.summary_labels['social'].config(text=str(summary.get('total_social_platforms', 0)))
        self.summary_labels['websites'].config(text=str(summary.get('total_websites', 0)))
        
    def validate_inputs(self):
        """Validate all input fields"""
        # Validate category and location
        category = self.category_var.get().strip()
        location = self.location_var.get().strip()
        
        if not category or not location:
            messagebox.showerror("Error", "Please enter both category and location")
            return None
        
        # Validate page inputs
        try:
            start_page = int(self.start_page_var.get().strip())
            if start_page < 1:
                raise ValueError("Start page must be >= 1")
        except ValueError:
            messagebox.showerror("Error", "Start page must be a valid number >= 1")
            return None
            
        end_page = None
        end_page_text = self.end_page_var.get().strip()
        if end_page_text:
            try:
                end_page = int(end_page_text)
                if end_page < start_page:
                    raise ValueError("End page must be >= start page")
            except ValueError:
                messagebox.showerror("Error", "End page must be a valid number >= start page")
                return None
        
        # Validate delay settings
        try:
            delay_settings = {
                'search_min': float(self.search_min_var.get().strip()),
                'search_max': float(self.search_max_var.get().strip()),
                'listing_min': float(self.listing_min_var.get().strip()),
                'listing_max': float(self.listing_max_var.get().strip()),
                'website_min': float(self.website_min_var.get().strip()),
                'website_max': float(self.website_max_var.get().strip()),
                'page_load_min': float(self.page_load_min_var.get().strip()),
                'page_load_max': float(self.page_load_max_var.get().strip()),
                'website_timeout': float(self.website_timeout_var.get().strip()),
                'website_retries': int(self.website_retries_var.get().strip()),
                'page_timeout': float(self.page_timeout_var.get().strip()),
                'page_retries': int(self.page_retries_var.get().strip())
            }
            
            # Validate delay ranges
            if delay_settings['search_min'] >= delay_settings['search_max']:
                raise ValueError("Search page min delay must be less than max delay")
            if delay_settings['listing_min'] >= delay_settings['listing_max']:
                raise ValueError("Listing page min delay must be less than max delay")
            if delay_settings['website_min'] >= delay_settings['website_max']:
                raise ValueError("Website min delay must be less than max delay")
            if delay_settings['page_load_min'] >= delay_settings['page_load_max']:
                raise ValueError("Page load min delay must be less than max delay")
            
            # Validate positive values
            for key, value in delay_settings.items():
                if value <= 0:
                    raise ValueError(f"{key} must be positive")
                    
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid delay settings: {str(e)}")
            return None
        
        return {
            'category': category,
            'location': location,
            'start_page': start_page,
            'end_page': end_page,
            'delay_settings': delay_settings
        }
        
    def start_scraping(self):
        """Start the scraping process"""
        # Validate inputs
        inputs = self.validate_inputs()
        if not inputs:
            return
            
        # Show warning about enhanced scraping
        warning_msg = ("Enhanced scraping is enabled. This will:\n"
                      "• Extract only URLs from search result pages\n"
                      "• Visit each individual listing page for complete business data\n"
                      "• Visit business websites to find social media and emails\n"
                      "• Use your custom delay settings to avoid being blocked\n"
                      "• Take significantly longer than basic scraping\n\n"
                      "Continue with enhanced scraping?")
        
        if not messagebox.askyesno("Enhanced Scraping", warning_msg):
            return
            
        # Update UI
        self.update_ui_for_scraping_start()
        
        # Clear previous data
        self.scraped_data = []
        self.log_text.delete(1.0, tk.END)
        self.update_summary()
        
        # Create scraper instance with delay settings
        self.scraper = YellowPagesScraper(
            progress_callback=self.update_progress,
            log_callback=self.log_message,
            delay_settings=inputs['delay_settings']
        )
        
        # Start scraping in a separate thread
        self.scraping_thread = threading.Thread(
            target=self.run_scraping_thread,
            args=(inputs['category'], inputs['location'], inputs['start_page'], inputs['end_page'])
        )
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
        
    def update_ui_for_scraping_start(self):
        """Update UI when scraping starts"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_csv_button.config(state=tk.DISABLED)
        self.save_json_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        
    def run_scraping_thread(self, category, location, start_page, end_page):
        """Run scraping in separate thread"""
        try:
            self.scraped_data = self.scraper.run_scraper(category, location, start_page, end_page)
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
            
        # Update final summary
        self.update_summary()
        
        # Play completion sound
        SoundNotifier.play_completion_sound()
        
        # Show detailed completion message
        summary = DataHandler.get_scraping_summary(self.scraped_data)
        completion_msg = (f"Scraping completed!\n\n"
                         f"Total listings: {summary.get('total_listings', 0)}\n"
                         f"Successful: {summary.get('successful_scrapes', 0)}\n"
                         f"Failed: {summary.get('failed_scrapes', 0)}\n"
                         f"Total emails found: {summary.get('total_emails', 0)}\n"
                         f"Social platforms found: {summary.get('total_social_platforms', 0)}\n"
                         f"Websites found: {summary.get('total_websites', 0)}")
        
        messagebox.showinfo("Scraping Complete", completion_msg)
        
    def scraping_error(self, error_message):
        """Handle scraping error"""
        self.progress_bar.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message(f"Error: {error_message}")
        
        # Play error sound
        SoundNotifier.play_error_sound()
        
        messagebox.showerror("Error", f"Scraping failed: {error_message}")
        
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraper:
            self.scraper.stop_scraping()
            self.log_message("Stop requested...")
            
    def save_as_csv(self):
        """Save scraped data as CSV file"""
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to save")
            return
            
        try:
            # Generate default filename
            category = self.category_var.get().strip()
            location = self.location_var.get().strip()
            default_filename = DataHandler.generate_filename(category, location, "csv")
            
            # Open file dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV File",
                initialfile=default_filename
            )
            
            if file_path:
                DataHandler.save_as_csv(self.scraped_data, file_path)
                self.log_message(f"Data saved to {file_path}")
                
                # Show summary in save confirmation
                summary = DataHandler.get_scraping_summary(self.scraped_data)
                save_msg = (f"Data saved successfully to:\n{file_path}\n\n"
                           f"Summary:\n"
                           f"• {summary.get('total_listings', 0)} listings\n"
                           f"• {summary.get('total_emails', 0)} emails\n"
                           f"• {summary.get('total_social_platforms', 0)} social links\n"
                           f"• {summary.get('total_websites', 0)} websites")
                
                messagebox.showinfo("Save Successful", save_msg)
                
        except Exception as e:
            error_msg = f"Error saving CSV: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", f"Failed to save CSV file:\n{str(e)}")
    
    def save_as_json(self):
        """Save scraped data as JSON file"""
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to save")
            return
            
        try:
            # Generate default filename
            category = self.category_var.get().strip()
            location = self.location_var.get().strip()
            default_filename = DataHandler.generate_filename(category, location, "json")
            
            # Open file dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save JSON File",
                initialfile=default_filename
            )
            
            if file_path:
                DataHandler.save_as_json(self.scraped_data, file_path)
                self.log_message(f"Data saved to {file_path}")
                
                # Show summary in save confirmation
                summary = DataHandler.get_scraping_summary(self.scraped_data)
                save_msg = (f"Data saved successfully to:\n{file_path}\n\n"
                           f"Summary:\n"
                           f"• {summary.get('total_listings', 0)} listings\n"
                           f"• {summary.get('total_emails', 0)} emails\n"
                           f"• {summary.get('total_social_platforms', 0)} social links\n"
                           f"• {summary.get('total_websites', 0)} websites")
                
                messagebox.showinfo("Save Successful", save_msg)
                
        except Exception as e:
            error_msg = f"Error saving JSON: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", f"Failed to save JSON file:\n{str(e)}")
