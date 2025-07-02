from typing import Dict, List, Optional
from models.element_model import ELEMENT_DATA


class DragonFace:
    """Represents a single face on a dragon die."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"DragonFace(name='{self.name}')"


class Dragon:
    """
    Represents a dragon die type in the Dragon Dice game.
    Each dragon has a display name and 12 faces with their effects.
    """

    def __init__(self, display_name: str, faces: List[Dict[str, str]]):
        self.display_name = display_name
        self.name = display_name.upper()  # Normalized name for keys
        self.faces = [DragonFace(face["name"], face["description"]) for face in faces]

        self._validate()

    def _validate(self):
        """Validate dragon data."""
        if len(self.faces) != 12:
            raise ValueError(
                f"Dragon must have exactly 12 faces, got {len(self.faces)}"
            )

        if not self.display_name:
            raise ValueError("Dragon must have a display name")

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"Dragon(display_name='{self.display_name}', faces={len(self.faces)})"

    def get_face_names(self) -> List[str]:
        """Get all face names for this dragon."""
        return [face.name for face in self.faces]

    def get_face_by_name(self, face_name: str) -> Optional[DragonFace]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None

    def get_face_by_index(self, index: int) -> Optional[DragonFace]:
        """Get a face by its index (0-11)."""
        if 0 <= index < len(self.faces):
            return self.faces[index]
        return None


class DragonAttackModel:
    """
    Model for dragon attack types.
    """

    def __init__(self, name: str, icon: str, display_name: str):
        self.name = name
        self.icon = icon
        self.display_name = display_name

    def __str__(self) -> str:
        return f"{self.icon} {self.display_name}"

    def __repr__(self) -> str:
        return f"DragonAttackModel(name='{self.name}', icon='{self.icon}', display_name='{self.display_name}')"


class DragonTypeModel:
    """
    Model for dragon types with element associations.
    """

    def __init__(self, name: str, display_name: str, element: str):
        self.name = name
        self.display_name = display_name
        self.element = element

        # Validate element
        if element not in [elem.icon for elem in ELEMENT_DATA.values()]:
            raise ValueError(f"Invalid element icon: {element}")

    def __str__(self) -> str:
        return f"{self.element} {self.display_name}"

    def __repr__(self) -> str:
        return f"DragonTypeModel(name='{self.name}', display_name='{self.display_name}', element='{self.element}')"


# Static dragon data - define dragon instances based on JSON structure
DRAGON_DATA = {
    "DRAKE": Dragon(
        display_name="Drake",
        faces=[
            {
                "name": "Jaws",
                "description": "A dragon's jaws inflict twelve points of damage on an army. Also counts as the 'ID' for ID based SAIs that effect Dragons.",
            },
            {
                "name": "Dragon Breath",
                "description": "Against another dragon, dragon breath inflicts five (ten for a White Dragon) points of damage; roll the dragon again and apply the new result as well. Against armies, five health-worth of units in the target army are killed. In addition, an effect based on the color affects the army.",
            },
            {
                "name": "Claw; Front Left",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Claw; Front Right",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Wing; Left",
                "description": "A dragon's wings inflict five points of damage on an army. After the attack, if the dragon is still alive, it flies away. It returns to it's summoning pool.",
            },
            {
                "name": "Wing; Right",
                "description": "A dragon's wings inflict five points of damage on an army. After the attack, if the dragon is still alive, it flies away. It returns to it's summoning pool.",
            },
            {
                "name": "Belly; Front",
                "description": "The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
            },
            {
                "name": "Belly; Rear",
                "description": "The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
            },
            {
                "name": "Claw; Rear Left",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Claw; Rear Right",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Tail; Front",
                "description": "The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
            },
            {
                "name": "Tail; Tip",
                "description": "The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
            },
        ],
    ),
    "WYRM": Dragon(
        display_name="Wyrm",
        faces=[
            {
                "name": "Jaws",
                "description": "A dragon's jaws inflict twelve points of damage on an army. Also counts as the 'ID' for ID based SAIs that effect Dragons.",
            },
            {
                "name": "Dragon Breath",
                "description": "Against another dragon, dragon breath inflicts five (ten for a White Dragon) points of damage; roll the dragon again and apply the new result as well. Against armies, five health-worth of units in the target army are killed. In addition, an effect based on the color affects the army.",
            },
            {
                "name": "Claw; Front Left",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Claw; Front Right",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Belly; Front",
                "description": "The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
            },
            {
                "name": "Belly; Rear",
                "description": "The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
            },
            {
                "name": "Claw; Rear Left",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Claw; Rear Right",
                "description": "A dragon's claws inflict six points of damage on an army.",
            },
            {
                "name": "Tail; Front",
                "description": "The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
            },
            {
                "name": "Tail; Middle",
                "description": "The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
            },
            {
                "name": "Tail; Tip",
                "description": "The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
            },
            {
                "name": "Treasure",
                "description": "One unit in the target army may immediately be promoted.",
            },
        ],
    ),
}


# Helper functions for dragons
def get_dragon(dragon_name: str) -> Optional[Dragon]:
    """Get a dragon by name."""
    dragon_key = dragon_name.upper()
    return DRAGON_DATA.get(dragon_key)


def get_all_dragon_names() -> List[str]:
    """Get all dragon names."""
    return list(DRAGON_DATA.keys())


def get_all_dragons() -> List[Dragon]:
    """Get all dragon objects."""
    return list(DRAGON_DATA.values())


def get_available_dragon_types() -> List[str]:
    """Get available dragon type display names."""
    return [dragon.display_name for dragon in DRAGON_DATA.values()]


def validate_dragon_data() -> bool:
    """Validate all dragon data."""
    try:
        # Validate dragons
        for dragon_name, dragon in DRAGON_DATA.items():
            if not isinstance(dragon, Dragon):
                print(f"ERROR: {dragon_name} is not a Dragon instance")
                return False
            if dragon.name != dragon_name:
                print(f"ERROR: Dragon name mismatch: {dragon.name} != {dragon_name}")
                return False
            if len(dragon.faces) != 12:
                print(
                    f"ERROR: Dragon {dragon_name} has {len(dragon.faces)} faces, expected 12"
                )
                return False

        print(f"✓ All dragon data validated successfully")
        print(f"  - {len(DRAGON_DATA)} dragons")
        return True
    except Exception as e:
        print(f"ERROR: Dragon data validation failed: {e}")
        return False


def calculate_required_dragons(force_size_points: int) -> int:
    """Calculate required dragons based on force size points.

    Official rules: 1 dragon per 24 points (or part thereof)
    Examples: 15 pts = 1 dragon, 24 pts = 1 dragon, 30 pts = 2 dragons, 60 pts = 3 dragons
    """
    import math
    
    POINTS_PER_DRAGON = 24
    return math.ceil(force_size_points / POINTS_PER_DRAGON)


