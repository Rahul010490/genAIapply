import csv
import os
from datetime import datetime
import logging

class DataSaver:
    def __init__(self, data, filename='linkedin_jobs.csv'):
        self.data = data
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def save_to_csv(self):
        """Save the extracted data to a CSV file"""
        if not self.data:
            print("\n⚠️ No data to save")
            return
            
        # Use absolute path for Jobs directory
        jobs_dir = os.path.join(os.getcwd(), 'Jobs')
        if not os.path.exists(jobs_dir):
            try:
                os.makedirs(jobs_dir)
            except PermissionError as e:
                print(f"❌ Error creating directory {jobs_dir}: {str(e)}")
                return
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"linkedin_jobs_{timestamp}.csv"
        filepath = os.path.join(jobs_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                
                # Write header
                writer.writerow([
                    'Job Title',
                    'Company',
                    'Location',
                    'Job Link',
                    'Description'
                ])
                
                # Write data
                for row in self.data:
                    writer.writerow(row)
                    
            print(f"✅ Data successfully saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to save data: {str(e)}")
            logging.error(f"Error saving data: {str(e)}")
