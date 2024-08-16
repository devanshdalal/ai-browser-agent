import base64
import logging
import os

import requests
from requests.adapters import HTTPAdapter, Retry

from utils import extract_json

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)

MODEL = "gpt-4o"
api_key = os.environ['OPENAI_API_KEY']


# openai.api_key = os.environ['OPENAI_API_KEY']


# Function to encode the image to base64
def encode_image(image_path):
    if not image_path:
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


SYSTEM = """
You are a website navigator connected to a web browser controller. Your task is to provide next instruction for the controller, eventually reaching user's target. You will receive screenshot(s) of the webpage you visit. You start on a blank page and the last screenshot is of webpage you are on right now. Produce exactly one of the following precise instruction for the web browser controller to execute as the next step and wait for the next image of the webpage. Always respond in strict json format only. Give a human readable description of the instruction as well. Select ONLY one instruction from the below instruction set.

**Instruction Set:**

1. **Navigating to Specific URLs**: 
- To go directly to a specific URL, respond with the following instruction: 
```json 
{ "action": "navigate", "url": "https://example.com", "description": "describe the action on what you are doing"} 
``` 

2. **Clicking Links**: 
Identify links/buttons. 
To click a link, respond with the following instruction: 
```json 
{ "action": "click", "text": "Link Text", "description": "describe the action on what you are doing"}
``` 
Be precise and do not guess link names.


3. **Scrolling Down a Page**:
- If you need to scroll down the current webpage, reply with the following instruction:
```json
{ "action": "scroll", "description": "describe the action on what you are doing"}
```
- Maybe scroll to the end of the page before compiling your final result.

4. **Typing in Input Boxes**: 
- To type in an input box bounded by a green box in the screenshot, respond with the following instruction:
```json 
{ "action": "type_input", "placeholder": "exact placeholder text in the input box", "text": "Search Query",
"description": "describe the action on what you are doing"} 
```
- Do not guess the input box's placeholder text value. 

5. **Compiling Results**: 
- Continue browsing iteratively until you find the answer to the user's question.
- Once you have found the required information, respond with the following: 
```json 
{ "action": "answer", "description": "The final answer or comments from the llm..."} 
``` 

6. **Using Google Search**: 
- For simple queries, you should navigate directly to 'https://google.com/search?q=<search term>'.

**Important Guidelines**: 
- DO NOT return more than one instruction at a time for at any step.
- Never guess the instruction. ALWAYS wait for the controller to acknowledge before giving the next instruction.
- If there is no screenshot provided, Use the 'navigate' instruction for browser to go to any page.
- Do not provide any information from your memory. Always use the information from the screenshot provided. DO NOT use any information that is not present in the screenshot.
- If you observe that assistant is stuck in giving same instructions again and again, respond with answer explaining the problem you are facing.
"""

examples = """
**Examples**:
instruction: Buy me a smartphone from amazon.in
reply: 
```
{ "action": "navigate", "url": "https://www.amazon.in", "description": "Navigating to Amazon India homepage." }
```

instruction: Tell me a the price of vivo t3x from smartprix
reply:
```
{ "action": "navigate", "url": "https://www.smartprix.in", "description": "Navigating to Amazon India homepage." }
```

instruction: From screener.in, what is the PE ratio of State Bank of India share
reply: 
```
{ "action": "navigate", "url": "https://www.screener.in", "description": "Navigating to Screener.in homepage." }
```
"""


def _is_prompt_containing(message: dict) -> bool:
    return message['role'] == 'user' and message['content'][0]['type'] == 'text'


class ChatController:
    def __init__(self):
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self._requests_session = requests.Session()
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504], allowed_methods=["POST"])
        self._requests_session.mount('http://', HTTPAdapter(max_retries=retries))
        self._messages = self._init_messages()

    def next_instruction(self, screenshot_path: str, user_prompt: str) -> dict:
        if screenshot_path is None and user_prompt is None:
            raise ValueError("Both prompt and screenshot are empty")
        if screenshot_path is None:
            self._messages = self._init_messages()
            self._append_message(prompt=user_prompt)
        else:  # user_prompt may be empty or not
            img = encode_image(screenshot_path)
            self._append_message(img=img, prompt=user_prompt)

        response = self._requests_session.post(url='https://api.openai.com/v1/chat/completions',
                                               headers=self._headers,
                                               json=self._request_body())
        # response = requests.post(url='https://api.openai.com/v1/chat/completions',
        #                          headers=self._headers,
        #                          json=self._request_body())

        print("Response from server....", response)
        res_text = None
        if response.status_code == 200:
            res_text = response.json()['choices'][0]['message']['content']
            print(res_text)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return {"action": "answer", "reply": "Error in processing the request"}

        json_str = extract_json(res_text)
        if json_str is None:
            print("The final response from llm:", res_text)
            return {"action": "answer", "reply": res_text}
        self._append_message(img=None, role="assistant", prompt=res_text)

        self._truncate(last_k=1)

        return json_str

    def _append_message(self, role: str = "user", prompt: str = '', img=None):
        content = []
        if prompt:
            content.append(
                {
                    "type": "text",
                    "text": prompt
                }
            )
        if img:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {'url': f"data:image/jpeg;base64,{img}", "detail": "high"},
                }
            )
        if content:
            self._messages.append({
                "role": role,
                "content": content
            })
        print("Message Count:", len(self._messages))

    def _truncate(self, last_k=0):
        retain = []
        scroll_active = True
        length = len(self._messages)
        ind = length - 1
        while ind >= 0:
            m = self._messages[ind]
            if m['role'] == 'assistant':
                scroll_active = scroll_active and ('scroll' in m['content'][0]['text'])
            if ind >= length - last_k:
                retain.append(m)
            elif _is_prompt_containing(m):
                retain.append(m)
            elif scroll_active:
                retain.append(m)
            elif m['role'] == 'system':
                retain.append(m)

            ind -= 1
        self._messages = list(reversed(retain))

    def _init_messages(self):
        return [{
            "role": "system",
            "content": SYSTEM
        }]

    # Construct the payload for the request
    def _request_body(self):
        return {
            'model': MODEL,
            'messages': self._messages,
            'temperature': 0,
            'max_tokens': 2048
        }
