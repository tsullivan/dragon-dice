#!/usr/bin/env python3
"""
Script to fix misplaced unit_id fields in test_comprehensive_game_flows.py
"""

import re


def fix_comprehensive_game_flows():
    """Fix the specific issues in test_comprehensive_game_flows.py"""
    
    file_path = "test/e2e/test_comprehensive_game_flows.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove misplaced unit_id from army definitions
    # Pattern: army definitions that have unit_id where they shouldn't
    army_patterns = [
        r'("name": "[^"]*",)\s*"unit_id": "[^"]*",\s*("army_type": "[^"]*",)',
        r'("name": "[^"]*",)\s*"unit_id": "[^"]*",\s*("location": "[^"]*",)',
    ]
    
    for pattern in army_patterns:
        content = re.sub(pattern, r'\1\n            \2', content)
    
    # Add missing unit_id to units that don't have it
    def add_unit_id_to_unit(match):
        unit_section = match.group(0)
        if '"unit_id"' not in unit_section:
            # Extract unit name for generating ID
            name_match = re.search(r'"name":\s*"([^"]*)"', unit_section)
            if name_match:
                unit_name = name_match.group(1).lower().replace(' ', '_')
                # Find where to insert unit_id (after name)
                name_end = name_match.end()
                comma_pos = unit_section.find(',', name_end)
                if comma_pos != -1:
                    new_unit_section = (
                        unit_section[:comma_pos+1] + 
                        f'\n                                "unit_id": "{unit_name}_id",' +
                        unit_section[comma_pos+1:]
                    )
                    return new_unit_section
        return unit_section
    
    # Pattern for units within unit arrays
    unit_pattern = r'\{\s*"name":\s*"[^"]*"[^}]*\}'
    content = re.sub(unit_pattern, add_unit_id_to_unit, content, flags=re.DOTALL)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed test_comprehensive_game_flows.py")


if __name__ == "__main__":
    fix_comprehensive_game_flows()