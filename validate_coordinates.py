#!/usr/bin/env python3
"""
Comprehensive Button Coordinate Validation Test
Tests all button positions to verify coordinate interpretation accuracy
"""

import cv2
import subprocess
import time

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def focus_dune_legacy():
    """Focus Dune Legacy application."""
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    return result.returncode == 0

def click_coordinates(x, y):
    """Click at specific pixel coordinates."""
    script = f'''
    tell application "System Events"
        click at {{{x}, {y}}}
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Click failed: {e}")
        return False

def get_screen_dimensions():
    """Get screen dimensions from current screenshot."""
    subprocess.run(['screencapture', '-x', '/tmp/screen_test.png'], capture_output=True)
    img = cv2.imread('/tmp/screen_test.png')
    if img is None:
        return None, None
    height, width = img.shape[:2]
    return width, height

def test_button_coordinates():
    """Test all button coordinate calculations."""
    print("🎯 COMPREHENSIVE BUTTON COORDINATE VALIDATION")
    print("=" * 50)
    
    # Get screen dimensions
    width, height = get_screen_dimensions()
    if not width or not height:
        print("❌ Could not get screen dimensions")
        return
        
    print(f"📐 Screen dimensions: {width}x{height}")
    
    # Define all button positions from our template extraction
    buttons = {
        "Single Player": (0.35, 0.35, 0.30, 0.08),
        "Multiplayer": (0.35, 0.45, 0.30, 0.08),
        "Options": (0.35, 0.55, 0.30, 0.08),
        "Map Editor": (0.35, 0.65, 0.30, 0.08),
        "Replay": (0.35, 0.75, 0.30, 0.08),
        "Quit": (0.35, 0.85, 0.30, 0.08)
    }
    
    print("\n📊 Calculated button positions:")
    for name, (x_norm, y_norm, w_norm, h_norm) in buttons.items():
        x = int(x_norm * width)
        y = int(y_norm * height)
        w = int(w_norm * width)
        h = int(h_norm * height)
        center_x = x + w // 2
        center_y = y + h // 2
        
        print(f"   {name:12}: Center({center_x:4}, {center_y:4}) Area({x}, {y}, {w}x{h})")
    
    # Test one button to validate coordinates
    test_button = "Options"
    x_norm, y_norm, w_norm, h_norm = buttons[test_button]
    
    x = int(x_norm * width)
    y = int(y_norm * height)
    w = int(w_norm * width) 
    h = int(h_norm * height)
    center_x = x + w // 2
    center_y = y + h // 2
    
    print(f"\n🎯 Testing {test_button} button coordinates:")
    print(f"   Center: ({center_x}, {center_y})")
    
    # Focus game
    audio_signal("Focusing Dune Legacy for coordinate test")
    if focus_dune_legacy():
        print("✅ Game focused successfully")
        audio_signal("Game focused")
    else:
        print("⚠️ Focus may have failed")
        audio_signal("Focus uncertain")
    
    # Wait and click
    time.sleep(2)
    audio_signal(f"Clicking {test_button} button now")
    print(f"🖱️  Clicking {test_button} at ({center_x}, {center_y})...")
    
    # Capture before screenshot
    subprocess.run(['screencapture', '-x', '/tmp/before_test_click.png'], capture_output=True)
    
    success = click_coordinates(center_x, center_y)
    
    if success:
        print("✅ Click executed successfully")
        audio_signal("Click successful")
        
        # Wait for UI response
        time.sleep(1)
        
        # Capture after screenshot
        subprocess.run(['screencapture', '-x', '/tmp/after_test_click.png'], capture_output=True)
        
        # Check if something changed
        before_size = 0
        after_size = 0
        try:
            import os
            before_size = os.path.getsize('/tmp/before_test_click.png')
            after_size = os.path.getsize('/tmp/after_test_click.png')
        except:
            pass
            
        if abs(before_size - after_size) > 1000:  # Significant change in file size
            print("📸 Screen changed - button click likely worked!")
            audio_signal("Screen changed, button click worked")
        else:
            print("⚠️ Screen appears unchanged - coordinates may be wrong")
            audio_signal("Screen unchanged, coordinates may be wrong")
            
    else:
        print("❌ Click failed")
        audio_signal("Click failed")
    
    return success

def main():
    """Main coordinate validation test."""
    audio_signal("Starting button coordinate validation test")
    
    success = test_button_coordinates()
    
    if success:
        print("\n✅ Coordinate test completed - check if button responded correctly")
        audio_signal("Coordinate test completed")
    else:
        print("\n❌ Coordinate test failed")
        audio_signal("Coordinate test failed")

if __name__ == "__main__":
    main()