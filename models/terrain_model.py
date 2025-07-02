from typing import Dict, List, Optional

from models.element_model import ELEMENT_DATA


class TerrainFace:
    """Represents a single face on a terrain die."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"TerrainFace(name='{self.name}')"


class Terrain:
    """
    Represents a terrain die in the Dragon Dice game.
    Each terrain has a name, type (major/minor), color (base terrain type),
    subtype (variant), and faces with their effects.
    """

    def __init__(
        self,
        name: str,
        terrain_type: str,
        color: str,
        subtype: str,
        faces: List[Dict[str, str]],
        elements: Optional[List[str]] = None,
        element_colors: Optional[List[str]] = None,
    ):
        self.name = name
        self.terrain_type = terrain_type  # "major" or "minor"
        self.color = color  # Base terrain type (Coastland, Deadland, etc.)
        self.subtype = subtype  # Variant (Bridge, Castle, etc.)
        self.faces = [TerrainFace(face["name"], face["description"]) for face in faces]

        # Derive elements from color if not provided
        self.elements = elements or self._derive_elements_from_color(color)
        self.element_colors = element_colors or [ELEMENT_DATA[elem].icon for elem in self.elements]

        # Display name
        self.display_name = name

        self._validate()

    def _derive_elements_from_color(self, color: str) -> List[str]:
        """Derive element list from terrain color."""
        color_to_elements = {
            "COASTLAND": ["AIR", "WATER"],
            "DEADLAND": ["DEATH"],
            "FEYLAND": ["WATER", "FIRE"],
            "FLATLAND": ["AIR", "EARTH"],
            "HIGHLAND": ["FIRE", "EARTH"],
            "SWAMPLAND": ["WATER", "EARTH"],
            "WASTELAND": ["AIR", "FIRE"],
        }
        return color_to_elements.get(color.upper(), [])

    def _validate(self):
        """Validate terrain data."""
        if self.terrain_type not in ["major", "minor"]:
            raise ValueError(f"Invalid terrain type: {self.terrain_type}")

        if not self.faces:
            raise ValueError("Terrain must have at least one face")

        # Validate elements if provided
        if self.elements:
            if not 1 <= len(self.elements) <= 2:
                raise ValueError("Terrain must have one or two elements.")

            valid_elements = list(ELEMENT_DATA.keys())
            for element in self.elements:
                if element not in valid_elements:
                    raise ValueError(f"Invalid element '{element}'. Must be one of {valid_elements}")

    def __str__(self) -> str:
        return f"{self.name} ({self.terrain_type})"

    def __repr__(self) -> str:
        return (
            f"Terrain(name='{self.name}', type='{self.terrain_type}', color='{self.color}', subtype='{self.subtype}')"
        )

    def get_element_names(self) -> List[str]:
        """Returns the element color names."""
        return [ELEMENT_DATA[elem].color_name for elem in self.elements] if self.elements else []

    def get_element_icons(self) -> List[str]:
        """Returns the element icons."""
        return self.element_colors

    def get_color_string(self) -> str:
        """Returns combined element colors as a single string."""
        return "".join(self.element_colors)

    def has_element(self, element: str) -> bool:
        """Check if this terrain has a specific element."""
        return element.upper() in (self.elements or [])

    def is_major_terrain(self) -> bool:
        """Check if this is a major terrain."""
        return self.terrain_type == "major"

    def is_minor_terrain(self) -> bool:
        """Check if this is a minor terrain."""
        return self.terrain_type == "minor"

    def get_face_names(self) -> List[str]:
        """Get all face names for this terrain."""
        return [face.name for face in self.faces]

    def get_face_by_name(self, face_name: str) -> Optional[TerrainFace]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None


# Static terrain data - define all terrain instances
TERRAIN_DATA = {
    "COASTLAND": Terrain(
        name="Coastland",
        terrain_type="major",
        color="Coastland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic coastland terrain"}],
        elements=["AIR", "WATER"],
    ),
    "DEADLAND": Terrain(
        name="Deadland",
        terrain_type="major",
        color="Deadland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic deadland terrain"}],
        elements=["DEATH"],
    ),
    "FLATLAND": Terrain(
        name="Flatland",
        terrain_type="major",
        color="Flatland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic flatland terrain"}],
        elements=["AIR", "EARTH"],
    ),
    "HIGHLAND": Terrain(
        name="Highland",
        terrain_type="major",
        color="Highland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic highland terrain"}],
        elements=["FIRE", "EARTH"],
    ),
    "SWAMPLAND": Terrain(
        name="Swampland",
        terrain_type="major",
        color="Swampland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic swampland terrain"}],
        elements=["WATER", "EARTH"],
    ),
    "FEYLAND": Terrain(
        name="Feyland",
        terrain_type="major",
        color="Feyland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic feyland terrain"}],
        elements=["WATER", "FIRE"],
    ),
    "WASTELAND": Terrain(
        name="Wasteland",
        terrain_type="major",
        color="Wasteland",
        subtype="Basic",
        faces=[{"name": "Basic", "description": "Basic wasteland terrain"}],
        elements=["AIR", "FIRE"],
    ),
}


# Helper functions for terrain access
def get_terrain(terrain_name: str) -> Optional[Terrain]:
    """Get a terrain by name."""
    terrain_key = terrain_name.upper()
    return TERRAIN_DATA.get(terrain_key)


def get_all_terrain_names() -> List[str]:
    """Get all terrain names."""
    return list(TERRAIN_DATA.keys())


def get_all_terrain_objects() -> List[Terrain]:
    """Get all terrain objects."""
    return list(TERRAIN_DATA.values())


def get_terrains_by_element(element: str) -> List[Terrain]:
    """Get all terrains that contain a specific element."""
    element = element.upper()
    return [terrain for terrain in TERRAIN_DATA.values() if terrain.has_element(element)]


def get_terrains_by_type(terrain_type: str) -> List[Terrain]:
    """Get all terrains of a specific type (major/minor)."""
    return [terrain for terrain in TERRAIN_DATA.values() if terrain.terrain_type == terrain_type.lower()]


def get_terrains_by_color(color: str) -> List[Terrain]:
    """Get all terrains of a specific color (base terrain type)."""
    color = color.upper()
    return [terrain for terrain in TERRAIN_DATA.values() if terrain.color.upper() == color]


def get_terrains_by_subtype(subtype: str) -> List[Terrain]:
    """Get all terrains of a specific subtype."""
    return [terrain for terrain in TERRAIN_DATA.values() if terrain.subtype.lower() == subtype.lower()]


def validate_terrain_data() -> bool:
    """Validate all terrain data."""
    try:
        for terrain_name, terrain in TERRAIN_DATA.items():
            if not isinstance(terrain, Terrain):
                print(f"ERROR: {terrain_name} is not a Terrain instance")
                return False

            # Allow terrain names to not match keys exactly
            # since we now use color as key but terrain.name is the full name

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
        raise KeyError(f"Unknown terrain type: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}")
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
    raise KeyError(f"Unknown terrain or location: '{name}'. Valid options: {valid_names}")


def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon display_name' format for display."""
    terrain = get_terrain(terrain_name)
    if not terrain:
        raise KeyError(f"Unknown terrain type: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}")
    return f"{terrain.get_color_string()} {terrain.display_name}"
