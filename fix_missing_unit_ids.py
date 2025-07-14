#!/usr/bin/env python3
"""
Script to fix missing 'unit_id' fields in test files.
Adds unique unit_id to units that are missing this field.
"""

import os
import re
import sys


def fix_unit_ids_in_file(file_path):
    """Fix missing unit_id in a single file."""
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    unit_counter = 1
    
    # Pattern to find unit definitions that don't have unit_id
    # Look for unit dict with name but no unit_id
    def add_unit_id(match):
        nonlocal changes_made, unit_counter
        unit_section = match.group(0)
        
        # Check if unit_id is already present
        if '"unit_id"' not in unit_section:
            # Find the position after "name": "UnitName",
            name_match = re.search(r'"name":\s*"([^"]*)",', unit_section)
            if name_match:
                name_end = name_match.end()
                # Insert unit_id after the name
                changes_made += 1
                unit_name = name_match.group(1).lower().replace(' ', '_')
                unit_id = f'unit_{unit_counter}'
                unit_counter += 1
                
                new_unit_section = (unit_section[:name_end] + 
                                  f'\n                                "unit_id": "{unit_id}",' +
                                  unit_section[name_end:])
                return new_unit_section
        
        return unit_section
    
    # Find all unit dictionaries
    unit_pattern = r'\{\s*"name":\s*"[^"]*"[^}]*"unit_type":[^}]*\}'
    content = re.sub(unit_pattern, add_unit_id, content, flags=re.DOTALL)
    
    # Also handle simpler unit patterns that might be missing unit_type too
    simple_unit_pattern = r'\{\s*"name":\s*"[^"]*",\s*"[^}]*"health"[^}]*\}'
    
    def add_unit_id_simple(match):
        nonlocal changes_made, unit_counter
        unit_section = match.group(0)
        
        # Check if unit_id is already present
        if '"unit_id"' not in unit_section:
            # Find the position after "name": "UnitName",
            name_match = re.search(r'"name":\s*"([^"]*)",', unit_section)
            if name_match:
                name_end = name_match.end()
                # Insert unit_id after the name
                changes_made += 1
                unit_name = name_match.group(1).lower().replace(' ', '_')
                unit_id = f'unit_{unit_counter}'
                unit_counter += 1
                
                new_unit_section = (unit_section[:name_end] + 
                                  f'\n                                "unit_id": "{unit_id}",' +
                                  unit_section[name_end:])
                return new_unit_section
        
        return unit_section
    
    content = re.sub(simple_unit_pattern, add_unit_id_simple, content, flags=re.DOTALL)
    
    # Only write if changes were made
    if changes_made > 0 and content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed {changes_made} missing unit_id in {file_path}")
        return True
    
    return False


def main():
    """Fix unit_id in all test files."""
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
                if fix_unit_ids_in_file(file_path):
                    total_files_fixed += 1
    
    print(f"\nFixed unit_id issues in {total_files_fixed} files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())