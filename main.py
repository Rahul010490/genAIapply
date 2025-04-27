import argparse
from agents.navigator import HTMLNavigator
from agents.extractor import HTMLDataExtractor
from agents.saver import DataSaver
from urllib.parse import quote

def create_linkedin_url(keywords, location):
    """Create a LinkedIn search URL from keywords and location"""
    encoded_keywords = quote(keywords)
    encoded_location = quote(location)
    return f"https://www.linkedin.com/jobs/search/?keywords={encoded_keywords}&location={encoded_location}"

def run_agentic_workflow(url):
    print("🔍 Starting LinkedIn jobs scraper...")
    print(f"📍 Target URL: {url}")
    
    # Initialize and run the navigator
    print("⏳ Loading webpage and waiting for dynamic content...")
    navigator = HTMLNavigator(url)
    page_source, driver = navigator.load_html()
    
    if not page_source or not driver:
        print("❌ Failed to load the page")
        return

    # Extract job data with descriptions
    extractor = HTMLDataExtractor(page_source, driver)
    data = extractor.extract_data()

    # Add headers to the data
    headers = [
        ['Job Title', 'Company', 'Location', 'Job Link', 'Description']
    ]
    data_with_headers = headers + data

    # Create Jobs directory if it doesn't exist
    import os
    if not os.path.exists('Jobs'):
        os.makedirs('Jobs')

    # Save to CSV
    output_file = os.path.join('Jobs', 'linkedin_jobs.csv')
    print("\n💾 Saving data to CSV...")
    saver = DataSaver(data_with_headers, filename=output_file)
    saver.save_to_csv()

    print(f"✅ Successfully scraped {len(data)} job listings with descriptions!")
    print(f"📁 Data saved to '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Jobs Scraper')
    parser.add_argument('--url', help='Full LinkedIn jobs search URL')
    parser.add_argument('--keywords', help='Job search keywords (e.g., "software engineer")')
    parser.add_argument('--location', help='Job location (e.g., "United States" or "Remote")')
    
    args = parser.parse_args()
    
    if args.url:
        linkedin_url = args.url
    elif args.keywords and args.location:
        linkedin_url = create_linkedin_url(args.keywords, args.location)
    else:
        parser.print_help()
        print("\nExamples:")
        print("1. Using direct URL:")
        print('   python main.py --url "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=Remote"')
        print("\n2. Using keywords and location:")
        print('   python main.py --keywords "software engineer" --location "United States"')
        exit(1)
        
    run_agentic_workflow(linkedin_url)
