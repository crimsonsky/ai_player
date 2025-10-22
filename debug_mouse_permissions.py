#!/usr/bin/env python3
"""
Mouse Control Permission Debugger
Systematically test and fix mouse control permissions on macOS
"""

import subprocess
import time
import sys

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def check_terminal_accessibility():
    """Check if Terminal has accessibility permissions."""
    print("🔐 CHECKING ACCESSIBILITY PERMISSIONS")
    print("=" * 40)
    
    # Check if we can get accessibility status
    script = '''
    tell application "System Events"
        try
            set currentApp to name of first application process whose frontmost is true
            return "SUCCESS: Can access System Events - " & currentApp
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ AppleScript accessibility test: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ AppleScript accessibility test failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ AppleScript test error: {e}")
        return False

def test_cliclick_permissions():
    """Test if cliclick has proper permissions."""
    print("\n🖱️ TESTING CLICLICK PERMISSIONS")
    print("=" * 35)
    
    try:
        # First check if cliclick is installed
        result = subprocess.run(['which', 'cliclick'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ cliclick not found - installing...")
            subprocess.run(['brew', 'install', 'cliclick'], capture_output=True)
        else:
            print(f"✅ cliclick found at: {result.stdout.strip()}")
        
        # Test cliclick version (should work without permissions)
        result = subprocess.run(['cliclick', '-V'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ cliclick version: {result.stdout.strip()}")
        else:
            print(f"❌ cliclick version check failed: {result.stderr}")
            return False
        
        # Test getting current mouse position (requires accessibility)
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Current mouse position: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Cannot get mouse position: {result.stderr.strip()}")
            print("   This indicates accessibility permission issue")
            return False
            
    except Exception as e:
        print(f"❌ cliclick test error: {e}")
        return False

def show_permission_instructions():
    """Show detailed instructions for enabling permissions."""
    print("\n📋 PERMISSION SETUP INSTRUCTIONS")
    print("=" * 40)
    
    instructions = [
        "1. Open System Preferences (or System Settings on macOS 13+)",
        "2. Go to Security & Privacy → Privacy → Accessibility",
        "3. Click the lock icon and enter your password", 
        "4. Look for 'Terminal' in the list",
        "5. If Terminal is listed, make sure it's checked ✓",
        "6. If Terminal is NOT listed, click '+' and add it:",
        "   - Navigate to /System/Applications/Utilities/Terminal.app",
        "   - Click 'Open' to add it",
        "   - Make sure the checkbox is checked ✓",
        "7. You may need to quit and restart Terminal after adding permissions"
    ]
    
    for instruction in instructions:
        print(f"   {instruction}")
    
    print(f"\n💡 Alternative locations for Terminal:")
    print(f"   • /Applications/Utilities/Terminal.app")
    print(f"   • /System/Applications/Utilities/Terminal.app")
    
    audio_signal("Check accessibility permissions in System Preferences")

def test_pyautogui_alternative():
    """Test pyautogui as alternative to cliclick."""
    print("\n🐍 TESTING PYAUTOGUI ALTERNATIVE")
    print("=" * 35)
    
    try:
        # Try to import pyautogui
        import pyautogui
        print("✅ pyautogui already installed")
        
        # Test getting screen size (doesn't require permissions)
        size = pyautogui.size()
        print(f"✅ Screen size: {size}")
        
        # Test getting mouse position (requires permissions)
        try:
            pos = pyautogui.position()
            print(f"✅ Current mouse position: {pos}")
            return True
        except Exception as e:
            print(f"❌ Cannot get mouse position with pyautogui: {e}")
            return False
            
    except ImportError:
        print("⚠️ pyautogui not installed - installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyautogui'], 
                          capture_output=True, timeout=30)
            print("✅ pyautogui installed")
            return test_pyautogui_alternative()  # Recursive test after install
        except Exception as e:
            print(f"❌ Failed to install pyautogui: {e}")
            return False

def perform_permission_tests():
    """Run comprehensive permission tests."""
    print("🔍 COMPREHENSIVE PERMISSION DIAGNOSIS")
    print("=" * 45)
    
    audio_signal("Starting permission diagnosis")
    
    results = {
        'applescript': False,
        'cliclick': False,
        'pyautogui': False
    }
    
    # Test 1: AppleScript accessibility
    results['applescript'] = check_terminal_accessibility()
    
    # Test 2: cliclick permissions
    results['cliclick'] = test_cliclick_permissions()
    
    # Test 3: pyautogui alternative
    results['pyautogui'] = test_pyautogui_alternative()
    
    # Summary
    print(f"\n📊 PERMISSION TEST RESULTS")
    print("=" * 30)
    
    working_methods = []
    for method, works in results.items():
        status = "✅ WORKING" if works else "❌ BLOCKED"
        print(f"   {method:12}: {status}")
        if works:
            working_methods.append(method)
    
    if working_methods:
        print(f"\n🎉 SUCCESS: {len(working_methods)} method(s) working!")
        audio_signal(f"{len(working_methods)} mouse control methods working")
        return working_methods
    else:
        print(f"\n❌ NO METHODS WORKING")
        audio_signal("No mouse control methods working")
        show_permission_instructions()
        return []

def test_working_mouse_control(methods):
    """Test actual mouse movement with working methods."""
    if not methods:
        print("❌ No working methods to test")
        return
    
    print(f"\n🖱️ TESTING ACTUAL MOUSE MOVEMENT")
    print("=" * 35)
    
    # Test coordinates - move to different corners
    test_positions = [
        (100, 100, "Top-left corner"),
        (500, 300, "Center-left"),
        (1000, 500, "Center"),
        (1500, 300, "Center-right")
    ]
    
    for method in methods:
        print(f"\n🧪 Testing {method} method:")
        
        for x, y, description in test_positions:
            print(f"   Moving to {description} ({x}, {y})...")
            audio_signal(f"Moving to {description}")
            
            success = False
            
            if method == 'cliclick':
                try:
                    result = subprocess.run(['cliclick', f'm:{x},{y}'], 
                                          capture_output=True, text=True, timeout=5)
                    success = result.returncode == 0
                except:
                    success = False
            
            elif method == 'pyautogui':
                try:
                    import pyautogui
                    pyautogui.moveTo(x, y, duration=0.5)
                    success = True
                except Exception as e:
                    print(f"      ❌ pyautogui failed: {e}")
                    success = False
            
            if success:
                print(f"      ✅ Moved to {description}")
                time.sleep(1)
            else:
                print(f"      ❌ Failed to move to {description}")
            
            time.sleep(0.5)

def main():
    """Main permission debugging workflow."""
    print("🔧 MOUSE CONTROL PERMISSION DEBUGGER")
    print("=" * 45)
    print("This will diagnose and help fix mouse control permissions")
    print("You should see the mouse cursor moving during successful tests")
    
    audio_signal("Starting mouse control debugging")
    
    # Run comprehensive tests
    working_methods = perform_permission_tests()
    
    if working_methods:
        print(f"\n✅ Ready to test mouse movement!")
        audio_signal("Ready to test mouse movement")
        
        # Test actual mouse movement
        test_working_mouse_control(working_methods)
        
        print(f"\n🎉 Mouse control debugging complete!")
        print(f"Working methods: {', '.join(working_methods)}")
        audio_signal("Mouse control debugging complete")
        
    else:
        print(f"\n🚫 PERMISSION SETUP REQUIRED")
        print("Please follow the instructions above to enable accessibility permissions")
        print("Then restart Terminal and run this script again")
        audio_signal("Permission setup required")

if __name__ == "__main__":
    main()