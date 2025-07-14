"""
Unit tests for army validation logic.

Tests the extracted business logic for Dragon Dice army composition validation
to ensure rules are correctly enforced independently of UI components.
"""

import unittest
from unittest.mock import Mock

from game_logic.army_validation import (
    ArmyComposition,
    ArmyCompositionBuilder,
    DragonDiceArmyValidator,
    ValidationResult,
)
from models.test.mock import create_player_setup_dict
from models.test.mock.typed_models import create_test_unit


class TestArmyComposition(unittest.TestCase):
    """Test the ArmyComposition dataclass."""

    def setUp(self):
        """Set up test fixtures using type-safe mock infrastructure."""
        # Create typed units with different health values
        self.unit_1pt = create_test_unit(
            unit_id="unit_1pt", name="1 Point Unit", unit_type="test_unit_1pt", health=1, max_health=1
        )

        self.unit_2pt = create_test_unit(
            unit_id="unit_2pt", name="2 Point Unit", unit_type="test_unit_2pt", health=2, max_health=2
        )

        self.unit_3pt = create_test_unit(
            unit_id="unit_3pt", name="3 Point Unit", unit_type="test_unit_3pt", health=3, max_health=3
        )

        # Dict-style units for testing
        self.dict_unit_1pt = {"max_health": 1, "unit_type": "test_unit"}
        self.dict_unit_2pt = {"max_health": 2, "unit_type": "test_unit"}

    def test_get_total_points_with_mock_units(self):
        """Test point calculation with typed unit objects."""
        army = ArmyComposition(
            army_type="Home",
            units=[self.unit_1pt, self.unit_2pt, self.unit_3pt],
        )

        assert army.get_total_points() == 6

    def test_get_total_points_with_dict_units(self):
        """Test point calculation with dictionary-style units."""
        army = ArmyComposition(army_type="Campaign", units=[self.dict_unit_1pt, self.dict_unit_2pt])

        assert army.get_total_points() == 3

    def test_get_total_points_empty_army(self):
        """Test point calculation for empty army."""
        army = ArmyComposition(army_type="Horde", units=[])
        assert army.get_total_points() == 0

    def test_get_unit_count(self):
        """Test unit count calculation."""
        army = ArmyComposition(army_type="Home", units=[self.unit_1pt, self.unit_2pt])

        assert army.get_unit_count() == 2

    def test_get_unit_count_empty(self):
        """Test unit count for empty army."""
        army = ArmyComposition(army_type="Campaign", units=[])
        assert army.get_unit_count() == 0


class TestDragonDiceArmyValidator(unittest.TestCase):
    """Test the main army validator class."""

    def setUp(self):
        """Set up test fixtures using type-safe mock infrastructure."""
        # Mock unit roster
        self.mock_unit_roster = Mock()
        self.mock_unit_roster.get_unit_definition.return_value = {"unit_class_type": "Heavy Melee"}

        self.validator = DragonDiceArmyValidator(self.mock_unit_roster)

        # Create typed test units
        self.unit_1pt = create_test_unit(
            unit_id="test_unit_1", name="1 Point Unit", unit_type="test_unit_1", health=1, max_health=1
        )

        self.unit_2pt = create_test_unit(
            unit_id="test_unit_2", name="2 Point Unit", unit_type="test_unit_2", health=2, max_health=2
        )

        self.unit_4pt = create_test_unit(
            unit_id="magic_unit_4", name="4 Point Magic Unit", unit_type="magic_unit", health=4, max_health=4
        )

        # Magic unit for testing Rule 3
        self.magic_unit_2pt = create_test_unit(
            unit_id="magic_unit_2", name="2 Point Magic Unit", unit_type="magic_unit", health=2, max_health=2
        )

    def test_valid_army_composition(self):
        """Test a valid army composition that should pass all rules."""
        armies = [
            ArmyComposition("Home", [self.unit_2pt, self.unit_2pt]),  # 4 pts (within 50% of 12)
            ArmyComposition("Campaign", [self.unit_2pt, self.unit_2pt, self.unit_2pt]),  # 6 pts (within 50% of 12)
            ArmyComposition("Horde", [self.unit_1pt, self.unit_1pt]),  # 2 pts
        ]

        result = self.validator.validate_army_composition(armies, force_size=12, num_players=2)

        assert result.is_valid, f"Expected valid but got errors: {result.errors}"
        assert len(result.errors) == 0
        assert result.total_force_points == 12

    def test_rule_1_empty_army_fails(self):
        """Test Rule 1: Each army must have at least 1 unit."""
        armies = [
            ArmyComposition("Home", []),  # Empty army - should fail
            ArmyComposition("Campaign", [self.unit_4pt]),
        ]

        result = self.validator.validate_army_composition(armies, force_size=10, num_players=2)

        assert not result.is_valid
        assert "Home Army must have at least 1 unit" in result.errors

    def test_rule_2_army_exceeds_50_percent_fails(self):
        """Test Rule 2: No army can exceed 50% of total force points."""
        armies = [
            ArmyComposition("Home", [self.unit_4pt, self.unit_4pt, self.unit_4pt]),  # 12 pts > 50% of 20
            ArmyComposition("Campaign", [self.unit_2pt]),  # 2 pts
        ]

        result = self.validator.validate_army_composition(armies, force_size=20, num_players=2)

        assert not result.is_valid
        assert any("exceeds maximum 10 pts" in error for error in result.errors)

    def test_rule_3_magic_units_exceed_50_percent_fails(self):
        """Test Rule 3: Magic units cannot exceed 50% of total force points."""

        # Set up magic unit definitions
        def mock_get_unit_definition(unit_type):
            if unit_type == "magic_unit":
                return {"unit_class_type": "Magic"}
            return {"unit_class_type": "Heavy Melee"}

        self.mock_unit_roster.get_unit_definition.side_effect = mock_get_unit_definition

        armies = [
            ArmyComposition("Home", [self.magic_unit_2pt, self.magic_unit_2pt]),  # 4 pts magic (within army limit)
            ArmyComposition(
                "Campaign", [self.magic_unit_2pt, self.unit_2pt, self.unit_2pt]
            ),  # 2 pts magic + 4 pts non-magic = 6 pts total
        ]
        # Total: 10 pts, Magic: 6 pts (exceeds 50% limit of 5 pts)

        result = self.validator.validate_army_composition(armies, force_size=10, num_players=2)

        assert not result.is_valid
        assert any("Magic units (6 pts) exceed maximum 5 pts" in error for error in result.errors)

    def test_rule_4_total_points_not_equal_force_size_fails(self):
        """Test Rule 4: Total army points must equal selected force size."""
        armies = [
            ArmyComposition("Home", [self.unit_2pt]),  # 2 pts
            ArmyComposition("Campaign", [self.unit_1pt]),  # 1 pt
        ]
        # Total = 3 pts, but force size = 10

        result = self.validator.validate_army_composition(armies, force_size=10, num_players=2)

        assert not result.is_valid
        assert any(
            "Total army points (3 pts) must equal selected force size (10 pts)" in error for error in result.errors
        )

    def test_horde_army_skipped_for_single_player(self):
        """Test that horde army validation is skipped for single player games."""
        armies = [
            ArmyComposition("Home", [self.unit_2pt, self.unit_2pt]),  # 4 pts
            ArmyComposition("Campaign", [self.unit_2pt, self.unit_2pt, self.unit_2pt]),  # 6 pts
            ArmyComposition("Horde", []),  # Empty horde army - should be skipped
        ]

        # Use force size 20 so both armies are within 50% limit (10 pts each max)
        result = self.validator.validate_army_composition(armies, force_size=20, num_players=1)

        # Should fail due to total points mismatch (10 != 20), but horde army error should not appear
        assert not result.is_valid
        # Check that horde army error is NOT in the errors (it should be skipped)
        horde_errors = [error for error in result.errors if "Horde" in error]
        assert len(horde_errors) == 0, "Horde army should be skipped for single player"

    def test_validate_single_army_valid(self):
        """Test validation of a single army within limits."""
        army = ArmyComposition("Home", [self.unit_2pt, self.unit_1pt])  # 3 pts

        is_valid, errors = self.validator.validate_single_army(army, max_points=5)

        assert is_valid
        assert len(errors) == 0

    def test_validate_single_army_exceeds_limit(self):
        """Test validation of a single army exceeding point limit."""
        army = ArmyComposition("Campaign", [self.unit_4pt, self.unit_4pt])  # 8 pts

        is_valid, errors = self.validator.validate_single_army(army, max_points=5)

        assert not is_valid
        assert "Campaign Army (8 pts) exceeds maximum 5 pts" in errors

    def test_validate_single_army_empty(self):
        """Test validation of empty single army."""
        army = ArmyComposition("Home", [])

        is_valid, errors = self.validator.validate_single_army(army, max_points=10)

        assert not is_valid
        assert "Home Army must have at least 1 unit" in errors

    def test_get_force_size_limits(self):
        """Test calculation of force size limits."""
        limits = self.validator.get_force_size_limits(24)

        expected = {
            "max_points_per_army": 12,  # 50% of 24
            "max_magic_points": 12,  # 50% of 24
            "total_force_size": 24,
        }

        assert limits == expected

    def test_get_force_size_limits_odd_number(self):
        """Test calculation of force size limits with odd force size (rounding down)."""
        limits = self.validator.get_force_size_limits(15)

        expected = {
            "max_points_per_army": 7,  # 50% of 15 rounded down
            "max_magic_points": 7,  # 50% of 15 rounded down
            "total_force_size": 15,
        }

        assert limits == expected

    def test_create_validation_summary_valid(self):
        """Test summary creation for valid composition."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            total_force_points=24,
            total_magic_points=8,
            army_point_totals={"Home": 12, "Campaign": 12},
        )

        summary = self.validator.create_validation_summary(result)
        assert summary == "✅ Army composition is valid"

    def test_create_validation_summary_invalid(self):
        """Test summary creation for invalid composition."""
        result = ValidationResult(
            is_valid=False,
            errors=["Home Army must have at least 1 unit", "Total points mismatch"],
            total_force_points=20,
            total_magic_points=10,
            army_point_totals={"Campaign": 20},
        )

        summary = self.validator.create_validation_summary(result)
        assert "❌ Army composition validation failed:" in summary
        assert "• Home Army must have at least 1 unit" in summary
        assert "• Total points mismatch" in summary


class TestArmyCompositionBuilder(unittest.TestCase):
    """Test the ArmyCompositionBuilder helper class."""

    def test_from_army_widgets(self):
        """Test building army compositions from UI widgets."""
        # Create typed units for widgets
        unit_2pt = create_test_unit(
            unit_id="widget_unit_2", name="Widget 2pt Unit", unit_type="widget_unit", health=2, max_health=2
        )

        unit_3pt = create_test_unit(
            unit_id="widget_unit_3", name="Widget 3pt Unit", unit_type="widget_unit", health=3, max_health=3
        )

        unit_1pt = create_test_unit(
            unit_id="widget_unit_1", name="Widget 1pt Unit", unit_type="widget_unit", health=1, max_health=1
        )

        # Mock army widgets with typed units
        mock_widget_1 = Mock()
        mock_widget_1.current_units = [unit_2pt, unit_3pt]

        mock_widget_2 = Mock()
        mock_widget_2.current_units = [unit_1pt]

        army_widgets = {"Home": mock_widget_1, "Campaign": mock_widget_2}

        armies = ArmyCompositionBuilder.from_army_widgets(army_widgets)

        assert len(armies) == 2
        assert armies[0].army_type == "Home"
        assert armies[0].get_total_points() == 5
        assert armies[1].army_type == "Campaign"
        assert armies[1].get_total_points() == 1

    def test_from_army_widgets_no_current_units(self):
        """Test building army compositions from widgets without current_units attribute."""
        mock_widget = Mock(spec=[])  # Widget without current_units
        army_widgets = {"Home": mock_widget}

        armies = ArmyCompositionBuilder.from_army_widgets(army_widgets)

        assert len(armies) == 1
        assert armies[0].army_type == "Home"
        assert armies[0].get_unit_count() == 0

    def test_from_player_data(self):
        """Test building army compositions from player data."""
        player_data = {
            "armies": {
                "home": {
                    "units": [
                        {"max_health": 2, "unit_type": "unit1"},
                        {"max_health": 1, "unit_type": "unit2"},
                    ]
                },
                "campaign": {"units": [{"max_health": 3, "unit_type": "unit3"}]},
            }
        }

        armies = ArmyCompositionBuilder.from_player_data(player_data)

        assert len(armies) == 2
        assert armies[0].army_type == "Home"
        assert armies[0].get_total_points() == 3
        assert armies[1].army_type == "Campaign"
        assert armies[1].get_total_points() == 3

    def test_from_player_data_no_armies(self):
        """Test building army compositions from player data without armies."""
        # Use type-safe player data with empty armies
        player_data = create_player_setup_dict(name="Test Player", home_terrain="Highland", force_size=24)
        # Clear armies to test the no-armies case
        player_data["armies"] = {}

        armies = ArmyCompositionBuilder.from_player_data(player_data)

        assert len(armies) == 0


if __name__ == "__main__":
    # Run the tests
    unittest.main()
