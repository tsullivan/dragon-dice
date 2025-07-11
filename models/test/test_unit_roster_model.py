import unittest
from unittest.mock import Mock, patch

from models.app_data_model import AppDataModel
from models.unit_model import UnitModel
from models.unit_roster_model import UnitRosterModel


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
        assert len(roster._unit_definitions) == 3  # 2 Goblin + 1 Amazon

    def test_get_available_unit_types(self):
        """Test getting available unit types."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)
        unit_types = roster.get_available_unit_types()

        assert len(unit_types) == 3

        # Check structure
        for unit_type in unit_types:
            assert "id" in unit_type
            assert "name" in unit_type
            assert "cost" in unit_type

        # Check specific units
        unit_ids = [unit["id"] for unit in unit_types]
        assert "goblin_thug" in unit_ids
        assert "goblin_cutthroat" in unit_ids
        assert "amazon_warrior" in unit_ids

        # Check cost calculation (using max_health as cost)
        thug_unit = next(u for u in unit_types if u["id"] == "goblin_thug")
        assert thug_unit["cost"] == 1

        cutthroat_unit = next(u for u in unit_types if u["id"] == "goblin_cutthroat")
        assert cutthroat_unit["cost"] == 2

    def test_get_available_unit_types_by_species(self):
        """Test getting unit types grouped by species."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)
        units_by_species = roster.get_available_unit_types_by_species()

        # Should have two species
        assert "Goblin" in units_by_species
        assert "Amazon" in units_by_species

        # Goblin should have 2 units
        assert len(units_by_species["Goblin"]) == 2
        goblin_unit_ids = [unit["id"] for unit in units_by_species["Goblin"]]
        assert "goblin_thug" in goblin_unit_ids
        assert "goblin_cutthroat" in goblin_unit_ids

        # Amazon should have 1 unit
        assert len(units_by_species["Amazon"]) == 1
        amazon_unit_ids = [unit["id"] for unit in units_by_species["Amazon"]]
        assert "amazon_warrior" in amazon_unit_ids

    def test_get_unit_definition(self):
        """Test getting specific unit definitions."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Test existing unit
        thug_def = roster.get_unit_definition("goblin_thug")
        assert thug_def is not None
        assert thug_def["display_name"] == "Thug"
        assert thug_def["max_health"] == 1
        assert thug_def["unit_class_type"] == "Heavy Melee"

        # Test non-existing unit
        invalid_def = roster.get_unit_definition("invalid_unit")
        assert invalid_def is None

    def test_create_unit_instance(self):
        """Test creating unit instances from definitions."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        # Test creating valid unit instance
        unit_instance = roster.create_unit_instance("goblin_thug", "test_instance_id", "Custom Thug Name")

        assert unit_instance is not None
        assert isinstance(unit_instance, UnitModel)
        assert unit_instance.unit_id == "test_instance_id"
        assert unit_instance.name == "Custom Thug Name"
        assert unit_instance.unit_type == "goblin_thug"
        assert unit_instance.health == 1
        assert unit_instance.max_health == 1

    def test_create_unit_instance_with_default_name(self):
        """Test creating unit instance with default name."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance("goblin_cutthroat", "test_instance_id")

        assert unit_instance is not None
        assert unit_instance.name == "Cutthroat"  # Default display name
        assert unit_instance.health == 2
        assert unit_instance.max_health == 2

    def test_create_unit_instance_invalid_type(self):
        """Test creating unit instance with invalid unit type."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance("invalid_unit_type", "test_instance_id")

        assert unit_instance is None

    def test_abilities_mapping(self):
        """Test that faces are properly available in unit creation."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = self.sample_unit_data

        roster = UnitRosterModel(mock_app_data_model)

        unit_instance = roster.create_unit_instance("amazon_warrior", "test_instance_id")

        assert unit_instance is not None
        # The new UnitModel uses faces instead of abilities
        assert unit_instance.faces is not None
        assert isinstance(unit_instance.faces, list)
        # Check that faces have been populated (exact validation depends on actual unit data structure)
        face_names = unit_instance.get_face_names()
        assert isinstance(face_names, list)

    def test_empty_unit_data_handling(self):
        """Test handling of empty unit data."""
        mock_app_data_model = Mock(spec=AppDataModel)
        mock_app_data_model.get_unit_definitions.return_value = {}

        roster = UnitRosterModel(mock_app_data_model)

        # Should handle empty data gracefully
        unit_types = roster.get_available_unit_types()
        assert len(unit_types) == 0

        units_by_species = roster.get_available_unit_types_by_species()
        assert len(units_by_species) == 0

        unit_def = roster.get_unit_definition("any_unit")
        assert unit_def is None

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
