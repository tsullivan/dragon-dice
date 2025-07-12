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
    eighth_face (variant), and faces with their effects.

    If is_advanced=True, the terrain can ONLY be used in the Frontier location.
    """

    def __init__(
        self, name: str, eighth_face: str, faces: List[Dict[str, str]], elements: List[str], is_advanced=False
    ):
        self.name = name
        self.terrain_type = "major"
        self.eighth_face = eighth_face  # Variant (Bridge, Castle, etc.)
        self.faces = [TerrainFace(face["name"], face["description"]) for face in faces]
        self.elements = elements
        self.is_advanced = is_advanced

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
        return f"Terrain(name='{self.name}', type='{self.terrain_type}', elements='{self.elements[0], self.elements[1]}', eighth_face='{self.eighth_face}')"

    def get_element_names(self) -> List[str]:
        """Returns the element color names."""
        return [ELEMENT_DATA[elem].color_name for elem in self.elements] if self.elements else []

    def get_element_icons(self) -> List[str]:
        """Returns the element icons."""
        return self.elements

    def get_color_string(self) -> str:
        """Returns combined element colors as a single string."""
        return "".join(self.elements)

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


# Static terrain data - detailed terrain dice only
TERRAIN_DATA = {
    # Detailed Terrain Dice
    "COASTLAND_CASTLE": Terrain(
        name="Coastland Castle",
        elements=["AIR", "WATER"],
        is_advanced=True,
        eighth_face="Castle",
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
    ),
    "COASTLAND_CITY": Terrain(
        name="Coastland City",
        elements=["AIR", "WATER"],
        eighth_face="City",
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
    ),
    "COASTLAND_DRAGON_LAIR": Terrain(
        name="Coastland Dragon Lair",
        elements=["AIR", "WATER"],
        is_advanced=True,
        eighth_face="Dragon Lair",
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
    ),
    "COASTLAND_GROVE": Terrain(
        name="Coastland Grove",
        elements=["AIR", "WATER"],
        is_advanced=True,
        eighth_face="Grove",
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
    ),
    "COASTLAND_STANDING_STONES": Terrain(
        name="Coastland Standing Stones",
        elements=["AIR", "WATER"],
        eighth_face="Standing Stones",
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
    ),
    "COASTLAND_TEMPLE": Terrain(
        name="Coastland Temple",
        elements=["AIR", "WATER"],
        eighth_face="Temple",
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
    ),
    "COASTLAND_TOWER": Terrain(
        name="Coastland Tower",
        elements=["AIR", "WATER"],
        eighth_face="Tower",
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
    ),
    "COASTLAND_VORTEX": Terrain(
        name="Coastland Vortex",
        elements=["AIR", "WATER"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
    "FEYLAND_CASTLE": Terrain(
        name="Feyland Castle",
        elements=["WATER", "FIRE"],
        is_advanced=True,
        eighth_face="Castle",
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
    ),
    "FEYLAND_CITY": Terrain(
        name="Feyland City",
        elements=["WATER", "FIRE"],
        eighth_face="City",
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
    ),
    "FEYLAND_DRAGON_LAIR": Terrain(
        name="Feyland Dragon Lair",
        elements=["WATER", "FIRE"],
        is_advanced=True,
        eighth_face="Dragon Lair",
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
    ),
    "FEYLAND_GROVE": Terrain(
        name="Feyland Grove",
        elements=["WATER", "FIRE"],
        is_advanced=True,
        eighth_face="Grove",
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
    ),
    "FEYLAND_STANDING_STONES": Terrain(
        name="Feyland Standing Stones",
        elements=["WATER", "FIRE"],
        eighth_face="Standing Stones",
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
    ),
    "FEYLAND_TEMPLE": Terrain(
        name="Feyland Temple",
        elements=["WATER", "FIRE"],
        eighth_face="Temple",
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
    ),
    "FEYLAND_TOWER": Terrain(
        name="Feyland Tower",
        elements=["WATER", "FIRE"],
        eighth_face="Tower",
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
    ),
    "FEYLAND_VORTEX": Terrain(
        name="Feyland Vortex",
        elements=["WATER", "FIRE"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
    "FLATLAND_CASTLE": Terrain(
        name="Flatland Castle",
        elements=["AIR", "EARTH"],
        is_advanced=True,
        eighth_face="Castle",
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
    ),
    "FLATLAND_CITY": Terrain(
        name="Flatland City",
        elements=["AIR", "EARTH"],
        eighth_face="City",
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
    ),
    "FLATLAND_DRAGON_LAIR": Terrain(
        name="Flatland Dragon Lair",
        elements=["AIR", "EARTH"],
        is_advanced=True,
        eighth_face="Dragon Lair",
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
    ),
    "FLATLAND_GROVE": Terrain(
        name="Flatland Grove",
        elements=["AIR", "EARTH"],
        is_advanced=True,
        eighth_face="Grove",
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
    ),
    "FLATLAND_STANDING_STONES": Terrain(
        name="Flatland Standing Stones",
        elements=["AIR", "EARTH"],
        eighth_face="Standing Stones",
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
    ),
    "FLATLAND_TEMPLE": Terrain(
        name="Flatland Temple",
        elements=["AIR", "EARTH"],
        eighth_face="Temple",
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
    ),
    "FLATLAND_TOWER": Terrain(
        name="Flatland Tower",
        elements=["AIR", "EARTH"],
        eighth_face="Tower",
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
    ),
    "FLATLAND_VORTEX": Terrain(
        name="Flatland Vortex",
        elements=["AIR", "EARTH"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
    "HIGHLAND_CASTLE": Terrain(
        name="Highland Castle",
        elements=["FIRE", "EARTH"],
        is_advanced=True,
        eighth_face="Castle",
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
    ),
    "HIGHLAND_CITY": Terrain(
        name="Highland City",
        elements=["FIRE", "EARTH"],
        eighth_face="City",
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
    ),
    "HIGHLAND_DRAGON_LAIR": Terrain(
        name="Highland Dragon Lair",
        elements=["FIRE", "EARTH"],
        is_advanced=True,
        eighth_face="Dragon Lair",
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
    ),
    "HIGHLAND_GROVE": Terrain(
        name="Highland Grove",
        elements=["FIRE", "EARTH"],
        is_advanced=True,
        eighth_face="Grove",
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
    ),
    "HIGHLAND_STANDING_STONES": Terrain(
        name="Highland Standing Stones",
        elements=["FIRE", "EARTH"],
        eighth_face="Standing Stones",
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
    ),
    "HIGHLAND_TEMPLE": Terrain(
        name="Highland Temple",
        elements=["FIRE", "EARTH"],
        eighth_face="Temple",
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
    ),
    "HIGHLAND_TOWER": Terrain(
        name="Highland Tower",
        elements=["FIRE", "EARTH"],
        eighth_face="Tower",
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
    ),
    "HIGHLAND_VORTEX": Terrain(
        name="Highland Vortex",
        elements=["FIRE", "EARTH"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
    "SWAMPLAND_CASTLE": Terrain(
        name="Swampland Castle",
        elements=["WATER", "EARTH"],
        is_advanced=True,
        eighth_face="Castle",
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
    ),
    "SWAMPLAND_CITY": Terrain(
        name="Swampland City",
        elements=["WATER", "EARTH"],
        eighth_face="City",
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
    ),
    "SWAMPLAND_DRAGON_LAIR": Terrain(
        name="Swampland Dragon Lair",
        elements=["WATER", "EARTH"],
        is_advanced=True,
        eighth_face="Dragon Lair",
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
    ),
    "SWAMPLAND_GROVE": Terrain(
        name="Swampland Grove",
        elements=["WATER", "EARTH"],
        is_advanced=True,
        eighth_face="Grove",
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
    ),
    "SWAMPLAND_STANDING_STONES": Terrain(
        name="Swampland Standing Stones",
        elements=["WATER", "EARTH"],
        eighth_face="Standing Stones",
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
    ),
    "SWAMPLAND_TEMPLE": Terrain(
        name="Swampland Temple",
        elements=["WATER", "EARTH"],
        eighth_face="Temple",
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
    ),
    "SWAMPLAND_TOWER": Terrain(
        name="Swampland Tower",
        elements=["WATER", "EARTH"],
        eighth_face="Tower",
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
    ),
    "SWAMPLAND_VORTEX": Terrain(
        name="Swampland Vortex",
        elements=["WATER", "EARTH"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
    "WASTELAND_CASTLE": Terrain(
        name="Wasteland Castle",
        elements=["AIR", "FIRE"],
        eighth_face="Castle",
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
    ),
    "WASTELAND_CITY": Terrain(
        name="Wasteland City",
        elements=["AIR", "FIRE"],
        eighth_face="City",
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
    ),
    "WASTELAND_DRAGON_LAIR": Terrain(
        name="Wasteland Dragon Lair",
        elements=["AIR", "FIRE"],
        eighth_face="Dragon Lair",
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
    ),
    "WASTELAND_GROVE": Terrain(
        name="Wasteland Grove",
        elements=["AIR", "FIRE"],
        eighth_face="Grove",
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
    ),
    "WASTELAND_STANDING_STONES": Terrain(
        name="Wasteland Standing Stones",
        elements=["AIR", "FIRE"],
        eighth_face="Standing Stones",
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
    ),
    "WASTELAND_TEMPLE": Terrain(
        name="Wasteland Temple",
        elements=["AIR", "FIRE"],
        eighth_face="Temple",
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
    ),
    "WASTELAND_TOWER": Terrain(
        name="Wasteland Tower",
        elements=["AIR", "FIRE"],
        eighth_face="Tower",
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
    ),
    "WASTELAND_VORTEX": Terrain(
        name="Wasteland Vortex",
        elements=["AIR", "FIRE"],
        is_advanced=True,
        eighth_face="Vortex",
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
                "description": "During any non-maneuver army roll at this terrain, before resolving SAI's (see  step 2 of 'Die Roll Resolution'), you may reroll one unit, ignoring the previous result.",
            },
        ],
    ),
}


# Helper functions for terrain access
def get_terrain(terrain_name: str) -> Optional[Terrain]:
    """Get a terrain by name."""
    terrain_key = terrain_name.upper()
    return TERRAIN_DATA.get(terrain_key)


def resolve_terrain_name(terrain_name: str) -> Optional[Terrain]:
    """Get a terrain by name, handling various input formats.

    Handles:
    - Direct terrain keys: "COASTLAND_CASTLE"
    - Display names: "Coastland Castle"
    - Names with parenthetical color info: "Coastland Castle (Blue, Green)"
    - Player-specific names: "Player 1 Coastland Castle"
    """
    if not terrain_name:
        return None

    # Clean the terrain name by removing color information in parentheses
    clean_name = terrain_name
    if "(" in terrain_name and ")" in terrain_name:
        paren_start = terrain_name.rfind("(")
        clean_name = terrain_name[:paren_start].strip()

    # Try direct lookup first (handles keys like "COASTLAND_CASTLE")
    terrain_key = clean_name.upper().replace(" ", "_")
    terrain = TERRAIN_DATA.get(terrain_key)
    if terrain:
        return terrain

    # Try original clean name format
    original_key = clean_name.upper()
    terrain = TERRAIN_DATA.get(original_key)
    if terrain:
        return terrain

    # Handle player-specific names like "Player 1 Coastland Castle"
    if " " in clean_name:
        parts = clean_name.split()
        if len(parts) >= 3 and parts[0] == "Player":
            # Extract base terrain name after "Player N"
            base_terrain = " ".join(parts[2:])
            base_terrain_key = base_terrain.upper().replace(" ", "_")
            terrain = TERRAIN_DATA.get(base_terrain_key)
            if terrain:
                return terrain

    # Search by display name (case-insensitive)
    clean_name_lower = clean_name.lower()
    for terrain in TERRAIN_DATA.values():
        if terrain.display_name.lower() == clean_name_lower:
            return terrain

    return None


def get_clean_terrain_display_name(terrain_name: str) -> str:
    """Get the clean display name for a terrain, handling various input formats.

    Args:
        terrain_name: Any terrain name format (with/without colors, player-specific, etc.)

    Returns:
        Clean display name from TERRAIN_DATA, or original name if not found
    """
    terrain = resolve_terrain_name(terrain_name)
    if terrain:
        return terrain.display_name

    # Fallback: clean the name manually if terrain not found
    clean_name = terrain_name
    if "(" in terrain_name and ")" in terrain_name:
        paren_start = terrain_name.rfind("(")
        clean_name = terrain_name[:paren_start].strip()

    return clean_name


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


def get_terrains_by_eighth_face(eighth_face: str) -> List[Terrain]:
    """Get all terrains of a specific eighth_face."""
    return [terrain for terrain in TERRAIN_DATA.values() if terrain.eighth_face.lower() == eighth_face.lower()]


def get_terrain_icon(terrain_name: str) -> str:
    """Get terrain icon based on its elements.

    Args:
        terrain_name: The terrain name or key

    Returns:
        String of element icons representing the terrain

    Raises:
        KeyError: If terrain not found
    """
    terrain = resolve_terrain_name(terrain_name)
    if not terrain:
        raise KeyError(f"Unknown terrain: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}")

    from models.element_model import get_element_icon

    return "".join(get_element_icon(element) for element in terrain.elements)


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
def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon display_name' format for display."""
    terrain = get_terrain(terrain_name)
    if not terrain:
        raise KeyError(f"Unknown terrain type: '{terrain_name}'. Valid terrains: {get_all_terrain_names()}")
    return f"{terrain.get_color_string()} {terrain.display_name}"
