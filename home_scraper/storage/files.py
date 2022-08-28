from pathlib import Path

from home_scraper.scraping.model import Home


def write_homes(homes_file: Path, homes: set[Home], overwrite: bool = False):
    homes_file.parent.mkdir(parents=True, exist_ok=True)

    if homes_file.is_file() and not overwrite:
        raise FileExistsError
    with homes_file.open("w") as file:
        for home in homes:
            file.write(home.json())
            file.write("\n")


def read_homes(homes_file: Path) -> set[Home]:

    if not homes_file.is_file():
        raise FileNotFoundError

    with homes_file.open() as file:
        json_strings = file.readlines()
    return {Home.parse_raw(json_string) for json_string in json_strings}
