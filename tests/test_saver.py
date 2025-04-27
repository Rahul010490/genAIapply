import pytest
import os
import csv
from agents.saver import DataSaver
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock, call

@pytest.fixture
def sample_data():
    return [
        ['Job Title', 'Company', 'Location', 'Job Link', 'Description'],
        ['Software Engineer', 'Tech Corp', 'San Francisco', 'http://example.com', 'Job description']
    ]

def test_saver_initialization(sample_data):
    saver = DataSaver(sample_data, filename='test_output.csv')
    assert saver.data == sample_data
    assert saver.base_filename == 'test_output.csv'

def test_save_to_csv_success(sample_data, tmp_path):
    filename = str(tmp_path / 'test_output.csv')
    saver = DataSaver(sample_data, filename=filename)
    
    timestamp = '20250427_163939'
    expected_filename = f"test_output_{timestamp}.csv"
    
    with patch('agents.saver.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = timestamp
        
        mo = mock_open()
        with patch('builtins.open', mo):
            saver.save_to_csv()
            
            # Verify file was opened with correct name
            assert expected_filename in str(mo.call_args[0][0])
            
            # Verify write calls
            handle = mo()
            for row in sample_data:
                assert ','.join(row) in str(handle.write.call_args_list)

def test_save_to_csv_with_fallback(sample_data):
    # Set up a counter to track how many times open is called
    call_count = 0
    
    def mock_open_with_fallback(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:  # First attempt (current directory)
            raise PermissionError("Access denied to current directory")
        else:  # Second attempt (desktop)
            return mock_open().return_value
    
    with patch('builtins.open', side_effect=mock_open_with_fallback):
        with patch('os.path.expanduser', return_value='/home/user'):
            saver = DataSaver(sample_data, filename='test_output.csv')
            saver.save_to_csv()
            
            # Verify both attempts were made
            assert call_count == 2

def test_save_to_csv_all_fallbacks_fail(sample_data):
    # Track attempted paths
    attempted_paths = []
    timestamp = '20250427_163939'
    
    def normalize_path(path):
        return path.replace('\\', '/') if '\\' in path else path
    
    def mock_open_with_failures(*args, **kwargs):
        attempted_paths.append(normalize_path(args[0]))
        raise PermissionError(f"Permission denied for {args[0]}")
        
    with patch('agents.saver.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = timestamp
        
        with patch('builtins.open', side_effect=mock_open_with_failures), \
             patch('os.path.expanduser', return_value='/home/user'), \
             patch('tempfile.gettempdir', return_value='/tmp'), \
             patch('os.path.exists', return_value=False), \
             patch('os.makedirs', return_value=None):
            
            saver = DataSaver(sample_data, filename='test_output.csv')
            
            # The save operation should fail but try all locations
            try:
                saver.save_to_csv()
            except PermissionError:
                pass  # Expected to fail
            
            # Verify that all three locations were attempted in the correct order
            expected_paths = [
                f'test_output_{timestamp}.csv',                          # Current directory
                f'/home/user/Desktop/test_output_{timestamp}.csv',       # Desktop
                f'/tmp/test_output_{timestamp}.csv'                      # Temp directory
            ]
            
            # Normalize all attempted paths
            attempted_paths = [normalize_path(p) for p in attempted_paths]
            
            assert len(attempted_paths) == 3
            for expected, actual in zip(expected_paths, attempted_paths):
                assert actual.endswith(expected)

def test_save_to_csv_empty_data():
    empty_data = []
    saver = DataSaver(empty_data, filename='empty_output.csv')
    
    mo = mock_open()
    with patch('builtins.open', mo):
        saver.save_to_csv()
        # Verify file was opened
        assert mo.call_count == 1
        # Verify write was not called since data is empty
        handle = mo()
        assert handle.write.call_count == 0

def test_save_to_csv_makedirs_failure(sample_data):
    # Mock makedirs to fail
    with patch('os.makedirs', side_effect=PermissionError), \
         patch('builtins.open', mock_open()), \
         patch('os.path.exists', return_value=False):
        
        saver = DataSaver(sample_data, filename='test_output.csv')
        saver.save_to_csv()  # Should handle makedirs failure gracefully
