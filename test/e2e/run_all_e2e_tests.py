#!/usr/bin/env python3
"""
Test runner for all end-to-end tests.
Provides a single command to run all E2E tests with detailed reporting.
"""

import unittest
import sys
import os
from PySide6.QtWidgets import QApplication

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from test_first_march_flows import TestFirstMarchFlows
from test_phase_transitions import TestPhaseTransitions
from test_action_flows import TestActionFlows


class E2ETestRunner:
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
            for test, traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print(f"\n💥 ERRORS ({len(result.errors)}):")
            for test, traceback in result.errors:
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
