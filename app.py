from flask import Flask, request, send_file, jsonify
import requests
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'MeshAnything API is running.'

@app.route('/process', methods=['POST'])
def process_mesh():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.obj'):
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        # Send the file to the existing MeshAnything service
        with open(input_path, 'rb') as f:
            files = {'file': (file.filename, f)}
            response = requests.post('https://f7f598e3bf7b1e54c2.gradio.live/process', files=files)
        
        if response.status_code == 200:
            output_path = os.path.join(UPLOAD_FOLDER, 'reconstructed_' + file.filename)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Failed to process file'}), 500

    return jsonify({'error': 'Invalid file format. Only .obj files are allowed.'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
