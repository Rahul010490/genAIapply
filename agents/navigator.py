from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
import time
import random
import logging

class HTMLNavigator:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.ua = UserAgent()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_driver(self):
        """Initialize Chrome driver with basic settings"""
        options = Options()
        
        # Set random user agent
        user_agent = self.ua.random
        options.add_argument(f'user-agent={user_agent}')
        
        # Basic browser settings
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logging.info("Driver setup successful")
            return True
        except WebDriverException as e:
            logging.error(f"Driver setup failed: {str(e)}")
            return False

    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add small random delay"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def load_html(self):
        """Load the webpage and get its HTML content"""
        if not self.setup_driver():
            return None, None
            
        try:
            print("\n📜 Loading job listings...")
            self.driver.get(self.url)
            
            # Short wait for content to load
            self.random_delay()
            
            # Look for job listings
            print("\nLooking for job listings...")
            jobs = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            
            if not jobs:
                print("\nTrying alternative selectors...")
                # Try alternative selectors
                selectors = [
                    ".job-card-container",
                    ".jobs-search-results__list-item",
                    ".job-card-list__entity-lockup",
                    ".base-card" # Another common LinkedIn class for job cards
                ]
                
                for selector in selectors:
                    jobs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if jobs:
                        print(f"\n✅ Found {len(jobs)} jobs using selector: {selector}")
                        break
            
            if jobs:
                print(f"\n✅ Successfully found {len(jobs)} job listings")
                
                # Save page source for inspection
                with open('linkedin_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print("\nSaved page source to linkedin_page.html for inspection")
                
                return self.driver.page_source, self.driver
            else:
                print("\n❌ No job listings found on the page")
                return None, None
                
        except Exception as e:
            logging.error(f"Error loading page: {str(e)}")
            print(f"\n❌ Error loading page: {str(e)}")
            return None, None
