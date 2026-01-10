"""Constants for the DorsalWatch integration."""

DOMAIN = "dorsalwatch"

# Configuration keys
CONF_COUNTRY = "country"
CONF_STATE = "state"
CONF_PUBLIC_KEY = "public_key"
CONF_PAGE_SIZE = "page_size"
CONF_TIME_RANGE = "time_range"

# Default values
DEFAULT_COUNTRY = "Australia"
DEFAULT_PAGE_SIZE = 12
DEFAULT_TIME_RANGE = 0
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# API
API_URL = "https://www.dorsalwatch.com/api/public/report/list"

# Available countries
COUNTRIES = [
    "Australia",
    "Hawaii", 
    "USA",
    "Reunion"
]
