"""
Script to run the tests for the Business Game application.

This script provides options for running all tests or specific test modules,
with configurable verbosity and test discovery patterns.

Usage:
    python run_tests.py                  # Run all tests with normal verbosity
    python run_tests.py -v               # Run all tests with high verbosity
    python run_tests.py -q               # Run all tests with minimal output
    python run_tests.py simulation       # Run only simulation tests
    python run_tests.py api              # Run only API tests
"""
import unittest
import sys
import os

def run_tests(pattern=None, verbosity=1):
    """
    Run tests matching the specified pattern with the given verbosity level.
    
    Args:
        pattern (str, optional): Pattern to match test files. Defaults to None.
        verbosity (int, optional): Verbosity level (0-2). Defaults to 1.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    if pattern:
        if os.path.isfile(f"tests/test_{pattern}.py"):
            # If a specific test module is requested
            test_suite = unittest.defaultTestLoader.discover("tests", pattern=f"test_{pattern}.py")
        else:
            print(f"Test module 'test_{pattern}.py' not found.")
            return False
    else:
        # Discover and run all tests
        test_suite = unittest.defaultTestLoader.discover("tests")
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=verbosity).run(test_suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()

if __name__ == "__main__":
    # Parse command line arguments
    verbosity = 1
    pattern = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-v":
            verbosity = 2
        elif arg == "-q":
            verbosity = 0
        else:
            pattern = arg
    
    # Run the tests
    success = run_tests(pattern, verbosity)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 