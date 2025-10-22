#!/usr/bin/env python3
"""
Corrected Button Position Test
Tests realistic button positions based on common game menu layouts
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

def test_corrected_coordinates():
    """Test more realistic button coordinates for Dune Legacy."""
    print("🎯 TESTING CORRECTED BUTTON COORDINATES")
    print("=" * 50)
    
    # Get screen dimensions
    subprocess.run(['screencapture', '-x', '/tmp/coord_test.png'], capture_output=True)
    img = cv2.imread('/tmp/coord_test.png')
    if img is None:
        print("❌ Could not capture screen")
        return
    
    height, width = img.shape[:2]
    print(f"📐 Screen dimensions: {width}x{height}")
    
    # More realistic button coordinates for Dune Legacy
    # Based on typical RTS game menu layouts - smaller, more centered
    corrected_buttons = {
        "Single Player": (0.40, 0.42, 0.20, 0.04),  # More centered, smaller
        "Multiplayer": (0.40, 0.47, 0.20, 0.04),    # 5% spacing between buttons
        "Options": (0.40, 0.52, 0.20, 0.04),        # Target button for test
        "Map Editor": (0.40, 0.57, 0.20, 0.04),
        "Replay": (0.40, 0.62, 0.20, 0.04),
        "Quit": (0.40, 0.67, 0.20, 0.04)
    }
    
    print("\n📊 Corrected button positions:")
    for name, (x_norm, y_norm, w_norm, h_norm) in corrected_buttons.items():
        x = int(x_norm * width)
        y = int(y_norm * height)
        w = int(w_norm * width)
        h = int(h_norm * height)
        center_x = x + w // 2
        center_y = y + h // 2
        
        print(f"   {name:12}: Center({center_x:4}, {center_y:4}) Area({x:4}, {y:4}, {w:3}x{h:2})")
    
    # Test the Options button with corrected coordinates
    test_button = "Options"
    x_norm, y_norm, w_norm, h_norm = corrected_buttons[test_button]
    
    x = int(x_norm * width)
    y = int(y_norm * height)
    w = int(w_norm * width)
    h = int(h_norm * height)
    center_x = x + w // 2
    center_y = y + h // 2
    
    print(f"\n🎯 Testing corrected {test_button} coordinates:")
    print(f"   Normalized: ({x_norm}, {y_norm}) Size: ({w_norm}, {h_norm})")
    print(f"   Pixels: ({x}, {y}) Size: {w}x{h}")
    print(f"   Center: ({center_x}, {center_y})")
    
    # Focus and test
    audio_signal("Focusing game for corrected coordinate test")
    
    if focus_dune_legacy():
        print("✅ Game focused successfully")
        audio_signal("Game focused")
    else:
        print("⚠️ Focus may have failed")
        audio_signal("Focus uncertain")
    
    time.sleep(2)
    
    # Capture before screenshot
    subprocess.run(['screencapture', '-x', '/tmp/before_corrected_click.png'], capture_output=True)
    
    # Click with corrected coordinates
    audio_signal(f"Clicking corrected {test_button} position")
    print(f"🖱️  Clicking {test_button} at corrected position ({center_x}, {center_y})...")
    
    success = click_coordinates(center_x, center_y)
    
    if success:
        print("✅ Click executed successfully")
        audio_signal("Click successful")
        
        time.sleep(1)
        
        # Capture after screenshot  
        subprocess.run(['screencapture', '-x', '/tmp/after_corrected_click.png'], capture_output=True)
        
        # Check for changes
        try:
            import os
            before_size = os.path.getsize('/tmp/before_corrected_click.png')
            after_size = os.path.getsize('/tmp/after_corrected_click.png')
            
            size_diff = abs(before_size - after_size)
            if size_diff > 1000:
                print(f"📸 Screen changed significantly ({size_diff} bytes) - button likely worked!")
                audio_signal("Screen changed, button click successful")
                return True
            else:
                print(f"⚠️ Small/no screen change ({size_diff} bytes) - coordinates may still be wrong")
                audio_signal("Minimal screen change, coordinates may be wrong")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not compare screenshots: {e}")
            return False
    else:
        print("❌ Click failed")
        audio_signal("Click failed")
        return False

def main():
    """Test corrected button coordinates."""
    audio_signal("Starting corrected coordinate test")
    
    success = test_corrected_coordinates()
    
    if success:
        print("\n✅ Corrected coordinates appear to work!")
        print("Next: Extract template images from these positions")
        audio_signal("Corrected coordinates successful")
    else:
        print("\n❌ Coordinates still need adjustment")
        print("Need to manually identify button positions")
        audio_signal("Coordinates still incorrect")

if __name__ == "__main__":
    main()