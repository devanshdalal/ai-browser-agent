import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from chat_controller import ChatController
from agent_controller import AgentController
from assistant import WebpageNavigatorAssistant
from utils import working_dir, screenshot_file

app = Flask(__name__)
UPLOAD_FOLDER = working_dir()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CORS(app)  # This will enable CORS for all routes

# agent_controller = AgentController()
# assistant = WebpageNavigatorAssistant()
chat_controller = ChatController()


@app.route('/instructions', methods=['POST'])
def upload_screenshot():
    prompt = request.form.get("prompt")
    is_prompt_empty = (prompt is None) or (not prompt.strip())
    is_screenshot_empty = 'screenshot' not in request.files
    if is_prompt_empty and is_screenshot_empty:
        return jsonify({'error': 'Both prompt and webpage screenshot cannot be skipped'}), 400
    if is_screenshot_empty:
        ins = chat_controller.next_instruction(None, prompt)
        return jsonify({'instructions': [ins]}), 200

    file = request.files['screenshot']
    if not file or file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, screenshot_file())
    file.save(filepath)
    ins = chat_controller.next_instruction(filepath, prompt)
    return jsonify({'message': 'File successfully uploaded', 'name': file.filename,
                    'instructions': [ins]}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7878, debug=True, use_reloader=False)
