#!/usr/bin/env python3
"""
Run linting on the Dragon Dice codebase using ruff.
"""

import subprocess
import sys


def run_ruff_check():
    """Run ruff linter to check for code quality issues."""
    print("🔍 Running code linting with ruff...")

    # Define directories to check
    directories = [
        "components/",
        "models/",
        "views/",
        "game_logic/",
        "controllers/",
        "config/",
        "utils/",
        "scripts/",
        "dragon_dice.py",
        "main_window.py",
    ]

    try:
        # Run ruff check
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check"] + directories + ["--config", "ruff.toml"],
            capture_output=True,
            text=True,
        )

        print(f"Return code: {result.returncode}")

        if result.stdout:
            print("\n📊 Linting results:")
            print(result.stdout)

        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)

        # Count issues
        issue_lines = [
            line for line in result.stdout.split("\n") if ":" in line and ("error:" in line or "warning:" in line)
        ]
        print(f"\n📈 Summary: {len(issue_lines)} linting issues found")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running ruff: {e}")
        return False


def run_ruff_format_check():
    """Check if code formatting is consistent."""
    print("\n🎨 Checking code formatting with ruff...")

    directories = [
        "components/",
        "models/",
        "views/",
        "game_logic/",
        "controllers/",
        "config/",
        "utils/",
        "scripts/",
        "dragon_dice.py",
        "main_window.py",
    ]

    try:
        # Run ruff format check (--check flag only checks, doesn't modify)
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--check"] + directories + ["--config", "ruff.toml"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ All files are properly formatted!")
        else:
            print("❌ Some files need formatting:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print("\nTo fix formatting, run: python scripts/format_code.py")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error checking formatting: {e}")
        return False


if __name__ == "__main__":
    lint_success = run_ruff_check()
    format_success = run_ruff_format_check()

    print("\n🏁 Final Results:")
    print(f"  Linting: {'✅ PASS' if lint_success else '❌ ISSUES FOUND'}")
    print(f"  Formatting: {'✅ PASS' if format_success else '❌ NEEDS FIXING'}")

    # Exit with error code if either check failed
    sys.exit(0 if (lint_success and format_success) else 1)
