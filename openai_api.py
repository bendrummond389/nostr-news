import json
import requests
import os

api_endpoint = "https://api.openai.com/v1/completions"
api_key = os.environ.get("OPENAI_API_KEY")


def format_summary_and_links(json_string):
    data = json.loads(json_string)
    summary = data.get('summary', 'No summary provided.')
    links = data.get('links', [])

    output = f"Summary:\n{summary}\n\nLinks:\n"
    for i, link in enumerate(links, start=1):
        output += f"{i}. {link}\n"

    return output


def get_summary(link) -> str:
    parameters = {
        "model": "text-davinci-003",
        "prompt": f"Please provide a JSON format output. Find 3 articles related to this one {link} combine and summarize them return a json with 2 fields summary and links",
        "max_tokens": 2000,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.post(api_endpoint, headers=headers, json=parameters)
    if response.status_code == 200:
        response_json = response.json()
        generated_text = response_json["choices"][0]["text"]
        return generated_text
    else:
        raise Exception(f"API request failed with status code: {response.status_code}")
