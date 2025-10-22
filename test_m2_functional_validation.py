#!/usr/bin/env python3
"""
M2 FUNCTIONAL VALIDATION TEST - LEVEL-1 ARCHITECTURAL CORRECTION
Tests Screen Context Identifier and Template Overlap Prevention

CRITICAL REQUIREMENTS:
1. Start from main menu
2. Confirm Screen Context ID is 'MAIN_MENU'
3. Click Single Player button
4. Confirm Screen Context ID is 'SINGLE_PLAYER_SUB_MENU'
5. Audio list detected elements (MUST NOT include "Single Player")
6. Click top-most button on new menu
"""

import subprocess
import time
import os
import sys

def ensure_app_focus():
    """Ensure Dune Legacy is focused."""
    print("🎯 Ensuring Dune Legacy is focused...")
    subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                  capture_output=True)
    time.sleep(2)
    
    # Verify focus
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
            capture_output=True, text=True)
        frontmost = result.stdout.strip()
        print(f"   Frontmost app: {frontmost}")
        return frontmost == "Dune Legacy"
    except:
        return False

def reset_to_main_menu():
    """Reset to main menu with safe ESC presses."""
    print("🔄 Resetting to main menu...")
    
    def get_frontmost_app():
        try:
            p = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
                capture_output=True, text=True)
            return p.stdout.strip()
        except Exception:
            return None
    
    # Press ESC twice with focus checks
    for i in range(2):
        front = get_frontmost_app()
        print(f"   Before ESC {i+1}: frontmost={front}")
        
        subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], 
                      capture_output=True)
        time.sleep(0.8)
        
        front_after = get_frontmost_app()
        if front_after != 'Dune Legacy':
            print("   Re-activating Dune Legacy")
            subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                          capture_output=True)
            time.sleep(0.8)
    
    print("✅ Reset completed")
    time.sleep(2)

def execute_m2_functional_validation():
    """Execute the M2 functional validation test sequence."""
    
    print("🧪 M2 FUNCTIONAL VALIDATION - LEVEL-1 ARCHITECTURAL CORRECTION")
    print("=" * 70)
    print("OBJECTIVE: Validate Screen Context Identifier and Template Overlap Prevention")
    print()
    
    try:
        # Ensure we can import the modules
        sys.path.insert(0, '/Users/amir/projects/ai_player')
        from src.perception.perception_module import PerceptionModule
        from mouse_control import MouseController
        
        # Initialize components
        config = {
            'confidence_threshold': 0.8,
            'audio_feedback': True
        }
        
        perception = PerceptionModule(config)
        mouse = MouseController()
        
        # Step 1: Ensure app focus and reset
        if not ensure_app_focus():
            raise Exception("Could not focus Dune Legacy")
        
        reset_to_main_menu()
        
        # Step 2: CRITICAL CHECK - Confirm Screen Context ID is 'MAIN_MENU'
        print("📋 STEP 2: Screen Context Verification - Main Menu")
        print("-" * 50)
        
        screenshot_path = perception.capture_screen()
        if not screenshot_path:
            raise Exception("Failed to capture main menu screenshot")
        
        main_menu_context = perception.identify_screen_context(screenshot_path)
        print(f"   🎯 Screen Context Detected: {main_menu_context}")
        
        if main_menu_context != 'MAIN_MENU':
            print(f"   ❌ ERROR: Expected 'MAIN_MENU', got '{main_menu_context}'")
            perception.audio_signal("Screen context error: Not on main menu")
            # Continue anyway for diagnostic purposes
        else:
            print(f"   ✅ SUCCESS: Main menu context confirmed")
            perception.audio_signal("Main menu context confirmed")
        
        # Step 3: Click Single Player button
        print("\n📋 STEP 3: Single Player Button Click")
        print("-" * 40)
        
        # Use known coordinates for Single Player
        from game_config import MENU_BUTTONS
        
        single_player_coords = MENU_BUTTONS["SINGLE_PLAYER"]
        norm_x, norm_y, confidence = single_player_coords
        
        screen_width = 3440
        screen_height = 1440
        
        abs_x = int(norm_x * screen_width)
        abs_y = int(norm_y * screen_height)
        
        print(f"   🖱️ Clicking Single Player at ({abs_x}, {abs_y})")
        perception.audio_signal("Clicking Single Player button")
        
        success = mouse.left_click(abs_x, abs_y)
        if not success:
            raise Exception("Failed to click Single Player")
        
        time.sleep(4)  # Wait for transition
        
        # Step 4: CRITICAL CHECK - Confirm Screen Context ID is 'SINGLE_PLAYER_SUB_MENU'
        print("\n📋 STEP 4: Screen Context Verification - Submenu")
        print("-" * 50)
        
        submenu_screenshot = perception.capture_screen()
        if not submenu_screenshot:
            raise Exception("Failed to capture submenu screenshot")
        
        submenu_context = perception.identify_screen_context(submenu_screenshot)
        print(f"   🎯 Screen Context Detected: {submenu_context}")
        
        if submenu_context != 'SINGLE_PLAYER_SUB_MENU':
            print(f"   ⚠️ WARNING: Expected 'SINGLE_PLAYER_SUB_MENU', got '{submenu_context}'")
            perception.audio_signal("Screen context warning: Unexpected submenu context")
        else:
            print(f"   ✅ SUCCESS: Submenu context confirmed")
            perception.audio_signal("Submenu context confirmed")
        
        # Step 5: CRITICAL VALIDATION - Run perception with context gating
        print("\n📋 STEP 5: Template Overlap Prevention Validation")
        print("-" * 55)
        
        analysis_result = perception.analyze_menu_screen(submenu_screenshot)
        
        detected_elements = analysis_result.get("elements_detected", [])
        screen_context = analysis_result.get("screen_context", "UNKNOWN")
        
        print(f"   📊 Analysis Results:")
        print(f"      Screen Context: {screen_context}")
        print(f"      Elements detected: {len(detected_elements)}")
        
        # CRITICAL CHECK: Ensure no 'Single Player' on submenu
        single_player_detected = False
        element_names = []
        
        for element in detected_elements:
            name = element.get("name", "UNKNOWN")
            text_label = element.get("text_label", "")
            template_id = element.get("template_id", "")
            
            # Check for Single Player template overlap
            if 'SINGLE_PLAYER' in template_id.upper() or 'single player' in text_label.lower():
                single_player_detected = True
                print(f"      ❌ CRITICAL ERROR: Single Player detected on submenu!")
                print(f"         Template ID: {template_id}")
                print(f"         Text Label: {text_label}")
            
            element_names.append(text_label if text_label else name)
        
        if single_player_detected:
            print(f"   ❌ TEMPLATE OVERLAP FAILURE: Single Player found on submenu")
            perception.audio_signal("CRITICAL FAILURE: Template overlap detected")
        else:
            print(f"   ✅ TEMPLATE OVERLAP PREVENTION SUCCESS: No Single Player on submenu")
            perception.audio_signal("Template overlap prevention successful")
        
        # Step 6: Click top-most button
        print("\n📋 STEP 6: Click Top-Most Button")
        print("-" * 35)
        
        if detected_elements:
            # Sort by y-coordinate to find top-most
            sorted_elements = sorted(detected_elements, key=lambda e: e.get("normalized_y", 1.0))
            top_element = sorted_elements[0]
            
            top_x = int(top_element["normalized_x"] * screen_width)
            top_y = int(top_element["normalized_y"] * screen_height)
            top_name = top_element.get("text_label") or top_element.get("name", "UNKNOWN")
            
            print(f"   🖱️ Clicking top button: '{top_name}' at ({top_x}, {top_y})")
            perception.audio_signal(f"Clicking {top_name}")
            
            final_success = mouse.left_click(top_x, top_y)
            
            if final_success:
                print(f"   ✅ Final click successful")
                time.sleep(3)
            else:
                print(f"   ❌ Final click failed")
        else:
            print(f"   ⚠️ No elements detected for final click")
        
        # Final Results
        print(f"\n📊 M2 FUNCTIONAL VALIDATION RESULTS")
        print("=" * 45)
        print(f"✅ Main menu context: {'SUCCESS' if main_menu_context == 'MAIN_MENU' else 'PARTIAL'}")
        print(f"✅ Single Player click: SUCCESS")
        print(f"✅ Submenu context: {'SUCCESS' if submenu_context == 'SINGLE_PLAYER_SUB_MENU' else 'PARTIAL'}")
        print(f"✅ Template Overlap Prevention: {'SUCCESS' if not single_player_detected else 'FAILED'}")
        print(f"✅ Element detection: SUCCESS ({len(detected_elements)} elements)")
        
        # Overall success determination
        overall_success = (
            main_menu_context == 'MAIN_MENU' and
            submenu_context == 'SINGLE_PLAYER_SUB_MENU' and
            not single_player_detected and
            len(detected_elements) > 0
        )
        
        if overall_success:
            print(f"\n🎉 M2 VALIDATION SUCCESS - READY FOR LOCKDOWN")
            perception.audio_signal("M2 validation complete - Template overlap prevention successful")
        else:
            print(f"\n❌ M2 VALIDATION PARTIAL - NEEDS REFINEMENT")
            perception.audio_signal("M2 validation incomplete - requires additional work")
        
        return overall_success, {
            'main_menu_context': main_menu_context,
            'submenu_context': submenu_context,
            'template_overlap_prevented': not single_player_detected,
            'elements_detected': len(detected_elements),
            'element_names': element_names
        }
        
    except Exception as e:
        print(f"\n❌ M2 FUNCTIONAL VALIDATION FAILED: {e}")
        print(f"   Check that Dune Legacy is running and accessible")
        return False, {'error': str(e)}

def main():
    """Run M2 functional validation."""
    success, results = execute_m2_functional_validation()
    
    print(f"\n📋 VALIDATION SUMMARY:")
    if success:
        print(f"🎉 M2 LEVEL-1 ARCHITECTURAL CORRECTION: VALIDATED")
        print(f"✅ Screen Context Identifier: WORKING")
        print(f"✅ Template Overlap Prevention: WORKING")
        print(f"✅ Perception Fusion: WORKING")
        print(f"📦 READY FOR M2 LOCKDOWN COMMIT")
    else:
        print(f"❌ M2 VALIDATION INCOMPLETE")
        print(f"🔧 Additional work required before lockdown")
    
    return success

if __name__ == "__main__":
    main()