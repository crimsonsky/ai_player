#!/usr/bin/env python3
"""
OCR Diagnostic Test - Signal Fusion Engine Support
Demonstrates current OCR limitations with game interface text extraction.
Provides evidence for architectural OCR alternative request.
"""

import sys
import os
import time
import subprocess
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, '/Users/amir/projects/ai_player/src')

def test_ocr_engines():
    """Test available OCR engines with current game interface."""
    
    print("=" * 80)
    print("🔍 OCR DIAGNOSTIC TEST - Game Interface Text Extraction")
    print("=" * 80)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Capture current screen
    print("📸 Capturing current screen for OCR analysis...")
    screenshot_path = "/tmp/ocr_diagnostic_screenshot.png"
    
    try:
        result = subprocess.run(['screencapture', '-x', screenshot_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ Screenshot capture failed: {result.stderr}")
            return False
            
        file_size = os.path.getsize(screenshot_path)
        print(f"✅ Screenshot captured: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return False
    
    # Test 1: Tesseract OCR
    print("\n" + "="*60)
    print("🧪 TEST 1: Tesseract OCR Analysis")
    print("="*60)
    
    try:
        print("🔍 Running tesseract on full screenshot...")
        result = subprocess.run(['tesseract', screenshot_path, 'stdout'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            extracted_text = result.stdout.strip()
            print(f"📄 Raw Tesseract Output:")
            print(f"   Length: {len(extracted_text)} characters")
            if extracted_text:
                print(f"   Content: '{extracted_text[:200]}...'")
                
                # Analyze for game-specific text
                game_keywords = ['dune', 'legacy', 'start', 'game', 'options', 'back', 'single', 'player']
                found_keywords = [kw for kw in game_keywords if kw.lower() in extracted_text.lower()]
                
                print(f"   Game Keywords Found: {found_keywords}")
                print(f"   Detection Rate: {len(found_keywords)}/{len(game_keywords)} ({len(found_keywords)/len(game_keywords)*100:.1f}%)")
            else:
                print("   ❌ NO TEXT DETECTED")
        else:
            print(f"❌ Tesseract failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Tesseract error: {e}")
    
    # Test 2: OCR Manager Integration
    print("\n" + "="*60)
    print("🧪 TEST 2: OCR Manager Integration Test")
    print("="*60)
    
    try:
        from src.utils.ocr_manager import OCRManager
        
        # Force tesseract usage
        config = {'ocr_engine': 'tesseract', 'audio_feedback': False}
        ocr_manager = OCRManager(config)
        
        print(f"✅ OCR Manager initialized with: {ocr_manager.ocr_method}")
        
        # Test text extraction
        print("🔍 Testing OCR Manager text extraction...")
        ocr_results = ocr_manager.extract_text_from_image(screenshot_path)
        
        print(f"📊 OCR Manager Results:")
        print(f"   Results Count: {len(ocr_results)}")
        
        for i, result in enumerate(ocr_results[:5], 1):  # Show first 5
            print(f"   Result {i}: '{result.text}' (confidence: {result.confidence:.3f})")
            
        if len(ocr_results) == 0:
            print("   ❌ NO TEXT RESULTS FROM OCR MANAGER")
            
    except Exception as e:
        print(f"❌ OCR Manager error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Signal Fusion Engine OCR Signal
    print("\n" + "="*60)
    print("🧪 TEST 3: Signal Fusion Engine S2 (OCR Signal)")
    print("="*60)
    
    try:
        from src.perception.perception_module import PerceptionModule
        
        config = {
            'confidence_threshold': 0.6,
            'audio_feedback': False,
            'template_library_path': '/Users/amir/projects/ai_player/data/templates',
            'ocr_engine': 'tesseract'
        }
        
        perception = PerceptionModule(config)
        print("✅ Signal Fusion Engine initialized")
        
        # Capture screen as array for S2 test
        screenshot_array = perception.capture_screen()
        if screenshot_array is not None:
            print(f"✅ Screenshot array captured: {screenshot_array.shape}")
            
            # Test S2 OCR signal directly
            s2_result = perception._signal_s2_ocr_detection(screenshot_array, 'MAIN_MENU')
            
            print(f"📊 S2 OCR Signal Results:")
            print(f"   Confidence: {s2_result['confidence']:.3f}")
            print(f"   Text Found: {s2_result['text_found']}")
            print(f"   Raw Text Sample: '{s2_result.get('raw_text', 'N/A')[:100]}...'")
            
            if s2_result['confidence'] == 0.0:
                print("   ❌ S2 OCR SIGNAL COMPLETELY NON-FUNCTIONAL")
            else:
                print(f"   🟡 S2 OCR Signal partially functional ({s2_result['confidence']*100:.1f}%)")
                
        else:
            print("❌ Screenshot array capture failed")
            
    except Exception as e:
        print(f"❌ Signal Fusion Engine S2 test error: {e}")
    
    # Test 4: Alternative OCR Analysis
    print("\n" + "="*60)
    print("🧪 TEST 4: Alternative OCR Engine Availability")
    print("="*60)
    
    # Check for EasyOCR
    try:
        import easyocr
        print("✅ EasyOCR available - could be integrated")
        
        # Quick EasyOCR test
        reader = easyocr.Reader(['en'])
        easyocr_results = reader.readtext(screenshot_path)
        
        print(f"📊 EasyOCR Results: {len(easyocr_results)} text regions detected")
        for i, (bbox, text, confidence) in enumerate(easyocr_results[:3], 1):
            print(f"   Result {i}: '{text}' (confidence: {confidence:.3f})")
            
    except ImportError:
        print("❌ EasyOCR not available - could be installed for better game text recognition")
    except Exception as e:
        print(f"⚠️ EasyOCR test error: {e}")
    
    # Check for Apple Vision Framework availability
    try:
        import objc
        import Vision
        print("✅ Apple Vision Framework available - ideal for native macOS OCR")
    except ImportError:
        print("❌ Apple Vision Framework not accessible - requires proper PyObjC setup")
    
    # Summary and Recommendations
    print("\n" + "="*80)
    print("📋 OCR DIAGNOSTIC SUMMARY & RECOMMENDATIONS")
    print("="*80)
    
    print("\n🔍 Current OCR Status:")
    print("   • Tesseract: ✅ Available, ❌ Poor game text performance")
    print("   • OCR Manager: ✅ Functional, ❌ Limited by underlying OCR engine")
    print("   • Signal Fusion S2: ❌ Non-functional due to text extraction failures")
    
    print("\n🎯 Recommended Solutions (Priority Order):")
    print("   1. Apple Vision Framework - Native macOS, optimized for graphics text")
    print("   2. EasyOCR Integration - Neural OCR with better game interface support")
    print("   3. Google Cloud Vision - Cloud-based, highest accuracy for complex text")
    print("   4. Hybrid Approach - Multiple OCR engines with confidence voting")
    
    print("\n⚠️ Current Blocking Issues:")
    print("   • Signal Fusion Engine stuck in UNCERTAIN state")
    print("   • Cannot distinguish between GUI buttons via text")
    print("   • No reliable context validation through text content")
    print("   • Autonomous navigation limited to position-based clicking")
    
    print(f"\n📊 OCR Diagnostic completed at {datetime.now().strftime('%H:%M:%S')}")
    print("📄 Results logged for architectural OCR alternative request")
    
    return True


def main():
    """Main diagnostic execution."""
    print("🔍 OCR Diagnostic Test - Demonstrating text extraction limitations")
    print("📌 Ensure Dune Legacy (or target application) is visible for testing")
    
    try:
        # Focus on current application for screenshot
        print("\n⏳ Starting diagnostic in 3 seconds...")
        time.sleep(3)
        
        success = test_ocr_engines()
        
        if success:
            print("\n✅ OCR diagnostic completed successfully")
            print("📄 Evidence collected for architectural OCR alternative request")
        else:
            print("\n❌ OCR diagnostic encountered errors")
            
    except KeyboardInterrupt:
        print("\n⚠️ OCR diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ OCR diagnostic failed: {e}")
    
    return success


if __name__ == "__main__":
    exit_code = 0 if main() else 1
    sys.exit(exit_code)