#!/usr/bin/env python3
"""
M2 OCR DIAGNOSIS - Debug Real OCR Issues
=======================================

This script will diagnose why the M2 system isn't detecting text elements.
It will check:
1. OCR engines available (tesseract, ocrmac, etc.)
2. Screenshot quality and accessibility
3. Real text extraction capabilities
4. Element detection pipeline

Following test guidelines: Real detection or proper failure diagnosis
"""

import subprocess
import sys
import os
import time

# Clean import path
sys.path.insert(0, '/Users/amir/projects/ai_player/src')

def focus_game():
    """Focus the game for testing."""
    print("🎯 Focusing Dune Legacy...")
    subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                  capture_output=True)
    time.sleep(2)

def check_ocr_engines():
    """Check what OCR engines are actually available."""
    print("🔍 CHECKING AVAILABLE OCR ENGINES")
    print("="*50)
    
    ocr_results = {}
    
    # Check tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            ocr_results['tesseract'] = f"✅ AVAILABLE: {version}"
        else:
            ocr_results['tesseract'] = f"❌ ERROR: Return code {result.returncode}"
    except FileNotFoundError:
        ocr_results['tesseract'] = "❌ NOT INSTALLED"
    except subprocess.TimeoutExpired:
        ocr_results['tesseract'] = "❌ TIMEOUT"
    except Exception as e:
        ocr_results['tesseract'] = f"❌ ERROR: {e}"
    
    # Check ocrmac
    try:
        result = subprocess.run(['python3', '-c', 'import ocrmac; print("ocrmac available")'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            ocr_results['ocrmac'] = "✅ AVAILABLE: Python module installed"
        else:
            ocr_results['ocrmac'] = f"❌ IMPORT ERROR: {result.stderr.strip()}"
    except Exception as e:
        ocr_results['ocrmac'] = f"❌ ERROR: {e}"
    
    # Print results
    for engine, status in ocr_results.items():
        print(f"   {engine}: {status}")
    
    return ocr_results

def test_direct_tesseract_ocr():
    """Test tesseract OCR directly on a screenshot."""
    print("\n🔬 TESTING DIRECT TESSERACT OCR")
    print("="*50)
    
    try:
        # Take a screenshot first
        screenshot_path = "/tmp/m2_ocr_test_screenshot.png"
        
        # Use screencapture to get a clean screenshot
        result = subprocess.run(['screencapture', '-x', screenshot_path], 
                              capture_output=True)
        
        if result.returncode != 0:
            print("❌ Screenshot capture failed")
            return False
        
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Test direct tesseract on the screenshot
        ocr_result = subprocess.run(['tesseract', screenshot_path, 'stdout'], 
                                  capture_output=True, text=True, timeout=10)
        
        if ocr_result.returncode == 0:
            text = ocr_result.stdout.strip()
            print(f"📝 Tesseract extracted text:")
            print(f"   Length: {len(text)} characters")
            if text:
                lines = text.split('\n')[:5]  # Show first 5 lines
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"   Line {i+1}: '{line.strip()}'")
                return True
            else:
                print("   ⚠️ No text detected by tesseract")
                return False
        else:
            print(f"❌ Tesseract failed: {ocr_result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Tesseract OCR timed out")
        return False
    except Exception as e:
        print(f"❌ Direct tesseract test failed: {e}")
        return False

def test_m2_ocr_manager():
    """Test the M2 OCR manager directly."""
    print("\n🧪 TESTING M2 OCR MANAGER")
    print("="*50)
    
    try:
        from utils.ocr_manager import OCRManager
        
        # Try different OCR methods
        methods = ['tesseract', 'ocrmac', 'shortcuts']
        
        for method in methods:
            print(f"\n   Testing OCR method: {method}")
            
            try:
                ocr = OCRManager(method=method)
                print(f"   ✅ {method} OCR manager initialized")
                
                # Test with a simple screenshot
                screenshot_path = "/tmp/m2_ocr_test_screenshot.png"
                
                if os.path.exists(screenshot_path):
                    results = ocr.extract_text(screenshot_path)
                    print(f"   📋 {method} results: {len(results)} text elements")
                    
                    for i, result in enumerate(results[:3]):  # Show first 3
                        text = getattr(result, 'text', str(result))
                        conf = getattr(result, 'confidence', 'N/A')
                        print(f"     {i+1}. '{text}' (conf: {conf})")
                else:
                    print(f"   ⚠️ No screenshot available for {method} test")
                    
            except RuntimeError as e:
                if "NOT_IMPLEMENTED" in str(e) or "FAILED" in str(e):
                    print(f"   ⚠️ {method} error (expected): {e}")
                else:
                    print(f"   ❌ {method} unexpected error: {e}")
            except Exception as e:
                print(f"   ❌ {method} failed: {e}")
    
    except Exception as e:
        print(f"❌ Could not test OCR manager: {e}")
        return False
    
    return True

def test_perception_module_components():
    """Test the perception module components."""
    print("\n🔧 TESTING PERCEPTION MODULE COMPONENTS")
    print("="*50)
    
    try:
        from perception.perception_module import PerceptionModule
        
        config = {
            'confidence_threshold': 0.6,
            'audio_feedback': False
        }
        
        perception = PerceptionModule(config)
        
        # Test screenshot capture
        screenshot = perception.capture_screen()
        if screenshot:
            print("✅ Screenshot capture working")
            print(f"   Screenshot: {screenshot}")
        else:
            print("❌ Screenshot capture failed")
        
        # Test context detection
        if screenshot:
            context = perception.identify_screen_context(screenshot)
            print(f"✅ Context detection: {context}")
            
            # Test element detection
            elements = perception.detect_elements(screenshot)
            print(f"✅ Element detection: {len(elements)} elements")
        
        return True
        
    except Exception as e:
        print(f"❌ Perception module test failed: {e}")
        return False

def main():
    """Main OCR diagnosis."""
    print("="*60)
    print("M2 OCR DIAGNOSIS - Real Detection Issues")
    print("="*60)
    
    # Focus the game
    focus_game()
    
    # Check available OCR engines
    ocr_engines = check_ocr_engines()
    
    # Test direct tesseract if available
    if "✅ AVAILABLE" in ocr_engines.get('tesseract', ''):
        tesseract_working = test_direct_tesseract_ocr()
    else:
        tesseract_working = False
        print("\n⚠️ Skipping direct tesseract test - not available")
    
    # Test M2 OCR manager
    ocr_manager_working = test_m2_ocr_manager()
    
    # Test perception module
    perception_working = test_perception_module_components()
    
    # Summary
    print(f"\n{'='*60}")
    print("M2 OCR DIAGNOSIS RESULTS")
    print(f"{'='*60}")
    
    print(f"OCR Engines Available: {sum('✅' in status for status in ocr_engines.values())}/{len(ocr_engines)}")
    for engine, status in ocr_engines.items():
        print(f"   {engine}: {status}")
    
    print(f"\nDirect Tesseract: {'✅ WORKING' if tesseract_working else '❌ FAILED'}")
    print(f"M2 OCR Manager: {'✅ WORKING' if ocr_manager_working else '❌ FAILED'}")
    print(f"Perception Module: {'✅ WORKING' if perception_working else '❌ FAILED'}")
    
    # Recommendations
    print(f"\n🔧 RECOMMENDATIONS:")
    if not any('✅' in status for status in ocr_engines.values()):
        print("❌ No working OCR engines - install tesseract: brew install tesseract")
    elif tesseract_working and not perception_working:
        print("⚠️ Tesseract works but M2 integration fails - check M2 OCR pipeline")
    elif perception_working:
        print("✅ M2 system should be working - investigate game interface visibility")
    
    return tesseract_working and perception_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)