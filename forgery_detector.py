import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import tempfile
import logging
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentForgeryDetector:
    def __init__(self):
        logger.info("Initializing Document Forgery Detector")
        self.temp_dir = tempfile.mkdtemp()
        self._configure_tesseract()

    def _configure_tesseract(self):
        tesseract_paths = ["/usr/bin/tesseract"]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata/"
                logger.info(f"Found Tesseract at: {path}")
                logger.info(f"Set TESSDATA_PREFIX to: {os.environ['TESSDATA_PREFIX']}")
                break




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
            if text_analysis['confidence'] < 50 or noise_analysis['is_suspicious'] or edge_analysis['is_suspicious']:
                results['is_forged'] = True
                results['confidence'] = max(results['confidence'], 0.85)
            else:
                results['confidence'] = min(results['confidence'] + text_analysis['confidence'] / 100, 0.95)
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            results['error'] = str(e)
        return results

    def _analyze_text(self, image):
        try:
            text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in text_data['conf'] if isinstance(conf, (int, str)) and str(conf).isdigit()]
            confidence = int(sum(confidences) / len(confidences)) if confidences else 0  # Convert to Python int
            return {'confidence': confidence}
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return {'error': str(e)}




    def _analyze_noise(self, image):
        try:
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            is_suspicious = laplacian_var < 50  # Lower variance may indicate tampering
            return {'laplacian_variance': laplacian_var, 'is_suspicious': is_suspicious}
        except Exception as e:
            logger.error(f"Error in noise analysis: {e}")
            return {'error': str(e)}

    def _analyze_edges(self, image):
        try:
            edges = cv2.Canny(image, 100, 200)
            edge_count = np.sum(edges > 0)
            is_suspicious = edge_count < 10000  # Too few edges might indicate smoothing/tampering
            return {'edge_count': edge_count, 'is_suspicious': is_suspicious}
        except Exception as e:
            logger.error(f"Error in edge analysis: {e}")
            return {'error': str(e)}
