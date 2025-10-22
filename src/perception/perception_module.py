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
        Initialize the Perception Module with Signal Fusion capabilities.
        
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
        
        # Clean M2 configuration
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        self._initialize_screen_info()
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize template library, OCR manager, and element location."""
        try:
            # Import the clean components with proper paths
            from ..utils.template_library import TemplateLibrary
            from ..utils.ocr_manager import OCRManager
            from .element_location import ElementLocationModule
            
            self.template_library = TemplateLibrary(self.config)
            self.ocr_manager = OCRManager(self.config)
            self.element_location = ElementLocationModule(self.config)
            
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
    def capture_screen(self) -> Optional[np.ndarray]:
        """
        Capture the current screen as numpy array.
        
        Returns:
            numpy.ndarray: Screenshot as BGR array, None if failed
        """
        try:
            import tempfile
            
            # Create temporary file for screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Use screencapture command (permissions already verified)
            result = subprocess.run(['screencapture', '-x', temp_path], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                # Load image as numpy array
                screenshot = cv2.imread(temp_path)
                
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                if screenshot is not None:
                    file_size = screenshot.nbytes
                    print(f"📸 Screenshot captured: {file_size} bytes")
                    return screenshot
                else:
                    print("❌ Failed to load screenshot as array")
                    return None
            else:
                print(f"❌ Screenshot failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Screen capture error: {e}")
            return None
    
    @with_timeout(5)
    def capture_screen_to_file(self) -> Optional[str]:
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
                print(f"📸 Screenshot saved: {file_size} bytes")
                return screenshot_path
            else:
                print(f"❌ Screenshot failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Screen capture error: {e}")
            return None
    
    def identify_screen_context(self, screenshot_path: str) -> str:
        """
        LEVEL-1 ARCHITECTURAL CORRECTION: Screen Context Identifier
        Uses OCR to read button text to determine screen context.
        Much more reliable than visual analysis since layouts are similar.
        
        Args:
            screenshot_path: Path to screenshot to analyze
            
        Returns:
            str: Screen context ID ('MAIN_MENU', 'SINGLE_PLAYER_SUB_MENU', 'UNKNOWN')
        """
        try:
            # Load screenshot
            image = cv2.imread(screenshot_path)
            if image is None:
                return 'UNKNOWN'
            
            print(f"   🔍 Screen Context Detection via Button Text OCR")
            
            # Find button-like regions to OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Detect button regions
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            button_regions = []
            for contour in contours:
                x, y, w_rect, h_rect = cv2.boundingRect(contour)
                
                # Filter for button-like regions
                if (w_rect > 80 and w_rect < 400 and h_rect > 25 and h_rect < 100 and 
                    cv2.contourArea(contour) > 800):
                    
                    # Convert to normalized ROI for OCR
                    roi = (x / w, y / h, w_rect / w, h_rect / h)
                    button_regions.append(roi)
            
            print(f"      Found {len(button_regions)} button-like regions")
            
            # Extract text from button regions using OCR
            detected_texts = []
            
            if self.ocr_manager:
                for i, roi in enumerate(button_regions[:8]):  # Limit to 8 regions to avoid slowdown
                    try:
                        ocr_results = self.ocr_manager.extract_text_from_image(screenshot_path, roi)
                        
                        for result in ocr_results:
                            if result.confidence > 0.3 and len(result.text.strip()) > 2:
                                text = result.text.strip().lower()
                                detected_texts.append(text)
                                print(f"         Button {i+1}: '{text}' (confidence: {result.confidence:.2f})")
                        
                    except Exception as e:
                        print(f"         OCR failed for region {i+1}: {e}")
            
            # Analyze detected text to determine screen context
            main_menu_texts = {'single player', 'multiplayer', 'options', 'quit', 'load game'}
            submenu_texts = {'campaign', 'skirmish', 'custom game', 'back', 'new game'}
            
            main_menu_matches = 0
            submenu_matches = 0
            
            print(f"      Detected texts: {detected_texts}")
            
            for text in detected_texts:
                # Check for main menu indicators
                for main_text in main_menu_texts:
                    if main_text in text or any(word in text for word in main_text.split()):
                        main_menu_matches += 1
                        print(f"         MAIN MENU indicator: '{text}' matches '{main_text}'")
                        break
                
                # Check for submenu indicators  
                for sub_text in submenu_texts:
                    if sub_text in text or any(word in text for word in sub_text.split()):
                        submenu_matches += 1
                        print(f"         SUBMENU indicator: '{text}' matches '{sub_text}'")
                        break
            
            print(f"      Main menu text matches: {main_menu_matches}")
            print(f"      Submenu text matches: {submenu_matches}")
            
            # Determine context based on text matches
            if main_menu_matches > submenu_matches and main_menu_matches >= 2:
                context = 'MAIN_MENU'
                print(f"      DECISION: Main menu (strong text evidence)")
            elif submenu_matches > main_menu_matches and submenu_matches >= 1:
                context = 'SINGLE_PLAYER_SUB_MENU' 
                print(f"      DECISION: Submenu (text evidence)")
            elif submenu_matches > 0:
                context = 'SINGLE_PLAYER_SUB_MENU'
                print(f"      DECISION: Submenu (some submenu text found)")
            elif main_menu_matches > 0:
                context = 'MAIN_MENU'
                print(f"      DECISION: Main menu (some main menu text found)")
            else:
                # Fallback: No clear text indicators, use basic heuristic
                if len(detected_texts) == 0:
                    context = 'UNKNOWN'
                    print(f"      DECISION: Unknown (no text detected)")
                else:
                    context = 'SINGLE_PLAYER_SUB_MENU'  # Assume submenu after Single Player click
                    print(f"      DECISION: Default to submenu (ambiguous text)")
            
            print(f"   🎯 Screen Context Identified: {context}")
            
            return context
            
        except Exception as e:
            print(f"❌ Screen context identification failed: {e}")
            return 'UNKNOWN'

    @with_timeout(10)
    def analyze_menu_screen(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Enhanced menu analysis with perception fusion (M2 implementation).
        NOW INCLUDES SCREEN CONTEXT GATING TO PREVENT TEMPLATE OVERLAP.
        
        Args:
            screenshot_path: Path to screenshot to analyze
            
        Returns:
            Dict containing analysis results with template and OCR data
        """
        self.audio_signal("Analyzing menu screen with perception fusion")
        
        analysis_result = {
            "screen_context": None,  # NEW: Screen Context ID
            "elements_detected": [],  # Updated structure with semantic validation
            "templates_detected": [],  # Legacy compatibility
            "text_extracted": {},
            "average_confidence": 0.0,
            "recalibration_needed": False,
            "timestamp": time.time()
        }
        
        try:
            # STEP 1: SCREEN CONTEXT IDENTIFICATION (CRITICAL FOR TEMPLATE OVERLAP PREVENTION)
            print("🎯 STEP 1: Identifying Screen Context...")
            screen_context = self.identify_screen_context(screenshot_path)
            analysis_result["screen_context"] = screen_context
            
            if screen_context == 'UNKNOWN':
                print("⚠️ Warning: Unknown screen context - proceeding with caution")
            
            # STEP 2: PERCEPTION FUSION (2C + 2D) WITH TEMPLATE GATING
            print("🔍 STEP 2: PERCEPTION FUSION - Template Matching + OCR + Semantic Validation...")
            
            # Initialize ElementLocationModule for enhanced detection
            from src.perception.element_location import ElementLocationModule
            
            element_config = {
                'templates_dir': 'data/templates',
                'confidence_threshold': self.confidence_threshold,
                'audio_feedback': self.audio_enabled,
                'screen_context': screen_context  # NEW: Pass context for template gating
            }
            
            element_locator = ElementLocationModule(element_config)
            
            # Execute CONTEXT-GATED element detection with perception fusion
            detected_elements = element_locator.detect_all_elements_with_context(screenshot_path, screen_context)
            
            # TEMPLATE OVERLAP PREVENTION: Apply semantic validation
            validated_elements = self._apply_template_overlap_prevention(detected_elements, screen_context)
            
            print(f"   📊 Screen Context: {screen_context}")
            print(f"   🔍 Raw detections: {len(detected_elements)}")
            print(f"   ✅ Validated elements: {len(validated_elements)}")
            
            # STEP 3: AUDIO FEEDBACK OF DETECTED ELEMENTS
            self._provide_audio_element_feedback(validated_elements, screen_context)
            
            # Process validated elements
            confidences = []
            
            for element in validated_elements:
                # New enhanced structure with semantic validation
                element_data = {
                    "template_id": element.template_id,
                    "name": element.name,
                    "normalized_x": element.normalized_x,
                    "normalized_y": element.normalized_y,
                    "confidence": element.confidence,
                    "roi": element.roi,
                    "method": element.method,
                    "text_label": element.text_label,
                    "is_functional_button": element.is_functional_button,
                    "text_confidence": element.text_confidence
                }
                analysis_result["elements_detected"].append(element_data)
                
                # Legacy compatibility structure
                template_data = {
                    "template_id": element.template_id,
                    "normalized_x": element.normalized_x,
                    "normalized_y": element.normalized_y,
                    "confidence": element.confidence,
                    "roi": element.roi
                }
                analysis_result["templates_detected"].append(template_data)
                
                confidences.append(element.confidence)
            
            # Calculate overall confidence
            if confidences:
                analysis_result["average_confidence"] = sum(confidences) / len(confidences)
            
            # Step 2: Check if recalibration needed
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
    
    def _apply_template_overlap_prevention(self, detected_elements: List, screen_context: str) -> List:
        """
        TEMPLATE OVERLAP PREVENTION: Filter elements based on screen context.
        Prevents main menu templates from matching on submenu screens.
        
        Args:
            detected_elements: Raw detected elements
            screen_context: Current screen context ID
            
        Returns:
            List of validated elements
        """
        if not detected_elements:
            return []
        
        validated_elements = []
        
        # Define template context mapping
        main_menu_templates = ['SINGLE_PLAYER', 'MULTIPLAYER', 'OPTIONS', 'QUIT']
        submenu_templates = ['BACK', 'CAMPAIGN', 'SKIRMISH', 'CUSTOM_GAME', 'LOAD_GAME']
        
        print(f"   🛡️ TEMPLATE OVERLAP PREVENTION - Context: {screen_context}")
        
        for element in detected_elements:
            template_id = getattr(element, 'template_id', 'UNKNOWN')
            
            # Apply context-based filtering
            should_include = True
            
            if screen_context == 'MAIN_MENU':
                # On main menu, exclude submenu-specific templates
                if any(submenu_tmpl in template_id.upper() for submenu_tmpl in submenu_templates):
                    if 'BACK' not in template_id.upper():  # Allow BACK on main menu for navigation
                        should_include = False
                        print(f"      ❌ Filtered {template_id}: submenu template on main menu")
                        
            elif screen_context == 'SINGLE_PLAYER_SUB_MENU':
                # On submenu, exclude main menu templates (CRITICAL FIX)
                if any(main_tmpl in template_id.upper() for main_tmpl in main_menu_templates):
                    should_include = False
                    print(f"      ❌ CRITICAL: Filtered {template_id}: main menu template on submenu")
            
            if should_include:
                validated_elements.append(element)
                print(f"      ✅ Validated {template_id}: appropriate for {screen_context}")
        
        return validated_elements
    
    def _provide_audio_element_feedback(self, validated_elements: List, screen_context: str) -> None:
        """
        Provide audio feedback listing all detected elements.
        Critical for M2 validation to ensure no 'Single Player' on submenu.
        
        Args:
            validated_elements: List of validated elements
            screen_context: Current screen context
        """
        if not validated_elements:
            self.audio_signal("No elements detected")
            return
        
        # Build audio report
        element_names = []
        for element in validated_elements:
            text_label = getattr(element, 'text_label', None)
            template_id = getattr(element, 'template_id', 'UNKNOWN')
            
            # Use text label if available, otherwise template ID
            name = text_label if text_label and text_label.strip() else template_id.replace('_', ' ')
            element_names.append(name)
        
        # Create audio report
        context_phrase = screen_context.replace('_', ' ').lower()
        elements_phrase = ', '.join(element_names)
        
        audio_message = f"On {context_phrase}, detected elements: {elements_phrase}"
        
        print(f"   🔊 Audio Report: {audio_message}")
        self.audio_signal(audio_message)
        
        # CRITICAL CHECK: Ensure no 'Single Player' on submenu
        if screen_context == 'SINGLE_PLAYER_SUB_MENU':
            for name in element_names:
                if 'single player' in name.lower():
                    print(f"   ❌ CRITICAL ERROR: 'Single Player' detected on submenu!")
                    self.audio_signal("CRITICAL ERROR: Single Player template overlap detected!")
                    break
            else:
                print(f"   ✅ Template Overlap Prevention SUCCESS: No 'Single Player' on submenu")

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
            print(f"Error adding template: {e}")
            return False

    # ===================================================================
    # SIGNAL FUSION ENGINE - Level-3 Architectural Correction
    # Implements multi-source validation per design specification
    # ===================================================================
    
    def signal_fusion_detection(self, target_elements: List[str] = None, context: str = 'MAIN_MENU') -> Dict[str, Any]:
        """
        SIGNAL FUSION ENGINE: Multi-source screen context validation.
        
        Implements Level-3 Architecture with three signal sources:
        - S1: Template Matching Confidence (OpenCV)
        - S2: OCR Text Detection (pytesseract)  
        - S3: Visual Pattern Analysis (Custom)
        
        Fusion Logic per design spec:
        IF (S1_confidence > 0.8 AND S2_text_match AND S3_pattern_valid):
            context = VALIDATED
        ELSE IF (S1_confidence > 0.6 AND S2_text_match):
            context = PROBABLE
        ELSE:
            context = UNCERTAIN → TRIGGER_RECALIBRATION
            
        Args:
            target_elements: List of elements to detect (e.g., ['start_game_button'])
            context: Expected screen context for validation
            
        Returns:
            Fusion result with validated elements and confidence metrics
        """
        try:
            print(f"🔬 SIGNAL FUSION ENGINE: Analyzing {context}")
            self.audio_signal(f"Signal fusion analysis starting")
            
            # Capture screen for all signal sources
            screenshot = self.capture_screen()
            if screenshot is None:
                return {'success': False, 'error': 'Screenshot capture failed', 'context': 'UNCERTAIN'}
            
            # Initialize fusion results
            fusion_result = {
                'success': False,
                'context': 'UNCERTAIN',
                'confidence': 0.0,
                'signals': {
                    's1_template': {'confidence': 0.0, 'matches': []},
                    's2_ocr': {'confidence': 0.0, 'text_found': []},
                    's3_visual': {'confidence': 0.0, 'patterns': []}
                },
                'validated_elements': [],
                'recalibration_needed': False
            }
            
            # S1: Template Matching Signal
            s1_result = self._signal_s1_template_matching(screenshot, target_elements)
            fusion_result['signals']['s1_template'] = s1_result
            
            # S2: OCR Text Detection Signal  
            s2_result = self._signal_s2_ocr_detection(screenshot, context)
            fusion_result['signals']['s2_ocr'] = s2_result
            
            # S3: Visual Pattern Analysis Signal
            s3_result = self._signal_s3_visual_analysis(screenshot, context)
            fusion_result['signals']['s3_visual'] = s3_result
            
            # Apply Fusion Logic
            fusion_result = self._apply_fusion_logic(fusion_result)
            
            # Self-Correction Loop
            if fusion_result['context'] == 'UNCERTAIN':
                fusion_result['recalibration_needed'] = True
                print("⚠️ Signal disagreement detected - triggering recalibration")
                
            print(f"📊 Fusion Result: {fusion_result['context']} (confidence: {fusion_result['confidence']:.2f})")
            return fusion_result
            
        except Exception as e:
            print(f"❌ Signal Fusion Engine error: {e}")
            return {
                'success': False, 
                'error': str(e), 
                'context': 'UNCERTAIN',
                'recalibration_needed': True
            }
    
    def _signal_s1_template_matching(self, screenshot: np.ndarray, target_elements: List[str]) -> Dict[str, Any]:
        """S1: Template Matching Confidence using OpenCV."""
        try:
            if not target_elements:
                target_elements = ['start_game_button', 'options_button', 'main_menu_title']
            
            # Save screenshot to temporary file for element location module
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            cv2.imwrite(temp_path, screenshot)
            
            try:
                # Use existing element location module for template matching
                element_matches = self.element_location.detect_all_elements(temp_path)
                
                s1_confidence = 0.0
                matched_elements = []
                
                for match in element_matches:
                    if match.template_id in target_elements and match.method == "template_matching":
                        matched_elements.append({
                            'element_id': match.template_id,
                            'confidence': match.confidence,
                            'position': (match.normalized_x, match.normalized_y)
                        })
                        s1_confidence = max(s1_confidence, match.confidence)
                
                return {
                    'confidence': s1_confidence,
                    'matches': matched_elements,
                    'method': 'opencv_template_matching'
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
        except Exception as e:
            print(f"S1 Template Matching error: {e}")
            return {'confidence': 0.0, 'matches': [], 'error': str(e)}
    
    def _signal_s2_ocr_detection(self, screenshot: np.ndarray, context: str) -> Dict[str, Any]:
        """S2: OCR Text Detection using pytesseract."""
        try:
            # Define expected text patterns for each context
            context_patterns = {
                'MAIN_MENU': ['start', 'game', 'options', 'quit', 'dune', 'legacy'],
                'IN_GAME': ['spice', 'credits', 'units', 'power', 'structures'],
                'SETTINGS': ['video', 'audio', 'controls', 'gameplay', 'back']
            }
            
            expected_patterns = context_patterns.get(context, [])
            
            # Extract text using OCR manager
            ocr_result = self.ocr_manager.extract_text_from_screenshot(screenshot)
            
            if not ocr_result.get('success', False):
                return {'confidence': 0.0, 'text_found': [], 'error': 'OCR extraction failed'}
            
            extracted_text = ocr_result.get('text', '').lower()
            text_matches = []
            s2_confidence = 0.0
            
            # Check for expected patterns
            for pattern in expected_patterns:
                if pattern.lower() in extracted_text:
                    text_matches.append(pattern)
                    s2_confidence += 0.2  # Incremental confidence per match
            
            # Cap confidence at 1.0
            s2_confidence = min(s2_confidence, 1.0)
            
            return {
                'confidence': s2_confidence,
                'text_found': text_matches,
                'raw_text': extracted_text[:200],  # Truncate for logging
                'method': 'pytesseract_ocr'
            }
            
        except Exception as e:
            print(f"S2 OCR Detection error: {e}")
            return {'confidence': 0.0, 'text_found': [], 'error': str(e)}
    
    def _signal_s3_visual_analysis(self, screenshot: np.ndarray, context: str) -> Dict[str, Any]:
        """S3: Visual Pattern Analysis using custom algorithms."""
        try:
            # Import OpenCV for visual analysis
            try:
                import cv2
            except ImportError:
                return {'confidence': 0.0, 'patterns': [], 'error': 'OpenCV not available'}
            
            patterns_detected = []
            s3_confidence = 0.0
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Pattern 1: Detect menu structure (vertical button layout)
            if context == 'MAIN_MENU':
                menu_confidence = self._detect_menu_structure(gray)
                if menu_confidence > 0.3:
                    patterns_detected.append('vertical_menu_layout')
                    s3_confidence += menu_confidence
            
            # Pattern 2: Detect dark/light regions (game UI vs menu)
            ui_confidence = self._detect_ui_regions(gray)
            if ui_confidence > 0.2:
                patterns_detected.append('ui_regions')
                s3_confidence += ui_confidence * 0.5
            
            # Pattern 3: Edge detection for button boundaries
            edge_confidence = self._detect_button_edges(gray)
            if edge_confidence > 0.3:
                patterns_detected.append('button_edges')
                s3_confidence += edge_confidence * 0.7
            
            # Cap confidence at 1.0
            s3_confidence = min(s3_confidence, 1.0)
            
            return {
                'confidence': s3_confidence,
                'patterns': patterns_detected,
                'method': 'custom_visual_analysis'
            }
            
        except Exception as e:
            print(f"S3 Visual Analysis error: {e}")
            return {'confidence': 0.0, 'patterns': [], 'error': str(e)}
    
    def _detect_menu_structure(self, gray_image: np.ndarray) -> float:
        """Detect vertical menu button structure."""
        try:
            import cv2
            
            # Apply edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Look for horizontal lines (menu buttons typically have horizontal edges)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Count horizontal line segments in the center-left area (typical menu location)
            height, width = gray_image.shape
            roi = horizontal_lines[int(height*0.3):int(height*0.8), int(width*0.2):int(width*0.6)]
            
            line_count = cv2.countNonZero(roi)
            # Normalize based on ROI size
            confidence = min(line_count / (roi.shape[0] * roi.shape[1] * 0.01), 1.0)
            
            return confidence
            
        except Exception:
            return 0.0
    
    def _detect_ui_regions(self, gray_image: np.ndarray) -> float:
        """Detect UI regions based on intensity patterns."""
        try:
            import cv2
            
            # Calculate image statistics
            mean_intensity = cv2.mean(gray_image)[0]
            
            # Look for regions with different intensities (UI elements vs background)
            height, width = gray_image.shape
            
            # Sample different regions
            regions = [
                gray_image[0:height//4, 0:width//4],           # Top-left
                gray_image[height//4:height//2, width//4:3*width//4],  # Center-top
                gray_image[height//2:3*height//4, width//4:3*width//4],  # Center
                gray_image[3*height//4:height, width//4:3*width//4]      # Bottom
            ]
            
            intensity_variance = 0
            for region in regions:
                if region.size > 0:
                    region_mean = cv2.mean(region)[0]
                    intensity_variance += abs(region_mean - mean_intensity)
            
            # Higher variance suggests structured UI elements
            confidence = min(intensity_variance / (4 * 128), 1.0)  # Normalize to 0-1
            
            return confidence
            
        except Exception:
            return 0.0
    
    def _detect_button_edges(self, gray_image: np.ndarray) -> float:
        """Detect button-like rectangular edges."""
        try:
            import cv2
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            button_like_shapes = 0
            height, width = gray_image.shape
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for button-like dimensions and positions
                aspect_ratio = w / h if h > 0 else 0
                area = w * h
                
                # Check if it looks like a button (reasonable aspect ratio, size, position)
                if (0.8 <= aspect_ratio <= 4.0 and  # Not too narrow or wide
                    area > (width * height * 0.005) and  # Not too small
                    area < (width * height * 0.2) and   # Not too large
                    x > width * 0.1 and x < width * 0.8):  # Reasonable horizontal position
                    button_like_shapes += 1
            
            # Normalize confidence based on expected number of menu buttons (3-6)
            confidence = min(button_like_shapes / 6.0, 1.0)
            
            return confidence
            
        except Exception:
            return 0.0
    
    def _apply_fusion_logic(self, fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fusion logic per design specification."""
        try:
            s1_conf = fusion_result['signals']['s1_template']['confidence']
            s2_conf = fusion_result['signals']['s2_ocr']['confidence'] 
            s3_conf = fusion_result['signals']['s3_visual']['confidence']
            
            s2_text_match = len(fusion_result['signals']['s2_ocr']['text_found']) > 0
            s3_pattern_valid = len(fusion_result['signals']['s3_visual']['patterns']) > 0
            
            print(f"📊 Signal Confidences - S1: {s1_conf:.2f}, S2: {s2_conf:.2f}, S3: {s3_conf:.2f}")
            print(f"📊 Signal Validations - S2_text: {s2_text_match}, S3_patterns: {s3_pattern_valid}")
            
            # Apply design specification fusion logic
            if s1_conf > 0.8 and s2_text_match and s3_pattern_valid:
                fusion_result['context'] = 'VALIDATED'
                fusion_result['confidence'] = (s1_conf + s2_conf + s3_conf) / 3.0
                fusion_result['success'] = True
                print("✅ Context VALIDATED (all signals strong)")
                
            elif s1_conf > 0.6 and s2_text_match:
                fusion_result['context'] = 'PROBABLE'
                fusion_result['confidence'] = (s1_conf + s2_conf) / 2.0
                fusion_result['success'] = True
                print("🟡 Context PROBABLE (template + OCR match)")
                
            else:
                fusion_result['context'] = 'UNCERTAIN'
                fusion_result['confidence'] = max(s1_conf, s2_conf, s3_conf)
                fusion_result['success'] = False
                print("⚠️ Context UNCERTAIN (insufficient signal agreement)")
            
            # Compile validated elements from strong signals
            if fusion_result['success']:
                validated_elements = []
                
                # Add template matches if confident
                if s1_conf > 0.6:
                    for match in fusion_result['signals']['s1_template']['matches']:
                        validated_elements.append(match)
                
                fusion_result['validated_elements'] = validated_elements
            
            return fusion_result
            
        except Exception as e:
            print(f"Fusion logic error: {e}")
            fusion_result['context'] = 'UNCERTAIN'
            fusion_result['success'] = False
            fusion_result['error'] = str(e)
            return fusion_result

    def adaptive_screen_recovery(self, target_context: str = 'MAIN_MENU', max_attempts: int = 5) -> Dict[str, Any]:
        """
        SIGNAL FUSION ADAPTIVE RECOVERY: Multi-strategy screen context recovery.
        
        REPLACES: Simple ESC-only navigation with intelligent recovery strategies
        IMPLEMENTS: Self-correcting navigation with focus management
        
        Recovery Strategies:
        1. Application focus re-assertion
        2. Window state validation and restoration  
        3. Progressive navigation (ESC, specific keys)
        4. Screen refresh and recapture
        5. Context-aware recovery based on current state
        6. Audio feedback and user guidance
        
        Args:
            target_context: Desired screen context to reach
            max_attempts: Maximum recovery attempts
            
        Returns:
            Recovery result with success status and final context
        """
        try:
            print(f"🔧 ADAPTIVE SCREEN RECOVERY: Targeting {target_context}")
            self.audio_signal(f"Starting adaptive recovery to {target_context.replace('_', ' ').lower()}")
            
            recovery_strategies = [
                self._strategy_focus_validation,
                self._strategy_progressive_navigation,
                self._strategy_window_restoration,
                self._strategy_context_aware_recovery,
                self._strategy_emergency_reset
            ]
            
            for attempt in range(max_attempts):
                print(f"\n--- Recovery Attempt {attempt + 1}/{max_attempts} ---")
                
                # Capture current state
                screenshot = self.capture_screen()
                if not screenshot:
                    print("   ⚠️ Screenshot capture failed, trying focus recovery...")
                    self._strategy_focus_validation()
                    time.sleep(1)
                    continue
                
                # Analyze current context
                fusion_result = self.validate_screen_context_fusion(screenshot)
                current_context = fusion_result['validated_context']
                confidence = fusion_result['fusion_confidence']
                
                print(f"   📊 Current: {current_context} (conf: {confidence:.2f})")
                
                # Check if we've reached target
                if current_context == target_context and confidence > 0.6:
                    print(f"✅ RECOVERY SUCCESS: Reached {target_context} with confidence {confidence:.2f}")
                    self.audio_signal(f"Recovery successful, reached {target_context.replace('_', ' ').lower()}")
                    return {
                        'success': True,
                        'final_context': current_context,
                        'confidence': confidence,
                        'attempts': attempt + 1,
                        'strategy_used': 'validation_success'
                    }
                
                # Apply recovery strategy based on attempt number
                strategy_index = min(attempt, len(recovery_strategies) - 1)
                strategy = recovery_strategies[strategy_index]
                
                print(f"   🔧 Applying strategy: {strategy.__name__}")
                strategy_result = strategy(current_context, target_context, attempt)
                
                if strategy_result.get('immediate_success'):
                    print(f"✅ Strategy succeeded immediately")
                    continue
                
                # Wait before next attempt
                time.sleep(1.5)
            
            # All attempts failed
            final_screenshot = self.capture_screen()
            if final_screenshot:
                final_fusion = self.validate_screen_context_fusion(final_screenshot)
                final_context = final_fusion['validated_context']
                final_confidence = final_fusion['fusion_confidence']
            else:
                final_context = 'UNKNOWN'
                final_confidence = 0.0
            
            print(f"❌ RECOVERY FAILED: Could not reach {target_context}")
            print(f"   Final state: {final_context} (conf: {final_confidence:.2f})")
            self.audio_signal(f"Recovery failed, unable to reach {target_context.replace('_', ' ').lower()}")
            
            return {
                'success': False,
                'final_context': final_context,
                'confidence': final_confidence,
                'attempts': max_attempts,
                'strategy_used': 'all_failed'
            }
            
        except Exception as e:
            print(f"❌ ADAPTIVE RECOVERY ERROR: {e}")
            return {
                'success': False,
                'final_context': 'UNKNOWN',
                'confidence': 0.0,
                'attempts': 0,
                'strategy_used': 'error',
                'error': str(e)
            }
    
    def _strategy_focus_validation(self, current_context: str, target_context: str, attempt: int) -> Dict[str, Any]:
        """Recovery Strategy 1: Application focus validation and restoration."""
        try:
            print("   🎯 STRATEGY: Focus validation and restoration")
            
            # Check if Dune Legacy is running and get window info
            result = subprocess.run([
                'osascript', '-e', 
                'tell application "System Events" to get name of every process whose background only is false'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                processes = result.stdout.strip()
                if 'Dune Legacy' not in processes:
                    print("   ⚠️ Dune Legacy not in foreground processes")
                    # Try to launch/focus the game
                    subprocess.run(['open', '-a', 'Dune Legacy'], capture_output=True)
                    time.sleep(3)
                    self.audio_signal("Relaunching Dune Legacy")
                else:
                    print("   ✅ Dune Legacy found in processes")
            
            # Force focus on Dune Legacy
            focus_commands = [
                'tell application "Dune Legacy" to activate',
                'tell application "System Events" to set frontmost of process "Dune Legacy" to true',
                'tell application "Dune Legacy" to tell window 1 to set index to 1'
            ]
            
            for cmd in focus_commands:
                subprocess.run(['osascript', '-e', cmd], capture_output=True)
                time.sleep(0.5)
            
            # Verify focus by checking window title
            window_result = subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to get name of first window of first application process whose frontmost is true'
            ], capture_output=True, text=True)
            
            if window_result.returncode == 0:
                window_name = window_result.stdout.strip()
                print(f"   📋 Active window: {window_name}")
                if 'Dune' in window_name or 'Legacy' in window_name:
                    print("   ✅ Focus validation successful")
                    return {'success': True, 'immediate_success': False}
            
            print("   ⚠️ Focus validation uncertain")
            return {'success': False, 'immediate_success': False}
            
        except Exception as e:
            print(f"   ❌ Focus validation failed: {e}")
            return {'success': False, 'immediate_success': False}
    
    def _strategy_progressive_navigation(self, current_context: str, target_context: str, attempt: int) -> Dict[str, Any]:
        """Recovery Strategy 2: Progressive navigation based on context analysis."""
        try:
            print("   🗺️ STRATEGY: Progressive context-aware navigation")
            
            # Context-specific navigation strategies
            if target_context == 'MAIN_MENU':
                if current_context == 'IN_GAME':
                    print("   📤 In-game detected, pressing ESC to menu")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                elif current_context == 'SINGLE_PLAYER_SUB_MENU':
                    print("   🔙 In submenu, pressing ESC to main menu")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                elif current_context == 'OPTIONS_MENU' or current_context == 'SETTINGS':
                    print("   ⚙️ In options/settings, trying ESC or Back")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                    time.sleep(0.5)
                    # Also try Enter key in case ESC doesn't work
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 36'], capture_output=True)
                elif current_context == 'UNKNOWN':
                    print("   ❓ Unknown context, trying multiple recovery keys")
                    recovery_keys = [53, 36, 49]  # ESC, Enter, Space
                    for key_code in recovery_keys:
                        subprocess.run(['osascript', '-e', f'tell application "System Events" to key code {key_code}'], capture_output=True)
                        time.sleep(0.3)
                else:
                    print(f"   🔄 Default navigation from {current_context}")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                    
            elif target_context == 'SINGLE_PLAYER_SUB_MENU':
                if current_context == 'MAIN_MENU':
                    print("   🎮 Main menu detected, looking for Single Player button")
                    # This would be handled by element detection and clicking
                    return {'success': False, 'immediate_success': False, 'needs_element_click': True}
                else:
                    print("   🔄 Not at main menu, navigating there first")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
            
            return {'success': True, 'immediate_success': False}
            
        except Exception as e:
            print(f"   ❌ Progressive navigation failed: {e}")
            return {'success': False, 'immediate_success': False}
    
    def _strategy_window_restoration(self, current_context: str, target_context: str, attempt: int) -> Dict[str, Any]:
        """Recovery Strategy 3: Window state validation and restoration."""
        try:
            print("   🪟 STRATEGY: Window state restoration")
            
            # Check window bounds and state
            bounds_result = subprocess.run([
                'osascript', '-e',
                '''tell application "System Events"
                    tell process "Dune Legacy"
                        get {position, size} of window 1
                    end tell
                end tell'''
            ], capture_output=True, text=True)
            
            if bounds_result.returncode == 0:
                print(f"   📏 Window bounds: {bounds_result.stdout.strip()}")
                
                # Check if window is minimized and restore it
                minimized_result = subprocess.run([
                    'osascript', '-e',
                    '''tell application "System Events"
                        tell process "Dune Legacy"
                            get value of attribute "AXMinimized" of window 1
                        end tell
                    end tell'''
                ], capture_output=True, text=True)
                
                if 'true' in minimized_result.stdout.lower():
                    print("   📤 Window minimized, restoring...")
                    subprocess.run([
                        'osascript', '-e',
                        '''tell application "System Events"
                            tell process "Dune Legacy"
                                set value of attribute "AXMinimized" of window 1 to false
                            end tell
                        end tell'''
                    ], capture_output=True)
                    time.sleep(1)
                    return {'success': True, 'immediate_success': False}
                
                # Ensure window is properly sized and positioned
                subprocess.run([
                    'osascript', '-e',
                    '''tell application "System Events"
                        tell process "Dune Legacy"
                            set position of window 1 to {100, 100}
                            set frontmost to true
                        end tell
                    end tell'''
                ], capture_output=True)
                
                return {'success': True, 'immediate_success': False}
            else:
                print("   ⚠️ Could not access window information")
                return {'success': False, 'immediate_success': False}
                
        except Exception as e:
            print(f"   ❌ Window restoration failed: {e}")
            return {'success': False, 'immediate_success': False}
    
    def _strategy_context_aware_recovery(self, current_context: str, target_context: str, attempt: int) -> Dict[str, Any]:
        """Recovery Strategy 4: Context-aware recovery based on screen analysis."""
        try:
            print("   🧠 STRATEGY: Context-aware intelligent recovery")
            
            # Use Signal Fusion to understand current screen better
            screenshot = self.capture_screen()
            if not screenshot:
                return {'success': False, 'immediate_success': False}
            
            # Analyze screen patterns for stuck states
            fusion_result = self.validate_screen_context_fusion(screenshot)
            signal_agreement = fusion_result.get('signal_agreement', 0.0)
            confidence = fusion_result.get('fusion_confidence', 0.0)
            
            print(f"   📊 Signal analysis - Agreement: {signal_agreement:.2f}, Confidence: {confidence:.2f}")
            
            # If signals are conflicted, try screen refresh
            if signal_agreement < 0.4:
                print("   🔄 Low signal agreement, forcing screen refresh")
                # Click somewhere neutral and recapture
                subprocess.run(['osascript', '-e', 'tell application "System Events" to click at {100, 100}'], capture_output=True)
                time.sleep(0.5)
                # Try Alt+Tab to refresh
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 48 using command down'], capture_output=True)
                time.sleep(0.3)
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 48 using command down'], capture_output=True)
                return {'success': True, 'immediate_success': False}
            
            # If confidence is very low, try multiple input methods
            if confidence < 0.3:
                print("   ⌨️ Low confidence, trying multiple input methods")
                input_methods = [
                    ('key code 53', 'ESC'),
                    ('key code 36', 'Enter'), 
                    ('key code 49', 'Space'),
                    ('key code 125', 'Down Arrow'),
                    ('key code 126', 'Up Arrow')
                ]
                
                for key_cmd, key_name in input_methods:
                    print(f"     🔘 Trying {key_name}")
                    subprocess.run(['osascript', '-e', f'tell application "System Events" to {key_cmd}'], capture_output=True)
                    time.sleep(0.4)
                
                return {'success': True, 'immediate_success': False}
            
            # Context-specific intelligent actions
            if current_context == 'UNKNOWN' and attempt >= 2:
                print("   🎯 Unknown context persisting, trying game-specific recovery")
                # Try common game menu shortcuts
                game_shortcuts = [
                    ('key code 53', 'ESC'),  # Menu
                    ('key code 15', 'R'),    # Restart/Reset
                    ('key code 3', 'F'),     # Fullscreen toggle
                    ('key code 35', 'P')     # Pause
                ]
                
                for shortcut, name in game_shortcuts:
                    print(f"     🎮 Trying game shortcut: {name}")
                    subprocess.run(['osascript', '-e', f'tell application "System Events" to {shortcut}'], capture_output=True)
                    time.sleep(0.6)
                
                return {'success': True, 'immediate_success': False}
            
            return {'success': True, 'immediate_success': False}
            
        except Exception as e:
            print(f"   ❌ Context-aware recovery failed: {e}")
            return {'success': False, 'immediate_success': False}
    
    def _strategy_emergency_reset(self, current_context: str, target_context: str, attempt: int) -> Dict[str, Any]:
        """Recovery Strategy 5: Emergency reset and application restart."""
        try:
            print("   🚨 STRATEGY: Emergency reset and restart")
            self.audio_signal("Emergency recovery, restarting application")
            
            # Force quit and restart Dune Legacy
            print("   🔄 Force quitting Dune Legacy...")
            subprocess.run(['pkill', '-f', 'Dune Legacy'], capture_output=True)
            time.sleep(2)
            
            print("   🚀 Restarting Dune Legacy...")
            subprocess.run(['open', '-a', 'Dune Legacy'], capture_output=True)
            time.sleep(5)  # Give more time for restart
            
            # Focus the restarted application
            subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], capture_output=True)
            time.sleep(2)
            
            print("   ✅ Emergency restart completed")
            return {'success': True, 'immediate_success': False}
            
        except Exception as e:
            print(f"   ❌ Emergency reset failed: {e}")
            return {'success': False, 'immediate_success': False}
    
    def validate_screen_context_fusion(self, screenshot_path: str) -> Dict[str, Any]:
        """
        SIGNAL FUSION ENGINE: Multi-source screen context validation.
        
        REPLACES: Single-source OCR dependency with robust multi-signal analysis
        IMPLEMENTS: Level-3 Architectural Correction
        
        Args:
            screenshot_path: Path to screenshot image
            
        Returns:
            Dictionary with validated context and fusion metadata
        """
        try:
            print("🔄 SIGNAL FUSION: Multi-source screen context validation")
            start_time = time.time()
            
            # Collect Signal 1: OCR Text Analysis (if available)
            s1_result = self._collect_ocr_signal(screenshot_path)
            print(f"   📝 S1 (OCR): {s1_result['context']} (conf: {s1_result['confidence']:.2f})")
            
            # Collect Signal 2: Visual Pattern Analysis
            s2_result = self._collect_visual_signal(screenshot_path)
            print(f"   🎯 S2 (Visual): {s2_result['context']} (conf: {s2_result['confidence']:.2f})")
            
            # Collect Signal 3: Element Density Analysis
            s3_result = self._collect_density_signal(screenshot_path)
            print(f"   📊 S3 (Density): {s3_result['context']} (conf: {s3_result['confidence']:.2f})")
            
            # Signal Fusion Algorithm
            signals = [s1_result, s2_result, s3_result]
            fusion_result = self._fuse_perception_signals(signals)
            
            processing_time = time.time() - start_time
            fusion_result['processing_time'] = processing_time
            
            # Update perception history
            self.perception_history.append(fusion_result)
            if len(self.perception_history) > self.max_history:
                self.perception_history.pop(0)
            
            # Log fusion result
            print(f"✅ SIGNAL FUSION COMPLETE: {fusion_result['confidence_level']}")
            print(f"   Context: {fusion_result['validated_context']}")
            print(f"   Fusion Confidence: {fusion_result['fusion_confidence']:.2f}")
            print(f"   Signal Agreement: {fusion_result['signal_agreement']:.2f}")
            
            return fusion_result
            
        except Exception as e:
            print(f"❌ SIGNAL FUSION ERROR: {e}")
            return {
                'validated_context': 'UNKNOWN',
                'fusion_confidence': 0.0,
                'confidence_level': 'ERROR',
                'signal_agreement': 0.0,
                'processing_time': 0.0,
                'error': str(e)
            }
    
    def _collect_ocr_signal(self, screenshot_path: str) -> Dict[str, Any]:
        """Collect OCR text signal for fusion - OPTIMIZED for speed."""
        try:
            if self.ocr_manager:
                # Use FAST OCR path - avoid slow pytesseract
                start_time = time.time()
                ocr_results = self.ocr_manager.extract_text_from_image(screenshot_path)
                ocr_time = time.time() - start_time
                
                # If OCR takes too long, use fallback immediately
                if ocr_time > 2.0:
                    print(f"   ⚠️ OCR too slow ({ocr_time:.2f}s), using fast fallback")
                    return self._fast_context_detection(screenshot_path)
                
                # Analyze text for context clues
                texts = [result.text.lower() for result in ocr_results if hasattr(result, 'text')]
                
                # Simple context detection based on text
                main_menu_keywords = ['start', 'new game', 'load', 'options', 'quit']
                submenu_keywords = ['single player', 'campaign', 'skirmish', 'back']
                
                main_score = sum(1 for text in texts for keyword in main_menu_keywords if keyword in text)
                sub_score = sum(1 for text in texts for keyword in submenu_keywords if keyword in text)
                
                if main_score > sub_score and main_score > 0:
                    return {'context': 'MAIN_MENU', 'confidence': min(main_score * 0.3, 0.8)}
                elif sub_score > 0:
                    return {'context': 'SINGLE_PLAYER_SUB_MENU', 'confidence': min(sub_score * 0.4, 0.8)}
                else:
                    return {'context': 'UNKNOWN', 'confidence': 0.1}
            else:
                return {'context': 'UNKNOWN', 'confidence': 0.0}
                
        except Exception as e:
            return {'context': 'UNKNOWN', 'confidence': 0.0, 'error': str(e)}
    
    def _fast_context_detection(self, screenshot_path: str) -> Dict[str, Any]:
        """Fast context detection using image analysis instead of slow OCR."""
        try:
            # Use the same logic as identify_screen_context but return fusion format
            context = self.identify_screen_context(screenshot_path)
            
            confidence_map = {
                'MAIN_MENU': 0.8,
                'SINGLE_PLAYER_SUB_MENU': 0.7,
                'IN_GAME': 0.6,
                'UNKNOWN': 0.1
            }
            
            return {
                'context': context,
                'confidence': confidence_map.get(context, 0.1)
            }
            
        except Exception as e:
            return {'context': 'UNKNOWN', 'confidence': 0.0, 'error': str(e)}
    
    def _collect_visual_signal(self, screenshot_path: str) -> Dict[str, Any]:
        """Collect visual pattern signal for fusion."""
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                return {'context': 'UNKNOWN', 'confidence': 0.0}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Edge density analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # Color variance analysis
            color_variance = np.std(gray)
            
            # Context prediction based on visual patterns
            if edge_density > 0.15 and color_variance > 40:
                return {'context': 'MAIN_MENU', 'confidence': 0.7}
            elif edge_density > 0.08 and color_variance > 25:
                return {'context': 'SINGLE_PLAYER_SUB_MENU', 'confidence': 0.6}
            elif edge_density < 0.05:
                return {'context': 'IN_GAME', 'confidence': 0.5}
            else:
                return {'context': 'UNKNOWN', 'confidence': 0.2}
                
        except Exception as e:
            return {'context': 'UNKNOWN', 'confidence': 0.0, 'error': str(e)}
    
    def _collect_density_signal(self, screenshot_path: str) -> Dict[str, Any]:
        """Collect element density signal for fusion."""
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                return {'context': 'UNKNOWN', 'confidence': 0.0}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Find contours for UI elements
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size (likely UI elements)
            min_area = (width * height) * 0.001
            max_area = (width * height) * 0.15
            ui_elements = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
            element_count = len(ui_elements)
            
            # Context prediction based on element count
            if 3 <= element_count <= 6:
                return {'context': 'MAIN_MENU', 'confidence': 0.6}
            elif 2 <= element_count <= 4:
                return {'context': 'SINGLE_PLAYER_SUB_MENU', 'confidence': 0.5}
            elif element_count > 6:
                return {'context': 'IN_GAME', 'confidence': 0.4}
            else:
                return {'context': 'UNKNOWN', 'confidence': 0.2}
                
        except Exception as e:
            return {'context': 'UNKNOWN', 'confidence': 0.0, 'error': str(e)}
    
    def _fuse_perception_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        SIGNAL FUSION ALGORITHM: Weighted voting with confidence analysis.
        
        Args:
            signals: List of signal dictionaries with context and confidence
            
        Returns:
            Fusion result with validated context and metadata
        """
        try:
            # Signal weights
            weights = [0.5, 0.3, 0.2]  # OCR, Visual, Density
            
            # Weighted voting
            context_votes = {}
            total_weight = 0.0
            valid_signals = 0
            
            for i, signal in enumerate(signals):
                confidence = signal['confidence']
                context = signal['context']
                
                if confidence > 0.1 and context != 'UNKNOWN':
                    weight = weights[i] * confidence
                    context_votes[context] = context_votes.get(context, 0) + weight
                    total_weight += weight
                    valid_signals += 1
            
            # Normalize votes
            if total_weight > 0:
                for context in context_votes:
                    context_votes[context] /= total_weight
            
            # Calculate signal agreement
            unique_contexts = set(s['context'] for s in signals if s['confidence'] > 0.1 and s['context'] != 'UNKNOWN')
            signal_agreement = 1.0 - (len(unique_contexts) - 1) / max(len(signals), 1) if unique_contexts else 0.0
            
            # Determine fusion result
            if context_votes:
                validated_context = max(context_votes.items(), key=lambda x: x[1])[0]
                fusion_confidence = context_votes[validated_context]
            else:
                validated_context = 'UNKNOWN'
                fusion_confidence = 0.0
            
            # Enhance confidence based on agreement
            if signal_agreement > 0.8 and fusion_confidence > 0.6:
                fusion_confidence = min(fusion_confidence * 1.2, 1.0)
            elif signal_agreement < 0.4:
                fusion_confidence *= 0.7
            
            # Determine confidence level
            if fusion_confidence >= 0.8:
                confidence_level = 'VALIDATED'
            elif fusion_confidence >= 0.6:
                confidence_level = 'PROBABLE'
            elif fusion_confidence >= 0.3:
                confidence_level = 'UNCERTAIN'
            else:
                confidence_level = 'INVALID'
            
            return {
                'validated_context': validated_context,
                'fusion_confidence': fusion_confidence,
                'confidence_level': confidence_level,
                'signal_agreement': signal_agreement,
                'context_votes': context_votes,
                'valid_signals': valid_signals,
                'recalibration_needed': fusion_confidence < 0.4 or signal_agreement < 0.5
            }
            
        except Exception as e:
            return {
                'validated_context': 'UNKNOWN',
                'fusion_confidence': 0.0,
                'confidence_level': 'ERROR',
                'signal_agreement': 0.0,
                'context_votes': {},
                'valid_signals': 0,
                'recalibration_needed': True,
                'error': str(e)
            }
    
    def detect_elements(self, screenshot_path: str = None, context: str = 'MAIN_MENU', 
                       target_elements: List[str] = None) -> Dict[str, Any]:
        """
        SIGNAL FUSION ELEMENT DETECTION: Multi-source element identification using Signal Fusion Engine.
        
        LEVEL-3 ARCHITECTURE: Replaces single-source detection with robust multi-signal validation.
        
        Args:
            screenshot_path: Path to screenshot (optional, will capture if not provided)
            context: Screen context for fusion analysis
            target_elements: Specific elements to detect
            
        Returns:
            Signal Fusion result with validated elements and confidence metrics
        """
        try:
            print(f"🔍 SIGNAL FUSION ELEMENT DETECTION: {context}")
            
            # Use Signal Fusion Engine for robust detection
            fusion_result = self.signal_fusion_detection(target_elements, context)
            
            if not fusion_result['success']:
                print(f"⚠️ Signal Fusion failed: {fusion_result.get('error', 'Unknown error')}")
                
                # Self-correction loop: attempt recalibration if needed
                if fusion_result.get('recalibration_needed', False):
                    print("🔧 Attempting signal recalibration...")
                    recalibration_result = self._perform_signal_recalibration(context)
                    
                    if recalibration_result['success']:
                        # Retry detection after recalibration
                        fusion_result = self.signal_fusion_detection(target_elements, context)
                        
                # If still failing, provide fallback detection
                if not fusion_result['success']:
                    fusion_result = self._fallback_detection(screenshot_path, context)
            
            # Enhance result with detection metadata
            fusion_result['detection_timestamp'] = time.time()
            fusion_result['context'] = context
            fusion_result['method'] = 'signal_fusion_engine'
            
            print(f"📊 Detection Complete: {len(fusion_result.get('validated_elements', []))} elements validated")
            return fusion_result
            
        except Exception as e:
            print(f"❌ Signal Fusion Element Detection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'context': 'UNCERTAIN',
                'validated_elements': [],
                'recalibration_needed': True
            }
    
    def _perform_signal_recalibration(self, context: str) -> Dict[str, Any]:
        """Perform signal recalibration for improved accuracy."""
        try:
            print("🔄 Signal recalibration starting...")
            self.audio_signal("Recalibrating detection signals")
            
            # Step 1: Recapture screen with enhanced settings
            time.sleep(0.5)  # Allow screen to stabilize
            fresh_screenshot = self.capture_screen()
            
            if fresh_screenshot is None:
                return {'success': False, 'error': 'Screenshot recapture failed'}
            
            # Step 2: Update dynamic ROI coordinates if template library is available
            if hasattr(self, 'template_library') and self.template_library:
                try:
                    # Refresh template coordinates based on current screen
                    self.template_library.refresh_template_coordinates(fresh_screenshot)
                except Exception as e:
                    print(f"Template library refresh failed: {e}")
            
            # Step 3: Clear OCR cache to force fresh extraction
            if hasattr(self.ocr_manager, 'clear_cache'):
                self.ocr_manager.clear_cache()
            
            print("✅ Signal recalibration complete")
            return {'success': True, 'recalibrated_signals': ['s1_template', 's2_ocr', 's3_visual']}
            
        except Exception as e:
            print(f"❌ Signal recalibration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fallback_detection(self, screenshot_path: str = None, context: str = 'MAIN_MENU') -> Dict[str, Any]:
        """Fallback detection when Signal Fusion fails."""
        try:
            print("🔄 Using fallback detection method...")
            
            elements = []
            
            # Fallback 1: Direct element location detection
            if hasattr(self, 'element_location') and self.element_location:
                try:
                    if screenshot_path:
                        # Use provided screenshot path
                        temp_path = screenshot_path
                    else:
                        # Capture fresh screenshot and save to temp file
                        screenshot = self.capture_screen()
                        if screenshot is None:
                            raise Exception("Screenshot capture failed")
                        
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            temp_path = temp_file.name
                        cv2.imwrite(temp_path, screenshot)
                        
                    element_matches = self.element_location.detect_all_elements(temp_path)
                    
                    # Clean up if we created a temp file
                    if not screenshot_path:
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    for match in element_matches:
                        elements.append({
                            'element_id': match.template_id,
                            'confidence': match.confidence,
                            'position': (match.normalized_x, match.normalized_y),
                            'source': 'fallback_element_location'
                        })
                except Exception as e:
                    print(f"Fallback element location failed: {e}")
            
            # Fallback 2: Basic OCR extraction
            if self.ocr_manager and len(elements) == 0:
                try:
                    if screenshot_path:
                        ocr_results = self.ocr_manager.extract_text_from_image(screenshot_path)
                    else:
                        screenshot = self.capture_screen()
                        if screenshot is not None:
                            ocr_results = self.ocr_manager.extract_text_from_screenshot(screenshot)
                        else:
                            ocr_results = {'success': False}
                    
                    if ocr_results.get('success', False):
                        text = ocr_results.get('text', '')
                        if text.strip():
                            elements.append({
                                'element_id': 'fallback_text',
                                'text': text,
                                'confidence': 0.5,
                                'source': 'fallback_ocr'
                            })
                except Exception as e:
                    print(f"Fallback OCR failed: {e}")
            
            success = len(elements) > 0
            return {
                'success': success,
                'context': 'PROBABLE' if success else 'UNCERTAIN', 
                'confidence': 0.5 if success else 0.0,
                'validated_elements': elements,
                'method': 'fallback_detection',
                'signals': {
                    's1_template': {'confidence': 0.0, 'matches': []},
                    's2_ocr': {'confidence': 0.5 if success else 0.0, 'text_found': []},
                    's3_visual': {'confidence': 0.0, 'patterns': []}
                }
            }
            
        except Exception as e:
            print(f"❌ Fallback detection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'context': 'UNCERTAIN',
                'validated_elements': []
            }
            
        except Exception as e:
            print(f"❌ Element detection failed: {e}")
            return []
    
    def get_perception_health_report(self) -> Dict[str, Any]:
        """Generate health report of Signal Fusion perception system."""
        try:
            if not self.perception_history:
                return {
                    'health': 'NO_DATA',
                    'recommendations': ['Perform perception validation tests']
                }
            
            recent_results = self.perception_history[-5:]
            
            # Calculate metrics
            avg_confidence = np.mean([r['fusion_confidence'] for r in recent_results])
            avg_agreement = np.mean([r['signal_agreement'] for r in recent_results])
            recalibration_rate = sum(r.get('recalibration_needed', False) for r in recent_results) / len(recent_results)
            
            # Determine health status
            if avg_confidence > 0.8 and avg_agreement > 0.7 and recalibration_rate < 0.2:
                health = 'EXCELLENT'
            elif avg_confidence > 0.6 and avg_agreement > 0.5 and recalibration_rate < 0.4:
                health = 'GOOD'
            elif avg_confidence > 0.4 and recalibration_rate < 0.6:
                health = 'FAIR'
            else:
                health = 'POOR'
            
            return {
                'health': health,
                'metrics': {
                    'avg_confidence': avg_confidence,
                    'avg_agreement': avg_agreement,
                    'recalibration_rate': recalibration_rate
                },
                'total_validations': len(self.perception_history),
                'recent_contexts': [r['validated_context'] for r in recent_results]
            }
            
        except Exception as e:
            return {'health': 'ERROR', 'error': str(e)}
    
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
    
    def navigate_to_context(self, target_context: str, max_attempts: int = 8) -> Dict[str, Any]:
        """
        SIGNAL FUSION NAVIGATION: Intelligent navigation to target screen context.
        
        REPLACES: Simple ESC-only navigation with comprehensive recovery strategies
        IMPLEMENTS: Multi-strategy navigation with adaptive recovery
        
        This method combines screen context validation with intelligent recovery
        strategies to reliably reach the target context.
        
        Navigation Strategies:
        1. Current context validation and direct navigation
        2. Adaptive recovery if navigation fails
        3. Element-based navigation when available
        4. Progressive fallback strategies
        5. Emergency recovery and restart if needed
        
        Args:
            target_context: Target screen context ('MAIN_MENU', 'SINGLE_PLAYER_SUB_MENU', etc.)
            max_attempts: Maximum navigation attempts
            
        Returns:
            Navigation result with success status and context information
        """
        try:
            print(f"🧭 SIGNAL FUSION NAVIGATION: Targeting {target_context}")
            self.audio_signal(f"Navigating to {target_context.replace('_', ' ').lower()}")
            
            navigation_start_time = time.time()
            
            for attempt in range(max_attempts):
                print(f"\n--- Navigation Attempt {attempt + 1}/{max_attempts} ---")
                
                # Step 1: Capture and analyze current context
                screenshot = self.capture_screen()
                if not screenshot:
                    print(f"   ❌ Screenshot capture failed, triggering recovery...")
                    recovery_result = self.adaptive_screen_recovery(target_context, max_attempts=2)
                    if not recovery_result['success']:
                        continue
                    screenshot = self.capture_screen()
                
                if not screenshot:
                    print(f"   ❌ Still cannot capture screenshot")
                    continue
                
                # Step 2: Signal Fusion context validation
                fusion_result = self.validate_screen_context_fusion(screenshot)
                current_context = fusion_result['validated_context']
                confidence = fusion_result['fusion_confidence']
                confidence_level = fusion_result['confidence_level']
                
                print(f"   📊 Current Context: {current_context}")
                print(f"   🎯 Confidence: {confidence:.2f} ({confidence_level})")
                
                # Step 3: Check if we've reached the target
                if current_context == target_context and confidence >= 0.6:
                    navigation_time = time.time() - navigation_start_time
                    print(f"✅ NAVIGATION SUCCESS: Reached {target_context}")
                    print(f"   ⏱️ Time taken: {navigation_time:.2f}s")
                    print(f"   🎯 Final confidence: {confidence:.2f}")
                    
                    self.audio_signal(f"Successfully reached {target_context.replace('_', ' ').lower()}")
                    
                    return {
                        'success': True,
                        'final_context': current_context,
                        'confidence': confidence,
                        'attempts': attempt + 1,
                        'navigation_time': navigation_time,
                        'strategy': 'direct_navigation'
                    }
                
                # Step 4: Intelligent navigation based on current context
                navigation_action = self._determine_navigation_action(current_context, target_context, fusion_result)
                
                print(f"   🗺️ Navigation Action: {navigation_action['action']}")
                if 'description' in navigation_action:
                    print(f"      {navigation_action['description']}")
                
                # Step 5: Execute navigation action
                action_result = self._execute_navigation_action(navigation_action, screenshot)
                
                if action_result.get('trigger_recovery'):
                    print(f"   🔧 Navigation triggered recovery requirement")
                    recovery_result = self.adaptive_screen_recovery(target_context, max_attempts=3)
                    if recovery_result['success']:
                        continue
                
                # Step 6: Wait and validate progress
                time.sleep(1.5)
                
                # Check progress
                progress_screenshot = self.capture_screen()
                if progress_screenshot:
                    progress_fusion = self.validate_screen_context_fusion(progress_screenshot)
                    progress_context = progress_fusion['validated_context']
                    
                    if progress_context != current_context:
                        print(f"   ✅ Progress detected: {current_context} → {progress_context}")
                    elif attempt >= 3:
                        print(f"   ⚠️ No progress after attempt {attempt + 1}, escalating recovery")
                        recovery_result = self.adaptive_screen_recovery(target_context, max_attempts=2)
            
            # Navigation failed after all attempts
            final_screenshot = self.capture_screen()
            if final_screenshot:
                final_fusion = self.validate_screen_context_fusion(final_screenshot)
                final_context = final_fusion['validated_context']
                final_confidence = final_fusion['fusion_confidence']
            else:
                final_context = 'UNKNOWN'
                final_confidence = 0.0
            
            navigation_time = time.time() - navigation_start_time
            
            print(f"❌ NAVIGATION FAILED: Could not reach {target_context}")
            print(f"   Final state: {final_context} (conf: {final_confidence:.2f})")
            print(f"   Total time: {navigation_time:.2f}s")
            
            self.audio_signal(f"Navigation failed, could not reach {target_context.replace('_', ' ').lower()}")
            
            return {
                'success': False,
                'final_context': final_context,
                'confidence': final_confidence,
                'attempts': max_attempts,
                'navigation_time': navigation_time,
                'strategy': 'all_failed'
            }
            
        except Exception as e:
            print(f"❌ NAVIGATION ERROR: {e}")
            return {
                'success': False,
                'final_context': 'UNKNOWN',
                'confidence': 0.0,
                'attempts': 0,
                'navigation_time': 0.0,
                'strategy': 'error',
                'error': str(e)
            }
    
    def _determine_navigation_action(self, current_context: str, target_context: str, fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best navigation action based on current and target context."""
        try:
            confidence = fusion_result.get('fusion_confidence', 0.0)
            
            # Navigation decision matrix
            if target_context == 'MAIN_MENU':
                if current_context == 'SINGLE_PLAYER_SUB_MENU':
                    return {'action': 'press_esc', 'description': 'Navigate from submenu to main menu'}
                elif current_context == 'IN_GAME':
                    return {'action': 'press_esc', 'description': 'Exit game to main menu'}
                elif current_context == 'OPTIONS_MENU':
                    return {'action': 'press_esc', 'description': 'Exit options to main menu'}
                elif current_context == 'UNKNOWN' or confidence < 0.4:
                    return {'action': 'recovery_needed', 'description': 'Unknown state, trigger recovery'}
                else:
                    return {'action': 'press_esc', 'description': 'Default ESC navigation'}
            
            elif target_context == 'SINGLE_PLAYER_SUB_MENU':
                if current_context == 'MAIN_MENU':
                    return {'action': 'click_single_player', 'description': 'Click Single Player button'}
                elif current_context == 'IN_GAME' or current_context == 'OPTIONS_MENU':
                    return {'action': 'navigate_to_main_first', 'description': 'Navigate to main menu first'}
                else:
                    return {'action': 'recovery_needed', 'description': 'Need recovery to reach submenu'}
            
            else:
                return {'action': 'press_esc', 'description': f'Default navigation to {target_context}'}
                
        except Exception as e:
            return {'action': 'recovery_needed', 'description': f'Navigation planning error: {e}'}
    
    def _execute_navigation_action(self, navigation_action: Dict[str, Any], screenshot_path: str) -> Dict[str, Any]:
        """Execute the determined navigation action."""
        try:
            action = navigation_action['action']
            
            if action == 'press_esc':
                print(f"   ⌨️ Pressing ESC key")
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                return {'success': True}
            
            elif action == 'click_single_player':
                print(f"   🖱️ Looking for Single Player button")
                # Use element detection to find and click single player button
                elements = self.detect_elements(screenshot_path, context='MAIN_MENU')
                
                single_player_element = None
                for element in elements:
                    text = element.get('text', '').lower()
                    if 'single' in text and 'player' in text:
                        single_player_element = element
                        break
                
                if single_player_element:
                    # This would require mouse controller integration
                    print(f"   ✅ Single Player button found")
                    return {'success': True, 'element_found': True}
                else:
                    print(f"   ❌ Single Player button not found")
                    return {'success': False, 'trigger_recovery': True}
            
            elif action == 'navigate_to_main_first':
                print(f"   🔄 Need to reach main menu first")
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                return {'success': True}
            
            elif action == 'recovery_needed':
                print(f"   🔧 Recovery required")
                return {'success': False, 'trigger_recovery': True}
            
            else:
                print(f"   ❓ Unknown action: {action}")
                return {'success': False}
                
        except Exception as e:
            print(f"   ❌ Action execution failed: {e}")
            return {'success': False}
    
