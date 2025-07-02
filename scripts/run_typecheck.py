#!/usr/bin/env python3
"""
Run type checking on the Dragon Dice codebase and generate a report.
"""

import subprocess
import sys


def run_mypy():
    """Run mypy type checking on main code directories."""
    print("🔍 Running type checking with mypy...")

    # Define directories to check
    directories = [
        "components/",
        "models/",
        "views/",
        "game_logic/",
        "controllers/",
        "config/",
        "utils/",
        "dragon_dice.py",
        "main_window.py",
    ]

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy"]
            + directories
            + ["--config-file", "mypy.ini", "--show-error-codes", "--pretty"],
            capture_output=True,
            text=True,
        )

        print(f"Return code: {result.returncode}")

        if result.stdout:
            print("\n📊 Type checking results:")
            print(result.stdout)

        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)

        # Count errors
        error_lines = [line for line in result.stdout.split("\n") if "error:" in line]
        print(f"\n📈 Summary: {len(error_lines)} type errors found")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running mypy: {e}")
        return False


if __name__ == "__main__":
    success = run_mypy()
    sys.exit(0 if success else 1)
