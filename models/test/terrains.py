#!/usr/bin/env python3
"""
Terrains model snapshot tests.

This module tests that terrain data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from models.terrain_model import TERRAIN_DATA, get_all_terrain_names


@pytest.mark.unit
class TestTerrainSnapshots:
    """Test class for terrain model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_terrain_data(self) -> Dict[str, Any]:
        """Serialize terrain data to JSON-compatible format."""
        terrains = {}
        for terrain_name, terrain in TERRAIN_DATA.items():
            terrains[terrain_name] = {
                "name": terrain.name,
                "display_name": terrain.display_name,
                "terrain_type": terrain.terrain_type,
                "eighth_face": terrain.eighth_face,
                "elements": terrain.elements,
                "face_names": terrain.get_face_names(),
                "face_count": len(terrain.faces),
                "is_major_terrain": terrain.is_major_terrain(),
                "is_minor_terrain": terrain.is_minor_terrain(),
            }
        return terrains

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

    def test_terrain_snapshot(self):
        """Test that terrain data matches snapshot."""
        current_data = self._serialize_terrain_data()
        snapshot_file = "terrain_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Terrain snapshot created: {len(current_data)} terrains")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if terrain data has changed
        assert current_normalized == existing_data, (
            "Terrain data has changed! "
            f"Expected {len(existing_data)} terrains, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Validate counts
        expected_terrain_count = len(get_all_terrain_names())
        assert len(current_data) == expected_terrain_count
        print(f"✓ Terrain snapshot validated: {len(current_data)} terrains")

    def test_terrain_data_integrity(self):
        """Test terrain data integrity."""
        terrain_data = self._serialize_terrain_data()

        # Validate minimum expected counts
        assert len(terrain_data) >= 40, "Should have at least 40 terrains"

        # Validate each terrain has required fields
        for terrain_name, terrain in terrain_data.items():
            assert "name" in terrain, f"Terrain {terrain_name} missing name field"
            assert "display_name" in terrain, f"Terrain {terrain_name} missing display_name field"
            assert "terrain_type" in terrain, f"Terrain {terrain_name} missing terrain_type field"
            assert "color" in terrain, f"Terrain {terrain_name} missing color field"
            assert "elements" in terrain, f"Terrain {terrain_name} missing elements field"
            assert "face_names" in terrain, f"Terrain {terrain_name} missing face_names field"
            assert "face_count" in terrain, f"Terrain {terrain_name} missing face_count field"
            assert isinstance(terrain["elements"], list), f"Terrain {terrain_name} elements should be a list"
            assert isinstance(terrain["face_names"], list), f"Terrain {terrain_name} face_names should be a list"
            assert terrain["face_count"] == 8, (
                f"Terrain {terrain_name} should have 8 faces, got {terrain['face_count']}"
            )
            assert len(terrain["face_names"]) == 8, (
                f"Terrain {terrain_name} should have 8 face names, got {len(terrain['face_names'])}"
            )

        print(f"✓ Terrain data integrity validated: {len(terrain_data)} terrains")

    def test_generate_terrain_snapshot(self):
        """Generate terrain snapshot file."""
        terrain_data = self._serialize_terrain_data()
        self._write_snapshot("terrain_data.json", terrain_data)
        print(f"✓ Terrain snapshot generated: {len(terrain_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestTerrainSnapshots()
    test_instance.test_generate_terrain_snapshot()
    test_instance.test_terrain_data_integrity()
    print("🎉 Terrain snapshot tests complete!")
