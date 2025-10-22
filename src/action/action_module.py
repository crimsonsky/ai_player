"""
Action Module - Module 4: INPUT EMULATION
Executes actions via macOS input emulation using pyobjc.
Includes game process management and focus control following development guidelines.
"""

import time
import subprocess
import psutil
import signal
import os
from typing import Dict, Any, Tuple, Optional
import Cocoa
import Quartz


class TimeoutException(Exception):
    """Exception raised when operations exceed timeout."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout detection."""
    raise TimeoutException("Operation timed out")


def with_timeout(seconds):
    """Decorator to add timeout protection to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutException:
                print(f"⚠️ HANG DETECTED: {func.__name__} exceeded {seconds}s timeout")
                return None
        return wrapper
    return decorator


class ActionModule:
    """
    Handles execution of actions through macOS CoreGraphics input emulation.
    Only uses pyobjc as specified in requirements (R2).
    Includes game process management for M1 milestone.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Action Module.
        
        Args:
            config: Configuration dictionary for action settings
        """
        self.config = config
        self.screen_width = None
        self.screen_height = None
        self.game_process = None
        self.game_path = config.get('game_path', '/Applications/Dune Legacy.app')
        self.audio_enabled = config.get('audio_feedback', True)
        self._get_screen_dimensions()
    
    def audio_signal(self, message: str, voice: str = "Alex") -> None:
        """
        Provide audio feedback during operations.
        
        Args:
            message: Message to speak
            voice: Voice to use for speech
        """
        if self.audio_enabled:
            try:
                os.system(f'say -v {voice} "{message}"')
            except Exception as e:
                print(f"Audio feedback failed: {e}")
    
    @with_timeout(10)
    def ensure_app_focus(self, app_name: str = "Dune Legacy") -> bool:
        """
        Ensure the specified application is in focus.
        Critical for reliable screen capture and input emulation.
        
        Args:
            app_name: Name of the application to focus
            
        Returns:
            bool: True if app is now in focus
        """
        try:
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                if app.localizedName() == app_name:
                    # Bring app to front
                    app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)
                    time.sleep(0.5)  # Allow focus transition
                    
                    # Verify focus
                    frontmost_app = workspace.frontmostApplication()
                    if frontmost_app and frontmost_app.localizedName() == app_name:
                        print(f"✅ {app_name} is now in focus")
                        return True
                    else:
                        print(f"⚠️ Failed to bring {app_name} to focus")
                        return False
            
            print(f"❌ {app_name} is not running")
            return False
            
        except Exception as e:
            print(f"Error ensuring app focus: {e}")
            return False
    
    def return_to_vscode(self) -> bool:
        """
        Return focus to VS Code after test completion.
        Part of post-test protocol.
        
        Returns:
            bool: True if VS Code is now focused
        """
        try:
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            vscode_names = ["Visual Studio Code", "Code", "VSCode"]
            
            for app in running_apps:
                app_name = app.localizedName()
                if any(name in app_name for name in vscode_names):
                    app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)
                    time.sleep(0.5)
                    print(f"✅ Returned focus to {app_name}")
                    return True
                    
            print("⚠️ VS Code not found in running applications")
            return False
            
        except Exception as e:
            print(f"Error returning to VS Code: {e}")
            return False
    
    def _get_screen_dimensions(self) -> None:
        """Get current screen dimensions for coordinate conversion."""
        screen = Cocoa.NSScreen.mainScreen()
        frame = screen.frame()
        self.screen_width = frame.size.width
        self.screen_height = frame.size.height
    
    def execute_action(self, action: int) -> bool:
        """
        Execute the given action.
        
        Args:
            action: Action ID from the decision module
            
        Returns:
            bool: True if action executed successfully, False otherwise
        """
        try:
            if action == 0:  # No-Op
                return True
            elif action == 1:  # Click action (will be parameterized later)
                return self._execute_click_action()
            elif action == 2:  # Key press (W key for movement)
                return self._execute_key_press('w')
            else:
                print(f"Unknown action: {action}")
                return False
        except Exception as e:
            print(f"Error executing action {action}: {e}")
            return False
    
    def _execute_click_action(self, x: float = 0.5, y: float = 0.5) -> bool:
        """
        Execute a mouse click at normalized coordinates.
        
        Args:
            x: Normalized x coordinate (0.0 to 1.0)
            y: Normalized y coordinate (0.0 to 1.0)
            
        Returns:
            bool: True if click executed successfully
        """
        # Convert normalized coordinates to absolute pixels
        abs_x = int(x * self.screen_width)
        abs_y = int(y * self.screen_height)
        
        # Create mouse click event
        click_down = Quartz.CGEventCreateMouseEvent(
            None,
            Quartz.kCGEventLeftMouseDown,
            (abs_x, abs_y),
            Quartz.kCGMouseButtonLeft
        )
        
        click_up = Quartz.CGEventCreateMouseEvent(
            None,
            Quartz.kCGEventLeftMouseUp,
            (abs_x, abs_y),
            Quartz.kCGMouseButtonLeft
        )
        
        # Post the events
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, click_down)
        time.sleep(0.01)  # Small delay between down and up
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, click_up)
        
        return True
    
    def _execute_key_press(self, key: str) -> bool:
        """
        Execute a key press.
        
        Args:
            key: Key to press (single character)
            
        Returns:
            bool: True if key press executed successfully
        """
        # Map common keys to their keycodes
        key_codes = {
            'w': 13,
            'a': 0,
            's': 1,
            'd': 2,
            'space': 49,
            'enter': 36,
            'escape': 53
        }
        
        keycode = key_codes.get(key.lower())
        if keycode is None:
            print(f"Unknown key: {key}")
            return False
        
        # Create key press events
        key_down = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
        key_up = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
        
        # Post the events
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
        time.sleep(0.01)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)
        
        return True
    
    def launch_game(self, app_name: str = "Dune Legacy") -> bool:
        """
        Launch the game application (M1 - Game Launch POC).
        
        Args:
            app_name: Name of the application to launch
            
        Returns:
            bool: True if game launched successfully
        """
        try:
            # Use NSWorkspace to launch the application
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            app_path = f"/Applications/{app_name}.app"
            
            success = workspace.launchApplication_(app_path)
            
            if success:
                print(f"Successfully launched {app_name}")
                # Give the app time to start up
                time.sleep(3)
                return True
            else:
                print(f"Failed to launch {app_name}")
                return False
                
        except Exception as e:
            print(f"Error launching game: {e}")
            return False
    
    def move_mouse(self, x: float, y: float, smooth: bool = True) -> bool:
        """
        Move mouse to normalized coordinates.
        
        Args:
            x: Normalized x coordinate (0.0 to 1.0)
            y: Normalized y coordinate (0.0 to 1.0)
            smooth: Whether to use smooth movement
            
        Returns:
            bool: True if movement executed successfully
        """
        try:
            abs_x = int(x * self.screen_width)
            abs_y = int(y * self.screen_height)
            
            if smooth:
                # Get current mouse position
                current_pos = Quartz.CGEventGetLocation(
                    Quartz.CGEventCreate(None)
                )
                current_x, current_y = current_pos.x, current_pos.y
                
                # Smooth interpolation (simple linear)
                steps = 10
                for i in range(steps + 1):
                    t = i / steps
                    inter_x = int(current_x + t * (abs_x - current_x))
                    inter_y = int(current_y + t * (abs_y - current_y))
                    
                    move_event = Quartz.CGEventCreateMouseEvent(
                        None,
                        Quartz.kCGEventMouseMoved,
                        (inter_x, inter_y),
                        0
                    )
                    Quartz.CGEventPost(Quartz.kCGHIDEventTap, move_event)
                    time.sleep(0.01)
            else:
                # Direct movement
                move_event = Quartz.CGEventCreateMouseEvent(
                    None,
                    Quartz.kCGEventMouseMoved,
                    (abs_x, abs_y),
                    0
                )
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, move_event)
            
            return True
            
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False
    
    def is_game_running(self, app_name: str = "Dune Legacy") -> bool:
        """
        Check if the game application is currently running.
        
        Args:
            app_name: Name of the application to check
            
        Returns:
            bool: True if game is running
        """
        try:
            # Check running applications
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                if app.localizedName() == app_name:
                    return True
            return False
            
        except Exception as e:
            print(f"Error checking if game is running: {e}")
            return False
    
    def close_game(self, app_name: str = "Dune Legacy") -> bool:
        """
        Close the game application gracefully.
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            bool: True if game closed successfully
        """
        try:
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                if app.localizedName() == app_name:
                    app.terminate()
                    time.sleep(2)  # Give time to close
                    return True
            
            print(f"{app_name} is not running")
            return False
            
        except Exception as e:
            print(f"Error closing game: {e}")
            return False