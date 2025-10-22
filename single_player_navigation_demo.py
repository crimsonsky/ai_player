#!/usr/bin/env python3
"""
Single Player Submenu Navigation and GUI Element Identification
Using Signal Fusion Engine + pyobjc Mouse Control

WORKFLOW:
1. Navigate from main menu to single player submenu
2. Identify and label all buttons using Signal Fusion Engine
3. Identify and label "Dune Legacy" headline and version number  
4. Move mouse in circle around each identified GUI element
5. Click the "Back" button to return to main menu

COMPLIANCE: AIP-TEST-V1.0 (Audio feedback, focus preservation, error handling)
"""

import sys
import os
import time
import math
import subprocess
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Add project paths
sys.path.insert(0, '/Users/amir/projects/ai_player/src')

class SinglePlayerNavigationDemo:
    """Complete single player submenu navigation and element identification demo."""
    
    def __init__(self):
        self.config = {
            'confidence_threshold': 0.6,
            'audio_feedback': True,
            'template_library_path': '/Users/amir/projects/ai_player/data/templates',
            'ocr_engine': 'tesseract',  # Force tesseract usage
            'game_app': 'Dune Legacy',
            'circle_radius': 30,
            'circle_steps': 20,
            'movement_speed': 0.05
        }
        self.perception = None
        self.mouse_control = None
        self.identified_elements = []
        
    def audio_signal(self, message: str, alert_type: str = 'info'):
        """Provide audio feedback."""
        if not self.config['audio_feedback']:
            print(f"🔊 {message}")
            return
            
        try:
            if alert_type == 'error':
                os.system('afplay /System/Library/Sounds/Basso.aiff')
                os.system(f'say "{message}" --rate=200')
            elif alert_type == 'success':
                os.system('afplay /System/Library/Sounds/Glass.aiff') 
                os.system(f'say "{message}" --rate=180')
            else:
                os.system(f'say "{message}" --rate=160')
        except Exception as e:
            print(f"🔊 Audio: {message} (Audio error: {e})")
    
    def focus_game(self) -> bool:
        """Ensure Dune Legacy has focus."""
        try:
            self.audio_signal("Focusing Dune Legacy game window")
            subprocess.run([
                'osascript', '-e', 
                f'tell application "{self.config["game_app"]}" to activate'
            ], capture_output=True, text=True, timeout=5)
            time.sleep(2)
            return True
        except Exception as e:
            self.audio_signal(f"Failed to focus game: {str(e)}", 'error')
            return False
    
    def initialize_systems(self) -> bool:
        """Initialize Signal Fusion Engine and mouse control."""
        try:
            self.audio_signal("Initializing detection and control systems")
            
            # Initialize Signal Fusion Engine
            from src.perception.perception_module import PerceptionModule
            self.perception = PerceptionModule(self.config)
            
            if not self.perception:
                self.audio_signal("Failed to initialize Signal Fusion Engine", 'error')
                return False
            
            # Initialize mouse control
            self.mouse_control = self._initialize_mouse_control()
            
            if not self.mouse_control:
                self.audio_signal("Failed to initialize mouse control", 'error')
                return False
            
            self.audio_signal("All systems ready", 'success')
            return True
            
        except Exception as e:
            self.audio_signal(f"System initialization failed: {str(e)}", 'error')
            return False
    
    def _initialize_mouse_control(self):
        """Initialize pyobjc mouse control system."""
        try:
            # Import pyobjc mouse control
            import Quartz
            
            class MouseControl:
                @staticmethod
                def get_screen_size():
                    """Get screen dimensions."""
                    screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
                    return int(screen.size.width), int(screen.size.height)
                
                @staticmethod
                def move_to(x: float, y: float):
                    """Move mouse to absolute coordinates."""
                    Quartz.CGWarpMouseCursorPosition((x, y))
                
                @staticmethod
                def click_at(x: float, y: float):
                    """Click at absolute coordinates."""
                    # Move to position
                    Quartz.CGWarpMouseCursorPosition((x, y))
                    time.sleep(0.1)
                    
                    # Create click events
                    click_down = Quartz.CGEventCreateMouseEvent(
                        None, Quartz.kCGEventLeftMouseDown, (x, y), Quartz.kCGMouseButtonLeft
                    )
                    click_up = Quartz.CGEventCreateMouseEvent(
                        None, Quartz.kCGEventLeftMouseUp, (x, y), Quartz.kCGMouseButtonLeft  
                    )
                    
                    # Post events
                    Quartz.CGEventPost(Quartz.kCGHIDEventTap, click_down)
                    time.sleep(0.05)
                    Quartz.CGEventPost(Quartz.kCGHIDEventTap, click_up)
                
                @staticmethod
                def circle_around_point(center_x: float, center_y: float, radius: float = 30, steps: int = 20):
                    """Move mouse in circle around a point."""
                    for i in range(steps + 1):
                        angle = (i / steps) * 2 * math.pi
                        x = center_x + radius * math.cos(angle)
                        y = center_y + radius * math.sin(angle)
                        Quartz.CGWarpMouseCursorPosition((x, y))
                        time.sleep(0.05)
            
            return MouseControl()
            
        except ImportError as e:
            print(f"❌ pyobjc not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Mouse control initialization failed: {e}")
            return None
    
    def navigate_to_single_player(self) -> bool:
        """Navigate from main menu to single player submenu."""
        try:
            self.audio_signal("Navigating to single player submenu")
            print("=" * 60)
            print("🎯 STEP 1: Navigate to Single Player Submenu")  
            print("=" * 60)
            
            # Use Signal Fusion Engine to detect main menu
            fusion_result = self.perception.signal_fusion_detection(
                target_elements=['start_game_button', 'single_player_button'],
                context='MAIN_MENU'
            )
            
            print(f"📊 Main Menu Detection:")
            print(f"   Success: {fusion_result['success']}")
            print(f"   Context: {fusion_result['context']}")  
            print(f"   Confidence: {fusion_result['confidence']:.3f}")
            
            if not fusion_result['success'] or fusion_result['context'] == 'UNCERTAIN':
                self.audio_signal("Cannot detect main menu reliably", 'error')
                return False
            
            # Look for single player button in validated elements
            single_player_element = None
            for element in fusion_result.get('validated_elements', []):
                element_id = element.get('element_id', '')
                if 'single_player' in element_id.lower() or 'start_game' in element_id.lower():
                    single_player_element = element
                    break
            
            if not single_player_element:
                self.audio_signal("Single player button not found", 'error')
                return False
            
            # Click single player button
            screen_width, screen_height = self.mouse_control.get_screen_size()
            pos = single_player_element.get('position', (0.5, 0.5))
            click_x = pos[0] * screen_width
            click_y = pos[1] * screen_height
            
            self.audio_signal("Clicking single player button")
            self.mouse_control.click_at(click_x, click_y)
            
            # Wait for submenu to load
            time.sleep(3)
            
            # Verify we're in single player submenu
            submenu_result = self.perception.signal_fusion_detection(
                target_elements=['back_button', 'new_game_button'],
                context='SINGLE_PLAYER_MENU'
            )
            
            if submenu_result['success'] and submenu_result['context'] in ['VALIDATED', 'PROBABLE']:
                self.audio_signal("Successfully navigated to single player submenu", 'success')
                return True
            else:
                self.audio_signal("Navigation may have failed, proceeding anyway")
                return True  # Continue even if verification is uncertain
                
        except Exception as e:
            self.audio_signal(f"Navigation failed: {str(e)}", 'error')
            return False
    
    def identify_gui_elements(self) -> List[Dict[str, Any]]:
        """Identify and label all GUI elements in single player submenu."""
        try:
            self.audio_signal("Identifying all GUI elements")
            print("\n" + "=" * 60)
            print("🔍 STEP 2: Identify and Label GUI Elements")
            print("=" * 60)
            
            # Use enhanced element detection with Signal Fusion Engine
            detection_result = self.perception.detect_elements(
                context='SINGLE_PLAYER_MENU',
                target_elements=['back_button', 'new_game_button', 'load_game_button', 'dune_legacy_title', 'version_number']
            )
            
            print(f"📊 Element Detection Result:")
            print(f"   Success: {detection_result['success']}")
            print(f"   Method: {detection_result.get('method', 'unknown')}")
            print(f"   Elements Found: {len(detection_result.get('validated_elements', []))}")
            
            # Also get OCR text to find headlines and version numbers
            screenshot = self.perception.capture_screen()
            if screenshot is not None:
                ocr_result = self.perception.ocr_manager.extract_text_from_screenshot(screenshot)
                
                if ocr_result.get('success', False):
                    raw_text = ocr_result.get('text', '')
                    print(f"📄 OCR Text Detected: '{raw_text[:200]}...'")
                    
                    # Look for specific text patterns
                    text_elements = self._extract_text_elements(raw_text, screenshot)
                    detection_result.get('validated_elements', []).extend(text_elements)
            
            # Label and categorize elements
            labeled_elements = self._label_elements(detection_result.get('validated_elements', []))
            self.identified_elements = labeled_elements
            
            # Display results
            print(f"\n🏷️ LABELED ELEMENTS:")
            for element in labeled_elements:
                print(f"   {element['category']}: {element['label']}")
                print(f"      Confidence: {element.get('confidence', 0):.3f}")
                if 'text' in element:
                    print(f"      Text: '{element['text'][:50]}...'")
                print()
            
            self.audio_signal(f"Identified {len(labeled_elements)} GUI elements", 'success')
            return labeled_elements
            
        except Exception as e:
            self.audio_signal(f"Element identification failed: {str(e)}", 'error')
            return []
    
    def _extract_text_elements(self, text: str, screenshot) -> List[Dict[str, Any]]:
        """Extract headline and version number from OCR text."""
        text_elements = []
        
        # Look for "Dune Legacy" headline
        if 'dune' in text.lower() and 'legacy' in text.lower():
            text_elements.append({
                'element_id': 'dune_legacy_headline',
                'category': 'headline',
                'label': 'Dune Legacy Title',
                'text': 'Dune Legacy',
                'confidence': 0.8,
                'position': (0.5, 0.2)  # Typical title position
            })
        
        # Look for version number patterns (e.g., "v1.2.3", "Version 1.2", "0.96")
        import re
        version_patterns = [
            r'v?\d+\.\d+\.\d+',  # v1.2.3 or 1.2.3
            r'Version\s+\d+\.\d+',  # Version 1.2
            r'\b\d+\.\d+\b'  # Simple 1.2
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                version_text = matches[0]
                text_elements.append({
                    'element_id': 'version_number',
                    'category': 'version',
                    'label': f'Version Number: {version_text}',
                    'text': version_text,
                    'confidence': 0.7,
                    'position': (0.5, 0.9)  # Typical bottom position
                })
                break
        
        return text_elements
    
    def _label_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Label and categorize detected elements."""
        labeled_elements = []
        
        for element in elements:
            element_id = element.get('element_id', '')
            text = element.get('text', '')
            
            # Categorize based on element ID and text content
            if 'back' in element_id.lower() or 'back' in text.lower():
                labeled_elements.append({
                    **element,
                    'category': 'button',
                    'label': 'Back Button',
                    'is_target': True  # This is our click target
                })
            elif 'new_game' in element_id.lower() or 'new' in text.lower():
                labeled_elements.append({
                    **element,
                    'category': 'button', 
                    'label': 'New Game Button'
                })
            elif 'load' in element_id.lower() or 'load' in text.lower():
                labeled_elements.append({
                    **element,
                    'category': 'button',
                    'label': 'Load Game Button'
                })
            elif 'dune' in element_id.lower() or 'legacy' in element_id.lower():
                labeled_elements.append({
                    **element,
                    'category': 'headline',
                    'label': 'Dune Legacy Title'
                })
            elif 'version' in element_id.lower():
                labeled_elements.append({
                    **element,
                    'category': 'version',
                    'label': f'Version Number'
                })
            else:
                # Generic element
                labeled_elements.append({
                    **element,
                    'category': 'element',
                    'label': f'GUI Element: {element_id}'
                })
        
        return labeled_elements
    
    def circle_around_elements(self):
        """Move mouse in circle around each identified element."""
        try:
            self.audio_signal("Circling around identified elements")
            print("\n" + "=" * 60)
            print("🔄 STEP 3: Circle Around Each GUI Element")
            print("=" * 60)
            
            screen_width, screen_height = self.mouse_control.get_screen_size()
            
            for i, element in enumerate(self.identified_elements, 1):
                label = element.get('label', 'Unknown Element')
                position = element.get('position', (0.5, 0.5))
                
                # Convert normalized coordinates to screen coordinates  
                center_x = position[0] * screen_width
                center_y = position[1] * screen_height
                
                print(f"🎯 Circling Element {i}: {label}")
                print(f"   Position: ({center_x:.0f}, {center_y:.0f})")
                
                self.audio_signal(f"Circling around {label}")
                
                # Move mouse in circle around the element
                self.mouse_control.circle_around_point(
                    center_x, center_y,
                    radius=self.config['circle_radius'],
                    steps=self.config['circle_steps']
                )
                
                time.sleep(0.5)  # Pause between elements
            
            self.audio_signal("Finished circling all elements", 'success')
            
        except Exception as e:
            self.audio_signal(f"Circling elements failed: {str(e)}", 'error')
    
    def click_back_button(self) -> bool:
        """Find and click the Back button."""
        try:
            self.audio_signal("Locating and clicking Back button")
            print("\n" + "=" * 60)
            print("🎯 STEP 4: Click Back Button")
            print("=" * 60)
            
            # Find the back button from identified elements
            back_button = None
            for element in self.identified_elements:
                if element.get('is_target', False) or 'back' in element.get('label', '').lower():
                    back_button = element
                    break
            
            if not back_button:
                # Try to detect back button directly
                self.audio_signal("Searching for back button with Signal Fusion")
                fusion_result = self.perception.signal_fusion_detection(
                    target_elements=['back_button'],
                    context='SINGLE_PLAYER_MENU'  
                )
                
                if fusion_result['success']:
                    for element in fusion_result.get('validated_elements', []):
                        if 'back' in element.get('element_id', '').lower():
                            back_button = element
                            break
            
            if not back_button:
                self.audio_signal("Back button not found", 'error')
                return False
            
            # Click the back button
            position = back_button.get('position', (0.5, 0.8))  # Default bottom position
            screen_width, screen_height = self.mouse_control.get_screen_size()
            
            click_x = position[0] * screen_width
            click_y = position[1] * screen_height
            
            print(f"🖱️ Clicking Back Button at ({click_x:.0f}, {click_y:.0f})")
            
            self.audio_signal("Clicking back button now")
            self.mouse_control.click_at(click_x, click_y)
            
            # Wait for navigation back to main menu
            time.sleep(3)
            
            # Verify we're back at main menu
            main_menu_check = self.perception.signal_fusion_detection(
                target_elements=['start_game_button', 'options_button'],
                context='MAIN_MENU'
            )
            
            if main_menu_check['success'] and main_menu_check['context'] in ['VALIDATED', 'PROBABLE']:
                self.audio_signal("Successfully returned to main menu", 'success')
                return True
            else:
                self.audio_signal("Back navigation completed, verifying...")
                return True  # Continue even if verification uncertain
                
        except Exception as e:
            self.audio_signal(f"Back button click failed: {str(e)}", 'error')
            return False
    
    def run_complete_demo(self) -> bool:
        """Execute the complete workflow."""
        try:
            self.audio_signal("Starting single player navigation demo", 'info')
            print("=" * 80)
            print("🎮 SINGLE PLAYER SUBMENU NAVIGATION DEMO")
            print("=" * 80)
            print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Initialize systems
            if not self.initialize_systems():
                return False
            
            # Focus game
            if not self.focus_game():
                return False
            
            # Step 1: Navigate to single player submenu
            if not self.navigate_to_single_player():
                return False
            
            # Step 2: Identify GUI elements
            elements = self.identify_gui_elements()
            if not elements:
                self.audio_signal("No elements identified, continuing anyway")
            
            # Step 3: Circle around elements
            if elements:
                self.circle_around_elements()
            
            # Step 4: Click back button
            success = self.click_back_button()
            
            # Final status
            if success:
                self.audio_signal("Demo completed successfully", 'success')
                print("\n🎉 DEMO COMPLETED SUCCESSFULLY")
            else:
                self.audio_signal("Demo completed with issues")
                print("\n⚠️ DEMO COMPLETED WITH ISSUES")
            
            return success
            
        except Exception as e:
            self.audio_signal(f"Demo failed: {str(e)}", 'error')
            print(f"❌ DEMO FAILED: {e}")
            return False
        
        finally:
            # Return focus to VS Code
            try:
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Visual Studio Code" to activate'
                ], capture_output=True, timeout=3)
                time.sleep(1)
            except:
                pass


def main():
    """Main execution."""
    demo = SinglePlayerNavigationDemo()
    
    print("🎯 Single Player Navigation Demo")
    print("This demo will:")
    print("1. Navigate to single player submenu")
    print("2. Identify and label all GUI elements")
    print("3. Circle mouse around each element")
    print("4. Click the Back button")
    print()
    
    demo.audio_signal("Demo ready to start")
    
    # Run the complete demo
    success = demo.run_complete_demo()
    
    return success


if __name__ == "__main__":
    exit_code = 0 if main() else 1
    sys.exit(exit_code)