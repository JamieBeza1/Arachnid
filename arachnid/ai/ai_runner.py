import json
from openai import OpenAI

client = OpenAI()

MODEL = "gpt-5-nano"
TITLE_PROMPT_PATH = "/home/beza/Arachnid/arachnid/ai/prompts/title_extraction.txt"

def get_prompt(prompt_path):
    with open(prompt_path, "r") as f:
        data = f.read()
    return data

title = "New n8n Vulnerability (9.9 CVSS) Lets Authenticated Users Execute System Commands"

def extract_from_title(title):
    resp = client.responses.create(model=MODEL,
                                   instructions=get_prompt(TITLE_PROMPT_PATH),
                                   input=f"TITLE:\n{title}",
                                   text={"format": {"type": "json_object"}},
    )
    return json.loads(resp.output_text)

print(f"ORIGINAL TITLE: {title}")
print(f"Extracted data: {extract_from_title(title)}")