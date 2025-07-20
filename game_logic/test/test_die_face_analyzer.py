"""
Unit tests for die face analysis logic.

Tests the extracted business logic for analyzing die faces from Dragon Dice
units to ensure analysis is correctly performed independently of UI components.
"""

import unittest
from unittest.mock import Mock

import constants
from models.die_face_analyzer import (
    DieFaceAnalyzer,
    DieFaceCount,
    UnitDieFaceExtractor,
)
from models.die_face_model import DieFaceModel
from models.test.mock.typed_models import create_test_unit


class TestDieFaceCount(unittest.TestCase):
    """Test the DieFaceCount dataclass."""

    def test_creation_with_icon(self):
        """Test creating DieFaceCount with explicit icon."""
        face_count = DieFaceCount(face_type="Melee", count=3, icon="⚔️")

        assert face_count.face_type == "Melee"
        assert face_count.count == 3
        assert face_count.icon == "⚔️"

    def test_creation_with_auto_icon(self):
        """Test creating DieFaceCount with automatic icon assignment."""
        face_count = DieFaceCount(face_type="Missile", count=2)

        assert face_count.face_type == "Missile"
        assert face_count.count == 2
        assert face_count.icon == "🏹"  # Should auto-assign missile icon


class TestDieFaceAnalyzer(unittest.TestCase):
    """Test the main die face analyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock unit roster
        self.mock_unit_roster = Mock()

        # Create test unit definitions with die faces
        self.melee_unit_def = {
            "die_faces": {
                "face_1": "Melee",
                "face_2": "Melee",
                "face_3": "Save",
                "face_4": "ID",
                "face_5": "Maneuver",
                "face_6": "SAI",
                "eighth_face_1": "Melee",
                "eighth_face_2": "Save",
            }
        }

        self.missile_unit_def = {
            "die_faces": {
                "face_1": "Missile",
                "face_2": "Missile",
                "face_3": "Missile",
                "face_4": "Save",
                "face_5": "ID",
                "face_6": "Maneuver",
                "eighth_face_1": "Missile",
                "eighth_face_2": "Save",
            }
        }

        def mock_get_unit_definition(unit_type):
            if unit_type == "melee_unit":
                return self.melee_unit_def
            if unit_type == "missile_unit":
                return self.missile_unit_def
            return None

        self.mock_unit_roster.get_unit_definition.side_effect = mock_get_unit_definition

        self.analyzer = DieFaceAnalyzer(self.mock_unit_roster)

        # Create typed test units
        self.melee_unit = create_test_unit(
            unit_id="melee_unit_1", name="Melee Test Unit", unit_type="melee_unit", health=2, max_health=2
        )

        self.missile_unit = create_test_unit(
            unit_id="missile_unit_1", name="Missile Test Unit", unit_type="missile_unit", health=1, max_health=1
        )

        # Dict-style units for mixed testing
        self.dict_melee_unit = {"unit_type": "melee_unit"}
        self.dict_missile_unit = {"unit_type": "missile_unit"}

    def test_count_die_faces_single_unit(self):
        """Test counting die faces for a single unit."""
        units = [self.melee_unit]

        face_counts = self.analyzer.count_die_faces(units)

        # Expected: 3 melee (2 standard + 1 eighth), 2 save (1 standard + 1 eighth), 1 maneuver, 1 SAI
        # ID faces should be excluded
        expected = {
            "Melee": 3,
            "Save": 2,
            "Maneuver": 1,
            "SAI": 1,
        }

        assert face_counts == expected

    def test_count_die_faces_multiple_units(self):
        """Test counting die faces for multiple units."""
        units = [self.melee_unit, self.missile_unit]

        face_counts = self.analyzer.count_die_faces(units)

        # Melee unit: 3 melee, 2 save, 1 maneuver, 1 SAI
        # Missile unit: 4 missile, 2 save, 1 maneuver
        expected = {
            "Melee": 3,
            "Missile": 4,
            "Save": 4,  # 2 + 2
            "Maneuver": 2,  # 1 + 1
            "SAI": 1,
        }

        assert face_counts == expected

    def test_count_die_faces_with_dict_units(self):
        """Test counting die faces with dictionary-style units."""
        units = [self.dict_melee_unit]

        face_counts = self.analyzer.count_die_faces(units)

        expected = {
            "Melee": 3,
            "Save": 2,
            "Maneuver": 1,
            "SAI": 1,
        }

        assert face_counts == expected

    def test_count_die_faces_no_units(self):
        """Test counting die faces with no units."""
        face_counts = self.analyzer.count_die_faces([])
        assert face_counts == {}

    def test_count_die_faces_no_roster(self):
        """Test counting die faces without unit roster."""
        analyzer = DieFaceAnalyzer(None)
        face_counts = analyzer.count_die_faces([self.melee_unit])
        assert face_counts == {}

    def test_count_die_faces_unit_not_found(self):
        """Test counting die faces for unit not in roster."""
        unknown_unit = Mock()
        unknown_unit.unit_type = "unknown_unit"

        face_counts = self.analyzer.count_die_faces([unknown_unit])
        assert face_counts == {}

    def test_get_sorted_face_counts(self):
        """Test sorting face counts by priority and count."""
        face_counts = {
            "SAI": 1,
            "Melee": 3,
            "Save": 2,
            "Missile": 3,
        }

        sorted_faces = self.analyzer.get_sorted_face_counts(face_counts)

        # Should be sorted by priority order first, then by count (descending)
        # Priority: MELEE, MISSILE, MAGIC, SAVE, MANEUVER, SAI
        expected_order = [
            ("Melee", 3),
            ("Missile", 3),
            ("Save", 2),
            ("SAI", 1),
        ]

        for i, (face_type, count) in enumerate(expected_order):
            assert sorted_faces[i].face_type == face_type
            assert sorted_faces[i].count == count

    def test_analyze_unit_die_faces(self):
        """Test complete analysis of unit die faces."""
        units = [self.melee_unit]

        sorted_faces = self.analyzer.analyze_unit_die_faces(units)

        # Should return sorted DieFaceCount objects
        assert len(sorted_faces) == 4
        assert sorted_faces[0].face_type == "Melee"
        assert sorted_faces[0].count == 3
        assert sorted_faces[0].icon == "⚔️"

    def test_get_face_distribution_summary(self):
        """Test comprehensive face distribution summary."""
        units = [self.melee_unit]

        summary = self.analyzer.get_face_distribution_summary(units)

        assert summary["total_faces"] == 7  # 3 melee + 2 save + 1 maneuver + 1 SAI
        assert summary["unique_face_types"] == 4
        assert "face_counts" in summary
        assert "sorted_faces" in summary
        assert "percentages" in summary
        assert summary["most_common"] is not None
        assert summary["least_common"] is not None

        # Check percentages
        expected_melee_percentage = round((3 / 7) * 100, 1)  # ~42.9%
        assert summary["percentages"]["Melee"] == expected_melee_percentage

    def test_compare_army_compositions(self):
        """Test comparison between two army compositions."""
        army1_units = [self.melee_unit]  # 3 melee, 2 save, 1 maneuver, 1 SAI
        army2_units = [self.missile_unit]  # 4 missile, 2 save, 1 maneuver

        comparison = self.analyzer.compare_army_compositions(army1_units, army2_units)

        assert comparison["army1_total"] == 7
        assert comparison["army2_total"] == 7

        # Check differences
        assert comparison["face_differences"]["Melee"]["difference"] == 3  # Army1 has 3 more melee
        assert comparison["face_differences"]["Missile"]["difference"] == -4  # Army1 has 4 fewer missile
        assert comparison["face_differences"]["Save"]["difference"] == 0  # Equal saves

        # Check advantages
        assert ("Melee", 3) in comparison["army1_advantages"]
        assert ("Missile", 4) in comparison["army2_advantages"]
        assert "Save" in comparison["equal_faces"]

    def test_get_tactical_analysis(self):
        """Test tactical analysis of unit composition."""
        units = [self.melee_unit]  # 3 melee, 2 save, 1 maneuver, 1 SAI

        analysis = self.analyzer.get_tactical_analysis(units)

        assert analysis["offensive_strength"] == 3  # 3 melee
        assert analysis["defensive_strength"] == 2  # 2 save
        assert analysis["utility_strength"] == 2  # 1 maneuver + 1 SAI
        assert analysis["total_combat_faces"] == 5  # 3 melee + 2 save
        assert analysis["primary_strength"] == "offensive"

        # With only 3/7 offensive faces, this should not have major weaknesses
        assert isinstance(analysis["weaknesses"], list)
        assert isinstance(analysis["balanced"], bool)

    def test_get_icon_for_face_type(self):
        """Test icon retrieval for face types."""
        assert DieFaceAnalyzer.get_icon_for_face_type("Melee") == "⚔️"
        assert DieFaceAnalyzer.get_icon_for_face_type("Missile") == "🏹"
        assert DieFaceAnalyzer.get_icon_for_face_type("Save") == "🛡️"

    def test_format_face_summary_compact(self):
        """Test compact face summary formatting."""
        face_counts = {
            "Melee": 3,
            "Save": 2,
            "Missile": 1,
        }

        summary = self.analyzer.format_face_summary(face_counts, compact=True)

        # Should be in priority order: melee, missile, save
        assert summary == "⚔️3 🏹1 🛡️2"

    def test_format_face_summary_detailed(self):
        """Test detailed face summary formatting."""
        face_counts = {"Melee": 3, "Save": 2}

        summary = self.analyzer.format_face_summary(face_counts, compact=False)

        assert summary == "Melee: 3, Save: 2"

    def test_format_face_summary_empty(self):
        """Test formatting empty face summary."""
        summary = self.analyzer.format_face_summary({})
        assert summary == "No die faces"


class TestUnitDieFaceExtractor(unittest.TestCase):
    """Test the UnitDieFaceExtractor utility class."""

    def test_extract_from_unit_definition(self):
        """Test extracting die faces from unit definition."""
        unit_def = {
            "die_faces": {
                "face_1": "Melee",
                "face_2": "Save",
                "face_3": "ID",
                "face_4": "Missile",
                "face_5": "Maneuver",
                "face_6": "SAI",
                "eighth_face_1": "Melee",
                "eighth_face_2": "Magic",
                "extra_field": "ignored",  # Should be ignored
            }
        }

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        expected = {
            "face_1": "Melee",
            "face_2": "Save",
            "face_3": "ID",
            "face_4": "Missile",
            "face_5": "Maneuver",
            "face_6": "SAI",
            "eighth_face_1": "Melee",
            "eighth_face_2": "Magic",
        }

        assert extracted == expected

    def test_extract_from_unit_definition_no_die_faces(self):
        """Test extracting from unit definition without die_faces."""
        unit_def = {"other_field": "value"}

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        assert extracted == {}

    def test_extract_from_unit_definition_partial(self):
        """Test extracting from unit definition with partial die_faces."""
        unit_def = {
            "die_faces": {
                "face_1": "Melee",
                "face_3": "Save",
                "eighth_face_1": "Missile",
            }
        }

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        expected = {
            "face_1": "Melee",
            "face_3": "Save",
            "eighth_face_1": "Missile",
        }

        assert extracted == expected

    def test_validate_face_structure_valid(self):
        """Test validation of valid face structure."""
        die_faces = {
            "face_1": "Melee",
            "face_2": "Missile",
            "face_3": "Magic",
            "face_4": "Save",
            "face_5": "ID",
            "face_6": "Maneuver",
            "eighth_face_1": "SAI",
            "eighth_face_2": "Melee",
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        assert is_valid
        assert len(errors) == 0

    def test_validate_face_structure_missing_faces(self):
        """Test validation of face structure with missing required faces."""
        die_faces = {
            "face_1": "Melee",
            "face_2": "Save",
            # Missing face_3 through face_6
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        assert not is_valid
        assert len(errors) == 4  # Missing face_3, face_4, face_5, face_6
        assert "Missing required face position: face_3" in errors

    def test_validate_face_structure_invalid_face_types(self):
        """Test validation of face structure with invalid face types."""
        die_faces = {
            "face_1": "Melee",
            "face_2": "INVALID_FACE",
            "face_3": "Save",
            "face_4": "ANOTHER_INVALID",
            "face_5": "ID",
            "face_6": "Maneuver",
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        assert not is_valid
        assert len(errors) == 2  # Two invalid face types
        assert any("Invalid face type 'INVALID_FACE'" in error for error in errors)
        assert any("Invalid face type 'ANOTHER_INVALID'" in error for error in errors)


if __name__ == "__main__":
    unittest.main()
