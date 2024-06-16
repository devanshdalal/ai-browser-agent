import json
import os
from datetime import datetime


def working_dir() -> str:
    # Get the current date and time
    now = datetime.now()
    # Create a string representing the current date and time
    date_time_string = now.strftime("%Y-%m-%d-%H")
    wd = 'uploads/' + date_time_string
    # Create a folder with the current date and time string as the name
    os.makedirs(wd, exist_ok=True)
    # Print the name of the new folder
    print("Created folder:", wd)
    return wd


def screenshot_file() -> str:
    return 'screenshot-' + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + '.png'

def extract_json(text: str) -> dict:
    json_str = text[text.find("{"):text.find("}") + 1]
    try:
        return json.loads(json_str)
    except:
        print("Failed to extract json out of", text)
        return None

def extract_json1(text: str) -> dict:
    escaped = text.replace("\n", "\\n")
    print("escaped", escaped)
    json_str = escaped[escaped.find("{"):escaped.find("}") + 1]
    print("json_str", json_str)
    return json.loads(json_str)
