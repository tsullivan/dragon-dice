#!/usr/bin/env python3
"""
Species model snapshot tests.

This module tests that species data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from models.species_model import ALL_SPECIES, get_all_species_names


@pytest.mark.unit
class TestSpeciesSnapshots:
    """Test class for species model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_species_data(self) -> Dict[str, Any]:
        """Serialize all species data to JSON-compatible format."""
        return {species_name: species.to_dict() for species_name, species in ALL_SPECIES.items()}

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

    def test_species_snapshot(self):
        """Test that species data matches snapshot."""
        current_data = self._serialize_species_data()
        snapshot_file = "species_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Species snapshot created: {len(current_data)} species")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if species data has changed
        assert current_normalized == existing_data, (
            "Species data has changed! "
            f"Expected {len(existing_data)} species, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Validate counts
        expected_species_count = len(get_all_species_names())
        assert len(current_data) == expected_species_count
        print(f"✓ Species snapshot validated: {len(current_data)} species")

    def test_species_data_integrity(self):
        """Test species data integrity."""
        species_data = self._serialize_species_data()

        # Validate minimum expected counts
        assert len(species_data) >= 10, "Should have at least 10 species"

        # Validate each species has required fields
        for species_name, species in species_data.items():
            assert "name" in species, f"Species {species_name} missing name field"
            assert "display_name" in species, f"Species {species_name} missing display_name field"
            assert "elements" in species, f"Species {species_name} missing elements field"
            assert isinstance(species["elements"], list), f"Species {species_name} elements should be a list"

        print(f"✓ Species data integrity validated: {len(species_data)} species")

    def test_generate_species_snapshot(self):
        """Generate species snapshot file."""
        species_data = self._serialize_species_data()
        self._write_snapshot("species_data.json", species_data)
        print(f"✓ Species snapshot generated: {len(species_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestSpeciesSnapshots()
    test_instance.test_generate_species_snapshot()
    test_instance.test_species_data_integrity()
    print("🎉 Species snapshot tests complete!")
