from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class HTMLNavigator:
    def __init__(self, url):
        self.url = url
        self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')  # Start maximized
        chrome_options.add_argument('--disable-gpu')  # Disable GPU usage
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Create a fresh Chrome instance with automatic driver management
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Make selenium control less detectable
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def load_html(self):
        try:
            # Load the page
            self.driver.get(self.url)
            print("\n🔐 LinkedIn Authentication Required")
            print("Please complete these steps:")
            print("1. Log in to LinkedIn in the opened browser")
            print("2. Complete any verification if needed")
            print("3. Wait for the job listings to load")
            print("4. Scroll down to load more jobs")
            print("5. Press Enter ONLY after you can see multiple job listings\n")
            
            print("\nWaiting for manual interaction...")
            print("1. Log in to LinkedIn")
            print("2. Wait for the job listings page to load")
            print("3. Scroll down manually to ensure jobs are visible")
            input("After completing these steps, press Enter to continue...\n")
            
            # Additional wait after user input
            time.sleep(3)
            
            print("\n📜 Loading job listings...")
            
            # Check for login status
            print("\nVerifying LinkedIn authentication...")
            try:
                # Look for common elements that indicate we're logged in
                login_button = self.driver.find_elements(By.CSS_SELECTOR, "a[data-tracking-control-name='guest_homepage-basic_sign-in-button']")
                if login_button:
                    print("⚠️ Please log in to LinkedIn and wait for the job listings page")
                    input("Press Enter AFTER you've logged in and can see job listings...\n")
                    time.sleep(5)  # Wait for page to settle after login
                
                # Verify we're on the jobs page
                print("Waiting for job search results to load...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list"))
                )
            except TimeoutException:
                print("⚠️ Job listings taking longer to load than expected")
                print("Please verify you can see job listings on the page")
                input("Press Enter when you can see the listings...\n")
            
            # Load more jobs through scrolling
            print("\nLoading more job listings...")
            total_scroll_attempts = 4
            jobs_found = False
            
            for i in range(total_scroll_attempts):
                print(f"\nScroll attempt {i + 1}/{total_scroll_attempts}")
                
                # Scroll and check for jobs
                self._scroll_page()
                time.sleep(3)
                
                jobs = self.driver.find_elements(By.CSS_SELECTOR, 
                    "div.job-card-container, li.jobs-search-results__list-item, div.base-card"
                )
                
                if jobs:
                    jobs_found = True
                    print(f"Found {len(jobs)} jobs")
                else:
                    print("No jobs visible yet - continuing to scroll...")
                
                # Additional small scrolls to ensure content loads
                for _ in range(2):
                    self.driver.execute_script("window.scrollBy(0, 200);")
                    time.sleep(1)
            
            if not jobs_found:
                print("\n⚠️ Still no jobs visible. Please verify manually:")
                print("1. You are logged into LinkedIn")
                print("2. You can see job listings on the page")
                input("Press Enter if you can see job listings, Ctrl+C to exit if not...")
            
            # Final wait for dynamic content
            print("\nWaiting for final content load...")
            time.sleep(5)
            
            # Final verification with retry
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Check multiple selectors
                    print("\nVerifying job listings...")
                    job_elements = (
                        self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container") or
                        self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item") or
                        self.driver.find_elements(By.CSS_SELECTOR, "div.base-card")
                    )
                    
                    if job_elements:
                        print(f"\n✅ Successfully verified {len(job_elements)} job listings")
                        # Save page source for debugging
                        with open('linkedin_page.html', 'w', encoding='utf-8') as f:
                            page_source = self.driver.page_source
                            f.write(page_source)
                            print("\nSaved page source to linkedin_page.html for inspection")
                        return page_source, self.driver
                        
                    if retry < max_retries - 1:
                        print("⚠️ No jobs found - retrying verification...")
                        # Try to inspect what elements are actually present
                        print("\nChecking page structure...")
                        elements = self.driver.find_elements(By.CSS_SELECTOR, "div, ul, li")
                        with open('page_elements.txt', 'w', encoding='utf-8') as f:
                            for elem in elements[:50]:  # First 50 elements
                                try:
                                    f.write(f"Element: {elem.tag_name}, Class: {elem.get_attribute('class')}\n")
                                except:
                                    continue
                        time.sleep(3)
                        self._scroll_page()
                        continue
                        
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"⚠️ Verification error - retry {retry + 1}/{max_retries}")
                        time.sleep(3)
                        continue
            
            print("\n❌ Could not verify job listings. Please check:")
            print("1. You are logged into LinkedIn")
            print("2. Job listings are visible on the page")
            print("3. Try scrolling manually before pressing Enter")
            return None, None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.driver.quit()
            if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                print("❌ LinkedIn rate limit detected. Try again later or use a different IP address.")
            return None, None

    def _extract_job_listings(self):
        """Extract basic job listing data"""
        return self.driver.page_source
            
    def _scroll_page(self):
        """Scroll the page to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
