import time
import random
from fake_useragent import UserAgent
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from loguru import logger
import requests

def human_delay(min_sec=1.5, max_sec=4.5):
    """Introduces randomized float jitter to mimic human reading/clicking speed."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def get_random_headers():
    """Generates a rotating robust header fingerprint."""
    ua = UserAgent(os=['windows', 'mac'])
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US,en;q=0.5', 'en-GB,en;q=0.9', 'en-US,en;q=0.9']),
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    return headers

def get_playwright_stealth_args():
    """Returns heavily evasive Chrome launch arguments."""
    return [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--window-size=1920,1080'
    ]

# Retry decorator for raw requests
def requests_retry_session(retries=3):
    """Returns a requests session configured with retries and realistic headers."""
    session = requests.Session()
    session.headers.update(get_random_headers())
    return session

# Playwright page readiness utility
def wait_for_human(page, selector=None):
    """Scrolls randomly then waits, mimicking user behavior."""
    human_delay(1.0, 2.5)
    page.mouse.wheel(0, random.randint(300, 700))
    human_delay(0.5, 1.5)
    if selector:
        page.wait_for_selector(selector, timeout=15000)
