from home_scraper.core import run


def handler(event: dict, context: dict):
    print("#### START ####")
    print("EVENT:", event)
    print("CONTEXT:", context)
    nr_of_new_homes = run()
    print("#### END ####")
    return {"new_homes": nr_of_new_homes}
