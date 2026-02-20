from playwright.sync_api import sync_playwright
import time
import random
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from loguru import logger
from filters import calculate_match_score, parse_summer_dates
from playwright_stealth import Stealth
import urllib.parse
from scraper_utils import human_delay, get_playwright_stealth_args
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def scrape_unstop():
    """Scrapes AI/ML internship listings from Unstop."""
    all_internships = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=get_playwright_stealth_args()
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        
        urls = [
            "https://unstop.com/internships?domain=tech&specialization=ai-ml",
            "https://unstop.com/internships?query=artificial%20intelligence",
            "https://unstop.com/internships?query=machine%20learning",
            "https://unstop.com/internships?query=data%20science"
        ]
        
        for url in urls:
            try:
                print(f"Scraping Unstop: {url} ...")
                page.goto(url, timeout=45000)
                
                # Wait for listings to load (Unstop uses dynamic loading)
                page.wait_for_selector(".listing-card", timeout=15000)
                
                # Scroll a bit to load more items if needed
                for _ in range(3):
                    page.mouse.wheel(0, random.randint(500, 1200))
                    human_delay(1.5, 3.2)
                
                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                
                listings = soup.find_all("div", class_="listing-card")
                
                for listing in listings:
                    try:
                        title_elem = listing.find("h2") or listing.find("div", class_="title")
                        if not title_elem:
                            continue
                        role_title = title_elem.text.strip()
                        
                        company_elem = listing.find("div", class_="org") or listing.find("div", class_="company")
                        company_name = company_elem.text.strip() if company_elem else "Unknown"
                        
                        # Find link
                        link_elem = listing.find_parent("a") or listing.find("a")
                        apply_link = ""
                        if link_elem and "href" in link_elem.attrs:
                            apply_link = link_elem["href"]
                            if apply_link.startswith("/"):
                                apply_link = "https://unstop.com" + apply_link
                        
                        location = "Unknown"
                        location_type = "India" # Default to India for Unstop unless specified
                        loc_elem = listing.find("div", title=lambda x: x and ("Location" in x or "City" in x))
                        if loc_elem:
                            location = loc_elem.text.strip()
                            if "Remote" in location or "Work From Home" in location:
                                location_type = "Remote"
                        
                        stipend = ""
                        stip_elem = listing.find("div", title=lambda x: x and "Stipend" in x)
                        if stip_elem:
                            stipend = stip_elem.text.strip()
                        
                        stipend_numeric = 0.0
                        if "₹" in stipend:
                            import re
                            stipend_clean = stipend.replace(",", "").replace("₹", "")
                            match = re.search(r'(\d+)', stipend_clean)
                            if match:
                                stipend_numeric = float(match.group(1))
                        
                        source_platform = "Unstop"
                        org_type = "Company"
                        role_type = "Research" if "research" in role_title.lower() else "Applied"
                        match_score = calculate_match_score(role_title, [], org_type, stipend_numeric)
                        
                        id_hash = hashlib.md5(f"{company_name}-{role_title}-{source_platform}".encode()).hexdigest()
                        
                        record = {
                            "id": id_hash,
                            "company_name": company_name,
                            "role_title": role_title,
                            "location": location,
                            "location_type": location_type,
                            "duration": "",
                            # We don't have easily extractable start dates directly on Unstop cards without clicking in,
                            # but if they appear, we would test them. Assuming general for now.
                            "stipend": stipend,
                            "stipend_numeric": stipend_numeric,
                            "stipend_currency": "INR",
                            "required_skills": "", 
                            "application_deadline": "", 
                            "apply_link": apply_link,
                            "source_platform": source_platform,
                            "date_scraped": datetime.now().strftime("%Y-%m-%d"),
                            "org_type": org_type,
                            "role_type": role_type,
                            "match_score": match_score
                        }
                        
                        all_internships.append(record)
                    except Exception as e:
                        logger.error(f"Error parsing Unstop listing: {e}")
            except Exception as e:
                logger.error(f"Failed to load Unstop {url}: {e}")
                # Raising exception triggers the tenacity retry decorator for the whole function
                raise e
                
            human_delay(2.5, 5.0)
            
        browser.close()
    
    return all_internships
