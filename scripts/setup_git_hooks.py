#!/usr/bin/env python3
"""
Script to set up git hooks for the Dragon Dice project.
Provides options for strict or lenient pre-commit checking.
"""

import os
import shutil
import sys
from pathlib import Path


def is_git_repo():
    """Check if we're in a git repository."""
    return Path(".git").exists()


def create_strict_hook():
    """Create a strict pre-commit hook that blocks commits on any issues."""
    hook_content = """#!/bin/bash
#
# Git pre-commit hook for Dragon Dice project (STRICT MODE)
# Runs type checking and linting before allowing commits
#

set -e  # Exit on any error

echo "🔍 Running pre-commit checks (STRICT MODE)..."

# Check if we're in the right directory
if [ ! -f "dragon_dice.py" ]; then
    echo "❌ Error: Not in Dragon Dice project root directory"
    exit 1
fi

# Function to run a check and handle results
run_check() {
    local check_name="$1"
    local script_path="$2"
    
    echo "🔄 Running $check_name..."
    
    if python "$script_path"; then
        echo "✅ $check_name passed"
        return 0
    else
        echo "❌ $check_name failed"
        echo ""
        echo "💡 To fix issues automatically, run:"
        echo "   python scripts/format_code.py"
        echo ""
        echo "💡 To skip this hook temporarily, run:"
        echo "   git commit --no-verify"
        echo ""
        return 1
    fi
}

# Run type checking (strict - must pass)
if ! run_check "Type checking" "scripts/run_typecheck.py"; then
    echo "❌ Commit blocked due to type checking errors"
    exit 1
fi

# Run linting (strict - must pass)  
if ! run_check "Code linting" "scripts/run_linter.py"; then
    echo "❌ Commit blocked due to linting errors"
    exit 1
fi

echo ""
echo "🎉 All pre-commit checks passed! Proceeding with commit..."
echo ""
"""
    return hook_content


def create_lenient_hook():
    """Create a lenient pre-commit hook that warns but doesn't block commits."""
    hook_content = """#!/bin/bash
#
# Git pre-commit hook for Dragon Dice project (LENIENT MODE)
# Runs checks but only warns, doesn't block commits
#

echo "🔍 Running pre-commit checks (LENIENT MODE)..."

# Check if we're in the right directory
if [ ! -f "dragon_dice.py" ]; then
    echo "❌ Error: Not in Dragon Dice project root directory"
    exit 1
fi

# Function to run a check and handle results
run_check() {
    local check_name="$1"
    local script_path="$2"
    
    echo "🔄 Running $check_name..."
    
    if python "$script_path"; then
        echo "✅ $check_name passed"
        return 0
    else
        echo "⚠️  $check_name failed (warnings only)"
        echo "💡 Consider running: python scripts/format_code.py"
        return 0  # Don't block commit
    fi
}

# Run checks (warnings only)
run_check "Type checking" "scripts/run_typecheck.py"
run_check "Code linting" "scripts/run_linter.py"

echo ""
echo "ℹ️  Pre-commit checks completed (lenient mode)"
echo "💡 Consider fixing any issues for better code quality"
echo ""
"""
    return hook_content


def install_hook(hook_content, mode_name):
    """Install the git hook."""
    hooks_dir = Path(".git/hooks")
    hook_path = hooks_dir / "pre-commit"

    if not hooks_dir.exists():
        print(f"❌ Error: {hooks_dir} does not exist")
        return False

    # Backup existing hook if it exists
    if hook_path.exists():
        backup_path = hook_path.with_suffix(".backup")
        shutil.copy2(hook_path, backup_path)
        print(f"📦 Backed up existing hook to {backup_path}")

    # Write new hook
    with open(hook_path, "w") as f:
        f.write(hook_content)

    # Make executable
    os.chmod(hook_path, 0o755)

    print(f"✅ Installed {mode_name} pre-commit hook")
    return True


def remove_hook():
    """Remove the pre-commit hook."""
    hook_path = Path(".git/hooks/pre-commit")

    if hook_path.exists():
        backup_path = hook_path.with_suffix(".backup")
        if backup_path.exists():
            shutil.copy2(backup_path, hook_path)
            print("📦 Restored backup hook")
        else:
            hook_path.unlink()
            print("🗑️  Removed pre-commit hook")
        return True
    else:
        print("ℹ️  No pre-commit hook found")
        return False


def main():
    """Main function to handle user interaction."""
    print("🔧 Git Hooks Setup for Dragon Dice")
    print("=" * 40)

    if not is_git_repo():
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    print("\nAvailable options:")
    print("1. Install STRICT mode hook (blocks commits on issues)")
    print("2. Install LENIENT mode hook (warns but allows commits)")
    print("3. Remove existing hook")
    print("4. Show current hook status")
    print("5. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                hook_content = create_strict_hook()
                if install_hook(hook_content, "STRICT"):
                    print("\n✅ Strict mode enabled!")
                    print("   Commits will be blocked if type/lint checks fail")
                    print("   Use 'git commit --no-verify' to bypass if needed")
                break

            elif choice == "2":
                hook_content = create_lenient_hook()
                if install_hook(hook_content, "LENIENT"):
                    print("\n✅ Lenient mode enabled!")
                    print("   You'll see warnings but commits won't be blocked")
                break

            elif choice == "3":
                if remove_hook():
                    print("\n✅ Hook removed successfully")
                break

            elif choice == "4":
                hook_path = Path(".git/hooks/pre-commit")
                if hook_path.exists():
                    print(f"\n📋 Hook exists: {hook_path}")
                    # Try to detect mode from content
                    with open(hook_path) as f:
                        content = f.read()
                        if "STRICT MODE" in content:
                            print("   Mode: STRICT (blocks commits)")
                        elif "LENIENT MODE" in content:
                            print("   Mode: LENIENT (warnings only)")
                        else:
                            print("   Mode: UNKNOWN (custom hook)")
                else:
                    print("\n📋 No pre-commit hook installed")
                continue

            elif choice == "5":
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1-5.")
                continue

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
