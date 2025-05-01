# scripts/constants.py

import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URLs
DHAN_CHARTS_HISTORICAL_URL = "https://api.dhan.co/v2/charts/historical"
DHAN_TODAY_EOD_URL = "https://api.dhan.co/v2/marketfeed/quote"

# Date Range
FROM_DATE = "2000-01-01"
TO_DATE = datetime.now().strftime("%Y-%m-%d")

# Timezone
INDIA_TZ = timezone(timedelta(hours=5, minutes=30))

# Access Token and Common API Headers
DHAN_API_KEY = os.getenv("DHAN_API_KEY", "").strip()
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "").strip()

# Check for required environment variables
if not DHAN_API_KEY:
    raise ValueError("DHAN_API_KEY environment variable is not set or empty")
if not DHAN_CLIENT_ID:
    raise ValueError("DHAN_CLIENT_ID environment variable is not set or empty")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "client-id": DHAN_CLIENT_ID,
    "access-token": DHAN_API_KEY
}

# Rate Limits for Data APIs
DATA_API_MAX_PER_SECOND = 5
DATA_API_MAX_PER_DAY = 100_000

# Safe throttling constants
SAFE_REQUESTS_PER_SECOND = 2   # Keep some margin
SAFE_SLEEP_BETWEEN_REQUESTS = 1 / SAFE_REQUESTS_PER_SECOND  # Seconds between requests

# Error handling configuration
MAX_RETRIES = 5
RETRY_BACKOFF_FACTOR = 2
RETRY_INITIAL_WAIT = 0.5  # seconds

# Cache directory for temporary data
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)