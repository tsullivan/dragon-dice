from typing import List, Tuple
from models.element_model import ELEMENT_ICONS


class Terrain:
    """
    Represents a terrain in the Dragon Dice game.
    Each terrain has a name, display name, elements, and element colors.
    """

    def __init__(
        self,
        name: str,
        display_name: str,
        elements: List[str],
        element_colors: List[str],
    ):
        self.name = name
        self.display_name = display_name
        self.elements = elements
        self.element_colors = element_colors

        # Validate elements
        if not 1 <= len(elements) <= 2:
            raise ValueError("Terrain must have one or two elements.")

        valid_elements = list(ELEMENT_ICONS.keys())
        for element in elements:
            if element not in valid_elements:
                raise ValueError(
                    f"Invalid element '{element}'. Must be one of {valid_elements}"
                )

        # Validate element colors match elements
        expected_colors = [ELEMENT_ICONS[elem][0] for elem in elements]
        if element_colors != expected_colors:
            raise ValueError(
                f"Element colors {element_colors} don't match elements {elements}"
            )

    def __str__(self) -> str:
        return f"{self.display_name} ({', '.join(self.get_element_names())})"

    def __repr__(self) -> str:
        return f"Terrain(name='{self.name}', display_name='{self.display_name}', elements={self.elements})"

    def get_element_names(self) -> List[str]:
        """Returns the element color names."""
        return [ELEMENT_ICONS[elem][1] for elem in self.elements]

    def get_element_icons(self) -> List[str]:
        """Returns the element icons."""
        return self.element_colors

    def get_color_string(self) -> str:
        """Returns combined element colors as a single string."""
        return "".join(self.element_colors)

    def has_element(self, element: str) -> bool:
        """Check if this terrain has a specific element."""
        return element.upper() in self.elements


# Terrain instances
TERRAIN_DATA = {
    "COASTLAND": Terrain(
        name="COASTLAND",
        display_name="Coastland",
        elements=["AIR", "WATER"],
        element_colors=[ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["WATER"][0]],
    ),
    "DEADLAND": Terrain(
        name="DEADLAND",
        display_name="Deadland",
        elements=["DEATH"],
        element_colors=[ELEMENT_ICONS["DEATH"][0]],
    ),
    "FLATLAND": Terrain(
        name="FLATLAND",
        display_name="Flatland",
        elements=["AIR", "EARTH"],
        element_colors=[ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["EARTH"][0]],
    ),
    "HIGHLAND": Terrain(
        name="HIGHLAND",
        display_name="Highland",
        elements=["FIRE", "EARTH"],
        element_colors=[ELEMENT_ICONS["FIRE"][0], ELEMENT_ICONS["EARTH"][0]],
    ),
    "SWAMPLAND": Terrain(
        name="SWAMPLAND",
        display_name="Swampland",
        elements=["WATER", "EARTH"],
        element_colors=[ELEMENT_ICONS["WATER"][0], ELEMENT_ICONS["EARTH"][0]],
    ),
    "FEYLAND": Terrain(
        name="FEYLAND",
        display_name="Feyland",
        elements=["WATER", "FIRE"],
        element_colors=[ELEMENT_ICONS["WATER"][0], ELEMENT_ICONS["FIRE"][0]],
    ),
    "WASTELAND": Terrain(
        name="WASTELAND",
        display_name="Wasteland",
        elements=["AIR", "FIRE"],
        element_colors=[ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["FIRE"][0]],
    ),
}


# Helper functions for terrain access
def get_terrain(terrain_name: str) -> Terrain:
    """Get a terrain by name."""
    terrain_key = terrain_name.upper()
    return TERRAIN_DATA.get(terrain_key)


def get_all_terrain_names() -> List[str]:
    """Get all terrain names."""
    return list(TERRAIN_DATA.keys())


def get_terrains_by_element(element: str) -> List[Terrain]:
    """Get all terrains that contain a specific element."""
    element = element.upper()
    return [
        terrain for terrain in TERRAIN_DATA.values() if terrain.has_element(element)
    ]


def validate_terrain_data() -> bool:
    """Validate all terrain data."""
    try:
        for terrain_name, terrain in TERRAIN_DATA.items():
            if not isinstance(terrain, Terrain):
                print(f"ERROR: {terrain_name} is not a Terrain instance")
                return False
            if terrain.name != terrain_name:
                print(f"ERROR: Terrain name mismatch: {terrain.name} != {terrain_name}")
                return False

        print(f"✓ All {len(TERRAIN_DATA)} terrains validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Terrain validation failed: {e}")
        return False


# Terrain utility functions
def get_terrain_icon(terrain_name: str) -> str:
    """Get terrain icon. Raises KeyError if terrain not found."""
    terrain = get_terrain(terrain_name)
    if not terrain:
        raise KeyError(
            f"Unknown terrain type: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}"
        )
    return terrain.get_color_string()


def get_terrain_or_location_icon(name: str) -> str:
    """Get icon for terrain type or location, checking both maps. Raises KeyError if not found."""
    from models.location_model import LOCATION_DATA

    name_key = name.upper()

    # Check terrain types first - return color icons
    terrain = get_terrain(name_key)
    if terrain:
        return terrain.get_color_string()

    # Then check locations - use icon property for locations
    if name_key in LOCATION_DATA:
        return LOCATION_DATA[name_key].icon

    # If not found in either, raise error
    valid_names = get_all_terrain_names() + list(LOCATION_DATA.keys())
    raise KeyError(
        f"Unknown terrain or location: '{name}'. Valid options: {valid_names}"
    )


def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon display_name' format for display."""
    terrain = get_terrain(terrain_name)
    if not terrain:
        raise KeyError(
            f"Unknown terrain type: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}"
        )
    return f"{terrain.get_color_string()} {terrain.display_name}"
