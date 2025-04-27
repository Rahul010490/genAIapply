# LinkedIn Job Scraper

A Python-based LinkedIn job scraper that extracts job listings and saves them to CSV files.

## Features

- Scrapes job listings from LinkedIn search results
- Extracts detailed information including:
  - Job Title
  - Company Name
  - Location
  - Job URL
  - Full Job Description
- Saves data to timestamped CSV files
- Handles rate limiting and retries
- Automatically manages ChromeDriver installation

## Requirements

- Python 3.7+
- Chrome browser installed
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The scraper can be run in two ways:

### 1. Using Direct LinkedIn URL

```bash
python main.py --url "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=Remote"
```

### 2. Using Keywords and Location

```bash
python main.py --keywords "software engineer" --location "United States"
```

## Output

- Scraped data is saved to the `Jobs` directory
- Files are named with timestamps (e.g., `linkedin_jobs_20250419_123456.csv`)
- CSV columns: Job Title, Company, Location, Job Link, Description

## Notes

- The scraper will prompt you to log in to LinkedIn if needed
- You can press Enter to continue once all job listings are loaded
- The script processes up to 25 job listings per run to avoid rate limiting
- Random delays are implemented to prevent blocking
- Automatic retry mechanism for failed job description extractions

## Error Handling

- Handles rate limiting with appropriate warnings
- Retries job description extraction up to 3 times
- Graceful handling of missing data fields
- Fallback options for saving files (Desktop/Temp directory)
