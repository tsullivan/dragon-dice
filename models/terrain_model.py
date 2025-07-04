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
    # Basic Terrains (keeping for backward compatibility)
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
    # Detailed Terrain Dice
    "COASTLAND_CASTLE": Terrain(
        name="Coastland Castle",
        terrain_type="major",
        color="Coastland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_CITY": Terrain(
        name="Coastland City",
        terrain_type="major",
        color="Coastland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_DRAGON_LAIR": Terrain(
        name="Coastland Dragon Lair",
        terrain_type="major",
        color="Coastland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_GROVE": Terrain(
        name="Coastland Grove",
        terrain_type="major",
        color="Coastland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_STANDING_STONES": Terrain(
        name="Coastland Standing Stones",
        terrain_type="major",
        color="Coastland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_TEMPLE": Terrain(
        name="Coastland Temple",
        terrain_type="major",
        color="Coastland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_TOWER": Terrain(
        name="Coastland Tower",
        terrain_type="major",
        color="Coastland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_VORTEX": Terrain(
        name="Coastland Vortex",
        terrain_type="major",
        color="Coastland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "FEYLAND_CASTLE": Terrain(
        name="Feyland Castle",
        terrain_type="major",
        color="Feyland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_CITY": Terrain(
        name="Feyland City",
        terrain_type="major",
        color="Feyland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_DRAGON_LAIR": Terrain(
        name="Feyland Dragon Lair",
        terrain_type="major",
        color="Feyland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_GROVE": Terrain(
        name="Feyland Grove",
        terrain_type="major",
        color="Feyland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_STANDING_STONES": Terrain(
        name="Feyland Standing Stones",
        terrain_type="major",
        color="Feyland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_TEMPLE": Terrain(
        name="Feyland Temple",
        terrain_type="major",
        color="Feyland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_TOWER": Terrain(
        name="Feyland Tower",
        terrain_type="major",
        color="Feyland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_VORTEX": Terrain(
        name="Feyland Vortex",
        terrain_type="major",
        color="Feyland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FLATLAND_CASTLE": Terrain(
        name="Flatland Castle",
        terrain_type="major",
        color="Flatland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_CITY": Terrain(
        name="Flatland City",
        terrain_type="major",
        color="Flatland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_DRAGON_LAIR": Terrain(
        name="Flatland Dragon Lair",
        terrain_type="major",
        color="Flatland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_GROVE": Terrain(
        name="Flatland Grove",
        terrain_type="major",
        color="Flatland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_STANDING_STONES": Terrain(
        name="Flatland Standing Stones",
        terrain_type="major",
        color="Flatland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_TEMPLE": Terrain(
        name="Flatland Temple",
        terrain_type="major",
        color="Flatland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_TOWER": Terrain(
        name="Flatland Tower",
        terrain_type="major",
        color="Flatland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_VORTEX": Terrain(
        name="Flatland Vortex",
        terrain_type="major",
        color="Flatland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "HIGHLAND_CASTLE": Terrain(
        name="Highland Castle",
        terrain_type="major",
        color="Highland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_CITY": Terrain(
        name="Highland City",
        terrain_type="major",
        color="Highland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_DRAGON_LAIR": Terrain(
        name="Highland Dragon Lair",
        terrain_type="major",
        color="Highland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_GROVE": Terrain(
        name="Highland Grove",
        terrain_type="major",
        color="Highland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_STANDING_STONES": Terrain(
        name="Highland Standing Stones",
        terrain_type="major",
        color="Highland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_TEMPLE": Terrain(
        name="Highland Temple",
        terrain_type="major",
        color="Highland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_TOWER": Terrain(
        name="Highland Tower",
        terrain_type="major",
        color="Highland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_VORTEX": Terrain(
        name="Highland Vortex",
        terrain_type="major",
        color="Highland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "SWAMPLAND_CASTLE": Terrain(
        name="Swampland Castle",
        terrain_type="major",
        color="Swampland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_CITY": Terrain(
        name="Swampland City",
        terrain_type="major",
        color="Swampland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_DRAGON_LAIR": Terrain(
        name="Swampland Dragon Lair",
        terrain_type="major",
        color="Swampland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_GROVE": Terrain(
        name="Swampland Grove",
        terrain_type="major",
        color="Swampland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_STANDING_STONES": Terrain(
        name="Swampland Standing Stones",
        terrain_type="major",
        color="Swampland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_TEMPLE": Terrain(
        name="Swampland Temple",
        terrain_type="major",
        color="Swampland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_TOWER": Terrain(
        name="Swampland Tower",
        terrain_type="major",
        color="Swampland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_VORTEX": Terrain(
        name="Swampland Vortex",
        terrain_type="major",
        color="Swampland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "WASTELAND_CASTLE": Terrain(
        name="Wasteland Castle",
        terrain_type="major",
        color="Wasteland",
        subtype="Castle",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Castle",
                "description": "When you capture this terrain, choose one of the following four terrain types: City, Standing Stones, Temple, or Tower. The castle becomes that terrain until its face is moved.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_CITY": Terrain(
        name="Wasteland City",
        terrain_type="major",
        color="Wasteland",
        subtype="City",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "City",
                "description": "During the Eighth Face Phase you may recruit a 1-health (small) unit or promote one unit in the controlling army.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_DRAGON_LAIR": Terrain(
        name="Wasteland Dragon Lair",
        terrain_type="major",
        color="Wasteland",
        subtype="Dragon Lair",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Dragon Lair",
                "description": "During the Eighth Face Phase, you may summon a dragon that matches at least one color of this terrain, an Ivory Dragon or any Ivory Hybrid Dragon, and place it at any terrain. The Dragon's Lair may not summon a White Dragon.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_GROVE": Terrain(
        name="Wasteland Grove",
        terrain_type="major",
        color="Wasteland",
        subtype="Grove",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Grove",
                "description": "During the Eighth Face Phase move one non-Dragonkin unit from any player's BUA to their DUA, a Dragonkin unit or minor terrain from your BUA to your Summoning Pool, or an Item from your BUA to your army controlling this eighth face. This is not optional and must be performed if possible.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_STANDING_STONES": Terrain(
        name="Wasteland Standing Stones",
        terrain_type="major",
        color="Wasteland",
        subtype="Standing Stones",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Standing Stones",
                "description": "All units in your controlling army may convert any or all of their magic results to a color that matches a color of this terrain.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_TEMPLE": Terrain(
        name="Wasteland Temple",
        terrain_type="major",
        color="Wasteland",
        subtype="Temple",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Temple",
                "description": "Your controlling army and all units in it cannot be affected by any opponent's death (black) magic. During the Eighth Face Phase you may force another player to bury one unit of their choice in their DUA.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_TOWER": Terrain(
        name="Wasteland Tower",
        terrain_type="major",
        color="Wasteland",
        subtype="Tower",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Tower",
                "description": "Your controlling army may use a missile action to attack any opponent's army. If attacking a Reserve Army, only count non-ID missile results.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_VORTEX": Terrain(
        name="Wasteland Vortex",
        terrain_type="major",
        color="Wasteland",
        subtype="Vortex",
        faces=[
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Magic Terrain", "description": "This icon on the terrain sets the current action to magic."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Missile Terrain", "description": "This icon on the terrain sets the current action to missile."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {"name": "Melee Terrain", "description": "This icon on the terrain sets the current action to melee."},
            {
                "name": "Vortex",
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
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
