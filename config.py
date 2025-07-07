"""Configuration settings for Yellow Pages Scraper"""

class Config:
    # Scraping settings
    BASE_URL = "https://www.yellowpages.ca/search/si/{page}/{category}/{location}"
    MIN_DELAY = 8
    MAX_DELAY = 12
    EMPTY_PAGE_THRESHOLD = 2
    
    # Request settings
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # UI settings
    WINDOW_SIZE = "900x700"  # Increased size for new fields
    WINDOW_TITLE = "Yellow Pages Scraper"
    
    # Default values
    DEFAULT_CATEGORY = "dentists"
    DEFAULT_LOCATION = "Toronto+ON"
    DEFAULT_START_PAGE = 1
