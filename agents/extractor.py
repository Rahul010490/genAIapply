from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import random

class HTMLDataExtractor:
    def __init__(self, page_source, driver):
        self.soup = BeautifulSoup(page_source, 'html.parser')
        self.driver = driver
        
        # Save parsed HTML and analyze structure
        with open('parsed_content.html', 'w', encoding='utf-8') as f:
            f.write("=== Page Structure Analysis ===\n\n")
            
            # Log all divs with class names containing relevant keywords
            f.write("=== Relevant Divs ===\n")
            for div in self.soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['job', 'card', 'search', 'result', 'list'])):
                f.write(f"\nElement: div\n")
                f.write(f"Classes: {div.get('class', [])}\n")
                f.write("First level content:\n")
                f.write(div.prettify()[:500] + "...\n")  # First 500 chars
                f.write("-" * 80 + "\n")
            
            # Log the full HTML for reference
            f.write("\n=== Full HTML ===\n")
            f.write(self.soup.prettify())

    def extract_data(self):
        print("\nSearching for job listings...")
        
        # Create debug file
        with open('debug_output.txt', 'w', encoding='utf-8') as debug_file:
            debug_file.write("=== LinkedIn Job Scraper Debug Output ===\n\n")
            debug_file.write("Raw HTML Source:\n")
            debug_file.write(self.soup.prettify())
            debug_file.write("\n\n=== Found Elements ===\n")
        
        # Log the parsing process
        with open('scraping_log.txt', 'w', encoding='utf-8') as log:
            log.write("=== LinkedIn Scraping Log ===\n\n")
            
            # Find jobs container first
            log.write("Searching for job containers...\n")
        container_selectors = [
            "div.jobs-search-results-list",
            "ul.jobs-search__results-list",
            "div.scaffold-layout__list",
            "main.scaffold-layout__list-container",
            "div.jobs-search__results-list"
        ]
        
        jobs_container = None
        for selector in container_selectors:
            jobs_container = self.soup.select_one(selector)
            if jobs_container:
                print(f"Found jobs container using: {selector}")
                with open('scraping_log.txt', 'a', encoding='utf-8') as log:
                    log.write(f"Found container with selector: {selector}\n")
                    log.write("Container HTML:\n")
                    log.write(jobs_container.prettify())
                    log.write("\n---\n")
                break
        
        if not jobs_container:
            print("⚠️ Could not find jobs container")
            return []
            
        # Find individual job cards within the container
        job_cards = []
        card_selectors = [
            "div.job-card-container",                      # Most common
            "li.jobs-search-results__list-item",          # Search results
            "div.base-card--link",                        # Alternative
            "div.job-card-list__entity",                  # List view
            "article.job-card-container"                  # Article format
        ]
        
        for selector in card_selectors:
            job_cards = self.soup.select(selector)
            if job_cards:
                print(f"Found job cards using selector: {selector}")
            with open('scraping_log.txt', 'a', encoding='utf-8') as log:
                log.write(f"\nFound {len(job_cards)} cards using {selector}\n")
                if job_cards:
                    log.write("\nFirst job card structure:\n")
                    first_card = job_cards[0]
                    log.write("Classes: " + str(first_card.get('class', [])) + "\n")
                    log.write("HTML Content:\n")
                    log.write(first_card.prettify())
                    log.write("\nAvailable elements:\n")
                    for elem in first_card.find_all(['h3', 'h4', 'a', 'span']):
                        log.write(f"{elem.name}: {elem.get('class', [])}\n")
                break
        
        if not job_cards:
            print("\n⚠️ No job listings found in the page source.")
            print("This might happen if:")
            print("1. The page hasn't fully loaded")
            print("2. LinkedIn's structure has changed")
            print("3. You're not logged in or need to complete verification")
            return []
            
        total_jobs = len(job_cards)
        max_jobs = min(25, total_jobs)  # Process up to 25 jobs
        print(f"\nFound {total_jobs} job listings")
        print(f"Processing first {max_jobs} listings...\n")
        
        data = []
        for index, job in enumerate(job_cards[:max_jobs]):
            try:
                # Extract basic info
                # Try different selectors for job details
                # Comprehensive selectors for all LinkedIn layouts
                # Look for job title in multiple locations
                title_selectors = [
                    'h3.base-search-card__title',
                    'h3.job-search-card__title',
                    'h3.job-card-list__title',
                    'h3.scaffold-layout__list-item-title',
                    '.job-details-jobs-unified-top-card__job-title',
                    '.job-card-container__title',
                    'a[data-control-name="job_card_title"]'
                ]
                title = None
                for selector in title_selectors:
                    title = job.select_one(selector)
                    if title:
                        break
                
                # Get the company name
                company_selectors = [
                    'h4.base-search-card__subtitle',
                    'h4.job-search-card__subtitle',
                    'a.job-card-container__company-name',
                    '.job-card-container__primary-description',
                    '.job-details-jobs-unified-top-card__company-name',
                    'span[data-tracking-control-name="public_jobs_mob_company_name"]'
                ]
                company = None
                for selector in company_selectors:
                    company = job.select_one(selector)
                    if company:
                        break
                
                # Get the location
                location_selectors = [
                    'span.job-search-card__location',
                    'div.job-card-container__metadata-item',
                    '.job-details-jobs-unified-top-card__bullet',
                    '.job-card-container__metadata-wrapper'
                ]
                location = None
                for selector in location_selectors:
                    location = job.select_one(selector)
                    if location:
                        break
                
                # Get the job link
                link_selectors = [
                    'a.base-card__full-link',
                    'a.job-card-list__title',
                    'a[data-tracking-control-name="public_jobs_jserp-result_search-card"]'
                ]
                link = None
                for selector in link_selectors:
                    link = job.select_one(selector)
                    if link:
                        break
                
                # Validate and extract required data
                if not (title and link):
                    print(f"Skipping job {index + 1} - missing title or link")
                    continue
                
                # Clean and process job URL first
                job_url = link.get('href', '').split('?')[0]  # Remove query parameters
                if not job_url:
                    print(f"Skipping job {index + 1} - invalid URL")
                    continue
                
                if not job_url.startswith('http'):
                    job_url = f"https://www.linkedin.com{job_url}"
                
                # Extract text content
                job_title = title.get_text(strip=True)
                job_company = company.get_text(strip=True) if company else "Company not listed"
                job_location = location.get_text(strip=True) if location else "Location not listed"
                
                print(f"Processing {index + 1}/{max_jobs}: {job_title}")
                
                # Log extracted data
                with open('debug_output.txt', 'a', encoding='utf-8') as debug_file:
                    debug_file.write(f"\n=== Job {index + 1} Details ===\n")
                    debug_file.write(f"Title: {job_title}\n")
                    debug_file.write(f"Company: {job_company}\n")
                    debug_file.write(f"Location: {job_location}\n")
                    debug_file.write(f"URL: {job_url}\n")
                    debug_file.write("Raw HTML:\n")
                    debug_file.write(job.prettify())
                    debug_file.write("\n---\n")
                
                # Get and log job description
                description = self._get_job_description(job_url)
                with open('debug_output.txt', 'a', encoding='utf-8') as debug_file:
                    debug_file.write("\nJob Description:\n")
                    debug_file.write(description)
                    debug_file.write("\n---\n")
                
                data.append([
                    job_title,
                    job_company,
                    job_location,
                    job_url,
                    description
                ])
                
            except Exception as e:
                print(f"Error processing job: {str(e)}")
                continue
        
        # Add summary
        processed = len(data)
        print(f"\n✨ Successfully extracted {processed} out of {max_jobs} job listings")
        if processed < max_jobs:
            print(f"⚠️ {max_jobs - processed} listings were skipped due to missing or invalid data")
        
        # Cleanup
        self.driver.quit()
        return data
        
    def _get_job_description(self, job_url):
        """Get job description by navigating to the job URL"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Navigate to job details page
                self.driver.get(job_url)
                
                # Random delay between 1.5 and 3 seconds to avoid rate limiting
                time.sleep(random.uniform(1.5, 3))
                
                # Wait for and get description using multiple possible selectors
                description_selectors = [
                    "jobs-description-content__text",         # Modern layout
                    "jobs-description__content",             # Common layout
                    "jobs-description-content__container",   # Alternative layout
                    "jobs-description",                      # Basic layout
                    "job-details"                           # Fallback layout
                ]
                
                # Try both CSS selector and class name approaches
                for selector in description_selectors:
                    try:
                        # Try CSS selector first
                        description = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f".{selector}"))
                        )
                        if description:
                            return description.text.strip()
                    except (TimeoutException, StaleElementReferenceException):
                        try:
                            # Try direct class name as fallback
                            description = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, selector))
                            )
                            if description:
                                return description.text.strip()
                        except (TimeoutException, StaleElementReferenceException):
                            continue
                
                # If no selectors worked, try a broader approach
                try:
                    description = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='description']"))
                    )
                    if description:
                        return description.text.strip()
                except:
                    raise TimeoutException("No description selectors found")
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying description extraction ({retry_count}/{max_retries})...")
                    time.sleep(random.uniform(2, 4))  # Exponential backoff
                else:
                    print(f"Could not get description after {max_retries} attempts: {str(e)}")
                    return "Description not available"
        
        return "Description not available"
