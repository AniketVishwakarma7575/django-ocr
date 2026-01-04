# ocr/services/ocr_service.py

import easyocr
import cv2
import numpy as np
import logging
import os
from django.conf import settings

logger = logging.getLogger('ocr')

# Initialize EasyOCR reader (global to avoid reloading)
reader = easyocr.Reader(['en'], gpu=False)


class OCRService:
    """Service class for OCR operations"""
    
    @staticmethod
    def validate_image(image_path):
        """Validate if image exists and is readable"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        return True
    
    @staticmethod
    def preprocess_image(image_path):
        """Preprocess image for better OCR results"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Improve contrast
        img = cv2.equalizeHist(img)
        
        # Remove noise
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Apply threshold
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return img
    
    @staticmethod
    def process_image(image_path):
        """Extract text from image using EasyOCR"""
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Validate image first
            OCRService.validate_image(image_path)
            
            # Preprocess image
            img = OCRService.preprocess_image(image_path)
            
            # Extract text
            results = reader.readtext(img, detail=0)
            
            # Join results
            text = "\n".join(results)
            
            if not text.strip():
                logger.warning("No text extracted from image")
                return "No text found in image"
            
            logger.info(f"Extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise


class TextCleaner:
    """Utility class for cleaning extracted text"""
    
    @staticmethod
    def clean(text):
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove multiple newlines
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
        
        return text.strip()


# Legacy function for backward compatibility
def extract_text(image_path):
    """
    Legacy function - Extract text from image
    Uses OCRService internally
    """
    return OCRService.process_image(image_path)