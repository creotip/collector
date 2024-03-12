import logging

from collector.constants import BASE_URL
from collector.playwright_manager import PlaywrightManager, SupportedDevices
from collector.users.search_results import UserSearchResult, extract_users_search_results

logger = logging.getLogger(__name__)


def search_users_flow(search_query: str, number_of_search_results: int = 5) -> list[UserSearchResult]:
    logger.info(f"Searching LinkedIn for: {search_query}")
    with PlaywrightManager(
            SupportedDevices.MOBILE_ANDROID_CHROME,
            f"{BASE_URL}/mwlite/search?keyword={search_query}&origin=CLUSTER_EXPANSION&trk=universal-search",
    ) as page:
        search_results = extract_users_search_results(page, number_of_search_results)

        return search_results
