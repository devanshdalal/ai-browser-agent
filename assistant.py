import time

from openai import OpenAI

from utils import extract_json

client = OpenAI()


def get_content_messages(user_prompt: str, screenshot_file=None):
    if screenshot_file:
        return [
            {
                "type": "image_file",
                "image_file": {'file_id': screenshot_file.id, 'detail': 'auto'},
            }
        ]
    else:
        return [
            {
                "type": "text",
                "text": user_prompt
            }
        ]


class WebpageNavigatorAssistant:
    def __init__(self):
        self._assistant_id = "asst_KX0eWXo5YKj9AMA9WXzczQqD"
        self._thread_id = 'thread_reKRDETVFnpTzt7SHpFyj5N8'

    def next_instruction(self, screenshot_path: str, user_prompt: str) -> dict:
        print("User Prompt:", user_prompt)
        screenshot_file = None
        if screenshot_path is not None:
            screenshot_file = client.files.create(
                file=open(screenshot_path, "rb"),
                purpose="vision"
            )
        else:
            self._truncate_messages()
        content_messages = get_content_messages(user_prompt, screenshot_file)

        thread_message = client.beta.threads.messages.create(
            self._thread_id,
            role="user",
            content=content_messages,
        )

        res_text = self._run_assistant()
        json_object = extract_json(res_text)
        if json_object is None:
            print("The final response from llm:", res_text)
            json_object = {"action": "answer", "reply": str(res_text)}
        return json_object

    def _run_assistant(self):
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=self._thread_id,
            assistant_id=self._assistant_id,
        )

        # Wait for completion
        while run.status != "completed":
            # Be nice to the API
            time.sleep(0.4)
            run = client.beta.threads.runs.retrieve(thread_id=self._thread_id, run_id=run.id)

        # Retrieve the Messages
        messages = client.beta.threads.messages.list(thread_id=self._thread_id)
        new_message = messages.data[0].content[0].text.value
        print(f"Generated message: {new_message}")
        return new_message

    def _truncate_messages(self):
        thread_messages = client.beta.threads.messages.list(thread_id=self._thread_id)
        count = 0
        for message in thread_messages.data:
            client.beta.threads.messages.delete(
                message_id=message.id,
                thread_id=self._thread_id,
            )
            count += 1
        if count > 0:
            print('Done truncating messages =', count)
