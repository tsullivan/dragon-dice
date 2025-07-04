#!/usr/bin/env python3
"""
Development environment setup script for Dragon Dice Companion.
Installs all dependencies and sets up development tools.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command with error handling."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def main():
    """Set up the development environment."""
    project_root = Path(__file__).parent.parent

    print("🚀 Setting up Dragon Dice Companion development environment...")
    print(f"📁 Project root: {project_root}")

    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Not in a virtual environment. Consider using 'python -m venv venv'")

    # Install requirements
    requirements_file = project_root / "requirements.txt"
    if not run_command(f"pip install -r {requirements_file}", "Installing Python dependencies"):
        return False

    # Install development packages
    dev_packages = [
        "pip-tools",  # For managing dependencies
        "twine",  # For package distribution
    ]

    for package in dev_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False

    # Set up pre-commit hooks (if pre-commit is installed)
    if run_command("which pre-commit", "Checking for pre-commit"):
        run_command("pre-commit install", "Setting up pre-commit hooks")

    # Run initial validation
    print("\n🔍 Running initial validation...")

    # Type check
    run_command("python scripts/run_typecheck.py", "Type checking")

    # Linting
    run_command("python scripts/run_linter.py", "Code linting")

    # Test discovery
    run_command("python -m pytest --collect-only -q", "Test discovery")

    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("   • Run 'python dragon_dice.py' to start the application")
    print("   • Run 'python -m pytest' to run tests")
    print("   • Run 'python scripts/run_linter.py' for code quality checks")
    print("   • Run 'python scripts/run_typecheck.py' for type checking")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
