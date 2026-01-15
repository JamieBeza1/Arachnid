import json, os, logging, sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
#from arachnid import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from arachnid.logger import get_logger

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Quitting...")

logger = get_logger(__name__, logging.DEBUG)

client = OpenAI(api_key=API_KEY)

MODEL = "gpt-5-nano"
TITLE_PROMPT_PATH = f"{os.getcwd()}/arachnid/ai/prompts/title_extraction.txt"
#TITLE = "New n8n Vulnerability (9.9 CVSS) Lets Authenticated Users Execute System Commands" 

class AIRunner:
    MODEL = "gpt-5-nano"
    TITLE_PROMPT_PATH = f"{os.getcwd()}/prompts/title_extraction.txt"

    @staticmethod
    def get_prompt(prompt_location):
        try:
            with open(prompt_location, "r") as f:
                data = f.read()
            return data
        except FileNotFoundError as e:
            logger.error(f"No prompt found: {prompt_location} - ({e})")

    @classmethod
    def send_data(cls, title, prompt):
        response = client.responses.create(
            model=cls.MODEL,
            instructions=cls.get_prompt(prompt),
            input=f"Retrun JSON only.\nTITLE:\n{title}",
            text={"format": {"type": "json_object"}},
        )
        return json.loads(response.output_text)

    @classmethod
    def title_summary(cls, title):
        return cls.send_data(title,TITLE_PROMPT_PATH)
    
    @classmethod
    def body_summary(cls, title, body):
        return


"""
ai = AIRunner()
title_json = ai.send_data(TITLE, TITLE_PROMPT_PATH)
print(f"Original Title: {TITLE}")
print(f"Extracted Data: {title_json}")
"""
