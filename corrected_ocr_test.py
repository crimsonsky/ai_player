#!/usr/bin/env python3
"""
Corrected OCR Test - With Proper Game Focus
Tests OCR functionality with properly focused Dune Legacy interface.
"""

import sys
import os
import time
import subprocess
from datetime import datetime

def test_focused_ocr():
    """Test OCR with properly focused game interface."""
    
    print("=" * 80)
    print("🔍 CORRECTED OCR TEST - Proper Game Focus")
    print("=" * 80)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Focus Dune Legacy
    print("🎯 Focusing Dune Legacy application...")
    try:
        result = subprocess.run([
            'osascript', '-e', 
            'tell application "Dune Legacy" to activate'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Dune Legacy focused successfully")
        else:
            print(f"⚠️ Focus command completed with: {result.stderr}")
        
        # Wait for focus to settle
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Failed to focus Dune Legacy: {e}")
        return False
    
    # Step 2: Capture focused game screenshot
    print("\n📸 Capturing focused game interface...")
    screenshot_path = "/tmp/focused_dune_legacy.png"
    
    try:
        result = subprocess.run(['screencapture', '-x', screenshot_path], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Focused screenshot captured: {file_size} bytes")
        else:
            print(f"❌ Screenshot capture failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return False
    
    # Step 3: Test OCR on focused game interface  
    print("\n🔍 Testing OCR on focused game interface...")
    
    # Use Python to call tesseract to avoid shell issues
    try:
        result = subprocess.run([
            'tesseract', screenshot_path, 'stdout'
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            # Handle text encoding properly
            try:
                extracted_text = result.stdout.decode('utf-8').strip()
            except UnicodeDecodeError:
                try:
                    extracted_text = result.stdout.decode('latin-1').strip() 
                except:
                    extracted_text = str(result.stdout).strip()
            print(f"📄 OCR Results from Focused Game:")
            print(f"   Text Length: {len(extracted_text)} characters")
            
            if extracted_text:
                print(f"   Raw Text: '{extracted_text[:300]}...'")
                
                # Check for game-specific keywords
                game_keywords = ['dune', 'legacy', 'start', 'game', 'options', 'back', 'single', 'player']
                found_keywords = []
                
                for keyword in game_keywords:
                    if keyword.lower() in extracted_text.lower():
                        found_keywords.append(keyword)
                
                print(f"   Game Keywords Found: {found_keywords}")
                
                if len(found_keywords) > 0:
                    print(f"✅ OCR SUCCESSFULLY DETECTED GAME TEXT")
                    print(f"   Detection Rate: {len(found_keywords)}/{len(game_keywords)} ({len(found_keywords)/len(game_keywords)*100:.1f}%)")
                else:
                    print(f"❌ NO GAME KEYWORDS DETECTED - OCR reading non-game content")
                    
                # Check if this looks like desktop vs game content
                desktop_indicators = ['chrome', 'safari', 'finder', 'dock', 'menu bar', 'github', 'google']
                desktop_found = [ind for ind in desktop_indicators if ind.lower() in extracted_text.lower()]
                
                if desktop_found:
                    print(f"⚠️ Desktop content detected: {desktop_found}")
                    print("   This suggests OCR is reading desktop instead of game")
                
            else:
                print("❌ NO TEXT EXTRACTED from focused game interface")
                
        else:
            try:
                error_msg = result.stderr.decode('utf-8') if result.stderr else 'Unknown error'
            except:
                error_msg = str(result.stderr)
            print(f"❌ Tesseract OCR failed: {error_msg}")
            
    except Exception as e:
        print(f"❌ OCR test error: {e}")
        return False
    
    # Step 4: Analysis and conclusion
    print("\n" + "="*60)
    print("📊 FOCUSED OCR TEST ANALYSIS")
    print("="*60)
    
    if extracted_text and len(found_keywords) > 0:
        print("✅ CORRECTED ASSESSMENT: OCR works with proper game focus")
        print("   Issue was lack of application focus in previous test")
        print("   OCR successfully extracts game interface text")
    elif extracted_text and len(desktop_found) > 0:
        print("❌ FOCUS ISSUE CONFIRMED: Still reading desktop content") 
        print("   Dune Legacy focus may not be working properly")
        print("   Need to investigate window management")
    else:
        print("❌ OCR EXTRACTION FAILED: No text detected from game interface")
        print("   This confirms OCR has fundamental issues with game graphics")
    
    # Cleanup
    try:
        os.unlink(screenshot_path)
    except:
        pass
    
    return True


def main():
    """Main execution."""
    print("🔍 Corrected OCR Test - Addressing focus issue from previous diagnostic")
    print("📌 This test properly focuses Dune Legacy before OCR analysis")
    print()
    
    try:
        success = test_focused_ocr()
        
        if success:
            print("\n✅ Corrected OCR test completed")
        else:
            print("\n❌ Corrected OCR test failed")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    # Return focus to VS Code
    try:
        subprocess.run([
            'osascript', '-e',
            'tell application "Visual Studio Code" to activate'
        ], capture_output=True, timeout=5)
    except:
        pass


if __name__ == "__main__":
    main()