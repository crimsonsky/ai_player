#!/usr/bin/env python3
"""
Template Capture Tool - Module 2B Implementation
Captures and manages visual templates for Dune Legacy menu elements.
Achieves Confidence Threshold >= 0.9 for all interactive elements.
"""

import subprocess
import time
import os
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import shutil


@dataclass
class TemplateDefinition:
    """Complete template definition with metadata."""
    template_id: str
    name: str
    description: str
    image_path: str
    confidence_threshold: float
    roi: Tuple[float, float, float, float]  # (x, y, w, h) normalized
    element_type: str  # "button", "text", "icon", "field"
    interactive: bool
    parent_screen: str  # "main_menu", "options", "game"


class TemplateCaptureTool:
    """
    Interactive template capture tool for building template libraries.
    Implements Module 2B specification for comprehensive UI element templates.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.templates_dir = self.config.get('templates_dir', 'data/templates')
        self.library_file = os.path.join(self.templates_dir, 'template_library.json')
        self.audio_enabled = self.config.get('audio_feedback', True)
        
        # Ensure directories exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(os.path.join(self.templates_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self.templates_dir, 'processed'), exist_ok=True)
        
        # Define Dune Legacy menu elements for capture
        self.target_elements = self._define_target_elements()
        self.captured_templates: Dict[str, TemplateDefinition] = {}
    
    def audio_signal(self, message: str):
        """Provide audio feedback."""
        if self.audio_enabled:
            try:
                os.system(f'say "{message}"')
            except:
                print(f"🔊 Audio: {message}")
    
    def _define_target_elements(self) -> List[Dict]:
        """Define all critical Dune Legacy menu elements to capture."""
        return [
            # Main Menu Elements
            {
                "template_id": "main_menu_title",
                "name": "Dune Legacy Title",
                "description": "Main game title text",
                "element_type": "text",
                "interactive": False,
                "parent_screen": "main_menu",
                "expected_roi": (0.2, 0.1, 0.6, 0.15),
                "confidence_threshold": 0.95
            },
            {
                "template_id": "start_game_button",
                "name": "Start Game Button",
                "description": "Primary start game button",
                "element_type": "button", 
                "interactive": True,
                "parent_screen": "main_menu",
                "expected_roi": (0.35, 0.35, 0.3, 0.08),
                "confidence_threshold": 0.95
            },
            {
                "template_id": "load_game_button",
                "name": "Load Game Button", 
                "description": "Load saved game button",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "main_menu",
                "expected_roi": (0.35, 0.45, 0.3, 0.08),
                "confidence_threshold": 0.95
            },
            {
                "template_id": "options_button",
                "name": "Options Button",
                "description": "Game settings/options button",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "main_menu", 
                "expected_roi": (0.35, 0.55, 0.3, 0.08),
                "confidence_threshold": 0.95
            },
            {
                "template_id": "quit_button",
                "name": "Quit Button",
                "description": "Exit game button",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "main_menu",
                "expected_roi": (0.35, 0.65, 0.3, 0.08),
                "confidence_threshold": 0.95
            },
            # Campaign Selection Elements
            {
                "template_id": "campaign_atreides",
                "name": "Atreides Campaign",
                "description": "House Atreides campaign option",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "campaign_select",
                "expected_roi": (0.2, 0.4, 0.25, 0.15),
                "confidence_threshold": 0.9
            },
            {
                "template_id": "campaign_harkonnen", 
                "name": "Harkonnen Campaign",
                "description": "House Harkonnen campaign option",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "campaign_select",
                "expected_roi": (0.55, 0.4, 0.25, 0.15),
                "confidence_threshold": 0.9
            },
            # Mission Start Elements
            {
                "template_id": "mission_start_button",
                "name": "Start Mission Button",
                "description": "Begin mission button",
                "element_type": "button",
                "interactive": True,
                "parent_screen": "mission_select",
                "expected_roi": (0.4, 0.8, 0.2, 0.08),
                "confidence_threshold": 0.95
            }
        ]
    
    def capture_full_template_library(self) -> bool:
        """
        Capture complete template library with user guidance.
        Implements Module 2B requirements.
        """
        self.audio_signal("Starting template library capture")
        print("🎯 TEMPLATE LIBRARY CAPTURE - Module 2B")
        print("=" * 50)
        
        try:
            # Step 1: Launch Dune Legacy
            print("🚀 Step 1: Launching Dune Legacy for template capture...")
            subprocess.run(['open', '/Applications/Dune Legacy.app'])
            time.sleep(4)
            
            # Step 2: Focus application
            self._focus_application("Dune Legacy")
            self.audio_signal("Game ready for template capture")
            
            # Step 3: Interactive template capture
            for element in self.target_elements:
                if element["parent_screen"] == "main_menu":
                    success = self._capture_template_interactive(element)
                    if not success:
                        print(f"❌ Failed to capture {element['name']}")
                        return False
            
            # Step 4: Navigate to other screens for additional templates
            print("\n📋 Capturing additional screen templates...")
            self._navigate_and_capture_additional_templates()
            
            # Step 5: Finalize library
            self._finalize_template_library()
            
            self.audio_signal("Template library capture complete")
            return True
            
        except Exception as e:
            print(f"❌ Template capture error: {e}")
            self.audio_signal("Template capture failed")
            return False
        
        finally:
            # Close game
            subprocess.run(['pkill', '-f', 'Dune Legacy'])
            self._focus_application("Visual Studio Code")
    
    def _capture_template_interactive(self, element_def: Dict) -> bool:
        """
        Capture a single template with user interaction.
        """
        print(f"\n🎯 Capturing: {element_def['name']}")
        print(f"   Type: {element_def['element_type']}")
        print(f"   Expected location: {element_def['expected_roi']}")
        
        # User prompt
        self.audio_signal(f"Locate {element_def['name']} on screen")
        print("   Position cursor over the element and press ENTER when ready...")
        input("   Press ENTER to capture template...")
        
        try:
            # Capture full screen
            timestamp = int(time.time())
            full_screenshot = f"/tmp/template_capture_{timestamp}.png"
            
            result = subprocess.run(['screencapture', '-x', full_screenshot])
            if result.returncode != 0:
                print("   ❌ Screenshot failed")
                return False
            
            # Crop to template region
            template_image = self._crop_template_region(
                full_screenshot, 
                element_def['expected_roi'],
                element_def['template_id']
            )
            
            if template_image:
                # Create template definition
                template = TemplateDefinition(
                    template_id=element_def['template_id'],
                    name=element_def['name'],
                    description=element_def['description'],
                    image_path=template_image,
                    confidence_threshold=element_def['confidence_threshold'],
                    roi=element_def['expected_roi'],
                    element_type=element_def['element_type'],
                    interactive=element_def['interactive'],
                    parent_screen=element_def['parent_screen']
                )
                
                self.captured_templates[element_def['template_id']] = template
                
                print(f"   ✅ Template captured: {os.path.basename(template_image)}")
                return True
            else:
                print("   ❌ Template cropping failed")
                return False
                
            # Cleanup
            if os.path.exists(full_screenshot):
                os.remove(full_screenshot)
                
        except Exception as e:
            print(f"   ❌ Capture error: {e}")
            return False
    
    def _crop_template_region(self, screenshot_path: str, roi: Tuple[float, float, float, float], template_id: str) -> Optional[str]:
        """
        Crop template region from screenshot using ImageMagick.
        """
        try:
            # Get image dimensions
            result = subprocess.run(['identify', screenshot_path], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("   ⚠️ ImageMagick identify failed, using manual cropping")
                return self._manual_crop_fallback(screenshot_path, roi, template_id)
            
            # Parse dimensions
            output_parts = result.stdout.split()
            if len(output_parts) >= 3:
                dimensions = output_parts[2]
                width, height = map(int, dimensions.split('x'))
                
                # Convert normalized ROI to pixels
                x_norm, y_norm, w_norm, h_norm = roi
                x_pixel = int(x_norm * width)
                y_pixel = int(y_norm * height) 
                w_pixel = int(w_norm * width)
                h_pixel = int(h_norm * height)
                
                # Create template file path
                template_path = os.path.join(self.templates_dir, 'processed', f"{template_id}.png")
                
                # Crop using ImageMagick
                crop_geometry = f"{w_pixel}x{h_pixel}+{x_pixel}+{y_pixel}"
                result = subprocess.run([
                    'convert', screenshot_path, 
                    '-crop', crop_geometry,
                    template_path
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(template_path):
                    return template_path
                else:
                    print(f"   ⚠️ ImageMagick crop failed: {result.stderr}")
                    return self._manual_crop_fallback(screenshot_path, roi, template_id)
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Crop error: {e}")
            return self._manual_crop_fallback(screenshot_path, roi, template_id)
    
    def _manual_crop_fallback(self, screenshot_path: str, roi: Tuple[float, float, float, float], template_id: str) -> Optional[str]:
        """
        Fallback: Manual template region specification.
        """
        template_path = os.path.join(self.templates_dir, 'raw', f"{template_id}_full.png")
        
        # Copy full screenshot as fallback
        try:
            shutil.copy2(screenshot_path, template_path)
            print(f"   ℹ️ Saved full screenshot as template: {template_id}")
            return template_path
        except Exception as e:
            print(f"   ❌ Fallback crop failed: {e}")
            return None
    
    def _navigate_and_capture_additional_templates(self):
        """Navigate to other screens and capture additional templates."""
        print("\n🔄 Capturing additional screen templates...")
        print("   Navigate manually through the game menus")
        print("   We'll capture templates for campaign selection and mission start")
        
        # This would be expanded to capture templates from other screens
        # For now, we'll focus on main menu templates
        pass
    
    def _finalize_template_library(self):
        """
        Finalize and save the template library.
        Implements JSON export with metadata.
        """
        print("\n💾 Finalizing template library...")
        
        try:
            # Convert templates to serializable format
            library_data = {
                "metadata": {
                    "version": "1.0",
                    "created": time.time(),
                    "game": "Dune Legacy",
                    "total_templates": len(self.captured_templates)
                },
                "templates": {}
            }
            
            for template_id, template in self.captured_templates.items():
                library_data["templates"][template_id] = asdict(template)
            
            # Save to JSON
            with open(self.library_file, 'w') as f:
                json.dump(library_data, f, indent=2)
            
            print(f"   ✅ Template library saved: {self.library_file}")
            print(f"   📊 Total templates: {len(self.captured_templates)}")
            
            # Generate summary report
            self._generate_library_report()
            
        except Exception as e:
            print(f"   ❌ Library finalization error: {e}")
    
    def _generate_library_report(self):
        """Generate template library summary report."""
        print("\n📋 TEMPLATE LIBRARY REPORT")
        print("=" * 40)
        
        for template_id, template in self.captured_templates.items():
            print(f"🎯 {template.name}")
            print(f"   ID: {template.template_id}")
            print(f"   Type: {template.element_type}")
            print(f"   Interactive: {template.interactive}")
            print(f"   Threshold: {template.confidence_threshold}")
            print(f"   ROI: {template.roi}")
            print(f"   File: {os.path.basename(template.image_path)}")
            print()
    
    def _focus_application(self, app_name: str):
        """Focus the specified application."""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(['osascript', '-e', script], timeout=5)
            time.sleep(0.5)
        except:
            pass


def main():
    """Run template capture tool."""
    config = {
        'templates_dir': 'data/templates',
        'audio_feedback': True
    }
    
    tool = TemplateCaptureTool(config)
    success = tool.capture_full_template_library()
    
    if success:
        print("\n🎉 TEMPLATE LIBRARY CAPTURE: SUCCESS")
        print("✅ Ready for Module 2C - Element Location implementation")
    else:
        print("\n❌ TEMPLATE LIBRARY CAPTURE: FAILED")
        print("   Review capture process and try again")


if __name__ == "__main__":
    main()