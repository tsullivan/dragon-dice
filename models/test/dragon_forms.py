#!/usr/bin/env python3
"""
Dragon forms model snapshot tests.

This module tests that dragon form data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from models.dragon_model import DRAGON_FORM_DATA, get_all_dragon_names


@pytest.mark.unit
class TestDragonFormSnapshots:
    """Test class for dragon form model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_dragon_form_data(self) -> Dict[str, Any]:
        """Serialize dragon form data to JSON-compatible format."""
        dragon_forms = {}
        for form_name, dragon in DRAGON_FORM_DATA.items():
            dragon_forms[form_name] = {
                "display_name": dragon.display_name,
                "name": dragon.name,
                "face_names": dragon.get_face_names(),
                "face_count": len(dragon.faces),
            }
        return dragon_forms

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
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_dragon_form_snapshot(self):
        """Test that dragon form data matches snapshot."""
        current_data = self._serialize_dragon_form_data()
        snapshot_file = "dragon_form_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Dragon form snapshot created: {len(current_data)} dragon forms")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if dragon form data has changed
        assert current_normalized == existing_data, (
            "Dragon form data has changed! "
            f"Expected {len(existing_data)} dragon forms, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Validate counts
        expected_dragon_count = len(get_all_dragon_names())
        assert len(current_data) == expected_dragon_count
        print(f"✓ Dragon form snapshot validated: {len(current_data)} dragon forms")

    def test_dragon_form_data_integrity(self):
        """Test dragon form data integrity."""
        dragon_form_data = self._serialize_dragon_form_data()

        # Validate minimum expected counts
        assert len(dragon_form_data) >= 2, "Should have at least 2 dragon forms (Drake, Wyrm)"

        # Validate each dragon form has required fields
        for form_name, form in dragon_form_data.items():
            assert "display_name" in form, f"Dragon form {form_name} missing display_name field"
            assert "name" in form, f"Dragon form {form_name} missing name field"
            assert "face_names" in form, f"Dragon form {form_name} missing face_names field"
            assert "face_count" in form, f"Dragon form {form_name} missing face_count field"
            assert isinstance(form["face_names"], list), f"Dragon form {form_name} face_names should be a list"
            assert form["face_count"] == 12, f"Dragon form {form_name} should have 12 faces, got {form['face_count']}"
            assert len(form["face_names"]) == 12, (
                f"Dragon form {form_name} should have 12 face names, got {len(form['face_names'])}"
            )

        print(f"✓ Dragon form data integrity validated: {len(dragon_form_data)} dragon forms")

    def test_generate_dragon_form_snapshot(self):
        """Generate dragon form snapshot file."""
        dragon_form_data = self._serialize_dragon_form_data()
        self._write_snapshot("dragon_form_data.json", dragon_form_data)
        print(f"✓ Dragon form snapshot generated: {len(dragon_form_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestDragonFormSnapshots()
    test_instance.test_generate_dragon_form_snapshot()
    test_instance.test_dragon_form_data_integrity()
    print("🎉 Dragon form snapshot tests complete!")
