#!/usr/bin/env python3
"""
Test Estimated Button Coordinates
Quick test of the estimated button positions from screenshot analysis
"""

import time
from mouse_control import MouseController

def test_estimated_coordinates():
    """Test the estimated button coordinates one by one."""
    
    print("🎯 TESTING ESTIMATED BUTTON COORDINATES")
    print("=" * 50)
    
    # Initialize mouse
    mouse = MouseController()
    
    # Estimated coordinates from analysis
    estimated_buttons = {
        "Single Player": (1720, 480),
        "Multi Player": (1720, 560), 
        "Options": (1720, 640),
        "Map Editor": (1720, 720),
        "Replay": (1720, 800),
        "Quit": (1720, 880)
    }
    
    print("📋 Estimated coordinates to test:")
    for name, coords in estimated_buttons.items():
        x, y = coords
        print(f"   {name:15} | ({x:4d}, {y:4d})")
    
    # Focus game first
    import subprocess
    print("\n🎮 Focusing Dune Legacy...")
    subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], capture_output=True)
    time.sleep(2)
    
    # Test each button
    for button_name, (x, y) in estimated_buttons.items():
        print(f"\n🎯 TESTING: {button_name}")
        print(f"   Target: ({x}, {y})")
        
        # Ask user if they want to test this one
        response = input(f"   Test {button_name}? (y/n/q): ").strip().lower()
        
        if response == 'q':
            print("🛑 Testing stopped by user")
            break
        elif response == 'n':
            print(f"⏭️ Skipping {button_name}")
            continue
        
        # Perform click
        print(f"🖱️ Clicking {button_name} at ({x}, {y})...")
        success = mouse.left_click(x, y)
        
        if success:
            time.sleep(1)  # Wait for response
            
            print("👀 RESULT CHECK:")
            actual = input(f"   What happened? (correct button / wrong button / nothing): ").strip().lower()
            
            if "correct" in actual:
                print(f"✅ SUCCESS: {button_name} is at ({x}, {y})")
            elif "wrong" in actual:
                wrong_button = input("   Which button was actually clicked? ")
                print(f"❌ WRONG: ({x}, {y}) clicks '{wrong_button}', not {button_name}")
            else:
                print(f"❌ NO RESPONSE: ({x}, {y}) may be empty space")
            
            # Return to main menu if needed
            if button_name != "Quit":
                print("🔙 Returning to main menu (pressing Escape)...")
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'], capture_output=True)
                time.sleep(2)
        else:
            print(f"❌ Click failed for {button_name}")
    
    print("\n🏁 Coordinate testing complete!")

if __name__ == "__main__":
    test_estimated_coordinates()