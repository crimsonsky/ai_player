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
    
    def identify_screen_context(self, screenshot_path: str) -> str:
        """
        LEVEL-1 ARCHITECTURAL CORRECTION: Screen Context Identifier
        Detects unique visual anchors to determine current screen context.
        This prevents Template Overlap (R1) by gating template matching.
        
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
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # MAIN MENU VISUAL ANCHOR: Look for "Dune Legacy" headline
            # This should be a large text area in the upper portion of main menu
            main_menu_indicators = []
            
            # Check for main menu layout patterns
            # Look for horizontal button arrangement in center-lower area
            center_y = h // 2
            lower_third = h * 2 // 3
            
            # Apply edge detection to find button-like rectangles
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            horizontal_buttons = 0
            vertical_buttons = 0
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for button-like regions
                if (w > 100 and w < 400 and h > 30 and h < 80 and 
                    cv2.contourArea(contour) > 1000):
                    
                    # Check if in main menu button area (center-lower)
                    if center_y < y < lower_third:
                        horizontal_buttons += 1
                    # Check if in submenu area (more vertical layout)
                    elif y > center_y:
                        vertical_buttons += 1
            
            # SINGLE PLAYER SUBMENU VISUAL ANCHOR
            # Look for different layout pattern - more vertical button arrangement
            # or specific submenu indicators
            
            # Main menu typically has 3-5 horizontal buttons in center
            # Submenu typically has more vertical button arrangement
            
            print(f"   Screen Context Analysis:")
            print(f"      Horizontal buttons (main menu area): {horizontal_buttons}")
            print(f"      Vertical buttons (submenu area): {vertical_buttons}")
            
            # Enhanced decision logic with multiple detection methods
            
            # Method 1: Button layout analysis
            layout_score_main = 0
            layout_score_submenu = 0
            
            if horizontal_buttons >= 3:
                layout_score_main += 2
            if vertical_buttons >= 2:
                layout_score_submenu += 2
            
            # Method 2: Screen region analysis
            # Look for text patterns that indicate different screens
            upper_region = gray[:h//3, :]  # Top third
            lower_region = gray[2*h//3:, :]  # Bottom third
            
            # Apply more aggressive edge detection for text
            upper_edges = cv2.Canny(upper_region, 30, 100)
            lower_edges = cv2.Canny(lower_region, 30, 100)
            
            # Count edge density (more edges = more text/UI elements)
            upper_density = np.sum(upper_edges > 0) / (upper_edges.shape[0] * upper_edges.shape[1])
            lower_density = np.sum(lower_edges > 0) / (lower_edges.shape[0] * lower_edges.shape[1])
            
            # Main menu typically has centered layout
            # Submenu typically has more content in upper region
            if upper_density > 0.02:  # Significant content in upper region
                layout_score_submenu += 1
            if lower_density > 0.015:  # Content in lower region
                layout_score_main += 1
            
            # Method 3: Button position analysis
            center_buttons = 0
            upper_buttons = 0
            
            for contour in contours:
                x, y, w, h_rect = cv2.boundingRect(contour)
                if (w > 100 and w < 400 and h_rect > 30 and h_rect < 80 and 
                    cv2.contourArea(contour) > 1000):
                    
                    if h//3 < y < 2*h//3:  # Center region
                        center_buttons += 1
                    elif y < h//2:  # Upper region
                        upper_buttons += 1
            
            # Main menu has buttons centered, submenu has buttons higher
            if center_buttons >= 2:
                layout_score_main += 1
            if upper_buttons >= 1:
                layout_score_submenu += 1
            
            print(f"      Main menu score: {layout_score_main}")
            print(f"      Submenu score: {layout_score_submenu}")
            print(f"      Upper density: {upper_density:.4f}")
            print(f"      Lower density: {lower_density:.4f}")
            print(f"      Center buttons: {center_buttons}, Upper buttons: {upper_buttons}")
            
            # Final decision based on scores
            if layout_score_main > layout_score_submenu:
                context = 'MAIN_MENU'
            elif layout_score_submenu > layout_score_main:
                context = 'SINGLE_PLAYER_SUB_MENU'
            else:
                # Fallback: Use simple button count heuristic
                if horizontal_buttons >= 3 and vertical_buttons <= 2:
                    context = 'MAIN_MENU'
                elif vertical_buttons >= 2 and horizontal_buttons <= 2:
                    context = 'SINGLE_PLAYER_SUB_MENU'
                else:
                    context = 'UNKNOWN'
            
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
    
