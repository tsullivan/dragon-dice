#!/usr/bin/env python3
"""
Helper script to fix test setup data with missing required fields.
"""
import re
import os
from pathlib import Path

def fix_player_setup_in_file(file_path):
    """Fix player setup data in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Player setup without force_size and selected_dragons
    pattern1 = re.compile(
        r'(\{\s*"name":\s*"[^"]+",\s*"home_terrain":\s*"[^"]+",)\s*("armies":\s*\{)',
        re.MULTILINE | re.DOTALL
    )
    
    def replace_func1(match):
        return match.group(1) + '\n                "force_size": 24,\n                "selected_dragons": [],\n                ' + match.group(2)
    
    content = pattern1.sub(replace_func1, content)
    
    # Pattern 2: Army setup without allocated_points
    pattern2 = re.compile(
        r'(\s*"(?:home|campaign|horde)":\s*\{\s*"name":\s*"[^"]+",\s*(?:"location":\s*"[^"]+",)?)\s*("units":\s*\[)',
        re.MULTILINE | re.DOTALL
    )
    
    def replace_func2(match):
        if 'allocated_points' not in match.group(0):
            return match.group(1) + '\n                        "allocated_points": 10,\n                        ' + match.group(2)
        return match.group(0)
    
    content = pattern2.sub(replace_func2, content)
    
    # Save if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all test files with player setup data."""
    test_dir = Path("test")
    fixed_count = 0
    
    for file_path in test_dir.rglob("*.py"):
        if "player_setup_data" in file_path.read_text():
            if fix_player_setup_in_file(file_path):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files total.")

if __name__ == "__main__":
    main()