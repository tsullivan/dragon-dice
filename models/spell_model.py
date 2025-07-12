# models/spell_model.py
from typing import Any, Dict, List, Optional

from models.element_model import ELEMENT_DATA


class SpellModel:
    """Represents a Dragon Dice spell with all its properties."""

    def __init__(
        self,
        name: str,
        species: str,
        cost: int,
        reserves: bool,
        cantrip: bool,
        effect: str,
        element: Optional[str] = None,  # If None is given, spell is Elemental type
    ):
        self.name = name
        self.species = species
        self.cost = cost
        self.reserves = reserves
        self.cantrip = cantrip
        self.effect = effect
        self.element = element  # For organizing spells by element

    def __repr__(self):
        return f"SpellModel(name='{self.name}', element='{self.element}', cost={self.cost})"

    def can_be_cast_from_reserves(self) -> bool:
        """Check if this spell can be cast from the reserves area."""
        return self.reserves

    def is_cantrip(self) -> bool:
        """Check if this spell is a cantrip (can be cast for free with certain die faces)."""
        return self.cantrip

    def get_species_restriction(self) -> str:
        """Get the species restriction for this spell."""
        return self.species

    def is_available_to_species(self, species_name: str) -> bool:
        """Check if this spell is available to a specific species."""
        return self.species == "Any" or self.species == species_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "species": self.species,
            "cost": self.cost,
            "reserves": self.reserves,
            "cantrip": self.cantrip,
            "effect": self.effect,
            "element": self.element,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpellModel":
        return cls(
            name=data.get("name", ""),
            species=data.get("species", "Any"),
            cost=data.get("cost", 1),
            reserves=data.get("reserves", False),
            cantrip=data.get("cantrip", False),
            effect=data.get("effect", ""),
            element=data.get("element"),
        )


# Air element spells
AIR_SPELLS = {
    "HAILSTORM": SpellModel(
        name="Hailstorm",
        species="Any",
        cost=2,
        reserves=False,
        cantrip=True,
        effect="Target any opposing army. Inflict one point of damage on the target.",
        element="AIR",
    ),
    "BLIZZARD": SpellModel(
        name="Blizzard",
        species="Coral Elves",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Subtract three melee results from all army rolls at that terrain until the beginning of your next turn.",
        element="AIR",
    ),
    "WILDING": SpellModel(
        name="Wilding",
        species="Feral",
        cost=3,
        reserves=True,
        cantrip=False,
        effect="Target any army. The target army may double the melee and save results of any one unit until the beginning of your next turn. Select the unit to double its results after the army makes each roll.",
        element="AIR",
    ),
    "WIND_WALK": SpellModel(
        name="Wind Walk",
        species="Any",
        cost=4,
        reserves=True,
        cantrip=False,
        effect="Target any army. Add four maneuver results to the target's rolls until the beginning of your next turn.",
        element="AIR",
    ),
    "FIELDS_OF_ICE": SpellModel(
        name="Fields of Ice",
        species="Frostwings",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Subtract four maneuver results from all army rolls at that terrain until the beginning of your next turn. Ties in maneuver rolls at that terrain are won by the counter-maneuvering army while the terrain is under the effect of Fields of Ice.",
        element="AIR",
    ),
    "MIRAGE": SpellModel(
        name="Mirage",
        species="Firewalkers",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target up to five health-worth of units at any terrain. The targets make a save roll. Those that do not generate a save result are moved to their Reserve Area.",
        element="AIR",
    ),
    "LIGHTNING_STRIKE": SpellModel(
        name="Lightning Strike",
        species="Any",
        cost=6,
        reserves=False,
        cantrip=False,
        effect="Target any opposing unit. The target makes a save roll. If it does not generate a save result, it is killed. A unit may not be targeted by more than one Lightning Strike per magic action.",
        element="AIR",
    ),
}

# Death element spells
DEATH_SPELLS = {
    "PALSY": SpellModel(
        name="Palsy",
        species="Any",
        cost=2,
        reserves=False,
        cantrip=True,
        effect="Target any opposing army. Subtract one result from the target's non-maneuver rolls until the beginning of your next turn.",
        element="DEATH",
    ),
    "DECAY": SpellModel(
        name="Decay",
        species="Goblins",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any opposing army. Subtract two melee results from the target's rolls until the beginning of your next turn.",
        element="DEATH",
    ),
    "EVIL_EYE": SpellModel(
        name="Evil Eye",
        species="Undead",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any opposing army. Subtract two save results from the target's rolls until the beginning of your next turn.",
        element="DEATH",
    ),
    "MAGIC_DRAIN": SpellModel(
        name="Magic Drain",
        species="Frostwings",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Subtract two magic results from all army rolls at that terrain until the beginning of your next turn.",
        element="DEATH",
    ),
    "RESTLESS_DEAD": SpellModel(
        name="Restless Dead",
        species="Undead",
        cost=3,
        reserves=True,
        cantrip=True,
        effect="Target any army. Add three maneuver results to the target's rolls until the beginning of your next turn.",
        element="DEATH",
    ),
    "SWAMP_FEVER": SpellModel(
        name="Swamp Fever",
        species="Swamp Stalkers",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target up to three health-worth of units in an opposing army. Roll the targets. If they roll an ID icon, they are killed. Any units killed by Swamp Fever make a second roll. If they roll an ID icon they are buried.",
        element="DEATH",
    ),
    "FINGER_OF_DEATH": SpellModel(
        name="Finger of Death",
        species="Any",
        cost=4,
        reserves=False,
        cantrip=False,
        effect="Target any opposing unit. Inflict one point of damage on the target with no save possible.",
        element="DEATH",
    ),
    "NECROMANTIC_WAVE": SpellModel(
        name="Necromantic Wave",
        species="Lava Elves",
        cost=5,
        reserves=True,
        cantrip=False,
        effect="Target any army. All units in the target army may count magic results as if they were melee or missile results until the beginning of your next turn.",
        element="DEATH",
    ),
    "EXHUME": SpellModel(
        name="Exhume",
        species="Undead",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target up to three health-worth of units in an opposing player's DUA. The targets make a save roll. If the targets do not generate a save result they are buried. You may return units, up to the health-worth of units buried in this way, to the casting army from your DUA.",
        element="DEATH",
    ),
    "OPEN_GRAVE": SpellModel(
        name="Open Grave",
        species="Undead",
        cost=5,
        reserves=True,
        cantrip=False,
        effect="Target any army. Until the beginning of your next turn, units in the target army that are killed following a save roll by any army-targeting effects (including melee and missile damage) go to their owner's Reserve Area instead of the DUA. If no save roll is possible when units are killed, Open Grave does nothing.",
        element="DEATH",
    ),
    "SOILED_GROUND": SpellModel(
        name="Soiled Ground",
        species="Any",
        cost=6,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Until the beginning of your next turn, any unit killed at that terrain that goes into the DUA must make a save roll. Those that do not generate a save result are buried.",
        element="DEATH",
    ),
}

# Earth element spells
EARTH_SPELLS = {
    "STONE_SKIN": SpellModel(
        name="Stone Skin",
        species="Any",
        cost=2,
        reserves=True,
        cantrip=True,
        effect="Target any army. Add one save result to the target's rolls until the beginning of your next turn.",
        element="EARTH",
    ),
    "PATH": SpellModel(
        name="Path",
        species="Any",
        cost=4,
        reserves=True,
        cantrip=False,
        effect="Target one of your units at a terrain. Move the target to any other terrain where you have an army.",
        element="EARTH",
    ),
    "BERSERKER_RAGE": SpellModel(
        name="Berserker Rage",
        species="Feral",
        cost=5,
        reserves=True,
        cantrip=False,
        effect="Target an army containing at least one Feral unit. All Feral units in the target army may count save results as if they were melee results during all counter-attacks, until the beginning of your next turn.",
        element="EARTH",
    ),
    "HIGHER_GROUND": SpellModel(
        name="Higher Ground",
        species="Dwarves",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any opposing army. Subtract five melee results from the target's rolls until the beginning of your next turn.",
        element="EARTH",
    ),
    "SCENT_OF_FEAR": SpellModel(
        name="Scent of Fear",
        species="Goblins",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target up to three health-worth of opposing units at any terrain. The target units are moved to their Reserve Area.",
        element="EARTH",
    ),
    "WALL_OF_THORNS": SpellModel(
        name="Wall of Thorns",
        species="Treefolk",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any terrain not at its eighth face. Any army that successfully maneuvers that terrain takes six points of damage. The army makes a melee roll instead of a save roll. Reduce the damage taken by the number of melee results generated. This effect lasts until the beginning of your next turn.",
        element="EARTH",
    ),
    "TRANSMUTE_ROCK_TO_MUD": SpellModel(
        name="Transmute Rock to Mud",
        species="Any",
        cost=6,
        reserves=False,
        cantrip=False,
        effect="Target any opposing army. Subtract six maneuver results from the target's rolls until the beginning of your next turn.",
        element="EARTH",
    ),
}

# Fire element spells
FIRE_SPELLS = {
    "ASH_STORM": SpellModel(
        name="Ash Storm",
        species="Any",
        cost=2,
        reserves=False,
        cantrip=True,
        effect="Target any terrain. Subtract one result from all army rolls at that terrain until the beginning of your next turn.",
        element="FIRE",
    ),
    "FEARFUL_FLAMES": SpellModel(
        name="Fearful Flames",
        species="Lava Elves",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any opposing unit. Inflict one point of damage on the target. If the target unit saves against the damage, the target unit makes a second save roll. Unless the target unit gets a save result, the target unit flees to reserves.",
        element="FIRE",
    ),
    "FIREBOLT": SpellModel(
        name="Firebolt",
        species="Dwarves",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any opposing unit. Inflict one point of damage on the target.",
        element="FIRE",
    ),
    "FIRESTORM": SpellModel(
        name="Firestorm",
        species="Scalders",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Inflict two points of damage on each army at that terrain.",
        element="FIRE",
    ),
    "FLASHFIRE": SpellModel(
        name="Flashfire",
        species="Firewalkers",
        cost=3,
        reserves=True,
        cantrip=True,
        effect="Target any army. During any non-maneuver army roll, the target's owner may re-roll any one unit in the target army once, ignoring the previous result. This effect lasts until the beginning of your next turn.",
        element="FIRE",
    ),
    "FIERY_WEAPON": SpellModel(
        name="Fiery Weapon",
        species="Any",
        cost=4,
        reserves=True,
        cantrip=False,
        effect="Target any army. Add two melee or missile results to any roll the target makes until the beginning of your next turn.",
        element="FIRE",
    ),
    "DANCING_LIGHTS": SpellModel(
        name="Dancing Lights",
        species="Any",
        cost=6,
        reserves=False,
        cantrip=False,
        effect="Target any opposing army. Subtract six melee results from the target's rolls until the beginning of your next turn.",
        element="FIRE",
    ),
}

# Water element spells
WATER_SPELLS = {
    "WATERY_DOUBLE": SpellModel(
        name="Watery Double",
        species="Any",
        cost=2,
        reserves=True,
        cantrip=True,
        effect="Target any army. Add one save result to the target's rolls until the beginning of your next turn.",
        element="WATER",
    ),
    "ACCELERATED_GROWTH": SpellModel(
        name="Accelerated Growth",
        species="Treefolk",
        cost=3,
        reserves=True,
        cantrip=True,
        effect="Target your DUA. When a two (or greater) health Treefolk unit is killed, you may instead exchange it with a one health Treefolk unit from your DUA. This effect lasts until the beginning of your next turn.",
        element="WATER",
    ),
    "FLASH_FLOOD": SpellModel(
        name="Flash Flood",
        species="Any",
        cost=4,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Reduce that terrain one step unless an opposing army at that terrain generates at least six maneuver results. A terrain may never be reduced by more than one step during a player's turn from the effects of Flash Flood.",
        element="WATER",
    ),
    "DELUGE": SpellModel(
        name="Deluge",
        species="Coral Elves",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Subtract three maneuver and three missile results from all army rolls at that terrain until the beginning of your next turn.",
        element="WATER",
    ),
    "MIRE": SpellModel(
        name="Mire",
        species="Swamp Stalkers",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Until the beginning of your next turn, any army marching at that terrain must first make a maneuver roll. The marching player then selects health-worth of units up to the maneuver results generated by this first roll. The army uses only those units, and items they carry, for any rolls in the march for both the maneuver step and the action step.",
        element="WATER",
    ),
    "TIDAL_WAVE": SpellModel(
        name="Tidal Wave",
        species="Scalders",
        cost=5,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Each army at that terrain takes four points of damage, and makes a combination save and maneuver roll. For this special combination roll, only effects that generate normal save and maneuver results count. The terrain is reduced one step unless an army generates at least four maneuver results. A terrain may never be reduced by more than one step during a player's turn from the effects of Tidal Wave.",
        element="WATER",
    ),
    "WALL_OF_FOG": SpellModel(
        name="Wall of Fog",
        species="Any",
        cost=6,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Subtract six missile results from any missile attack targeting an army at that terrain until the beginning of your next turn.",
        element="WATER",
    ),
}

# Elemental spells (any element)
ELEMENTAL_SPELLS = {
    "EVOLVE_DRAGONKIN": SpellModel(
        name="Evolve Dragonkin",
        species="Eldarim",
        cost=3,
        reserves=True,
        cantrip=False,
        effect="Target one of your Dragonkin units that matches the element of magic used to cast this spell. The target is promoted one health-worth.",
        element="ELEMENTAL",
    ),
    "RESURRECT_DEAD": SpellModel(
        name="Resurrect Dead",
        species="Any",
        cost=3,
        reserves=True,
        cantrip=False,
        effect="Target one health-worth of units in your DUA that contains the element of magic used to cast this spell. Return the targets to the casting army. Magic of any one element (or Ivory) may be used to resurrect Amazons. Multiple casting of this spell targeting a single unit must all use the same element of magic.",
        element="ELEMENTAL",
    ),
    "ESFAHS_GIFT": SpellModel(
        name="Esfah's Gift",
        species="Amazons",
        cost=3,
        reserves=True,
        cantrip=True,
        effect="Target a minor terrain in your BUA. Move that terrain to your summoning pool.",
        element="ELEMENTAL",
    ),
    "SUMMON_DRAGONKIN": SpellModel(
        name="Summon Dragonkin",
        species="Any",
        cost=3,
        reserves=False,
        cantrip=False,
        effect="Target one health-worth of Dragonkin units in your Summoning Pool that match the element of magic used to cast this spell. The targets join the casting army.",
        element="ELEMENTAL",
    ),
    "RALLY": SpellModel(
        name="Rally",
        species="Amazons",
        cost=5,
        reserves=True,
        cantrip=False,
        effect="Target up to three of your Amazon units at a terrain. Move those units to any other terrain where you have at least one Amazon unit.",
        element="ELEMENTAL",
    ),
    "RISE_OF_THE_ELDARIM": SpellModel(
        name="Rise of the Eldarim",
        species="Eldarim",
        cost=5,
        reserves=True,
        cantrip=False,
        effect="Target any Eldarim unit that matches the element of magic used to cast this spell. The target is promoted one health-worth.",
        element="ELEMENTAL",
    ),
    "SUMMON_DRAGON": SpellModel(
        name="Summon Dragon",
        species="Any",
        cost=7,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Summon one dragon that contains the element used to cast this spell from any Summoning Pool or terrain to the target terrain. Magic of any one element may be used to summon an Ivory or Ivory Hybrid Dragon from any Summoning Pool to the target terrain.",
        element="ELEMENTAL",
    ),
    "SUMMON_WHITE_DRAGON": SpellModel(
        name="Summon White Dragon",
        species="Any",
        cost=14,
        reserves=False,
        cantrip=False,
        effect="Target any terrain. Summon one White Dragon from any Summoning Pool or terrain to the target terrain. Any combination of magic elements may be used to cast this spell.",
        element="ELEMENTAL",
    ),
}

# Combined spell data organized by element
SPELLS_BY_ELEMENT = {
    "AIR": AIR_SPELLS,
    "DEATH": DEATH_SPELLS,
    "EARTH": EARTH_SPELLS,
    "FIRE": FIRE_SPELLS,
    "WATER": WATER_SPELLS,
    "ELEMENTAL": ELEMENTAL_SPELLS,
}

# All spells in a single dictionary for easy access
ALL_SPELLS = {}
for element_spells in SPELLS_BY_ELEMENT.values():
    ALL_SPELLS.update(element_spells)


# Helper functions for spell data access
def get_spell(spell_name: str) -> Optional[SpellModel]:
    """Get a specific spell by name (case-insensitive lookup)."""
    spell_key = spell_name.upper().replace(" ", "_")
    return ALL_SPELLS.get(spell_key)


def get_spells_by_element(element: str) -> Dict[str, SpellModel]:
    """Get all spells for a specific element."""
    return SPELLS_BY_ELEMENT.get(element.upper(), {})


def get_spells_for_species(species_name: str) -> List[SpellModel]:
    """Get all spells available to a specific species."""
    available_spells = []
    for spell in ALL_SPELLS.values():
        if spell.is_available_to_species(species_name):
            available_spells.append(spell)
    return available_spells


def get_cantrip_spells() -> List[SpellModel]:
    """Get all cantrip spells."""
    return [spell for spell in ALL_SPELLS.values() if spell.is_cantrip()]


def get_spells_by_cost(cost: int) -> List[SpellModel]:
    """Get all spells with a specific cost."""
    return [spell for spell in ALL_SPELLS.values() if spell.cost == cost]


def get_reserve_spells() -> List[SpellModel]:
    """Get all spells that can be cast from reserves."""
    return [spell for spell in ALL_SPELLS.values() if spell.can_be_cast_from_reserves()]


def search_spells_by_effect(search_term: str) -> List[SpellModel]:
    """Search for spells by effect description (case-insensitive)."""
    search_lower = search_term.lower()
    results = []
    for spell in ALL_SPELLS.values():
        if search_lower in spell.effect.lower():
            results.append(spell)
    return results


def get_all_spell_names() -> List[str]:
    """Get a list of all spell names."""
    return [spell.name for spell in ALL_SPELLS.values()]


def get_spells_by_element_and_species(element: str, species: str) -> List[SpellModel]:
    """Get spells for a specific element that are available to a specific species."""
    element_spells = get_spells_by_element(element)
    return [spell for spell in element_spells.values() if spell.is_available_to_species(species)]


def validate_spell_elements() -> bool:
    """Validate that all spell elements are valid (match ELEMENT_DATA keys)."""
    valid_elements = set(ELEMENT_DATA.keys())
    valid_elements.add("ELEMENTAL")  # Special case for elemental spells

    for spell_name, spell in ALL_SPELLS.items():
        if spell.element and spell.element not in valid_elements:
            print(f"ERROR: Spell '{spell_name}' has invalid element '{spell.element}'")
            return False

    total_spells = len(ALL_SPELLS)
    total_by_element = sum(len(spells) for spells in SPELLS_BY_ELEMENT.values())

    if total_spells != total_by_element:
        print(f"ERROR: Mismatch in spell counts: {total_spells} total vs {total_by_element} by element")
        return False

    print(f"✓ All {total_spells} spells validated successfully")
    return True


def get_spell_statistics() -> Dict[str, Any]:
    """Get statistics about the spell collection."""
    cost_distribution: Dict[int, int] = {}

    # Calculate cost distribution
    for spell in ALL_SPELLS.values():
        cost = spell.cost
        cost_distribution[cost] = cost_distribution.get(cost, 0) + 1

    stats = {
        "total_spells": len(ALL_SPELLS),
        "spells_by_element": {element: len(spells) for element, spells in SPELLS_BY_ELEMENT.items()},
        "cantrip_count": len(get_cantrip_spells()),
        "reserve_count": len(get_reserve_spells()),
        "species_restricted": len([s for s in ALL_SPELLS.values() if s.species != "Any"]),
        "universal_spells": len([s for s in ALL_SPELLS.values() if s.species == "Any"]),
        "cost_distribution": cost_distribution,
    }

    return stats
