#!/usr/bin/env python3
"""
Reliable Click Test with Visual Mouse Movement
Tests different clicking methods to find one that actually works
"""

import subprocess
import time
import os

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def method1_applescript_click(x, y):
    """Method 1: Basic AppleScript click."""
    script = f'''
    tell application "System Events"
        click at {{{x}, {y}}}
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def method2_applescript_mouse_move_click(x, y):
    """Method 2: Move mouse then click."""
    script = f'''
    tell application "System Events"
        set the mouse location to {{{x}, {y}}}
        delay 0.1
        click at {{{x}, {y}}}
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def method3_cliclick(x, y):
    """Method 3: Using cliclick utility (if available)."""
    try:
        # Check if cliclick is available
        result = subprocess.run(['which', 'cliclick'], capture_output=True)
        if result.returncode != 0:
            return False, "cliclick not installed"
        
        # Move mouse and click
        result1 = subprocess.run(['cliclick', 'm:' + str(x) + ',' + str(y)], 
                                capture_output=True, text=True, timeout=5)
        time.sleep(0.1)
        result2 = subprocess.run(['cliclick', 'c:.'], 
                                capture_output=True, text=True, timeout=5)
        
        return result1.returncode == 0 and result2.returncode == 0, "cliclick method"
    except Exception as e:
        return False, str(e)

def method4_applescript_enhanced(x, y):
    """Method 4: Enhanced AppleScript with proper mouse handling."""
    script = f'''
    tell application "System Events"
        -- Move mouse to position
        set mouseLoc to {{{x}, {y}}}
        
        -- Perform click with explicit mouse down/up
        tell application "System Events"
            key down command
            key up command
        end tell
        
        -- Alternative click method
        do shell script "echo 'Moving to " + {x} + "," + {y} + "'"
        
        click at {{{x}, {y}}}
        
        -- Verify click
        delay 0.2
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def test_all_click_methods():
    """Test all clicking methods to find one that works."""
    print("🖱️  TESTING CLICK METHODS")
    print("=" * 30)
    
    # Test coordinates (center of screen)
    test_x, test_y = 1720, 776
    
    print(f"🎯 Target coordinates: ({test_x}, {test_y})")
    
    methods = [
        ("Method 1: Basic AppleScript", method1_applescript_click),
        ("Method 2: Mouse Move + Click", method2_applescript_mouse_move_click),
        ("Method 3: cliclick utility", method3_cliclick),
        ("Method 4: Enhanced AppleScript", method4_applescript_enhanced)
    ]
    
    # Focus Dune Legacy first
    audio_signal("Focusing Dune Legacy for click test")
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    subprocess.run(['osascript', '-e', focus_script], capture_output=True)
    time.sleep(2)
    
    working_methods = []
    
    for method_name, method_func in methods:
        print(f"\n🧪 Testing {method_name}...")
        audio_signal(f"Testing {method_name.split(':')[0]}")
        
        # Capture before
        subprocess.run(['screencapture', '-x', f'/tmp/before_{len(working_methods)}.png'], 
                      capture_output=True)
        
        success, error = method_func(test_x, test_y)
        
        if success:
            print(f"   ✅ {method_name}: SUCCESS")
            audio_signal("Method successful")
            
            time.sleep(1)
            
            # Capture after
            subprocess.run(['screencapture', '-x', f'/tmp/after_{len(working_methods)}.png'], 
                          capture_output=True)
            
            working_methods.append((method_name, method_func))
        else:
            print(f"   ❌ {method_name}: FAILED - {error}")
            audio_signal("Method failed")
        
        time.sleep(1)  # Brief pause between methods
    
    print(f"\n📊 Results: {len(working_methods)}/{len(methods)} methods work")
    
    if working_methods:
        print("✅ Working methods:")
        for name, func in working_methods:
            print(f"   - {name}")
        audio_signal(f"{len(working_methods)} methods are working")
        return working_methods[0][1]  # Return first working method
    else:
        print("❌ No click methods are working!")
        audio_signal("No click methods working")
        return None

def test_working_click_method(click_func):
    """Test the working click method on actual Dune Legacy buttons."""
    if not click_func:
        print("❌ No working click method available")
        return
    
    print("\n🎮 TESTING WORKING METHOD ON ACTUAL BUTTONS")
    print("=" * 45)
    
    # More button positions to try
    test_positions = [
        ("Center Screen", 1720, 720),
        ("Upper Center", 1720, 500),
        ("Lower Center", 1720, 900),
        ("Left Center", 1200, 720),
        ("Right Center", 2200, 720),
    ]
    
    for name, x, y in test_positions:
        print(f"\n🎯 Testing {name} at ({x}, {y})")
        audio_signal(f"Testing {name}")
        
        # Focus game
        focus_script = '''
        tell application "Dune Legacy"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', focus_script], capture_output=True)
        time.sleep(1)
        
        # Try click
        success, error = click_func(x, y)
        
        if success:
            print(f"   ✅ Click executed at {name}")
            audio_signal("Click successful")
        else:
            print(f"   ❌ Click failed at {name}: {error}")
            audio_signal("Click failed")
        
        time.sleep(2)

def main():
    """Test and find working click method."""
    audio_signal("Starting click method testing")
    
    working_method = test_all_click_methods()
    
    if working_method:
        print("\n🎉 Found working click method!")
        test_working_click_method(working_method)
    else:
        print("\n💡 Suggestions:")
        print("1. Check System Preferences > Security & Privacy > Accessibility")
        print("2. Add Terminal to allowed apps for controlling computer")
        print("3. Try installing cliclick: brew install cliclick")
        audio_signal("No working methods found, check accessibility permissions")

if __name__ == "__main__":
    main()