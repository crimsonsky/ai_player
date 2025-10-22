"""
Perception Module - Module 1: RAW DATA -> FEATURES
Handles screen capture, OCR, and template matching for game state perception.
Implements M2 - Menu Reading POC with focus management and timeout protection.
"""

import time
import os
import signal
import subprocess
from typing import Dict, Any, List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import Cocoa
import Quartz


class TimeoutException(Exception):
    """Exception raised when operations exceed timeout."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout detection."""
    raise TimeoutException("Operation timed out")


def with_timeout(seconds):
    """Decorator to add timeout protection to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutException:
                print(f"⚠️ HANG DETECTED: {func.__name__} exceeded {seconds}s timeout")
                return None
        return wrapper
    return decorator


class PerceptionModule:
    """
    Handles all perception tasks including screen capture, template matching, and OCR.
    Implements requirements for resolution independence (Req 2.6) and M2 functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Perception Module.
        
        Args:
            config: Configuration dictionary for perception settings
        """
        self.config = config
        self.template_library = None
        self.ocr_manager = None
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        self.screen_width = None
        self.screen_height = None
        self.audio_enabled = config.get('audio_feedback', True)
        self._initialize_screen_info()
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize template library and OCR manager."""
        try:
            # Import the new components
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
            
            from template_library import TemplateLibrary
            from ocr_manager import OCRManager
            
            self.template_library = TemplateLibrary(self.config)
            self.ocr_manager = OCRManager(self.config)
            
            # Load existing template library if available
            self.template_library.load_template_library()
            
            print("✅ Perception Module components initialized")
            
        except ImportError as e:
            print(f"⚠️ Could not import perception components: {e}")
            print("   Using basic perception mode")
        except Exception as e:
            print(f"❌ Error initializing perception components: {e}")
            print("   Using basic perception mode")
    
    def audio_signal(self, message: str, voice: str = "Alex") -> None:
        """Provide audio feedback during operations."""
        if self.audio_enabled:
            try:
                os.system(f'say -v {voice} "{message}"')
            except Exception as e:
                print(f"Audio feedback failed: {e}")
    
    def ensure_app_focus(self, app_name: str = "Dune Legacy") -> bool:
        """
        Ensure the specified application is in focus before screen capture.
        Critical for reliable perception.
        """
        try:
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                if app.localizedName() == app_name:
                    app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)
                    time.sleep(0.5)  # Allow focus transition
                    return True
            return False
        except Exception as e:
            print(f"Error ensuring app focus: {e}")
            return False
    
    def _initialize_screen_info(self) -> None:
        """Initialize screen dimensions for normalization."""
        screen = Cocoa.NSScreen.mainScreen()
        frame = screen.frame()
        self.screen_width = frame.size.width
        self.screen_height = frame.size.height
    
    @with_timeout(5)
    def capture_screen(self) -> Optional[str]:
        """
        Capture the current screen and save to temporary file.
        
        Returns:
            str: Path to captured screenshot, None if failed
        """
        try:
            timestamp = int(time.time())
            screenshot_path = f"/tmp/ai_player_screenshot_{timestamp}.png"
            
            # Use screencapture command (permissions already verified)
            result = subprocess.run(['screencapture', '-x', screenshot_path], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                print(f"📸 Screenshot captured: {file_size} bytes")
                return screenshot_path
            else:
                print(f"❌ Screenshot failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Screen capture error: {e}")
            return None
    
    @with_timeout(15)
    def analyze_menu_screen(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Complete M2 menu analysis: template matching + OCR.
        
        Args:
            screenshot_path: Path to screenshot image
            
        Returns:
            Dict containing detected elements, text, and confidence scores
        """
        self.audio_signal("Analyzing menu screen")
        
        analysis_result = {
            "templates_detected": [],
            "text_extracted": {},
            "average_confidence": 0.0,
            "recalibration_needed": False,
            "timestamp": time.time()
        }
        
        try:
            # Step 1: Template matching (if available)
            if self.template_library:
                print("🔍 Running template matching...")
                template_matches = self.template_library.detect_elements_fallback(screenshot_path)
                
                for match in template_matches:
                    template_data = {
                        "template_id": match.template_id,
                        "normalized_x": match.normalized_x,
                        "normalized_y": match.normalized_y,
                        "confidence": match.confidence,
                        "roi": match.roi
                    }
                    analysis_result["templates_detected"].append(template_data)
                
                print(f"   📍 Found {len(template_matches)} template matches")
            
            # Step 2: OCR text extraction (if available)
            if self.ocr_manager:
                print("📝 Running OCR text extraction...")
                text_data = self.ocr_manager.extract_menu_text(screenshot_path)
                analysis_result["text_extracted"] = text_data
                
                print(f"   📋 Extracted: '{text_data.get('title', '')}' + {len(text_data.get('menu_items', []))} menu items")
            
            # Step 3: Calculate overall confidence
            confidences = []
            
            # Add template confidences
            for template in analysis_result["templates_detected"]:
                confidences.append(template["confidence"])
            
            # Add OCR confidence
            if "confidence" in analysis_result["text_extracted"]:
                confidences.append(analysis_result["text_extracted"]["confidence"])
            
            if confidences:
                analysis_result["average_confidence"] = sum(confidences) / len(confidences)
            
            # Step 4: Check if recalibration needed
            if analysis_result["average_confidence"] < self.confidence_threshold:
                analysis_result["recalibration_needed"] = True
                print(f"⚠️ Low confidence ({analysis_result['average_confidence']:.2f} < {self.confidence_threshold})")
                self.audio_signal("Low confidence detected")
            else:
                print(f"✅ Good confidence: {analysis_result['average_confidence']:.2f}")
                self.audio_signal("Menu analysis complete")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Menu analysis error: {e}")
            analysis_result["recalibration_needed"] = True
            return analysis_result
    
    def run_full_m2_pipeline(self, app_name: str = "Dune Legacy") -> Dict[str, Any]:
        """
        Complete M2 - Menu Reading POC pipeline.
        
        Args:
            app_name: Name of application to analyze
            
        Returns:
            Dict containing full analysis results
        """
        self.audio_signal("Starting M2 menu reading pipeline")
        
        pipeline_result = {
            "success": False,
            "screenshot_path": None,
            "analysis": {},
            "error": None
        }
        
        try:
            # Step 1: Ensure app focus
            if not self.ensure_app_focus(app_name):
                raise Exception(f"Could not focus {app_name}")
            
            # Step 2: Capture screen
            screenshot_path = self.capture_screen()
            if not screenshot_path:
                raise Exception("Screen capture failed")
            
            pipeline_result["screenshot_path"] = screenshot_path
            
            # Step 3: Analyze menu
            analysis = self.analyze_menu_screen(screenshot_path)
            pipeline_result["analysis"] = analysis
            
            # Step 4: Check success criteria
            templates_found = len(analysis["templates_detected"])
            text_found = len(analysis["text_extracted"].get("menu_items", []))
            confidence_ok = analysis["average_confidence"] >= self.confidence_threshold
            
            if templates_found > 0 and text_found > 0 and confidence_ok:
                pipeline_result["success"] = True
                self.audio_signal("M2 pipeline completed successfully")
            else:
                pipeline_result["success"] = False
                self.audio_signal("M2 pipeline completed with issues")
            
            return pipeline_result
            
        except Exception as e:
            pipeline_result["error"] = str(e)
            print(f"❌ M2 pipeline error: {e}")
            self.audio_signal("M2 pipeline failed")
            return pipeline_result
            region = Quartz.CGRectMake(0, 0, self.screen_width, self.screen_height)
            image_ref = Quartz.CGWindowListCreateImage(
                region,
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID,
                Quartz.kCGWindowImageDefault
            )
            
            # Convert to PIL Image then to numpy array
            width = Quartz.CGImageGetWidth(image_ref)
            height = Quartz.CGImageGetHeight(image_ref)
            bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
            
            # Get raw pixel data
            data_provider = Quartz.CGImageGetDataProvider(image_ref)
            data = Quartz.CGDataProviderCopyData(data_provider)
            
            # Convert to numpy array
            image_array = np.frombuffer(data, dtype=np.uint8)
            image_array = image_array.reshape((height, bytes_per_row))
            
            # Extract RGB channels (assuming BGRA format)
            rgb_array = image_array[:, :width*4].reshape((height, width, 4))
            rgb_array = rgb_array[:, :, [2, 1, 0]]  # BGR to RGB
            
            return rgb_array
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def extract_features(self, screenshot: np.ndarray) -> Dict[str, Any]:
        """
        Extract features from the screenshot using template matching and OCR.
        
        Args:
            screenshot: Raw screenshot as numpy array
            
        Returns:
            Dict containing extracted features and game state information
        """
        features = {
            'elements': [],
            'text_data': {},
            'is_in_main_menu': False,
            'is_in_game': False,
            'is_game_over': False,
            'avg_confidence_score': 0.0,
            'current_minerals': 0,
            'power_consumption': 0
        }
        
        try:
            # Template matching for UI elements
            elements, avg_confidence = self._find_template_matches(screenshot)
            features['elements'] = elements
            features['avg_confidence_score'] = avg_confidence
            
            # OCR for text extraction
            text_data = self._extract_text_ocr(screenshot)
            features['text_data'] = text_data
            
            # Game state detection based on found elements and text
            features.update(self._detect_game_state(elements, text_data))
            
            # Extract resource information if in game
            if features['is_in_game']:
                resources = self._extract_resources(text_data)
                features.update(resources)
            
        except Exception as e:
            print(f"Error extracting features: {e}")
        
        return features
    
    def _find_template_matches(self, screenshot: np.ndarray) -> Tuple[List[Dict], float]:
        """
        Find template matches in the screenshot.
        
        Args:
            screenshot: Screenshot to search in
            
        Returns:
            Tuple of (list of matches, average confidence)
        """
        elements = []
        confidences = []
        
        # Convert to grayscale for template matching
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        for template_id, template_info in self.template_library.items():
            try:
                template = cv2.imread(template_info['path'], cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # Perform template matching
                result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= template_info.get('threshold', self.confidence_threshold))
                
                for pt in zip(*locations[::-1]):
                    confidence = result[pt[1], pt[0]]
                    
                    # Normalize coordinates (0 to 1)
                    norm_x = pt[0] / self.screen_width
                    norm_y = pt[1] / self.screen_height
                    
                    elements.append({
                        'id': template_id,
                        'x': norm_x,
                        'y': norm_y,
                        'confidence': confidence
                    })
                    confidences.append(confidence)
                    
            except Exception as e:
                print(f"Error matching template {template_id}: {e}")
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        return elements, avg_confidence
    
    def _extract_text_ocr(self, screenshot: np.ndarray) -> Dict[str, str]:
        """
        Extract text from screenshot using macOS Vision framework.
        
        Args:
            screenshot: Screenshot to extract text from
            
        Returns:
            Dictionary of extracted text data
        """
        text_data = {}
        
        try:
            # This is a placeholder for ocrmac integration
            # In the actual implementation, we'll use ocrmac here
            
            # For now, return mock data structure
            text_data = {
                'detected_text': [],
                'resource_numbers': [],
                'menu_text': []
            }
            
        except Exception as e:
            print(f"Error in OCR extraction: {e}")
        
        return text_data
    
    def _detect_game_state(self, elements: List[Dict], text_data: Dict) -> Dict[str, bool]:
        """
        Detect current game state based on UI elements and text.
        
        Args:
            elements: List of detected UI elements
            text_data: Extracted text data
            
        Returns:
            Dictionary of game state flags
        """
        state = {
            'is_in_main_menu': False,
            'is_in_game': False,
            'is_game_over': False
        }
        
        # Simple heuristics based on detected elements
        element_ids = [elem['id'] for elem in elements]
        
        if 'main_menu_button' in element_ids or 'start_game_button' in element_ids:
            state['is_in_main_menu'] = True
        elif 'minimap' in element_ids or 'resource_panel' in element_ids:
            state['is_in_game'] = True
        elif 'game_over_text' in element_ids:
            state['is_game_over'] = True
        
        return state
    
    def _extract_resources(self, text_data: Dict) -> Dict[str, int]:
        """
        Extract resource values from OCR text data.
        
        Args:
            text_data: OCR extracted text
            
        Returns:
            Dictionary of resource values
        """
        resources = {
            'current_minerals': 0,
            'power_consumption': 0
        }
        
        # This will be implemented with actual OCR parsing
        # For now, return default values
        
        return resources
    
    def load_template_library(self, template_path: str) -> bool:
        """
        Load template library from JSON file.
        
        Args:
            template_path: Path to template library JSON
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # This will load the actual template library
            # For now, create a mock library
            self.template_library = {
                'main_menu_button': {
                    'path': 'data/templates/main_menu.png',
                    'threshold': 0.8
                },
                'start_game_button': {
                    'path': 'data/templates/start_game.png',
                    'threshold': 0.8
                }
            }
            return True
        except Exception as e:
            print(f"Error loading template library: {e}")
            return False
    
    def add_template(self, template_id: str, template_path: str, threshold: float = 0.8) -> bool:
        """
        Add a new template to the library.
        
        Args:
            template_id: Unique identifier for the template
            template_path: Path to the template image
            threshold: Confidence threshold for matching
            
        Returns:
            bool: True if added successfully
        """
        try:
            self.template_library[template_id] = {
                'path': template_path,
                'threshold': threshold
            }
            return True
        except Exception as e:
            print(f"Error adding template {template_id}: {e}")
            return False