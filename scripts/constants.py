# scripts/constants.py

import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URLs
DHAN_CHARTS_HISTORICAL_URL = "https://api.dhan.co/v2/charts/historical"

# Date Range
FROM_DATE = "2000-01-01"
TO_DATE = datetime.now().strftime("%Y-%m-%d")

# Timezone
INDIA_TZ = timezone(timedelta(hours=5, minutes=30))

# Access Token and Common API Headers
DHAN_API_KEY = os.getenv("DHAN_API_KEY", "").strip()

HEADERS = {
    "Content-Type": "application/json",
    "access-token": DHAN_API_KEY
}

# Rate Limits for Data APIs
DATA_API_MAX_PER_SECOND = 5
DATA_API_MAX_PER_DAY = 100_000

# Safe throttling constants
SAFE_REQUESTS_PER_SECOND = 1   # Keep some margin
SAFE_SLEEP_BETWEEN_REQUESTS = 1 / SAFE_REQUESTS_PER_SECOND # 1 seconds sleep
