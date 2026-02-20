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
from sites.rss_feeds import scrape_linkedin, scrape_indeed
from sites.bigtech import scrape_bigtech
from sites.niche import scrape_niche_boards, scrape_aggregators
from sites.universities import scrape_universities
from sites.search_engine import scrape_search_engine

logger.add("scraper_errors.log", rotation="1 MB", level="ERROR")

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
        print(f"[{source_name}] Found 0 valid new listings out of {len(raw_listings)} scraped.")
        return 0
        
    added = append_to_csv(valid_listings)
    print(f"[{source_name}] Scraped {len(raw_listings)}, {len(valid_listings)} passed filters, added {added} new to CSV.")
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
        "linkedin": scrape_linkedin,
        "indeed": scrape_indeed,
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
            print(f"Source {specific_source} not found.")
            return

    for source_name, scraper_func in scrapers.items():
        try:
            print(f"Starting {source_name}...")
            listings = scraper_func()
            if not dry_run:
                added = process_and_save(source_name, listings)
                total_added += added
            else:
                print(f"[DRY-RUN] {source_name}: Found {len(listings)} raw listings.")
                if listings:
                    print("- Sample -")
                    import pprint
                    pprint.pprint(listings[0])
        except Exception as e:
            logger.error(f"Failed {source_name}: {str(e)}")
            failed_sources.append(source_name)
            
    if not dry_run:
        update_run_history(total_added, failed_sources)
        
    print("\n========================================")
    print("🤖 AI/ML Internship Scraper — Daily Run")
    from datetime import datetime
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')} | ⏰ Time: {datetime.now().strftime('%I:%M %p')}")
    print(f"✅ Sources scraped: {len(scrapers) - len(failed_sources)}/{len(scrapers)}")
    print(f"❌ Sources failed:  {len(failed_sources)} (see scraper_errors.log)")
    if not dry_run:
        print(f"🆕 New listings found: {total_added}")
        print("💾 Saved to: internships.csv")
    print("========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated AI/ML Internship Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Run scrapers without saving to CSV")
    parser.add_argument("--source", type=str, help="Run a specific source only")
    args = parser.parse_args()
    
    run_scrapers(dry_run=args.dry_run, specific_source=args.source)
