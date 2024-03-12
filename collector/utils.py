import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import ElementHandle

from collector.constants import COOKIES_PATH

LINKEDIN_COOKIE = "li_at"


def save_cookies(cookies):
    if not COOKIES_PATH.parent.exists():
        COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Only save the LinkedIn cookie
    cookies = list(filter(lambda cookie: cookie["name"] == LINKEDIN_COOKIE, cookies))

    with COOKIES_PATH.open("w") as file:
        json.dump(cookies, file, indent=2)


def load_cookies() -> dict[str, str]:
    with COOKIES_PATH.open("r") as file:
        return json.load(file)


# Example of how to use saveUserProfileMetadataToFile (assuming similar JSON serialization as in save_cookies_to_file)
def save_user_profile_metadata_to_file(path: str, metadata):
    with open(path, "w") as file:
        json.dump(metadata, file, indent=2)


def save_data_to_file(path: str, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=2)


def element_has_class(element: ElementHandle, class_name: str) -> bool:
    """Check if the element has the specified class name."""
    return element.evaluate(f"(element) => element.classList.contains('{class_name}')")


def clean_directory_old_files(dirname: Path, days_old: int):
    for file in dirname.iterdir():
        if (datetime.now() - datetime.fromtimestamp(file.stat().st_ctime)).days > days_old:
            if file.is_dir():
                for nested_file in file.iterdir():
                    nested_file.unlink()
                file.rmdir()
            else:
                file.unlink()
