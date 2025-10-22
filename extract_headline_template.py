#!/usr/bin/env python3
"""
Dune Legacy Headline Template Extractor
Extracts the 'Dune Legacy' headline template for Visual Anchor classification
"""

import cv2
import numpy as np
import subprocess
import os
from pathlib import Path

def extract_dune_legacy_headline():
    """Extract Dune Legacy headline template from main menu screenshot."""
    
    screenshot_path = "/tmp/dune_legacy_main_menu_for_headline.png"
    
    if not os.path.exists(screenshot_path):
        print("❌ Screenshot not found. Taking new screenshot...")
        subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], capture_output=True)
        subprocess.run(['sleep', '2'], capture_output=True)
        subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True)
    
    # Load screenshot
    img = cv2.imread(screenshot_path)
    if img is None:
        print("❌ Could not load screenshot")
        return False
    
    print(f"📸 Loaded screenshot: {img.shape}")
    
    # Based on game observations, the Dune Legacy headline is typically:
    # - Near the top center of the screen
    # - Large golden/yellow text
    # - Positioned around 50% width, 10-20% height
    
    height, width = img.shape[:2]
    
    # Define headline ROI (normalized coordinates)
    # Typical position: center-top area
    headline_x_norm = 0.35  # Start at 35% width
    headline_y_norm = 0.05  # Start at 5% height 
    headline_w_norm = 0.30  # Width of 30%
    headline_h_norm = 0.15  # Height of 15%
    
    # Convert to pixel coordinates
    x = int(headline_x_norm * width)
    y = int(headline_y_norm * height)
    w = int(headline_w_norm * width)
    h = int(headline_h_norm * height)
    
    print(f"🎯 Headline ROI: ({x}, {y}, {w}, {h})")
    
    # Extract headline region
    headline_region = img[y:y+h, x:x+w]
    
    # Save the headline template
    templates_dir = Path("data/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    headline_template_path = templates_dir / "dune_legacy_headline.png"
    cv2.imwrite(str(headline_template_path), headline_region)
    
    print(f"💾 Headline template saved: {headline_template_path}")
    
    # Also save a debug version with ROI marked
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(debug_img, "DUNE LEGACY HEADLINE", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    debug_path = "/tmp/headline_extraction_debug.png"
    cv2.imwrite(debug_path, debug_img)
    print(f"🖼️ Debug visualization: {debug_path}")
    
    # Update template library JSON
    update_template_library(headline_template_path, headline_x_norm, headline_y_norm, 
                          headline_w_norm, headline_h_norm)
    
    return True

def update_template_library(template_path, x_norm, y_norm, w_norm, h_norm):
    """Update template library with new Dune Legacy headline template."""
    
    import json
    from pathlib import Path
    
    library_file = Path("data/templates/template_library.json")
    
    # Load existing library or create new
    if library_file.exists():
        with open(library_file, 'r') as f:
            library = json.load(f)
    else:
        library = {}
    
    # Ensure templates key exists
    if "templates" not in library:
        library["templates"] = {}
    
    # Add headline template
    headline_template = {
        "name": "Dune Legacy Headline",
        "image_path": str(template_path),
        "roi": [x_norm, y_norm, w_norm, h_norm],
        "confidence_threshold": 0.85,
        "element_type": "visual_anchor",
        "interactive": False,
        "description": "Main game title - Visual Anchor, not clickable"
    }
    
    library["templates"]["VISUAL_ANCHOR_HEADLINE"] = headline_template
    
    # Save updated library
    with open(library_file, 'w') as f:
        json.dump(library, f, indent=2)
    
    print(f"📚 Template library updated: {library_file}")
    print(f"   Added: VISUAL_ANCHOR_HEADLINE")

def main():
    """Extract Dune Legacy headline template for Visual Anchor classification."""
    
    print("🏷️ DUNE LEGACY HEADLINE TEMPLATE EXTRACTION")
    print("=" * 50)
    print("Objective: Create Visual Anchor template for 'Dune Legacy' headline")
    print("Purpose: Separate headline from functional buttons in perception fusion")
    print()
    
    success = extract_dune_legacy_headline()
    
    if success:
        print("\n✅ HEADLINE TEMPLATE EXTRACTION COMPLETE")
        print("📚 Template added to library as VISUAL_ANCHOR_HEADLINE")
        print("🎯 Classification: Visual Anchor (non-clickable)")
        print("🔗 Ready for DVC versioning and perception fusion testing")
    else:
        print("\n❌ HEADLINE TEMPLATE EXTRACTION FAILED")
        
    return success

if __name__ == "__main__":
    main()