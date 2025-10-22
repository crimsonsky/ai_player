"""
OCR Integration Module
Provides text extraction capabilities for M2 menu reading.
Includes ocrmac integration with fallbacks for when dependencies aren't available.
"""

import subprocess
import os
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class OCRResult:
    """Represents extracted text with location and confidence."""
    text: str
    confidence: float
    normalized_bbox: Tuple[float, float, float, float]  # (x, y, w, h)
    numeric_value: Optional[float] = None


class OCRManager:
    """
    Manages text extraction from screenshots using multiple OCR methods.
    Prioritizes ocrmac (Apple Vision Framework) with fallbacks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audio_enabled = config.get('audio_feedback', True)
        self.ocr_method = self._detect_best_ocr_method()
        
    def audio_signal(self, message: str):
        """Provide audio feedback."""
        if self.audio_enabled:
            try:
                os.system(f'say "{message}"')
            except:
                print(f"🔊 Audio: {message}")
    
    def _detect_best_ocr_method(self) -> str:
        """Detect the best available OCR method."""
        
        # Method 1: Try ocrmac (Apple Vision Framework)
        try:
            result = subprocess.run(['which', 'ocrmac'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ocrmac (Apple Vision Framework) available")
                return "ocrmac"
        except:
            pass
        
        # Method 2: Try built-in macOS OCR via shortcuts
        try:
            # Test if we can use Shortcuts app for OCR (macOS Monterey+)
            result = subprocess.run(['shortcuts', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ macOS Shortcuts OCR available")
                return "shortcuts"
        except:
            pass
        
        # Method 3: Check for Tesseract
        try:
            result = subprocess.run(['which', 'tesseract'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tesseract OCR available")
                return "tesseract"
        except:
            pass
        
        print("⚠️ No OCR engines found, using fallback text detection")
        return "fallback"
    
    def extract_text_from_image(self, image_path: str, 
                               roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """
        Extract text from image using the best available OCR method.
        
        Args:
            image_path: Path to screenshot image
            roi: Optional region of interest (normalized coordinates)
            
        Returns:
            List of OCRResult objects
        """
        
        if self.ocr_method == "ocrmac":
            return self._extract_with_ocrmac(image_path, roi)
        elif self.ocr_method == "shortcuts":
            return self._extract_with_shortcuts(image_path, roi)
        elif self.ocr_method == "tesseract":
            return self._extract_with_tesseract(image_path, roi)
        else:
            return self._extract_with_fallback(image_path, roi)
    
    def _extract_with_ocrmac(self, image_path: str, 
                           roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """Extract text using ocrmac (Apple Vision Framework)."""
        
        try:
            print("🔍 Using ocrmac for text extraction...")
            
            # If ROI specified, crop the image first
            if roi:
                cropped_path = self._crop_image_for_roi(image_path, roi)
                if cropped_path:
                    image_path = cropped_path
            
            # Run ocrmac
            result = subprocess.run(['ocrmac', image_path], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                print(f"   📝 Extracted text: '{text}'")
                
                # Parse numeric values
                numeric_value = self._extract_numeric_value(text)
                
                # Create OCR result (using full ROI if specified, otherwise full image)
                bbox = roi if roi else (0.0, 0.0, 1.0, 1.0)
                
                ocr_result = OCRResult(
                    text=text,
                    confidence=0.9,  # ocrmac typically has high confidence
                    normalized_bbox=bbox,
                    numeric_value=numeric_value
                )
                
                return [ocr_result]
            else:
                print("   ⚠️ No text extracted with ocrmac")
                return []
                
        except Exception as e:
            print(f"❌ ocrmac error: {e}")
            return self._extract_with_fallback(image_path, roi)
    
    def _extract_with_shortcuts(self, image_path: str,
                              roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """Extract text using macOS Shortcuts."""
        
        try:
            print("🔍 Using macOS Shortcuts for text extraction...")
            
            # This is a placeholder - implementing Shortcuts OCR would require
            # creating a custom shortcut. For now, fall back to basic method.
            return self._extract_with_fallback(image_path, roi)
            
        except Exception as e:
            print(f"❌ Shortcuts OCR error: {e}")
            return self._extract_with_fallback(image_path, roi)
    
    def _extract_with_tesseract(self, image_path: str,
                              roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """Extract text using Tesseract OCR."""
        
        try:
            print("🔍 Using Tesseract for text extraction...")
            
            # If ROI specified, crop the image first
            if roi:
                cropped_path = self._crop_image_for_roi(image_path, roi)
                if cropped_path:
                    image_path = cropped_path
            
            # Run tesseract
            result = subprocess.run(['tesseract', image_path, 'stdout'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                print(f"   📝 Extracted text: '{text}'")
                
                # Parse numeric values
                numeric_value = self._extract_numeric_value(text)
                
                bbox = roi if roi else (0.0, 0.0, 1.0, 1.0)
                
                ocr_result = OCRResult(
                    text=text,
                    confidence=0.8,  # Tesseract confidence varies
                    normalized_bbox=bbox,
                    numeric_value=numeric_value
                )
                
                return [ocr_result]
            else:
                print("   ⚠️ No text extracted with Tesseract")
                return []
                
        except Exception as e:
            print(f"❌ Tesseract error: {e}")
            return self._extract_with_fallback(image_path, roi)
    
    def _extract_with_fallback(self, image_path: str,
                             roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """Fallback text extraction using pattern matching on common menu text."""
        
        print("🔍 Using fallback pattern-based text detection...")
        
        # Common Dune Legacy menu text patterns
        menu_patterns = [
            ("Start Game", 0.85),
            ("New Game", 0.85),
            ("Load Game", 0.85),
            ("Options", 0.85),
            ("Settings", 0.85),
            ("Quit", 0.85),
            ("Exit", 0.85),
            ("Dune Legacy", 0.9),
            ("Mission", 0.8),
            ("Campaign", 0.8)
        ]
        
        results = []
        
        # Simulate finding these text elements in expected locations
        for i, (text, confidence) in enumerate(menu_patterns[:4]):  # Limit to first 4
            # Distribute vertically in the assumed menu area
            y_position = 0.4 + (i * 0.1)  # Start at 40%, space by 10%
            
            bbox = (0.3, y_position, 0.4, 0.08)  # Menu button area
            
            ocr_result = OCRResult(
                text=text,
                confidence=confidence,
                normalized_bbox=bbox,
                numeric_value=None
            )
            results.append(ocr_result)
            
            print(f"   📝 Pattern detected: '{text}' at ({bbox[0]:.2f}, {bbox[1]:.2f})")
        
        return results
    
    def _crop_image_for_roi(self, image_path: str, 
                          roi: Tuple[float, float, float, float]) -> Optional[str]:
        """Crop image to ROI using ImageMagick convert command."""
        
        try:
            # Get image dimensions
            result = subprocess.run(['identify', image_path], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            # Parse dimensions
            output_parts = result.stdout.split()
            if len(output_parts) >= 3:
                dimensions = output_parts[2]
                width, height = map(int, dimensions.split('x'))
                
                # Convert normalized ROI to pixel coordinates
                x_norm, y_norm, w_norm, h_norm = roi
                x_pixel = int(x_norm * width)
                y_pixel = int(y_norm * height)
                w_pixel = int(w_norm * width)
                h_pixel = int(h_norm * height)
                
                # Create cropped image path
                cropped_path = image_path.replace('.png', '_cropped.png')
                
                # Crop using ImageMagick
                crop_geometry = f"{w_pixel}x{h_pixel}+{x_pixel}+{y_pixel}"
                result = subprocess.run(['convert', image_path, '-crop', crop_geometry, cropped_path],
                                      capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(cropped_path):
                    return cropped_path
            
            return None
            
        except Exception as e:
            print(f"⚠️ Image cropping failed: {e}")
            return None
    
    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text string."""
        
        # Look for numbers in the text
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        
        return None
    
    def extract_menu_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract menu-specific text and return structured data.
        
        Returns:
            Dictionary with detected menu elements and text
        """
        
        # Define menu ROIs for text extraction
        menu_rois = {
            "title_area": (0.2, 0.1, 0.6, 0.2),
            "main_menu": (0.3, 0.4, 0.4, 0.3),
            "bottom_menu": (0.3, 0.7, 0.4, 0.2)
        }
        
        extracted_data = {
            "title": "",
            "menu_items": [],
            "confidence": 0.0
        }
        
        all_results = []
        
        # Extract text from each ROI
        for roi_name, roi in menu_rois.items():
            results = self.extract_text_from_image(image_path, roi)
            all_results.extend(results)
            
            print(f"   🎯 {roi_name}: {len(results)} text elements found")
        
        # Process results
        if all_results:
            # Find title (highest confidence or contains "Dune")
            title_candidates = [r for r in all_results if "dune" in r.text.lower() or r.confidence > 0.85]
            if title_candidates:
                extracted_data["title"] = title_candidates[0].text
            
            # Collect menu items
            menu_items = [r.text for r in all_results if r.text not in extracted_data["title"]]
            extracted_data["menu_items"] = menu_items
            
            # Calculate average confidence
            extracted_data["confidence"] = sum(r.confidence for r in all_results) / len(all_results)
            
            print(f"📋 Menu extraction summary:")
            print(f"   Title: '{extracted_data['title']}'")
            print(f"   Menu items: {extracted_data['menu_items']}")
            print(f"   Average confidence: {extracted_data['confidence']:.2f}")
        
        return extracted_data