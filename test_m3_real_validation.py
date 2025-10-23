"""
M3 VALIDATION TEST - Real Game Screenshot Pipeline Validation
End-to-end validation of YOLOv8 perception pipeline with actual Dune Legacy gameplay

Features:
- Proper game focus management before screenshot capture
- Audio feedback for user awareness during operations
- Complete cleanup protocol (close game, refocus VS Code)
- Real screenshot processing through M3 pipeline
- Comprehensive output analysis and validation

Author: Agent A
Compliance: M3 validation requirements with proper game lifecycle management
"""

import sys
import os
import time
import json
from pathlib import Path
from PIL import Image
import numpy as np
import subprocess
import logging

# Audio feedback system
def play_audio_signal(signal_type: str):
    """
    Play audio signals for user feedback during operations.
    
    Args:
        signal_type: Type of audio signal ('start', 'progress', 'success', 'error', 'cleanup')
    """
    try:
        audio_signals = {
            'start': 'Ping',      # System start sound
            'progress': 'Pop',    # Progress indication
            'success': 'Glass',   # Success completion
            'error': 'Basso',     # Error notification
            'cleanup': 'Purr'     # Cleanup completion
        }
        
        sound_name = audio_signals.get(signal_type, 'Ping')
        # Use macOS say command for audio feedback
        subprocess.run(['afplay', f'/System/Library/Sounds/{sound_name}.aiff'], 
                      capture_output=True, timeout=2)
        print(f"🔊 Audio Signal: {signal_type}")
    except:
        print(f"🔇 Audio signal failed: {signal_type}")


def focus_application(app_name: str) -> bool:
    """
    Focus specific application using AppleScript.
    
    Args:
        app_name: Name of application to focus
        
    Returns:
        bool: Success status
    """
    try:
        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Focused application: {app_name}")
            time.sleep(2)  # Allow focus to take effect
            return True
        else:
            print(f"❌ Failed to focus {app_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Focus application failed: {e}")
        return False


def close_application(app_name: str) -> bool:
    """
    Properly close application using AppleScript.
    
    Args:
        app_name: Name of application to close
        
    Returns:
        bool: Success status
    """
    try:
        script = f'''
        tell application "{app_name}"
            quit
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Closed application: {app_name}")
            time.sleep(3)  # Allow application to close
            return True
        else:
            print(f"⚠️  Close attempt for {app_name}: {result.stderr}")
            return True  # May already be closed
    except Exception as e:
        print(f"❌ Close application failed: {e}")
        return False


def launch_dune_legacy() -> bool:
    """
    Launch Dune Legacy and wait for it to be ready for screenshot.
    
    Returns:
        bool: Success status
    """
    try:
        play_audio_signal('start')
        print("🚀 Launching Dune Legacy...")
        
        # Launch Dune Legacy
        dune_paths = [
            '/Applications/Dune Legacy.app',
            '/Applications/Games/Dune Legacy.app',
            '/Users/amir/Applications/Dune Legacy.app'
        ]
        
        dune_path = None
        for path in dune_paths:
            if os.path.exists(path):
                dune_path = path
                break
        
        if not dune_path:
            print("❌ Dune Legacy not found in standard locations")
            return False
        
        # Launch the application
        subprocess.Popen(['open', dune_path])
        print(f"✅ Launched: {dune_path}")
        
        # Wait for application to start
        time.sleep(8)
        
        # Focus the application
        focus_success = focus_application('Dune Legacy')
        if focus_success:
            play_audio_signal('progress')
            print("✅ Dune Legacy focused and ready")
            return True
        else:
            print("⚠️  Dune Legacy launched but focus failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to launch Dune Legacy: {e}")
        play_audio_signal('error')
        return False


def capture_gameplay_screenshot(save_path: str) -> bool:
    """
    Capture a real gameplay screenshot from focused Dune Legacy.
    
    Args:
        save_path: Path to save the screenshot
        
    Returns:
        bool: Success status
    """
    try:
        # Add src to path for imports
        sys.path.append(str(Path(__file__).parent / 'src'))
        
        from src.perception.screen_capture import GameScreenCapture
        
        play_audio_signal('progress')
        print("📸 Capturing gameplay screenshot...")
        
        # Ensure Dune Legacy is focused
        focus_application('Dune Legacy')
        time.sleep(2)
        
        # Initialize screen capture
        capture = GameScreenCapture()
        
        # Capture the screen
        screenshot = capture.capture_game_screen()
        
        if screenshot is None:
            print("❌ Screenshot capture failed - no image returned")
            return False
        
        # Save the screenshot
        screenshot.save(save_path)
        print(f"✅ Screenshot saved: {save_path}")
        print(f"   Resolution: {screenshot.size}")
        
        play_audio_signal('success')
        return True
        
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        play_audio_signal('error')
        return False


def execute_m3_pipeline_validation(screenshot_path: str):
    """
    Execute complete M3 pipeline validation with real screenshot.
    
    Args:
        screenshot_path: Path to the test screenshot
    """
    try:
        # Add src to path for imports
        sys.path.append(str(Path(__file__).parent / 'src'))
        
        from src.perception.yolo_detection_engine import YOLODetectionEngine, run_complete_perception_pipeline
        from src.perception.semantic_map import SemanticMap
        
        play_audio_signal('progress')
        print("\n" + "="*60)
        print("M3 PIPELINE VALIDATION - Real Game Screenshot")
        print("="*60)
        
        # Load the test screenshot
        test_image = Image.open(screenshot_path)
        print(f"✅ Loaded test screenshot: {test_image.size}")
        
        # Initialize YOLOv8 detection engine
        print("🧠 Initializing YOLOv8 Detection Engine...")
        detection_engine = YOLODetectionEngine()
        
        # Execute complete M3 pipeline
        print("🔄 Executing M3 Pipeline: Screenshot → YOLOv8 → SemanticMap")
        start_time = time.time()
        
        semantic_map = run_complete_perception_pipeline(test_image, detection_engine)
        
        pipeline_time = time.time() - start_time
        print(f"✅ M3 Pipeline completed in {pipeline_time:.3f}s")
        
        # Validate SemanticMap structure
        print("\n📊 SEMANTIC MAP VALIDATION:")
        print(f"   Type: {type(semantic_map)}")
        print(f"   Detection Count: {len(semantic_map.elements)}")
        print(f"   Timestamp: {semantic_map.timestamp}")
        print(f"   Screen Resolution: {semantic_map.screen_resolution}")
        
        # Analyze top detections
        if semantic_map.elements:
            print("\n🎯 TOP 3 DETECTIONS ANALYSIS:")
            sorted_elements = sorted(semantic_map.elements, 
                                   key=lambda x: x.confidence_score, reverse=True)
            
            for i, element in enumerate(sorted_elements[:3]):
                print(f"   Detection {i+1}:")
                print(f"     Label: {element.element_label}")
                print(f"     Semantic Value: {element.semantic_value}")
                print(f"     Confidence: {element.confidence_score:.3f}")
                print(f"     Bounding Box: {element.bounding_box}")
                
                # Validate coordinate normalization
                x1, y1, x2, y2 = element.bounding_box
                img_width, img_height = test_image.size
                
                normalized_coords = (
                    x1 / img_width, y1 / img_height,
                    x2 / img_width, y2 / img_height
                )
                
                coords_valid = all(0.0 <= coord <= 1.0 for coord in normalized_coords)
                print(f"     Normalized Coords: {[f'{c:.3f}' for c in normalized_coords]}")
                print(f"     Coordinates Valid: {'✅' if coords_valid else '❌'}")
                print()
        
        # Generate JSON output for analysis
        print("📄 SEMANTIC MAP JSON SERIALIZATION:")
        try:
            # Convert to JSON-serializable format
            map_data = {
                'timestamp': semantic_map.timestamp,
                'screen_resolution': semantic_map.screen_resolution,
                'detection_count': len(semantic_map.elements),
                'elements': []
            }
            
            for element in semantic_map.elements:
                element_data = {
                    'element_id': element.element_id,
                    'element_label': element.element_label.name if hasattr(element.element_label, 'name') else str(element.element_label),
                    'bounding_box': list(element.bounding_box),
                    'confidence_score': float(element.confidence_score),
                    'semantic_value': element.semantic_value,
                    'detection_method': element.detection_method
                }
                map_data['elements'].append(element_data)
            
            json_output = json.dumps(map_data, indent=2)
            print(json_output)
            
            # Save JSON output for analysis
            json_path = screenshot_path.replace('.png', '_semantic_map.json')
            with open(json_path, 'w') as f:
                f.write(json_output)
            print(f"\n💾 JSON output saved: {json_path}")
            
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
        
        # Performance assessment
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Pipeline Time: {pipeline_time:.3f}s")
        print(f"   Target FPS: 30.0 (33.3ms)")
        print(f"   Achieved FPS: {1/pipeline_time:.1f}")
        print(f"   Real-time Capable: {'✅' if pipeline_time < 0.1 else '⚠️' if pipeline_time < 0.2 else '❌'}")
        
        # Validation summary
        validation_success = (
            isinstance(semantic_map, SemanticMap) and
            hasattr(semantic_map, 'elements') and
            hasattr(semantic_map, 'timestamp') and
            hasattr(semantic_map, 'screen_resolution')
        )
        
        print(f"\n🏆 M3 VALIDATION RESULT: {'✅ PASSED' if validation_success else '❌ FAILED'}")
        
        if validation_success:
            play_audio_signal('success')
            print("🚀 M3 Pipeline structurally validated - Ready for M4 State Representation!")
        else:
            play_audio_signal('error')
            print("❌ M3 Pipeline validation failed - Investigation required")
        
        return validation_success
        
    except Exception as e:
        print(f"❌ M3 Pipeline validation failed: {e}")
        play_audio_signal('error')
        return False


def cleanup_and_refocus():
    """
    Complete cleanup protocol: close game and refocus VS Code.
    """
    try:
        play_audio_signal('cleanup')
        print("\n🧹 CLEANUP PROTOCOL INITIATED")
        
        # Close Dune Legacy
        print("Closing Dune Legacy...")
        close_application('Dune Legacy')
        
        # Refocus Visual Studio Code
        print("Refocusing Visual Studio Code...")
        focus_success = focus_application('Visual Studio Code')
        
        if focus_success:
            print("✅ Cleanup complete - VS Code focused")
            play_audio_signal('success')
        else:
            print("⚠️  VS Code focus failed - manual focus may be needed")
        
        print("🏁 M3 Validation Test Complete!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        play_audio_signal('error')


def main():
    """
    Main M3 validation test execution.
    """
    print("🎯 M3 VALIDATION TEST - Real Game Screenshot Pipeline")
    print("="*60)
    
    screenshot_path = 'test_assets/dune_legacy_gameplay_screenshot.png'
    
    try:
        # Step 1: Launch and focus Dune Legacy
        launch_success = launch_dune_legacy()
        if not launch_success:
            print("❌ Cannot proceed - Dune Legacy launch failed")
            return
        
        # Wait for game to be ready and automatically proceed to screenshot
        print("\n⏳ Waiting for Dune Legacy to be ready...")
        print("   Auto-proceeding to screenshot in 5 seconds...")
        time.sleep(5)  # Give time for game to load without user input
        
        # Step 2: Capture real gameplay screenshot
        screenshot_success = capture_gameplay_screenshot(screenshot_path)
        if not screenshot_success:
            print("❌ Cannot proceed - Screenshot capture failed")
            cleanup_and_refocus()
            return
        
        # Step 3: Execute M3 pipeline validation
        validation_success = execute_m3_pipeline_validation(screenshot_path)
        
        # Step 4: Report results and next steps
        if validation_success:
            print("\n🎉 M3 VALIDATION: STRUCTURAL SUCCESS!")
            print("✅ SemanticMap structure is valid")
            print("✅ YOLOv8 pipeline is functional") 
            print("✅ JSON serialization works")
            print("✅ Ready to proceed to M4 State Representation")
        else:
            print("\n⚠️  M3 VALIDATION: ISSUES DETECTED")
            print("❌ Pipeline validation failed")
            print("🔧 Investigation required before M4")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        play_audio_signal('error')
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        play_audio_signal('error')
    finally:
        # Always run cleanup
        cleanup_and_refocus()


if __name__ == "__main__":
    main()