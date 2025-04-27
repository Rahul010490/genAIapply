import pytest
from agents.extractor import HTMLDataExtractor
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def test_extractor_initialization(mock_soup, mock_driver):
    extractor = HTMLDataExtractor(mock_soup.prettify(), mock_driver)
    assert extractor.soup is not None
    assert extractor.driver is not None

def test_extract_data_with_valid_content(mock_soup, mock_driver):
    extractor = HTMLDataExtractor(mock_soup.prettify(), mock_driver)
    
    # Mock the job description method
    with patch.object(extractor, '_get_job_description', return_value='Mock job description'):
        data = extractor.extract_data()
        
        assert len(data) > 0
        first_job = data[0]
        
        # Verify job data structure
        assert len(first_job) == 5  # [title, company, location, url, description]
        assert first_job[0] == "Software Engineer"
        assert first_job[1] == "Tech Company"
        assert first_job[2] == "San Francisco, CA"
        assert "linkedin.com/jobs/view/123456" in first_job[3]
        assert first_job[4] == "Mock job description"

def test_extract_data_with_empty_content(mock_driver):
    empty_html = "<html><body></body></html>"
    extractor = HTMLDataExtractor(empty_html, mock_driver)
    data = extractor.extract_data()
    assert len(data) == 0

def test_get_job_description(monkeypatch):
    # Create mocks
    mock_driver = MagicMock()
    mock_element = MagicMock()
    mock_element.text = "Test job description"
    
    # Mock find_element to return our mock element
    mock_driver.find_element.return_value = mock_element
    
    # Mock WebDriverWait to immediately return success
    mock_wait = MagicMock()
    mock_wait.until.return_value = mock_element
    
    def mock_webdriverwait(*args, **kwargs):
        return mock_wait
    
    monkeypatch.setattr('selenium.webdriver.support.wait.WebDriverWait', mock_webdriverwait)
    monkeypatch.setattr('time.sleep', lambda x: None)  # Skip delays
    
    extractor = HTMLDataExtractor("<html></html>", mock_driver)
    description = extractor._get_job_description("https://www.linkedin.com/jobs/view/123456")
    assert description == "Test job description"

def test_get_job_description_timeout(monkeypatch):
    # Create mock driver
    mock_driver = MagicMock()
    mock_element = MagicMock()
    mock_element.text = "Description not available"
    
    # Mock find_element to return our mock element
    mock_driver.find_element.return_value = mock_element
    
    # Mock WebDriverWait to raise TimeoutException
    def mock_webdriverwait(*args, **kwargs):
        raise TimeoutException("Timed out")
    
    monkeypatch.setattr('selenium.webdriver.support.wait.WebDriverWait', mock_webdriverwait)
    monkeypatch.setattr('time.sleep', lambda x: None)  # Skip delays
    
    extractor = HTMLDataExtractor("<html></html>", mock_driver)
    with patch.object(mock_driver, 'get', side_effect=TimeoutException):
        description = extractor._get_job_description("https://www.linkedin.com/jobs/view/123456")
        assert description == "Description not available"

def test_extract_data_with_missing_fields(mock_driver):
    # HTML with missing company and location
    html = """
    <div class="jobs-search-results-list">
        <div class="job-card-container">
            <h3 class="base-search-card__title">Software Engineer</h3>
            <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/123456">View Job</a>
        </div>
    </div>
    """
    extractor = HTMLDataExtractor(html, mock_driver)
    
    with patch.object(extractor, '_get_job_description', return_value='Mock description'):
        data = extractor.extract_data()
        
        assert len(data) > 0
        first_job = data[0]
        assert first_job[0] == "Software Engineer"
        assert first_job[1] == "Company not listed"
        assert first_job[2] == "Location not listed"
