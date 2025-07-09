"""Test script for the Yellow Pages Scraper"""

from scraper import YellowPagesScraper
from data_handler import DataHandler
import json

def test_basic_scraping():
    """Test basic scraping functionality"""
    print("Testing Enhanced Yellow Pages Scraper...")
    
    # Custom delay settings for testing (faster)
    delay_settings = {
        'search_min': 2,
        'search_max': 3,
        'listing_min': 1,
        'listing_max': 2,
        'website_min': 1,
        'website_max': 2,
        'page_load_min': 0.5,
        'page_load_max': 1,
        'website_timeout': 10,
        'website_retries': 2,
        'page_timeout': 20,
        'page_retries': 2
    }
    
    # Create scraper instance with custom delays
    scraper = YellowPagesScraper(delay_settings=delay_settings)
    
    # Test with a small scrape
    category = "dentists"
    location = "Toronto+ON"
    start_page = 1
    end_page = 1  # Only scrape first page for testing
    
    print(f"Starting test scrape for {category} in {location}, page {start_page}")
    print("Using faster delay settings for testing...")
    
    try:
        # Run scraper
        data = scraper.run_scraper(category, location, start_page, end_page)
        
        if data:
            print(f"✓ Successfully scraped {len(data)} listings")
            
            # Get summary
            summary = DataHandler.get_scraping_summary(data)
            print(f"\nSummary Statistics:")
            print(f"- Total listings: {summary.get('total_listings', 0)}")
            print(f"- Successful scrapes: {summary.get('successful_scrapes', 0)}")
            print(f"- Failed scrapes: {summary.get('failed_scrapes', 0)}")
            print(f"- Success rate: {summary.get('success_rate', 0)}%")
            print(f"- Total emails: {summary.get('total_emails', 0)}")
            print(f"- Total social platforms: {summary.get('total_social_platforms', 0)}")
            print(f"- Total websites: {summary.get('total_websites', 0)}")
            print(f"- Listings with emails: {summary.get('listings_with_emails', 0)}")
            print(f"- Listings with social links: {summary.get('listings_with_social', 0)}")
            print(f"- Listings with websites: {summary.get('listings_with_websites', 0)}")
            
            # Show first listing as example
            if data:
                first_listing = data[0]
                print(f"\nFirst listing example:")
                print(f"Name: {first_listing.get('name', 'N/A')}")
                print(f"Phone: {first_listing.get('phone', 'N/A')}")
                print(f"Website: {first_listing.get('website', 'N/A')}")
                print(f"Emails: {first_listing.get('emails', [])}")
                print(f"Social links: {list(first_listing.get('social_links', {}).keys())}")
                print(f"Scraping status: {first_listing.get('scraping_status', 'N/A')}")
                
                # Show full JSON structure for debugging
                print(f"\nFull JSON structure:")
                print(json.dumps(first_listing, indent=2))
                
            return True
        else:
            print("✗ No data scraped")
            return False
            
    except Exception as e:
        print(f"✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_delay_settings():
    """Test different delay settings"""
    print("\nTesting delay settings...")
    
    # Test with default settings
    default_scraper = YellowPagesScraper()
    print(f"Default search delay range: {default_scraper.SEARCH_PAGE_MIN_DELAY} - {default_scraper.SEARCH_PAGE_MAX_DELAY}")
    print(f"Default listing delay range: {default_scraper.LISTING_PAGE_MIN_DELAY} - {default_scraper.LISTING_PAGE_MAX_DELAY}")
    print(f"Default website delay range: {default_scraper.WEBSITE_MIN_DELAY} - {default_scraper.WEBSITE_MAX_DELAY}")
    
    # Test with custom settings
    custom_delays = {
        'search_min': 1,
        'search_max': 2,
        'listing_min': 0.5,
        'listing_max': 1,
        'website_min': 0.5,
        'website_max': 1,
        'page_load_min': 0.2,
        'page_load_max': 0.5,
        'website_timeout': 5,
        'website_retries': 1,
        'page_timeout': 10,
        'page_retries': 1
    }
    
    custom_scraper = YellowPagesScraper(delay_settings=custom_delays)
    print(f"Custom search delay range: {custom_scraper.SEARCH_PAGE_MIN_DELAY} - {custom_scraper.SEARCH_PAGE_MAX_DELAY}")
    print(f"Custom listing delay range: {custom_scraper.LISTING_PAGE_MIN_DELAY} - {custom_scraper.LISTING_PAGE_MAX_DELAY}")
    print(f"Custom website delay range: {custom_scraper.WEBSITE_MIN_DELAY} - {custom_scraper.WEBSITE_MAX_DELAY}")
    
    return True

if __name__ == "__main__":
    print("Enhanced Yellow Pages Scraper Test Suite")
    print("=" * 50)
    
    # Test delay settings
    test_delay_settings()
    
    # Test basic scraping
    success = test_basic_scraping()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed!")
