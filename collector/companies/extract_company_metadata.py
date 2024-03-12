from playwright.sync_api import Page
from pydantic import BaseModel

from collector.helpers import get_attribute, get_inner_text


class CompanyInfo(BaseModel):
    name: str
    profile_image: str
    profile_url: str
    description: str
    about: str
    website: str
    industry: str
    headquarters: str
    organization_type: str
    founded: str
    company_size: str
    specialties: list[str]

    class Config:
        str_strip_whitespace = True


def extract_company_metadata(page: Page) -> CompanyInfo:
    # top card section
    name = get_inner_text(page, "h1.top-card-layout__title")
    profile_url = page.url
    profile_image = get_attribute(page, ".top-card-layout__entity-image-container img", "src")
    description = get_inner_text(page, "h4.top-card-layout__second-subline")

    # about section
    about = get_inner_text(page, 'p[data-test-id="about-us__description"]')
    website = get_inner_text(page, 'div[data-test-id="about-us__website"] dd a')
    industry = get_inner_text(page, 'div[data-test-id="about-us__industry"] dd')
    company_size = get_inner_text(page, 'div[data-test-id="about-us__size"] dd')
    headquarters = get_inner_text(page, 'div[data-test-id="about-us__headquarters"] dd')
    organization_type = get_inner_text(page, 'div[data-test-id="about-us__organizationType"] dd')
    founded = get_inner_text(page, 'div[data-test-id="about-us__foundedOn"] dd')

    specialties_str = get_inner_text(page, 'div[data-test-id="about-us__specialties"] dd')
    specialties = specialties_str.split(",")
    if specialties[-1].removeprefix("and "):
        last_item = specialties[-1].split("and ")[-1]
        specialties[-1] = last_item

    return CompanyInfo(
        name=name,
        profile_image=profile_image,
        profile_url=profile_url,
        description=description,
        about=about,
        website=website,
        industry=industry,
        headquarters=headquarters,
        organization_type=organization_type,
        founded=founded,
        company_size=company_size,
        specialties=specialties,
    )
