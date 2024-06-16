import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from agent_controller import AgentController
from utils import working_dir, screenshot_file

app = Flask(__name__)
UPLOAD_FOLDER = working_dir()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CORS(app)  # This will enable CORS for all routes

agent_controller = AgentController()


@app.route('/instructions', methods=['POST'])
def upload_screenshot():
    prompt = request.form.get("prompt")
    if not prompt.strip():
        return jsonify({'error': 'No prompt provided'}), 400
    if 'screenshot' not in request.files:
        ins = agent_controller.next_instruction(None, prompt)
        return jsonify({'instructions': [ins]}), 200

    file = request.files['screenshot']
    if not file or file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, screenshot_file())
    file.save(filepath)
    ins = agent_controller.next_instruction(filepath, prompt)
    return jsonify({'message': 'File successfully uploaded', 'name': file.filename,
                    'instructions': [ins]}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7878, debug=True, use_reloader=False)
