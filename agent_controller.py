import base64
import os

import requests

from utils import extract_json

api_key = os.environ['OPENAI_API_KEY']
# openai.api_key = os.environ['OPENAI_API_KEY']
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

def request_body(messages):
    # Construct the payload
    return {
        'model': 'gpt-4o',
        'messages': messages,
        'temperature': 0,
        'max_tokens': 4096
    }


# Function to encode the image to base64
def encode_image(image_path):
    if not image_path:
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# scroll_ins = """
#             5. **Scrolling Down a Page**:
#             - If you need to scroll down the current webpage, use this JSON format:
#             ```json
#             { "action": "scroll" }
#             ```
#
#             - Always scroll to the end of the page before compiling your final result.
# """

messages = [{
    "role": "system",
    "content": """
            You are a website crawler connected to a web browser. Your task is to find the answer to user prompt
            by giving the following instructions for browsing the web iteratively. 
            You will receive screenshots of the websites you visit.

            **Instructions:** 

            1. **Reading Screenshots**: Always start by carefully examining the content of the screenshot provided to
            you. Do not make assumptions about the links or content; rely only on what you see. 
            Always respond in strict json format only. 
            For each instruction, give a human readable description of what you are doing as well.


            2. **Clicking Links**: 
            Identify links/buttons. 
            To click a link, respond in the following JSON format: 
            ```json 
            { "action": "click", "text": "Link Text", "description": "describe the action"}
            ``` 
            Be precise and do not guess link names. 


            3. **Navigating to Specific URLs**: 
            - To go directly to a specific URL, respond with this JSON format: 
            ```json 
            { "action": "navigate", "url": "https://example.com", "description": "describe the action"} 
            ``` 

            4. **Typing in Input Boxes**: 
            - To type in an input box element, respond with this JSON format:
            - Do not guess the input box's placeholder text. 
            ```json 
            { "action": "type_input", “placeholder”: “exact placeholder text in the input box”, "text": "Search Query",
            "description": "describe the action"} 
            ``` 

            6. **Compiling Results**: 
            - Continue browsing iteratively until you find the answer to the user's question.
            - Once you have found the required information, respond with this JSON format: 
            ```json 
            { "action": "answer", “description”: “The final answer or comments from the llm..."} 
            ``` 

            O7. **Using Google Search**: 
            - For simple queries, you should navigate directly to 'https://google.com/search?q=<search term>'.

            8. **Direct URLs**: 
            - If the user provides a direct URL, navigate to it without making up any links. 

            **Important Guidelines**: 
            - Always be precise and exact in your actions. 
            - Never guess the link names or content. 
            - Do not use any external sources for information, just rely on information from provided screenshots.

           """
}]

def get_step_message(user_prompt: str, img=None):
    content = [
        {
            "type": "text",
            "text": user_prompt
        }
    ]

    if img:
        content.append({
            "type": "image_url",
            "image_url": {'url': f'data:image/jpeg;base64,{img}', 'detail': 'high'},
        })

    return [
            {
                "role": "user",
                "content": content
            }
        ]

class AgentController:
    def __init__(self):
        pass

    def next_instruction(self, screenshot_path: str, user_prompt: str) -> list:
        print("User Prompt:", user_prompt)
        img = encode_image(screenshot_path)
        step_message = get_step_message(user_prompt, img)

        payload = request_body(messages + step_message)
        response = requests.post(url='https://api.openai.com/v1/chat/completions',
                                 headers=headers,
                                 json=payload)

        print("Response from server....")
        res_text = None
        if response.status_code == 200:
            res_text = response.json()['choices'][0]['message']['content']
            print(res_text)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

        j = extract_json(res_text)
        if j is None:
            print("The final response from llm:", res_text)
            return { "action": "answer", "reply": res_text }
        print(j)

        return j
