"""
Unit tests for die face analysis logic.

Tests the extracted business logic for analyzing die faces from Dragon Dice
units to ensure analysis is correctly performed independently of UI components.
"""

import unittest
from unittest.mock import Mock
from game_logic.die_face_analyzer import (
    DieFaceAnalyzer,
    DieFaceCount,
    UnitDieFaceExtractor,
)
import utils.constants as constants


class TestDieFaceCount(unittest.TestCase):
    """Test the DieFaceCount dataclass."""

    def test_creation_with_icon(self):
        """Test creating DieFaceCount with explicit icon."""
        face_count = DieFaceCount(face_type=constants.ICON_MELEE, count=3, icon="⚔️")

        self.assertEqual(face_count.face_type, constants.ICON_MELEE)
        self.assertEqual(face_count.count, 3)
        self.assertEqual(face_count.icon, "⚔️")

    def test_creation_with_auto_icon(self):
        """Test creating DieFaceCount with automatic icon assignment."""
        face_count = DieFaceCount(face_type=constants.ICON_MISSILE, count=2)

        self.assertEqual(face_count.face_type, constants.ICON_MISSILE)
        self.assertEqual(face_count.count, 2)
        self.assertEqual(face_count.icon, "🏹")  # Should auto-assign missile icon


class TestDieFaceAnalyzer(unittest.TestCase):
    """Test the main die face analyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock unit roster
        self.mock_unit_roster = Mock()

        # Create test unit definitions with die faces
        self.melee_unit_def = {
            "die_faces": {
                "face_1": constants.ICON_MELEE,
                "face_2": constants.ICON_MELEE,
                "face_3": constants.ICON_SAVE,
                "face_4": constants.ICON_ID,
                "face_5": constants.ICON_MANEUVER,
                "face_6": constants.ICON_SAI,
                "eighth_face_1": constants.ICON_MELEE,
                "eighth_face_2": constants.ICON_SAVE,
            }
        }

        self.missile_unit_def = {
            "die_faces": {
                "face_1": constants.ICON_MISSILE,
                "face_2": constants.ICON_MISSILE,
                "face_3": constants.ICON_MISSILE,
                "face_4": constants.ICON_SAVE,
                "face_5": constants.ICON_ID,
                "face_6": constants.ICON_MANEUVER,
                "eighth_face_1": constants.ICON_MISSILE,
                "eighth_face_2": constants.ICON_SAVE,
            }
        }

        def mock_get_unit_definition(unit_type):
            if unit_type == "melee_unit":
                return self.melee_unit_def
            elif unit_type == "missile_unit":
                return self.missile_unit_def
            return None

        self.mock_unit_roster.get_unit_definition.side_effect = mock_get_unit_definition

        self.analyzer = DieFaceAnalyzer(self.mock_unit_roster)

        # Create test units
        self.melee_unit = Mock()
        self.melee_unit.unit_type = "melee_unit"

        self.missile_unit = Mock()
        self.missile_unit.unit_type = "missile_unit"

        # Dict-style units
        self.dict_melee_unit = {"unit_type": "melee_unit"}
        self.dict_missile_unit = {"unit_type": "missile_unit"}

    def test_count_die_faces_single_unit(self):
        """Test counting die faces for a single unit."""
        units = [self.melee_unit]

        face_counts = self.analyzer.count_die_faces(units)

        # Expected: 3 melee (2 standard + 1 eighth), 2 save (1 standard + 1 eighth), 1 maneuver, 1 SAI
        # ID faces should be excluded
        expected = {
            constants.ICON_MELEE: 3,
            constants.ICON_SAVE: 2,
            constants.ICON_MANEUVER: 1,
            constants.ICON_SAI: 1,
        }

        self.assertEqual(face_counts, expected)

    def test_count_die_faces_multiple_units(self):
        """Test counting die faces for multiple units."""
        units = [self.melee_unit, self.missile_unit]

        face_counts = self.analyzer.count_die_faces(units)

        # Melee unit: 3 melee, 2 save, 1 maneuver, 1 SAI
        # Missile unit: 4 missile, 2 save, 1 maneuver
        expected = {
            constants.ICON_MELEE: 3,
            constants.ICON_MISSILE: 4,
            constants.ICON_SAVE: 4,  # 2 + 2
            constants.ICON_MANEUVER: 2,  # 1 + 1
            constants.ICON_SAI: 1,
        }

        self.assertEqual(face_counts, expected)

    def test_count_die_faces_with_dict_units(self):
        """Test counting die faces with dictionary-style units."""
        units = [self.dict_melee_unit]

        face_counts = self.analyzer.count_die_faces(units)

        expected = {
            constants.ICON_MELEE: 3,
            constants.ICON_SAVE: 2,
            constants.ICON_MANEUVER: 1,
            constants.ICON_SAI: 1,
        }

        self.assertEqual(face_counts, expected)

    def test_count_die_faces_no_units(self):
        """Test counting die faces with no units."""
        face_counts = self.analyzer.count_die_faces([])
        self.assertEqual(face_counts, {})

    def test_count_die_faces_no_roster(self):
        """Test counting die faces without unit roster."""
        analyzer = DieFaceAnalyzer(None)
        face_counts = analyzer.count_die_faces([self.melee_unit])
        self.assertEqual(face_counts, {})

    def test_count_die_faces_unit_not_found(self):
        """Test counting die faces for unit not in roster."""
        unknown_unit = Mock()
        unknown_unit.unit_type = "unknown_unit"

        face_counts = self.analyzer.count_die_faces([unknown_unit])
        self.assertEqual(face_counts, {})

    def test_get_sorted_face_counts(self):
        """Test sorting face counts by priority and count."""
        face_counts = {
            constants.ICON_SAI: 1,
            constants.ICON_MELEE: 3,
            constants.ICON_SAVE: 2,
            constants.ICON_MISSILE: 3,
        }

        sorted_faces = self.analyzer.get_sorted_face_counts(face_counts)

        # Should be sorted by priority order first, then by count (descending)
        # Priority: MELEE, MISSILE, MAGIC, SAVE, MANEUVER, SAI
        expected_order = [
            (constants.ICON_MELEE, 3),
            (constants.ICON_MISSILE, 3),
            (constants.ICON_SAVE, 2),
            (constants.ICON_SAI, 1),
        ]

        for i, (face_type, count) in enumerate(expected_order):
            self.assertEqual(sorted_faces[i].face_type, face_type)
            self.assertEqual(sorted_faces[i].count, count)

    def test_analyze_unit_die_faces(self):
        """Test complete analysis of unit die faces."""
        units = [self.melee_unit]

        sorted_faces = self.analyzer.analyze_unit_die_faces(units)

        # Should return sorted DieFaceCount objects
        self.assertEqual(len(sorted_faces), 4)
        self.assertEqual(sorted_faces[0].face_type, constants.ICON_MELEE)
        self.assertEqual(sorted_faces[0].count, 3)
        self.assertEqual(sorted_faces[0].icon, "⚔️")

    def test_get_face_distribution_summary(self):
        """Test comprehensive face distribution summary."""
        units = [self.melee_unit]

        summary = self.analyzer.get_face_distribution_summary(units)

        self.assertEqual(
            summary["total_faces"], 7
        )  # 3 melee + 2 save + 1 maneuver + 1 SAI
        self.assertEqual(summary["unique_face_types"], 4)
        self.assertIn("face_counts", summary)
        self.assertIn("sorted_faces", summary)
        self.assertIn("percentages", summary)
        self.assertIsNotNone(summary["most_common"])
        self.assertIsNotNone(summary["least_common"])

        # Check percentages
        expected_melee_percentage = round((3 / 7) * 100, 1)  # ~42.9%
        self.assertEqual(
            summary["percentages"][constants.ICON_MELEE], expected_melee_percentage
        )

    def test_compare_army_compositions(self):
        """Test comparison between two army compositions."""
        army1_units = [self.melee_unit]  # 3 melee, 2 save, 1 maneuver, 1 SAI
        army2_units = [self.missile_unit]  # 4 missile, 2 save, 1 maneuver

        comparison = self.analyzer.compare_army_compositions(army1_units, army2_units)

        self.assertEqual(comparison["army1_total"], 7)
        self.assertEqual(comparison["army2_total"], 7)

        # Check differences
        self.assertEqual(
            comparison["face_differences"][constants.ICON_MELEE]["difference"], 3
        )  # Army1 has 3 more melee
        self.assertEqual(
            comparison["face_differences"][constants.ICON_MISSILE]["difference"], -4
        )  # Army1 has 4 fewer missile
        self.assertEqual(
            comparison["face_differences"][constants.ICON_SAVE]["difference"], 0
        )  # Equal saves

        # Check advantages
        self.assertIn((constants.ICON_MELEE, 3), comparison["army1_advantages"])
        self.assertIn((constants.ICON_MISSILE, 4), comparison["army2_advantages"])
        self.assertIn(constants.ICON_SAVE, comparison["equal_faces"])

    def test_get_tactical_analysis(self):
        """Test tactical analysis of unit composition."""
        units = [self.melee_unit]  # 3 melee, 2 save, 1 maneuver, 1 SAI

        analysis = self.analyzer.get_tactical_analysis(units)

        self.assertEqual(analysis["offensive_strength"], 3)  # 3 melee
        self.assertEqual(analysis["defensive_strength"], 2)  # 2 save
        self.assertEqual(analysis["utility_strength"], 2)  # 1 maneuver + 1 SAI
        self.assertEqual(analysis["total_combat_faces"], 5)  # 3 melee + 2 save
        self.assertEqual(analysis["primary_strength"], "offensive")

        # With only 3/7 offensive faces, this should not have major weaknesses
        self.assertIsInstance(analysis["weaknesses"], list)
        self.assertIsInstance(analysis["balanced"], bool)

    def test_get_icon_for_face_type(self):
        """Test icon retrieval for face types."""
        self.assertEqual(
            DieFaceAnalyzer.get_icon_for_face_type(constants.ICON_MELEE), "⚔️"
        )
        self.assertEqual(
            DieFaceAnalyzer.get_icon_for_face_type(constants.ICON_MISSILE), "🏹"
        )
        self.assertEqual(
            DieFaceAnalyzer.get_icon_for_face_type(constants.ICON_SAVE), "🛡️"
        )
        self.assertEqual(DieFaceAnalyzer.get_icon_for_face_type("unknown"), "❓")

    def test_format_face_summary_compact(self):
        """Test compact face summary formatting."""
        face_counts = {
            constants.ICON_MELEE: 3,
            constants.ICON_SAVE: 2,
            constants.ICON_MISSILE: 1,
        }

        summary = self.analyzer.format_face_summary(face_counts, compact=True)

        # Should be in priority order: melee, missile, save
        self.assertEqual(summary, "⚔️3 🏹1 🛡️2")

    def test_format_face_summary_detailed(self):
        """Test detailed face summary formatting."""
        face_counts = {constants.ICON_MELEE: 3, constants.ICON_SAVE: 2}

        summary = self.analyzer.format_face_summary(face_counts, compact=False)

        self.assertEqual(summary, "Melee: 3, Save: 2")

    def test_format_face_summary_empty(self):
        """Test formatting empty face summary."""
        summary = self.analyzer.format_face_summary({})
        self.assertEqual(summary, "No die faces")


class TestUnitDieFaceExtractor(unittest.TestCase):
    """Test the UnitDieFaceExtractor utility class."""

    def test_extract_from_unit_definition(self):
        """Test extracting die faces from unit definition."""
        unit_def = {
            "die_faces": {
                "face_1": constants.ICON_MELEE,
                "face_2": constants.ICON_SAVE,
                "face_3": constants.ICON_ID,
                "face_4": constants.ICON_MISSILE,
                "face_5": constants.ICON_MANEUVER,
                "face_6": constants.ICON_SAI,
                "eighth_face_1": constants.ICON_MELEE,
                "eighth_face_2": constants.ICON_MAGIC,
                "extra_field": "ignored",  # Should be ignored
            }
        }

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        expected = {
            "face_1": constants.ICON_MELEE,
            "face_2": constants.ICON_SAVE,
            "face_3": constants.ICON_ID,
            "face_4": constants.ICON_MISSILE,
            "face_5": constants.ICON_MANEUVER,
            "face_6": constants.ICON_SAI,
            "eighth_face_1": constants.ICON_MELEE,
            "eighth_face_2": constants.ICON_MAGIC,
        }

        self.assertEqual(extracted, expected)

    def test_extract_from_unit_definition_no_die_faces(self):
        """Test extracting from unit definition without die_faces."""
        unit_def = {"other_field": "value"}

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        self.assertEqual(extracted, {})

    def test_extract_from_unit_definition_partial(self):
        """Test extracting from unit definition with partial die_faces."""
        unit_def = {
            "die_faces": {
                "face_1": constants.ICON_MELEE,
                "face_3": constants.ICON_SAVE,
                "eighth_face_1": constants.ICON_MISSILE,
            }
        }

        extracted = UnitDieFaceExtractor.extract_from_unit_definition(unit_def)

        expected = {
            "face_1": constants.ICON_MELEE,
            "face_3": constants.ICON_SAVE,
            "eighth_face_1": constants.ICON_MISSILE,
        }

        self.assertEqual(extracted, expected)

    def test_validate_face_structure_valid(self):
        """Test validation of valid face structure."""
        die_faces = {
            "face_1": constants.ICON_MELEE,
            "face_2": constants.ICON_MISSILE,
            "face_3": constants.ICON_MAGIC,
            "face_4": constants.ICON_SAVE,
            "face_5": constants.ICON_ID,
            "face_6": constants.ICON_MANEUVER,
            "eighth_face_1": constants.ICON_SAI,
            "eighth_face_2": constants.ICON_MELEE,
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_face_structure_missing_faces(self):
        """Test validation of face structure with missing required faces."""
        die_faces = {
            "face_1": constants.ICON_MELEE,
            "face_2": constants.ICON_SAVE,
            # Missing face_3 through face_6
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 4)  # Missing face_3, face_4, face_5, face_6
        self.assertIn("Missing required face position: face_3", errors)

    def test_validate_face_structure_invalid_face_types(self):
        """Test validation of face structure with invalid face types."""
        die_faces = {
            "face_1": constants.ICON_MELEE,
            "face_2": "INVALID_FACE",
            "face_3": constants.ICON_SAVE,
            "face_4": "ANOTHER_INVALID",
            "face_5": constants.ICON_ID,
            "face_6": constants.ICON_MANEUVER,
        }

        is_valid, errors = UnitDieFaceExtractor.validate_face_structure(die_faces)

        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)  # Two invalid face types
        self.assertTrue(
            any("Invalid face type 'INVALID_FACE'" in error for error in errors)
        )
        self.assertTrue(
            any("Invalid face type 'ANOTHER_INVALID'" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
