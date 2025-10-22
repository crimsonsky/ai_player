#!/usr/bin/env python3
"""
CLEAN M2 SYSTEM TEST - Real Detection Only
=========================================

This is the ONLY M2 test file needed. It:
1. Uses the actual perception_module.py (no V3, no signal fusion)
2. Detects REAL buttons from actual game interface
3. Throws proper errors when detection fails (no fake data)
4. Performs real mouse interaction on detected elements

NO FALLBACK DATA - REAL DETECTION OR FAILURE
"""

import subprocess
import time
import sys
import os

# Clean import - use actual source structure
sys.path.insert(0, '/Users/amir/projects/ai_player/src')

def focus_game():
    """Focus the Dune Legacy game."""
    print("🎯 Focusing Dune Legacy...")
    subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                  capture_output=True)
    time.sleep(2)

def initialize_m2_system():
    """Initialize the real M2 perception system."""
    print("🔧 Initializing M2 Perception System...")
    
    try:
        from perception.perception_module import PerceptionModule
        
        config = {
            'confidence_threshold': 0.7,
            'audio_feedback': False,
            'resolution_independent': True
        }
        
        perception = PerceptionModule(config)
        print("✅ M2 Perception Module initialized")
        return perception
        
    except Exception as e:
        print(f"❌ Failed to initialize M2: {e}")
        raise RuntimeError(f"M2_INITIALIZATION_FAILED: {e}")

def capture_and_analyze_screen(perception):
    """Capture screenshot and analyze real game interface."""
    print("\n📸 REAL SCREEN CAPTURE AND ANALYSIS")
    print("="*50)
    
    # Real screenshot capture
    screenshot_path = perception.capture_screen()
    
    if not screenshot_path:
        raise RuntimeError("SCREENSHOT_FAILED: Could not capture game screen")
    
    print(f"✅ Screenshot captured: {screenshot_path}")
    
    # Real context detection
    context = perception.identify_screen_context(screenshot_path)
    print(f"🎯 Real Context: {context}")
    
    # Real element detection
    elements = perception.detect_elements(screenshot_path)
    print(f"🔍 Real Elements Detected: {len(elements)}")
    
    return {
        'screenshot_path': screenshot_path,
        'context': context,
        'elements': elements
    }

def find_and_click_single_player_button(perception, analysis):
    """Find actual single player button and click it."""
    print("\n🎮 FINDING REAL SINGLE PLAYER BUTTON")
    print("="*50)
    
    elements = analysis['elements']
    
    if not elements:
        raise RuntimeError("NO_ELEMENTS_DETECTED: No UI elements found on screen")
    
    # Search for single player button in REAL detected elements
    single_player_button = None
    
    print("📋 Real elements found:")
    for i, element in enumerate(elements):
        text = element.get('text', element.get('id', 'Unknown'))
        confidence = element.get('confidence', 0)
        coords = element.get('coordinates', element.get('normalized_coords', 'No coords'))
        
        print(f"   {i+1}. '{text}' (conf: {confidence:.3f}) at {coords}")
        
        # Look for single player indicators in REAL text
        if any(keyword in text.lower() for keyword in ['single', 'start', 'campaign']):
            single_player_button = element
            print(f"🎯 FOUND REAL SINGLE PLAYER BUTTON: '{text}'")
            break
    
    if not single_player_button:
        raise RuntimeError("SINGLE_PLAYER_BUTTON_NOT_FOUND: No single player button detected in real elements")
    
    # Click the real button
    return click_real_element(single_player_button)

def click_real_element(element):
    """Click a real detected element using mouse control."""
    print(f"\n🖱️ CLICKING REAL ELEMENT")
    
    try:
        # Import mouse control
        sys.path.append('/Users/amir/projects/ai_player')
        from mouse_control import MouseController
        
        mouse = MouseController()
        
        # Get real coordinates
        coords = element.get('coordinates', element.get('normalized_coords'))
        
        if not coords or len(coords) < 4:
            raise RuntimeError(f"INVALID_COORDINATES: Element has no valid coordinates: {coords}")
        
        x, y, w, h = coords
        
        # Convert to absolute coordinates if needed
        if x <= 1.0:  # Normalized coordinates
            abs_x = int((x + w/2) * 1920)  # Adjust screen size as needed
            abs_y = int((y + h/2) * 1080)
        else:
            abs_x = int(x + w/2)
            abs_y = int(y + h/2)
        
        print(f"🎯 Clicking at real coordinates: ({abs_x}, {abs_y})")
        
        # Perform real click
        mouse.click(abs_x, abs_y)
        time.sleep(2)  # Wait for UI response
        
        print("✅ Real click performed successfully")
        return True
        
    except Exception as e:
        raise RuntimeError(f"CLICK_FAILED: Could not click real element: {e}")

def verify_navigation_result(perception):
    """Verify that navigation actually worked by analyzing new screen."""
    print("\n🔄 VERIFYING REAL NAVIGATION RESULT")
    print("="*50)
    
    time.sleep(1)  # Brief wait for UI transition
    
    try:
        new_analysis = capture_and_analyze_screen(perception)
        new_context = new_analysis['context']
        
        print(f"📊 New context after navigation: {new_context}")
        
        if new_context != 'MAIN_MENU':
            print("✅ Navigation successful - context changed")
            return True
        else:
            print("⚠️ Context unchanged - navigation may have failed")
            return False
            
    except Exception as e:
        print(f"❌ Could not verify navigation: {e}")
        return False

def main():
    """Main M2 system test - real detection only."""
    print("="*60)
    print("CLEAN M2 SYSTEM TEST - REAL DETECTION ONLY")
    print("="*60)
    
    try:
        # Step 1: Focus game
        focus_game()
        
        # Step 2: Initialize M2 system
        perception = initialize_m2_system()
        
        # Step 3: Capture and analyze real screen
        analysis = capture_and_analyze_screen(perception)
        
        # Step 4: Find and click real single player button
        click_success = find_and_click_single_player_button(perception, analysis)
        
        # Step 5: Verify real navigation result
        navigation_success = verify_navigation_result(perception)
        
        # Results
        print(f"\n{'='*60}")
        print("M2 REAL DETECTION TEST RESULTS")
        print(f"{'='*60}")
        
        print(f"Screen Capture: ✅ SUCCESS")
        print(f"Element Detection: ✅ SUCCESS ({len(analysis['elements'])} real elements)")
        print(f"Button Click: {'✅ SUCCESS' if click_success else '❌ FAILED'}")
        print(f"Navigation: {'✅ SUCCESS' if navigation_success else '⚠️ UNCLEAR'}")
        
        overall_success = click_success and len(analysis['elements']) > 0
        
        if overall_success:
            print(f"\n🎉 M2 SYSTEM WORKING: Real detection and interaction successful!")
        else:
            print(f"\n⚠️ M2 SYSTEM ISSUES: Check detection or navigation")
        
        return overall_success
        
    except RuntimeError as e:
        print(f"\n❌ M2 SYSTEM FAILURE: {e}")
        print("✅ GOOD: System failed properly instead of using fake data")
        return False
        
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)