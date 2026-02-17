from seleniumbase import SB
import base64
import random
import time
from dataclasses import dataclass
from typing import Tuple, Dict

import requests

import random
from seleniumbase import SB


REQUIRED_SELECTOR = "#required-element"


def session_cycle(url: str, runtime_range=(450, 800)) -> bool:
    """
    Runs one full browser cycle.
    Returns True if restart should occur.
    Returns False if execution should stop immediately.
    """

    runtime = random.randint(*runtime_range)

    with SB(uc=True, ad_block=True) as primary:

        primary.open(url)

        # Immediate condition check (no waiting)
        if not primary.is_element_present("#live-channel-stream-information"):
            return False  # exit immediately

        # Spawn secondary driver
        secondary = primary.get_new_driver(undetectable=True)

        try:
            secondary.open(url)

            if not secondary.is_element_present(REQUIRED_SELECTOR):
                return False

            primary.sleep(runtime)

        finally:
            secondary.quit()

    return True  # signal restart


'''def main():
    url = "https://example.com"

    while True:
        should_restart = session_cycle(url)

        if not should_restart:
            break  # hard exit if condition not met'''




IP_API_URL = "http://ip-api.com/json/"
DEFAULT_TIMEOUT = 10


@dataclass(frozen=True)
class GeoContext:
    latitude: float
    longitude: float
    timezone: str
    country_code: str


def fetch_geo_context(timeout: int = DEFAULT_TIMEOUT) -> GeoContext:
    """Fetch geolocation context from public IP API."""
    try:
        response = requests.get(IP_API_URL, timeout=timeout)
        response.raise_for_status()
        data: Dict = response.json()

        return GeoContext(
            latitude=data["lat"],
            longitude=data["lon"],
            timezone=data["timezone"],
            country_code=data["countryCode"].lower(),
        )

    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch geolocation data: {exc}") from exc


def decode_channel_name(encoded_name: str) -> str:
    """Decode base64 channel identifier."""
    decoded_bytes = base64.b64decode(encoded_name)
    return decoded_bytes.decode("utf-8")


def build_stream_url(channel_name: str) -> str:
    """Construct stream URL."""
    return f"https://www.twitch.tv/{channel_name}"


def safe_click(sb: SB, selector: str, timeout: int = 4) -> None:
    """Click element if present."""
    if sb.is_element_present(selector):
        sb.cdp.click(selector, timeout=timeout)


def start_session(url: str, geo: GeoContext, runtime: int) -> None:
    """Launch a single browser session."""
    with SB(
        uc=True,
        locale="en",
        ad_block=True,
        chromium_arg="--disable-webgl",
    ) as browser:

        browser.activate_cdp_mode(
            url,
            tzone=geo.timezone,
            geoloc=(geo.latitude, geo.longitude),
        )

        browser.sleep(2)
        safe_click(browser, 'button:contains("Accept")')
        browser.sleep(2)

        safe_click(browser, 'button:contains("Start Watching")')
        browser.sleep(5)

        browser.sleep(runtime)


def main() -> None:
    encoded_name = "YnJ1dGFsbGVz"
    channel_name = decode_channel_name(encoded_name)
    stream_url = build_stream_url(channel_name)
    stream_url = 'https://www.twitch.tv/pgl'
    geo = fetch_geo_context()

    while True:
        should_restart = session_cycle(stream_url)

        if not should_restart:
            break  # hard exit if condition not met


if __name__ == "__main__":
    main()
