import pytest
from agents.navigator import HTMLNavigator
from selenium.webdriver.chrome.options import Options
from unittest.mock import patch, MagicMock, call, DEFAULT
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_navigator_initialization():
    url = "https://www.linkedin.com/jobs/search"
    with patch('agents.navigator.webdriver.Chrome') as mock_chrome:
        navigator = HTMLNavigator(url)
        assert navigator.url == url
        assert mock_chrome.called

def test_setup_driver():
    url = "https://www.linkedin.com/jobs/search"
    with patch('agents.navigator.webdriver.Chrome') as mock_chrome:
        navigator = HTMLNavigator(url)
        mock_driver = mock_chrome.return_value
        
        # Verify Chrome options were set
        options_call = mock_chrome.call_args[1]['options']
        assert '--start-maximized' in options_call.arguments
        assert '--disable-gpu' in options_call.arguments

def test_load_html_success(monkeypatch):
    url = "https://www.linkedin.com/jobs/search"
    mock_driver = MagicMock()
    mock_element = MagicMock()
    
    # Mock the page source to include the expected content
    mock_driver.page_source = """
    <div class="jobs-search-results-list">
        <div class="job-card-container">
            <h3>Test Job Title</h3>
        </div>
    </div>
    """
    
    # Mock find_elements to return some results
    mock_driver.find_elements.return_value = [MagicMock(), MagicMock()]
    
    # Mock input function and sleep
    monkeypatch.setattr('builtins.input', lambda _: '')
    monkeypatch.setattr('time.sleep', lambda x: None)
    
    # Mock WebDriverWait
    mock_wait = MagicMock()
    mock_wait.until.return_value = mock_element
    
    def mock_webdriverwait(*args, **kwargs):
        return mock_wait
    
    monkeypatch.setattr('selenium.webdriver.support.wait.WebDriverWait', mock_webdriverwait)
    
    with patch('agents.navigator.webdriver.Chrome', return_value=mock_driver):
        navigator = HTMLNavigator(url)
        page_source, driver = navigator.load_html()
        
        assert page_source is not None
        assert driver is not None
        assert "jobs-search-results-list" in page_source

def test_load_html_failure(monkeypatch):
    url = "https://www.linkedin.com/jobs/search"
    
    # Mock Chrome to raise an exception
    mock_driver = MagicMock()
    mock_driver.get.side_effect = Exception("Failed to load page")
    
    with patch('agents.navigator.webdriver.Chrome', return_value=mock_driver):
        navigator = HTMLNavigator(url)
        page_source, driver = navigator.load_html()
        
        assert page_source is None
        assert driver is None

def test_scroll_page(monkeypatch):
    url = "https://www.linkedin.com/jobs/search"
    mock_driver = MagicMock()
    
    # Set up height values for scrolling
    heights = [100, 150, 150]
    height_index = 0
    
    def mock_execute_script(script, *args):
        nonlocal height_index
        if script == "return document.body.scrollHeight":
            height = heights[min(height_index, len(heights)-1)]
            height_index += 1
            return height
        return None
    
    mock_driver.execute_script = MagicMock(side_effect=mock_execute_script)
    
    # Create test navigator
    class TestNavigator(HTMLNavigator):
        def __init__(self):
            self.url = url
            self.driver = mock_driver
    
    navigator = TestNavigator()
    
    with patch('time.sleep', return_value=None):  # Skip delays
        navigator._scroll_page()
    
    # Expected script calls
    expected_calls = [
        call("return document.body.scrollHeight"),
        call("window.scrollTo(0, document.body.scrollHeight);"),
        call("return document.body.scrollHeight"),
        call("return document.body.scrollHeight"),
        call("window.scrollTo(0, document.body.scrollHeight);"),
        call("return document.body.scrollHeight")
    ]
    
    # Get actual calls and filter for scroll-related ones
    actual_calls = mock_driver.execute_script.call_args_list
    scroll_calls = [c for c in actual_calls if any(x in str(c) for x in ["scrollHeight", "scrollTo"])]
    
    # Compare call sequences
    assert len(scroll_calls) == len(expected_calls)
    for actual, expected in zip(scroll_calls, expected_calls):
        assert str(actual) == str(expected)
