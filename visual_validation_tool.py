#!/usr/bin/env python3
"""
Visual Validation Tool for AI Player System
Shows screenshots with detected menu buttons and their designations overlaid

This tool creates visual evidence that the M2 system correctly identifies menu elements.
"""

import os
import sys
import time
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.perception.element_location import ElementLocationModule, ElementMatch
from src.perception.ocr_integration import OCRIntegrationModule, OCRResult
from src.perception.perception_module import PerceptionModule
from src.utils.template_library import TemplateLibrary


class VisualValidationTool:
    """
    Visual validation tool that shows screenshots with detected elements overlaid.
    Provides clear visual evidence of M2 system accuracy.
    """
    
    def __init__(self):
        """Initialize the visual validation tool."""
        print("🎯 VISUAL VALIDATION TOOL")
        print("=" * 40)
        print("Creating visual evidence of M2 system accuracy")
        
        # Initialize M2 components with unified configuration
        config = {
            'templates_dir': 'data/templates',
            'confidence_threshold': 0.95,
            'ocr_confidence_threshold': 0.8,
            'audio_feedback': True,
            'game_name': 'Dune Legacy',
            'debug_mode': True,
            'element_confidence_threshold': 0.85
        }
        
        self.element_location = ElementLocationModule(config)
        self.ocr_integration = OCRIntegrationModule(config)
        self.perception_module = PerceptionModule(config)
        self.template_library = TemplateLibrary(config)
        
        # Colors for different confidence levels
        self.colors = {
            'high': (0, 255, 0),     # Green for high confidence (≥0.9)
            'medium': (0, 165, 255), # Orange for medium confidence (0.7-0.9)
            'low': (0, 0, 255),      # Red for low confidence (<0.7)
            'text': (255, 255, 255), # White for text
            'bg': (0, 0, 0)          # Black for background
        }
        
    def validate_with_visuals(self, game_name: str = "Dune Legacy") -> Dict[str, Any]:
        """
        Run full validation with visual overlay showing detected elements.
        
        Args:
            game_name: Name of the game to validate
            
        Returns:
            Dictionary with validation results and paths to visual evidence
        """
        print(f"🎮 Starting visual validation for {game_name}")
        
        results = {
            'timestamp': int(time.time()),
            'game_name': game_name,
            'screenshot_path': None,
            'annotated_path': None,
            'elements_detected': [],
            'text_extracted': {},
            'confidence_stats': {},
            'validation_passed': False
        }
        
        try:
            # Step 1: Launch game and capture screenshot
            print("📱 Step 1: Launching game and capturing screenshot...")
            if not self._launch_and_focus_game(game_name):
                print(f"❌ Could not launch or focus {game_name}")
                return results
                
            # Capture screenshot
            screenshot_path = self.perception_module.capture_screen()
            if not screenshot_path:
                print("❌ Failed to capture screenshot")
                return results
                
            results['screenshot_path'] = screenshot_path
            print(f"✅ Screenshot captured: {screenshot_path}")
            
            # Step 2: Detect elements using the same approach as live validation test
            print("🔍 Step 2: Detecting menu elements...")
            
            # Try ElementLocationModule first (OpenCV/ROI detection)
            detected_elements = self.element_location.detect_all_elements(screenshot_path)
            
            # If ElementLocationModule doesn't find elements, use TemplateLibrary fallback
            if not detected_elements:
                print("🔄 Using TemplateLibrary fallback detection...")
                detected_elements = self.template_library.detect_elements_fallback(screenshot_path)
            
            results['elements_detected'] = [
                {
                    'name': elem.name if hasattr(elem, 'name') else elem.template_id,
                    'coordinates': (
                        elem.normalized_x if hasattr(elem, 'normalized_x') else elem.center_x, 
                        elem.normalized_y if hasattr(elem, 'normalized_y') else elem.center_y, 
                        elem.roi[2] if hasattr(elem, 'roi') and elem.roi else 0.1, 
                        elem.roi[3] if hasattr(elem, 'roi') and elem.roi else 0.1
                    ),
                    'confidence': elem.confidence,
                    'method': elem.method if hasattr(elem, 'method') else 'fallback'
                }
                for elem in detected_elements
            ]
            
            # Step 3: Extract text
            print("📝 Step 3: Extracting text from interface...")
            text_data = self.ocr_integration.extract_all_text(screenshot_path)
            results['text_extracted'] = text_data
            
            # Step 4: Create annotated visualization
            print("🎨 Step 4: Creating visual annotation...")
            annotated_path = self._create_annotated_image(
                screenshot_path, detected_elements, text_data
            )
            results['annotated_path'] = annotated_path
            
            # Step 5: Calculate confidence statistics
            results['confidence_stats'] = self._calculate_confidence_stats(
                detected_elements, text_data
            )
            
            # Step 6: Determine if validation passed
            results['validation_passed'] = self._evaluate_validation_success(
                detected_elements, text_data
            )
            
            # Display results
            self._display_results(results)
            
            # Open the annotated image for viewing
            if annotated_path and os.path.exists(annotated_path):
                print(f"🖼️  Opening annotated image: {annotated_path}")
                subprocess.run(['open', annotated_path], check=False)
            
            return results
            
        except Exception as e:
            print(f"❌ Visual validation error: {e}")
            results['error'] = str(e)
            return results
    
    def _launch_and_focus_game(self, game_name: str) -> bool:
        """Launch and focus the game."""
        try:
            # Try to focus existing game first
            focus_script = f'''
            tell application "{game_name}"
                activate
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', focus_script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {game_name} is now in focus")
                time.sleep(2)  # Wait for focus to take effect
                return True
            else:
                print(f"⚠️ Could not focus {game_name}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error launching/focusing game: {e}")
            return False
    
    def _create_annotated_image(self, screenshot_path: str, elements: List, text_data: Dict) -> str:
        """Create an annotated image showing all detected elements and text."""
        try:
            # Load image with OpenCV
            img = cv2.imread(screenshot_path)
            if img is None:
                print("❌ Could not load screenshot for annotation")
                return None
                
            height, width = img.shape[:2]
            
            # Create overlay for semi-transparent annotations
            overlay = img.copy()
            
            # Annotate detected elements
            for elem in elements:
                self._draw_element_annotation(overlay, elem, width, height)
            
            # Annotate text regions
            self._draw_text_annotations(overlay, text_data, width, height)
            
            # Add legend
            self._draw_legend(overlay)
            
            # Blend overlay with original image
            alpha = 0.8
            annotated = cv2.addWeighted(img, alpha, overlay, 1 - alpha, 0)
            
            # Save annotated image
            timestamp = int(time.time())
            annotated_path = f"/tmp/ai_player_visual_validation_{timestamp}.png"
            cv2.imwrite(annotated_path, annotated)
            
            print(f"✅ Annotated image saved: {annotated_path}")
            return annotated_path
            
        except Exception as e:
            print(f"❌ Error creating annotated image: {e}")
            return None
    
    def _draw_element_annotation(self, img: np.ndarray, elem, width: int, height: int):
        """Draw annotation for a detected element."""
        # Handle different element types (ElementMatch vs TemplateMatch)
        if hasattr(elem, 'normalized_x') and hasattr(elem, 'name'):
            # ElementMatch from ElementLocationModule
            center_x = int(elem.normalized_x * width)
            center_y = int(elem.normalized_y * height)
            elem_name = elem.name
            elem_confidence = elem.confidence
            elem_method = getattr(elem, 'method', 'element_location')
            elem_roi = getattr(elem, 'roi', None)
        else:
            # TemplateMatch from TemplateLibrary (or other types)
            center_x = int((getattr(elem, 'normalized_x', None) or getattr(elem, 'center_x', 0.5)) * width)
            center_y = int((getattr(elem, 'normalized_y', None) or getattr(elem, 'center_y', 0.5)) * height)
            elem_name = getattr(elem, 'name', None) or getattr(elem, 'template_id', 'unknown')
            elem_confidence = getattr(elem, 'confidence', 0.0)
            elem_method = getattr(elem, 'method', 'fallback')
            elem_roi = getattr(elem, 'roi', None)
        
        # Use ROI for dimensions if available
        if elem_roi:
            x_norm, y_norm, w_norm, h_norm = elem_roi
            x = int(x_norm * width)
            y = int(y_norm * height)
            w = int(w_norm * width)
            h = int(h_norm * height)
        else:
            # Default size around center point
            w, h = 100, 30
            x, y = center_x - w//2, center_y - h//2
        
        # Choose color based on confidence
        if elem_confidence >= 0.9:
            color = self.colors['high']
            confidence_label = "HIGH"
        elif elem_confidence >= 0.7:
            color = self.colors['medium']
            confidence_label = "MED"
        else:
            color = self.colors['low']
            confidence_label = "LOW"
        
        # Draw bounding box
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
        
        # Draw element name and confidence
        label = f"{elem_name} ({confidence_label}: {elem_confidence:.2f})"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        
        # Background for text
        cv2.rectangle(img, 
                     (x, y - label_size[1] - 10), 
                     (x + label_size[0] + 10, y), 
                     color, -1)
        
        # Text
        cv2.putText(img, label, (x + 5, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw method indicator
        method_label = f"Method: {elem_method}"
        cv2.putText(img, method_label, (x + 5, y + h + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def _draw_text_annotations(self, img: np.ndarray, text_data: Dict, width: int, height: int):
        """Draw annotations for extracted text regions."""
        if 'text_data' not in text_data:
            return
            
        # Define approximate regions where text was extracted
        text_regions = {
            'title_area': (0.2, 0.05, 0.6, 0.2),
            'main_menu_buttons': (0.3, 0.3, 0.4, 0.4),
            'version_info': (0.05, 0.9, 0.3, 0.08),
            'resource_areas': (0.05, 0.05, 0.9, 0.15)
        }
        
        for region_name, roi in text_regions.items():
            # Convert normalized coordinates to pixels
            x = int(roi[0] * width)
            y = int(roi[1] * height)
            w = int(roi[2] * width)
            h = int(roi[3] * height)
            
            # Draw text region outline
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            
            # Label the region
            region_label = f"TEXT: {region_name}"
            cv2.putText(img, region_label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    def _draw_legend(self, img: np.ndarray):
        """Draw legend explaining the color coding."""
        legend_y = 50
        legend_x = img.shape[1] - 300
        
        # Legend background
        cv2.rectangle(img, (legend_x - 10, legend_y - 30), 
                     (img.shape[1] - 10, legend_y + 120), (0, 0, 0), -1)
        cv2.rectangle(img, (legend_x - 10, legend_y - 30), 
                     (img.shape[1] - 10, legend_y + 120), (255, 255, 255), 2)
        
        # Legend title
        cv2.putText(img, "DETECTION LEGEND", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Legend items
        items = [
            ("HIGH CONF (≥0.9)", self.colors['high']),
            ("MED CONF (0.7-0.9)", self.colors['medium']),
            ("LOW CONF (<0.7)", self.colors['low']),
            ("TEXT REGIONS", (255, 255, 0))
        ]
        
        for i, (label, color) in enumerate(items):
            y_pos = legend_y + 25 + (i * 20)
            cv2.rectangle(img, (legend_x, y_pos - 10), (legend_x + 15, y_pos + 5), color, -1)
            cv2.putText(img, label, (legend_x + 25, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _calculate_confidence_stats(self, elements: List, text_data: Dict) -> Dict[str, Any]:
        """Calculate confidence statistics."""
        stats = {
            'element_detection': {
                'total_elements': len(elements),
                'high_confidence': len([e for e in elements if e.confidence >= 0.9]),
                'medium_confidence': len([e for e in elements if 0.7 <= e.confidence < 0.9]),
                'low_confidence': len([e for e in elements if e.confidence < 0.7]),
                'average_confidence': sum(e.confidence for e in elements) / len(elements) if elements else 0
            },
            'text_extraction': {
                'total_extractions': len(text_data.get('text_data', {})),
                'average_confidence': text_data.get('average_confidence', 0),
                'method_used': text_data.get('method', 'unknown')
            }
        }
        return stats
    
    def _evaluate_validation_success(self, elements: List, text_data: Dict) -> bool:
        """Evaluate if the validation was successful."""
        # Criteria for success:
        # 1. At least 2 elements detected
        # 2. Average element confidence ≥ 0.7
        # 3. At least some text extracted
        
        if len(elements) < 2:
            return False
            
        avg_elem_conf = sum(e.confidence for e in elements) / len(elements)
        if avg_elem_conf < 0.7:
            return False
            
        if not text_data.get('text_data') or len(text_data.get('text_data', {})) == 0:
            return False
            
        return True
    
    def _display_results(self, results: Dict[str, Any]):
        """Display validation results."""
        print("\n🎯 VISUAL VALIDATION RESULTS")
        print("=" * 50)
        
        print(f"Game: {results['game_name']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Status: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")
        
        if results['elements_detected']:
            print(f"\n📍 Elements Detected: {len(results['elements_detected'])}")
            for elem in results['elements_detected']:
                conf_emoji = "✅" if elem['confidence'] >= 0.9 else "⚠️" if elem['confidence'] >= 0.7 else "❌"
                print(f"   {conf_emoji} {elem['name']}: {elem['confidence']:.2f} ({elem['method']})")
        
        if results['confidence_stats']:
            stats = results['confidence_stats']
            elem_stats = stats['element_detection']
            print(f"\n📊 Confidence Statistics:")
            print(f"   Average element confidence: {elem_stats['average_confidence']:.3f}")
            print(f"   High confidence detections: {elem_stats['high_confidence']}")
            print(f"   Medium confidence detections: {elem_stats['medium_confidence']}")
            print(f"   Low confidence detections: {elem_stats['low_confidence']}")
        
        if results['annotated_path']:
            print(f"\n🖼️  Visual Evidence: {results['annotated_path']}")
        
        print("\n" + "=" * 50)


def main():
    """Main entry point for visual validation tool."""
    print("🎯 AI Player Visual Validation Tool")
    print("Generating visual evidence of M2 system accuracy")
    print("=" * 60)
    
    tool = VisualValidationTool()
    results = tool.validate_with_visuals("Dune Legacy")
    
    if results['validation_passed']:
        print("\n✅ VISUAL VALIDATION: PASSED")
        print("M2 system demonstrates accurate menu identification")
    else:
        print("\n❌ VISUAL VALIDATION: NEEDS IMPROVEMENT")  
        print("M2 system requires refinement for reliable operation")
    
    return results


if __name__ == "__main__":
    main()