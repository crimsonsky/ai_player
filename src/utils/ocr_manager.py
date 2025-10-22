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
        
        # Check if a specific OCR engine is requested in config
        preferred_engine = config.get('ocr_engine')
        if preferred_engine == 'tesseract':
            # Force tesseract usage
            try:
                result = subprocess.run(['which', 'tesseract'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.ocr_method = "tesseract"
                    print("✅ Using tesseract OCR engine (forced by config)")
                else:
                    raise Exception("Tesseract not found")
            except:
                print("❌ Tesseract forced but not available, falling back to auto-detection")
                self.ocr_method = self._detect_best_ocr_method()
        else:
            self.ocr_method = self._detect_best_ocr_method()
        
    def audio_signal(self, message: str):
        """Provide audio feedback."""
        if self.audio_enabled:
            try:
                os.system(f'say "{message}"')
            except:
                print(f"🔊 Audio: {message}")
    
    def _detect_best_ocr_method(self) -> str:
        """
        Detect the best available OCR method.
        
        LEVEL-5 ARCHITECTURAL CORRECTION: Prioritize Apple Vision Framework
        """
        
        # Method 1: Apple Vision Framework (LEVEL-5 MANDATE)
        try:
            # Test if Apple Vision Framework is available via PyObjC
            import Vision
            import Foundation
            import Quartz
            print("✅ Apple Vision Framework available (Level-5 mandate)")
            return "apple_vision"
        except ImportError:
            print("⚠️ Apple Vision Framework not available - falling back")
        except Exception as e:
            print(f"⚠️ Vision Framework test error: {e}")
        
        # Method 2: Try ocrmac (Legacy Apple Vision)
        try:
            result = subprocess.run(['which', 'ocrmac'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ocrmac (Legacy Apple Vision) available")
                return "ocrmac"
        except:
            pass
        
        # Method 3: Check for Tesseract (DECOMMISSIONED per Level-5)
        try:
            result = subprocess.run(['which', 'tesseract'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("⚠️ Tesseract available but DECOMMISSIONED per Level-5 correction")
                print("   Using as emergency fallback only")
                return "tesseract"
        except:
            pass
        
        print("❌ CRITICAL: No OCR engines found - cannot proceed")
        raise RuntimeError("NO_OCR_ENGINES: Apple Vision Framework required for Level-5 architecture. Install PyObjC and Vision framework.")
    
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
        
        if self.ocr_method == "apple_vision":
            return self._extract_with_apple_vision(image_path, roi)
        elif self.ocr_method == "ocrmac":
            return self._extract_with_ocrmac(image_path, roi)
        elif self.ocr_method == "shortcuts":
            return self._extract_with_shortcuts(image_path, roi)
        elif self.ocr_method == "tesseract":
            return self._extract_with_tesseract(image_path, roi)
        else:
            raise RuntimeError(f"UNKNOWN_OCR_METHOD: '{self.ocr_method}' is not supported. Use 'apple_vision', 'ocrmac', 'shortcuts', or 'tesseract'.")
    
    def extract_text_from_screenshot(self, screenshot_array, 
                                   roi: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        """
        Extract text from screenshot numpy array.
        
        Args:
            screenshot_array: numpy array from screen capture
            roi: Optional region of interest (normalized coordinates)
            
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        try:
            import tempfile
            import cv2
            
            # Save screenshot array to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Convert BGR to RGB if needed and save
            if len(screenshot_array.shape) == 3 and screenshot_array.shape[2] == 3:
                # Assume BGR format from OpenCV, convert to RGB for saving
                rgb_array = cv2.cvtColor(screenshot_array, cv2.COLOR_BGR2RGB)
                cv2.imwrite(temp_path, cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR))
            else:
                cv2.imwrite(temp_path, screenshot_array)
            
            # Use Apple Vision Framework directly on screenshot array if available
            if self.ocr_method == "apple_vision":
                try:
                    from .apple_vision_ocr import create_apple_vision_ocr
                    
                    vision_ocr = create_apple_vision_ocr(self.config)
                    result = vision_ocr.extract_text_from_screenshot(screenshot_array, roi)
                    
                    # Clean up temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
                    return result
                    
                except Exception as e:
                    print(f"⚠️ Direct Vision Framework extraction failed: {e}")
                    # Fall back to file-based extraction
            
            # Extract text using existing method (file-based)
            ocr_results = self.extract_text_from_image(temp_path, roi)
            
            # Clean up temporary file
            import os
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Convert OCRResult list to simple dict format
            if ocr_results and len(ocr_results) > 0:
                combined_text = ' '.join([result.text for result in ocr_results if result.text])
                return {
                    'success': True,
                    'text': combined_text,
                    'results': ocr_results
                }
            else:
                return {
                    'success': False,
                    'text': '',
                    'error': 'No text detected'
                }
                
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'error': str(e)
            }
    
    def _extract_with_apple_vision(self, image_path: str, 
                                 roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """
        Extract text using Apple Vision Framework.
        
        LEVEL-5 ARCHITECTURAL CORRECTION: Primary OCR method for Signal Fusion Engine.
        """
        try:
            print("🔍 Using Apple Vision Framework for text extraction...")
            
            # Import and initialize Apple Vision OCR
            from .apple_vision_ocr import create_apple_vision_ocr
            
            vision_ocr = create_apple_vision_ocr(self.config)
            
            # Extract text using Vision Framework
            result = vision_ocr.extract_text_from_image_path(image_path, roi)
            
            if result['success']:
                # Convert Apple Vision results to OCRResult format
                ocr_results = []
                
                for vision_result in result['results']:
                    ocr_result = OCRResult(
                        text=vision_result.text,
                        confidence=vision_result.confidence,
                        normalized_bbox=vision_result.normalized_bbox
                    )
                    ocr_results.append(ocr_result)
                
                print(f"   📝 Apple Vision extracted {len(ocr_results)} text regions")
                return ocr_results
                
            else:
                print(f"   ❌ Apple Vision extraction failed: {result['error']}")
                raise RuntimeError(f"APPLE_VISION_OCR_FAILED: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ Apple Vision Framework error: {e}")
            raise RuntimeError(f"APPLE_VISION_OCR_FAILED: Apple Vision Framework text extraction failed: {e}")
    
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
            raise RuntimeError(f"OCRMAC_FAILED: ocrmac text extraction failed: {e}")
    
    def _extract_with_shortcuts(self, image_path: str,
                              roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """Extract text using macOS Shortcuts."""
        
        try:
            print("🔍 Using macOS Shortcuts for text extraction...")
            
            # This method is not implemented yet
            raise RuntimeError("SHORTCUTS_OCR_NOT_IMPLEMENTED: macOS Shortcuts OCR is not yet implemented")
            
        except Exception as e:
            print(f"❌ Shortcuts OCR error: {e}")
            raise RuntimeError(f"SHORTCUTS_OCR_FAILED: macOS Shortcuts OCR failed: {e}")
    
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
            raise RuntimeError(f"TESSERACT_OCR_FAILED: Tesseract text extraction failed: {e}")
    
    def _extract_with_fallback(self, image_path: str,
                             roi: Optional[Tuple[float, float, float, float]] = None) -> List[OCRResult]:
        """REMOVED: No fallback data - throw error when real OCR fails."""
        
        print("❌ OCR FAILURE: Real text extraction failed")
        print("❌ NO FALLBACK DATA: System cannot generate fake coordinates")
        print("❌ CRITICAL ERROR: Cannot detect interface elements without working OCR")
        
        raise RuntimeError(
            "OCR_EXTRACTION_FAILED: All OCR methods failed to extract text. "
            "Cannot proceed without real text detection. "
            "Check OCR dependencies (tesseract, ocrmac, etc.) or screenshot quality."
        )
    
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