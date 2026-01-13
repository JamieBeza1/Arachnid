import json,os
from dotenv import load_dotenv
from openai import OpenAI 

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment")
client = OpenAI(api_key=API_KEY) 

MODEL = "gpt-5-nano" 

TITLE_PROMPT_PATH = "./arachnid/ai/prompts/title_extraction.txt" 

def get_prompt(prompt_path): 
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f: 
            data = f.read()
            return data
    
title = "New n8n Vulnerability (9.9 CVSS) Lets Authenticated Users Execute System Commands" 

def extract_from_title(title): 
    resp = client.responses.create(
        model=MODEL, 
        instructions=get_prompt(TITLE_PROMPT_PATH), 
        input=f"Return JSON only.\nTITLE:\n{title}", 
        text={"format": {"type": "json_object"}}, ) 
    return json.loads(resp.output_text) 

print(f"ORIGINAL TITLE: {title}") 
print(f"Extracted data: {extract_from_title(title)}")


#print(get_prompt(TITLE_PROMPT_PATH))
