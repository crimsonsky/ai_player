#!/usr/bin/env python3
"""
Test Coordinate Interpretation by Clicking Detected Button
Updated to use working pyobjc mouse control system
"""

import cv2
import subprocess
import time
from mouse_control import MouseController

def get_screen_dimensions(screenshot_path):
    """Get screen dimensions from screenshot."""
    img = cv2.imread(screenshot_path)
    if img is None:
        return None, None
    height, width = img.shape[:2]
    return width, height

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def click_coordinates(x, y, mouse_controller):
    """Click at specific pixel coordinates using pyobjc mouse control."""
    try:
        print(f"🖱️ Moving to ({x}, {y}) and clicking...")
        success = mouse_controller.left_click(x, y)
        if success:
            print(f"✅ Successfully clicked at ({x}, {y})")
            return True
        else:
            print(f"❌ Failed to click at ({x}, {y})")
            return False
    except Exception as e:
        print(f"❌ Click failed: {e}")
        return False

def main():
    """Test clicking the Options button based on current coordinate calculations."""
    screenshot_path = "/tmp/dune_legacy_current.png"
    
    # Initialize mouse controller
    mouse = MouseController()
    print("🖱️ Mouse controller initialized - using pyobjc CoreGraphics")
    
    # Get screen dimensions
    width, height = get_screen_dimensions(screenshot_path)
    if not width or not height:
        print("❌ Could not get screen dimensions")
        return
        
    print(f"📐 Screen dimensions: {width}x{height}")
    
    # Current "Options" button coordinates from template extraction
    # roi: (0.35, 0.55, 0.30, 0.08) - normalized coordinates
    x_norm, y_norm, w_norm, h_norm = 0.35, 0.55, 0.30, 0.08
    
    # Convert to pixel coordinates
    x = int(x_norm * width)
    y = int(y_norm * height)
    w = int(w_norm * width)
    h = int(h_norm * height)
    
    # Calculate center of button
    center_x = x + w // 2
    center_y = y + h // 2
    
    print(f"🎯 Calculated Options button area:")
    print(f"   Top-left: ({x}, {y})")
    print(f"   Size: {w}x{h}")
    print(f"   Center: ({center_x}, {center_y})")
    
    # Show current mouse position
    current_x, current_y = mouse.get_position()
    print(f"📍 Current mouse position: ({current_x:.0f}, {current_y:.0f})")
    
    # Ask user to confirm
    print(f"\n⚠️  About to click at coordinates ({center_x}, {center_y})")
    print("Make sure Dune Legacy is visible and active!")
    
    # Focus Dune Legacy first
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    print("🎮 Focusing Dune Legacy...")
    audio_signal("Focusing Dune Legacy")
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Dune Legacy focused successfully")
        audio_signal("Game focused")
    else:
        print(f"⚠️ Focus may have failed: {result.stderr}")
        audio_signal("Focus uncertain")
    
    time.sleep(2)  # Give more time for focus
    
    # Attempt the click automatically after focus
    print(f"🖱️  Clicking at ({center_x}, {center_y}) in 3 seconds...")
    audio_signal("Clicking Options button in 3 seconds")
    time.sleep(3)
    
    success = click_coordinates(center_x, center_y, mouse)
    
    if success:
        print("✅ Click executed successfully")
        print("👀 OBSERVE: Did the Options menu open? If not, coordinates are wrong!")
        audio_signal("Click completed - check if Options menu opened")
    else:
        print("❌ Click failed")
        audio_signal("Click failed")
    
    # Show final mouse position
    final_x, final_y = mouse.get_position()
    print(f"📍 Final mouse position: ({final_x:.0f}, {final_y:.0f})")
    
    # Wait a moment then capture result
    time.sleep(2)
    subprocess.run(['screencapture', '-x', '/tmp/after_click.png'], capture_output=True)
    print("📸 Post-click screenshot saved to /tmp/after_click.png")

if __name__ == "__main__":
    main()