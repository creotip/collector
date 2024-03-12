import logging

from collector.activities.extract_post_activity import extract_post_activity
from collector.activities.models import PostActivity
from collector.playwright_manager import PlaywrightManager, SupportedDevices

logger = logging.getLogger(__name__)


def post_activity_flow(post_url: str) -> PostActivity:
    logger.info(f"Getting user activities for: {post_url}")
    with PlaywrightManager(SupportedDevices.MOBILE_ANDROID_CHROME, post_url) as page:
        res = extract_post_activity(page)
        return res
