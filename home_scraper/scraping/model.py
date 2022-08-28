from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from home_scraper.scraping.enums import Status
from home_scraper.scraping.urls import BASE_URL


class Home(BaseModel):
    address: str
    url: str
    price: str
    status: Status
    created: datetime = datetime.now()

    def __hash__(self):
        return hash((self.address, self.status))

    def __eq__(self, other):
        same_address = self.address == other.address
        same_status = self.status == other.status
        return same_address and same_status

    @property
    def full_url(self):
        return BASE_URL + self.url

    @classmethod
    def from_tag(cls, tag: Tag) -> "Home":

        scraped_home = cls(
            address=cls._get_address(tag),
            url=cls._get_url(tag),
            price=cls._get_price(tag),
            status=cls._get_status(tag),
        )
        return scraped_home

    @staticmethod
    def _get_address(tag: Tag) -> str:
        return tag.div.h3.text

    @staticmethod
    def _get_url(tag: Tag) -> str:
        return tag.a.attrs["href"]

    @staticmethod
    def _get_price(tag: Tag) -> tuple[str, Status]:
        money_index = tag.text.find("€")
        if money_index >= 0:
            return tag.text[money_index : money_index + 15].strip()
        return "Onbekend"

    @classmethod
    def _get_status(cls, tag: Tag) -> tuple[str, Status]:
        if "Verhuurd" in tag.text:
            return Status.RENTED

        url = cls._get_url(tag)
        request = requests.get(BASE_URL + url, timeout=10)
        soup = BeautifulSoup(request.text, "html.parser")
        if "Reactietermijn gesloten" in soup.text:
            return Status.VIEWING
        return Status.AVAILABLE

    def is_available(self):
        return self.status == Status.AVAILABLE
