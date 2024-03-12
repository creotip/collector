from playwright.sync_api import Page

from collector.helpers import get_attribute, get_inner_text
from collector.users.models import (
    Accomplishments,
    Certification,
    ContactInfo,
    EducationHistory,
    Experience,
    JobPromotion,
    UserProfileMetadata,
)
from collector.utils import (
    element_has_class,
)


def extract_profile_metadata(page: Page) -> UserProfileMetadata:
    page.wait_for_selector("dd.body-small.text-color-text-low-emphasis", timeout=5000)

    profile_url = page.url.split("?")[0]
    profile_name = get_inner_text(page, ".basic-profile-section h1.text-color-text.heading-large")
    profile_image = get_attribute(page, ".basic-profile-section .image-and-actions img", "src")

    open_to_work = check_open_to_work_or_job(page)

    education_selector = (
        "xpath=//dd[contains(@class, 'body-small')][contains(@class, "
        "'text-color-text-low-emphasis')]//span[contains(text(), 'University') or contains(text(), "
        "'School')]"
    )
    education = get_inner_text(page, education_selector)

    current_company = get_inner_text(page, ".member-current-company")

    location_text = get_inner_text(
        page,
        "xpath=//dd[contains(@class, 'body-small text-color-text-low-emphasis')][" "last()]",
    )
    location = location_text.split("\n")[0].strip()  # Location is not parsed properly
    about = get_inner_text(page, ".about-section .summary-container .description")
    experiences: list[Experience] = extract_experiences(page)
    education_history: list[EducationHistory] = extract_education_history(page)
    skills: list[str] = extract_skills(page)
    accomplishments: Accomplishments = extract_accomplishments(page)
    contact_info: list[ContactInfo] = extract_contact_info(page)

    return UserProfileMetadata(
        profile_name=profile_name if profile_name else "",
        profile_url=profile_url,
        profile_image=profile_image,
        open_to_work=open_to_work,
        education=education,
        current_company=current_company if current_company else "",
        location=location,
        about=about if about else "",
        experiences=experiences,
        skills=skills,
        education_history=education_history,
        accomplishments=accomplishments,
        contact_info=contact_info,
    )


def extract_education_history(page: Page) -> list[EducationHistory]:
    education_items = page.query_selector_all(".education-container ol > li.visible-entity")
    education_history = [EducationHistory(title=get_inner_text(item, ".list-item-heading")) for item in education_items]
    return education_history


def extract_skills(page: Page) -> list[str]:
    skills_elements = page.query_selector_all(".skills-container .skill-item")
    skills = [get_inner_text(item, "> span") for item in skills_elements]
    return skills


def extract_accomplishments(page: Page) -> Accomplishments:
    certifications_elements = page.query_selector_all(
        ".accomplishment-list .certifications-section .detail-container ul li"
    )
    certifications = [
        Certification(
            title=get_inner_text(item, ".list-item-heading"),
            issuer=get_inner_text(item, ".list-item-detail > div"),
        )
        for item in certifications_elements
    ]

    languages_elements = page.query_selector_all(".accomplishment-list .languages-section .detail-container ul li")
    languages = [get_inner_text(item, ".list-item-heading") for item in languages_elements]

    return Accomplishments(certifications=certifications, languages=languages)


def extract_contact_info(page: Page) -> list[ContactInfo]:
    contact_info_elements = page.query_selector_all(".contacts-container .contact-info")
    contact_info = [
        ContactInfo(
            title=get_inner_text(item, ".contact-detail-container .contact-title"),
            value=get_inner_text(item, ".contact-detail-container a"),
        )
        for item in contact_info_elements
    ]
    return contact_info


def extract_experiences(page: Page) -> list[Experience]:
    experiences = []
    experience_elements = page.query_selector_all(".experience-container ol > li.visible-entity")
    for item in experience_elements:
        title = get_inner_text(item, ".list-item-heading")
        company_url = get_attribute(item, "a", "href")
        promotions: list[JobPromotion] = []
        if element_has_class(item, "grouped"):
            promotion_elements = item.query_selector_all(".entity-lockup-border ul > li")
            for promotion in promotion_elements:
                job_title = get_inner_text(promotion, "dl > dt")
                raw_date = get_inner_text(promotion, "dl > dd.mr-6.body-small.text-color-text")
                promotions.append(JobPromotion(job_title=job_title, raw_date=raw_date))

        experience = Experience(
            title=title,
            company_url=company_url.split("?")[0] if company_url else None,
            promotions=promotions,
        )
        experiences.append(experience)
    return experiences


def check_open_to_work_or_job(page: Page) -> bool:
    open_to_work_patterns = ["open to work", "open to job"]
    for text in open_to_work_patterns:
        if page.query_selector(f"text=/{text}/i"):
            return True
    return False
