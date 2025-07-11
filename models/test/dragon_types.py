#!/usr/bin/env python3
"""
Dragon types model snapshot tests.

This module tests that dragon type data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from models.dragon_model import DRAGON_TYPE_DATA, get_all_dragon_type_names


@pytest.mark.unit
class TestDragonTypeSnapshots:
    """Test class for dragon type model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_dragon_type_data(self) -> Dict[str, Any]:
        """Serialize dragon type data to JSON-compatible format."""
        dragon_types = {}
        for type_name, dragon_type in DRAGON_TYPE_DATA.items():
            dragon_types[type_name] = {
                "name": dragon_type.name,
                "dragon_type": dragon_type.dragon_type,
                "elements": dragon_type.elements,
                "is_white": dragon_type.is_white,
                "display_name": dragon_type.get_display_name(),
                "description": dragon_type.get_description(),
                "health": dragon_type.get_health(),
                "force_value": dragon_type.get_force_value(),
                "has_doubled_damage": dragon_type.has_doubled_damage(),
                "has_doubled_treasure": dragon_type.has_doubled_treasure(),
                "can_summon_from_terrain": dragon_type.can_summon_from_terrain(),
            }
        return dragon_types

    def _write_snapshot(self, filename: str, data: Dict[str, Any]) -> None:
        """Write snapshot data to a JSON file."""
        self.snapshots_dir.mkdir(exist_ok=True)
        filepath = self.snapshots_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)

    def _read_snapshot(self, filename: str) -> Dict[str, Any]:
        """Read snapshot data from a JSON file."""
        filepath = self.snapshots_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)

    def test_dragon_type_snapshot(self):
        """Test that dragon type data matches snapshot."""
        current_data = self._serialize_dragon_type_data()
        snapshot_file = "dragon_type_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Dragon type snapshot created: {len(current_data)} dragon types")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if dragon type data has changed
        assert current_normalized == existing_data, (
            "Dragon type data has changed! "
            f"Expected {len(existing_data)} dragon types, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Validate counts
        expected_dragon_type_count = len(get_all_dragon_type_names())
        assert len(current_data) == expected_dragon_type_count
        print(f"✓ Dragon type snapshot validated: {len(current_data)} dragon types")

    def test_dragon_type_data_integrity(self):
        """Test dragon type data integrity."""
        dragon_type_data = self._serialize_dragon_type_data()

        # Validate minimum expected counts
        assert len(dragon_type_data) >= 25, "Should have at least 25 dragon types"

        # Validate each dragon type has required fields
        for type_name, dragon_type in dragon_type_data.items():
            assert "name" in dragon_type, f"Dragon type {type_name} missing name field"
            assert "dragon_type" in dragon_type, f"Dragon type {type_name} missing dragon_type field"
            assert "elements" in dragon_type, f"Dragon type {type_name} missing elements field"
            assert "display_name" in dragon_type, f"Dragon type {type_name} missing display_name field"
            assert "description" in dragon_type, f"Dragon type {type_name} missing description field"
            assert "health" in dragon_type, f"Dragon type {type_name} missing health field"
            assert "force_value" in dragon_type, f"Dragon type {type_name} missing force_value field"
            assert isinstance(dragon_type["elements"], list), f"Dragon type {type_name} elements should be a list"
            assert isinstance(dragon_type["health"], int), f"Dragon type {type_name} health should be an integer"
            assert isinstance(dragon_type["force_value"], int), (
                f"Dragon type {type_name} force_value should be an integer"
            )
            assert dragon_type["health"] in [5, 10], (
                f"Dragon type {type_name} health should be 5 or 10, got {dragon_type['health']}"
            )
            assert dragon_type["force_value"] in [1, 2], (
                f"Dragon type {type_name} force_value should be 1 or 2, got {dragon_type['force_value']}"
            )

        print(f"✓ Dragon type data integrity validated: {len(dragon_type_data)} dragon types")

    def test_generate_dragon_type_snapshot(self):
        """Generate dragon type snapshot file."""
        dragon_type_data = self._serialize_dragon_type_data()
        self._write_snapshot("dragon_type_data.json", dragon_type_data)
        print(f"✓ Dragon type snapshot generated: {len(dragon_type_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestDragonTypeSnapshots()
    test_instance.test_generate_dragon_type_snapshot()
    test_instance.test_dragon_type_data_integrity()
    print("🎉 Dragon type snapshot tests complete!")
