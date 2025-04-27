import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

@pytest.fixture
def mock_html():
    return """
    <div class="jobs-search-results-list">
        <div class="job-card-container">
            <h3 class="base-search-card__title">Software Engineer</h3>
            <h4 class="base-search-card__subtitle">Tech Company</h4>
            <span class="job-search-card__location">San Francisco, CA</span>
            <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/123456">View Job</a>
            <div class="jobs-description-content__text">
                We are looking for a Software Engineer to join our team.
                Requirements:
                - 3+ years of experience
                - Python expertise
                - Web development skills
            </div>
        </div>
    </div>
    """

@pytest.fixture
def mock_driver(mock_html):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    # Create a temporary HTML file
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(mock_html)
    
    # Load the temporary file
    driver.get('file://' + os.path.abspath('temp.html'))
    
    yield driver
    
    # Cleanup
    driver.quit()
    if os.path.exists('temp.html'):
        os.remove('temp.html')

@pytest.fixture
def mock_soup(mock_html):
    return BeautifulSoup(mock_html, 'html.parser')
