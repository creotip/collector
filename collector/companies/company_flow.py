import logging

from collector.companies.extract_company_metadata import CompanyInfo, extract_company_metadata
from collector.companies.search_results import extract_companies_search_results
from collector.constants import BASE_URL
from collector.helpers import verify_signin
from collector.playwright_manager import PlaywrightManager, SupportedDevices

logger = logging.getLogger(__name__)


def search_companies_flow(search_query: str, number_of_search_results: int = 5) -> list[CompanyInfo]:
    logger.info(f"Searching LinkedIn for: {search_query}")

    with PlaywrightManager(
        SupportedDevices.TABLET_ANDROID_CHROME,
        f"{BASE_URL}/search/results/companies/?keywords={search_query}&origin" f"=SWITCH_SEARCH_VERTICAL&sid=Pz-",
    ) as page:
        search_results = extract_companies_search_results(page, number_of_search_results)

    with PlaywrightManager(SupportedDevices.MOBILE_ANDROID_CHROME) as page:
        companies_metadata = []
        for company_url in search_results:
            if company_url:
                page.goto(f"{company_url}about", wait_until="networkidle")
                verify_signin(page)
                try:
                    profile_metadata = extract_company_metadata(page)
                    companies_metadata.append(profile_metadata)
                except Exception as e:
                    logger.error(f"Error extracting company metadata from {company_url =}: {e}")
                    continue

        return companies_metadata
