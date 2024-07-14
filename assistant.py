import time

from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI

from utils import extract_json

client = OpenAI()


def get_content_messages(user_prompt: str, screenshot_file=None):
    if screenshot_file:
        return [
            {
                "type": "image_file",
                "image_file": {'file_id': screenshot_file.id, 'detail': 'high'},
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
        # thread = client.beta.threads.create()
        self._thread_id = 'thread_reKRDETVFnpTzt7SHpFyj5N8'
        self._duration_sec = 60
        self._scheduler = BackgroundScheduler()
        job = self._scheduler.add_job(func=self._truncate_old_messages, trigger='interval', minutes=1)
        self._scheduler.start()

    def next_instruction(self, screenshot_path: str, user_prompt: str) -> list:
        print("User Prompt:", user_prompt)
        screenshot_file = None
        if screenshot_path is not None:
            screenshot_file = client.files.create(
                file=open(screenshot_path, "rb"),
                purpose="vision"
            )
        content_messages = get_content_messages(user_prompt, screenshot_file)

        thread_message = client.beta.threads.messages.create(
            self._thread_id,
            role="user",
            content=content_messages,
        )

        res_text = self._run_assistant()
        j = extract_json(res_text)
        if j is None:
            print("The final response from llm:", res_text)
            return {"action": "answer", "reply": res_text}
        print(j)

        return j

    def _run_assistant(self):
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=self._thread_id,
            assistant_id=self._assistant_id,
        )

        # Wait for completion
        while run.status != "completed":
            # Be nice to the API
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=self._thread_id, run_id=run.id)

        # Retrieve the Messages
        messages = client.beta.threads.messages.list(thread_id=self._thread_id)
        new_message = messages.data[0].content[0].text.value
        print(f"Generated message: {new_message}")
        return new_message

    def _truncate_old_messages(self):
        thread_messages = client.beta.threads.messages.list(thread_id=self._thread_id)
        count = 0
        for message in thread_messages.data:
            if message.created_at < time.time() - self._duration_sec:
                client.beta.threads.messages.delete(
                    message_id=message.id,
                    thread_id=self._thread_id,
                )
                count += 1
        if count > 0:
            print('Done truncating old messages!', count)
