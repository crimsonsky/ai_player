#!/usr/bin/env python3
"""
Post-restart permission test
Run this after restarting Terminal to verify Screen Recording permissions
"""

import subprocess
import os
import time


def test_after_restart():
    print("🔄 Testing Screen Recording Permissions After Restart")
    print("=" * 50)
    
    # Test 1: Basic screencapture
    print("Test 1: Basic screencapture...")
    try:
        result = subprocess.run(['screencapture', '-x', '/tmp/restart_test.png'], 
                              capture_output=True, text=True, timeout=10)
        
        print(f"   Return code: {result.returncode}")
        if result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        
        if result.returncode == 0 and os.path.exists('/tmp/restart_test.png'):
            file_size = os.path.getsize('/tmp/restart_test.png')
            print(f"   ✅ SUCCESS! Screenshot captured (size: {file_size} bytes)")
            os.remove('/tmp/restart_test.png')
            os.system('say "Screen recording permissions are working"')
            return True
        else:
            print("   ❌ Still failing - check System Preferences again")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def instructions():
    print("\n📋 TROUBLESHOOTING STEPS:")
    print("1. Completely quit Terminal (Cmd+Q)")
    print("2. Reopen Terminal")
    print("3. Run this test again: python test_after_restart.py")
    print("\nIf still failing:")
    print("- Check System Preferences > Privacy & Security > Screen Recording")
    print("- Make sure Terminal is checked/enabled")
    print("- Try removing Terminal and adding it again")
    print("- On newer macOS, check 'Screen & System Audio Recording'")


if __name__ == "__main__":
    success = test_after_restart()
    
    if not success:
        instructions()
        
    print("\nNote: If permissions are working, we can immediately proceed to M2!")