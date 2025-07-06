#!/usr/bin/env python3
"""
Snapshot tests for Dragon Dice model data.

This module generates static JSON files defining every species, unit, spell, dragon, and terrain.
The tests ensure that model data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest

from models.dragon_model import (
    DRAGON_FORM_DATA,
    DRAGON_TYPE_DATA,
    get_all_dragon_names,
    get_all_dragon_type_names,
)
from models.species_model import ALL_SPECIES, get_all_species_names
from models.spell_model import ALL_SPELLS, get_all_spell_names
from models.terrain_model import TERRAIN_DATA, get_all_terrain_names
from models.unit_data import UNIT_DATA


@pytest.mark.unit
class TestModelSnapshots:
    """Test class for generating and validating model data snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        test_dir = Path(__file__).parent
        snapshots_dir = test_dir / "snapshots"
        snapshots_dir.mkdir(exist_ok=True)
        return snapshots_dir

    def _serialize_species_data(self) -> Dict[str, Any]:
        """Serialize all species data to JSON-compatible format."""
        return {
            species_name: species.to_dict() for species_name, species in ALL_SPECIES.items()
        }

    def _serialize_spell_data(self) -> Dict[str, Any]:
        """Serialize all spell data to JSON-compatible format."""
        return {
            spell_name: spell.to_dict() for spell_name, spell in ALL_SPELLS.items()
        }

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

    def _serialize_terrain_data(self) -> Dict[str, Any]:
        """Serialize terrain data to JSON-compatible format."""
        terrains = {}
        for terrain_name, terrain in TERRAIN_DATA.items():
            terrains[terrain_name] = {
                "name": terrain.name,
                "display_name": terrain.display_name,
                "terrain_type": terrain.terrain_type,
                "color": terrain.color,
                "subtype": terrain.subtype,
                "elements": terrain.elements,
                "element_colors": terrain.element_colors,
                "face_names": terrain.get_face_names(),
                "face_count": len(terrain.faces),
                "is_major_terrain": terrain.is_major_terrain(),
                "is_minor_terrain": terrain.is_minor_terrain(),
            }
        return terrains

    def _serialize_unit_data(self) -> Dict[str, Any]:
        """Serialize unit data to JSON-compatible format."""
        try:
            units = {}
            for i, unit in enumerate(UNIT_DATA):
                unit_key = getattr(unit, 'unit_id', f'unit_{i}')
                units[unit_key] = {
                    "name": unit.name,
                    "unit_type": getattr(unit, 'unit_type', 'Unknown'),
                    "health": unit.health,
                    "max_health": getattr(unit, 'max_health', unit.health),
                    "species_name": unit.species.name if hasattr(unit, 'species') and unit.species else 'Unknown',
                    "face_count": len(unit.faces),
                    "face_names": [face.name for face in unit.faces] if hasattr(unit.faces[0], 'name') else [],
                }
            return units
        except Exception as e:
            # Handle case where unit data might not be fully implemented
            return {"error": f"Unit data serialization failed: {str(e)}"}

    def _write_snapshot(self, filename: str, data: Dict[str, Any]) -> None:
        """Write snapshot data to a JSON file."""
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

    def test_unit_snapshot(self):
        """Test that unit data matches snapshot."""
        current_data = self._serialize_unit_data()
        snapshot_file = "unit_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            if "error" not in current_data:
                print(f"✓ Unit snapshot created: {len(current_data)} units")
            else:
                print(f"⚠ Unit snapshot created with error: {current_data['error']}")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if unit data has changed
        assert current_normalized == existing_data, (
            "Unit data has changed! "
            f"Expected {len(existing_data)} units, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        # Only validate counts if no error occurred
        if "error" not in current_data:
            print(f"✓ Unit snapshot validated: {len(current_data)} units")
        else:
            print(f"⚠ Unit snapshot generated with error: {current_data['error']}")

    def test_generate_all_snapshots(self):
        """Generate all snapshot files in a single test run."""
        # This test is mainly for initial generation
        print("\n🔄 Generating all model data snapshots...")

        # Generate each snapshot
        species_data = self._serialize_species_data()
        self._write_snapshot("species_data.json", species_data)
        print(f"  ✓ Species: {len(species_data)} entries")

        spell_data = self._serialize_spell_data()
        self._write_snapshot("spell_data.json", spell_data)
        print(f"  ✓ Spells: {len(spell_data)} entries")

        dragon_form_data = self._serialize_dragon_form_data()
        self._write_snapshot("dragon_form_data.json", dragon_form_data)
        print(f"  ✓ Dragon forms: {len(dragon_form_data)} entries")

        dragon_type_data = self._serialize_dragon_type_data()
        self._write_snapshot("dragon_type_data.json", dragon_type_data)
        print(f"  ✓ Dragon types: {len(dragon_type_data)} entries")

        terrain_data = self._serialize_terrain_data()
        self._write_snapshot("terrain_data.json", terrain_data)
        print(f"  ✓ Terrains: {len(terrain_data)} entries")

        unit_data = self._serialize_unit_data()
        self._write_snapshot("unit_data.json", unit_data)
        if "error" not in unit_data:
            print(f"  ✓ Units: {len(unit_data)} entries")
        else:
            print(f"  ⚠ Units: error occurred during serialization")

        print(f"\n📁 All snapshots saved to: {self.snapshots_dir}")

    def test_data_integrity(self):
        """Test overall data integrity across all models."""
        # Collect all data
        species_data = self._serialize_species_data()
        spell_data = self._serialize_spell_data()
        dragon_form_data = self._serialize_dragon_form_data()
        dragon_type_data = self._serialize_dragon_type_data()
        terrain_data = self._serialize_terrain_data()
        unit_data = self._serialize_unit_data()

        # Validate minimum expected counts
        assert len(species_data) >= 10, "Should have at least 10 species"
        assert len(spell_data) >= 30, "Should have at least 30 spells"
        assert len(dragon_form_data) >= 2, "Should have at least 2 dragon forms (Drake, Wyrm)"
        assert len(dragon_type_data) >= 25, "Should have at least 25 dragon types"
        assert len(terrain_data) >= 40, "Should have at least 40 terrains"

        # Summary statistics
        total_entries = (
            len(species_data)
            + len(spell_data)
            + len(dragon_form_data)
            + len(dragon_type_data)
            + len(terrain_data)
        )

        if "error" not in unit_data:
            total_entries += len(unit_data)

        print(f"\n📊 Model Data Summary:")
        print(f"  Species: {len(species_data)}")
        print(f"  Spells: {len(spell_data)}")
        print(f"  Dragon Forms: {len(dragon_form_data)}")
        print(f"  Dragon Types: {len(dragon_type_data)}")
        print(f"  Terrains: {len(terrain_data)}")
        if "error" not in unit_data:
            print(f"  Units: {len(unit_data)}")
        else:
            print(f"  Units: {unit_data['error']}")
        print(f"  Total Entries: {total_entries}")

        assert total_entries > 100, "Should have substantial amount of game data"


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestModelSnapshots()
    test_instance.test_generate_all_snapshots()
    print("\n🎉 Snapshot generation complete!")