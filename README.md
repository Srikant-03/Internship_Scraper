# 🎯 Automated AI/ML Internship Scraper

A complete, production-ready system that scrapes 60+ platforms for AI/ML internships, filters them by relevancy and stipend, stores them in a deduplicated CSV, and presents them on a premium interactive dashboard.

## 🚀 Setup Instructions

1. **Install Dependencies**
   Ensure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Environment Variables**
   Rename `.env.example` to `.env`. (Optional for future API integrations).

## 🖥️ Running the Dashboard UI
To view the beautiful Web Dashboard with all filters:
```bash
python app.py
```
Then open `http://127.0.0.1:5000` in your browser. From here you can filter the results or manually trigger a live scraping session.

## 🤖 Running the Scraper Manually via CLI
If you want to run the scraper directly from the terminal without the UI:
```bash
# Run all sources
python scraper.py

# Run a specific source
python scraper.py --source internshala

# Run all sources without saving to CSV (Dry Run)
python scraper.py --dry-run
```

## ⏰ Setting up Automation (Daily at 8:00 AM)

### For Windows:
We recommend using **Task Scheduler**:
1. Open Windows Task Scheduler.
2. Click **Create Basic Task**.
3. Name it "AI Internship Scraper", set Trigger to **Daily at 8:00 AM**.
4. Set Action to **Start a Program**.
5. Browse for `run_scheduler.bat` located in this folder.
   *(Alternatively, run the batch file manually and leave the console open!)*

### For Linux / macOS:
Add this line to your crontab (`crontab -e`) to run it daily at 8:00 AM:
```bash
0 8 * * * cd /path/to/internship_scraper && python scraper.py >> cron_output.log 2>&1
```

## 📁 Project Structure
- `app.py`: Flask web dashboard server.
- `scraper.py`: Main orchestrator that runs all scraping modules.
- `scheduler.py`: A persistent python loop that triggers the scraper daily at 8AM.
- `filters.py`: Logic to check job descriptions, skills, and evaluate stipends.
- `output_handler.py`: Saves data to `internships.csv` and ensures no duplicates via `internships_log.json`.
- `sites/`: Contains dynamic and static web scrapers for platforms like Internshala, Unstop, Naukri, Big Tech, and Government portals.
- `templates/` & `static/`: HTML/CSS/JS for the dashboard frontend.
