from extract.extract import get_data

def test_get_data_returns_none_on_error():
    
    # Use invalid URL that will cause request to fail
    bad_url = "http://invalid-url-that-does-not-exist.com/api"
    
    result = get_data(bad_url, 'test_subset', '2025-01-01')
    
    assert result is None