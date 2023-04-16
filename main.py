import json
import schedule
import time
from dotenv import load_dotenv
from scrape import get_wikipedia_current_events, filter_and_print_events
from openai_api import format_summary_and_links, get_summary

load_dotenv()

current_data = ""


def scrape_webpage() -> bool:
    global current_data
    soup = get_wikipedia_current_events()
    content_div = soup.find("div", {"class": "content"})

    if content_div:
        new_data = content_div.text.strip()
    else:
        print("Ohhh Ghhez, there's like no stuff here")
        return False

    if new_data != current_data:
        current_data = new_data
        return True

    return False


def load_events_from_file(filename: str) -> dict:
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_events_to_file(filename: str, events: dict):
    with open(filename, "w") as f:
        json.dump(events, f)


def run():
    filename = "old_events.json"
    old_events = load_events_from_file(filename)

    schedule.every(10).seconds.do(scrape_webpage)

    while True:
        schedule.run_pending()
        soup = get_wikipedia_current_events()
        new_events = filter_and_print_events(soup, old_events)

        if new_events:
            old_events.update(new_events)
            save_events_to_file(filename, old_events)


if __name__ == "__main__":
    run()
