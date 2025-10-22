#!/usr/bin/env python3
"""
Apple Vision Framework OCR Validation Test
Creates test image with text and validates OCR extraction capability.
"""

import sys
import cv2
import numpy as np
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/Users/amir/projects/ai_player/src')

def create_test_game_interface():
    """Create synthetic game interface with text for testing."""
    
    # Create black background simulating game interface
    width, height = 800, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create PIL image for text rendering
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    try:
        # Try to use a standard system font
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 36)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Add game interface text
    texts = [
        ("DUNE LEGACY", (250, 50), (255, 255, 255)),
        ("Single Player", (300, 200), (200, 200, 200)),
        ("Multiplayer", (300, 250), (200, 200, 200)),
        ("Options", (330, 300), (200, 200, 200)),
        ("Back", (360, 450), (180, 180, 180)),
        ("v0.96.4", (650, 550), (120, 120, 120))
    ]
    
    for text, pos, color in texts:
        draw.text(pos, text, fill=color, font=font)
    
    # Convert back to numpy array
    test_image = np.array(pil_image)
    
    return test_image

def test_apple_vision_text_detection():
    """Test Apple Vision Framework with known text content."""
    
    print("🎮 Creating synthetic game interface...")
    test_image = create_test_game_interface()
    
    print("💾 Saving test image...")
    test_path = '/Users/amir/projects/ai_player/test_game_interface.png'
    cv2.imwrite(test_path, test_image)
    print(f"   Saved: {test_path}")
    
    print("\n👁️ Testing Apple Vision Framework OCR...")
    
    try:
        from src.utils.apple_vision_ocr import create_apple_vision_ocr
        
        config = {
            'audio_feedback': True,
            'ocr_engine': 'apple_vision'
        }
        
        vision_ocr = create_apple_vision_ocr(config)
        
        # Test with the synthetic image
        result = vision_ocr.extract_text_from_screenshot(test_image)
        
        print(f"\n📊 Apple Vision OCR Results:")
        print(f"   Success: {result['success']}")
        print(f"   Text detected: {len(result['results'])} items")
        print(f"   Combined text: '{result['text']}'")
        print(f"   Average confidence: {result['confidence']:.3f}")
        
        if result['results']:
            print(f"\n📋 Individual text detections:")
            for i, text_result in enumerate(result['results']):
                print(f"   {i+1}. '{text_result.text}' (conf: {text_result.confidence:.3f})")
                
        # Test with file path method
        print(f"\n🔄 Testing file-based OCR...")
        file_result = vision_ocr.extract_text_from_image_path(test_path)
        
        print(f"   File OCR success: {file_result['success']}")
        print(f"   File OCR text: '{file_result['text']}'")
        print(f"   File OCR confidence: {file_result['confidence']:.3f}")
        
        return result['success'] and len(result['results']) > 0
        
    except Exception as e:
        print(f"❌ Apple Vision test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Apple Vision validation test."""
    
    print("👁️ Apple Vision Framework OCR Validation")
    print("🎯 Testing text detection capability with synthetic game interface")
    print("=" * 80)
    
    success = test_apple_vision_text_detection()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Apple Vision Framework OCR validation PASSED")
        print("🚀 Ready for Signal Fusion Engine integration")
    else:
        print("❌ Apple Vision Framework OCR validation FAILED")
        print("🔧 Needs diagnostic review")

if __name__ == "__main__":
    main()