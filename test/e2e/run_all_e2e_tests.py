#!/usr/bin/env python3
"""
Test runner for all E2E tests in the Dragon Dice application.
Provides comprehensive testing with reporting and CI/CD integration.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_e2e_tests(
    test_categories=None, verbose=False, capture_output=True, save_screenshots=True
):
    """
    Run E2E tests with specified options.

    Args:
        test_categories: List of test categories to run (default: all)
        verbose: Enable verbose output
        capture_output: Capture test output
        save_screenshots: Save screenshots during visual tests
    """
    print("🧪 Dragon Dice E2E Test Suite")
    print("=" * 50)

    # Available test categories
    available_categories = {
        "complete": "test_complete_gameplay_flow.py",
        "visual": "test_visual_validation.py",
        "performance": "test_performance_validation.py",
        "existing": "test_*_flows.py",  # Existing E2E tests
    }

    if test_categories is None:
        test_categories = list(available_categories.keys())

    # Build pytest arguments
    pytest_args = []

    # Add test files based on categories
    test_dir = Path(__file__).parent
    for category in test_categories:
        if category in available_categories:
            test_pattern = available_categories[category]
            if category == "existing":
                # Add existing E2E tests
                existing_tests = list(test_dir.glob("test_*_flows.py"))
                pytest_args.extend(str(test) for test in existing_tests)
            else:
                test_file = test_dir / test_pattern
                if test_file.exists():
                    pytest_args.append(str(test_file))
                else:
                    print(f"⚠️ Test file not found: {test_file}")

    if not pytest_args:
        print("❌ No test files found to run")
        return False

    # Add pytest options
    if verbose:
        pytest_args.extend(["-v", "-s"])
    else:
        pytest_args.append("-v")

    if not capture_output:
        pytest_args.append("--capture=no")

    # Add custom markers and options
    pytest_args.extend(
        [
            "--tb=short",  # Short traceback format
            "--maxfail=5",  # Stop after 5 failures
            "--durations=10",  # Show 10 slowest tests
        ]
    )

    # Set environment variables for tests
    if save_screenshots:
        os.environ["E2E_SAVE_SCREENSHOTS"] = "1"

    print(f"Running tests: {', '.join(test_categories)}")
    print()

    # Run the tests
    start_time = time.time()
    result = pytest.main(pytest_args)
    end_time = time.time()

    # Print summary
    print("\n" + "=" * 50)
    print("🏁 E2E Tests Completed")
    print(f"⏱️ Total time: {end_time - start_time:.1f} seconds")

    if result == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {result}")

    return result == 0


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run Dragon Dice E2E tests")

    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["complete", "visual", "performance", "existing", "all"],
        default=["all"],
        help="Test categories to run",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--no-capture",
        action="store_true",
        help="Do not capture output (useful for debugging)",
    )

    parser.add_argument(
        "--no-screenshots",
        action="store_true",
        help="Do not save screenshots during visual tests",
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only essential tests (complete gameplay flow)",
    )

    args = parser.parse_args()

    # Handle special cases
    if "all" in args.categories:
        categories = ["complete", "visual", "performance", "existing"]
    elif args.quick:
        categories = ["complete"]
    else:
        categories = args.categories

    # Run the tests
    success = run_e2e_tests(
        test_categories=categories,
        verbose=args.verbose,
        capture_output=not args.no_capture,
        save_screenshots=not args.no_screenshots,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
    """Comprehensive test runner for end-to-end tests."""

    def __init__(self):
        self.app = None
        self.setup_qt_application()

    def setup_qt_application(self):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

    def run_all_tests(self):
        """Run all end-to-end test suites."""
        print("🚀 Dragon Dice Digital - End-to-End Test Suite")
        print("=" * 60)
        print("Testing complete user workflows to catch integration issues")
        print("=" * 60)

        # Create test suite
        suite = unittest.TestSuite()

        # Add all test classes
        test_classes = [
            TestFirstMarchFlows,
            TestPhaseTransitions,
            TestActionFlows,
        ]

        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)

        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            descriptions=True,
            failfast=False,
        )

        print(f"\nRunning {suite.countTestCases()} end-to-end tests...\n")

        result = runner.run(suite)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 E2E TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")

        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for test, _traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print(f"\n💥 ERRORS ({len(result.errors)}):")
            for test, _traceback in result.errors:
                print(f"  - {test}")

        if result.skipped:
            print(f"\n⏭️ SKIPPED ({len(result.skipped)}):")
            for test, reason in result.skipped:
                print(f"  - {test}: {reason}")

        success_rate = (
            (
                (result.testsRun - len(result.failures) - len(result.errors))
                / result.testsRun
                * 100
            )
            if result.testsRun > 0
            else 0
        )
        print(f"\n✨ Success Rate: {success_rate:.1f}%")

        if result.wasSuccessful():
            print("🎉 All E2E tests passed! The game workflows are working correctly.")
        else:
            print(
                "⚠️ Some E2E tests failed. Check the failures above for integration issues."
            )

        return result.wasSuccessful()

    def run_specific_test_suite(self, test_class_name):
        """Run a specific test suite by name."""
        test_classes = {
            "first_march": TestFirstMarchFlows,
            "phase_transitions": TestPhaseTransitions,
            "action_flows": TestActionFlows,
        }

        if test_class_name not in test_classes:
            print(f"❌ Unknown test suite: {test_class_name}")
            print(f"Available suites: {', '.join(test_classes.keys())}")
            return False

        test_class = test_classes[test_class_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()


def main():
    """Main entry point for the test runner."""
    runner = E2ETestRunner()

    if len(sys.argv) > 1:
        # Run specific test suite
        test_suite = sys.argv[1]
        success = runner.run_specific_test_suite(test_suite)
    else:
        # Run all tests
        success = runner.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
