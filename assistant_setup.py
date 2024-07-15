from openai import OpenAI
import json

client = OpenAI()

instructions ="""
You are a website navigator connected to a web browser controller. Your task is to help the user reach their goal. \
You will receive screenshot of the webpage you visit. You start on a blank page and the last screenshot always shows \
the webpage you are on right now. Give exactly one of the following precise instruction for the web browser controller 
to execute for the next step and wait for the next image of the webpage. SEND AT MOST ONE INSTRUCTION PER SCREENSHOT \
UPLOAD. Return in exactly one message and wait for the next screenshot. Always respond in strict json format only. \
For each instruction, give a human readable description of what you are doing as well.

**Instructions:** 

1. **Navigating to Specific URLs**: 
- To go directly to a specific URL, respond with the following instruction: 
```json 
{ "action": "navigate", "url": "https://example.com", "description": "describe the action"} 
``` 

2. **Clicking Links**: 
Identify links/buttons. 
To click a link, respond with the following instruction: 
```json 
{ "action": "click", "text": "Link Text", "description": "describe the action"}
``` 
Be precise and do not guess link names.


3. **Scrolling Down a Page**:
- If you need to scroll down the current webpage, reply with the following instruction:
```json
{ "action": "scroll", "description": "describe the action"}
```
- Maybe scroll to the end of the page before compiling your final result.

4. **Typing in Input Boxes**: 
- To type in an input box bounded by a green box in the screenshot, respond with the following instruction:
```json 
{ "action": "type_input", “placeholder”: “exact placeholder text in the input box”, "text": "Search Query",
"description": "describe the action"} 
```
- Do not guess the input box's placeholder text value. 

5. **Compiling Results**: 
- Continue browsing iteratively until you find the answer to the user's question.
- Once you have found the required information, respond with the following: 
```json 
{ "action": "answer", “description”: “The final answer or comments from the llm..."} 
``` 

6. **Using Google Search**: 
- For simple queries, you should navigate directly to 'https://google.com/search?q=<search term>'.

7. **Direct URLs**: 
- If the user provides a direct URL, navigate to it without making up any links. 

**Important Guidelines**: 
- Always be precise and exact in your actions.
- Never guess the link names or content. 
- If there is no screenshot provided, Use the 'navigate' instruction for browser to go to any page.
- Do not use any external sources for information, just rely on information from provided in screenshots.
- If you feel that you are stuck in a loop, respond with answer explaining the problem you are facing.
"""
assistant_name = "Webpage Navigator Assistant"
model = "gpt-4o"
response_format = { "type": "json_object" }

# assistant = client.beta.assistants.create(
#     instructions=instructions,
#     name=assistant_name,
#     tools=[],
#     model=model,
#     temperature=0.5,
#     response_format=response_format,
# )
# assistant_id = "asst_KX0eWXo5YKj9AMA9WXzczQqD" # key1
# assistant_id = 'asst_JMjQ6CwtS03nRLggyXP6UG4z' # personal key
# assistant_id = 'asst_2EFUwo5IxZgyJWGVaOU9W92Z' # key2
assistant_id = 'asst_1cP9cf9BZxW00c8vqIL98UtE' # browser project

# assistant = client.beta.assistants.update(
#   assistant_id=assistant_id,
#   instructions=instructions,
#   name=assistant_name,
#   response_format=response_format,
#   model=model,
#   temperature=0
# )

# assistant = client.beta.assistants.retrieve(assistant_id)
# print(assistant)

# thread = client.beta.threads.create()
# print(thread)
# thread_id = 'thread_reKRDETVFnpTzt7SHpFyj5N8' # key 1
# thread_id = 'thread_owse0VvvuckMn2XdVsQo53wi' # personal key
thread_id = 'thread_qgsTXs2kdJanRoM7J4b3BZK0'
# thread = client.beta.threads.update(
#   thread_id,
#   tool_resources=None,
# )
# print(thread)

def deleteMessages(n):
    thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
    for message in thread_messages.data:
        if n <= 0:
            break
        client.beta.threads.messages.delete(
          message_id=message.id,
          thread_id=thread_id,
        )
        n-=1

# deleteMessages()

# run_id = 'run_cPkjYp48jUwoNcni38I6IuPS'
# run = client.beta.threads.runs.retrieve(
#   thread_id=thread_id,
#   run_id=run_id
# )

# deleted_message = client.beta.threads.messages.delete(
#   message_id='msg_6trz8hZcbA6zIqXbeh58tDrn',
#   thread_id=thread_id,
# )
thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
print('Done!')



