import feedparser
import hashlib
from datetime import datetime
from loguru import logger
from bs4 import BeautifulSoup
from filters import calculate_match_score
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def scrape_linkedin():
    """Scrapes LinkedIn using their public RSS feed as a fallback."""
    all_internships = []
    url = "https://www.linkedin.com/jobs/search/?keywords=AI+ML+internship&format=rss"
    
    try:
        print(f"Scraping LinkedIn (RSS): {url} ...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            try:
                # LinkedIn RSS title format: "Company searching for Role in Location"
                # but sometimes varies. Let's do a basic parse.
                raw_title = entry.title
                
                role_title = raw_title
                company_name = "Unknown"
                if " at " in raw_title:
                    parts = raw_title.split(" at ")
                    role_title = parts[0].strip()
                    company_name = parts[1].split(" (")[0].strip() if " (" in parts[1] else parts[1].strip()
                
                location = "International"
                location_type = "International"
                
                # Try to extract location from title or description
                if "India" in raw_title or "India" in entry.description:
                    location_type = "India"
                    location = "India"
                if "Remote" in raw_title or "Remote" in entry.description:
                    location_type = "Remote"
                    location = "Remote"
                
                apply_link = entry.link
                source_platform = "LinkedIn"
                
                id_hash = hashlib.md5(f"{company_name}-{role_title}-{source_platform}".encode()).hexdigest()
                
                org_type = "Company"
                role_type = "Research" if "research" in role_title.lower() else "Applied"
                match_score = calculate_match_score(role_title, ["AI/ML"], org_type, 0.0)
                
                record = {
                    "id": id_hash,
                    "company_name": company_name,
                    "role_title": role_title,
                    "location": location,
                    "location_type": location_type,
                    "duration": "",
                    "stipend": "",
                    "stipend_numeric": 0.0,
                    "stipend_currency": "USD" if location_type != "India" else "INR",
                    "required_skills": "AI/ML", 
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
                logger.error(f"Error parsing LinkedIn entry: {e}")
                
    except Exception as e:
        logger.error(f"Failed to load LinkedIn RSS: {e}")
        raise e
        
    return all_internships

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def scrape_indeed():
    """Scrapes Indeed using their public RSS feed."""
    all_internships = []
    url = "https://rss.indeed.com/rss?q=AI+ML+internship&l=India"
    
    try:
        print(f"Scraping Indeed (RSS): {url} ...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            try:
                # Indeed RSS title: "Role - Company - Location"
                raw_title = entry.title
                parts = raw_title.split(" - ")
                
                role_title = parts[0].strip() if len(parts) > 0 else raw_title
                company_name = parts[1].strip() if len(parts) > 1 else "Unknown"
                location = parts[2].strip() if len(parts) > 2 else "India"
                
                location_type = "India"
                if "Remote" in location:
                    location_type = "Remote"
                
                apply_link = entry.link
                source_platform = "Indeed"
                
                id_hash = hashlib.md5(f"{company_name}-{role_title}-{source_platform}".encode()).hexdigest()
                
                org_type = "Company"
                role_type = "Research" if "research" in role_title.lower() else "Applied"
                match_score = calculate_match_score(role_title, ["AI/ML"], org_type, 0.0)
                
                record = {
                    "id": id_hash,
                    "company_name": company_name,
                    "role_title": role_title,
                    "location": location,
                    "location_type": location_type,
                    "duration": "",
                    "stipend": "",
                    "stipend_numeric": 0.0,
                    "stipend_currency": "INR",
                    "required_skills": "AI/ML", 
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
                logger.error(f"Error parsing Indeed entry: {e}")
                
    except Exception as e:
        logger.error(f"Failed to load Indeed RSS: {e}")
        raise e
        
    return all_internships
