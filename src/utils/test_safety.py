"""
Test Utilities for AI Player Project
Provides guaranteed cleanup and focus management for all tests.
"""

import subprocess
import time
import os


def guaranteed_vscode_return():
    """
    CRITICAL FUNCTION: Guaranteed return to VS Code.
    Multiple fallback methods to ensure user isn't stranded.
    """
    methods = [
        # Method 1: AppleScript with Visual Studio Code
        '''tell application "Visual Studio Code" to activate''',
        # Method 2: AppleScript with Code
        '''tell application "Code" to activate''',
        # Method 3: AppleScript with any VS Code variant
        '''tell application system events to set frontmost of first process whose name contains "Code" to true''',
    ]
    
    for i, script in enumerate(methods, 1):
        try:
            print(f"   Trying VS Code focus method {i}...")
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ VS Code focused using method {i}")
                time.sleep(0.5)
                return True
        except Exception as e:
            print(f"   Method {i} failed: {e}")
    
    # Last resort: Try to focus any text editor
    try:
        print("   Last resort: trying any text editor...")
        editors = ["TextEdit", "Sublime Text", "Atom", "Vim"]
        for editor in editors:
            try:
                script = f'tell application "{editor}" to activate'
                subprocess.run(['osascript', '-e', script], timeout=3)
                print(f"   Focused {editor} as fallback")
                return True
            except:
                continue
    except:
        pass
    
    print("   ⚠️ Could not return to any editor - user intervention needed")
    return False


def guaranteed_cleanup(game_name="Dune Legacy", screenshot_path=None):
    """
    CRITICAL FUNCTION: Guaranteed cleanup with multiple safety nets.
    """
    print("🧹 GUARANTEED CLEANUP - Always executes...")
    
    cleanup_success = True
    
    # 1. Force close game with multiple methods
    try:
        print(f"   Closing {game_name}...")
        methods = [
            ['pkill', '-f', game_name],
            ['killall', game_name],
            ['osascript', '-e', f'tell application "{game_name}" to quit']
        ]
        
        for method in methods:
            try:
                subprocess.run(method, timeout=5)
                time.sleep(0.5)
            except:
                continue
                
    except Exception as e:
        print(f"   ⚠️ Game closure issue: {e}")
        cleanup_success = False
    
    # 2. Remove screenshot
    try:
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"   Removing screenshot: {screenshot_path}")
            os.remove(screenshot_path)
    except Exception as e:
        print(f"   ⚠️ Screenshot removal issue: {e}")
    
    # 3. CRITICAL: Return to VS Code
    print("   CRITICAL: Returning to VS Code...")
    vscode_success = guaranteed_vscode_return()
    
    if vscode_success:
        print("✅ Guaranteed cleanup complete")
    else:
        print("⚠️ Cleanup complete but VS Code focus failed - CHECK MANUALLY")
        # Audio alert for manual intervention
        try:
            os.system('say "Attention: Please manually return to VS Code"')
        except:
            pass
    
    return cleanup_success and vscode_success


class TestSafetyWrapper:
    """
    Context manager to guarantee cleanup for any test.
    Usage:
        with TestSafetyWrapper("Dune Legacy") as safety:
            # Your test code here
            safety.screenshot_path = "path/to/screenshot.png"
    """
    
    def __init__(self, game_name="Dune Legacy"):
        self.game_name = game_name
        self.screenshot_path = None
    
    def __enter__(self):
        print("🛡️ Test safety wrapper activated")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"🚨 Test failed with {exc_type.__name__}: {exc_val}")
        
        guaranteed_cleanup(self.game_name, self.screenshot_path)
        
        # Don't suppress exceptions
        return False