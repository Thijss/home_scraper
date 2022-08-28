import sys

from home_scraper.config import DataSource, settings
from home_scraper.notifications.slack import send_message
from home_scraper.scraping.model import Home
from home_scraper.scraping.tags import get_tags_on_website
from home_scraper.storage.enums import StorageMode
from home_scraper.storage.files import read_homes, write_homes
from home_scraper.storage.s3 import S3

FILE_NAME = "existing_homes.txt"


def _get_new_homes():
    if settings.data_source == DataSource.LOCAL:
        return read_homes(settings.base_dir / "fixtures" / FILE_NAME)
    return {Home.from_tag(tag) for tag in get_tags_on_website()}


def _get_existing_homes():

    local_homes_path = settings.storage.storage_dir / FILE_NAME
    if settings.storage.mode == StorageMode.AWS:
        try:
            S3().download_file(s3_path=FILE_NAME, local_path=local_homes_path)
        except FileNotFoundError:
            return set()

    try:
        return read_homes(local_homes_path)
    except FileNotFoundError:
        return set()


if __name__ == "__main__":
    new_homes = _get_new_homes()
    existing_homes = _get_existing_homes()

    new_or_updated_homes = new_homes - existing_homes

    if not new_or_updated_homes:
        sys.exit(0)

    local_homes_file = settings.storage.storage_dir / FILE_NAME
    write_homes(
        homes_file=local_homes_file,
        homes=existing_homes.union(new_homes),
        overwrite=True,
    )
    if settings.storage.mode == StorageMode.AWS:
        S3().upload_file(FILE_NAME, local_path=local_homes_file)

    available_homes = {home for home in new_or_updated_homes if home.is_available()}
    for home in available_homes:
        message = f"Home available!\n" f"\t{home.address}\n" f"\t{home.full_url}"
        if settings.slack:
            send_message(message=message, channel=settings.slack.channel)
