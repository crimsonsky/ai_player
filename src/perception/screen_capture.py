"""
Module 3A: Screen Capture - AIP-SDS-V2.3
Learning-Based Perception Stream Engine Foundation

High-speed, non-blocking screen capture utility using pyobjc CoreGraphics
for 30+ FPS game window isolation and capture.

MANDATE: Foundation component for YOLOv8 Perception Engine integration.
"""

import time
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np

# pyobjc CoreGraphics imports for screen capture
from Quartz import (
    CGWindowListCopyWindowInfo, 
    CGImageCreateWithImageInRect,
    CGDisplayCreateImage,
    CGMainDisplayID,
    CGRectMake,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)
from Quartz.CoreGraphics import CGDataProviderCopyData
import Cocoa
import AppKit


class GameScreenCapture:
    """
    High-speed screen capture system for Learning-Based Perception Engine.
    
    Implements Module 3A per AIP-SDS-V2.3 specification with 30+ FPS capability
    and game window isolation for "Dune Legacy" target.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize screen capture system."""
        self.config = config or {}
        self.audio_feedback = self.config.get('audio_feedback', False)
        self.target_game = self.config.get('game_name', 'Dune Legacy')
        
        # Performance tracking for 30+ FPS requirement
        self.capture_times = []
        self.last_capture_time = 0
        
        # Window isolation cache
        self.game_window_info = None
        self.window_cache_time = 0
        self.window_cache_duration = 2.0  # Refresh window info every 2 seconds
        
        if self.audio_feedback:
            self._audio_signal("Screen capture system initialized - Module 3A ready")
    
    def _audio_signal(self, message: str):
        """Audio feedback for debugging and status updates."""
        if self.audio_feedback:
            print(f"🎥 SCREEN CAPTURE: {message}")
    
    def capture_game_screen(self, crop_to_game_window: bool = True) -> Optional[Image.Image]:
        """
        Primary screen capture function - returns PIL Image of game screen.
        
        Args:
            crop_to_game_window: If True, isolates and crops to game window only
            
        Returns:
            PIL Image (RGB format) or None if capture fails
        """
        start_time = time.time()
        
        try:
            if crop_to_game_window:
                # Attempt game window isolation first
                game_image = self._capture_game_window()
                if game_image:
                    self._update_performance_metrics(start_time)
                    return game_image
                
                # Fallback to full screen if game window not found
                self._audio_signal("Game window not found, falling back to full screen")
            
            # Capture full screen using CoreGraphics
            full_screen_image = self._capture_full_screen()
            
            if full_screen_image:
                self._update_performance_metrics(start_time)
                return full_screen_image
            
            return None
            
        except Exception as e:
            self._audio_signal(f"Screen capture failed: {e}")
            return None
    
    def _capture_game_window(self) -> Optional[Image.Image]:
        """
        Isolate and capture specific game window using window information.
        
        Returns:
            PIL Image of game window or None if not found
        """
        try:
            # Get or refresh game window information
            window_info = self._get_game_window_info()
            
            if not window_info:
                return None
            
            # Extract window bounds
            bounds = window_info['kCGWindowBounds']
            x = int(bounds['X'])
            y = int(bounds['Y']) 
            width = int(bounds['Width'])
            height = int(bounds['Height'])
            
            self._audio_signal(f"Capturing game window at ({x}, {y}) size {width}x{height}")
            
            # Capture full screen first
            main_display_id = CGMainDisplayID()
            screenshot = CGDisplayCreateImage(main_display_id)
            
            if not screenshot:
                return None
            
            # Crop to game window bounds
            crop_rect = CGRectMake(x, y, width, height)
            cropped_screenshot = CGImageCreateWithImageInRect(screenshot, crop_rect)
            
            if not cropped_screenshot:
                return None
            
            # Convert CGImage to PIL Image
            pil_image = self._cgimage_to_pil(cropped_screenshot)
            return pil_image
            
        except Exception as e:
            self._audio_signal(f"Game window capture failed: {e}")
            return None
    
    def _capture_full_screen(self) -> Optional[Image.Image]:
        """
        Capture full screen using CoreGraphics for fallback scenarios.
        
        Returns:
            PIL Image of full screen or None if capture fails
        """
        try:
            self._audio_signal("Capturing full screen")
            
            # Capture main display
            main_display_id = CGMainDisplayID()
            screenshot = CGDisplayCreateImage(main_display_id)
            
            if not screenshot:
                return None
            
            # Convert CGImage to PIL Image
            pil_image = self._cgimage_to_pil(screenshot)
            return pil_image
            
        except Exception as e:
            self._audio_signal(f"Full screen capture failed: {e}")
            return None
    
    def _get_game_window_info(self) -> Optional[Dict[str, Any]]:
        """
        Get window information for target game application.
        
        Returns:
            Window info dictionary or None if not found
        """
        current_time = time.time()
        
        # Use cached window info if recent
        if (self.game_window_info and 
            current_time - self.window_cache_time < self.window_cache_duration):
            return self.game_window_info
        
        try:
            # Get list of all on-screen windows
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, 
                kCGNullWindowID
            )
            
            # Search for target game window
            for window in window_list:
                window_name = window.get('kCGWindowName', '')
                owner_name = window.get('kCGWindowOwnerName', '')
                
                # Check for Dune Legacy window
                if (self.target_game.lower() in window_name.lower() or 
                    self.target_game.lower() in owner_name.lower()):
                    
                    # Validate window has reasonable bounds
                    bounds = window.get('kCGWindowBounds', {})
                    if bounds.get('Width', 0) > 100 and bounds.get('Height', 0) > 100:
                        self.game_window_info = window
                        self.window_cache_time = current_time
                        self._audio_signal(f"Found game window: {window_name or owner_name}")
                        return window
            
            # No suitable game window found
            self.game_window_info = None
            return None
            
        except Exception as e:
            self._audio_signal(f"Window enumeration failed: {e}")
            return None
    
    def _cgimage_to_pil(self, cg_image) -> Optional[Image.Image]:
        """
        Convert CoreGraphics CGImage to PIL Image (RGB format).
        
        Args:
            cg_image: CGImage from CoreGraphics
            
        Returns:
            PIL Image in RGB format
        """
        try:
            # Get image data
            data_provider = cg_image.dataProvider()
            data = CGDataProviderCopyData(data_provider)
            
            # Get image dimensions and properties
            width = cg_image.width()
            height = cg_image.height()
            bytes_per_row = cg_image.bytesPerRow()
            
            # Convert to numpy array
            image_array = np.frombuffer(data, dtype=np.uint8)
            image_array = image_array.reshape((height, bytes_per_row))
            
            # Extract RGB channels (CoreGraphics often uses BGRA format)
            # Adjust based on actual format - may need BGR -> RGB conversion
            rgb_array = image_array[:, :width*4].reshape((height, width, 4))
            
            # Convert BGRA to RGB (drop alpha channel and swap B/R)
            rgb_image = rgb_array[:, :, [2, 1, 0]]  # BGR -> RGB
            
            # Create PIL Image
            pil_image = Image.fromarray(rgb_image, 'RGB')
            return pil_image
            
        except Exception as e:
            self._audio_signal(f"CGImage to PIL conversion failed: {e}")
            return None
    
    def _update_performance_metrics(self, start_time: float):
        """
        Track capture performance to ensure 30+ FPS capability.
        
        Args:
            start_time: Capture start timestamp
        """
        capture_duration = time.time() - start_time
        self.capture_times.append(capture_duration)
        self.last_capture_time = capture_duration
        
        # Keep only recent measurements (last 30 captures)
        if len(self.capture_times) > 30:
            self.capture_times.pop(0)
        
        # Calculate average FPS
        if len(self.capture_times) >= 5:
            avg_time = sum(self.capture_times) / len(self.capture_times)
            avg_fps = 1.0 / avg_time if avg_time > 0 else 0
            
            # Log performance if audio feedback enabled
            if self.audio_feedback and len(self.capture_times) % 10 == 0:
                self._audio_signal(f"Performance: {avg_fps:.1f} FPS (target: 30+ FPS)")
    
    def get_capture_performance(self) -> Dict[str, float]:
        """
        Get current capture performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.capture_times:
            return {
                'avg_fps': 0.0,
                'last_capture_time_ms': 0.0,
                'samples': 0
            }
        
        avg_time = sum(self.capture_times) / len(self.capture_times)
        avg_fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            'avg_fps': avg_fps,
            'last_capture_time_ms': self.last_capture_time * 1000,
            'samples': len(self.capture_times)
        }
    
    def validate_30fps_requirement(self) -> bool:
        """
        Validate that screen capture meets 30+ FPS requirement.
        
        Returns:
            True if meeting performance requirement, False otherwise
        """
        performance = self.get_capture_performance()
        return performance['avg_fps'] >= 30.0
    
    def test_capture_speed(self, num_captures: int = 10) -> Dict[str, Any]:
        """
        Test screen capture speed with multiple captures.
        
        Args:
            num_captures: Number of test captures to perform
            
        Returns:
            Performance test results
        """
        self._audio_signal(f"Testing capture speed with {num_captures} captures...")
        
        test_start_time = time.time()
        successful_captures = 0
        
        for i in range(num_captures):
            image = self.capture_game_screen()
            if image:
                successful_captures += 1
        
        total_time = time.time() - test_start_time
        
        results = {
            'total_captures': num_captures,
            'successful_captures': successful_captures,
            'total_time_seconds': total_time,
            'average_fps': successful_captures / total_time if total_time > 0 else 0,
            'success_rate': successful_captures / num_captures if num_captures > 0 else 0,
            'meets_30fps_requirement': (successful_captures / total_time) >= 30.0 if total_time > 0 else False
        }
        
        self._audio_signal(
            f"Test complete: {results['average_fps']:.1f} FPS, "
            f"{results['success_rate']*100:.1f}% success rate"
        )
        
        return results


def create_screen_capture(config: Dict[str, Any] = None) -> GameScreenCapture:
    """
    Factory function to create screen capture instance.
    
    Module 3A Implementation per AIP-SDS-V2.3
    """
    return GameScreenCapture(config)


# Validation and testing functions
def validate_screen_capture():
    """Quick validation of screen capture functionality."""
    try:
        capture = create_screen_capture({'audio_feedback': True})
        print("✅ Screen capture system created successfully")
        
        # Test single capture
        image = capture.capture_game_screen()
        if image:
            print(f"✅ Screen capture successful: {image.size} pixels")
            print(f"   Image format: {image.mode}")
            
            # Test performance
            performance = capture.get_capture_performance()
            if performance['avg_fps'] > 0:
                print(f"✅ Performance: {performance['avg_fps']:.1f} FPS")
            
            return True
        else:
            print("❌ Screen capture returned no image")
            return False
            
    except Exception as e:
        print(f"❌ Screen capture validation failed: {e}")
        return False


if __name__ == "__main__":
    print("🎥 Module 3A: Screen Capture - AIP-SDS-V2.3")
    print("=" * 60)
    validate_screen_capture()