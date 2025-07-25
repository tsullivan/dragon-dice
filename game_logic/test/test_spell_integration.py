import unittest
from unittest.mock import Mock

from game_logic.action_resolver import ActionResolver
from game_logic.spell_resolver import SpellResolver
from models.effect_state.effect_manager import EffectManager
from models.test.mock import create_army_dict, create_player_setup_dict


class TestSpellIntegration(unittest.TestCase):
    """Test spell integration between ActionResolver, SpellResolver, and EffectManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock game state manager
        self.mock_gsm = Mock()
        self.mock_gsm.get_active_army_units.return_value = []
        self.mock_gsm.get_army_location.return_value = "forest"

        # Create real effect manager and spell resolver
        self.effect_manager = EffectManager()
        self.spell_resolver = SpellResolver(self.mock_gsm, self.effect_manager)

        # Create action resolver with spell resolver
        self.action_resolver = ActionResolver(self.mock_gsm, self.effect_manager, None, self.spell_resolver)

    def test_spell_resolver_initialization(self):
        """Test that spell resolver initializes correctly."""
        assert self.spell_resolver is not None
        assert self.spell_resolver.game_state_manager == self.mock_gsm
        assert self.spell_resolver.effect_manager == self.effect_manager

    def test_action_resolver_has_spell_resolver(self):
        """Test that action resolver has spell resolver reference."""
        assert self.action_resolver.spell_resolver is not None
        assert self.action_resolver.spell_resolver == self.spell_resolver

    def test_spell_requirements_lookup(self):
        """Test spell requirements lookup."""
        requirements = self.spell_resolver.get_spell_requirements("Stone Skin")

        assert "spell_name" in requirements
        assert requirements["spell_name"] == "Stone Skin"
        assert "cost" in requirements
        assert "element" in requirements

    def test_effect_manager_spell_effect_addition(self):
        """Test adding spell effects to effect manager."""
        initial_count = len(self.effect_manager.active_effects)

        effect_data = {
            "spell_name": "Stone Skin",
            "target_player": "TestPlayer",
            "effect_type": "modifier",
            "duration": "until_next_turn",
            "target_type": "army",
            "target_identifier": "test_army",
        }

        effect_id = self.effect_manager.add_spell_effect("TestPlayer", effect_data)

        assert effect_id is not None
        assert len(self.effect_manager.active_effects) == initial_count + 1

        # Verify effect structure
        added_effect = self.effect_manager.active_effects[-1]
        assert added_effect["type"] == "spell"
        assert added_effect["spell_name"] == "Stone Skin"
        assert added_effect["caster_player_name"] == "TestPlayer"

    def test_spell_effect_expiration(self):
        """Test spell effect expiration functionality."""
        # Add a spell effect
        effect_data = {
            "spell_name": "Wind Walk",
            "target_player": "TestPlayer",
            "effect_type": "modifier",
            "duration": "until_next_turn",
            "target_type": "army",
            "target_identifier": "test_army",
        }

        self.effect_manager.add_spell_effect("TestPlayer", effect_data)
        initial_count = len(self.effect_manager.active_effects)

        # Expire effects for the player
        expired_spells = self.effect_manager.expire_spell_effects_for_player("TestPlayer")

        assert len(expired_spells) == 1
        assert expired_spells[0] == "Wind Walk"
        assert len(self.effect_manager.active_effects) == initial_count - 1

    def test_magic_results_counting_by_element(self):
        """Test counting magic results by element."""
        # Mock active units with species elements
        mock_unit = Mock()
        mock_unit.species.elements = ["earth", "fire"]
        self.mock_gsm.get_active_army_units.return_value = [mock_unit]

        parsed_dice = [{"type": "Magic", "count": 2}]

        element_counts = self.action_resolver._count_magic_results_by_element("TestPlayer", parsed_dice)

        # Should have both elements available
        assert "earth" in element_counts
        assert "fire" in element_counts
        assert element_counts["earth"] == 2
        assert element_counts["fire"] == 2

    def test_get_player_species(self):
        """Test getting player species from active units."""
        # Mock units with different species
        mock_unit1 = Mock()
        mock_unit1.species.name = "Dwarf"
        mock_unit2 = Mock()
        mock_unit2.species.name = "Goblin"

        self.mock_gsm.get_active_army_units.return_value = [mock_unit1, mock_unit2]

        species = self.action_resolver._get_player_species("TestPlayer")

        assert "Dwarf" in species
        assert "Goblin" in species
        assert len(species) == 2

    def test_get_player_elements(self):
        """Test getting player elements from active units."""
        # Mock units with different elements
        mock_unit1 = Mock()
        mock_unit1.species.elements = ["earth", "fire"]
        mock_unit2 = Mock()
        mock_unit2.species.elements = ["air", "earth"]  # earth overlaps

        self.mock_gsm.get_active_army_units.return_value = [mock_unit1, mock_unit2]

        elements = self.action_resolver._get_player_elements("TestPlayer")

        # Should have unique elements
        assert "earth" in elements
        assert "fire" in elements
        assert "air" in elements
        assert len(elements) == 3  # No duplicates

    def test_process_effect_expirations_with_spells(self):
        """Test effect expiration processing includes spell effects."""
        # Add a spell effect
        effect_data = {
            "spell_name": "Blizzard",
            "target_player": "TestPlayer",
            "effect_type": "modifier",
            "duration": "until_next_turn",
            "target_type": "army",
            "target_identifier": "test_army",
        }

        self.effect_manager.add_spell_effect("TestPlayer", effect_data)
        initial_count = len(self.effect_manager.active_effects)

        # Process expiration for the player
        self.effect_manager.process_effect_expirations("TestPlayer")

        # Spell effect should be expired
        assert len(self.effect_manager.active_effects) == initial_count - 1


if __name__ == "__main__":
    unittest.main()
