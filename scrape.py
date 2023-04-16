import asyncio
import requests
from bs4 import BeautifulSoup
import datetime
from nostr_submit import publish_to_nostr
from openai_api import *


def get_wikipedia_current_events() -> BeautifulSoup:
    today = datetime.datetime.now().strftime("%Y_%B_%-d")
    url = f"https://en.wikipedia.org/wiki/Portal:Current_events/{today}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def filter_and_print_events(soup: BeautifulSoup, old_events: dict) -> dict:
    new_events = {}
    body_content = soup.find("div", {"id": "bodyContent"})
    list_items = body_content.find_all("li")[3:]
    innermost_list_items = [li for li in list_items if not li.find("ul")]

    for idx, li in enumerate(innermost_list_items):
        event_text = li.text.strip()

        if event_text not in old_events:
            external_links = li.find_all("a", {"class": "external"})
            non_wiki_links = [link["href"] for link in external_links]
            new_events[event_text] = non_wiki_links

            event_data = {
                "summary": f"{idx + 1}. {event_text}",
                "links": non_wiki_links,
            }
            formatted_event = format_summary_and_links(json.dumps(event_data))
            print(formatted_event)
            asyncio.run(publish_to_nostr(formatted_event))
            
            

    return new_events
