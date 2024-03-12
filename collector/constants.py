from pathlib import Path

from decouple import config
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent
STATE_DIR = Path(config("STATE_DIR", default=str(ROOT_DIR / "state")))

VIDEOS_DIR = STATE_DIR / "videos"
STORE_VIDEOS = config("STORE_VIDEOS", default=False, cast=bool)
VIDEOS_CLEANUP_INTERVAL_DAYS = 7

COOKIES_PATH = STATE_DIR / "cookies.json"
EXAMPLES_PATH = Path(__file__).parent.parent / "linkedin_examples" / "search"

HEADLESS = config("HEADLESS", default=False, cast=bool)

BASE_URL = "https://www.linkedin.com"

# LinkedIn URLs
LINKEDIN_LOGIN_URL = f"{BASE_URL}/login"
LINKEDIN_FEED_URL = f"{BASE_URL}/feed/"

PLAYWRIGHT_TIMEOUT = config("PLAYWRIGHT_TIMEOUT", default=1000 * 60 * 5, cast=int)  # in milliseconds, default 5 minutes
