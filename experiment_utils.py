from assistant import WebpageNavigatorAssistant
from chat_controller import ChatController

json = """
```json
{
  "action": "answer",
  "reply": "One of the Vivo phones listed on smartprix.com is the Vivo V31 Pro 5G."
}
```
"""

controller = ChatController()

response = controller.next_instruction(None,
                            "Using google, tell me the minimum price of Irfc in the past 6 months?")

print('response', response)
