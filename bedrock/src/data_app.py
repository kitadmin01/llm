from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/path/to/upload'
ALLOWED_EXTENSIONS = {'gif', 'jpeg', 'xml', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        return jsonify({'message': 'File successfully uploaded'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
