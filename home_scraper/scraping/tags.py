import requests
from bs4 import BeautifulSoup, Tag

from home_scraper.scraping.urls import REGION_CODES, SEARCH_URL


def get_tags_on_website() -> list[Tag]:
    page = 1
    tags_on_website = []
    while True:
        tags_on_page = _get_tags_on_page(page)
        if not tags_on_page:
            break
        tags_on_website += tags_on_page
        page += 1
    return tags_on_website


def _get_tags_on_page(page: int) -> list:
    url = f"{SEARCH_URL}{_get_regions()}&page={page}"

    request = requests.get(url, timeout=10)

    soup = BeautifulSoup(request.text, "html.parser")
    tags_on_page = list(soup.select(".block.block-default"))
    return tags_on_page


def _get_regions() -> str:
    regions = ",".join(REGION_CODES.values())
    return f"&regions={regions}"
