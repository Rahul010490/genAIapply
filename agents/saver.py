import csv
from datetime import datetime
import os

class DataSaver:
    def __init__(self, data, filename='output.csv'):
        self.data = data
        self.base_filename = filename
        
    def save_to_csv(self):
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_parts = os.path.splitext(self.base_filename)
            unique_filename = f"{filename_parts[0]}_{timestamp}{filename_parts[1]}"
            
            # Try saving in current directory first
            with open(unique_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(self.data)
            print(f"✅ Data successfully saved to: {unique_filename}")
            
        except Exception as e:
            print(f"❌ Error saving to current directory: {str(e)}")
            try:
                # Try desktop as fallback
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                fallback_path = os.path.join(desktop_path, unique_filename)
                with open(fallback_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(self.data)
                print(f"✅ Data saved to desktop: {fallback_path}")
            except Exception as e2:
                print(f"❌ Error saving to desktop: {str(e2)}")
                # Last resort: save in temp directory
                import tempfile
                temp_path = os.path.join(tempfile.gettempdir(), unique_filename)
                with open(temp_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(self.data)
                print(f"✅ Data saved to temp directory: {temp_path}")
