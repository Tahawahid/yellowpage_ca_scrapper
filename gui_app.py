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
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create sections
        self.create_input_section(main_frame)
        self.create_button_section(main_frame)
        self.create_progress_section(main_frame)
        self.create_log_section(main_frame)
        
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
                    "Pages: Start=1, End=5 (scrape pages 1-5) or Start=3, End=3 (scrape only page 3)")
        ttk.Label(input_frame, text=help_text, font=("Arial", 8), foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0)
        )
        
        # Configure input frame grid
        input_frame.columnconfigure(1, weight=1)
        
    def create_button_section(self, parent):
        """Create button section"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
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
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        progress_frame.columnconfigure(0, weight=1)
        
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.LabelFrame(parent, text="Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollable text widget
        self.log_text = tk.Text(log_frame, height=15, width=80, wrap=tk.WORD)
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
        main_frame.rowconfigure(3, weight=1)
        
    def log_message(self, message):
        """Add message to log text widget"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, page, total_listings):
        """Update progress display"""
        self.progress_label.config(text=f"Page {page} - Total listings found: {total_listings}")
        
    def validate_page_inputs(self):
        """Validate start and end page inputs"""
        try:
            start_page = int(self.start_page_var.get().strip())
            if start_page < 1:
                raise ValueError("Start page must be >= 1")
        except ValueError:
            messagebox.showerror("Error", "Start page must be a valid number >= 1")
            return None, None
            
        end_page = None
        end_page_text = self.end_page_var.get().strip()
        if end_page_text:
            try:
                end_page = int(end_page_text)
                if end_page < start_page:
                    raise ValueError("End page must be >= start page")
            except ValueError:
                messagebox.showerror("Error", "End page must be a valid number >= start page")
                return None, None
                
        return start_page, end_page
        
    def start_scraping(self):
        """Start the scraping process"""
        category = self.category_var.get().strip()
        location = self.location_var.get().strip()
        
        if not category or not location:
            messagebox.showerror("Error", "Please enter both category and location")
            return
            
        # Validate page inputs
        start_page, end_page = self.validate_page_inputs()
        if start_page is None:
            return
            
        # Update UI
        self.update_ui_for_scraping_start()
        
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
            args=(category, location, start_page, end_page)
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
            
        # Play completion sound
        SoundNotifier.play_completion_sound()
        
        messagebox.showinfo("Complete", f"Scraping completed! Found {len(self.scraped_data)} listings.")
        
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
                messagebox.showinfo("Success", f"Data saved successfully to:\n{file_path}")
                
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
                messagebox.showinfo("Success", f"Data saved successfully to:\n{file_path}")
                
        except Exception as e:
            error_msg = f"Error saving JSON: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", f"Failed to save JSON file:\n{str(e)}")
