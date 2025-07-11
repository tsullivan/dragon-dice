#!/usr/bin/env python3
"""
Spells model snapshot tests.

This module tests that spell data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from models.spell_model import ALL_SPELLS, get_all_spell_names


@pytest.mark.unit
class TestSpellSnapshots:
    """Test class for spell model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_spell_data(self) -> Dict[str, Any]:
        """Serialize all spell data to JSON-compatible format."""
        return {spell_name: spell.to_dict() for spell_name, spell in ALL_SPELLS.items()}

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

    def test_spell_snapshot(self):
        """Test that spell data matches snapshot."""
        current_data = self._serialize_spell_data()
        snapshot_file = "spell_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Spell snapshot created: {len(current_data)} spells")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if spell data has changed
        assert current_normalized == existing_data, (
            "Spell data has changed! "
            f"Expected {len(existing_data)} spells, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Validate counts
        expected_spell_count = len(get_all_spell_names())
        assert len(current_data) == expected_spell_count
        print(f"✓ Spell snapshot validated: {len(current_data)} spells")

    def test_spell_data_integrity(self):
        """Test spell data integrity."""
        spell_data = self._serialize_spell_data()

        # Validate minimum expected counts
        assert len(spell_data) >= 30, "Should have at least 30 spells"

        # Validate each spell has required fields
        for spell_name, spell in spell_data.items():
            assert "name" in spell, f"Spell {spell_name} missing name field"
            assert "cost" in spell, f"Spell {spell_name} missing cost field"
            assert "element" in spell, f"Spell {spell_name} missing element field"
            assert "effect" in spell, f"Spell {spell_name} missing effect field"
            assert "species" in spell, f"Spell {spell_name} missing species field"
            assert isinstance(spell["cost"], int), f"Spell {spell_name} cost should be an integer"

        print(f"✓ Spell data integrity validated: {len(spell_data)} spells")

    def test_generate_spell_snapshot(self):
        """Generate spell snapshot file."""
        spell_data = self._serialize_spell_data()
        self._write_snapshot("spell_data.json", spell_data)
        print(f"✓ Spell snapshot generated: {len(spell_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestSpellSnapshots()
    test_instance.test_generate_spell_snapshot()
    test_instance.test_spell_data_integrity()
    print("🎉 Spell snapshot tests complete!")
