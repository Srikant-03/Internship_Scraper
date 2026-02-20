import argparse
from loguru import logger
from output_handler import append_to_csv, update_run_history
from filters import is_valid_internship, is_valid_stipend

# Import scrapers
from sites.internshala import scrape_internshala
from sites.unstop import scrape_unstop
from sites.naukri import scrape_naukri
from sites.government import scrape_government
from sites.misc_india import scrape_shine, scrape_foundit, scrape_apna, scrape_cutshort
from sites.international import scrape_international
from sites.rss_feeds import scrape_linkedin as scrape_remotive, scrape_indeed as scrape_weworkremotely
from sites.linkedin import scrape_linkedin  # NEW: direct LinkedIn Jobs page scraper
from sites.bigtech import scrape_bigtech
from sites.niche import scrape_niche_boards, scrape_aggregators
from sites.universities import scrape_universities
from sites.search_engine import scrape_search_engine

logger.add("scraper_errors.log", rotation="1 MB", level="ERROR")
# Human-readable logs for the UI
logger.add("scraper_run.log", rotation="5 MB", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {message}")

def process_and_save(source_name: str, raw_listings: list):
    valid_listings = []
    
    for item in raw_listings:
        # Check title and skills
        skills = item.get("required_skills", "")
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        
        if not is_valid_internship(item["role_title"], skill_list):
            continue
            
        # Check stipend
        is_india = item.get("stipend_currency") == "INR" or item.get("location_type") == "India"
        if not is_valid_stipend(item["stipend"], item["stipend_numeric"], is_india):
            continue
            
        valid_listings.append(item)
    
    if not valid_listings:
        logger.info(f"[{source_name}] Searched through {len(raw_listings)} listings, but none matched our criteria.")
        return 0
        
    added = append_to_csv(valid_listings)
    logger.info(f"[{source_name}] Analyzed {len(raw_listings)} listings, found {len(valid_listings)} matches, and saved {added} brand new ones!")
    return added

def run_scrapers(dry_run=False, specific_source=None):
    total_added = 0
    failed_sources = []
    
    scrapers = {
        "internshala": scrape_internshala,
        "unstop": scrape_unstop,
        "naukri": scrape_naukri,
        "government": scrape_government,
        "shine": scrape_shine,
        "foundit": scrape_foundit,
        "apna": scrape_apna,
        "cutshort": scrape_cutshort,
        "international": scrape_international,
        "linkedin": scrape_linkedin,          # NEW: direct LinkedIn Jobs page
        "remotive": scrape_remotive,           # Remote jobs RSS (was 'linkedin')
        "weworkremotely": scrape_weworkremotely, # Remote jobs RSS (was 'indeed')
        "bigtech": scrape_bigtech,
        "niche": scrape_niche_boards,
        "aggregators": scrape_aggregators,
        "universities": scrape_universities,
        "search": scrape_search_engine
    }
    
    if specific_source:
        if specific_source in scrapers:
            scrapers = {specific_source: scrapers[specific_source]}
        else:
            logger.error(f"Source {specific_source} not found.")
            return

    for source_name, scraper_func in scrapers.items():
        try:
            logger.info(f"🚀 Starting to check {source_name} for new opportunities...")
            listings = scraper_func()
            if not dry_run:
                added = process_and_save(source_name, listings)
                total_added += added
            else:
                logger.info(f"[{source_name}] DRY-RUN: Found {len(listings)} raw listings.")
        except Exception as e:
            logger.error(f"Failed {source_name}: {str(e)}")
            failed_sources.append(source_name)
            
    if not dry_run:
        update_run_history(total_added, failed_sources)
        
    logger.info("========================================")
    logger.info("✅ All scraping tasks completed!")
    logger.info(f"Sources checked: {len(scrapers) - len(failed_sources)} successful, {len(failed_sources)} failed.")
    if not dry_run:
        logger.info(f"🎉 Total new internships added today: {total_added}")
    logger.info("========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated AI/ML Internship Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Run scrapers without saving to CSV")
    parser.add_argument("--source", type=str, help="Run a specific source only")
    args = parser.parse_args()
    
    run_scrapers(dry_run=args.dry_run, specific_source=args.source)
