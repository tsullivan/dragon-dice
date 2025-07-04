from typing import Dict, List, Optional

from models.element_model import ELEMENT_DATA


class MinorTerrainFace:
    """Represents a single face on a minor terrain die."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"MinorTerrainFace(name='{self.name}')"


class MinorTerrain:
    """
    Represents a minor terrain die in the Dragon Dice game.
    Minor terrains are smaller terrain dice that can be placed on major terrains
    and provide additional effects to armies controlling them.
    """

    def __init__(
        self,
        name: str,
        color: str,
        subtype: str,
        faces: List[Dict[str, str]],
        elements: Optional[List[str]] = None,
        element_colors: Optional[List[str]] = None,
    ):
        self.name = name
        self.terrain_type = "minor"  # Always minor for this model
        self.color = color  # Base terrain type (Coastland, Deadland, etc.)
        self.subtype = subtype  # Variant (Bridge, Forest, Knoll, Village)
        self.faces = [MinorTerrainFace(face["name"], face["description"]) for face in faces]

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
        """Validate minor terrain data."""
        if not self.faces:
            raise ValueError("Minor terrain must have at least one face")

        # Validate elements if provided
        if self.elements:
            if not 1 <= len(self.elements) <= 2:
                raise ValueError("Minor terrain must have one or two elements.")

            valid_elements = list(ELEMENT_DATA.keys())
            for element in self.elements:
                if element not in valid_elements:
                    raise ValueError(f"Invalid element '{element}'. Must be one of {valid_elements}")

    def __str__(self) -> str:
        return f"{self.name} (minor)"

    def __repr__(self) -> str:
        return f"MinorTerrain(name='{self.name}', color='{self.color}', subtype='{self.subtype}')"

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
        """Check if this minor terrain has a specific element."""
        return element.upper() in (self.elements or [])

    def is_minor_terrain(self) -> bool:
        """Check if this is a minor terrain (always True for this model)."""
        return True

    def get_face_names(self) -> List[str]:
        """Get all face names for this minor terrain."""
        return [face.name for face in self.faces]

    def get_face_by_name(self, face_name: str) -> Optional[MinorTerrainFace]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None


# Static minor terrain data - define all minor terrain instances
MINOR_TERRAIN_DATA = {
    "COASTLAND_BRIDGE": MinorTerrain(
        name="Coastland Bridge",
        color="Coastland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_FOREST": MinorTerrain(
        name="Coastland Forest",
        color="Coastland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_KNOLL": MinorTerrain(
        name="Coastland Knoll",
        color="Coastland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_VILLAGE": MinorTerrain(
        name="Coastland Village",
        color="Coastland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "DEADLAND_BRIDGE": MinorTerrain(
        name="Deadland Bridge",
        color="Deadland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_FOREST": MinorTerrain(
        name="Deadland Forest",
        color="Deadland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_KNOLL": MinorTerrain(
        name="Deadland Knoll",
        color="Deadland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_VILLAGE": MinorTerrain(
        name="Deadland Village",
        color="Deadland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "FEYLAND_BRIDGE": MinorTerrain(
        name="Feyland Bridge",
        color="Feyland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_FOREST": MinorTerrain(
        name="Feyland Forest",
        color="Feyland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_KNOLL": MinorTerrain(
        name="Feyland Knoll",
        color="Feyland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_VILLAGE": MinorTerrain(
        name="Feyland Village",
        color="Feyland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FLATLAND_BRIDGE": MinorTerrain(
        name="Flatland Bridge",
        color="Flatland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_FOREST": MinorTerrain(
        name="Flatland Forest",
        color="Flatland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_KNOLL": MinorTerrain(
        name="Flatland Knoll",
        color="Flatland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_VILLAGE": MinorTerrain(
        name="Flatland Village",
        color="Flatland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "HIGHLAND_BRIDGE": MinorTerrain(
        name="Highland Bridge",
        color="Highland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_FOREST": MinorTerrain(
        name="Highland Forest",
        color="Highland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_KNOLL": MinorTerrain(
        name="Highland Knoll",
        color="Highland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_VILLAGE": MinorTerrain(
        name="Highland Village",
        color="Highland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "SWAMPLAND_BRIDGE": MinorTerrain(
        name="Swampland Bridge",
        color="Swampland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_FOREST": MinorTerrain(
        name="Swampland Forest",
        color="Swampland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_KNOLL": MinorTerrain(
        name="Swampland Knoll",
        color="Swampland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_VILLAGE": MinorTerrain(
        name="Swampland Village",
        color="Swampland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "WASTELAND_BRIDGE": MinorTerrain(
        name="Wasteland Bridge",
        color="Wasteland",
        subtype="Bridge",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood Minor",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_FOREST": MinorTerrain(
        name="Wasteland Forest",
        color="Wasteland",
        subtype="Forest",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Lost Minor",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_KNOLL": MinorTerrain(
        name="Wasteland Knoll",
        color="Wasteland",
        subtype="Knoll",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide Minor",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_VILLAGE": MinorTerrain(
        name="Wasteland Village",
        color="Wasteland",
        subtype="Village",
        faces=[
            {
                "name": "ID Minor",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile Minor",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee Minor",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic Minor",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers Minor",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves Minor",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt Minor",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
}


# Helper functions for minor terrain access
def get_minor_terrain(terrain_name: str) -> Optional[MinorTerrain]:
    """Get a minor terrain by name."""
    terrain_key = terrain_name.upper()
    return MINOR_TERRAIN_DATA.get(terrain_key)


def get_all_minor_terrain_names() -> List[str]:
    """Get all minor terrain names."""
    return list(MINOR_TERRAIN_DATA.keys())


def get_all_minor_terrain_objects() -> List[MinorTerrain]:
    """Get all minor terrain objects."""
    return list(MINOR_TERRAIN_DATA.values())


def get_minor_terrains_by_element(element: str) -> List[MinorTerrain]:
    """Get all minor terrains that contain a specific element."""
    element = element.upper()
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if terrain.has_element(element)]


def get_minor_terrains_by_color(color: str) -> List[MinorTerrain]:
    """Get all minor terrains of a specific color (base terrain type)."""
    color = color.upper()
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if terrain.color.upper() == color]


def get_minor_terrains_by_subtype(subtype: str) -> List[MinorTerrain]:
    """Get all minor terrains of a specific subtype."""
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if terrain.subtype.lower() == subtype.lower()]


def validate_minor_terrain_data() -> bool:
    """Validate all minor terrain data."""
    try:
        for terrain_name, terrain in MINOR_TERRAIN_DATA.items():
            if not isinstance(terrain, MinorTerrain):
                print(f"ERROR: {terrain_name} is not a MinorTerrain instance")
                return False

        print(f"✓ All {len(MINOR_TERRAIN_DATA)} minor terrains validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Minor terrain validation failed: {e}")
        return False
