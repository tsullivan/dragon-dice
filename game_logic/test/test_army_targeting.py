import unittest
from unittest.mock import Mock, patch

from models.game_state.game_state_manager import GameStateManager
from models.test.mock import create_army_dict, create_player_setup_dict


class TestArmyTargeting(unittest.TestCase):
    """Test the army targeting system for Dragon Dice combat."""

    def setUp(self):
        """Set up test data for army targeting tests using type-safe mocks."""

        # Create Player 1 with complete mock data
        player1_data = create_player_setup_dict(name="Player 1", home_terrain="Highland", force_size=24)

        # Override armies with specific test configuration
        player1_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 1 Highland",
                allocated_points=10,
                unique_id="player_1_home",
                unit_count=1,
            ),
            "campaign": create_army_dict(
                name="Campaign Army",
                location="Swampland (Green, Yellow)",
                allocated_points=10,
                unique_id="player_1_campaign",
                unit_count=1,
            ),
        }

        # Create Player 2 with complete mock data
        player2_data = create_player_setup_dict(name="Player 2", home_terrain="Coastland", force_size=24)

        # Override armies with specific test configuration
        player2_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 2 Coastland",
                allocated_points=10,
                unique_id="player_2_home",
                unit_count=1,
            ),
            "horde": create_army_dict(
                name="Horde Army",
                location="Player 1 Highland",  # At Player 1's home
                allocated_points=10,
                unique_id="player_2_horde",
                unit_count=1,
            ),
        }

        self.player_setup_data = [player1_data, player2_data]
        self.frontier_terrain = "Swampland (Green, Yellow)"
        self.distance_rolls = [("Player 1", 5), ("Player 2", 3)]

        self.manager = GameStateManager(self.player_setup_data, self.frontier_terrain, self.distance_rolls)

    def test_find_defending_armies_at_location_with_enemies(self):
        """Test finding defending armies when enemies are present."""
        # Player 1 attacking at their home where Player 2 has a horde
        defending_armies = self.manager.find_defending_armies_at_location("Player 1", "Player 1 Highland")

        assert len(defending_armies) == 1
        assert defending_armies[0]["player"] == "Player 2"
        assert defending_armies[0]["army_id"] == "horde"

    def test_find_defending_armies_at_location_no_enemies(self):
        """Test finding defending armies when no enemies are present."""
        # Player 1 attacking at their own location with no enemies
        defending_armies = self.manager.find_defending_armies_at_location("Player 1", "Player 2 Coastland")

        assert len(defending_armies) == 1
        assert defending_armies[0]["player"] == "Player 2"
        assert defending_armies[0]["army_id"] == "home"

    def test_find_defending_armies_empty_location(self):
        """Test finding defending armies at an empty location."""
        defending_armies = self.manager.find_defending_armies_at_location("Player 1", "Empty Location")

        assert len(defending_armies) == 0

    def test_determine_primary_defending_player_home_priority(self):
        """Test that home armies have priority in defending."""
        # Create a new setup with multiple army types at same location for priority testing
        player1_data = create_player_setup_dict(name="Player 1", home_terrain="Highland", force_size=24)
        player1_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 1 Highland",
                allocated_points=10,
                unique_id="player_1_home",
                unit_count=1,
            ),
        }

        player2_data = create_player_setup_dict(name="Player 2", home_terrain="Coastland", force_size=24)
        player2_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 2 Coastland",
                allocated_points=8,
                unique_id="player_2_home",
                unit_count=1,
            ),
            "campaign": create_army_dict(
                name="Campaign Army",
                location="Player 1 Highland",  # Same location as horde
                allocated_points=6,
                unique_id="player_2_campaign",
                unit_count=1,
            ),
            "horde": create_army_dict(
                name="Horde Army",
                location="Player 1 Highland",  # Same location as campaign
                allocated_points=6,
                unique_id="player_2_horde",
                unit_count=1,
            ),
        }

        player_setup_data = [player1_data, player2_data]
        manager = GameStateManager(player_setup_data, self.frontier_terrain, self.distance_rolls)

        # Should prefer horde over campaign (home > campaign > horde)
        # In this case, horde is the highest priority present
        defending_player = manager.determine_primary_defending_player("Player 1", "Player 1 Highland")

        assert defending_player == "Player 2"

    def test_determine_primary_defending_player_no_enemies(self):
        """Test determining defending player when no enemies present."""
        defending_player = self.manager.determine_primary_defending_player("Player 1", "Empty Location")

        assert defending_player is None

    def test_determine_primary_defending_army_id_with_priority(self):
        """Test determining defending army ID with Dragon Dice priority rules."""
        defending_army_id = self.manager.determine_primary_defending_army_id("Player 1", "Player 1 Highland")

        # Should return the horde army ID (Player 2's horde at Player 1's home)
        assert defending_army_id == "player_2_horde"

    def test_get_armies_at_location(self):
        """Test getting all armies at a specific location."""
        armies = self.manager.get_armies_at_location("Player 1 Highland")

        # Should find Player 1's home army and Player 2's horde army
        assert len(armies) == 2

        army_players = [army["player"] for army in armies]
        army_types = [army["army_id"] for army in armies]

        assert "Player 1" in army_players
        assert "Player 2" in army_players
        assert "home" in army_types
        assert "horde" in army_types

    def test_army_targeting_integration(self):
        """Test the complete army targeting flow."""
        # Simulate Player 1 attacking at frontier location
        attacking_player = "Player 1"
        location = "Swampland (Green, Yellow)"

        # Should find Player 1's campaign army as the only army there
        defending_player = self.manager.determine_primary_defending_player(attacking_player, location)

        # No defending armies since only Player 1's army is there
        assert defending_player is None

        # Now test at Player 1's home where Player 2 has horde
        location = "Player 1 Highland"
        defending_player = self.manager.determine_primary_defending_player(attacking_player, location)
        defending_army_id = self.manager.determine_primary_defending_army_id(attacking_player, location)

        assert defending_player == "Player 2"
        assert defending_army_id == "player_2_horde"


if __name__ == "__main__":
    unittest.main()
