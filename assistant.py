import time, atexit

from openai import OpenAI

from utils import extract_json

client = OpenAI()


def get_content_messages(user_prompt: str, screenshot_file=None):
    content_messages = []
    if user_prompt and user_prompt.strip():
        content_messages.append({
            "type": "text",
            "text": user_prompt
        })
    if screenshot_file:
        content_messages.append(
            {
                "type": "image_file",
                "image_file": {'file_id': screenshot_file.id, 'detail': 'high'},
            })
    return content_messages


class WebpageNavigatorAssistant:
    def __init__(self):
        # self._assistant_id = 'asst_JMjQ6CwtS03nRLggyXP6UG4z' # "asst_KX0eWXo5YKj9AMA9WXzczQqD"
        # self._thread_id = 'thread_owse0VvvuckMn2XdVsQo53wi'# 'thread_reKRDETVFnpTzt7SHpFyj5N8'
        self._assistant_id = 'asst_2EFUwo5IxZgyJWGVaOU9W92Z'  # key2
        # self._thread_id = 'thread_y6gZmLdiXV0myvlW3uKngHmd' # key2
        self._thread_id = None  # key2
        atexit.register(self._close)

    def next_instruction(self, screenshot_path: str, user_prompt: str) -> dict:
        print("User Prompt:", user_prompt)
        screenshot_file = None
        if screenshot_path is not None:
            screenshot_file = client.files.create(
                file=open(screenshot_path, "rb"),
                purpose="vision"
            )
        else:
            self._maybe_delete_thread()
            self._create_thread()
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

    # Run the assistant
    def _run_assistant(self):
        run = client.beta.threads.runs.create(
            thread_id=self._thread_id,
            assistant_id=self._assistant_id,
            max_completion_tokens=2000
        )
        print("Run created:", run.id)

        # Wait for completion
        while run.status != "completed":
            # Be nice to the API
            print(run.status)
            if run.status == "failed":
                print("Run failed", run)
                return ""
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=self._thread_id, run_id=run.id)

        # Retrieve the Messages
        messages = client.beta.threads.messages.list(thread_id=self._thread_id)
        assistant_messages = []
        for message in messages.data:
            if message.role == "assistant":
                assistant_messages.append(message)
            else:
                break

        # Delete all assistant messages except the first one
        first_assistant_message = assistant_messages.pop()
        while assistant_messages:
            message = assistant_messages.pop()
            print(f"Deleting Assistant message: {message}")
            client.beta.threads.messages.delete(
                message_id=message.id,
                thread_id=self._thread_id,
            )
        response_message = first_assistant_message.content[0].text.value
        print(f"Generated message: {response_message}")
        return response_message

    def _maybe_delete_thread(self):
        tid, self._thread_id = self._thread_id, None
        if tid:
            try:
                response = client.beta.threads.delete(tid)
                print('Deleted thread', response)
            except Exception as e:
                print('Failed to delete thread', tid, e)

    # create a thread
    def _create_thread(self):
        thread = client.beta.threads.create()
        print("Created thread:", thread.id)
        self._thread_id = thread.id

    def _close(self):
        print("Closing...")
        self._maybe_delete_thread()
