#!/usr/bin/env python3
"""
Test runner for all chore system tests.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all test suites."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_suite(suite_name):
    """Run a specific test suite."""
    loader = unittest.TestLoader()
    
    if suite_name == 'comprehensive':
        import test_comprehensive
        suite = loader.loadTestsFromModule(test_comprehensive)
    elif suite_name == 'integration':
        import test_integration
        suite = loader.loadTestsFromModule(test_integration)
    elif suite_name == 'performance':
        import test_performance
        suite = loader.loadTestsFromModule(test_performance)
    else:
        print(f"Unknown test suite: {suite_name}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        suite_name = sys.argv[1]
        success = run_specific_suite(suite_name)
    else:
        print("Running all test suites...")
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
