#!/usr/bin/env python3
"""
Run all model snapshot tests.

This script runs all the individual snapshot tests and provides a summary.
"""

import subprocess
import sys
from pathlib import Path


def run_test_file(test_file: Path) -> bool:
    """Run a single test file and return True if successful."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False


def main():
    """Run all snapshot tests."""
    test_files = [
        Path(__file__).parent / "species.py",
        Path(__file__).parent / "spells.py",
        Path(__file__).parent / "dragon_forms.py",
        Path(__file__).parent / "dragon_types.py",
        Path(__file__).parent / "terrains.py",
        Path(__file__).parent / "units.py",
        Path(__file__).parent / "die_faces.py",
    ]

    results = {}

    print("🔄 Running all model snapshot tests...")
    print("=" * 50)

    for test_file in test_files:
        test_name = test_file.stem
        print(f"\n📋 Running {test_name} tests...")

        success = run_test_file(test_file)
        results[test_name] = success

        if success:
            print(f"✅ {test_name} tests passed")
        else:
            print(f"❌ {test_name} tests failed")

    print("\n" + "=" * 50)
    print("📊 Summary:")

    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")

    print(f"\nResults: {passed}/{total} test files passed")

    if passed == total:
        print("\n🎉 All snapshot tests passed!")
        return 0
    print(f"\n⚠️  {total - passed} test file(s) failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
