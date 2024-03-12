from playwright.sync_api import Page


# The extraction of companies doesn't work on mobile
# on desktop and tablet it works
def extract_companies_search_results(page: Page, number_of_search_results: int) -> list[str | None]:
    search_container = page.locator(".search-results-container")
    search_container.wait_for()

    search_results = []
    search_list = page.query_selector_all(
        ".reusable-search__entity-result-list .reusable-search__result-container .entity-result__universal-image a"
    )

    for item in search_list[:number_of_search_results]:
        profile_url = item.get_attribute("href")
        search_results.append(profile_url)

    return search_results
