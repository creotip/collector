import logging
from datetime import datetime

from collector.constants import LINKEDIN_FEED_URL, LINKEDIN_LOGIN_URL
from collector.helpers import validate_checkpoint
from collector.playwright_manager import PlaywrightManager, SupportedDevices
from collector.utils import save_cookies

logger = logging.getLogger(__name__)


def login_to_linkedin(username: str, password: str):
    with PlaywrightManager(
        SupportedDevices.MOBILE_ANDROID_CHROME,
        LINKEDIN_LOGIN_URL,
        set_cookies=False,
        validate_signin=False,
        store_video=True,
    ) as page:
        page.fill("#username", username, strict=True)
        page.fill("#password", password, strict=True)
        page.click('[aria-label="Sign in"]', strict=True)

        validate_checkpoint(page)

        page.wait_for_url(LINKEDIN_FEED_URL)
        save_cookies(page.context.cookies())


def check_linkedin_login() -> datetime:
    logger.info("Checking if LinkedIn cookies are still valid.")
    with PlaywrightManager(SupportedDevices.MOBILE_ANDROID_CHROME, LINKEDIN_FEED_URL) as page:
        return datetime.fromtimestamp(page.context.cookies()[0]["expires"])
