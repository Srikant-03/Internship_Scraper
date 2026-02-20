import re
import dateparser
from datetime import datetime

INCLUDE_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "nlp", "natural language processing",
    "computer vision", "data science", "generative ai", "gen ai",
    "llm", "large language model", "reinforcement learning",
    "mlops", "ai research", "ai engineer", "ml engineer",
    "transformer", "diffusion model", "multimodal", "robotics ai",
    "speech recognition", "recommendation system", "ai intern"
]

EXCLUDE_KEYWORDS = ["senior", "5+ years", "lead", "manager", "director", "10 years"]

def is_valid_internship(title: str, skills: list) -> bool:
    """
    Checks if the internship title or skills match our desired keywords
    and do not contain exclusion keywords.
    """
    title_lower = title.lower()
    skills_lower = [s.lower() for s in skills]
    text_to_check = title_lower + " " + " ".join(skills_lower)

    # Check for exclusions first
    for exc in EXCLUDE_KEYWORDS:
        if exc in text_to_check:
            return False

    # Check for inclusions: Title OR Skills must have at least one keyword
    for inc in INCLUDE_KEYWORDS:
        if inc in text_to_check:
            return True

    return False

def is_valid_stipend(stipend_str: str, numeric_val: float, is_india: bool) -> bool:
    """
    Indian internships: minimum 20 INR per month, or not mentioned.
    International: any compensation > 0.
    Unpaid/0 is always excluded.
    """
    if stipend_str is None or stipend_str.strip() == "":
        return True # Not mentioned, keep it to be safe

    stipend_lower = stipend_str.lower()
    
    if "unpaid" in stipend_lower or numeric_val == 0:
        return False
        
    if is_india:
        # Minimum stipend is 5000 INR per month to avoid very low-value listings
        if numeric_val > 0 and numeric_val < 5000:
            return False
            
    return True

def parse_summer_dates(date_string: str) -> bool:
    """
    NLP constraint: Internship MUST start on/after May 20. End date is flexible.
    If explicitly says Summer, it passes.
    """
    ALLOW_TERMS = ["", "not mentioned", "rolling", "immediately", "asap", "flexible", "ongoing", "open", "continuous", "anytime"]
    if not date_string or str(date_string).strip().lower() in ALLOW_TERMS:
        return True # Default allow if unspecified
        
    date_lower = str(date_string).lower()
    
    # Explicit summer keywords
    if "summer" in date_lower or "may" in date_lower or "june" in date_lower:
        return True
        
    # NLP Parse
    # Attempt to extract early dates. 
    # Example: "Starts Jan 2026" should fail.
    try:
        parsed_date = dateparser.parse(date_lower, settings={'PREFER_DATES_FROM': 'future'})
        if parsed_date:
            # We enforce May 20th of the current year (or next if scraping in late winter)
            curr_year = datetime.now().year
            start_threshold = datetime(curr_year, 5, 20)
            
            # If it's starting between Jan 1 and May 19, reject it.
            if parsed_date < start_threshold and parsed_date.year == curr_year:
                return False
                
        return True
    except Exception:
        # If parsing fails entirely, we don't block it to avoid safe drops
        return True

def calculate_match_score(title: str, skills: list, org_type: str, stipend: float) -> int:
    """
    Out of 100.
    Base 50. 
    +20 for Core keywords (AI, ML, Computer Vision)
    +15 for Academic/Research Org
    +15 for high stipend
    """
    score = 50
    title_lower = title.lower()
    skills_lower = [s.lower() for s in skills]
    text_to_check = title_lower + " " + " ".join(skills_lower)
    
    core_keywords = ["research", "deep learning", "computer vision", "generative ai", "nlp", "scientist"]
    for word in core_keywords:
        if word in text_to_check:
            score += 20
            break
            
    if org_type in ["Institution", "Government"]:
        score += 15
        
    if stipend > 40000: # High stipend reward
        score += 15
        
    return min(100, score)

