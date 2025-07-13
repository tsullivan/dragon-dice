# models/species_model.py
from typing import Any, Dict, List, Optional, Tuple

from models.element_model import ELEMENT_DATA
from utils.field_access import strict_get, strict_get_optional


class SpeciesAbility:
    """Represents a species-specific ability."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"SpeciesAbility(name='{self.name}')"

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "SpeciesAbility":
        return cls(
            name=strict_get(data, "name", "SpeciesAbility"),
            description=strict_get(data, "description", "SpeciesAbility"),
        )


def _get_element_tuple(element_name: str):
    """Convert element name to (icon, color_name) tuple."""
    element = ELEMENT_DATA[element_name]
    return (element.icon, element.color_name)


class SpeciesModel:
    def __init__(
        self,
        name: str,
        display_name: str,
        elements: List[str],
        element_colors: List[Tuple[str, str]],
        description: str,
        abilities: Optional[List[SpeciesAbility]] = None,  # Dragonkin do not have their own Species Abilities
    ):
        self.name = name
        self.display_name = display_name
        self.elements = elements  # Element names like ["DEATH", "EARTH"]
        self.element_colors = element_colors  # [(icon, color_name), ...]
        self.description = description
        self.abilities = abilities or []  # List of species abilities

    def __repr__(self):
        elements_str = ", ".join([f"{icon} {color}" for icon, color in self.element_colors])
        return f"SpeciesModel(name='{self.name}', elements=[{elements_str}])"

    def get_element_icons(self) -> List[str]:
        """Get just the element icons for this species."""
        return [icon for icon, _ in self.element_colors]

    def get_element_names(self) -> List[str]:
        """Get just the element color names for this species."""
        return [color_name for _, color_name in self.element_colors]

    def has_element(self, element: str) -> bool:
        """Check if this species has a specific element."""
        return element.upper() in self.elements

    def get_abilities(self) -> List[SpeciesAbility]:
        """Get the list of species abilities."""
        return self.abilities

    def get_ability_by_name(self, ability_name: str) -> Optional[SpeciesAbility]:
        """Get a specific ability by name."""
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "elements": self.elements,
            "element_colors": self.element_colors,
            "description": self.description,
            "abilities": [ability.to_dict() for ability in self.abilities],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpeciesModel":
        abilities_data = strict_get_optional(data, "abilities", [])
        abilities = [SpeciesAbility.from_dict(ability_dict) for ability_dict in abilities_data]
        return cls(
            name=strict_get(data, "name", "SpeciesModel"),
            display_name=strict_get_optional(data, "display_name", ""),
            elements=strict_get(data, "elements", "SpeciesModel"),
            element_colors=strict_get_optional(data, "element_colors", []),
            description=strict_get(data, "description", "SpeciesModel"),
            abilities=abilities,
        )


# Species definitions based on Dragon Dice rules
SPECIES_DATA = {
    "AMAZON": SpeciesModel(
        name="Amazon",
        display_name="Amazons",
        elements=["IVORY"],
        element_colors=[_get_element_tuple("IVORY")],
        description="No elements (ivory)",
        abilities=[
            SpeciesAbility(
                name="Javelin Charge",
                description="During a march, instead of taking the maneuver step, you may bury a minor terrain the marching army controls. Amazons in that army may then count maneuver results as if they were missile results during a missile action this turn.",
            ),
            SpeciesAbility(
                name="Kukri Charge",
                description="During a march, instead of taking the maneuver step, you may bury a minor terrain the marching army controls. Amazons in that army may then count maneuver results as if they were melee results during a melee action this turn.",
            ),
            SpeciesAbility(
                name="Terrain Harmony",
                description="Amazon units generate magic results matching the elements of the terrain where they are located. Amazon units in the Reserves Area generate Ivory magic, which may only be used to cast Elemental spells.",
            ),
        ],
    ),
    "CORAL_ELF": SpeciesModel(
        name="Coral Elf",
        display_name="Coral Elves",
        elements=["AIR", "WATER"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("WATER")],
        description="Air & Water (blue & green)",
        abilities=[
            SpeciesAbility(
                name="Coastal Dodge",
                description="When at a terrain that contains water, Coral Elves may count maneuver results as if they were save results.",
            ),
            SpeciesAbility(
                name="Defensive Volley",
                description="When at a terrain that contains air, Coral Elves units may counter-attack against a missile action. Follow the same process used for a regular melee counter-attack, using missile results instead of melee results.",
            ),
        ],
    ),
    "DWARF": SpeciesModel(
        name="Dwarf",
        display_name="Dwarves",
        elements=["FIRE", "EARTH"],
        element_colors=[_get_element_tuple("FIRE"), _get_element_tuple("EARTH")],
        description="Fire & Earth (red & yellow)",
        abilities=[
            SpeciesAbility(
                name="Mountain Mastery",
                description="When at a terrain that contains earth, Dwarves may count melee results as if they were maneuver results.",
            ),
            SpeciesAbility(
                name="Dwarven Might",
                description="When at a terrain that contains fire, Dwarves may count save results as if they were melee results when rolling for a counter-attack.",
            ),
        ],
    ),
    "FERAL": SpeciesModel(
        name="Feral",
        display_name="Feral",
        elements=["AIR", "EARTH"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("EARTH")],
        description="Air & Earth (blue & yellow)",
        abilities=[
            SpeciesAbility(
                name="Feralization",
                description="During the Species Abilities Phase, each of your armies containing at least one Feral unit at a terrain that contains earth or air may recruit a small (1 health) Feral unit to, or promote one Feral unit in, the army.",
            ),
            SpeciesAbility(
                name="Stampede",
                description="When at a terrain that contains both earth and air, Feral units may count maneuver results as if they were melee results during a counter‑attack.",
            ),
        ],
    ),
    "FIREWALKER": SpeciesModel(
        name="Firewalker",
        display_name="Firewalkers",
        elements=["AIR", "FIRE"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("FIRE")],
        description="Air & Fire (blue & red)",
        abilities=[
            SpeciesAbility(
                name="Air Flight",
                description="During the Retreat Step of the Reserves Phase, Firewalker units may move from any terrain that contains air to any other terrain that contains air and where you have at least one Firewalker unit.",
            ),
            SpeciesAbility(
                name="Flaming Shields",
                description="When at a terrain that contains fire, Firewalkers may count save results as if they were melee results. Flaming Shields does not apply when making a counter-attack.",
            ),
        ],
    ),
    "FROSTWING": SpeciesModel(
        name="Frostwing",
        display_name="Frostwings",
        elements=["DEATH", "AIR"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("AIR")],
        description="Death & Air (black & blue)",
        abilities=[
            SpeciesAbility(
                name="Winter's Fortitude",
                description="During the Species Abilities Phase, if you have at least one Frostwing unit at a terrain that contains air, you may move one Frostwing unit of your choice from your BUA to your DUA.",
            ),
            SpeciesAbility(
                name="Magic Negation",
                description="When an opponent takes a magic action at a terrain containing Frostwings, the Frostwing units may make a magic negation roll. Roll the Frostwing units before the opponent totals their magic results. Subtract the magic results generated by the Frostwing units from the opponent's results.\n* The number of magic results that may be subtracted is equal to the number of Frostwing units in the Frostwing player's DUA, up to a maximum of five ⚰️ (see page 21).",
            ),
        ],
    ),
    "GOBLIN": SpeciesModel(
        name="Goblin",
        display_name="Goblins",
        elements=["DEATH", "EARTH"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("EARTH")],
        description="Death & Earth (black & yellow)",
        abilities=[
            SpeciesAbility(
                name="Swamp Mastery",
                description="When at a terrain that contains earth, Goblins may count melee results as if they were maneuver results.",
            ),
            SpeciesAbility(
                name="Foul Stench",
                description="When an army containing Goblins takes a melee action, the opposing player must select a number of their units after they have resolved their save roll.\n* The selected units cannot perform a counter-attack during this melee action. The number of units that must be selected in this way is equal to the number of Goblin units in the Goblin player's DUA, up to a maximum of three ⚰️ (see page 21).",
            ),
        ],
    ),
    "LAVA_ELF": SpeciesModel(
        name="Lava Elf",
        display_name="Lava Elves",
        elements=["DEATH", "FIRE"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("FIRE")],
        description="Death & Fire (black & red)",
        abilities=[
            SpeciesAbility(
                name="Volcanic Adaptation",
                description="When at a terrain that contains fire, Lava Elves may count maneuver results as if they were save results.",
            ),
            SpeciesAbility(
                name="Cursed Bullets",
                description="When targeting an army at the same terrain with a missile attack, Lava Elves missile results inflict damage that may only be reduced by save results generated by spells.\n* The number of missile results that may be effected in this way is equal to the number of Lava Elves units in the Lava Elves player's DUA, up to a maximum of three ⚰️ (see page 21).",
            ),
        ],
    ),
    "SCALDER": SpeciesModel(
        name="Scalder",
        display_name="Scalders",
        elements=["WATER", "FIRE"],
        element_colors=[_get_element_tuple("WATER"), _get_element_tuple("FIRE")],
        description="Water & Fire (green & red)",
        abilities=[
            SpeciesAbility(
                name="Scorching Touch",
                description="When at a terrain that contains fire, Scalders making a save roll against a melee attack inflict one point of damage on the attacking army for each save result rolled. Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            ),
            SpeciesAbility(
                name="Intangibility",
                description="When at a terrain that contains water, Scalders may count maneuver results as if they were save results against missile damage.",
            ),
        ],
    ),
    "SWAMP_STALKER": SpeciesModel(
        name="Swamp Stalker",
        display_name="Swamp Stalkers",
        elements=["DEATH", "WATER"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("WATER")],
        description="Death & Water (black & green)",
        abilities=[
            SpeciesAbility(
                name="Born of the Swamp",
                description="When at a terrain that contains water, Swamp Stalkers may count maneuver results as if they were save results.",
            ),
            SpeciesAbility(
                name="Mutate",
                description="During the Species Abilities Phase, you may attempt to Mutate providing the following criteria are met:\n- An opposing player must have at least one unit in their Reserves Area.\n- You must have at least one army containing a Swamp Stalker at a terrain.\n- You must have at least one Swamp Stalker unit in your DUA (or a Deadlands minor terrain in play).\n* Target units in an opponent's Reserve Area to make a save roll. Units that do not generate a save result are killed. One of your armies at a terrain that contains at least one Swamp Stalker unit can then recruit or promote Swamp Stalker units up to the health-worth that were killed this way.\n* The number of units that may be targeted in this way is equal to the number of Swamp Stalker units in the Swamp Stalker player's DUA, up to a maximum of one ⚰️ (see page 21).",
            ),
        ],
    ),
    "TREEFOLK": SpeciesModel(
        name="Treefolk",
        display_name="Treefolk",
        elements=["WATER", "EARTH"],
        element_colors=[_get_element_tuple("WATER"), _get_element_tuple("EARTH")],
        description="Water & Earth (green & yellow)",
        abilities=[
            SpeciesAbility(
                name="Rapid Growth",
                description="When at a terrain that contains earth, Treefolk units that do not roll an SAI result may be re-rolled once when making a counter-maneuver. The previous results are ignored. Any units you wish to re-roll in this way must be selected and re-rolled together.",
            ),
            SpeciesAbility(
                name="Replanting",
                description="When at a terrain that contains water, Treefolk units that are killed should be rolled before being moved to the DUA. Any units that roll an ID icon are instead moved to your Reserve Area.",
            ),
        ],
    ),
    "UNDEAD": SpeciesModel(
        name="Undead",
        display_name="Undead",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Death only (black)",
        abilities=[
            SpeciesAbility(
                name="Stepped Damage",
                description="When an Undead unit is killed you may instead exchange it with an Undead unit of lesser health from your DUA.",
            ),
            SpeciesAbility(
                name="Bone Magic",
                description="When an army containing Undead takes a magic action, each Undead unit that rolls at least one non-ID magic result may add one additional magic result.\n* The number of magic results that may be added in this way is equal to the number of Undead units in the Undead player's DUA, up to a maximum of four ⚰️ (see page 21).",
            ),
        ],
    ),
}

ELDARIIM_ABILITIES = [
    SpeciesAbility(
        name="Resist Fear",
        description="Dragonkin units up to the total health of Eldarim in their army ignore any restrictions that prevent them from rolling during a dragon attack.",
    ),
    SpeciesAbility(
        name="Dragonkin Handlers",
        description="During the Species Abilities Phase, select an army that contains at least one Eldarim unit at a terrain. Move a small (1 health) Dragonkin unit from the Summoning Pool to the army, or promote one Dragonkin unit in the army. Moved or promoted units must match an element of the terrain. This ability may only be used if the total health-worth of Dragonkin after the exchange is not greater than the total healthworth of Eldarim in that army. ",
    ),
]

# Single-element Eldarim subspecies
ELDARIM_SUBSPECIES = {
    "ELDARIM_AIR": SpeciesModel(
        name="Eldarim Air",
        display_name="Eldarim (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
        abilities=ELDARIIM_ABILITIES,
    ),
    "ELDARIM_DEATH": SpeciesModel(
        name="Eldarim Death",
        display_name="Eldarim (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
        abilities=ELDARIIM_ABILITIES,
    ),
    "ELDARIM_EARTH": SpeciesModel(
        name="Eldarim Earth",
        display_name="Eldarim (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
        abilities=ELDARIIM_ABILITIES,
    ),
    "ELDARIM_FIRE": SpeciesModel(
        name="Eldarim Fire",
        display_name="Eldarim (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
        abilities=ELDARIIM_ABILITIES,
    ),
    "ELDARIM_WATER": SpeciesModel(
        name="Eldarim Water",
        display_name="Eldarim (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
        abilities=ELDARIIM_ABILITIES,
    ),
}

# Multi-element Dragon species
DRAGON_SPECIES = {
    "DRAGONCRUSADER": SpeciesModel(
        name="Dragoncrusader",
        display_name="Dragoncrusaders",
        elements=["AIR", "DEATH", "EARTH", "FIRE", "WATER"],
        element_colors=[_get_element_tuple("WHITE")],
        description="All Elements (white)",
    ),
    "DRAGONLORD": SpeciesModel(
        name="Dragonlord",
        display_name="Dragonlords",
        elements=["AIR", "DEATH", "EARTH", "FIRE", "WATER"],
        element_colors=[_get_element_tuple("WHITE")],
        description="All Elements (white)",
    ),
    "DRAGONSLAYER": SpeciesModel(
        name="Dragonslayer",
        display_name="Dragonslayers",
        elements=["AIR", "DEATH", "EARTH", "FIRE", "WATER"],
        element_colors=[_get_element_tuple("WHITE")],
        description="All Elements (white)",
    ),
}

# Single-element Dragon subspecies
DRAGON_SUBSPECIES = {
    "DRAGONKIN_AIR": SpeciesModel(
        name="Dragonkin Air",
        display_name="Dragonkin (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
    ),
    "DRAGONKIN_DEATH": SpeciesModel(
        name="Dragonkin Death",
        display_name="Dragonkin (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
    ),
    "DRAGONKIN_EARTH": SpeciesModel(
        name="Dragonkin Earth",
        display_name="Dragonkin (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
    ),
    "DRAGONKIN_FIRE": SpeciesModel(
        name="Dragonkin Fire",
        display_name="Dragonkin (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
    ),
    "DRAGONKIN_WATER": SpeciesModel(
        name="Dragonkin Water",
        display_name="Dragonkin (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
    ),
    "DRAGONMASTER_AIR": SpeciesModel(
        name="Dragonmaster Air",
        display_name="Dragonmasters (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
    ),
    "DRAGONMASTER_DEATH": SpeciesModel(
        name="Dragonmaster Death",
        display_name="Dragonmasters (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
    ),
    "DRAGONMASTER_EARTH": SpeciesModel(
        name="Dragonmaster Earth",
        display_name="Dragonmasters (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
    ),
    "DRAGONMASTER_FIRE": SpeciesModel(
        name="Dragonmaster Fire",
        display_name="Dragonmasters (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
    ),
    "DRAGONMASTER_WATER": SpeciesModel(
        name="Dragonmaster Water",
        display_name="Dragonmasters (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
    ),
    "DRAGONHUNTER_AIR": SpeciesModel(
        name="Dragonhunter Air",
        display_name="Dragonhunters (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
    ),
    "DRAGONHUNTER_DEATH": SpeciesModel(
        name="Dragonhunter Death",
        display_name="Dragonhunters (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
    ),
    "DRAGONHUNTER_EARTH": SpeciesModel(
        name="Dragonhunter Earth",
        display_name="Dragonhunters (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
    ),
    "DRAGONHUNTER_FIRE": SpeciesModel(
        name="Dragonhunter Fire",
        display_name="Dragonhunters (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
    ),
    "DRAGONHUNTER_WATER": SpeciesModel(
        name="Dragonhunter Water",
        display_name="Dragonhunters (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
    ),
    "DRAGONZEALOT_AIR": SpeciesModel(
        name="Dragonzealot Air",
        display_name="Dragonzealots (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
    ),
    "DRAGONZEALOT_DEATH": SpeciesModel(
        name="Dragonzealot Death",
        display_name="Dragonzealots (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
    ),
    "DRAGONZEALOT_EARTH": SpeciesModel(
        name="Dragonzealot Earth",
        display_name="Dragonzealots (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
    ),
    "DRAGONZEALOT_FIRE": SpeciesModel(
        name="Dragonzealot Fire",
        display_name="Dragonzealots (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
    ),
    "DRAGONZEALOT_WATER": SpeciesModel(
        name="Dragonzealot Water",
        display_name="Dragonzealots (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
    ),
}

# Combined species data
ALL_SPECIES = {
    **SPECIES_DATA,
    **ELDARIM_SUBSPECIES,
    **DRAGON_SPECIES,
    **DRAGON_SUBSPECIES,
}


# Helper functions for species data access
def get_species(species_name: str) -> Optional[SpeciesModel]:
    """Get a specific species by name."""
    return ALL_SPECIES.get(species_name)


def get_species_by_element(element: str) -> List[SpeciesModel]:
    """Get all species that have a specific element."""
    element = element.upper()
    return [species for species in ALL_SPECIES.values() if species.has_element(element)]


def get_all_species_names() -> List[str]:
    """Get a list of all species names."""
    return list(ALL_SPECIES.keys())


def get_basic_species() -> Dict[str, SpeciesModel]:
    """Get only the basic species (not subspecies)."""
    return SPECIES_DATA


def get_eldarim_subspecies() -> Dict[str, SpeciesModel]:
    """Get all Eldarim subspecies."""
    return ELDARIM_SUBSPECIES


def get_dragon_species() -> Dict[str, SpeciesModel]:
    """Get all Dragon species."""
    return {**DRAGON_SPECIES, **DRAGON_SUBSPECIES}


def get_species_abilities(species_name: str) -> List[SpeciesAbility]:
    """Get all abilities for a specific species."""
    species = ALL_SPECIES.get(species_name)
    if species:
        return species.get_abilities()
    return []


def get_all_species_abilities() -> Dict[str, List[SpeciesAbility]]:
    """Get all abilities for all species."""
    return {name: species.get_abilities() for name, species in ALL_SPECIES.items()}


def search_abilities_by_name(ability_name: str) -> List[Tuple[str, SpeciesAbility]]:
    """Search for abilities by name across all species. Returns list of (species_name, ability) tuples."""
    results = []
    for species_name, species in ALL_SPECIES.items():
        for ability in species.get_abilities():
            if ability_name.lower() in ability.name.lower():
                results.append((species_name, ability))
    return results


def validate_species_elements() -> bool:
    """Validate that all species use valid elements from ELEMENT_DATA."""
    valid_elements = set(ELEMENT_DATA.keys())

    for species_name, species in ALL_SPECIES.items():
        for element in species.elements:
            if element not in valid_elements:
                print(f"ERROR: Species '{species_name}' has invalid element '{element}'")
                return False

        # Validate element_colors match elements (except for multi-element species using white)
        if species.elements == ["AIR", "DEATH", "EARTH", "FIRE", "WATER"]:
            # Multi-element species should use white
            if species.element_colors != [_get_element_tuple("WHITE")]:
                print(f"ERROR: Multi-element species '{species_name}' should use white icon")
                return False
        else:
            # Single/dual element species should have matching colors
            expected_colors = [_get_element_tuple(elem) for elem in species.elements]
            if species.element_colors != expected_colors:
                print(f"ERROR: Species '{species_name}' has mismatched element colors")
                return False

    print(f"✓ All {len(ALL_SPECIES)} species validated successfully")
    return True


def validate_species_abilities() -> bool:
    """Validate that all basic species have abilities defined."""
    species_without_abilities = []

    for species_name, species in SPECIES_DATA.items():
        if not species.get_abilities():
            species_without_abilities.append(species_name)

    if species_without_abilities:
        print(f"ERROR: Species without abilities: {species_without_abilities}")
        return False

    total_abilities = sum(len(species.get_abilities()) for species in SPECIES_DATA.values())
    print(f"✓ All {len(SPECIES_DATA)} basic species have abilities ({total_abilities} total abilities)")
    return True
