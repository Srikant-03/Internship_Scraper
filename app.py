from flask import Flask, render_template, jsonify, request
import pandas as pd
from pathlib import Path
import threading
import sys
import os

# Import the scraper orchestrator
# We need to add the current dir to path to import scraper properly if needed, but it's in the same dir
from scraper import run_scrapers

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "internships.csv"

# Global state for scraping
scraper_t = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/internships")
def get_internships():
    if not DATA_FILE.exists():
        return jsonify([])
        
    try:
        df = pd.read_csv(DATA_FILE)
        # Safely convert NaN to empty strings for JSON serialization
        df = df.fillna("")
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return jsonify([])

@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    global scraper_t
    
    if scraper_t and scraper_t.is_alive():
        return jsonify({"status": "running", "message": "Scraping is already in progress!"})
        
    def scrape_job():
        # Running the full scraper
        run_scrapers(dry_run=False)
        
    scraper_t = threading.Thread(target=scrape_job)
    scraper_t.start()
    
    return jsonify({"status": "started", "message": "Scraper started successfully. This might take a while."})

@app.route("/api/scrape/status")
def scrape_status():
    global scraper_t
    if scraper_t and scraper_t.is_alive():
        return jsonify({"status": "running"})
    return jsonify({"status": "idle"})

@app.route("/api/logs")
def get_logs():
    log_file = Path(__file__).parent / "scraper_run.log"
    if not log_file.exists():
        return jsonify({"logs": ["No logs yet. Click 'Run Scraper Now' to start!"]})
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Return last N lines
            return jsonify({"logs": [l.strip() for l in lines[-75:]]})
    except Exception as e:
        return jsonify({"logs": [f"Error reading logs: {e}"]})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
