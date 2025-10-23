"""
NEW Module 2: Input Emulation API - AIP-SDS-V2.3
Level-6 Architectural Implementation

This module provides a clean, precise input control API using pyobjc CoreGraphics
for pixel-perfect, non-blocking input emulation on macOS.

MANDATE: Replace all deprecated rule-based vision systems with learning-based
AI perception, starting with a robust input control foundation.
"""

import time
import math
from typing import Tuple, Optional
from Quartz import (
    CGEventCreateMouseEvent, CGEventPost, CGEventCreateKeyboardEvent,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventRightMouseDown, 
    kCGEventRightMouseUp, kCGEventMouseMoved, kCGEventKeyDown, kCGEventKeyUp,
    kCGMouseButtonLeft, kCGMouseButtonRight, kCGHIDEventTap,
    kCGEventSourceStateHIDSystemState
)
from Quartz.CoreGraphics import CGEventSourceCreate


class InputAPI:
    """
    NEW Module 2: Input Emulation API - AIP-SDS-V2.3
    
    Provides precise, low-latency input control using pyobjc CoreGraphics.
    Implements all required input methods for autonomous game interaction.
    """
    
    def __init__(self, config: dict = None):
        """Initialize Input API with configuration."""
        self.config = config or {}
        self.audio_feedback = self.config.get('audio_feedback', False)
        
        # Create CoreGraphics event source
        self.event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
        
        if self.audio_feedback:
            self._audio_signal("Input API initialized - NEW M2 ready")
    
    def _audio_signal(self, message: str):
        """Provide audio feedback for debugging."""
        if self.audio_feedback:
            print(f"🔊 INPUT API: {message}")
    
    def move_mouse(self, x: int, y: int, duration: float = 0.1) -> bool:
        """
        Smooth movement of cursor to target coordinates with human-like interpolation.
        
        Args:
            x: Target X coordinate (pixels)
            y: Target Y coordinate (pixels)  
            duration: Movement duration in seconds (default 0.1)
            
        Returns:
            bool: Success status
        """
        try:
            # Get current cursor position for smooth interpolation
            from Quartz import CGEventGetLocation, CGEventCreate, kCGEventMouseMoved
            
            # Create a dummy event to get current position
            current_event = CGEventCreate(None)
            current_pos = CGEventGetLocation(current_event)
            
            start_x, start_y = int(current_pos.x), int(current_pos.y)
            
            # Calculate movement parameters
            distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            steps = max(int(distance / 5), 10)  # Minimum 10 steps for smoothness
            step_duration = duration / steps
            
            self._audio_signal(f"Moving mouse from ({start_x}, {start_y}) to ({x}, {y})")
            
            # Perform smooth movement with non-linear interpolation
            for i in range(steps + 1):
                # Use easing function for human-like movement
                progress = i / steps
                eased_progress = self._ease_in_out_cubic(progress)
                
                # Calculate intermediate position
                current_x = start_x + (x - start_x) * eased_progress
                current_y = start_y + (y - start_y) * eased_progress
                
                # Create and post mouse move event
                move_event = CGEventCreateMouseEvent(
                    self.event_source,
                    kCGEventMouseMoved,
                    (current_x, current_y),
                    kCGMouseButtonLeft
                )
                CGEventPost(kCGHIDEventTap, move_event)
                
                # Small delay for smooth movement
                if i < steps:
                    time.sleep(step_duration)
            
            return True
            
        except Exception as e:
            self._audio_signal(f"Mouse movement failed: {e}")
            return False
    
    def left_click(self, x: int, y: int) -> bool:
        """
        Precise left mouse button click at target coordinates.
        
        Args:
            x: Click X coordinate (pixels)
            y: Click Y coordinate (pixels)
            
        Returns:
            bool: Success status
        """
        try:
            self._audio_signal(f"Left clicking at ({x}, {y})")
            
            # Move to target position first
            self.move_mouse(x, y, duration=0.05)
            
            # Create mouse down event
            mouse_down = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventLeftMouseDown,
                (x, y),
                kCGMouseButtonLeft
            )
            
            # Create mouse up event
            mouse_up = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventLeftMouseUp,
                (x, y),
                kCGMouseButtonLeft
            )
            
            # Post events with proper timing
            CGEventPost(kCGHIDEventTap, mouse_down)
            time.sleep(0.01)  # Brief hold for reliable click
            CGEventPost(kCGHIDEventTap, mouse_up)
            
            return True
            
        except Exception as e:
            self._audio_signal(f"Left click failed: {e}")
            return False
    
    def right_click(self, x: int, y: int) -> bool:
        """
        Precise right mouse button click for context menus.
        
        Args:
            x: Click X coordinate (pixels)
            y: Click Y coordinate (pixels)
            
        Returns:
            bool: Success status
        """
        try:
            self._audio_signal(f"Right clicking at ({x}, {y})")
            
            # Move to target position first
            self.move_mouse(x, y, duration=0.05)
            
            # Create right mouse down event
            mouse_down = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventRightMouseDown,
                (x, y),
                kCGMouseButtonRight
            )
            
            # Create right mouse up event
            mouse_up = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventRightMouseUp,
                (x, y),
                kCGMouseButtonRight
            )
            
            # Post events with proper timing
            CGEventPost(kCGHIDEventTap, mouse_down)
            time.sleep(0.01)  # Brief hold for reliable click
            CGEventPost(kCGHIDEventTap, mouse_up)
            
            return True
            
        except Exception as e:
            self._audio_signal(f"Right click failed: {e}")
            return False
    
    def drag_select(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Drag selection from start to end coordinates for unit group selection.
        
        Args:
            x1: Start X coordinate (pixels)
            y1: Start Y coordinate (pixels)
            x2: End X coordinate (pixels)
            y2: End Y coordinate (pixels)
            
        Returns:
            bool: Success status
        """
        try:
            self._audio_signal(f"Drag selecting from ({x1}, {y1}) to ({x2}, {y2})")
            
            # Move to start position
            self.move_mouse(x1, y1, duration=0.05)
            
            # Mouse down at start position
            mouse_down = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventLeftMouseDown,
                (x1, y1),
                kCGMouseButtonLeft
            )
            CGEventPost(kCGHIDEventTap, mouse_down)
            
            # Drag to end position with smooth movement
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            drag_steps = max(int(distance / 10), 5)  # Smooth drag movement
            
            for i in range(1, drag_steps + 1):
                progress = i / drag_steps
                current_x = x1 + (x2 - x1) * progress
                current_y = y1 + (y2 - y1) * progress
                
                # Create drag event
                drag_event = CGEventCreateMouseEvent(
                    self.event_source,
                    kCGEventMouseMoved,
                    (current_x, current_y),
                    kCGMouseButtonLeft
                )
                CGEventPost(kCGHIDEventTap, drag_event)
                time.sleep(0.01)  # Smooth drag timing
            
            # Mouse up at end position
            mouse_up = CGEventCreateMouseEvent(
                self.event_source,
                kCGEventLeftMouseUp,
                (x2, y2),
                kCGMouseButtonLeft
            )
            CGEventPost(kCGHIDEventTap, mouse_up)
            
            return True
            
        except Exception as e:
            self._audio_signal(f"Drag select failed: {e}")
            return False
    
    def key_press(self, key: str) -> bool:
        """
        Press and release a keyboard key using CoreGraphics key codes.
        
        Args:
            key: Key to press (e.g., 'A', '1', 'Enter', 'Space')
            
        Returns:
            bool: Success status
        """
        try:
            self._audio_signal(f"Pressing key: {key}")
            
            # Map common keys to CoreGraphics key codes
            key_codes = {
                'A': 0x00, 'B': 0x0B, 'C': 0x08, 'D': 0x02, 'E': 0x0E,
                'F': 0x03, 'G': 0x05, 'H': 0x04, 'I': 0x22, 'J': 0x26,
                'K': 0x28, 'L': 0x25, 'M': 0x2E, 'N': 0x2D, 'O': 0x1F,
                'P': 0x23, 'Q': 0x0C, 'R': 0x0F, 'S': 0x01, 'T': 0x11,
                'U': 0x20, 'V': 0x09, 'W': 0x0D, 'X': 0x07, 'Y': 0x10,
                'Z': 0x06,
                '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15, '5': 0x17,
                '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19, '0': 0x1D,
                'Enter': 0x24, 'Return': 0x24, 'Space': 0x31, 'Escape': 0x35,
                'Tab': 0x30, 'Delete': 0x33, 'Backspace': 0x33
            }
            
            key_upper = key.upper()
            if key_upper not in key_codes:
                self._audio_signal(f"Unknown key: {key}")
                return False
            
            key_code = key_codes[key_upper]
            
            # Create key down event
            key_down = CGEventCreateKeyboardEvent(
                self.event_source, key_code, True
            )
            
            # Create key up event
            key_up = CGEventCreateKeyboardEvent(
                self.event_source, key_code, False
            )
            
            # Post events with proper timing
            CGEventPost(kCGHIDEventTap, key_down)
            time.sleep(0.01)  # Brief hold for reliable key press
            CGEventPost(kCGHIDEventTap, key_up)
            
            return True
            
        except Exception as e:
            self._audio_signal(f"Key press failed: {e}")
            return False
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """
        Cubic easing function for human-like mouse movement.
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            float: Eased progress value
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 1 + p * p * p / 2


def create_input_api(config: dict = None) -> InputAPI:
    """
    Factory function to create Input API instance.
    
    NEW M2 Implementation per AIP-SDS-V2.3
    """
    return InputAPI(config)


# Validation functions for testing
def validate_input_api():
    """Quick validation of Input API functionality."""
    try:
        api = create_input_api({'audio_feedback': True})
        print("✅ Input API created successfully")
        
        # Test basic functionality without actual input
        print("✅ All input methods available:")
        print(f"   - move_mouse: {hasattr(api, 'move_mouse')}")
        print(f"   - left_click: {hasattr(api, 'left_click')}")
        print(f"   - right_click: {hasattr(api, 'right_click')}")
        print(f"   - drag_select: {hasattr(api, 'drag_select')}")
        print(f"   - key_press: {hasattr(api, 'key_press')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Input API validation failed: {e}")
        return False


if __name__ == "__main__":
    print("🎯 NEW Module 2: Input Emulation API - AIP-SDS-V2.3")
    print("=" * 60)
    validate_input_api()