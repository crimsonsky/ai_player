#!/usr/bin/env python3
"""
Enhanced Button Coordinate Validation
Tests multiple button positions and provides detailed feedback

UPDATED: Uses working pyobjc mouse control system
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

def capture_screenshot(path):
    """Capture current screenshot."""
    try:
        subprocess.run(['screencapture', '-x', path], capture_output=True, timeout=5)
        return True
    except:
        return False

def test_button_click(button_name, coordinates, mouse, screenshot_before=None):
    """Test clicking a specific button and validate response."""
    x, y = coordinates
    
    print(f"\n🎯 TESTING: {button_name}")
    print(f"   Target coordinates: ({x}, {y})")
    
    # Show current mouse position
    current_x, current_y = mouse.get_position()
    print(f"   Current mouse: ({current_x:.0f}, {current_y:.0f})")
    
    # Take before screenshot if requested
    if screenshot_before:
        capture_screenshot(screenshot_before)
        print(f"📸 Before screenshot: {screenshot_before}")
    
    # Perform the click
    print(f"🖱️ Clicking {button_name}...")
    audio_signal(f"Clicking {button_name}")
    
    success = mouse.left_click(x, y)
    
    if success:
        print(f"✅ Click executed successfully at ({x}, {y})")
        
        # Wait for UI response
        time.sleep(1)
        
        # Take after screenshot
        after_path = f"/tmp/after_{button_name.lower().replace(' ', '_')}.png"
        capture_screenshot(after_path)
        print(f"📸 After screenshot: {after_path}")
        
        # Ask user for validation
        print(f"👀 VALIDATION REQUIRED:")
        print(f"   Did clicking {button_name} produce the expected result?")
        print(f"   Compare screenshots to verify UI change")
        
        return True
    else:
        print(f"❌ Click failed for {button_name}")
        audio_signal(f"Click failed for {button_name}")
        return False

def main():
    """Test multiple button coordinates from the current detection system."""
    
    print("🧪 ENHANCED BUTTON COORDINATE VALIDATION")
    print("=" * 50)
    print("Testing button positions using pyobjc mouse control")
    print()
    
    # Initialize mouse controller
    mouse = MouseController()
    print("🖱️ Mouse controller initialized")
    
    # Get screen dimensions from latest screenshot
    screenshot_path = "/tmp/dune_legacy_current.png"
    width, height = get_screen_dimensions(screenshot_path)
    
    if not width or not height:
        print("❌ Could not get screen dimensions")
        print("   Make sure to take a screenshot first:")
        print("   screencapture -x /tmp/dune_legacy_current.png")
        return
        
    print(f"📐 Screen dimensions: {width}x{height}")
    
    # Button definitions from M2 perception system
    # These are the current ROI coordinates we're validating
    buttons = {
        "Options": (0.35, 0.55, 0.30, 0.08),
        "Single Player": (0.35, 0.45, 0.30, 0.08), 
        "Multi Player": (0.35, 0.50, 0.30, 0.08),
        "Map Editor": (0.35, 0.60, 0.30, 0.08),
        "Replay": (0.35, 0.65, 0.30, 0.08),
        "Quit": (0.35, 0.70, 0.30, 0.08)
    }
    
    print(f"🎯 Buttons to test: {len(buttons)}")
    for name in buttons.keys():
        print(f"   • {name}")
    
    # Focus Dune Legacy
    print("\n🎮 Focusing Dune Legacy...")
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Dune Legacy focused successfully")
    else:
        print(f"⚠️ Focus may have failed: {result.stderr}")
    
    time.sleep(2)
    
    # Test each button
    for button_name, roi in buttons.items():
        x_norm, y_norm, w_norm, h_norm = roi
        
        # Convert to pixel coordinates  
        x = int(x_norm * width)
        y = int(y_norm * height)
        w = int(w_norm * width)
        h = int(h_norm * height)
        
        # Calculate center
        center_x = x + w // 2
        center_y = y + h // 2
        
        print(f"\n{'='*30}")
        print(f"ROI: {roi}")
        print(f"Pixel area: ({x}, {y}) {w}x{h}")
        print(f"Center: ({center_x}, {center_y})")
        
        # Ask user if they want to test this button
        print(f"\n⚠️ Ready to test {button_name}")
        print("   Press Enter to test, 's' to skip, 'q' to quit")
        
        user_input = input(">>> ").strip().lower()
        
        if user_input == 'q':
            print("🛑 Testing aborted by user")
            break
        elif user_input == 's':
            print(f"⏭️ Skipping {button_name}")
            continue
        
        # Test the button
        before_path = f"/tmp/before_{button_name.lower().replace(' ', '_')}.png"
        test_button_click(button_name, (center_x, center_y), mouse, before_path)
        
        # Brief pause between tests
        time.sleep(1)
    
    print("\n🏁 COORDINATE VALIDATION COMPLETE")
    print("Review the screenshot pairs to determine coordinate accuracy:")
    print("   /tmp/before_*.png vs /tmp/after_*.png")
    
    # Final summary
    audio_signal("Coordinate validation complete")

if __name__ == "__main__":
    main()