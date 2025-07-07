import requests
from bs4 import BeautifulSoup
import time

# Test URL
url = "https://www.yellowpages.com/salt-lake-city-ut/barbers"
# api_url = "https://www.yellowpages.com/search?search_terms=barbers&geo_location_terms=Salt+Lake+City%2C+UT"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def test_scrape(url):
    try:
        print(f"Testing URL: {url}")
        
        # Make request with polite delay
        time.sleep(2)
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for listings
            listings = soup.find_all('div', class_='result')
            print(f"Found {len(listings)} business listings")
            
            # Check for pagination
            pagination = soup.find('div', class_='pagination')
            print(f"Pagination detected: {bool(pagination)}")
            
            # Quick test - extract first 3 business names
            print("\nSample Business Names:")
            for i, listing in enumerate(listings[:3]):
                name = listing.find('a', class_='business-name')
                print(f"{i+1}. {name.text.strip() if name else 'No name found'}")
                
            # Check for blocking
            if "captcha" in response.text.lower():
                print("\n⚠️ WARNING: CAPTCHA detected - scraping may be blocked")
            elif "access denied" in response.text.lower():
                print("\n⚠️ WARNING: Access denied - request blocked")
            else:
                print("\n✅ Page appears scrapeable")
                
        elif response.status_code == 403:
            print("⛔ BLOCKED: Received 403 Forbidden response")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_scrape(url)