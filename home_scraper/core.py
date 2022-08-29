from home_scraper.config import DataSource, settings
from home_scraper.notifications.slack import send_message
from home_scraper.scraping.model import Home
from home_scraper.scraping.tags import get_tags_on_website
from home_scraper.storage.enums import StorageLocation
from home_scraper.storage.files import read_homes, write_homes
from home_scraper.storage.s3 import S3, upload_homes_to_s3


FILE_NAME = "existing_homes.txt"


def run() -> int:
    new_homes = _get_new_homes()
    existing_homes = _get_existing_homes()

    new_or_updated_homes = new_homes - existing_homes
    if not new_or_updated_homes:
        print(f"No new homes found")
        return 0

    new_available_homes = {home for home in new_or_updated_homes if home.is_available()}
    for home in new_available_homes:
        message = f"Home available!\n" f"\t{home.address}\n" f"\t{home.full_url}"
        print(message)
        if settings.slack:
            send_message(message=message, channel=settings.slack.channel)

    if settings.storage.mode == StorageLocation.S3:
        upload_homes_to_s3(s3_path=FILE_NAME, homes=existing_homes.union(new_homes))
    else:
        local_homes_file = settings.storage.results_dir / FILE_NAME
        write_homes(
            homes_file=local_homes_file,
            homes=existing_homes.union(new_homes),
            overwrite=True,
        )
    return len(new_or_updated_homes)


def _get_new_homes():
    if settings.data_source == DataSource.LOCAL:
        return read_homes(settings.base_dir / "fixtures" / FILE_NAME)
    return {Home.from_tag(tag) for tag in get_tags_on_website()}


def _get_existing_homes():

    if settings.storage.mode == StorageLocation.S3:
        try:
            data_stream = S3().download_to_memory(s3_path=FILE_NAME)
        except FileNotFoundError:
            return set()
        homes = {Home.parse_raw(data) for data in data_stream.readlines()}
        return homes

    try:
        return read_homes(settings.storage.results_dir / FILE_NAME)
    except FileNotFoundError:
        return set()


if __name__ == "__main__":
    run()
