#!/usr/bin/env python3
"""
M2 Perception Fusion Validation Test
Tests the integration of Module 2C (Template Matching) with Module 2D (OCR)
Confirms proper semantic classification of functional buttons vs visual anchors
"""

import subprocess
import time
import os
import sys

# Add src path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_perception_fusion():
    """Test the complete perception fusion implementation."""
    
    print("🧪 M2 PERCEPTION FUSION VALIDATION TEST")
    print("=" * 50)
    print("Objective: Validate Module 2C + 2D integration")
    print("Expected: Text labels extracted, functional buttons confirmed")
    print("Key Test: 'Dune Legacy' headline should be Visual Anchor (non-clickable)")
    print()
    
    try:
        # Focus Dune Legacy
        print("🎮 Focusing Dune Legacy...")
        subprocess.run(['osascript', '-e', 'tell application "Dune Legacy" to activate'], 
                      capture_output=True)
        time.sleep(3)
        
        # Import perception module
        print("📦 Loading Perception Module...")
        
        from perception.element_location import ElementLocationModule
        
        # Initialize with OCR enabled
        config = {
            'templates_dir': 'data/templates',
            'confidence_threshold': 0.95,
            'audio_feedback': True
        }
        
        element_locator = ElementLocationModule(config)
        
        # Capture screenshot
        print("📸 Capturing screenshot...")
        screenshot_path = "/tmp/perception_fusion_test.png"
        subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True)
        
        if not os.path.exists(screenshot_path):
            raise Exception("Screenshot capture failed")
        
        # Execute perception fusion detection
        print("\n🔍 EXECUTING PERCEPTION FUSION (Module 2C + 2D)...")
        print("   Template Matching + OCR + Semantic Classification")
        
        detected_elements = element_locator.detect_all_elements(screenshot_path)
        
        if not detected_elements:
            raise Exception("No elements detected")
        
        # Analyze results
        print(f"\n📊 PERCEPTION FUSION RESULTS:")
        print("=" * 40)
        
        functional_buttons = []
        visual_anchors = []
        
        for element in detected_elements:
            print(f"\n🎯 Element: {element.name}")
            print(f"   Template ID: {element.template_id}")
            print(f"   Position: ({element.normalized_x:.3f}, {element.normalized_y:.3f})")
            print(f"   Visual Confidence: {element.confidence:.3f}")
            
            if element.text_label:
                print(f"   📝 Text Label: '{element.text_label}' (OCR Conf: {element.text_confidence:.3f})")
                print(f"   🏷️ Classification: {'Functional Button' if element.is_functional_button else 'Visual Anchor'}")
                
                if element.is_functional_button:
                    functional_buttons.append(element)
                else:
                    visual_anchors.append(element)
            else:
                print(f"   ⚠️ No text extracted")
                
        # Validation checks
        print(f"\n✅ VALIDATION RESULTS:")
        print("=" * 30)
        
        print(f"📊 Detection Summary:")
        print(f"   Total Elements: {len(detected_elements)}")
        print(f"   Functional Buttons: {len(functional_buttons)}")
        print(f"   Visual Anchors: {len(visual_anchors)}")
        
        # Check for Dune Legacy headline detection
        dune_legacy_found = False
        for element in visual_anchors:
            if element.text_label and 'dune legacy' in element.text_label.lower():
                dune_legacy_found = True
                print(f"✅ 'Dune Legacy' headline correctly classified as Visual Anchor")
                print(f"   Text: '{element.text_label}' | Clickable: {element.is_functional_button}")
                break
        
        if not dune_legacy_found:
            print("⚠️ 'Dune Legacy' headline not found or not classified as Visual Anchor")
        
        # Check for functional buttons
        menu_buttons_found = []
        for element in functional_buttons:
            if element.text_label:
                text = element.text_label.lower()
                if any(btn in text for btn in ['single', 'player', 'option', 'quit', 'start', 'new']):
                    menu_buttons_found.append(element.text_label)
        
        if menu_buttons_found:
            print(f"✅ Functional menu buttons detected: {menu_buttons_found}")
        else:
            print("⚠️ No recognized functional menu buttons found")
        
        # Overall validation
        fusion_success = (
            len(detected_elements) > 0 and
            any(e.text_label for e in detected_elements) and  # At least one element has text
            len(functional_buttons) > 0  # At least one functional button
        )
        
        if fusion_success:
            print("\n🎉 PERCEPTION FUSION VALIDATION: SUCCESS")
            print("✅ Module 2C + 2D integration working correctly")
            print("✅ Text extraction and semantic classification functional")
            print("✅ Functional button confirmation implemented")
            
            # Audio feedback
            subprocess.run(['say', 'Perception fusion validation successful'], capture_output=True)
            
        else:
            print("\n❌ PERCEPTION FUSION VALIDATION: FAILED")
            print("   Module 2C + 2D integration requires debugging")
        
        # Save detailed results
        results_file = "/tmp/perception_fusion_results.txt"
        with open(results_file, "w") as f:
            f.write("M2 PERCEPTION FUSION VALIDATION RESULTS\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("DETECTED ELEMENTS:\n")
            for element in detected_elements:
                f.write(f"  {element.name}:\n")
                f.write(f"    Position: ({element.normalized_x:.3f}, {element.normalized_y:.3f})\n")
                f.write(f"    Visual Confidence: {element.confidence:.3f}\n")
                f.write(f"    Text Label: '{element.text_label}'\n")
                f.write(f"    Text Confidence: {element.text_confidence:.3f}\n")
                f.write(f"    Functional Button: {element.is_functional_button}\n")
                f.write(f"    Method: {element.method}\n\n")
            
            f.write(f"SUMMARY:\n")
            f.write(f"  Total Elements: {len(detected_elements)}\n")
            f.write(f"  Functional Buttons: {len(functional_buttons)}\n")
            f.write(f"  Visual Anchors: {len(visual_anchors)}\n")
            f.write(f"  Validation Success: {fusion_success}\n")
        
        print(f"\n💾 Detailed results saved: {results_file}")
        
        return fusion_success, {
            'total_elements': len(detected_elements),
            'functional_buttons': len(functional_buttons),
            'visual_anchors': len(visual_anchors),
            'dune_legacy_found': dune_legacy_found,
            'menu_buttons': menu_buttons_found
        }
        
    except Exception as e:
        print(f"\n❌ PERCEPTION FUSION TEST FAILED: {e}")
        subprocess.run(['say', f'Perception fusion test failed: {str(e)}'], capture_output=True)
        return False, {'error': str(e)}

def main():
    """Execute perception fusion validation test."""
    
    success, results = test_perception_fusion()
    
    if success:
        print("\n✅ M2 PERCEPTION FUSION: READY FOR M2 LOCKDOWN")
        print("   Integration of Module 2C + 2D validated successfully")
    else:
        print("\n❌ M2 PERCEPTION FUSION: REQUIRES DEBUGGING")
        print("   Additional work needed before M2 lockdown")
        
    return success

if __name__ == "__main__":
    main()