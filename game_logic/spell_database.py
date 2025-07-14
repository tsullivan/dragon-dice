"""
Dragon Dice Spell Database - contains all spells available for casting.

This module provides a comprehensive database of Dragon Dice spells with their costs,
elements, targeting, and effects. Excludes Reserve spells for now.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from utils import strict_get


@dataclass
class Spell:
    """Represents a Dragon Dice spell."""

    name: str
    element: str  # "air", "death", "earth", "fire", "water", "elemental"
    cost: int
    species: Optional[str] = None  # None for "Any", or specific species name
    cantrip: bool = False
    description: str = ""
    target_type: str = "army"  # "army", "terrain", "self", "any_army"
    is_offensive: bool = False
    reserves_only: bool = False  # We'll exclude these for now


# Complete spell database from Dragon Dice rules
SPELL_DATABASE = {
    # AIR SPELLS
    "hailstorm": Spell(
        name="Hailstorm",
        element="air",
        cost=2,
        cantrip=True,
        description="Inflict 1 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "lightning": Spell(
        name="Lightning",
        element="air",
        cost=3,
        description="Inflict 2 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "wilding": Spell(
        name="Wilding",
        element="air",
        cost=3,
        species="Feral",
        cantrip=True,
        description="Target army can double melee and save results of one unit",
        target_type="any_army",
    ),
    "wind_walk": Spell(
        name="Wind Walk",
        element="air",
        cost=4,
        cantrip=True,
        description="Add 4 maneuver results to target army's rolls",
        target_type="any_army",
    ),
    "tempest": Spell(
        name="Tempest",
        element="air",
        cost=5,
        description="Inflict 3 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "whirlwind": Spell(
        name="Whirlwind",
        element="air",
        cost=6,
        description="Inflict 1 damage on all opposing armies",
        target_type="all_armies",
        is_offensive=True,
    ),
    # DEATH SPELLS
    "palsy": Spell(
        name="Palsy",
        element="death",
        cost=2,
        cantrip=True,
        description="Subtract 1 result from target's non-maneuver rolls",
        target_type="any_army",
        is_offensive=True,
    ),
    "fear": Spell(
        name="Fear",
        element="death",
        cost=3,
        description="Subtract 2 results from target's non-maneuver rolls",
        target_type="any_army",
        is_offensive=True,
    ),
    "restless_dead": Spell(
        name="Restless Dead",
        element="death",
        cost=3,
        species="Undead",
        cantrip=True,
        description="Add 3 maneuver results to target army's rolls",
        target_type="any_army",
    ),
    "death_stare": Spell(
        name="Death Stare",
        element="death",
        cost=4,
        description="Inflict 2 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "plague": Spell(
        name="Plague",
        element="death",
        cost=5,
        description="Inflict 3 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "death_cloud": Spell(
        name="Death Cloud",
        element="death",
        cost=6,
        description="Inflict 1 damage on all opposing armies",
        target_type="all_armies",
        is_offensive=True,
    ),
    # EARTH SPELLS
    "stone_skin": Spell(
        name="Stone Skin",
        element="earth",
        cost=2,
        cantrip=True,
        description="Add 1 save result to target army's rolls",
        target_type="any_army",
    ),
    "armor": Spell(
        name="Armor",
        element="earth",
        cost=3,
        description="Add 2 save results to target army's rolls",
        target_type="any_army",
    ),
    "path": Spell(
        name="Path",
        element="earth",
        cost=4,
        cantrip=True,
        description="Move one of your units to another terrain where you have an army",
        target_type="self",
    ),
    "berserker_rage": Spell(
        name="Berserker Rage",
        element="earth",
        cost=5,
        species="Feral",
        cantrip=True,
        description="Feral units can count save results as melee results during counter-attacks",
        target_type="self",
    ),
    "iron_skin": Spell(
        name="Iron Skin",
        element="earth",
        cost=5,
        description="Add 3 save results to target army's rolls",
        target_type="any_army",
    ),
    "earthquake": Spell(
        name="Earthquake",
        element="earth",
        cost=6,
        description="Inflict 1 damage on all armies at target terrain",
        target_type="terrain",
        is_offensive=True,
    ),
    # FIRE SPELLS
    "ash_storm": Spell(
        name="Ash Storm",
        element="fire",
        cost=2,
        cantrip=True,
        description="Subtract 1 result from all army rolls at target terrain",
        target_type="terrain",
        is_offensive=True,
    ),
    "flashfire": Spell(
        name="Flashfire",
        element="fire",
        cost=3,
        species="Firewalkers",
        cantrip=True,
        description="Target army can re-roll one unit once during non-maneuver rolls",
        target_type="any_army",
    ),
    "fiery_weapon": Spell(
        name="Fiery Weapon",
        element="fire",
        cost=4,
        cantrip=True,
        description="Add 2 melee or missile results to target army's rolls",
        target_type="any_army",
    ),
    "fireball": Spell(
        name="Fireball",
        element="fire",
        cost=4,
        description="Inflict 2 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "flame_storm": Spell(
        name="Flame Storm",
        element="fire",
        cost=5,
        description="Inflict 3 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "conflagration": Spell(
        name="Conflagration",
        element="fire",
        cost=6,
        description="Inflict 1 damage on all armies at target terrain",
        target_type="terrain",
        is_offensive=True,
    ),
    # WATER SPELLS
    "watery_double": Spell(
        name="Watery Double",
        element="water",
        cost=2,
        cantrip=True,
        description="Add 1 save result to target army's rolls",
        target_type="any_army",
    ),
    "accelerated_growth": Spell(
        name="Accelerated Growth",
        element="water",
        cost=3,
        species="Treefolk",
        cantrip=True,
        description="Exchange killed 2+ health Treefolk with 1 health unit from DUA",
        target_type="self",
    ),
    "mist": Spell(
        name="Mist",
        element="water",
        cost=3,
        description="Add 2 save results to target army's rolls",
        target_type="any_army",
    ),
    "water_walk": Spell(
        name="Water Walk",
        element="water",
        cost=4,
        description="Add 4 maneuver results to target army's rolls",
        target_type="any_army",
    ),
    "deluge": Spell(
        name="Deluge",
        element="water",
        cost=5,
        description="Inflict 3 damage on any opposing army",
        target_type="any_army",
        is_offensive=True,
    ),
    "flood": Spell(
        name="Flood",
        element="water",
        cost=6,
        description="Inflict 1 damage on all armies at target terrain",
        target_type="terrain",
        is_offensive=True,
    ),
    # ELEMENTAL SPELLS (any element can cast)
    "evolve_dragonkin": Spell(
        name="Evolve Dragonkin",
        element="elemental",
        cost=3,
        species="Eldarim",
        cantrip=True,
        description="Promote one Dragonkin unit one health-worth",
        target_type="self",
    ),
    "resurrect_dead": Spell(
        name="Resurrect Dead",
        element="elemental",
        cost=3,
        cantrip=True,
        description="Return one health-worth of units from DUA to casting army",
        target_type="self",
    ),
    "esfahs_gift": Spell(
        name="Esfah's Gift",
        element="elemental",
        cost=3,
        species="Amazons",
        cantrip=True,
        description="Move minor terrain from BUA to summoning pool",
        target_type="self",
    ),
    "rally": Spell(
        name="Rally",
        element="elemental",
        cost=5,
        species="Amazons",
        cantrip=True,
        description="Move up to 3 Amazon units to another terrain with Amazons",
        target_type="self",
    ),
    "rise_of_the_eldarim": Spell(
        name="Rise of the Eldarim",
        element="elemental",
        cost=5,
        species="Eldarim",
        cantrip=True,
        description="Promote one Eldarim unit one health-worth",
        target_type="self",
    ),
    "necromantic_wave": Spell(
        name="Necromantic Wave",
        element="elemental",
        cost=5,
        species="Lava Elves",
        cantrip=True,
        description="Target army can count magic results as melee or missile results",
        target_type="any_army",
    ),
    "open_grave": Spell(
        name="Open Grave",
        element="elemental",
        cost=5,
        species="Undead",
        cantrip=True,
        description="Units killed by army-targeting effects go to Reserve Area instead of DUA",
        target_type="self",
    ),
}


class SpellDatabase:
    """Manages the Dragon Dice spell database and spell selection logic."""

    def __init__(self):
        self.spells = SPELL_DATABASE

    def get_available_spells(
        self,
        magic_points_by_element: Dict[str, int],
        army_species: List[str],
        cantrip_points: int = 0,
        cantrip_only: bool = False,
    ) -> List[Spell]:
        """
        Get list of spells that can be cast with available magic points.

        Args:
            magic_points_by_element: Dictionary of element -> available magic points
            army_species: List of species present in the casting army
            cantrip_points: Magic points available specifically for cantrip spells
            cantrip_only: If True, only return cantrip spells

        Returns:
            List of spells that can be cast
        """
        available_spells = []

        for spell in self.spells.values():
            if spell.reserves_only:
                continue  # Skip reserve spells for now

            # Check if this is cantrip-only mode
            if cantrip_only and not spell.cantrip:
                continue

            # Check if we have enough magic points
            if cantrip_only:
                # Use cantrip points
                if spell.cost > cantrip_points:
                    continue
            else:
                # Use regular magic points
                if spell.element == "elemental":
                    # Elemental spells can be cast with any element
                    total_available = sum(magic_points_by_element.values())
                    if spell.cost > total_available:
                        continue
                else:
                    # Element-specific spell
                    available_for_element = strict_get(magic_points_by_element, spell.element)
                    if spell.cost > available_for_element:
                        continue

            # Check species restrictions
            if spell.species and spell.species not in army_species:
                continue

            available_spells.append(spell)

        # Sort by element, then by cost, then by name
        available_spells.sort(key=lambda s: (s.element, s.cost, s.name))
        return available_spells

    def get_spell_by_name(self, name: str) -> Optional[Spell]:
        """Get a spell by its name."""
        return self.spells.get(name.lower().replace(" ", "_"))

    def get_spells_by_element(self, element: str) -> List[Spell]:
        """Get all spells of a specific element."""
        return [spell for spell in self.spells.values() if spell.element == element and not spell.reserves_only]

    def get_cantrip_spells(self) -> List[Spell]:
        """Get all cantrip spells."""
        return [spell for spell in self.spells.values() if spell.cantrip and not spell.reserves_only]

    def format_spell_description(self, spell: Spell) -> str:
        """Format a spell for display."""
        element_icons = {"air": "💨", "death": "💀", "earth": "🌍", "fire": "🔥", "water": "🌊", "elemental": "✨"}

        icon = strict_get(element_icons, spell.element)
        species_text = f" ({spell.species})" if spell.species else ""
        cantrip_text = " [Cantrip]" if spell.cantrip else ""

        return f"{icon} {spell.name}{species_text}{cantrip_text} - Cost: {spell.cost}\n    {spell.description}"

    def get_element_color(self, element: str) -> str:
        """Get CSS color for an element."""
        element_colors = {
            "air": "#87ceeb",  # Sky blue
            "death": "#2f2f2f",  # Dark gray
            "earth": "#daa520",  # Goldenrod
            "fire": "#ff6347",  # Tomato red
            "water": "#4682b4",  # Steel blue
            "elemental": "#9370db",  # Medium purple
        }
        return strict_get(element_colors, element)
