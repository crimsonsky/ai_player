#!/usr/bin/env python3
"""
TEMPLATE OVERLAP DIAGNOSTIC TEST
Debug the critical Template Overlap issue where Single Player template 
matches buttons with completely different text on sub-menus.
"""

import subprocess
import time
import os
import sys
import cv2

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_template_overlap():
    """Diagnose the template overlap issue in detail."""
    
    print("🔍 TEMPLATE OVERLAP DIAGNOSTIC TEST")
    print("=" * 50)
    print("OBJECTIVE: Debug why Single Player template matches wrong buttons")
    print("ISSUE: Previous test left game in sub-menu, new test incorrectly identifies sub-menu button as 'Single Player'")
    print()
    
    try:
        # Focus Dune Legacy (which should be in sub-menu state)
        print("🎮 Step 1: Focusing current Dune Legacy state...")
        subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                      capture_output=True)
        time.sleep(2)
        
        # Capture current screen
        print("📸 Step 2: Capturing current screen state...")
        screenshot_path = "/tmp/diagnostic_current_screen.png"
        subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True)
        
        if not os.path.exists(screenshot_path):
            raise Exception("Screenshot capture failed")
        
        # Load and analyze the screenshot
        print("🔍 Step 3: Analyzing current screen content...")
        
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            raise Exception("Could not load screenshot")
        
        print(f"   Screenshot dimensions: {screenshot.shape}")
        
        # Extract text from the ENTIRE screen using OCR to see what's actually there
        print("\n📝 Step 4: FULL SCREEN OCR - What text is actually visible?")
        
        try:
            # Use ocrmac to extract ALL text from the screen
            result = subprocess.run(['ocrmac', screenshot_path], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                full_screen_text = result.stdout.strip()
                print("   📋 FULL SCREEN TEXT CONTENT:")
                print("   " + "=" * 40)
                for line in full_screen_text.split('\n'):
                    if line.strip():
                        print(f"   📄 '{line.strip()}'")
                print("   " + "=" * 40)
            else:
                print("   ⚠️ OCR failed to extract any text")
                full_screen_text = ""
                
        except Exception as e:
            print(f"   ❌ OCR error: {e}")
            full_screen_text = ""
        
        # Check if "Single Player" text actually appears anywhere
        contains_single_player = "single player" in full_screen_text.lower() if full_screen_text else False
        
        print(f"\n🎯 Step 5: CRITICAL CHECK - Does screen contain 'Single Player' text?")
        print(f"   Result: {'YES' if contains_single_player else 'NO'}")
        
        if not contains_single_player:
            print("   ⚠️ PROBLEM CONFIRMED: No 'Single Player' text on screen, but system detected it!")
            print("   This proves Template Overlap Prevention is FAILING")
        
        # Now test the current detection system
        print(f"\n🔍 Step 6: TESTING CURRENT DETECTION SYSTEM...")
        
        # Import and test the game config detection (what's currently being used)
        from game_config import MENU_BUTTONS
        
        print("   📊 Game Config Detection Method:")
        single_player_coords = MENU_BUTTONS["SINGLE_PLAYER"]
        print(f"   Single Player coordinates: {single_player_coords}")
        
        # Extract template from that position and see what's actually there
        screen_height, screen_width = screenshot.shape[:2]
        norm_x, norm_y, confidence = single_player_coords
        
        center_x = int(norm_x * screen_width)
        center_y = int(norm_y * screen_height)
        
        print(f"   Absolute coordinates: ({center_x}, {center_y})")
        
        # Extract region around that coordinate
        button_width, button_height = 200, 60
        x1 = max(0, center_x - button_width // 2)
        y1 = max(0, center_y - button_height // 2)
        x2 = min(screenshot.shape[1], center_x + button_width // 2)
        y2 = min(screenshot.shape[0], center_y + button_height // 2)
        
        actual_region = screenshot[y1:y2, x1:x2]
        region_path = "/tmp/actual_button_region.png"
        cv2.imwrite(region_path, actual_region)
        
        print(f"   📸 Extracted region saved: {region_path}")
        
        # OCR the actual region to see what text is there
        try:
            result = subprocess.run(['ocrmac', region_path], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                actual_button_text = result.stdout.strip()
                print(f"   📝 ACTUAL TEXT at Single Player coordinates: '{actual_button_text}'")
            else:
                actual_button_text = ""
                print(f"   📝 No text extracted from button region")
                
        except Exception as e:
            print(f"   ❌ Region OCR failed: {e}")
            actual_button_text = ""
        
        # Final diagnosis
        print(f"\n🚨 TEMPLATE OVERLAP DIAGNOSIS:")
        print("=" * 50)
        
        if actual_button_text and "single player" not in actual_button_text.lower():
            print(f"❌ CRITICAL BUG CONFIRMED:")
            print(f"   - System detected: 'Single Player'")
            print(f"   - Actual text at location: '{actual_button_text}'")
            print(f"   - This is a TEMPLATE OVERLAP failure")
            print(f"   - The system is using hardcoded coordinates instead of dynamic detection")
            print(f"\n🔧 ROOT CAUSE:")
            print(f"   The test is using game_config.py coordinates (ground truth)")
            print(f"   instead of the enhanced perception system with OCR validation")
        else:
            print(f"✅ No template overlap detected in this case")
        
        # Show the debug images
        print(f"\n🖼️ DEBUG VISUALIZATIONS:")
        print(f"   Full screen: {screenshot_path}")
        print(f"   Button region: {region_path}")
        
        subprocess.run(['open', screenshot_path], capture_output=True)
        subprocess.run(['open', region_path], capture_output=True)
        
        return {
            'full_screen_text': full_screen_text,
            'contains_single_player': contains_single_player,
            'actual_button_text': actual_button_text,
            'coordinates_used': single_player_coords,
            'template_overlap_confirmed': actual_button_text and "single player" not in actual_button_text.lower()
        }
        
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC TEST FAILED: {e}")
        return {'error': str(e)}

def main():
    """Execute template overlap diagnostic."""
    
    results = diagnose_template_overlap()
    
    if results.get('template_overlap_confirmed'):
        print(f"\n🚨 TEMPLATE OVERLAP BUG CONFIRMED")
        print(f"   The system needs to use enhanced perception with OCR validation")
        print(f"   instead of hardcoded game_config.py coordinates")
    elif results.get('error'):
        print(f"\n❌ Diagnostic failed: {results['error']}")
    else:
        print(f"\n✅ No template overlap detected in current state")
    
    return results

if __name__ == "__main__":
    main()