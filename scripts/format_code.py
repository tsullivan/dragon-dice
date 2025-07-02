#!/usr/bin/env python3
"""
Auto-format code using ruff formatter.
"""

import subprocess
import sys


def format_code():
    """Format code using ruff formatter."""
    print("🎨 Formatting code with ruff...")

    # Define directories to format
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
        # Run ruff format (will modify files)
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format"] + directories + ["--config", "ruff.toml"],
            capture_output=True,
            text=True,
        )

        print(f"Return code: {result.returncode}")

        if result.stdout:
            print("\n📊 Formatting results:")
            print(result.stdout)

        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Code formatting completed successfully!")
        else:
            print("❌ Some formatting issues occurred")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running ruff format: {e}")
        return False


if __name__ == "__main__":
    success = format_code()
    sys.exit(0 if success else 1)
