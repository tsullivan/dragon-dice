#!/usr/bin/env python3
"""
Die faces model snapshot tests.

This module tests that die face data hasn't changed unexpectedly by comparing against reference snapshots.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from models.die_face_model import (
    ALL_DIE_FACES,
    DRAGON_DIE_FACES,
    ID_FACES,
    MAGIC_FACES,
    MELEE_FACES,
    MISSILE_FACES,
    MOVE_FACES,
    SAVE_FACES,
    get_die_face,
    get_faces_by_type,
)


@pytest.mark.unit
class TestDieFaceSnapshots:
    """Test class for die face model snapshots."""

    @property
    def snapshots_dir(self) -> Path:
        """Get the directory for storing snapshot files."""
        return Path(__file__).parent / "snapshots"

    def _serialize_die_face_data(self) -> Dict[str, Any]:
        """Serialize die face data to JSON-compatible format."""
        die_faces = {}
        for face_name, face in ALL_DIE_FACES.items():
            die_faces[face_name] = face.to_dict()
        return die_faces

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

    def test_die_face_snapshot(self):
        """Test that die face data matches snapshot."""
        current_data = self._serialize_die_face_data()
        snapshot_file = "die_face_data.json"

        # Read existing snapshot for comparison
        existing_data = self._read_snapshot(snapshot_file)

        # If no existing snapshot, create it and pass the test
        if not existing_data:
            self._write_snapshot(snapshot_file, current_data)
            print(f"✓ Die face snapshot created: {len(current_data)} die faces")
            return

        # Normalize both datasets (JSON converts tuples to lists)
        current_normalized = json.loads(json.dumps(current_data))

        # Compare data - this will fail if die face data has changed
        assert current_normalized == existing_data, (
            "Die face data has changed! "
            f"Expected {len(existing_data)} die faces, got {len(current_data)}. "
            f"If this change is intentional, delete the snapshot file at: "
            f"{self.snapshots_dir / snapshot_file} and re-run the test."
        )

        print(f"✓ Die face snapshot validated: {len(current_data)} die faces")

    def test_die_face_data_integrity(self):
        """Test die face data integrity."""
        die_face_data = self._serialize_die_face_data()

        # Validate minimum expected counts
        assert len(die_face_data) >= 50, "Should have at least 50 die faces"

        # Validate each die face has required fields
        for face_name, face in die_face_data.items():
            assert "name" in face, f"Die face {face_name} missing name field"
            assert "display_name" in face, f"Die face {face_name} missing display_name field"
            assert "description" in face, f"Die face {face_name} missing description field"
            assert "face_type" in face, f"Die face {face_name} missing face_type field"
            assert "base_value" in face, f"Die face {face_name} missing base_value field"
            assert isinstance(face["base_value"], int), f"Die face {face_name} base_value should be an integer"
            assert face["base_value"] >= 0, f"Die face {face_name} base_value should be non-negative"

        # Validate specific face type counts
        id_faces = [face for face in die_face_data.values() if face["face_type"] == "ID"]
        assert len(id_faces) >= 4, "Should have at least 4 ID faces"

        melee_faces = [face for face in die_face_data.values() if face["face_type"] == "MELEE"]
        assert len(melee_faces) >= 6, "Should have at least 6 melee faces"

        missile_faces = [face for face in die_face_data.values() if face["face_type"] == "MISSILE"]
        assert len(missile_faces) >= 6, "Should have at least 6 missile faces"

        move_faces = [face for face in die_face_data.values() if face["face_type"] == "MOVE"]
        assert len(move_faces) >= 5, "Should have at least 5 move faces"

        save_faces = [face for face in die_face_data.values() if face["face_type"] == "SAVE"]
        assert len(save_faces) >= 4, "Should have at least 4 save faces"

        magic_faces = [face for face in die_face_data.values() if face["face_type"] == "MAGIC"]
        assert len(magic_faces) >= 6, "Should have at least 6 magic faces"

        dragon_faces = [
            face
            for face in die_face_data.values()
            if face["face_type"] in ["DRAGON_ATTACK", "DRAGON_SPECIAL", "DRAGON_VULNERABLE"]
        ]
        assert len(dragon_faces) >= 12, "Should have at least 12 dragon faces"

        print(f"✓ Die face data integrity validated: {len(die_face_data)} die faces")

    def test_die_face_collections(self):
        """Test that die face collections are properly organized."""
        # Test that basic face collections exist and have expected sizes
        assert len(ID_FACES) >= 4, "ID_FACES should have at least 4 faces"
        assert len(MELEE_FACES) >= 6, "MELEE_FACES should have at least 6 faces"
        assert len(MISSILE_FACES) >= 6, "MISSILE_FACES should have at least 6 faces"
        assert len(MOVE_FACES) >= 5, "MOVE_FACES should have at least 5 faces"
        assert len(SAVE_FACES) >= 4, "SAVE_FACES should have at least 4 faces"
        assert len(MAGIC_FACES) >= 6, "MAGIC_FACES should have at least 6 faces"
        assert len(DRAGON_DIE_FACES) >= 12, "DRAGON_DIE_FACES should have at least 12 faces"

        # Test that helper functions work
        test_face = get_die_face("ID_1")
        assert test_face is not None, "get_die_face should return a face for valid name"
        assert test_face.name == "ID_1", "get_die_face should return correct face"

        id_faces_by_type = get_faces_by_type("ID")
        assert len(id_faces_by_type) >= 4, "get_faces_by_type should return ID faces"

        print("✓ Die face collections validated")

    def test_dragon_die_faces_integrity(self):
        """Test dragon die faces specifically."""
        # Validate dragon-specific faces
        dragon_faces = [
            "Jaws",
            "Dragon_Breath",
            "Claw_Front_Left",
            "Claw_Front_Right",
            "Wing_Left",
            "Wing_Right",
            "Belly_Front",
            "Belly_Rear",
            "Claw_Rear_Left",
            "Claw_Rear_Right",
            "Tail_Front",
            "Tail_Tip",
            "Tail_Middle",
            "Treasure",
        ]

        for face_name in dragon_faces:
            face = get_die_face(face_name)
            assert face is not None, f"Dragon face {face_name} should exist"
            assert face.face_type in ["DRAGON_ATTACK", "DRAGON_SPECIAL", "DRAGON_VULNERABLE"], (
                f"Dragon face {face_name} should have dragon face type"
            )
            assert face.description, f"Dragon face {face_name} should have description"

        print("✓ Dragon die faces integrity validated")

    def test_generate_die_face_snapshot(self):
        """Generate die face snapshot file."""
        die_face_data = self._serialize_die_face_data()
        self._write_snapshot("die_face_data.json", die_face_data)
        print(f"✓ Die face snapshot generated: {len(die_face_data)} entries")


if __name__ == "__main__":
    # Run the snapshot generation manually
    test_instance = TestDieFaceSnapshots()
    test_instance.test_generate_die_face_snapshot()
    test_instance.test_die_face_data_integrity()
    test_instance.test_die_face_collections()
    test_instance.test_dragon_die_faces_integrity()
    print("🎉 Die face snapshot tests complete!")
