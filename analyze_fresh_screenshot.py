#!/usr/bin/env python3
"""
Fresh Screenshot Analysis Tool
Analyze the fresh screenshot to identify actual button positions

This will help us understand the real menu layout.
"""

import cv2
import numpy as np

def analyze_fresh_screenshot():
    """Analyze the fresh screenshot to understand button layout."""
    
    print("🔍 FRESH SCREENSHOT ANALYSIS")
    print("=" * 40)
    
    screenshot_path = "/tmp/dune_legacy_fresh.png"
    
    try:
        img = cv2.imread(screenshot_path)
        
        if img is None:
            print("❌ Could not load fresh screenshot")
            return
            
        height, width = img.shape[:2]
        print(f"✅ Loaded fresh screenshot: {width}x{height}")
        
        # Create analysis image with grid overlay
        analysis_img = img.copy()
        
        # Draw grid lines for coordinate reference
        grid_color = (100, 100, 100)  # Gray
        grid_spacing = 100
        
        # Vertical lines
        for x in range(0, width, grid_spacing):
            cv2.line(analysis_img, (x, 0), (x, height), grid_color, 1)
            if x % 200 == 0:  # Label every 200 pixels
                cv2.putText(analysis_img, str(x), (x+5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, grid_color, 1)
        
        # Horizontal lines
        for y in range(0, height, grid_spacing):
            cv2.line(analysis_img, (0, y), (width, y), grid_color, 1)
            if y % 200 == 0:  # Label every 200 pixels
                cv2.putText(analysis_img, str(y), (5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, grid_color, 1)
        
        # Mark the center
        center_x, center_y = width // 2, height // 2
        cv2.circle(analysis_img, (center_x, center_y), 10, (0, 255, 0), 2)
        cv2.putText(analysis_img, f"CENTER ({center_x}, {center_y})", 
                    (center_x - 80, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Mark our previous wrong click
        wrong_click_x, wrong_click_y = 1720, 849
        cv2.circle(analysis_img, (wrong_click_x, wrong_click_y), 15, (0, 0, 255), 3)
        cv2.putText(analysis_img, f"WRONG CLICK ({wrong_click_x}, {wrong_click_y})", 
                    (wrong_click_x - 120, wrong_click_y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Draw the old ROI that was wrong
        old_roi_x = int(0.35 * width)
        old_roi_y = int(0.55 * height)
        old_roi_w = int(0.30 * width)
        old_roi_h = int(0.08 * height)
        
        cv2.rectangle(analysis_img, (old_roi_x, old_roi_y), (old_roi_x + old_roi_w, old_roi_y + old_roi_h), 
                      (255, 0, 0), 2)
        cv2.putText(analysis_img, "OLD WRONG ROI", 
                    (old_roi_x, old_roi_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Save analysis image
        analysis_path = "/tmp/screenshot_analysis.png"
        cv2.imwrite(analysis_path, analysis_img)
        
        print(f"💾 Analysis image saved: {analysis_path}")
        print(f"\n📊 SCREENSHOT DETAILS:")
        print(f"   Resolution: {width}x{height}")
        print(f"   Center: ({center_x}, {center_y})")
        print(f"   Previous wrong click: ({wrong_click_x}, {wrong_click_y})")
        print(f"   Wrong click normalized: ({wrong_click_x/width:.4f}, {wrong_click_y/height:.4f})")
        
        # Suggest typical menu button locations
        print(f"\n🎮 TYPICAL MENU ANALYSIS:")
        print(f"   If this is a centered vertical menu:")
        
        # Estimate menu area (typically centered)
        menu_center_x = center_x
        menu_start_y = height // 3  # Menus often start 1/3 down
        button_height = 60
        button_spacing = 80
        
        buttons = ["Single Player", "Multi Player", "Options", "Map Editor", "Replay", "Quit"]
        
        print(f"   Estimated button positions (center points):")
        for i, button in enumerate(buttons):
            est_y = menu_start_y + i * button_spacing
            print(f"   {button:15} | Center: ({menu_center_x:4d}, {est_y:4d}) | Normalized: ({menu_center_x/width:.4f}, {est_y/height:.4f})")
            
            # Draw estimated positions on analysis image
            cv2.circle(analysis_img, (menu_center_x, est_y), 8, (0, 255, 255), 2)  # Yellow circles
            cv2.putText(analysis_img, button[:8], 
                        (menu_center_x + 15, est_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Save updated analysis
        cv2.imwrite(analysis_path, analysis_img)
        
        print(f"\n📸 Open these files to examine:")
        print(f"   Original: {screenshot_path}")
        print(f"   Analysis: {analysis_path}")
        
        # Open the analysis image
        print(f"\n🔍 Opening analysis image...")
        import subprocess
        subprocess.run(['open', analysis_path], capture_output=True)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    analyze_fresh_screenshot()