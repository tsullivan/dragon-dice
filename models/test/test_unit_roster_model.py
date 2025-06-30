import unittest
from unittest.mock import Mock, patch
from models.unit_roster_model import UnitRosterModel
from models.unit_model import UnitModel
from models.app_data_model import AppDataModel


class TestUnitRosterModel(unittest.TestCase):
    """Test the UnitRosterModel for unit definition management."""

    def setUp(self):
        """Set up test data for unit roster tests."""
        self.sample_unit_data = {
            "Goblin": [
                {
                    "unit_type_id": "goblin_thug",
                    "display_name": "Thug",
                    "max_health": 1,
                    "unit_class_type": "Heavy Melee",
                    "abilities": {"id_results": {"MELEE": 1, "SAVE": 1}},
                },
                {
                    "unit_type_id": "goblin_cutthroat",
                    "display_name": "Cutthroat",
                    "max_health": 2,
                    "unit_class_type": "Heavy Melee",
                    "abilities": {"id_results": {"MELEE": 2, "SAVE": 1}},
                },
            ],
            "Amazon": [
                {
                    "unit_type_id": "amazon_warrior",
                    "display_name": "Warrior",
                    "max_health": 2,
                    "unit_class_type": "Light Melee",
                    "abilities": {"id_results": {"MELEE": 1, "MISSILE": 1, "SAVE": 1}},
                }
            ],
        }

    def test_unit_roster_initialization(self):
        """Test UnitRosterModel initialization."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Should have loaded unit definitions
        mock_app_data_model.get_unit_definitions.assert_called_once()
        self.assertEqual(len(roster._unit_definitions), 3)  # 2 Goblin + 1 Amazon

    def test_get_available_unit_types(self):
        """Test getting available unit types."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)
        unit_types = roster.get_available_unit_types()

        self.assertEqual(len(unit_types), 3)

        # Check structure
        for unit_type in unit_types:
            self.assertIn("id", unit_type)
            self.assertIn("name", unit_type)
            self.assertIn("cost", unit_type)

        # Check specific units
        unit_ids = [unit["id"] for unit in unit_types]
        self.assertIn("goblin_thug", unit_ids)
        self.assertIn("goblin_cutthroat", unit_ids)
        self.assertIn("amazon_warrior", unit_ids)

        # Check cost calculation (using max_health as cost)
        thug_unit = next(u for u in unit_types if u["id"] == "goblin_thug")
        self.assertEqual(thug_unit["cost"], 1)

        cutthroat_unit = next(u for u in unit_types if u["id"] == "goblin_cutthroat")
        self.assertEqual(cutthroat_unit["cost"], 2)

    def test_get_available_unit_types_by_species(self):
        """Test getting unit types grouped by species."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)
        units_by_species = roster.get_available_unit_types_by_species()

        # Should have two species
        self.assertIn("Goblin", units_by_species)
        self.assertIn("Amazon", units_by_species)

        # Goblin should have 2 units
        self.assertEqual(len(units_by_species["Goblin"]), 2)
        goblin_unit_ids = [unit["id"] for unit in units_by_species["Goblin"]]
        self.assertIn("goblin_thug", goblin_unit_ids)
        self.assertIn("goblin_cutthroat", goblin_unit_ids)

        # Amazon should have 1 unit
        self.assertEqual(len(units_by_species["Amazon"]), 1)
        amazon_unit_ids = [unit["id"] for unit in units_by_species["Amazon"]]
        self.assertIn("amazon_warrior", amazon_unit_ids)

    def test_get_unit_definition(self):
        """Test getting specific unit definitions."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Test existing unit
        thug_def = roster.get_unit_definition("goblin_thug")
        self.assertIsNotNone(thug_def)
        self.assertEqual(thug_def["display_name"], "Thug")
        self.assertEqual(thug_def["max_health"], 1)
        self.assertEqual(thug_def["unit_class_type"], "Heavy Melee")

        # Test non-existing unit
        invalid_def = roster.get_unit_definition("invalid_unit")
        self.assertIsNone(invalid_def)

    def test_create_unit_instance(self):
        """Test creating unit instances from definitions."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Test creating valid unit instance
        unit_instance = roster.create_unit_instance(
            "goblin_thug", "test_instance_id", "Custom Thug Name"
        )

        self.assertIsNotNone(unit_instance)
        self.assertIsInstance(unit_instance, UnitModel)
        self.assertEqual(unit_instance.unit_id, "test_instance_id")
        self.assertEqual(unit_instance.name, "Custom Thug Name")
        self.assertEqual(unit_instance.unit_type, "goblin_thug")
        self.assertEqual(unit_instance.health, 1)
        self.assertEqual(unit_instance.max_health, 1)

    def test_create_unit_instance_with_default_name(self):
        """Test creating unit instance with default name."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance(
            "goblin_cutthroat", "test_instance_id"
        )

        self.assertIsNotNone(unit_instance)
        self.assertEqual(unit_instance.name, "Cutthroat")  # Default display name
        self.assertEqual(unit_instance.health, 2)
        self.assertEqual(unit_instance.max_health, 2)

    def test_create_unit_instance_invalid_type(self):
        """Test creating unit instance with invalid unit type."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance(
            "invalid_unit_type", "test_instance_id"
        )

        self.assertIsNone(unit_instance)

    def test_abilities_mapping(self):
        """Test that abilities are properly mapped in unit creation."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance(
            "amazon_warrior", "test_instance_id"
        )

        self.assertIsNotNone(unit_instance)
        self.assertIn("id_results", unit_instance.abilities)

        id_results = unit_instance.abilities["id_results"]
        self.assertEqual(id_results["MELEE"], 1)
        self.assertEqual(id_results["MISSILE"], 1)
        self.assertEqual(id_results["SAVE"], 1)

    def test_empty_unit_data_handling(self):
        """Test handling of empty unit data."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = {}

        roster = UnitRosterModel(mock_app_data_model)

        # Should handle empty data gracefully
        unit_types = roster.get_available_unit_types()
        self.assertEqual(len(unit_types), 0)

        units_by_species = roster.get_available_unit_types_by_species()
        self.assertEqual(len(units_by_species), 0)

        unit_def = roster.get_unit_definition("any_unit")
        self.assertIsNone(unit_def)

    @unittest.skip("Test disabled - needs unit data structure refactoring")
    def test_unit_data_structure_validation(self):
        """Test that unit data structure is properly validated."""
        # Malformed unit data missing required fields
        malformed_data = {
            "TestSpecies": [
                {
                    "unit_type_id": "test_unit",
                    # Missing display_name, max_health, etc.
                }
            ]
        }

        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = malformed_data

        roster = UnitRosterModel(mock_app_data_model)

        # Should handle malformed data gracefully
        try:
            unit_types = roster.get_available_unit_types()
            # Should not crash, but may have incomplete data
            self.assertIsInstance(unit_types, list)
        except Exception as e:
            # If it does fail, it should be a controlled failure
            self.assertIsInstance(e, (KeyError, AttributeError))

    def test_unit_roster_caching(self):
        """Test that unit roster data is cached properly."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Multiple calls should not reload data
        roster.get_available_unit_types()
        roster.get_available_unit_types()
        roster.get_unit_definition("goblin_thug")

        # Should only have loaded once during initialization
        mock_app_data_model.get_unit_definitions.assert_called_once()


if __name__ == "__main__":
    unittest.main()
