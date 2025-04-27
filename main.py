import argparse
from agents.navigator import HTMLNavigator
from agents.extractor import DataExtractor
from agents.saver import DataSaver

def run_agentic_workflow(url):
    # Initialize the navigator and get the page HTML
    navigator = HTMLNavigator(url)
    page_source, driver = navigator.load_html()
    
    if not page_source:
        print("❌ Failed to load the page")
        return
    
    # Extract data from the page
    extractor = DataExtractor()
    job_data = extractor.extract_data(page_source)
    
    # Save the extracted data
    print("\n💾 Saving data to CSV...")
    saver = DataSaver(job_data)
    saver.save_to_csv()
    
    if driver:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Job Scraper')
    parser.add_argument('--keywords', required=True, help='Job search keywords')
    parser.add_argument('--location', required=True, help='Job location')
    
    args = parser.parse_args()
    
    # Construct LinkedIn job search URL
    base_url = "https://www.linkedin.com/jobs/search/?"
    params = {
        'keywords': args.keywords.replace(' ', '%20'),
        'location': args.location.replace(' ', '%20')
    }
    url = base_url + '&'.join([f"{k}={v}" for k, v in params.items()])
    
    print("🔍 Starting LinkedIn jobs scraper...")
    print(f"📍 Target URL: {url}")
    print("⏳ Loading webpage and waiting for dynamic content...")
    
    run_agentic_workflow(url)

if __name__ == "__main__":
    main()
