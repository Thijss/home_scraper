import logging

from home_scraper.core import run

FILE_NAME = "existing_homes.txt"


def handler(event, context):
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting HomeScraper")
    number_of_houses = run()
    logging.info("Completed HomeScraper")

    return {"new_houses": number_of_houses}
