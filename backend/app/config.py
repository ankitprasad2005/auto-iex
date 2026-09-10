import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
DAM_SCRAPE_HOUR = int(os.environ.get("DAM_SCRAPE_HOUR", "13"))
