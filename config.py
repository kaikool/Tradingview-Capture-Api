"""Configuration settings for TradingView integration"""

urls = {
    "tvcoins": "https://www.tradingview.com/tvcoins/details/",
    "signin": "https://www.tradingview.com/accounts/signin/",
    "tvchart": "https://www.tradingview.com/chart/"
}

# Chart capture settings
CHART_LOAD_TIMEOUT = 10  # seconds
SCREENSHOT_TIMEOUT = 3   # seconds
DEFAULT_ADJUSTMENT = 30

# Rate limiting
REQUESTS_PER_MINUTE = 10
CLEANUP_INTERVAL = 60  # seconds

# Session settings
SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
