#!/usr/bin/env python3
"""
Interactive Button Position Finder
Helps identify the correct button positions by analyzing the actual screenshot
"""

import cv2
import numpy as np
import subprocess
import time

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def analyze_screenshot(screenshot_path):
    """Analyze screenshot to find likely button positions."""
    print("🔍 ANALYZING DUNE LEGACY SCREENSHOT")
    print("=" * 40)
    
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"❌ Could not load screenshot: {screenshot_path}")
        return
    
    height, width = img.shape[:2]
    print(f"📐 Image dimensions: {width}x{height}")
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define range for gold/yellow colors (typical for Dune Legacy buttons)
    # Gold/yellow buttons typically have hue around 15-35
    lower_gold = np.array([10, 100, 100])
    upper_gold = np.array([40, 255, 255])
    
    # Create mask for gold colors
    mask = cv2.inRange(hsv, lower_gold, upper_gold)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"🎯 Found {len(contours)} gold-colored regions")
    
    # Filter contours by size (buttons should be reasonably large)
    button_candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        
        # Filter by size - buttons should be at least 100x30 pixels and less than 500x100
        if 100 <= w <= 500 and 20 <= h <= 100 and area > 2000:
            button_candidates.append((x, y, w, h, area))
    
    # Sort by Y position (top to bottom)
    button_candidates.sort(key=lambda x: x[1])
    
    print(f"📊 Found {len(button_candidates)} button candidates:")
    
    for i, (x, y, w, h, area) in enumerate(button_candidates):
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Convert to normalized coordinates
        norm_x = center_x / width
        norm_y = center_y / height
        norm_w = w / width
        norm_h = h / height
        
        print(f"   Button {i+1}: Pixel({x:4}, {y:4}) Size({w:3}x{h:2}) Center({center_x:4}, {center_y:4}) Norm({norm_x:.3f}, {norm_y:.3f})")
    
    # Create annotated image
    annotated = img.copy()
    
    # Draw all button candidates
    for i, (x, y, w, h, area) in enumerate(button_candidates):
        color = (0, 255, 0)  # Green
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.putText(annotated, f"Btn{i+1}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw center point
        center_x = x + w // 2
        center_y = y + h // 2
        cv2.circle(annotated, (center_x, center_y), 5, (0, 0, 255), -1)
    
    # Save annotated image
    output_path = "/tmp/button_analysis.png"
    cv2.imwrite(output_path, annotated)
    print(f"📸 Analysis saved to: {output_path}")
    
    return button_candidates

def test_real_button_position(candidates, button_index=0):
    """Test clicking on a real detected button position."""
    if not candidates or button_index >= len(candidates):
        print("❌ No valid button candidate to test")
        return False
    
    x, y, w, h, area = candidates[button_index]
    center_x = x + w // 2 
    center_y = y + h // 2
    
    print(f"\n🎯 Testing detected button {button_index + 1}:")
    print(f"   Position: ({x}, {y}) Size: {w}x{h}")
    print(f"   Center: ({center_x}, {center_y})")
    
    # Focus game
    audio_signal("Focusing game for real button test")
    focus_script = '''
    tell application "Dune Legacy"
        activate  
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Game focused")
    else:
        print("⚠️ Focus uncertain")
    
    time.sleep(2)
    
    # Click the button
    audio_signal(f"Clicking detected button {button_index + 1}")
    click_script = f'''
    tell application "System Events"
        click at {{{center_x}, {center_y}}}
    end tell
    '''
    
    # Capture before
    subprocess.run(['screencapture', '-x', '/tmp/before_real_click.png'], capture_output=True)
    
    result = subprocess.run(['osascript', '-e', click_script], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Click executed")
        audio_signal("Click executed")
        
        time.sleep(1)
        
        # Capture after
        subprocess.run(['screencapture', '-x', '/tmp/after_real_click.png'], capture_output=True)
        
        return True
    else:
        print("❌ Click failed")
        audio_signal("Click failed")
        return False

def main():
    """Main button analysis and test."""
    audio_signal("Starting button position analysis")
    
    # Capture fresh screenshot
    subprocess.run(['screencapture', '-x', '/tmp/dune_legacy_analysis.png'], capture_output=True)
    
    # Analyze for button positions
    candidates = analyze_screenshot('/tmp/dune_legacy_analysis.png')
    
    if candidates:
        print(f"\n✅ Found {len(candidates)} button candidates")
        audio_signal(f"Found {len(candidates)} button candidates")
        
        # Test the first candidate (likely topmost button)
        if len(candidates) > 0:
            print(f"\n🧪 Testing first button candidate...")
            test_real_button_position(candidates, 0)
    else:
        print("❌ No button candidates found")
        audio_signal("No buttons detected")

if __name__ == "__main__":
    main()