from bs4 import BeautifulSoup
import logging

class DataExtractor:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def extract_data(self, html_content):
        if not html_content:
            print("\n❌ No HTML content to extract from")
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        job_data = []
        
        # First try the standard jobs container
        print("\nSearching for job listings...")
        jobs_container = soup.select_one("ul.jobs-search__results-list")
        if jobs_container:
            print("Found jobs container using: ul.jobs-search__results-list")
            job_cards = jobs_container.select("li")
        else:
            # Try alternative containers
            print("Trying alternative job card selectors...")
            selectors = [
                "div.base-card",  # New LinkedIn base card
                "div.job-card-container",  # Standard job card
                "div.jobs-search-results__list-item",  # Alternative listing
                "li.jobs-search-results__list-item"  # Another variation
            ]
            
            for selector in selectors:
                job_cards = soup.select(selector)
                if job_cards:
                    print(f"Found {len(job_cards)} jobs using: {selector}")
                    break
            else:
                job_cards = []

        if not job_cards:
            print("\n⚠️ No job listings found in the page source.")
            print("This might happen if:")
            print("1. The page hasn't fully loaded")
            print("2. LinkedIn's structure has changed")
            print("3. You're not logged in or need to complete verification")
            return []

        print(f"\nProcessing {len(job_cards)} job listings...")
        
        for card in job_cards:
            try:
                # Try multiple selectors for each field
                title = self._try_selectors(card, [
                    "h3.base-search-card__title",
                    "h3.job-card-base__title",
                    "a.job-card-list__title"
                ])
                
                company = self._try_selectors(card, [
                    "h4.base-search-card__subtitle",
                    "a.job-card-container__company-name",
                    "span.job-card-base__company-name"
                ])
                
                location = self._try_selectors(card, [
                    "span.job-search-card__location",
                    "div.job-card-container__metadata-wrapper span",
                    "span.job-card-base__location"
                ])
                
                job_link = card.select_one("a")
                link = job_link.get('href', '') if job_link else ''
                if link and not link.startswith('http'):
                    link = 'https://www.linkedin.com' + link
                
                if title and company:  # Only add if we have at least title and company
                    job_data.append([
                        title.strip(),
                        company.strip(),
                        location.strip() if location else "N/A",
                        link.strip(),
                        ""  # Empty description - we're not getting detailed views
                    ])
                
            except Exception as e:
                logging.error(f"Error extracting job data: {str(e)}")
                continue
        
        print(f"\n✅ Successfully extracted {len(job_data)} job listings")
        return job_data

    def _try_selectors(self, element, selectors):
        """Try multiple selectors and return the first successful match"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return ""

    def get_job_description(self, driver, job_url):
        """Placeholder for job description - not used in this version"""
        return "Description not available"
