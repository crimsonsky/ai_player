#!/usr/bin/env python3
"""
R1 FIX FUNCTIONAL VALIDATION TEST
Tests Template Overlap Prevention via Perception Fusion (Module 2C + 2D)

CRITICAL TEST: Verify 'Single Player' template does NOT match on Menu 2
"""

import subprocess
import time
import os
import sys

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mouse_control import MouseController

def execute_r1_fix_validation():
    """Execute the R1 fix functional validation test."""
    
    print("🧪 R1 FIX FUNCTIONAL VALIDATION TEST")
    print("=" * 50)
    print("OBJECTIVE: Validate Template Overlap Prevention")
    print("CRITICAL CHECK: 'Single Player' template must NOT match Menu 2 elements")
    print("TEST SEQUENCE: Main Menu → Click Single Player → New Screen → Validate")
    print()
    
    try:
        # Initialize mouse controller
        mouse = MouseController()
        
        # Focus Dune Legacy
        print("🎮 Step 1: Focusing Dune Legacy...")
        subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                      capture_output=True)
        time.sleep(3)
        
        # Audio signal start
        subprocess.run(['say', 'Test Action Signalling - R1 Fix Validation Start'], capture_output=True)
        
        # Import perception module 
        print("📦 Step 2: Loading Enhanced Perception Module...")
        from src.perception.perception_module import PerceptionModule
        
        # Initialize perception with enhanced configuration
        config = {
            'confidence_threshold': 0.95,
            'audio_feedback': True
        }
        
        perception = PerceptionModule(config)
        
        # Step 3: Initial Screen Analysis
        print("\n📸 Step 3: Initial Main Menu Analysis...")
        initial_screenshot = perception.capture_screen()
        
        if not initial_screenshot:
            raise Exception("Failed to capture initial screenshot")
        
        print("🔍 Running Perception Fusion on Main Menu...")
        main_menu_analysis = perception.analyze_menu_screen(initial_screenshot)
        
        # Find Single Player button
        single_player_element = None
        for element in main_menu_analysis["elements_detected"]:
            text_label = (element.get("text_label") or "").lower()
            if ("single" in text_label or "player" in text_label or 
                "single" in element["template_id"].lower()):
                single_player_element = element
                break
        
        if not single_player_element:
            raise Exception("Single Player button not found on main menu")
        
        print(f"✅ Single Player found: {single_player_element['template_id']}")
        print(f"   Text Label: '{single_player_element.get('text_label', 'N/A')}'")
        print(f"   Position: ({single_player_element['normalized_x']:.3f}, {single_player_element['normalized_y']:.3f})")
        
        # Audio signal detection success
        subprocess.run(['say', 'Test Action Signalling - Single Player Detection Success'], capture_output=True)
        
        # Step 4: Click Single Player (Screen Transition)
        print("\n🖱️ Step 4: Clicking Single Player Button...")
        
        # Convert normalized coordinates to absolute
        screen_width = 3440  # Adjust based on your screen
        screen_height = 1440
        
        abs_x = int(single_player_element['normalized_x'] * screen_width)
        abs_y = int(single_player_element['normalized_y'] * screen_height)
        
        print(f"   Clicking at absolute coordinates: ({abs_x}, {abs_y})")
        
        success = mouse.left_click(abs_x, abs_y)
        
        if not success:
            raise Exception("Failed to click Single Player button")
        
        # Audio signal action success
        subprocess.run(['say', 'Test Action Signalling - Action Success'], capture_output=True)
        
        # Wait for screen transition
        print("⏳ Waiting for screen transition...")
        time.sleep(4)
        
        # Step 5: NEW SCREEN ANALYSIS (Critical R1 Test)
        print("\n🔍 Step 5: CRITICAL R1 TEST - New Screen Analysis...")
        print("   Testing Template Overlap Prevention...")
        
        new_screenshot = perception.capture_screen()
        if not new_screenshot:
            raise Exception("Failed to capture new screen screenshot")
        
        print("🔍 Running Perception Fusion on New Menu...")
        new_menu_analysis = perception.analyze_menu_screen(new_screenshot)
        
        # Step 6: Validate Template Overlap Prevention
        print("\n📊 Step 6: R1 VALIDATION - Template Overlap Check...")
        
        detected_buttons = new_menu_analysis["elements_detected"]
        
        print(f"   Total elements detected on new screen: {len(detected_buttons)}")
        
        # CRITICAL CHECK: Look for invalid Single Player matches
        invalid_single_player_matches = []
        valid_buttons = []
        
        for element in detected_buttons:
            template_id = element["template_id"]
            text_label = element.get("text_label", "")
            
            print(f"   🎯 Element: {element['name']}")
            print(f"      Template ID: {template_id}")
            print(f"      Text Label: '{text_label}'")
            print(f"      Functional Button: {element.get('is_functional_button', True)}")
            
            # Check for Single Player template overlap
            if ("single" in template_id.lower() or "player" in template_id.lower()):
                if text_label and not any(word in text_label.lower() for word in ['single', 'player']):
                    invalid_single_player_matches.append({
                        'template_id': template_id,
                        'text_label': text_label,
                        'element': element
                    })
                    print(f"      ❌ INVALID MATCH: Single Player template with '{text_label}' text")
                else:
                    print(f"      ✅ Valid Single Player match")
            else:
                valid_buttons.append(element)
        
        # Step 7: Audio Output (Master Verification)
        print("\n📢 Step 7: AUDIO ANNOUNCEMENT - Master Verification...")
        
        button_names = []
        for element in valid_buttons:
            if element.get('is_functional_button', True):
                text_label = element.get('text_label', element.get('name', 'Unknown'))
                button_names.append(text_label)
        
        if button_names:
            announcement = f"Detected {len(button_names)} valid buttons: " + ", ".join(button_names)
            print(f"   📢 {announcement}")
            subprocess.run(['say', announcement], capture_output=True)
        else:
            announcement = "No valid buttons detected on new screen"
            print(f"   📢 {announcement}")
            subprocess.run(['say', announcement], capture_output=True)
        
        # Step 8: R1 Validation Results
        print(f"\n🎯 R1 FIX VALIDATION RESULTS:")
        print("=" * 40)
        
        r1_fix_success = len(invalid_single_player_matches) == 0
        
        if r1_fix_success:
            print("✅ R1 FIX: SUCCESS")
            print("   ✅ No invalid Single Player template matches on Menu 2")
            print("   ✅ Template Overlap Prevention working correctly")
            print("   ✅ Perception Fusion (2C + 2D) validated")
            
            subprocess.run(['say', 'R1 Fix Validation Successful - Template overlap prevention confirmed'], capture_output=True)
        else:
            print("❌ R1 FIX: FAILED")
            print(f"   ❌ Found {len(invalid_single_player_matches)} invalid Single Player matches:")
            for match in invalid_single_player_matches:
                print(f"      - {match['template_id']} matched '{match['text_label']}'")
            
            subprocess.run(['say', 'R1 Fix Validation Failed - Template overlap still occurring'], capture_output=True)
        
        # Step 9: Click Top Button (if valid buttons found)
        if valid_buttons and r1_fix_success:
            print("\n🖱️ Step 9: Clicking Top-most Valid Button...")
            
            # Find top-most button (lowest y coordinate)
            top_button = min(valid_buttons, key=lambda b: b['normalized_y'])
            
            abs_x = int(top_button['normalized_x'] * screen_width)
            abs_y = int(top_button['normalized_y'] * screen_height)
            
            print(f"   Top button: '{top_button.get('text_label', top_button['name'])}'")
            print(f"   Clicking at: ({abs_x}, {abs_y})")
            
            mouse.left_click(abs_x, abs_y)
            subprocess.run(['say', 'Test Action Signalling - Final Action'], capture_output=True)
        
        # Save comprehensive results
        results_file = "/tmp/r1_fix_validation_results.txt"
        with open(results_file, "w") as f:
            f.write("R1 FIX FUNCTIONAL VALIDATION RESULTS\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("TEST OBJECTIVE:\n")
            f.write("Validate Template Overlap Prevention via Perception Fusion (2C + 2D)\n")
            f.write("Prevent Menu 1 'Single Player' template from matching Menu 2 elements\n\n")
            
            f.write("MAIN MENU ANALYSIS:\n")
            f.write(f"Single Player Button Found: {single_player_element['template_id']}\n")
            f.write(f"Text Label: '{single_player_element.get('text_label', 'N/A')}'\n")
            f.write(f"Position: ({single_player_element['normalized_x']:.3f}, {single_player_element['normalized_y']:.3f})\n\n")
            
            f.write("NEW SCREEN ANALYSIS:\n")
            f.write(f"Total Elements Detected: {len(detected_buttons)}\n")
            f.write(f"Valid Buttons: {len(valid_buttons)}\n")
            f.write(f"Invalid Single Player Matches: {len(invalid_single_player_matches)}\n\n")
            
            f.write("DETECTED BUTTONS ON NEW SCREEN:\n")
            for element in valid_buttons:
                f.write(f"  {element['name']}: '{element.get('text_label', 'N/A')}'\n")
            
            f.write(f"\nR1 FIX VALIDATION: {'SUCCESS' if r1_fix_success else 'FAILED'}\n")
            f.write(f"Template Overlap Prevention: {'WORKING' if r1_fix_success else 'NEEDS DEBUGGING'}\n")
        
        print(f"\n💾 Detailed results saved: {results_file}")
        
        return r1_fix_success, {
            'main_menu_single_player': single_player_element,
            'new_screen_buttons': len(valid_buttons),
            'invalid_matches': len(invalid_single_player_matches),
            'r1_fix_working': r1_fix_success
        }
        
    except Exception as e:
        print(f"\n❌ R1 FIX VALIDATION TEST FAILED: {e}")
        subprocess.run(['say', f'R1 Fix validation failed: {str(e)}'], capture_output=True)
        return False, {'error': str(e)}

def main():
    """Execute R1 fix functional validation test."""
    
    success, results = execute_r1_fix_validation()
    
    if success:
        print("\n🎉 R1 FIX FUNCTIONAL VALIDATION: SUCCESS")
        print("✅ Template Overlap Prevention confirmed working")
        print("✅ Perception Fusion (2C + 2D) validated")
        print("✅ Ready for M2 Lockdown Commit")
    else:
        print("\n❌ R1 FIX FUNCTIONAL VALIDATION: FAILED")
        print("   Additional debugging required before M2 lockdown")
        
    return success

if __name__ == "__main__":
    main()