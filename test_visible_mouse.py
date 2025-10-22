#!/usr/bin/env python3
"""
Visible Mouse Movement Test
Uses cliclick to actually move the mouse visibly and click
"""

import subprocess
import time

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def move_mouse_and_click(x, y, description="position"):
    """Move mouse visibly and click using cliclick."""
    print(f"🖱️  Moving mouse to {description} at ({x}, {y})")
    
    try:
        # Move mouse to position (this should be visible)
        result1 = subprocess.run(['cliclick', f'm:{x},{y}'], 
                                capture_output=True, text=True, timeout=5)
        
        if result1.returncode != 0:
            print(f"❌ Mouse move failed: {result1.stderr}")
            return False
        
        print(f"✅ Mouse moved to ({x}, {y})")
        
        # Wait a moment so you can see the mouse
        time.sleep(1)
        
        # Click at current position
        result2 = subprocess.run(['cliclick', 'c:.'], 
                                capture_output=True, text=True, timeout=5)
        
        if result2.returncode != 0:
            print(f"❌ Click failed: {result2.stderr}")
            return False
        
        print(f"✅ Clicked at ({x}, {y})")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mouse_movement():
    """Test visible mouse movement and clicking."""
    print("🖱️  TESTING VISIBLE MOUSE MOVEMENT")
    print("=" * 35)
    
    audio_signal("Testing visible mouse movement")
    
    # Focus Dune Legacy first
    print("🎮 Focusing Dune Legacy...")
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Dune Legacy focused")
        audio_signal("Game focused")
    else:
        print("⚠️ Focus may have failed")
    
    time.sleep(2)
    
    # Test different positions with visible mouse movement
    test_positions = [
        (1720, 400, "Upper center"),      # Top area
        (1720, 600, "Middle-upper"),      # Likely single player area
        (1720, 700, "Center"),            # Likely multiplayer area  
        (1720, 800, "Middle-lower"),      # Likely options area
        (1720, 900, "Lower center"),      # Lower area
    ]
    
    for x, y, description in test_positions:
        print(f"\n🎯 Testing {description}...")
        audio_signal(f"Testing {description}")
        
        # Capture before screenshot
        subprocess.run(['screencapture', '-x', f'/tmp/before_{description.replace(" ", "_")}.png'], 
                      capture_output=True)
        
        # Move mouse and click
        success = move_mouse_and_click(x, y, description)
        
        if success:
            audio_signal("Click successful")
            
            # Wait for potential UI response
            time.sleep(1)
            
            # Capture after screenshot
            subprocess.run(['screencapture', '-x', f'/tmp/after_{description.replace(" ", "_")}.png'], 
                          capture_output=True)
            
            # Check if screen changed
            try:
                import os
                before_path = f'/tmp/before_{description.replace(" ", "_")}.png'
                after_path = f'/tmp/after_{description.replace(" ", "_")}.png'
                
                if os.path.exists(before_path) and os.path.exists(after_path):
                    before_size = os.path.getsize(before_path)
                    after_size = os.path.getsize(after_path)
                    size_diff = abs(before_size - after_size)
                    
                    if size_diff > 1000:
                        print(f"📸 Screen changed significantly ({size_diff} bytes) - button likely worked!")
                        audio_signal("Button responded!")
                        print(f"🎉 SUCCESS: {description} appears to be a working button!")
                        return x, y, description
                    else:
                        print(f"📸 Minimal change ({size_diff} bytes) - not a button")
            except:
                pass
        else:
            audio_signal("Click failed")
        
        time.sleep(2)  # Pause between tests
    
    print("\n❌ No responsive button found at tested positions")
    audio_signal("No responsive buttons found")
    return None, None, None

def main():
    """Test visible mouse movement to find actual button positions."""
    print("🎯 FINDING ACTUAL BUTTON POSITIONS")
    print("You should see the mouse cursor moving around the screen!")
    print("=" * 50)
    
    audio_signal("Starting mouse movement test - watch the cursor")
    
    # Give user time to watch
    time.sleep(3)
    
    x, y, description = test_mouse_movement()
    
    if x and y:
        print(f"\n🎉 FOUND WORKING BUTTON: {description} at ({x}, {y})")
        print("This position will be used to extract template images!")
        audio_signal(f"Found working button at {description}")
    else:
        print("\n💭 If you didn't see the mouse moving, there might be a permission issue.")
        print("Check System Preferences > Security & Privacy > Privacy > Accessibility")
        print("Make sure Terminal is enabled for controlling your computer.")
        audio_signal("Check accessibility permissions if mouse didn't move")

if __name__ == "__main__":
    main()