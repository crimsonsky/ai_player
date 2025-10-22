#!/usr/bin/env python3
"""
Focused cliclick Diagnosis
Debug why cliclick reports success but mouse doesn't move
"""

import subprocess
import time

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def test_cliclick_detailed():
    """Detailed cliclick testing with verbose output."""
    print("🔍 DETAILED CLICLICK DIAGNOSIS")
    print("=" * 35)
    
    # Test 1: Check cliclick installation
    print("1. Checking cliclick installation...")
    try:
        result = subprocess.run(['cliclick', '-V'], capture_output=True, text=True, timeout=5)
        print(f"   ✅ cliclick version: {result.stdout.strip()}")
        if result.stderr:
            print(f"   ⚠️ stderr: {result.stderr.strip()}")
    except Exception as e:
        print(f"   ❌ cliclick not working: {e}")
        return False
    
    # Test 2: Get current mouse position
    print("\n2. Getting current mouse position...")
    try:
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            current_pos = result.stdout.strip()
            print(f"   ✅ Current position: {current_pos}")
        else:
            print(f"   ❌ Cannot get position: {result.stderr.strip()}")
            print("   💡 This indicates accessibility permission missing for cliclick")
            return False
    except Exception as e:
        print(f"   ❌ Position check error: {e}")
        return False
    
    # Test 3: Try small mouse movement with verbose output
    print("\n3. Testing small mouse movement...")
    try:
        # Get current position first
        result = subprocess.run(['cliclick', 'p'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("   ❌ Cannot get starting position")
            return False
            
        start_pos = result.stdout.strip()
        print(f"   📍 Starting position: {start_pos}")
        
        # Parse current position
        if ',' in start_pos:
            x_str, y_str = start_pos.split(',')
            current_x = int(x_str.strip())
            current_y = int(y_str.strip())
            
            # Move 10 pixels right
            new_x = current_x + 10
            new_y = current_y
            
            print(f"   🎯 Moving to: {new_x},{new_y} (10 pixels right)")
            audio_signal("Moving mouse 10 pixels right")
            
            # Attempt move
            result = subprocess.run(['cliclick', f'm:{new_x},{new_y}'], 
                                  capture_output=True, text=True, timeout=5)
            
            print(f"   📋 Move command result:")
            print(f"      Return code: {result.returncode}")
            print(f"      stdout: '{result.stdout.strip()}'")
            print(f"      stderr: '{result.stderr.strip()}'")
            
            if result.returncode == 0:
                time.sleep(0.5)
                
                # Check if position actually changed
                result2 = subprocess.run(['cliclick', 'p'], capture_output=True, text=True, timeout=5)
                if result2.returncode == 0:
                    end_pos = result2.stdout.strip()
                    print(f"   📍 End position: {end_pos}")
                    
                    if end_pos != start_pos:
                        print("   ✅ Mouse actually moved!")
                        audio_signal("Mouse movement successful")
                        return True
                    else:
                        print("   ❌ Mouse did NOT move (position unchanged)")
                        audio_signal("Mouse did not move")
                        return False
                else:
                    print("   ❌ Cannot verify end position")
                    return False
            else:
                print("   ❌ Move command failed")
                return False
        else:
            print(f"   ❌ Cannot parse position: {start_pos}")
            return False
            
    except Exception as e:
        print(f"   ❌ Movement test error: {e}")
        return False

def check_accessibility_specifically():
    """Check accessibility permissions specifically."""
    print("\n🔐 ACCESSIBILITY PERMISSION CHECK")
    print("=" * 35)
    
    # Method 1: Try to use AppleScript to check accessibility
    script = '''
    tell application "System Events"
        try
            -- Try to get a UI element (requires accessibility)
            set frontApp to name of first application process whose frontmost is true
            return "SUCCESS: Can access UI elements of " & frontApp
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"   ✅ AppleScript accessibility: {result.stdout.strip()}")
        else:
            print(f"   ❌ AppleScript accessibility blocked: {result.stderr.strip()}")
            print("   💡 This confirms accessibility permission issue")
    except Exception as e:
        print(f"   ❌ AppleScript test error: {e}")

def show_cliclick_specific_fix():
    """Show specific instructions for cliclick permissions."""
    print("\n🔧 CLICLICK PERMISSION FIX")
    print("=" * 30)
    
    print("The issue is that cliclick needs specific accessibility permissions.")
    print("Here's how to fix it:")
    print()
    print("1. Open System Preferences/Settings")
    print("2. Go to Privacy & Security → Privacy → Accessibility")  
    print("3. Look for these entries and ensure they're enabled:")
    print("   • Terminal ✓")
    print("   • cliclick ✓ (if listed)")
    print("4. If cliclick isn't listed, add it manually:")
    print("   • Click '+' button")
    print("   • Navigate to: /usr/local/bin/cliclick")
    print("   • Add and enable it ✓")
    print("5. If you can't find cliclick binary, find it with:")
    print("   which cliclick")
    print()
    print("⚠️ IMPORTANT: You may need to restart Terminal after changes")
    
    audio_signal("Check cliclick permissions in accessibility settings")

def main():
    """Main cliclick diagnosis."""
    print("🖱️ CLICLICK MOVEMENT DIAGNOSIS")
    print("=" * 35)
    print("This will determine why cliclick reports success but doesn't move mouse")
    
    audio_signal("Starting cliclick diagnosis")
    
    # Run detailed cliclick test
    success = test_cliclick_detailed()
    
    # Check general accessibility
    check_accessibility_specifically()
    
    if not success:
        show_cliclick_specific_fix()
        
        # Show where cliclick is installed
        print(f"\n📍 FINDING CLICLICK BINARY")
        print("=" * 30)
        try:
            result = subprocess.run(['which', 'cliclick'], capture_output=True, text=True)
            if result.returncode == 0:
                cliclick_path = result.stdout.strip()
                print(f"cliclick is located at: {cliclick_path}")
                print(f"Add this path to accessibility permissions: {cliclick_path}")
            else:
                print("❌ cliclick not found in PATH")
        except:
            print("❌ Could not locate cliclick")
    else:
        print("\n🎉 cliclick is working properly!")
        audio_signal("cliclick working properly")

if __name__ == "__main__":
    main()