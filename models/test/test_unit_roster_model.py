import unittest
from unittest.mock import Mock, patch
from models.unit_roster_model import UnitRosterModel
from models.unit_model import UnitModel


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

    @patch("models.unit_roster_model.ResourceManager")
    def test_unit_roster_initialization(self, mock_resource_manager_class):
        """Test UnitRosterModel initialization."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        # Should have loaded unit definitions
        mock_resource_manager.load_unit_definitions.assert_called_once()
        self.assertEqual(len(roster._unit_definitions), 3)  # 2 Goblin + 1 Amazon

    @patch("models.unit_roster_model.ResourceManager")
    def test_get_available_unit_types(self, mock_resource_manager_class):
        """Test getting available unit types."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()
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

    @patch("models.unit_roster_model.ResourceManager")
    def test_get_available_unit_types_by_species(self, mock_resource_manager_class):
        """Test getting unit types grouped by species."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()
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

    @patch("models.unit_roster_model.ResourceManager")
    def test_get_unit_definition(self, mock_resource_manager_class):
        """Test getting specific unit definitions."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        # Test existing unit
        thug_def = roster.get_unit_definition("goblin_thug")
        self.assertIsNotNone(thug_def)
        self.assertEqual(thug_def["display_name"], "Thug")
        self.assertEqual(thug_def["max_health"], 1)
        self.assertEqual(thug_def["unit_class_type"], "Heavy Melee")

        # Test non-existing unit
        invalid_def = roster.get_unit_definition("invalid_unit")
        self.assertIsNone(invalid_def)

    @patch("models.unit_roster_model.ResourceManager")
    def test_create_unit_instance(self, mock_resource_manager_class):
        """Test creating unit instances from definitions."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

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

    @patch("models.unit_roster_model.ResourceManager")
    def test_create_unit_instance_with_default_name(self, mock_resource_manager_class):
        """Test creating unit instance with default name."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        unit_instance = roster.create_unit_instance(
            "goblin_cutthroat", "test_instance_id"
        )

        self.assertIsNotNone(unit_instance)
        self.assertEqual(unit_instance.name, "Cutthroat")  # Default display name
        self.assertEqual(unit_instance.health, 2)
        self.assertEqual(unit_instance.max_health, 2)

    @patch("models.unit_roster_model.ResourceManager")
    def test_create_unit_instance_invalid_type(self, mock_resource_manager_class):
        """Test creating unit instance with invalid unit type."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        unit_instance = roster.create_unit_instance(
            "invalid_unit_type", "test_instance_id"
        )

        self.assertIsNone(unit_instance)

    @patch("models.unit_roster_model.ResourceManager")
    def test_abilities_mapping(self, mock_resource_manager_class):
        """Test that abilities are properly mapped in unit creation."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        unit_instance = roster.create_unit_instance(
            "amazon_warrior", "test_instance_id"
        )

        self.assertIsNotNone(unit_instance)
        self.assertIn("id_results", unit_instance.abilities)

        id_results = unit_instance.abilities["id_results"]
        self.assertEqual(id_results["MELEE"], 1)
        self.assertEqual(id_results["MISSILE"], 1)
        self.assertEqual(id_results["SAVE"], 1)

    @patch("models.unit_roster_model.ResourceManager")
    def test_empty_unit_data_handling(self, mock_resource_manager_class):
        """Test handling of empty unit data."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = {}
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        # Should handle empty data gracefully
        unit_types = roster.get_available_unit_types()
        self.assertEqual(len(unit_types), 0)

        units_by_species = roster.get_available_unit_types_by_species()
        self.assertEqual(len(units_by_species), 0)

        unit_def = roster.get_unit_definition("any_unit")
        self.assertIsNone(unit_def)

    @patch("models.unit_roster_model.ResourceManager")
    def test_unit_data_structure_validation(self, mock_resource_manager_class):
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

        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = malformed_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        # Should handle malformed data gracefully
        try:
            unit_types = roster.get_available_unit_types()
            # Should not crash, but may have incomplete data
            self.assertIsInstance(unit_types, list)
        except Exception as e:
            # If it does fail, it should be a controlled failure
            self.assertIsInstance(e, (KeyError, AttributeError))

    @patch("models.unit_roster_model.ResourceManager")
    def test_unit_roster_caching(self, mock_resource_manager_class):
        """Test that unit roster data is cached properly."""
        mock_resource_manager = Mock()
        mock_resource_manager.load_unit_definitions.return_value = self.sample_unit_data
        mock_resource_manager_class.return_value = mock_resource_manager

        roster = UnitRosterModel()

        # Multiple calls should not reload data
        roster.get_available_unit_types()
        roster.get_available_unit_types()
        roster.get_unit_definition("goblin_thug")

        # Should only have loaded once during initialization
        mock_resource_manager.load_unit_definitions.assert_called_once()


if __name__ == "__main__":
    unittest.main()
