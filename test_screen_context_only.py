#!/usr/bin/env python3
"""
SIMPLIFIED SCREEN CONTEXT VALIDATION TEST
Test the Screen Context Identifier using existing screenshots
"""

import sys
sys.path.insert(0, '/Users/amir/projects/ai_player')

from src.perception.perception_module import PerceptionModule
import os

def test_screen_context_identifier():
    """Test Screen Context Identifier with existing screenshots."""
    
    print("🧪 TESTING SCREEN CONTEXT IDENTIFIER")
    print("=" * 45)
    
    # Initialize perception module
    config = {
        'confidence_threshold': 0.8,
        'audio_feedback': False  # Disable audio for testing
    }
    
    perception = PerceptionModule(config)
    
    # Test with available screenshots
    test_screenshots = [
        '/tmp/reset_main_menu.png',
        '/tmp/after_click_screen.png',
        '/tmp/single_player_submenu.png',
        '/tmp/main_menu_before_nav.png'
    ]
    
    results = []
    
    for screenshot_path in test_screenshots:
        if os.path.exists(screenshot_path):
            print(f"\n📸 Testing: {os.path.basename(screenshot_path)}")
            print("-" * 40)
            
            try:
                context = perception.identify_screen_context(screenshot_path)
                results.append((screenshot_path, context))
                print(f"   🎯 Result: {context}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append((screenshot_path, f"ERROR: {e}"))
        else:
            print(f"\n⚠️ Screenshot not found: {screenshot_path}")
    
    # Summary
    print(f"\n📊 SCREEN CONTEXT IDENTIFICATION RESULTS:")
    print("=" * 50)
    
    for screenshot_path, context in results:
        filename = os.path.basename(screenshot_path)
        print(f"   {filename:<25} → {context}")
    
    # Validation
    main_menu_detected = any('MAIN_MENU' in result[1] for result in results)
    submenu_detected = any('SINGLE_PLAYER_SUB_MENU' in result[1] for result in results)
    
    print(f"\n✅ Main Menu Detection: {'SUCCESS' if main_menu_detected else 'FAILED'}")
    print(f"✅ Submenu Detection: {'SUCCESS' if submenu_detected else 'FAILED'}")
    
    if main_menu_detected and submenu_detected:
        print(f"\n🎉 SCREEN CONTEXT IDENTIFIER: WORKING")
    else:
        print(f"\n❌ SCREEN CONTEXT IDENTIFIER: NEEDS IMPROVEMENT")
    
    return main_menu_detected and submenu_detected

if __name__ == "__main__":
    success = test_screen_context_identifier()
    
    if success:
        print(f"\n📦 Screen Context Identifier validated - Ready for integration")
    else:
        print(f"\n🔧 Screen Context Identifier needs refinement")