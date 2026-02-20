# 🤖 AI/ML Internship Radar

> **A production-ready, fully automated web scraper that discovers AI/ML internship opportunities from 60+ global sources — India and Worldwide — and presents them in a stunning real-time dashboard.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.x-green.svg)](https://flask.palletsprojects.com)
[![Playwright](https://img.shields.io/badge/playwright-stealth-blueviolet.svg)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📸 Dashboard Preview

The dashboard features a Bloomberg-inspired dark UI with:
- 🌍 **Region Tab Bar** — instantly filter by Everything / 🇮🇳 India / 🌐 Global / 📡 Remote
- 📊 **Match Score Badges** — every listing scored out of 100 for AI/ML relevance
- ⚡ **Real-time Logs** — view live scraper activity as it runs
- 🎛️ **Smart Sidebar Filters** — Source, Location Type, Stipend, Org Type, Role Level

---

## 🎯 What It Does

This system automatically:
1. **Scrapes 60+ platforms** for AI/ML internship listings worldwide
2. **Filters** by AI/ML relevance, stipend thresholds, and summer date windows
3. **Deduplicates** across all sources using content hashing
4. **Scores** every listing with a 0–100 AI/ML match score
5. **Presents** results in a live web dashboard at `http://localhost:5000`
6. **Auto-schedules** daily scrapes at 8:00 AM

---

## 🔍 Data Sources (60+ Platforms)

### 🇮🇳 India Platforms
| Source | Method | Notes |
|--------|--------|-------|
| **Internshala** | Playwright (stealth) | Largest Indian internship platform |
| **Unstop** | Playwright (headless=False) | Tech-focused, may require CAPTCHA |
| **Naukri.com** | Playwright (headless=False) | India's largest job board |
| **LinkedIn Jobs** | Playwright (headless=False) | 7 topics × 5 Indian cities |
| **Shine.com** | Requests + BeautifulSoup | Mid-level jobs board |
| **Foundit (Monster India)** | Requests + BeautifulSoup | - |
| **Apna** | Playwright | Blue-collar + tech roles |
| **CutShort** | Requests | Startup-focused |
| **DRDO / Government Labs** | Requests | Govt research portals |
| **Search Engine (DDG Dorks)** | DuckDuckGo API | Hidden opportunities, .ac.in sites |

### 🌐 International Platforms
| Source | Method | Coverage |
|--------|--------|----------|
| **LinkedIn Jobs** | Playwright | Worldwide, 15+ European countries, US cities, Canada, Asia |
| **Remotive.com RSS** | RSS Feed | AI/ML remote internships |
| **WeWorkRemotely RSS** | RSS Feed | Remote programming & data science |
| **WeWorkRemotely** | Playwright | AI/ML keyword search |
| **Universities (Dynamic)** | DuckDuckGo (54 queries) | See below ↓ |
| **BigTech Careers** | Requests | Google, Meta, Microsoft, Apple, Amazon |
| **Niche AI Boards** | Requests | ML-specific job boards |
| **Aggregators** | Requests | Indeed-style aggregators |

### 🎓 University & Research Lab Discovery (Dynamic)

The university scraper runs **54 targeted DuckDuckGo searches** that refresh on every run — no hardcoded lists:

| Region | Examples |
|--------|---------|
| 🇮🇳 India | IIT, IISc, IIIT, TIFR, DRDO, ISRO, ISI |
| 🇫🇮 Nordic | **Aalto University**, FCAI, KTH, Chalmers, DTU, NTNU, Helsinki |
| 🇩🇪 Germany/DACH | DAAD RISE, Max Planck, TU Munich, RWTH, ETH Zurich, EPFL, IST Austria |
| 🇬🇧 UK | Oxford, Cambridge, UCL, Imperial, Edinburgh |
| 🇫🇷🇳🇱 France/NL | Inria, TU Delft, CWI Amsterdam |
| 🇨🇳 China | Tsinghua, Peking, SJTU, USTC, ZJU, Fudan, CAS |
| 🇸🇬 Singapore | NUS, NTU, A*STAR, AI Singapore |
| 🇯🇵🇰🇷 Japan/Korea | RIKEN AIP, NII, KAIST, NAVER AI Lab, Samsung |
| 🇦🇺 Australia | ANU, Melbourne, CSIRO Data61 |
| 🇨🇦 Canada | Mitacs, Vector Institute, Mila, UBC, McGill |
| 🇺🇸 USA | MIT, Stanford, CMU, Berkeley, Cornell, UW, Georgia Tech, NSF REU |
| 🇺🇸 US National Labs | Oak Ridge, Argonne, PNNL, Sandia, DOE SULI |
| 🌐 Global AI Labs | OpenAI, DeepMind, Anthropic, Meta FAIR, Google, NVIDIA, Adobe, IBM, AI2 |
| 🌍 Misc | CERN, ESA, KAUST (UAE), Technion, AIMS Africa, USP Brazil |

---

## 🏗️ Project Structure

```
internship_scraper/
├── app.py                    # Flask web server + Socket.IO for live logs
├── scraper.py                # Orchestrator — runs all scrapers
├── filters.py                # AI/ML keyword filter, stipend validator, date parser
├── output_handler.py         # CSV append with deduplication
├── scraper_utils.py          # Human delays, Playwright stealth args
│
├── sites/                    # Individual scraper modules
│   ├── internshala.py        # Playwright stealth — 400+ listings
│   ├── unstop.py             # Playwright headless=False, 7 search URLs
│   ├── naukri.py             # Playwright headless=False (CAPTCHA-aware)
│   ├── linkedin.py           # LinkedIn PUBLIC jobs page — 80+ search configs
│   ├── rss_feeds.py          # Remotive.com + WeWorkRemotely RSS
│   ├── government.py         # DRDO, ISRO, Govt India portals
│   ├── misc_india.py         # Shine, Foundit, Apna, CutShort
│   ├── international.py      # WeWorkRemotely Playwright scraper
│   ├── bigtech.py            # Google, Meta, Microsoft, Apple, Amazon careers
│   ├── niche.py              # Niche AI job boards + aggregators
│   ├── search_engine.py      # DuckDuckGo dork search (8 query patterns)
│   └── universities.py       # Dynamic DDG search — 54 queries, global unis
│
├── templates/
│   └── index.html            # Dashboard HTML (Phosphor Icons + custom CSS)
│
├── static/
│   ├── style.css             # Bloomberg dark UI, glassmorphism, animations
│   ├── script.js             # Live filtering, region tabs, real-time logs
│   └── favicon.ico
│
├── internships.csv           # Output data file (gitignored)
├── internships_log.json      # Run history + metadata (gitignored)
├── scraper_run.log           # Full activity log (gitignored)
└── scraper_errors.log        # Error log (gitignored)
```

---

## ⚙️ How Filtering Works

### 1. AI/ML Keyword Filter (`filters.py`)
A listing must contain **at least one** of 50+ AI/ML keywords:
- Core: `machine learning`, `deep learning`, `neural network`, `NLP`
- Applied: `computer vision`, `reinforcement learning`, `LLM`, `generative AI`
- Tools: `PyTorch`, `TensorFlow`, `transformers`, `scikit-learn`, `pandas`
- Roles: `data science intern`, `AI engineer`, `ML research`

### 2. Stipend Filter
- **India listings**: Minimum ₹5,000/month (or unpaid is OK)
- **International listings**: Any stipend (or unpaid research is OK)
- Filter respects INR vs USD currencies automatically

### 3. Date Filter (`parse_summer_dates`)
- Summer internships must start **on or after May 20**
- Flexible terms like `"Immediately"`, `"ASAP"`, `"Rolling"`, `"Flexible"` are **always allowed**

### 4. Match Scoring (`calculate_match_score`)
Each listing gets a 0–100 score based on:
- Number of AI/ML keywords found in title + description
- Institution type (Research institution gets bonus)
- Stipend level relative to tier

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- Google Chrome (for Playwright)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-ml-internship-radar.git
cd ai-ml-internship-radar/internship_scraper
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install chromium
```

### 5. Run the App
```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🎮 Usage Guide

### Running the Dashboard
```bash
python app.py
```
The dashboard auto-loads the last scrape results. Click **"Run Scraper Now"** to trigger a fresh scrape.

### Running the Scraper Manually
```bash
# Full scrape (all sources)
python scraper.py

# Dry-run (doesn't save to CSV, just logs)
python scraper.py --dry-run

# Scrape a specific source only
python scraper.py --source internshala
python scraper.py --source linkedin
python scraper.py --source universities
python scraper.py --source naukri --dry-run
```

### Available `--source` Values
| Source Key | Description |
|-----------|-------------|
| `internshala` | Internshala scraper |
| `unstop` | Unstop scraper |
| `naukri` | Naukri.com scraper |
| `linkedin` | LinkedIn Jobs direct scraper (80+ configs) |
| `remotive` | Remotive RSS feed |
| `weworkremotely` | WeWorkRemotely RSS feed |
| `government` | Indian government labs |
| `shine` | Shine.com |
| `foundit` | Foundit.in |
| `apna` | Apna.co |
| `cutshort` | CutShort.io |
| `international` | WeWorkRemotely Playwright |
| `bigtech` | FAANG + big tech careers |
| `niche` | Niche AI boards |
| `aggregators` | Job aggregators |
| `universities` | Global university DDG search |
| `search` | DuckDuckGo dork search |

### Scheduling (Auto-run Daily)

**Windows Task Scheduler:**
```powershell
schtasks /create /tn "AI Radar Scraper" /tr "python C:\path\to\internship_scraper\scraper.py" /sc DAILY /st 08:00
```

**Linux/macOS Cron:**
```bash
0 8 * * * cd /path/to/internship_scraper && python scraper.py >> cron.log 2>&1
```

---

## 🖥️ Dashboard Features

### Region Tab Bar
Filter instantly by choosing a region tab above the cards:
| Tab | Filter |
|-----|--------|
| 🌍 Everything | All listings |
| 🇮🇳 India | Indian locations only |
| 🌐 Global / Abroad | International listings |
| 📡 Remote | Fully remote positions |

### Sidebar Filters
- **Search**: Text search across role, company, and skills
- **Location Type**: 🌍 All / 📡 Remote / 🇮🇳 India / 🌐 Global
- **Stipend (INR)**: Any / Paid Only / >₹10K / >₹20K / >₹50K / Unpaid
- **Source Platform**: Per-source dropdown (dynamically populated)
- **Organization Type**: All / Company / Institution / Government
- **Role Level**: All / Research Core / Applied Engineering

### Match Score Badges
- 🟢 **High Score (80–100)**: Strong AI/ML role, research focus, competitive stipend
- 🟡 **Medium Score (60–79)**: Relevant role, moderate AI/ML alignment
- 🔴 **Low Score (<60)**: Peripherally relevant

---

## 🔒 Anti-Blocking Features

The scraper uses multiple layers of anti-detection:

1. **Playwright Stealth Plugin** — patches browser fingerprints
2. **Human-like delays** — random `time.sleep()` between 1–5 seconds per action
3. **Realistic User-Agents** — Chrome 122 Windows 10 UA strings
4. **Random scrolling** — simulates reading behavior
5. **Visible Browser Mode** — Naukri, Unstop, and LinkedIn run with `headless=False` so **you can manually solve CAPTCHAs** if they appear (45-second window)
6. **Tenacity retry** — automatic retry with exponential backoff on failures

---

## 🛠️ Configuration

Key settings are in `filters.py`:

```python
# Minimum stipend for Indian internships (INR/month)
MIN_INDIA_STIPEND = 5000

# AI/ML keywords required in title/description
KEYWORDS = ["machine learning", "deep learning", "NLP", ...]

# Summer date filter — internships must start from:
SUMMER_START = datetime(current_year, 5, 20)

# Flex terms always allowed regardless of date
ALLOW_TERMS = ["immediately", "asap", "rolling", "flexible", "ongoing"]
```

---

## 📦 Requirements

```
flask
flask-socketio
playwright
playwright-stealth
beautifulsoup4
lxml
requests
ddgs                # DuckDuckGo search API
duckduckgo-search   # Legacy fallback
feedparser          # RSS parsing
pandas
loguru              # Structured logging
tenacity            # Retry logic
schedule            # Daily scheduling
```

---

## 🔧 Troubleshooting

### "No listings found" for Naukri / Unstop
These sites use CAPTCHAs. When the browser window opens, solve the CAPTCHA within:
- **Naukri**: 45 seconds
- **Unstop**: 20 seconds

### LinkedIn shows 0 results
LinkedIn may show a sign-in modal. The scraper waits 8–12 seconds after page load — close the popup manually when it appears.

### DuckDuckGo returning 0 results
DDG has rate limits. Add a longer delay in `scraper_utils.py` `human_delay()` or wait a few minutes before re-running.

### Port 5000 already in use
Change the port in `app.py`:
```python
socketio.run(app, host="0.0.0.0", port=5001, debug=False)
```

---

## 📄 Output Format

Results are saved to `internships.csv` with these columns:

| Column | Description |
|--------|-------------|
| `id` | MD5 hash — used for deduplication |
| `company_name` | Company or institution name |
| `role_title` | Job title |
| `location` | City/Country |
| `location_type` | `India` / `International` / `Remote` |
| `duration` | Internship duration |
| `stipend` | Raw stipend text |
| `stipend_numeric` | Numeric value (INR or USD) |
| `stipend_currency` | `INR` or `USD` |
| `required_skills` | Skills mentioned |
| `application_deadline` | Deadline date |
| `apply_link` | Direct application URL |
| `source_platform` | Which scraper found it |
| `date_scraped` | Date of discovery |
| `org_type` | `Company` / `Institution` / `Government` |
| `role_type` | `Research` / `Applied` |
| `match_score` | 0–100 AI/ML relevance score |

---

## 🤝 Contributing

1. Fork the repository
2. Add a new scraper in `sites/yoursite.py`
3. Register it in `scraper.py`'s `scrapers` dict
4. Submit a pull request

**Adding a new scraper:** Follow the pattern in any existing `sites/*.py` file — return a list of dicts matching the output schema above.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## ⚠️ Disclaimer

This tool is for **personal educational use** only. Respect each website's `robots.txt` and Terms of Service. The included rate limiting and human-like delays help ensure respectful usage. Do not use this tool for commercial scraping or at high frequencies.
