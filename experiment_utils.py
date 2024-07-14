from assistant import WebpageNavigatorAssistant

json = """
```json
{
  "action": "answer",
  "reply": "One of the Vivo phones listed on smartprix.com is the Vivo V31 Pro 5G."
}
```
"""

controller = WebpageNavigatorAssistant()

controller.next_instruction(None,
                            "What are some of the Vivo phones listed on smartprix.com?")
