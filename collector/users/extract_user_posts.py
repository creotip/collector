from enum import StrEnum, auto

from playwright.sync_api import Page
from pydantic import BaseModel

from collector.constants import BASE_URL
from collector.helpers import get_attribute, get_inner_text


class ActivityType(StrEnum):
    LIKES = auto()
    SUPPORTS = auto()
    FUNNY = auto()
    LOVES = auto()
    CELEBRATES = auto()
    FINDS_THIS_INSIGHTFUL = auto()
    COMMENTED = auto()
    POSTED = auto()


class UserActivity(BaseModel):
    url: str
    content: str
    activity_type: ActivityType


def extract_user_posts(page: Page, posts_to_collect=15) -> list[UserActivity]:
    page.locator("#base-activity").wait_for()
    user_posts = []
    seen_urns = set()
    loading_new_posts_timeout = 5000

    while len(user_posts) < posts_to_collect:
        page.wait_for_selector("#base-activity .feed-container .feed-item article")
        feed_items = page.query_selector_all("ol.feed-container li.feed-item")

        for item in feed_items:
            if len(user_posts) >= posts_to_collect:
                break
            featured_activity_urn = get_attribute(item, "article", "data-featured-activity-urn")
            if featured_activity_urn and featured_activity_urn not in seen_urns:
                activity_url = f"{BASE_URL}/feed/update/{featured_activity_urn}"
                content_selector = ".attributed-text-segment-list__container .attributed-text-segment-list__content"
                content = get_inner_text(item, content_selector)

                activity_type = ActivityType.POSTED
                header_element = item.query_selector(".main-feed-activity-card__header")

                if header_element:
                    header_text = (header_element.inner_text()).lower()
                    for name, keyword in ActivityType.__members__.items():
                        if keyword in header_text:
                            activity_type = ActivityType[keyword.upper()]
                            break
                else:
                    activity_type = ActivityType.POSTED

                user_posts.append(UserActivity(url=activity_url, content=content, activity_type=activity_type))
                seen_urns.add(featured_activity_urn)

        if len(user_posts) < posts_to_collect:
            # Scroll to attempt to load more posts
            page.keyboard.press("End")
            # Wait for the potential loading of new posts
            page.wait_for_timeout(loading_new_posts_timeout)

    return user_posts
