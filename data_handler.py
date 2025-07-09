"""Data handling utilities"""

import json
import csv
import os
from datetime import datetime


class DataHandler:
    @staticmethod
    def save_as_csv(data, file_path):
        """Save data as CSV file"""
        if not data:
            raise ValueError("No data to save")
            
        # Create directory if it doesn't exist and file_path has a directory
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # First pass: collect all possible fieldnames
        all_fieldnames = set()
        flat_data = []
        
        for item in data:
            flat_item = {}
            
            # Copy basic fields
            basic_fields = ['name', 'phone', 'website', 'url', 'page_number', 'scraped_at', 'business_hours', 'scraping_status']
            for field in basic_fields:
                flat_item[field] = item.get(field, '')
            
            # Handle address fields
            if 'address' in item and item['address']:
                for addr_key, addr_value in item['address'].items():
                    flat_item[f'address_{addr_key}'] = addr_value or ''
            
            # Handle categories
            if 'categories' in item:
                flat_item['categories'] = '|'.join(item['categories']) if item['categories'] else ''
            
            # Handle phone numbers
            if 'phone_numbers' in item:
                phone_numbers = item['phone_numbers']
                for i, phone_info in enumerate(phone_numbers):
                    flat_item[f'phone_{i+1}_number'] = phone_info.get('number', '')
                    flat_item[f'phone_{i+1}_type'] = phone_info.get('type', '')
            
            # Handle websites
            if 'websites' in item:
                websites = item['websites']
                for i, website in enumerate(websites):
                    flat_item[f'website_{i+1}'] = website
            
            # Handle emails
            if 'emails' in item:
                flat_item['emails'] = '|'.join(item['emails']) if item['emails'] else ''
                flat_item['emails_count'] = len(item['emails'])
            
            # Handle social links
            if 'social_links' in item:
                social_links = item['social_links']
                for platform, links in social_links.items():
                    flat_item[f'social_{platform}'] = '|'.join(links) if links else ''
                    flat_item[f'social_{platform}_count'] = len(links)
            
            flat_data.append(flat_item)
            all_fieldnames.update(flat_item.keys())
        
        # Ensure all items have all fieldnames
        for flat_item in flat_data:
            for fieldname in all_fieldnames:
                if fieldname not in flat_item:
                    flat_item[fieldname] = ''
        
        # Write CSV
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            if flat_data:
                writer = csv.DictWriter(f, fieldnames=sorted(all_fieldnames))
                writer.writeheader()
                writer.writerows(flat_data)
    
    @staticmethod
    def save_as_json(data, file_path):
        """Save data as JSON file"""
        if not data:
            raise ValueError("No data to save")
            
        # Create directory if it doesn't exist and file_path has a directory
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def generate_filename(category, location, extension):
        """Generate filename based on category and location"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_location = location.replace('+', '_').replace(' ', '_')
        clean_category = category.replace(' ', '_')
        return f"yp_enhanced_{clean_category}_{clean_location}_{timestamp}.{extension}"
    
    @staticmethod
    def get_scraping_summary(data):
        """Get summary statistics of scraped data"""
        if not data:
            return {}
        
        total_listings = len(data)
        successful_scrapes = len([item for item in data if item.get('scraping_status') == 'success'])
        failed_scrapes = total_listings - successful_scrapes
        
        total_emails = sum(len(item.get('emails', [])) for item in data)
        total_social_platforms = sum(len(item.get('social_links', {})) for item in data)
        total_websites = sum(len(item.get('websites', [])) for item in data)
        
        listings_with_emails = len([item for item in data if item.get('emails')])
        listings_with_social = len([item for item in data if item.get('social_links')])
        listings_with_websites = len([item for item in data if item.get('websites')])
        
        # Additional statistics
        avg_emails_per_listing = total_emails / total_listings if total_listings > 0 else 0
        avg_social_per_listing = total_social_platforms / total_listings if total_listings > 0 else 0
        avg_websites_per_listing = total_websites / total_listings if total_listings > 0 else 0
        
        success_rate = (successful_scrapes / total_listings * 100) if total_listings > 0 else 0
        
        return {
            'total_listings': total_listings,
            'successful_scrapes': successful_scrapes,
            'failed_scrapes': failed_scrapes,
            'success_rate': round(success_rate, 2),
            'total_emails': total_emails,
            'total_social_platforms': total_social_platforms,
            'total_websites': total_websites,
            'listings_with_emails': listings_with_emails,
            'listings_with_social': listings_with_social,
            'listings_with_websites': listings_with_websites,
            'avg_emails_per_listing': round(avg_emails_per_listing, 2),
            'avg_social_per_listing': round(avg_social_per_listing, 2),
            'avg_websites_per_listing': round(avg_websites_per_listing, 2)
        }
