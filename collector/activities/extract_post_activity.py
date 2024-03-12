import time

from playwright.sync_api import Page

from collector.activities.extract_comments import extract_comments
from collector.activities.models import PostActivity, User
from collector.helpers import str_to_number


def extract_post_activity(page: Page) -> PostActivity:
    page.wait_for_selector(".feed-item", timeout=5000)

    user_name_selector = 'a[data-tracking-control-name="feed-detail_main-feed-card_feed-actor-name"]'
    user_url = page.get_attribute(user_name_selector, "href")
    user_name = page.inner_text(user_name_selector)

    company_selector = 'div[data-test-id="main-feed-activity-card__entity-lockup"] p'
    company = page.inner_text(company_selector)

    time_selector = 'div[data-test-id="main-feed-activity-card__entity-lockup"] time'
    time_posted = page.inner_text(time_selector)

    content = page.inner_text('p[data-test-id="main-feed-activity-card__commentary"]')

    number_of_reactions_text = page.inner_text('a[data-test-id="social-actions__reactions"] span')
    number_of_reactions = str_to_number(number_of_reactions_text)
    number_of_comments_text = page.inner_text('a[data-test-id="social-actions__comments"]')
    number_of_comments = str_to_number(number_of_comments_text)

    def get_scroll_height():
        return page.evaluate("document.documentElement.scrollHeight")

    last_height = get_scroll_height()
    should_scroll = True

    while should_scroll:
        page.keyboard.press("End")
        time.sleep(2)
        new_height = get_scroll_height()
        if new_height == last_height:
            break
        last_height = new_height

    comments_list_elements = page.query_selector_all(".comments-list .comments-list__parent-comment-item")

    comments_list = extract_comments(comments_list_elements)

    return PostActivity(
        user=User(user_url=user_url, user_name=user_name, company=company),
        time_posted=time_posted,
        content=content,
        number_of_reactions=number_of_reactions,
        number_of_comments=number_of_comments,
        comments_list=comments_list,
    )
