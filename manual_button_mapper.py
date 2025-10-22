#!/usr/bin/env python3
"""
Manual Button Coordinate Mapping Tool
Use mouse clicks to identify actual button positions in Dune Legacy

CRITICAL: This tool will help us discover the REAL button coordinates
since our current detection system is using wrong placeholder values.
"""

import cv2
import subprocess
import time
from mouse_control import MouseController

def capture_screenshot(path):
    """Capture current screenshot."""
    try:
        subprocess.run(['screencapture', '-x', path], capture_output=True, timeout=5)
        return True
    except:
        return False

def audio_signal(message):
    """Provide audio feedback."""
    try:
        subprocess.run(['say', message], capture_output=True, timeout=3)
    except:
        print(f"🔊 Audio: {message}")

def get_screen_dimensions(screenshot_path):
    """Get screen dimensions from screenshot."""
    img = cv2.imread(screenshot_path)
    if img is None:
        return None, None
    height, width = img.shape[:2]
    return width, height

def focus_dune_legacy():
    """Focus Dune Legacy window."""
    focus_script = '''
    tell application "Dune Legacy"
        activate
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', focus_script], capture_output=True, text=True)
    return result.returncode == 0

def manual_button_mapping():
    """Interactive tool to manually map button coordinates."""
    
    print("🎯 MANUAL BUTTON COORDINATE MAPPING")
    print("=" * 50)
    print("This tool will help us find the REAL button coordinates")
    print("by clicking and testing each button position manually.")
    print()
    
    # Initialize mouse controller
    mouse = MouseController()
    
    # Focus game
    print("🎮 Focusing Dune Legacy...")
    if focus_dune_legacy():
        print("✅ Game focused")
    else:
        print("⚠️ Focus may have failed")
    
    time.sleep(2)
    
    # Take initial screenshot
    screenshot_path = "/tmp/dune_legacy_mapping.png"
    capture_screenshot(screenshot_path)
    
    # Get dimensions
    width, height = get_screen_dimensions(screenshot_path)
    print(f"📐 Screen dimensions: {width}x{height}")
    
    # Button mapping data
    button_coordinates = {}
    
    # Expected buttons in Dune Legacy main menu
    expected_buttons = [
        "Single Player",
        "Multi Player", 
        "Options",
        "Map Editor",
        "Replay",
        "Quit"
    ]
    
    print("\n📋 Buttons to map:")
    for i, button in enumerate(expected_buttons, 1):
        print(f"   {i}. {button}")
    
    print("\n" + "="*50)
    print("MANUAL MAPPING PROCESS:")
    print("1. Look at the Dune Legacy main menu")
    print("2. For each button, we'll click at different positions")
    print("3. You tell us which button was actually clicked")
    print("4. We'll record the correct coordinates")
    print("="*50)
    
    # Manual coordinate discovery
    for button_name in expected_buttons:
        print(f"\n🎯 MAPPING: {button_name}")
        print("-" * 30)
        
        found = False
        attempts = 0
        max_attempts = 3
        
        while not found and attempts < max_attempts:
            attempts += 1
            
            # Get current mouse position as starting point
            current_x, current_y = mouse.get_position()
            print(f"📍 Current mouse: ({current_x:.0f}, {current_y:.0f})")
            
            print(f"\nAttempt {attempts}/{max_attempts} for {button_name}")
            print("Instructions:")
            print("1. Move your mouse over the button you want to map")
            print("2. Press Enter when positioned correctly")
            print("3. We'll click at that position and you confirm")
            
            input(">>> Position mouse over the button and press Enter...")
            
            # Get the position where user placed mouse
            target_x, target_y = mouse.get_position()
            print(f"🎯 Target position: ({target_x:.0f}, {target_y:.0f})")
            
            # Confirm before clicking
            print(f"About to click at ({target_x:.0f}, {target_y:.0f})")
            confirm = input("Press Enter to click, 'r' to reposition, 's' to skip: ").strip().lower()
            
            if confirm == 's':
                print(f"⏭️ Skipping {button_name}")
                break
            elif confirm == 'r':
                print("🔄 Repositioning...")
                continue
            
            # Perform the click
            print(f"🖱️ Clicking at ({target_x:.0f}, {target_y:.0f})...")
            audio_signal(f"Clicking at position")
            
            success = mouse.left_click(target_x, target_y)
            
            if success:
                time.sleep(1)  # Wait for UI response
                
                print("👀 VERIFICATION:")
                print(f"What happened after clicking at ({target_x:.0f}, {target_y:.0f})?")
                print("Options:")
                print("1. Correct button was clicked ✅")
                print("2. Wrong button was clicked ❌")
                print("3. Nothing happened ❌")
                print("4. Game state changed unexpectedly ❌")
                
                result = input("Enter 1, 2, 3, or 4: ").strip()
                
                if result == '1':
                    # Success! Record coordinates
                    button_coordinates[button_name] = {
                        'pixel_coords': (target_x, target_y),
                        'normalized_coords': (target_x / width, target_y / height)
                    }
                    
                    print(f"✅ SUCCESS: {button_name} mapped to ({target_x:.0f}, {target_y:.0f})")
                    print(f"   Normalized: ({target_x/width:.4f}, {target_y/height:.4f})")
                    
                    found = True
                    
                    # Go back to main menu if we entered a sub-menu
                    if button_name in ["Options", "Single Player", "Multi Player", "Map Editor", "Replay"]:
                        print("🔙 Returning to main menu...")
                        time.sleep(1)
                        # Press Escape to return to main menu
                        subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], 
                                     capture_output=True)
                        time.sleep(2)
                
                else:
                    print(f"❌ Incorrect click for {button_name}")
                    if result == '2':
                        actual_button = input("Which button was actually clicked? ")
                        print(f"📝 Note: Position ({target_x:.0f}, {target_y:.0f}) clicks '{actual_button}'")
            
            else:
                print("❌ Click failed")
        
        if not found and attempts >= max_attempts:
            print(f"⚠️ Could not map {button_name} after {max_attempts} attempts")
    
    # Display results
    print("\n" + "="*50)
    print("🎯 BUTTON MAPPING RESULTS")
    print("="*50)
    
    if button_coordinates:
        for button_name, coords in button_coordinates.items():
            px, py = coords['pixel_coords']
            nx, ny = coords['normalized_coords']
            print(f"{button_name:15} | Pixel: ({px:4.0f}, {py:4.0f}) | Normalized: ({nx:.4f}, {ny:.4f})")
        
        # Save results to file
        results_file = "/tmp/button_coordinates_real.txt"
        with open(results_file, 'w') as f:
            f.write("# REAL BUTTON COORDINATES - Manually Mapped\n")
            f.write(f"# Screen Resolution: {width}x{height}\n")
            f.write(f"# Mapped on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("PIXEL_COORDINATES = {\n")
            for button_name, coords in button_coordinates.items():
                px, py = coords['pixel_coords']
                f.write(f'    "{button_name}": ({px:.0f}, {py:.0f}),\n')
            f.write("}\n\n")
            
            f.write("NORMALIZED_COORDINATES = {\n")
            for button_name, coords in button_coordinates.items():
                nx, ny = coords['normalized_coords']
                f.write(f'    "{button_name}": ({nx:.4f}, {ny:.4f}),\n')
            f.write("}\n")
        
        print(f"\n💾 Results saved to: {results_file}")
        
    else:
        print("⚠️ No buttons were successfully mapped")
    
    print("\n🏁 Manual mapping complete!")
    audio_signal("Button mapping complete")

if __name__ == "__main__":
    manual_button_mapping()