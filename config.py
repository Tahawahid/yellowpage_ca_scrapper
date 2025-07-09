"""Configuration settings for Yellow Pages Scraper"""

class Config:
    # Scraping settings
    BASE_URL = "https://www.yellowpages.ca/search/si/{page}/{category}/{location}"
    EMPTY_PAGE_THRESHOLD = 2
    
    # Default delay settings (in seconds)
    DEFAULT_SEARCH_PAGE_MIN_DELAY = 8
    DEFAULT_SEARCH_PAGE_MAX_DELAY = 12
    DEFAULT_LISTING_PAGE_MIN_DELAY = 3
    DEFAULT_LISTING_PAGE_MAX_DELAY = 6
    DEFAULT_WEBSITE_MIN_DELAY = 2
    DEFAULT_WEBSITE_MAX_DELAY = 4
    DEFAULT_PAGE_LOAD_MIN_DELAY = 1
    DEFAULT_PAGE_LOAD_MAX_DELAY = 3
    
    # Timeout and retry settings
    DEFAULT_WEBSITE_TIMEOUT = 15
    DEFAULT_MAX_WEBSITE_RETRIES = 2
    DEFAULT_PAGE_LOAD_TIMEOUT = 30
    DEFAULT_MAX_PAGE_RETRIES = 3
    
    # Request settings
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # UI settings
    WINDOW_SIZE = "1200x900"  # Increased for delay controls
    WINDOW_TITLE = "Yellow Pages Enhanced Scraper"
    
    # Default values
    DEFAULT_CATEGORY = "dentists"
    DEFAULT_LOCATION = "Toronto+ON"
    DEFAULT_START_PAGE = 1
    
    # Social media domains to look for
    SOCIAL_DOMAINS = [
        'facebook.com',
        'twitter.com',
        'x.com',
        'instagram.com',
        'linkedin.com',
        'youtube.com',
        'tiktok.com',
        'pinterest.com',
        'snapchat.com',
        'threads.net',
        'whatsapp.com',
        'telegram.org',
        'discord.com',
        'reddit.com',
        'tumblr.com',
        'flickr.com',
        'vimeo.com',
        'twitch.tv',
        'github.com',
        'behance.net',
        'dribbble.com',
        'medium.com',
        'quora.com',
        'stackoverflow.com'
    ]
