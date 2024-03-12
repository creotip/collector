from datetime import datetime, timedelta

from fastapi import HTTPException
from playwright.sync_api import ElementHandle, Page


def get_inner_text(page: Page | ElementHandle, selector: str, default: str = "") -> str:
    element = page.query_selector(selector)
    return element.inner_text() if element else default


def get_attribute(page: Page | ElementHandle, selector: str, attribute: str, default: str = "") -> str:
    element = page.query_selector(selector)
    return element.get_attribute(attribute) if element else default


def validate_checkpoint(page: Page):
    if "checkpoint" in page.url:
        raise HTTPException(
            status_code=401,
            detail="LinkedIn is asking for additional verification. Please login manually to LinkedIn and complete "
                   "the verification process.",
        )


def verify_signin(page: Page):
    if "signup" in page.url:
        raise HTTPException(
            status_code=401,
            detail="Cookies are expired. You need to login to LinkedIn first. Use the /login endpoint.",
        )


def parse_date_string(date_str):
    if date_str.endswith("mo"):
        number = int(date_str[:-2])
        return timedelta(days=number * 30)
    elif date_str.endswith("yr"):
        number = int(date_str[:-2])
        return timedelta(days=number * 365)
    else:
        unit = date_str[-1]
        number = int(date_str[:-1])

        if unit == "s":
            return timedelta(seconds=number)
        elif unit == "m":
            return timedelta(minutes=number)
        elif unit == "h":
            return timedelta(hours=number)
        elif unit == "d":
            return timedelta(days=number)
        elif unit == "w":
            return timedelta(weeks=number)
        else:
            raise ValueError(f"Unknown time unit: {unit}")


def filter_posts_by_date(days, posts):
    filtered_posts = []
    now = datetime.now()

    for post in posts:
        post_age = parse_date_string(post["date"])
        post_date = now - post_age
        if (now - post_date).days <= days:
            filtered_posts.append(post)

    return filtered_posts


def is_post_date_in_timespan(post_timespan: str, days: float):
    post_age = parse_date_string(post_timespan)
    return post_age <= timedelta(days=days)


def str_to_number(string: str) -> int | None:
    try:
        return int(string)
    except ValueError:
        return None
