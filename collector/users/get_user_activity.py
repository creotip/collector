import logging

from collector.constants import BASE_URL
from collector.playwright_manager import PlaywrightManager, SupportedDevices
from collector.users.extract_user_posts import UserActivity, extract_user_posts

logger = logging.getLogger(__name__)


def get_user_activity(user_linkedin_slug: str, posts_to_collect: int = 15) -> list[UserActivity]:
    logger.info(f"Getting user activities for: {user_linkedin_slug}")
    with PlaywrightManager(
        SupportedDevices.MOBILE_ANDROID_CHROME, f"{BASE_URL}/mwlite/profile/in/{user_linkedin_slug}/recent-activity"
    ) as page:
        search_results = extract_user_posts(page, posts_to_collect)

        return search_results
