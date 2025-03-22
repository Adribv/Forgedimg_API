from flask import Flask, request, jsonify
from forgery_detector import DocumentForgeryDetector

app = Flask(__name__)
detector = DocumentForgeryDetector()

@app.route('/detect', methods=['POST'])
def detect_forgery():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    result = detector.analyze_document(file_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
