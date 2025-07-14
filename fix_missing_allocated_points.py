#!/usr/bin/env python3
"""
Script to fix missing 'allocated_points' fields in test files.
Adds 'allocated_points': 10 to armies that are missing this field.
"""

import os
import re
import sys


def fix_allocated_points_in_file(file_path):
    """Fix missing allocated_points in a single file."""
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Pattern to find army definitions that don't have allocated_points
    # Look for army dict with name and location but no allocated_points
    army_pattern = r'("(?:home|campaign|horde)":\s*\{[^}]*"location":\s*"[^"]*"[^}]*)"units":'
    
    def check_and_add_allocated_points(match):
        army_section = match.group(1)
        nonlocal changes_made
        
        # Check if allocated_points is already present
        if 'allocated_points' not in army_section:
            # Add allocated_points before units
            changes_made += 1
            return army_section + '\n                        "allocated_points": 10,\n                        "units":'
        else:
            # Already has allocated_points, don't change
            return match.group(0)
    
    # Apply the fix
    content = re.sub(army_pattern, check_and_add_allocated_points, content, flags=re.DOTALL)
    
    # Only write if changes were made
    if changes_made > 0 and content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed {changes_made} missing allocated_points in {file_path}")
        return True
    
    return False


def main():
    """Fix allocated_points in all test files."""
    test_dir = "test/e2e"
    
    if not os.path.exists(test_dir):
        print(f"Test directory {test_dir} not found")
        return 1
    
    total_files_fixed = 0
    
    # Process all Python test files
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py') and file.startswith('test_'):
                file_path = os.path.join(root, file)
                if fix_allocated_points_in_file(file_path):
                    total_files_fixed += 1
    
    print(f"\nFixed allocated_points issues in {total_files_fixed} files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())