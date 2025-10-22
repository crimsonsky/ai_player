#!/usr/bin/env python3
"""
Screenshot Debug Script
Isolates and debugs screen capture issues for M2 implementation.
Tests various methods and provides detailed error information.
"""

import subprocess
import time
import os
import sys


def audio_signal(message: str):
    """Provide audio feedback during debugging."""
    try:
        os.system(f'say "{message}"')
    except:
        print(f"🔊 Audio: {message}")


def test_basic_screencapture():
    """Test basic screencapture command with detailed error reporting."""
    print("=== Testing Basic Screenshot Capture ===")
    
    timestamp = int(time.time())
    screenshot_path = f"/tmp/debug_screenshot_{timestamp}.png"
    
    try:
        print(f"Attempting screenshot to: {screenshot_path}")
        
        # Test 1: Basic screencapture
        print("Test 1: Basic screencapture command...")
        result = subprocess.run(['screencapture', '-x', screenshot_path], 
                              capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        print(f"   Stdout: '{result.stdout}'")
        print(f"   Stderr: '{result.stderr}'")
        
        if result.returncode == 0:
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                print(f"   ✅ Screenshot created successfully (size: {file_size} bytes)")
                
                # Get file info
                file_result = subprocess.run(['file', screenshot_path], 
                                           capture_output=True, text=True)
                print(f"   File info: {file_result.stdout.strip()}")
                
                # Cleanup
                os.remove(screenshot_path)
                return True
            else:
                print(f"   ❌ Screenshot command succeeded but file not found")
                return False
        else:
            print(f"   ❌ Screenshot command failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Screenshot command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Screenshot error: {e}")
        return False


def test_screencapture_variations():
    """Test different screencapture options and formats."""
    print("\n=== Testing Screenshot Variations ===")
    
    timestamp = int(time.time())
    base_path = f"/tmp/debug_screenshot_{timestamp}"
    
    tests = [
        ("Basic PNG", ['screencapture', '-x', f"{base_path}_basic.png"]),
        ("JPG Format", ['screencapture', '-x', '-t', 'jpg', f"{base_path}_jpg.jpg"]),
        ("With Window ID", ['screencapture', '-x', '-l', '0', f"{base_path}_window.png"]),
        ("Interactive Mode", ['screencapture', '-i', f"{base_path}_interactive.png"]),
    ]
    
    results = {}
    
    for test_name, command in tests:
        print(f"\nTest: {test_name}")
        print(f"   Command: {' '.join(command)}")
        
        try:
            if "interactive" in test_name.lower():
                print("   Skipping interactive test (requires user input)")
                results[test_name] = "SKIPPED"
                continue
                
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            output_path = command[-1]
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ Success (size: {file_size} bytes)")
                results[test_name] = "SUCCESS"
                
                # Cleanup
                os.remove(output_path)
            else:
                print(f"   ❌ Failed (return code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                results[test_name] = "FAILED"
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[test_name] = "ERROR"
    
    return results


def test_permissions():
    """Test for permission issues that might block screenshot capture."""
    print("\n=== Testing Permissions ===")
    
    try:
        # Test 1: Check if we can write to /tmp
        test_file = "/tmp/permission_test.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ Write permission to /tmp: OK")
        else:
            print("❌ Write permission to /tmp: FAILED")
            
    except Exception as e:
        print(f"❌ /tmp write test failed: {e}")
    
    # Test 2: Check screencapture command availability
    try:
        result = subprocess.run(['which', 'screencapture'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            screencapture_path = result.stdout.strip()
            print(f"✅ screencapture command found at: {screencapture_path}")
        else:
            print("❌ screencapture command not found")
    except Exception as e:
        print(f"❌ screencapture availability check failed: {e}")
    
    # Test 3: Check for Screen Recording permission (macOS Catalina+)
    print("\nChecking Screen Recording permissions...")
    print("ℹ️  If screenshots fail, you may need to grant 'Screen Recording' permission")
    print("   Go to: System Preferences > Security & Privacy > Privacy > Screen Recording")
    print("   Add Terminal or Python to the allowed apps")


def test_alternative_methods():
    """Test alternative screenshot methods."""
    print("\n=== Testing Alternative Methods ===")
    
    # Method 1: Using osascript
    print("\nMethod 1: Using osascript...")
    timestamp = int(time.time())
    screenshot_path = f"/tmp/osascript_screenshot_{timestamp}.png"
    
    try:
        applescript = f'''
        tell application "System Events"
            set screenshot to (do shell script "screencapture -x {screenshot_path}")
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=15)
        
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"   ✅ osascript method worked (size: {file_size} bytes)")
            os.remove(screenshot_path)
            return "osascript"
        else:
            print("   ❌ osascript method failed")
            
    except Exception as e:
        print(f"   ❌ osascript method error: {e}")
    
    # Method 2: Using Python imaging libraries (if available)
    print("\nMethod 2: Checking for Python imaging libraries...")
    try:
        import PIL.ImageGrab
        print("   ✅ PIL.ImageGrab available")
        
        # Quick test
        screenshot = PIL.ImageGrab.grab()
        if screenshot:
            print(f"   ✅ PIL screenshot works (size: {screenshot.size})")
            return "PIL"
        
    except ImportError:
        print("   ℹ️  PIL not available (expected - not installed yet)")
    except Exception as e:
        print(f"   ❌ PIL test error: {e}")
    
    return None


def main():
    """Run comprehensive screenshot debugging."""
    print("🔍 SCREENSHOT CAPTURE DEBUG")
    print("=" * 50)
    
    audio_signal("Starting screenshot debugging")
    
    # Test 1: Basic functionality
    basic_success = test_basic_screencapture()
    
    # Test 2: Variations
    variation_results = test_screencapture_variations()
    
    # Test 3: Permissions
    test_permissions()
    
    # Test 4: Alternatives
    alternative_method = test_alternative_methods()
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 DEBUG SUMMARY")
    print("=" * 50)
    
    if basic_success:
        print("✅ Basic screenshot capture: WORKING")
        audio_signal("Screenshot capture is working")
    else:
        print("❌ Basic screenshot capture: FAILED")
        audio_signal("Screenshot capture failed")
    
    print("\nVariation test results:")
    for test, result in variation_results.items():
        status = "✅" if result == "SUCCESS" else "❌" if result == "FAILED" else "⚠️"
        print(f"   {status} {test}: {result}")
    
    if alternative_method:
        print(f"\n✅ Alternative method available: {alternative_method}")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    
    if basic_success:
        print("✅ Screenshot capture is working - investigate M2 test logic")
    else:
        print("❌ Screenshot capture blocked - likely permissions issue")
        print("   1. Check System Preferences > Security & Privacy > Privacy > Screen Recording")
        print("   2. Add Terminal and/or Python to allowed applications")
        print("   3. Restart Terminal after granting permissions")
        
    if alternative_method == "PIL":
        print("✅ PIL.ImageGrab can be used as fallback method")
    elif alternative_method == "osascript":
        print("✅ osascript method can be used as fallback")


if __name__ == "__main__":
    main()