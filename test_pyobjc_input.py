#!/usr/bin/env python3
"""
DIAGNOSIS MANDATE: Test pyobjc (CoreGraphics) mouse control
Target: Req 2.1 (Input Emulation) validation for Risk R2 mitigation
"""

import sys
from Quartz import CGEventCreate, CGEventPost, CGEventCreateMouseEvent
from Quartz import kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp
from Quartz import kCGMouseButtonLeft, kCGHIDEventTap
import time

def test_pyobjc_mouse_movement():
    """Test minimal mouse movement using pyobjc CoreGraphics"""
    print("🖱️ PYOBJC MOUSE CONTROL DIAGNOSIS")
    print("=" * 40)
    print("Testing Req 2.1 (Input Emulation) compliance...")
    
    try:
        # Get current mouse position first
        import Quartz
        current_pos = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        print(f"📍 Current mouse position: ({current_pos.x:.0f}, {current_pos.y:.0f})")
        
        # Test 1: Simple mouse movement to top-left corner
        print("\n🎯 Test 1: Moving mouse to (100, 100)")
        target_x, target_y = 100, 100
        
        # Create mouse move event
        move_event = CGEventCreateMouseEvent(
            None,  # source
            kCGEventMouseMoved,  # type
            (target_x, target_y),  # location
            kCGMouseButtonLeft  # button (not used for move)
        )
        
        if move_event is None:
            print("❌ CRITICAL: Failed to create mouse event - pyobjc API issue")
            return False
            
        # Post the event
        CGEventPost(kCGHIDEventTap, move_event)
        print("✅ Mouse move event posted successfully")
        
        # Wait and check new position
        time.sleep(0.5)
        new_pos = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        print(f"📍 New mouse position: ({new_pos.x:.0f}, {new_pos.y:.0f})")
        
        # Validate movement
        if abs(new_pos.x - target_x) < 5 and abs(new_pos.y - target_y) < 5:
            print("✅ SUCCESS: Mouse moved correctly - pyobjc permissions OK")
            return True
        else:
            print("❌ FAILURE: Mouse did NOT move - PERMISSION ISSUE DETECTED")
            print(f"   Expected: ({target_x}, {target_y})")
            print(f"   Actual: ({new_pos.x:.0f}, {new_pos.y:.0f})")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: pyobjc mouse control failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_pyobjc_click():
    """Test mouse clicking functionality"""
    print("\n🎯 Test 2: Mouse click capability")
    
    try:
        # Get current position for safe clicking
        import Quartz
        current_pos = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        click_x, click_y = current_pos.x, current_pos.y
        
        print(f"📍 Testing click at current position: ({click_x:.0f}, {click_y:.0f})")
        
        # Create mouse down event
        mouse_down = CGEventCreateMouseEvent(
            None,
            kCGEventLeftMouseDown,
            (click_x, click_y),
            kCGMouseButtonLeft
        )
        
        # Create mouse up event
        mouse_up = CGEventCreateMouseEvent(
            None,
            kCGEventLeftMouseUp,
            (click_x, click_y),
            kCGMouseButtonLeft
        )
        
        if mouse_down is None or mouse_up is None:
            print("❌ CRITICAL: Failed to create click events")
            return False
        
        # Post click events
        CGEventPost(kCGHIDEventTap, mouse_down)
        time.sleep(0.05)  # Brief delay between down/up
        CGEventPost(kCGHIDEventTap, mouse_up)
        
        print("✅ Click events posted successfully")
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: pyobjc click failed: {e}")
        return False

def main():
    print("🔍 PYOBJC INPUT EMULATION DIAGNOSIS")
    print("=" * 50)
    print("Validating Req 2.1 compliance for Risk R2 mitigation")
    print("Target: Resolve macOS security permissions for CoreGraphics")
    print()
    
    # Test movement first
    movement_ok = test_pyobjc_mouse_movement()
    
    if movement_ok:
        # Test clicking if movement works
        click_ok = test_pyobjc_click()
        
        if click_ok:
            print("\n🎉 DIAGNOSIS COMPLETE: pyobjc input control WORKING")
            print("✅ Req 2.1 (Input Emulation): VALIDATED")
            print("✅ Risk R2 (Input Instability): MITIGATED")
        else:
            print("\n⚠️ PARTIAL SUCCESS: Movement OK, clicking failed")
            
    else:
        print("\n🔐 PERMISSION ISSUE DETECTED")
        print("=" * 30)
        print("REQUIRED FIXES:")
        print("1. Open System Settings/Preferences")
        print("2. Go to Privacy & Security → Accessibility")
        print("3. Add Terminal (or your Python app) with ✓ enabled")
        print("4. Go to Privacy & Security → Input Monitoring") 
        print("5. Add Terminal (or your Python app) with ✓ enabled")
        print("\n⚠️ You may need to restart Terminal after changes")
        print("\n🔄 Rerun this script after fixing permissions")

if __name__ == "__main__":
    main()