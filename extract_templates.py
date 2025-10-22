#!/usr/bin/env python3
"""
Template Extraction Tool for M2 Perception Module
Extracts individual button templates from Dune Legacy main menu screenshot
"""

import cv2
import numpy as np
import os
from PIL import Image
import json
from typing import List, Tuple, Dict


class TemplateExtractor:
    """Extract and save template images for OpenCV matching."""
    
    def __init__(self):
        self.templates_dir = "/Users/amir/projects/ai_player/data/templates"
        self.raw_dir = os.path.join(self.templates_dir, "raw")
        self.processed_dir = os.path.join(self.templates_dir, "processed")
        
        # Ensure directories exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def extract_templates_from_screenshot(self, screenshot_path: str):
        """Extract template images from full screenshot."""
        print("🎯 TEMPLATE EXTRACTION - M2 Perception Refinement")
        print("=" * 50)
        
        # Load the screenshot
        img = cv2.imread(screenshot_path)
        if img is None:
            print(f"❌ Could not load screenshot: {screenshot_path}")
            return
            
        height, width = img.shape[:2]
        print(f"📐 Screenshot dimensions: {width}x{height}")
        
        # Define template regions based on typical Dune Legacy menu layout
        # These coordinates are educated guesses - we'll refine them
        template_regions = {
            "MENU_HDR_title": {
                "name": "Dune Legacy Title",
                "roi": (0.25, 0.15, 0.50, 0.15),  # Upper center area
                "description": "Main title with blue background and gold border"
            },
            "MENU_BTN_single_player": {
                "name": "Single Player", 
                "roi": (0.35, 0.35, 0.30, 0.08),  # First button
                "description": "Single player button - gold with text"
            },
            "MENU_BTN_multiplayer": {
                "name": "Multiplayer",
                "roi": (0.35, 0.45, 0.30, 0.08),  # Second button  
                "description": "Multiplayer button - gold with text"
            },
            "MENU_BTN_options": {
                "name": "Options",
                "roi": (0.35, 0.55, 0.30, 0.08),  # Third button
                "description": "Options button - gold with text"
            },
            "MENU_BTN_map_editor": {
                "name": "Map Editor", 
                "roi": (0.35, 0.65, 0.30, 0.08),  # Fourth button
                "description": "Map editor button - gold with text"
            },
            "MENU_BTN_replay": {
                "name": "Replay",
                "roi": (0.35, 0.75, 0.30, 0.08),  # Fifth button
                "description": "Replay button - gold with text"
            },
            "MENU_BTN_quit": {
                "name": "Quit",
                "roi": (0.35, 0.85, 0.30, 0.08),  # Sixth button
                "description": "Quit button - gold with text"
            }
        }
        
        extracted_templates = {}
        
        for template_id, template_info in template_regions.items():
            print(f"\n🔍 Extracting {template_id}: {template_info['name']}")
            
            # Convert normalized coordinates to pixel coordinates
            x_norm, y_norm, w_norm, h_norm = template_info['roi']
            x = int(x_norm * width)
            y = int(y_norm * height) 
            w = int(w_norm * width)
            h = int(h_norm * height)
            
            print(f"   📏 Pixel coordinates: ({x}, {y}) size: {w}x{h}")
            
            # Extract the region
            template_img = img[y:y+h, x:x+w]
            
            if template_img.size == 0:
                print(f"   ❌ Empty template region for {template_id}")
                continue
                
            # Save raw template
            raw_path = os.path.join(self.raw_dir, f"{template_id}.png")
            cv2.imwrite(raw_path, template_img)
            print(f"   ✅ Raw template saved: {raw_path}")
            
            # Process template for better matching
            processed_img = self._process_template(template_img)
            processed_path = os.path.join(self.processed_dir, f"{template_id}.png")
            cv2.imwrite(processed_path, processed_img)
            print(f"   ✅ Processed template saved: {processed_path}")
            
            # Store template metadata
            extracted_templates[template_id] = {
                "name": template_info['name'],
                "description": template_info['description'],
                "roi": template_info['roi'],
                "raw_path": raw_path,
                "processed_path": processed_path,
                "pixel_coordinates": (x, y, w, h),
                "confidence_threshold": 0.85
            }
        
        # Save template library JSON
        library_path = os.path.join(self.templates_dir, "template_library.json")
        template_library = {
            "version": "2.0",
            "extracted_from": screenshot_path,
            "extraction_timestamp": "2025-10-22",
            "templates": extracted_templates
        }
        
        with open(library_path, 'w') as f:
            json.dump(template_library, f, indent=2)
            
        print(f"\n✅ Template library saved: {library_path}")
        print(f"📊 Extracted {len(extracted_templates)} templates")
        
        return extracted_templates
    
    def _process_template(self, img: np.ndarray) -> np.ndarray:
        """Process template image for better matching accuracy."""
        # Convert to grayscale for better matching stability
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
            
        # Apply slight gaussian blur to reduce noise
        processed = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Enhance contrast
        processed = cv2.convertScaleAbs(processed, alpha=1.2, beta=10)
        
        return processed
    
    def preview_templates(self, screenshot_path: str):
        """Preview template extraction regions before saving."""
        img = cv2.imread(screenshot_path)
        if img is None:
            return
            
        # Create preview with bounding boxes
        preview = img.copy()
        height, width = img.shape[:2]
        
        # Draw template regions
        template_regions = {
            "Title": (0.25, 0.15, 0.50, 0.15, (255, 0, 0)),  # Blue
            "Single Player": (0.35, 0.35, 0.30, 0.08, (0, 255, 0)),  # Green
            "Multiplayer": (0.35, 0.45, 0.30, 0.08, (0, 255, 0)),
            "Options": (0.35, 0.55, 0.30, 0.08, (0, 255, 0)),
            "Map Editor": (0.35, 0.65, 0.30, 0.08, (0, 255, 0)),
            "Replay": (0.35, 0.75, 0.30, 0.08, (0, 255, 0)),
            "Quit": (0.35, 0.85, 0.30, 0.08, (0, 255, 0))
        }
        
        for name, (x_norm, y_norm, w_norm, h_norm, color) in template_regions.items():
            x = int(x_norm * width)
            y = int(y_norm * height)
            w = int(w_norm * width) 
            h = int(h_norm * height)
            
            # Draw rectangle
            cv2.rectangle(preview, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            cv2.putText(preview, name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Save preview
        preview_path = "/tmp/template_extraction_preview.png"
        cv2.imwrite(preview_path, preview)
        print(f"📸 Template extraction preview saved: {preview_path}")
        
        return preview_path


def main():
    """Main entry point for template extraction."""
    extractor = TemplateExtractor()
    
    screenshot_path = "/tmp/dune_legacy_full_menu.png"
    
    # Check if screenshot exists
    if not os.path.exists(screenshot_path):
        print(f"❌ Screenshot not found: {screenshot_path}")
        print("Please capture a Dune Legacy main menu screenshot first")
        return
    
    # Preview extraction regions
    print("📸 Creating template extraction preview...")
    preview_path = extractor.preview_templates(screenshot_path)
    if preview_path:
        print(f"Opening preview: {preview_path}")
        os.system(f"open {preview_path}")
    
    # Wait for user confirmation
    input("\n⏳ Review the preview and press Enter to proceed with extraction...")
    
    # Extract templates
    templates = extractor.extract_templates_from_screenshot(screenshot_path)
    
    if templates:
        print("\n🎉 Template extraction completed successfully!")
        print("Next steps:")
        print("1. Review extracted templates in data/templates/")
        print("2. Implement TM_CCOEFF_NORMED matching in perception_module.py")
        print("3. Test with live game detection")
    else:
        print("\n❌ Template extraction failed")


if __name__ == "__main__":
    main()