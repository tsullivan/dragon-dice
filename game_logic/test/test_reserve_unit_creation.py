import unittest
from unittest.mock import MagicMock, Mock, patch

from game_logic.game_state_manager import GameStateManager


class TestReserveUnitCreation(unittest.TestCase):
    """Test the reserve unit creation system using actual unit roster."""

    def setUp(self):
        """Set up test data for reserve unit creation tests."""
        self.player_setup_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",
                        "units": [],
                        "unique_id": "player_1_home",
                    }
                },
            }
        ]

        self.frontier_terrain = "Swampland (Green, Yellow)"
        self.distance_rolls = [("Player 1", 5)]

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_basic(self, mock_roster_class):
        """Test basic reserve unit creation."""
        # Mock unit roster
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Mock available units
        mock_roster.get_available_unit_types_by_species.return_value = {
            "Goblin": [
                {"id": "goblin_thug", "name": "Thug"},
                {"id": "goblin_cutthroat", "name": "Cutthroat"},
            ]
        }

        # Mock unit definitions with health-based costs
        mock_roster.get_unit_definition.side_effect = lambda unit_id: {
            "goblin_thug": {"display_name": "Thug", "max_health": 1},
            "goblin_cutthroat": {"display_name": "Cutthroat", "max_health": 2},
        }[unit_id]

        # Mock unit instance creation
        mock_unit_instance = Mock()
        mock_unit_instance.unit_id = "player_1_reserve_1"
        mock_unit_instance.name = "Reserve Thug"
        mock_unit_instance.health = 1
        mock_unit_instance.max_health = 1
        mock_unit_instance.unit_type = "goblin_thug"
        mock_unit_instance.get_face_names.return_value = ["Melee", "Save"]  # Mock faces instead of abilities

        mock_roster.create_unit_instance.return_value = mock_unit_instance

        # Create manager and test reserve creation
        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        reserves = manager._create_reserve_units("Player 1", 5)

        # Should create units within point limit
        assert len(reserves) > 0
        assert len(reserves) <= 5  # Max 5 units with 1 health each

        # Verify unit structure
        for unit in reserves:
            assert "id" in unit
            assert "name" in unit
            assert "health" in unit
            assert "max_health" in unit
            assert "point_cost" in unit
            assert "unit_type" in unit
            assert "faces" in unit
            assert unit["location"] == "Reserve Pool"

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_variety(self, mock_roster_class):
        """Test that reserve unit creation provides variety."""
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Mock multiple affordable units
        mock_roster.get_available_unit_types_by_species.return_value = {
            "Goblin": [
                {"id": "goblin_thug", "name": "Thug"},
                {"id": "goblin_mugger", "name": "Mugger"},
                {"id": "goblin_pelter", "name": "Pelter"},
            ]
        }

        # All units cost 1 point (health = 1)
        mock_roster.get_unit_definition.side_effect = lambda unit_id: {
            "goblin_thug": {"display_name": "Thug", "max_health": 1},
            "goblin_mugger": {"display_name": "Mugger", "max_health": 1},
            "goblin_pelter": {"display_name": "Pelter", "max_health": 1},
        }[unit_id]

        # Mock unit instance creation to return different units
        def create_instance_side_effect(unit_id, instance_id, name):
            instance = Mock()
            instance.unit_id = instance_id
            instance.name = name
            instance.health = 1
            instance.max_health = 1
            instance.unit_type = unit_id
            instance.get_face_names.return_value = ["Melee", "Save"]  # Mock faces instead of abilities
            return instance

        mock_roster.create_unit_instance.side_effect = create_instance_side_effect

        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        reserves = manager._create_reserve_units("Player 1", 6)

        # Should create 6 units (cycling through the 3 types)
        assert len(reserves) == 6

        # Should have variety in unit types
        unit_types = [unit["unit_type"] for unit in reserves]
        unique_types = set(unit_types)
        assert len(unique_types) > 1  # Should have more than one type

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_cost_limits(self, mock_roster_class):
        """Test that reserve unit creation respects cost limits."""
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Mock units with different costs
        mock_roster.get_available_unit_types_by_species.return_value = {
            "Goblin": [
                {"id": "goblin_thug", "name": "Thug"},  # Cost 1
                {"id": "goblin_cutthroat", "name": "Cutthroat"},  # Cost 2
                {"id": "goblin_marauder", "name": "Marauder"},  # Cost 3
            ]
        }

        mock_roster.get_unit_definition.side_effect = lambda unit_id: {
            "goblin_thug": {"display_name": "Thug", "max_health": 1},
            "goblin_cutthroat": {"display_name": "Cutthroat", "max_health": 2},
            "goblin_marauder": {"display_name": "Marauder", "max_health": 3},
        }[unit_id]

        def create_instance_side_effect(unit_id, instance_id, name):
            health = {"goblin_thug": 1, "goblin_cutthroat": 2, "goblin_marauder": 3}[unit_id]
            instance = Mock()
            instance.unit_id = instance_id
            instance.name = name
            instance.health = health
            instance.max_health = health
            instance.unit_type = unit_id
            instance.get_face_names.return_value = ["Melee", "Save"]  # Mock faces instead of abilities
            return instance

        mock_roster.create_unit_instance.side_effect = create_instance_side_effect

        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        reserves = manager._create_reserve_units("Player 1", 5)

        # Calculate total cost used
        total_cost = sum(unit["point_cost"] for unit in reserves)
        assert total_cost <= 5  # Should not exceed budget

        # Should create some units
        assert len(reserves) > 0

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_no_affordable_units(self, mock_roster_class):
        """Test reserve creation when no units are affordable."""
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Mock expensive units only
        mock_roster.get_available_unit_types_by_species.return_value = {
            "Goblin": [{"id": "goblin_expensive", "name": "Expensive"}]
        }

        # Unit costs more than available points
        mock_roster.get_unit_definition.side_effect = lambda unit_id: {
            "goblin_expensive": {"display_name": "Expensive", "max_health": 10}
        }[unit_id]

        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        reserves = manager._create_reserve_units("Player 1", 5)

        # Should create no units if none are affordable
        assert len(reserves) == 0

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_empty_roster(self, mock_roster_class):
        """Test reserve creation with empty unit roster."""
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Empty roster
        mock_roster.get_available_unit_types_by_species.return_value = {}

        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        reserves = manager._create_reserve_units("Player 1", 10)

        # Should create no units with empty roster
        assert len(reserves) == 0

    @patch("models.unit_roster_model.UnitRosterModel")
    def test_create_reserve_units_cap_limit(self, mock_roster_class):
        """Test that reserve unit creation respects the unit cap."""
        mock_roster = Mock()
        mock_roster_class.return_value = mock_roster

        # Mock cheap units
        mock_roster.get_available_unit_types_by_species.return_value = {
            "Goblin": [{"id": "goblin_thug", "name": "Thug"}]
        }

        mock_roster.get_unit_definition.return_value = {
            "display_name": "Thug",
            "max_health": 1,
        }

        mock_unit_instance = Mock()
        mock_unit_instance.unit_id = "player_1_reserve_1"
        mock_unit_instance.name = "Reserve Thug"
        mock_unit_instance.health = 1
        mock_unit_instance.max_health = 1
        mock_unit_instance.unit_type = "goblin_thug"
        mock_unit_instance.get_face_names.return_value = ["Melee", "Save"]  # Mock faces instead of abilities
        mock_roster.create_unit_instance.return_value = mock_unit_instance

        manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

        # Try to create way more units than the cap allows
        reserves = manager._create_reserve_units("Player 1", 100)

        # Should be capped at 15 units regardless of points available
        assert len(reserves) <= 15


if __name__ == "__main__":
    unittest.main()
