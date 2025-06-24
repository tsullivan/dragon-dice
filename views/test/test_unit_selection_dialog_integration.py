#!/usr/bin/env python3
"""
Quick test to verify unit sorting in the selection dialog
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.unit_roster_model import UnitRosterModel
from views.unit_selection_dialog import UnitSelectionDialog


def test_unit_sorting():
    unit_roster = UnitRosterModel()
    units_by_species = unit_roster.get_available_unit_types_by_species()

    # Create a dialog instance to test the sorting method
    dialog = UnitSelectionDialog("Test Army", unit_roster)

    # Test sorting for Amazon species (has many units with different health/types)
    if "Amazon" in units_by_species:
        amazon_units = units_by_species["Amazon"]
        print(f"Found {len(amazon_units)} Amazon units")

        # Use the dialog's sorting method
        sorted_units = dialog._sort_units_for_display(amazon_units)

        print("\nSorted Amazon units (Health ASC, Class ASC, Name ASC):")
        for i, unit in enumerate(sorted_units):
            health = unit.get("max_health", 0)
            class_type = unit.get("unit_class_type", "N/A")
            name = unit.get("display_name", "")
            print(f"{i+1:2d}. {name:<20} | {class_type:<12} | {health} HP")

        # Verify sorting is correct
        for i in range(len(sorted_units) - 1):
            current = sorted_units[i]
            next_unit = sorted_units[i + 1]

            current_health = current.get("max_health", 0)
            next_health = next_unit.get("max_health", 0)

            # Health should be ascending (current <= next)
            assert (
                current_health <= next_health
            ), f"Health sorting violation at position {i}: {current_health} > {next_health}"

            # If health is the same, check class type
            if current_health == next_health:
                current_class = current.get("unit_class_type", "N/A")
                next_class = next_unit.get("unit_class_type", "N/A")

                # Class type should be ascending (current <= next)
                assert (
                    current_class <= next_class
                ), f"Class type sorting violation at position {i}: {current_class} > {next_class}"

                # If class type is the same, check name
                if current_class == next_class:
                    current_name = current.get("display_name", "")
                    next_name = next_unit.get("display_name", "")

                    # Name should be ascending (current <= next)
                    assert (
                        current_name <= next_name
                    ), f"Name sorting violation at position {i}: {current_name} > {next_name}"

        print("\n✓ Sorting verification passed!")
    else:
        assert False, "Amazon species not found in unit roster"


if __name__ == "__main__":
    test_unit_sorting()
