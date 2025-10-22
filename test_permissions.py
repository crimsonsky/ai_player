#!/usr/bin/env python3
"""
Quick permission validation test
Run this after granting Screen Recording permissions
"""

import subprocess
import os

def quick_test():
    print("🧪 Quick Permission Test")
    
    try:
        result = subprocess.run(['screencapture', '-x', '/tmp/permission_test.png'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and os.path.exists('/tmp/permission_test.png'):
            file_size = os.path.getsize('/tmp/permission_test.png')
            print(f"✅ SUCCESS! Screenshot works (size: {file_size} bytes)")
            os.remove('/tmp/permission_test.png')
            os.system('say "Screenshot permissions fixed"')
            return True
        else:
            print(f"❌ Still failing: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()