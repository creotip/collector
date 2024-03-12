from contextlib import ContextDecorator
from datetime import datetime
from enum import Enum

from fastapi import HTTPException
from playwright.sync_api import Page, sync_playwright

from collector.constants import HEADLESS, ROOT_DIR, STORE_VIDEOS, VIDEOS_CLEANUP_INTERVAL_DAYS, VIDEOS_DIR
from collector.helpers import verify_signin
from collector.utils import clean_directory_old_files, load_cookies


# Full list of supported devices located here:
# https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json
class SupportedDevices(Enum):
    DESKTOP_CHROME = "Desktop Chrome"
    MOBILE_ANDROID_CHROME = "Pixel 7"
    MOBILE_IPHONE_SAFARI = "iPhone 13"
    TABLET_ANDROID_CHROME = "Galaxy Tab S4"
    TABLET_IPAD_SAFARI = "iPad (gen 7)"


class PlaywrightManager(ContextDecorator):
    def __init__(
            self,
            device: SupportedDevices,
            url: str | None,
            set_cookies: bool = True,
            validate_signin: bool = True,
            store_video: bool = STORE_VIDEOS,
    ):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.device = device
        self.launch_url = url

        self.set_cookies = set_cookies
        self.validate_signin = validate_signin
        self.store_video = store_video
        self.start_time = datetime.now()

    def __enter__(self) -> Page:
        try:
            return self._setup()
        except Exception as e:
            self._teardown(e)
            raise

    def __exit__(self, *exc):
        self._teardown(*exc)

    def _setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=HEADLESS, slow_mo=5000)

        record_video_dir = None
        if self.store_video:
            record_video_dir = ROOT_DIR / "videos"

        self.context = self.browser.new_context(
            record_video_dir=record_video_dir, **self.playwright.devices[self.device.value]
        )

        if self.set_cookies:
            try:
                cookies = load_cookies()
                self.context.add_cookies(cookies)
            except FileNotFoundError:
                raise HTTPException(
                    status_code=401,
                    detail="No cookies were found. You need to login to LinkedIn first. Use the /login endpoint.",
                )

        self.page = self.context.new_page()
        if self.launch_url:
            self.page.goto(self.launch_url)
            if self.validate_signin:
                verify_signin(self.page)

        return self.page

    def _teardown(self, *exc):
        # If exception was raised, wait a couple of seconds to capture the last frame of the video
        if self.store_video and exc[0]:
            if self.page:
                self.page.wait_for_timeout(5 * 1000)

        if self.context:
            self.context.close()

        if self.store_video and self.page:
            self._store_video()

        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _store_video(self):
        default_filename_base = "video"

        url_to_parse = self.launch_url if self.launch_url else self.page.url
        if isinstance(url_to_parse, str) and "/" in url_to_parse:
            path_component = url_to_parse.strip("/").split("/")[-1]
        else:
            # Fallback to a default value if the URL does not contain "/"
            path_component = default_filename_base

        # In case there's a & in the URL, we want to remove it and everything after it
        path_component = path_component.split("&")[0]

        time = self.start_time.strftime("%H-%M-%S")
        date = self.start_time.strftime("%Y-%m-%d")
        file_name = f"{path_component}_{time}.webm"

        file_path = VIDEOS_DIR / date / file_name

        self.page.video.save_as(file_path)
        self.page.video.delete()

        clean_directory_old_files(VIDEOS_DIR, VIDEOS_CLEANUP_INTERVAL_DAYS)
