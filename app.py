import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import tempfile
import logging
import gc
from flask import Flask, request, jsonify
import uuid
import werkzeug.utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class DocumentForgeryDetector:
    def __init__(self):
        logger.info("Initializing Document Forgery Detector")
        self.temp_dir = tempfile.mkdtemp()
        self._configure_tesseract()

    def _configure_tesseract(self):
        # Simplified Tesseract configuration for cloud deployment
        # On Render, we'll install Tesseract via apt-get in a build script
        if os.environ.get('TESSDATA_PREFIX'):
            logger.info(f"Using TESSDATA_PREFIX from environment: {os.environ.get('TESSDATA_PREFIX')}")
        else:
            logger.info("No TESSDATA_PREFIX found in environment")
        
        # Limit OpenMP threads to prevent memory issues
        os.environ["OMP_THREAD_LIMIT"] = "1"

    def analyze_document(self, file_path):
        results = {'is_forged': False, 'confidence': 0.0, 'analysis_details': {}}
        if not os.path.exists(file_path):
            return {'error': 'File does not exist'}
        results = self._analyze_image(file_path)
        gc.collect()  # Free up memory after processing
        return results

    def _analyze_image(self, image_path):
        results = {'is_forged': False, 'confidence': 0.0, 'analysis_details': {}}
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return {"error": "Invalid image file"}
            
            text_analysis = self._analyze_text(image)
            noise_analysis = self._analyze_noise(image)
            edge_analysis = self._analyze_edges(image)
            
            results['analysis_details']['text_analysis'] = text_analysis
            results['analysis_details']['noise_analysis'] = noise_analysis
            results['analysis_details']['edge_analysis'] = edge_analysis
            
            # Adjust confidence threshold for better accuracy
            if text_analysis.get('confidence', 0) < 50 or noise_analysis.get('is_suspicious', False) or edge_analysis.get('is_suspicious', False):
                results['is_forged'] = True
                results['confidence'] = max(results.get('confidence', 0), 0.85)
            else:
                results['confidence'] = min(results.get('confidence', 0) + text_analysis.get('confidence', 0) / 100, 0.95)
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            results['error'] = str(e)
        return results

    def _analyze_text(self, image):
        try:
            text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in text_data['conf'] if isinstance(conf, (int, str)) and str(conf).isdigit()]
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
            return {'confidence': confidence}
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return {'error': str(e), 'confidence': 0.0}

    def _analyze_noise(self, image):
        try:
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            is_suspicious = laplacian_var < 50  # Lower variance may indicate tampering
            return {'laplacian_variance': laplacian_var, 'is_suspicious': is_suspicious}
        except Exception as e:
            logger.error(f"Error in noise analysis: {e}")
            return {'error': str(e), 'is_suspicious': False}

    def _analyze_edges(self, image):
        try:
            edges = cv2.Canny(image, 100, 200)
            edge_count = np.sum(edges > 0)
            is_suspicious = edge_count < 10000  # Too few edges might indicate smoothing/tampering
            return {'edge_count': edge_count, 'is_suspicious': is_suspicious}
        except Exception as e:
            logger.error(f"Error in edge analysis: {e}")
            return {'error': str(e), 'is_suspicious': False}


# Initialize detector
detector = DocumentForgeryDetector()

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Document Forgery Detector</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                form { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                input[type="submit"] { background: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
                input[type="submit"]:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <h1>Document Forgery Detector</h1>
            <p>Upload a document image to check for potential forgery.</p>
            <form method="post" action="/analyze" enctype="multipart/form-data">
                <input type="file" name="document" required>
                <br><br>
                <input type="submit" value="Analyze Document">
            </form>
        </body>
    </html>
    """

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'document' not in request.files:
        return jsonify({'error': 'No document part in the request'}), 400
    
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    # Save file with secure filename
    filename = werkzeug.utils.secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    try:
        # Analyze the document
        results = detector.analyze_document(file_path)
        
        # Clean up the file after analysis
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)