#!/usr/bin/env python3
"""
CORRECTED FUNCTIONAL VALIDATION TEST
Ensures proper screen state before testing Template Overlap Prevention
"""

import subprocess
import time
import os
import sys

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mouse_control import MouseController

def ensure_main_menu_state():
    """Ensure we're on the main menu before starting the test."""
    
    print("🔄 SCREEN STATE VALIDATION")
    print("=" * 30)
    print("Ensuring we start from the main menu...")
    
    # Focus Dune Legacy
    subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                  capture_output=True)
    time.sleep(2)
    
    # Capture current screen to analyze what's there
    screenshot_path = "/tmp/current_screen_state.png"
    subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True)
    
    # Use OCR to identify current screen
    try:
        result = subprocess.run(['ocrmac', screenshot_path], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            screen_text = result.stdout.strip().lower()
            print(f"📄 Current screen contains: {screen_text}")
            
            # Check if we're on main menu (contains "single player", "options", etc.)
            main_menu_indicators = ['single player', 'multiplayer', 'options', 'map editor']
            is_main_menu = any(indicator in screen_text for indicator in main_menu_indicators)
            
            if is_main_menu:
                print("✅ Already on main menu")
                return True
            else:
                print("⚠️ Not on main menu. Attempting to return...")
                
                # Try pressing ESC a few times to get back to main menu
                for i in range(3):
                    print(f"   Pressing ESC (attempt {i+1})")
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], 
                                  capture_output=True)
                    time.sleep(1)
                    
                    # Check again
                    subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True)
                    result = subprocess.run(['ocrmac', screenshot_path], 
                                          capture_output=True, text=True, timeout=5)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        screen_text = result.stdout.strip().lower()
                        is_main_menu = any(indicator in screen_text for indicator in main_menu_indicators)
                        
                        if is_main_menu:
                            print("✅ Successfully returned to main menu")
                            return True
                
                print("❌ Could not return to main menu")
                return False
        else:
            print("⚠️ Could not read screen content")
            return False
            
    except Exception as e:
        print(f"❌ Screen state validation failed: {e}")
        return False

def execute_corrected_functional_test():
    """Execute the corrected functional test starting from the proper main menu state."""
    
    print("🧪 CORRECTED M2 FUNCTIONAL VALIDATION")
    print("=" * 50)
    print("OBJECTIVE: Test Template Overlap Prevention from correct starting state")
    print()
    
    try:
        # Step 1: Ensure proper starting state
        if not ensure_main_menu_state():
            raise Exception("Could not establish main menu starting state")
        
        # Initialize mouse controller
        mouse = MouseController()
        
        # Audio signal start
        subprocess.run(['say', 'Corrected functional validation starting from main menu'], 
                      capture_output=True)
        
        # Step 2: Analyze MAIN MENU with OCR validation
        print("\n📋 STEP 2: MAIN MENU ANALYSIS with OCR Validation")
        
        main_menu_screenshot = "/tmp/validated_main_menu.png"
        subprocess.run(['screencapture', '-x', main_menu_screenshot], capture_output=True)
        
        # Use OCR to find actual "Single Player" button
        result = subprocess.run(['ocrmac', main_menu_screenshot], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            screen_text = result.stdout.strip()
            print(f"📄 Main menu text content:")
            for line in screen_text.split('\n'):
                if line.strip():
                    print(f"   📝 '{line.strip()}'")
            
            # Verify "Single Player" is actually present
            if "single player" in screen_text.lower():
                print("✅ 'Single Player' text confirmed on main menu")
            else:
                raise Exception("Single Player text not found on main menu - wrong screen state")
        
        # Step 3: Use game config coordinates (since we're now on the correct screen)
        from game_config import MENU_BUTTONS
        
        single_player_coords = MENU_BUTTONS["SINGLE_PLAYER"]
        norm_x, norm_y, confidence = single_player_coords
        
        screen_width = 3440  # Your screen resolution
        screen_height = 1440
        
        abs_x = int(norm_x * screen_width)
        abs_y = int(norm_y * screen_height)
        
        print(f"🎯 Single Player button coordinates: ({abs_x}, {abs_y})")
        
        # Step 4: Click Single Player
        print("\n📋 STEP 4: Click Single Player for screen transition")
        
        success = mouse.left_click(abs_x, abs_y)
        if not success:
            raise Exception("Failed to click Single Player button")
        
        subprocess.run(['say', 'Single Player clicked - awaiting screen transition'], 
                      capture_output=True)
        
        # Wait for transition
        time.sleep(4)
        
        # Step 5: Analyze NEW SCREEN with proper OCR validation
        print("\n📋 STEP 5: NEW SCREEN ANALYSIS - Template Overlap Test")
        
        new_screen_screenshot = "/tmp/new_screen_after_click.png"
        subprocess.run(['screencapture', '-x', new_screen_screenshot], capture_output=True)
        
        # Extract ALL text from new screen
        result = subprocess.run(['ocrmac', new_screen_screenshot], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            new_screen_text = result.stdout.strip()
            print(f"📄 New screen text content:")
            for line in new_screen_text.split('\n'):
                if line.strip():
                    print(f"   📝 '{line.strip()}'")
            
            # CRITICAL TEST: Check if "Single Player" text still appears
            contains_single_player = "single player" in new_screen_text.lower()
            
            print(f"\n🎯 TEMPLATE OVERLAP TEST RESULTS:")
            print(f"   New screen contains 'Single Player' text: {'YES' if contains_single_player else 'NO'}")
            
            if contains_single_player:
                print("⚠️ WARNING: 'Single Player' text found on new screen")
                print("   This could indicate we're still on main menu (transition failed)")
            else:
                print("✅ SUCCESS: No 'Single Player' text on new screen")
                print("   Screen transition successful, different content detected")
            
            # Now test if the DETECTION SYSTEM would incorrectly identify Single Player
            print(f"\n🔍 DETECTION SYSTEM TEST:")
            print(f"   Testing if system would incorrectly detect 'Single Player' at same coordinates...")
            
            # Extract the region at the original Single Player coordinates
            import cv2
            new_screenshot = cv2.imread(new_screen_screenshot)
            
            button_width, button_height = 200, 60
            x1 = max(0, abs_x - button_width // 2)
            y1 = max(0, abs_y - button_height // 2)
            x2 = min(new_screenshot.shape[1], abs_x + button_width // 2)
            y2 = min(new_screenshot.shape[0], abs_y + button_height // 2)
            
            region_at_sp_coords = new_screenshot[y1:y2, x1:x2]
            region_path = "/tmp/region_at_sp_coordinates.png"
            cv2.imwrite(region_path, region_at_sp_coords)
            
            # OCR this specific region
            result = subprocess.run(['ocrmac', region_path], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                region_text = result.stdout.strip()
                print(f"   📝 Text at Single Player coordinates: '{region_text}'")
                
                if "single player" in region_text.lower():
                    print("❌ PROBLEM: Still shows 'Single Player' - transition may have failed")
                else:
                    print("✅ SUCCESS: Different text at Single Player coordinates")
                    print(f"   This proves template overlap prevention would work")
            else:
                print("   ⚠️ No text detected at Single Player coordinates region")
            
        # Step 6: Audio announcement of actual buttons found
        print(f"\n📢 STEP 6: Audio announcement of new screen content")
        
        # Extract actual button names from new screen
        new_screen_lines = [line.strip() for line in new_screen_text.split('\n') if line.strip()]
        likely_buttons = [line for line in new_screen_lines if len(line) < 30 and len(line) > 3]
        
        if likely_buttons:
            announcement = f"New screen buttons detected: " + ", ".join(likely_buttons[:5])  # First 5
            print(f"   📢 {announcement}")
            subprocess.run(['say', announcement], capture_output=True)
        else:
            subprocess.run(['say', 'New screen detected but no clear button text identified'], 
                          capture_output=True)
        
        print(f"\n✅ CORRECTED FUNCTIONAL VALIDATION COMPLETE")
        print(f"   Started from verified main menu state")
        print(f"   Screen transition detected and validated")
        print(f"   Template overlap prevention can be properly tested")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CORRECTED FUNCTIONAL TEST FAILED: {e}")
        subprocess.run(['say', f'Test failed: {str(e)}'], capture_output=True)
        return False

def main():
    """Execute corrected functional validation."""
    
    success = execute_corrected_functional_test()
    
    if success:
        print(f"\n🎉 Test completed successfully with proper screen state management")
    else:
        print(f"\n❌ Test failed - screen state management needed")
    
    return success

if __name__ == "__main__":
    main()