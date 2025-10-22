#!/usr/bin/env python3
"""
Visual Click Analysis Tool
Analyze where we actually clicked vs where buttons are located

This will help us understand the coordinate mapping error.
"""

import cv2
import numpy as np

def analyze_click_results():
    """Analyze the before/after screenshots to understand the click error."""
    
    print("🔍 VISUAL CLICK ANALYSIS")
    print("=" * 40)
    
    # Load screenshots
    before_path = "/tmp/dune_legacy_current.png"
    after_path = "/tmp/after_click.png"
    
    try:
        before_img = cv2.imread(before_path)
        after_img = cv2.imread(after_path)
        
        if before_img is None or after_img is None:
            print("❌ Could not load screenshots")
            return
            
        print(f"✅ Loaded screenshots: {before_img.shape[:2]}")
        
        # Our click coordinates
        click_x, click_y = 1720, 849
        
        # Create visualization
        vis_img = before_img.copy()
        
        # Draw our click point
        cv2.circle(vis_img, (click_x, click_y), 20, (0, 0, 255), 3)  # Red circle
        cv2.circle(vis_img, (click_x, click_y), 5, (0, 0, 255), -1)  # Red dot
        
        # Add text label
        cv2.putText(vis_img, f"CLICKED: ({click_x}, {click_y})", 
                    (click_x - 100, click_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw the ROI we thought was "Options"
        # roi: (0.35, 0.55, 0.30, 0.08) 
        height, width = before_img.shape[:2]
        roi_x = int(0.35 * width)
        roi_y = int(0.55 * height) 
        roi_w = int(0.30 * width)
        roi_h = int(0.08 * height)
        
        # Draw ROI rectangle
        cv2.rectangle(vis_img, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (255, 0, 0), 3)  # Blue rectangle
        cv2.putText(vis_img, "EXPECTED 'OPTIONS' ROI", 
                    (roi_x, roi_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Save visualization
        output_path = "/tmp/click_analysis.png"
        cv2.imwrite(output_path, vis_img)
        print(f"💾 Click analysis saved to: {output_path}")
        
        # Analysis
        print("\n📊 COORDINATE ANALYSIS:")
        print(f"   Screen size: {width}x{height}")
        print(f"   Click point: ({click_x}, {click_y})")
        print(f"   Expected ROI: ({roi_x}, {roi_y}) {roi_w}x{roi_h}")
        print(f"   ROI center: ({roi_x + roi_w//2}, {roi_y + roi_h//2})")
        
        # Check if click was inside ROI
        if (roi_x <= click_x <= roi_x + roi_w and 
            roi_y <= click_y <= roi_y + roi_h):
            print("✅ Click was inside expected ROI")
        else:
            print("❌ Click was OUTSIDE expected ROI")
            
        # Distance from ROI center
        roi_center_x = roi_x + roi_w // 2
        roi_center_y = roi_y + roi_h // 2
        distance = ((click_x - roi_center_x)**2 + (click_y - roi_center_y)**2)**0.5
        print(f"   Distance from ROI center: {distance:.1f} pixels")
        
        # Relative position analysis
        print(f"\n🎯 RELATIVE POSITION:")
        print(f"   Click normalized: ({click_x/width:.4f}, {click_y/height:.4f})")
        print(f"   ROI normalized: ({roi_x/width:.4f}, {roi_y/height:.4f})")
        
        # Compare with typical menu layouts
        print(f"\n🎮 MENU ANALYSIS:")
        print(f"   If this is a vertical menu, click y={click_y} suggests:")
        
        # Estimate button positions based on typical menu layout
        estimated_button_height = 60  # Typical button height
        estimated_spacing = 80       # Typical spacing between buttons
        
        # If Single Player is around y=849, estimate other buttons
        single_player_y = click_y
        print(f"   Single Player (clicked): y ≈ {single_player_y}")
        print(f"   Multi Player: y ≈ {single_player_y + estimated_spacing}")
        print(f"   Options: y ≈ {single_player_y + 2*estimated_spacing}")
        print(f"   Map Editor: y ≈ {single_player_y + 3*estimated_spacing}")
        print(f"   Replay: y ≈ {single_player_y + 4*estimated_spacing}")
        print(f"   Quit: y ≈ {single_player_y + 5*estimated_spacing}")
        
        print(f"\n📸 Open the analysis image to see visual representation:")
        print(f"   {output_path}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    analyze_click_results()