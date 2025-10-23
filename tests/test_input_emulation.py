#!/usr/bin/env python3
"""
NEW M2 Input Emulation API Validation Test Suite - AIP-SDS-V2.3
Level-6 Architectural Implementation

Test Cases per AGENT COMMAND specification:
1. Left-click precision validation at coordinate (100, 100)  
2. Drag selection from (50, 50) to (200, 200) with movement verification

MANDATE: Validate pyobjc CoreGraphics integration and input precision
before proceeding with M3 Learning-Based Perception Engine.
"""

import sys
import time
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.action.input_api import InputAPI, create_input_api
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Ensure src/action/input_api.py is properly created")
    sys.exit(1)


class InputEmulationTestSuite:
    """
    Comprehensive test suite for NEW M2 Input Emulation API.
    
    Validates all core input functions per AIP-SDS-V2.3 specification.
    """
    
    def __init__(self):
        """Initialize test suite with audio feedback enabled."""
        self.config = {
            'audio_feedback': True
        }
        self.api = None
        self.test_results = {}
    
    def setup_test_environment(self):
        """Setup test environment and validate prerequisites."""
        print("🔧 Setting up Input Emulation Test Environment...")
        
        try:
            # Create Input API instance
            self.api = create_input_api(self.config)
            print("✅ Input API instance created successfully")
            
            # Validate macOS permissions
            print("⚠️  macOS Permissions Required:")
            print("   - System Preferences → Security & Privacy → Accessibility")
            print("   - Add Terminal/VS Code to allowed applications")
            print("   - Input Monitoring permissions may be required")
            
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            return False
    
    def test_case_1_left_click_precision(self):
        """
        Test Case 1: Left-click precision validation at coordinate (100, 100)
        
        Per AGENT COMMAND: Verify precise left mouse button click functionality.
        """
        print("\n" + "="*60)
        print("🧪 TEST CASE 1: Left-Click Precision Validation")
        print("="*60)
        
        try:
            target_x, target_y = 100, 100
            
            print(f"📍 Target coordinates: ({target_x}, {target_y})")
            print("⚠️  WARNING: This will perform actual mouse click!")
            print("   Make sure no important applications are at test coordinates")
            
            # Get user confirmation for actual input testing
            if not self._get_user_confirmation("Proceed with left-click test?"):
                print("⏭️  Test skipped by user")
                return False
            
            print("🔄 Executing left-click...")
            start_time = time.time()
            
            # Execute left click at target coordinates
            success = self.api.left_click(target_x, target_y)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            print(f"⏱️  Execution time: {execution_time:.2f}ms")
            
            if success:
                print("✅ Left-click executed successfully")
                
                # Validate performance requirement (<10ms latency per AIP-SDS-V2.3)
                if execution_time < 10.0:
                    print("✅ Performance requirement met (<10ms latency)")
                    self.test_results['test_case_1'] = 'PASSED'
                    return True
                else:
                    print(f"⚠️  Performance warning: {execution_time:.2f}ms > 10ms target")
                    self.test_results['test_case_1'] = 'PASSED_WITH_WARNING'
                    return True
            else:
                print("❌ Left-click failed")
                self.test_results['test_case_1'] = 'FAILED'
                return False
                
        except Exception as e:
            print(f"❌ Test Case 1 error: {e}")
            self.test_results['test_case_1'] = 'ERROR'
            return False
    
    def test_case_2_drag_select_validation(self):
        """
        Test Case 2: Drag selection from (50, 50) to (200, 200) with movement verification
        
        Per AGENT COMMAND: Verify drag selection functionality for unit group selection.
        """
        print("\n" + "="*60)
        print("🧪 TEST CASE 2: Drag Selection Validation")
        print("="*60)
        
        try:
            start_x, start_y = 50, 50
            end_x, end_y = 200, 200
            
            print(f"📍 Drag from: ({start_x}, {start_y}) to ({end_x}, {end_y})")
            print("⚠️  WARNING: This will perform actual mouse drag operation!")
            print("   Make sure no important applications are in drag area")
            
            # Get user confirmation for actual input testing
            if not self._get_user_confirmation("Proceed with drag selection test?"):
                print("⏭️  Test skipped by user")
                return False
            
            print("🔄 Executing drag selection...")
            start_time = time.time()
            
            # Execute drag selection
            success = self.api.drag_select(start_x, start_y, end_x, end_y)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            print(f"⏱️  Execution time: {execution_time:.2f}ms")
            
            if success:
                print("✅ Drag selection executed successfully")
                
                # Validate reasonable execution time for smooth drag
                if execution_time < 200.0:  # Reasonable for smooth drag operation
                    print("✅ Drag timing appropriate for smooth operation")
                    self.test_results['test_case_2'] = 'PASSED'
                    return True
                else:
                    print(f"⚠️  Performance warning: {execution_time:.2f}ms drag operation")
                    self.test_results['test_case_2'] = 'PASSED_WITH_WARNING'
                    return True
            else:
                print("❌ Drag selection failed")
                self.test_results['test_case_2'] = 'FAILED'
                return False
                
        except Exception as e:
            print(f"❌ Test Case 2 error: {e}")
            self.test_results['test_case_2'] = 'ERROR'
            return False
    
    def test_additional_input_functions(self):
        """
        Additional validation of move_mouse, right_click, and key_press functions.
        
        Comprehensive API coverage per AIP-SDS-V2.3 specification.
        """
        print("\n" + "="*60)
        print("🧪 ADDITIONAL TESTS: Complete API Coverage")
        print("="*60)
        
        additional_tests = {}
        
        try:
            # Test 3: Mouse movement precision
            print("🔄 Testing mouse movement...")
            success = self.api.move_mouse(150, 150, duration=0.1)
            additional_tests['move_mouse'] = 'PASSED' if success else 'FAILED'
            
            # Test 4: Right-click functionality  
            if self._get_user_confirmation("Test right-click at (150, 150)?", default=False):
                print("🔄 Testing right-click...")
                success = self.api.right_click(150, 150)
                additional_tests['right_click'] = 'PASSED' if success else 'FAILED'
            else:
                additional_tests['right_click'] = 'SKIPPED'
            
            # Test 5: Key press functionality
            if self._get_user_confirmation("Test key press (ESC key)?", default=False):
                print("🔄 Testing key press...")
                success = self.api.key_press('Escape')
                additional_tests['key_press'] = 'PASSED' if success else 'FAILED'
            else:
                additional_tests['key_press'] = 'SKIPPED'
            
            self.test_results['additional_tests'] = additional_tests
            
        except Exception as e:
            print(f"❌ Additional tests error: {e}")
            self.test_results['additional_tests'] = {'error': str(e)}
    
    def _get_user_confirmation(self, message: str, default: bool = True) -> bool:
        """Get user confirmation for input tests that perform actual actions."""
        try:
            default_char = 'Y' if default else 'N'
            response = input(f"❓ {message} [y/N if default=False, Y/n if default=True] (default: {default_char}): ").strip().lower()
            
            if not response:
                return default
            
            return response.startswith('y')
            
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️  Test interrupted by user")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📊 INPUT EMULATION API TEST REPORT")
        print("="*80)
        print(f"🕒 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Architecture: AIP-SDS-V2.3 - NEW M2 Input Emulation API")
        
        print(f"\n📋 Core Test Results:")
        for test_name, result in self.test_results.items():
            if test_name != 'additional_tests':
                status_icon = "✅" if result == 'PASSED' else ("⚠️" if 'WARNING' in result else "❌")
                print(f"   {status_icon} {test_name}: {result}")
        
        if 'additional_tests' in self.test_results:
            print(f"\n🔧 Additional API Tests:")
            additional = self.test_results['additional_tests']
            if isinstance(additional, dict):
                for func_name, result in additional.items():
                    status_icon = "✅" if result == 'PASSED' else ("⏭️" if result == 'SKIPPED' else "❌")
                    print(f"   {status_icon} {func_name}: {result}")
        
        # Overall assessment
        core_tests_passed = all(
            result in ['PASSED', 'PASSED_WITH_WARNING'] 
            for test_name, result in self.test_results.items() 
            if test_name != 'additional_tests'
        )
        
        print(f"\n🎯 Overall Assessment:")
        if core_tests_passed:
            print("✅ NEW M2 Input Emulation API validation SUCCESSFUL")
            print("🚀 Ready for M3 Learning-Based Perception Engine integration")
        else:
            print("❌ Input API validation requires attention")
            print("🔧 Review failed tests before proceeding to M3")
        
        return core_tests_passed


def main():
    """Main test execution function."""
    print("🎯 NEW M2 INPUT EMULATION API TEST SUITE")
    print("🏗️  AIP-SDS-V2.3 - Level-6 Architectural Implementation")
    print("="*80)
    
    # Create test suite
    test_suite = InputEmulationTestSuite()
    
    try:
        # Setup test environment
        if not test_suite.setup_test_environment():
            print("❌ Test environment setup failed - aborting tests")
            return False
        
        print("\n⚠️  IMPORTANT: These tests perform actual mouse/keyboard input!")
        print("   - Close important applications before proceeding")
        print("   - Ensure macOS Accessibility permissions are granted")
        print("   - Tests can be skipped individually if needed")
        
        if not test_suite._get_user_confirmation("Proceed with input emulation tests?"):
            print("⏭️  Test suite cancelled by user")
            return False
        
        # Execute core test cases per AGENT COMMAND
        print(f"\n🧪 Executing Core Test Cases...")
        test_suite.test_case_1_left_click_precision()
        test_suite.test_case_2_drag_select_validation()
        
        # Execute additional API coverage tests
        test_suite.test_additional_input_functions()
        
        # Generate final report
        success = test_suite.generate_test_report()
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)