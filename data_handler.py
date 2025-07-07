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
        
        # Flatten data for CSV
        flat_data = []
        for item in data:
            flat_item = {}
            # Copy all non-nested fields
            for key, value in item.items():
                if key != 'address':
                    if key == 'categories':
                        flat_item[key] = '|'.join(value) if isinstance(value, list) else str(value)
                    else:
                        flat_item[key] = value
            
            # Add address fields
            if 'address' in item and item['address']:
                for addr_key, addr_value in item['address'].items():
                    flat_item[f'address_{addr_key}'] = addr_value
            
            flat_data.append(flat_item)
        
        # Write CSV
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            if flat_data:
                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
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
        return f"yp_{clean_category}_{clean_location}_{timestamp}.{extension}"
