import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing of prescription images"""

    def __init__(self):
        # Configure tesseract path if needed (for Windows)
        if os.name == 'nt':
            # Common installation paths for tesseract on Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\*\AppData\Local\Tesseract-OCR\tesseract.exe'
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert PIL to OpenCV format
            if isinstance(image, Image.Image):
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Morphological operations to clean up the image
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            return cleaned
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image

    def extract_text(self, image_path):
        """Extract text from image file"""
        try:
            # Load image
            if image_path.lower().endswith('.pdf'):
                return self._extract_from_pdf(image_path)
            else:
                return self._extract_from_image(image_path)

        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {str(e)}")
            return ""

    def _extract_from_image(self, image_path):
        """Extract text from single image"""
        try:
            # Load image with PIL
            image = Image.open(image_path)

            # Preprocess image
            processed_image = self.preprocess_image(image)

            # Extract text using pytesseract
            text = pytesseract.image_to_string(processed_image)

            return text.strip()

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return ""

    def _extract_from_pdf(self, pdf_path):
        """Extract text from PDF by converting to images"""
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)

            all_text = ""
            for i, image in enumerate(images):
                # Preprocess each page
                processed_image = self.preprocess_image(image)

                # Extract text from each page
                text = pytesseract.image_to_string(processed_image)
                all_text += f"\n--- Page {i+1} ---\n{text}"

            return all_text.strip()

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return ""

    def save_uploaded_file(self, file, upload_folder='uploads'):
        """Save uploaded file and return the path"""
        try:
            # Create upload folder if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Generate unique filename
            filename = f"prescription_{int(time.time())}_{file.filename}"
            file_path = os.path.join(upload_folder, filename)

            # Save file
            file.save(file_path)

            return file_path

        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return None

# Utility function to get OCR processor instance
def get_ocr_processor():
    """Get OCR processor instance"""
    return OCRProcessor()
