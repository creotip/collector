from playwright.sync_api import Page
from pydantic import BaseModel

from collector.helpers import get_attribute


class UserSearchResult(BaseModel):
    profile_url: str
    profile_image: str


def extract_users_search_results(page: Page, number_of_search_results: int) -> list[UserSearchResult]:
    search_container = page.locator(".search-container")
    search_container.wait_for()

    search_results = []
    search_list = page.query_selector_all(".search-list li a")

    for item in search_list[:number_of_search_results]:
        profile_url = item.get_attribute("href")
        profile_image = get_attribute(item, "img", "src")
        search_results.append(
            UserSearchResult(
                profile_url=profile_url,
                profile_image=profile_image,
            )
        )

    return search_results
