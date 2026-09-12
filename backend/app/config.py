import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
DAM_SCRAPE_HOUR = int(os.environ.get("DAM_SCRAPE_HOUR", "13"))

# Single-user, no-auth tool with no cookies/session state to leak, so a
# wildcard default is safe; override with a comma-separated list in
# deployments that want to restrict it.
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
