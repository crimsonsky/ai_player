"""
Apple Vision Framework OCR Integration - Level-5 Architectural Correction
Module 2D: Text Extraction via Native macOS Vision Framework

MANDATE: Replace pytesseract/ocrmac with Apple Vision Framework for 
graphics-rendered game text extraction capability.

COMPLIANCE: Level-5 Architectural Correction for Signal Fusion Engine
"""

try:
    import Foundation
    import Vision
    import Quartz
    import AppKit
    APPLE_VISION_AVAILABLE = True
except ImportError:
    APPLE_VISION_AVAILABLE = False

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass
import tempfile
import os


@dataclass
class VisionOCRResult:
    """Apple Vision Framework OCR result."""
    text: str
    confidence: float
    normalized_bbox: Tuple[float, float, float, float]  # (x, y, width, height)
    character_boxes: Optional[List[Tuple[str, float, float, float, float]]] = None


class AppleVisionOCR:
    """Apple Vision Framework OCR engine - Level-5 Architecture."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Apple Vision OCR engine."""
        if not APPLE_VISION_AVAILABLE:
            raise ImportError("Apple Vision Framework not available")
        
        self.config = config
        self.audio_feedback = config.get('audio_feedback', False)
    """
    Apple Vision Framework OCR Engine - Level-5 Architecture
    
    REPLACES: pytesseract, ocrmac dependencies  
    PROVIDES: Native macOS OCR optimized for graphics-rendered text
    ENABLES: Signal Fusion Engine S2 (OCR Signal) functionality
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audio_enabled = config.get('audio_feedback', True)
        
        # Apple Vision Framework configuration - use constants by integer values
        self.recognition_level = 1  # VNRequestTextRecognitionLevelAccurate
        self.revision = 1  # VNRecognizeTextRequestRevision1
        self.use_language_correction = False  # Better for UI elements
        self.minimum_text_height = 0.03  # Adjust for game interface text size
        
        # Initialize Vision Framework request
        self._initialize_vision_request()
        
        self.audio_signal("Apple Vision Framework OCR initialized")
        
    def audio_signal(self, message: str):
        """Audio feedback for operations."""
        if self.audio_enabled:
            try:
                os.system(f'say "{message}" --rate=180')
            except:
                print(f"🔊 {message}")
        else:
            print(f"👁️ Vision OCR: {message}")
    
    def _initialize_vision_request(self):
        """Initialize Apple Vision Framework text recognition request."""
        try:
            # Create text recognition request with optimal settings for game interfaces
            self.text_request = Vision.VNRecognizeTextRequest.alloc().init()
            
            # Configure for maximum accuracy with game graphics
            self.text_request.setRecognitionLevel_(self.recognition_level)
            self.text_request.setRevision_(self.revision)
            self.text_request.setUsesLanguageCorrection_(self.use_language_correction)
            self.text_request.setMinimumTextHeight_(self.minimum_text_height)
            
            # Enable automatic language detection
            self.text_request.setRecognitionLanguages_(["en-US"])
            
            print("✅ Apple Vision Framework request configured for game interface OCR")
            
        except Exception as e:
            print(f"❌ Vision Framework initialization error: {e}")
            raise RuntimeError(f"VISION_FRAMEWORK_INIT_FAILED: {e}")
    
    def extract_text_from_screenshot(self, screenshot_array: np.ndarray, 
                                   roi: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        """
        Extract text from screenshot using Apple Vision Framework.
        
        Args:
            screenshot_array: numpy array from screen capture (BGR format)
            roi: Optional region of interest (normalized coordinates)
            
        Returns:
            Dict with 'success', 'results', 'text', 'confidence' keys
        """
        try:
            self.audio_signal("Analyzing game interface text")
            
            # Convert screenshot to temporary file for Vision Framework
            temp_image_path = self._prepare_image_for_vision(screenshot_array, roi)
            if temp_image_path is None:
                return {
                    'success': False,
                    'error': 'Image preparation failed',
                    'results': [],
                    'text': '',
                    'confidence': 0.0
                }
            
            try:
                # Create Vision image request handler from file URL
                image_url = Foundation.NSURL.fileURLWithPath_(temp_image_path)
                request_handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(
                    image_url, Foundation.NSDictionary.dictionary()
                )
                
                # Perform text recognition
                error = Foundation.NSError.alloc().init()
                success = request_handler.performRequests_error_([self.text_request], error)
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_image_path)
                except:
                    pass
            
            if not success:
                error_msg = str(error.localizedDescription()) if error else "Unknown Vision Framework error"
                return {
                    'success': False,
                    'error': f'Vision Framework recognition failed: {error_msg}',
                    'results': [],
                    'text': '',
                    'confidence': 0.0
                }
            
            # Process recognition results
            vision_results = self._process_vision_results(self.text_request.results())
            
            # Compile final result
            combined_text = ' '.join([result.text for result in vision_results])
            avg_confidence = sum([result.confidence for result in vision_results]) / len(vision_results) if vision_results else 0.0
            
            self.audio_signal(f"Detected {len(vision_results)} text regions")
            
            return {
                'success': True,
                'results': vision_results,
                'text': combined_text,
                'confidence': avg_confidence,
                'method': 'apple_vision_framework'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'text': '',
                'confidence': 0.0
            }
    
    def _prepare_image_for_vision(self, screenshot_array: np.ndarray, 
                                roi: Optional[Tuple[float, float, float, float]] = None) -> Optional[str]:
        """
        Convert numpy screenshot array to temporary file for Vision Framework.
        
        Args:
            screenshot_array: BGR numpy array from OpenCV
            roi: Optional region of interest for cropping
            
        Returns:
            Path to temporary image file suitable for Vision Framework processing
        """
        try:
            import cv2
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(screenshot_array, cv2.COLOR_BGR2RGB)
            
            # Apply ROI if specified
            if roi:
                x, y, w, h = roi
                height, width = rgb_image.shape[:2]
                
                # Convert normalized coordinates to pixels
                x1 = int(x * width)
                y1 = int(y * height)
                x2 = int((x + w) * width)
                y2 = int((y + h) * height)
                
                # Ensure bounds are valid
                x1 = max(0, min(x1, width))
                y1 = max(0, min(y1, height))
                x2 = max(x1, min(x2, width))
                y2 = max(y1, min(y2, height))
                
                rgb_image = rgb_image[y1:y2, x1:x2]
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name
                
            # Convert back to BGR for OpenCV saving
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(temp_path, bgr_image)
            
            return temp_path
            
        except Exception as e:
            if self.audio_feedback:
                print(f"Image preparation error: {e}")
            return None
    
    def _process_vision_results(self, vision_observations) -> List[VisionOCRResult]:
        """
        Process Apple Vision Framework recognition results.
        
        Args:
            vision_observations: VNRecognizedTextObservation array from Vision Framework
            
        Returns:
            List of VisionOCRResult objects
        """
        results = []
        
        try:
            for observation in vision_observations:
                # Get top candidate for each text observation
                candidates = observation.topCandidates_(1)
                
                if len(candidates) > 0:
                    candidate = candidates[0]
                    text = str(candidate.string())
                    confidence = float(candidate.confidence())
                    
                    # Get bounding box (normalized coordinates)
                    bbox = observation.boundingBox()
                    
                    # Vision Framework uses bottom-left origin, convert to top-left
                    normalized_bbox = (
                        float(bbox.origin.x),  # x
                        1.0 - float(bbox.origin.y) - float(bbox.size.height),  # y (flipped)
                        float(bbox.size.width),  # width
                        float(bbox.size.height)  # height
                    )
                    
                    # Create result object
                    result = VisionOCRResult(
                        text=text,
                        confidence=confidence,
                        normalized_bbox=normalized_bbox
                    )
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Vision results processing error: {e}")
            return []
    
    def extract_text_from_image_path(self, image_path: str,
                                   roi: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        """
        Extract text from image file using Apple Vision Framework.
        
        Args:
            image_path: Path to image file
            roi: Optional region of interest
            
        Returns:
            Dict with OCR results
        """
        try:
            import cv2
            
            # Load image as numpy array
            screenshot_array = cv2.imread(image_path)
            if screenshot_array is None:
                return {
                    'success': False,
                    'error': f'Could not load image: {image_path}',
                    'results': [],
                    'text': '',
                    'confidence': 0.0
                }
            
            # Use screenshot extraction method
            return self.extract_text_from_screenshot(screenshot_array, roi)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'text': '',
                'confidence': 0.0
            }
    
    def get_available_languages(self) -> List[str]:
        """Get list of supported recognition languages."""
        try:
            supported_languages = Vision.VNRecognizeTextRequest.supportedRecognitionLanguagesForTextRecognitionLevel_revision_error_(
                self.recognition_level, self.revision, None
            )
            return [str(lang) for lang in supported_languages[0]] if supported_languages[0] else ["en-US"]
        except:
            return ["en-US"]
    
    def configure_for_game_text(self):
        """Configure Vision Framework specifically for game interface text."""
        try:
            # Optimize for game graphics text
            self.text_request.setMinimumTextHeight_(0.01)  # Smaller text detection
            self.text_request.setUsesLanguageCorrection_(False)  # Disable for UI elements
            
            # Custom words that commonly appear in game interfaces
            game_vocabulary = [
                "Start", "Game", "Options", "Back", "Quit", "Continue",
                "New", "Load", "Save", "Settings", "Audio", "Video",
                "Single", "Player", "Multiplayer", "Campaign", "Mission"
            ]
            
            # Note: Custom vocabulary requires VNStringArray, implementation may vary
            self.audio_signal("Configured for game interface text recognition")
            
        except Exception as e:
            print(f"⚠️ Game text configuration warning: {e}")


def create_apple_vision_ocr(config: Dict[str, Any]) -> AppleVisionOCR:
    """
    Factory function to create Apple Vision Framework OCR engine.
    
    LEVEL-5 ARCHITECTURAL CORRECTION: This replaces all pytesseract/ocrmac usage.
    """
    try:
        vision_ocr = AppleVisionOCR(config)
        vision_ocr.configure_for_game_text()
        
        print("✅ Apple Vision Framework OCR engine ready for Signal Fusion Engine")
        return vision_ocr
        
    except Exception as e:
        print(f"❌ Apple Vision Framework creation failed: {e}")
        raise RuntimeError(f"VISION_OCR_CREATION_FAILED: {e}")