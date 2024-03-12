import json
import os
import random

import pytest
from decouple import config
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import sync_playwright

from collector.activities.post_activity_flow import post_activity_flow
from collector.companies.company_flow import search_companies_flow
from collector.companies.extract_company_metadata import CompanyInfo
from collector.constants import ROOT_DIR
from collector.login.login_page import login_to_linkedin
from collector.playwright_manager import SupportedDevices
from collector.users.extract_profile_metadata import extract_profile_metadata
from collector.users.get_user_activity import get_user_activity
from collector.users.models import UserProfileMetadata
from collector.users.users_flow import search_users_flow
from collector.utils import load_cookies

load_dotenv()

SAVE_MOCK_DATA = config("SAVE_MOCK_DATA", default=False, cast=bool)

LINKEDIN_ME_PROFILE_URL = "https://www.linkedin.com/me?trk=p_mwlite_profile_self-secondary_nav"
LINKEDIN_USER_PROFILE_URL = "https://www.linkedin.com/in/inbarshirizly/"
LINKEDIN_USER_PROFILE_URL_OPEN_TO_WORK = "https://www.linkedin.com/in/saveenaseth25/"
LINKEDIN_USER_SLUG_WITH_ACTIVITY = "adir-kandel"
LINKEDIN_USER_POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7163923270633734145/"
MOCK_DATA_DIR = ROOT_DIR / "tests" / "data"


@pytest.fixture
def search_company_query() -> str:
    return random.choice(["microdot", "google", "apple", "amazon", "facebook", "revrod", "linkedin", "microsoft"])


@pytest.fixture
def search_user_query() -> str:
    return Faker().name()


NUMBER_OF_SEARCH_RESULTS = 2


def test_login_and_save_cookies():
    linkedin_username = os.environ["LINKEDIN_USERNAME"]
    linkedin_password = os.environ["LINKEDIN_PASSWORD"]

    login_to_linkedin(linkedin_username, linkedin_password)


def test_me_profile():
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        context = browser.new_context(**p.devices[SupportedDevices.MOBILE_ANDROID_CHROME.value])
        page = context.new_page()
        context.add_cookies(load_cookies())

        page.goto("https://www.linkedin.com")
        assert "Feed" in page.title()

        page.goto(LINKEDIN_ME_PROFILE_URL)

        profile_name = page.text_content(".basic-profile-section h1.text-color-text.heading-large")
        profile_role = page.text_content(".basic-profile-section dd.body-small.text-color-text span")

        print(
            {
                "profileName": profile_name,
                "profileRole": profile_role,
            }
        )
        context.close()


def test_user_profile():
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        context = browser.new_context(**p.devices[SupportedDevices.MOBILE_ANDROID_CHROME.value])
        page = context.new_page()
        context.add_cookies(load_cookies())

        page.goto("https://www.linkedin.com", wait_until="networkidle")
        assert "Feed" in page.title()

        page.goto(LINKEDIN_USER_PROFILE_URL, wait_until="networkidle")

        page.wait_for_selector("dd.body-small.text-color-text-low-emphasis")

        profile_metadata = extract_profile_metadata(page)
        print(profile_metadata)

        context.close()


def test_search_users(search_user_query: str, save_mock_data: bool = SAVE_MOCK_DATA):
    test_me_profile()
    profiles_metadata: list[UserProfileMetadata] = search_users_flow(
        search_query=search_user_query, number_of_search_results=NUMBER_OF_SEARCH_RESULTS
    )
    if save_mock_data:
        with open(MOCK_DATA_DIR / "generated" / "generated_users_found.json", "w") as f:
            json.dump([json.loads(c.model_dump_json()) for c in profiles_metadata], f, indent=2)
    assert len(profiles_metadata) == NUMBER_OF_SEARCH_RESULTS


def test_search_companies(search_company_query: str, save_mock_data: bool = SAVE_MOCK_DATA):
    companies_metadata: list[CompanyInfo] = search_companies_flow(
        search_query=search_company_query, number_of_search_results=NUMBER_OF_SEARCH_RESULTS
    )
    if save_mock_data:
        with open(MOCK_DATA_DIR / "generated" / "generated_companies_found.json", "w") as f:
            json.dump([json.loads(c.model_dump_json()) for c in companies_metadata], f, indent=2)
    assert len(companies_metadata) == NUMBER_OF_SEARCH_RESULTS


def test_get_user_activities(save_mock_data: bool = SAVE_MOCK_DATA):
    activities = get_user_activity(LINKEDIN_USER_SLUG_WITH_ACTIVITY, posts_to_collect=15)
    if save_mock_data:
        with open(MOCK_DATA_DIR / "generated" / "generated_activities_found.json", "w") as f:
            json.dump([json.loads(c.model_dump_json()) for c in activities], f, indent=2)


def test_get_post_activity():
    activity = post_activity_flow(LINKEDIN_USER_POST_URL)
    with open(MOCK_DATA_DIR / "generated" / "generated_post_activity.json", "w") as f:
        json.dump(json.loads(activity.model_dump_json()), f, indent=2)
