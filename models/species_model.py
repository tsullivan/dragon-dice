# models/species_model.py
from typing import Any, Dict, List, Tuple

from models.element_model import ELEMENT_DATA


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
        description: str = "",
    ):
        self.name = name
        self.display_name = display_name
        self.elements = elements  # Element names like ["DEATH", "EARTH"]
        self.element_colors = element_colors  # [(icon, color_name), ...]
        self.description = description

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "elements": self.elements,
            "element_colors": self.element_colors,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpeciesModel":
        return cls(
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            elements=data.get("elements", []),
            element_colors=data.get("element_colors", []),
            description=data.get("description", ""),
        )


# Species definitions based on Dragon Dice rules
SPECIES_DATA = {
    "AMAZON": SpeciesModel(
        name="Amazon",
        display_name="Amazons",
        elements=["IVORY"],
        element_colors=[_get_element_tuple("IVORY")],
        description="No elements (ivory)",
    ),
    "CORAL_ELF": SpeciesModel(
        name="Coral Elf",
        display_name="Coral Elves",
        elements=["AIR", "WATER"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("WATER")],
        description="Air & Water (blue & green)",
    ),
    "DWARF": SpeciesModel(
        name="Dwarf",
        display_name="Dwarves",
        elements=["FIRE", "EARTH"],
        element_colors=[_get_element_tuple("FIRE"), _get_element_tuple("EARTH")],
        description="Fire & Earth (red & yellow)",
    ),
    "FERAL": SpeciesModel(
        name="Feral",
        display_name="Feral",
        elements=["AIR", "EARTH"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("EARTH")],
        description="Air & Earth (blue & yellow)",
    ),
    "FIREWALKER": SpeciesModel(
        name="Firewalker",
        display_name="Firewalkers",
        elements=["AIR", "FIRE"],
        element_colors=[_get_element_tuple("AIR"), _get_element_tuple("FIRE")],
        description="Air & Fire (blue & red)",
    ),
    "FROSTWING": SpeciesModel(
        name="Frostwing",
        display_name="Frostwings",
        elements=["DEATH", "AIR"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("AIR")],
        description="Death & Air (black & blue)",
    ),
    "GOBLIN": SpeciesModel(
        name="Goblin",
        display_name="Goblins",
        elements=["DEATH", "EARTH"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("EARTH")],
        description="Death & Earth (black & yellow)",
    ),
    "LAVA_ELF": SpeciesModel(
        name="Lava Elf",
        display_name="Lava Elves",
        elements=["DEATH", "FIRE"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("FIRE")],
        description="Death & Fire (black & red)",
    ),
    "SCALDER": SpeciesModel(
        name="Scalder",
        display_name="Scalders",
        elements=["WATER", "FIRE"],
        element_colors=[_get_element_tuple("WATER"), _get_element_tuple("FIRE")],
        description="Water & Fire (green & red)",
    ),
    "SWAMP_STALKER": SpeciesModel(
        name="Swamp Stalker",
        display_name="Swamp Stalkers",
        elements=["DEATH", "WATER"],
        element_colors=[_get_element_tuple("DEATH"), _get_element_tuple("WATER")],
        description="Death & Water (black & green)",
    ),
    "TREEFOLK": SpeciesModel(
        name="Treefolk",
        display_name="Treefolk",
        elements=["WATER", "EARTH"],
        element_colors=[_get_element_tuple("WATER"), _get_element_tuple("EARTH")],
        description="Water & Earth (green & yellow)",
    ),
    "UNDEAD": SpeciesModel(
        name="Undead",
        display_name="Undead",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Death only (black)",
    ),
}

# Single-element Eldarim subspecies
ELDARIM_SUBSPECIES = {
    "ELDARIM_AIR": SpeciesModel(
        name="Eldarim Air",
        display_name="Eldarim (Air)",
        elements=["AIR"],
        element_colors=[_get_element_tuple("AIR")],
        description="Single element - Air (blue)",
    ),
    "ELDARIM_DEATH": SpeciesModel(
        name="Eldarim Death",
        display_name="Eldarim (Death)",
        elements=["DEATH"],
        element_colors=[_get_element_tuple("DEATH")],
        description="Single element - Death (black)",
    ),
    "ELDARIM_EARTH": SpeciesModel(
        name="Eldarim Earth",
        display_name="Eldarim (Earth)",
        elements=["EARTH"],
        element_colors=[_get_element_tuple("EARTH")],
        description="Single element - Earth (yellow)",
    ),
    "ELDARIM_FIRE": SpeciesModel(
        name="Eldarim Fire",
        display_name="Eldarim (Fire)",
        elements=["FIRE"],
        element_colors=[_get_element_tuple("FIRE")],
        description="Single element - Fire (red)",
    ),
    "ELDARIM_WATER": SpeciesModel(
        name="Eldarim Water",
        display_name="Eldarim (Water)",
        elements=["WATER"],
        element_colors=[_get_element_tuple("WATER")],
        description="Single element - Water (green)",
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
def get_species(species_name: str) -> SpeciesModel:
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
