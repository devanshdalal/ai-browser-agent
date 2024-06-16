from utils import extract_json1, extract_json

json = """
```json
{
  "action": "answer",
  "reply": "One of the Vivo phones listed on smartprix.com is the Vivo V31 Pro 5G."
}
```
"""

print(extract_json(json))