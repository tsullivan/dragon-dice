from typing import Dict, List, Optional, Union
from models.element_model import ELEMENT_ICONS


class DieFaceModel:
    """
    Represents a die face in the Dragon Dice game.
    Each die face has a type, value, and description of its effect.
    """

    def __init__(
        self,
        face_type: str,
        display_name: str,
        description: str,
        value: Optional[Union[int, str]] = None,
        icon: Optional[str] = None,
        category: str = "basic",
    ):
        self.face_type = face_type
        self.display_name = display_name
        self.description = description
        self.value = value
        self.icon = icon or self._get_default_icon(face_type)
        self.category = category

    def _get_default_icon(self, face_type: str) -> str:
        """Get default icon for face type."""
        icon_map = {
            "ID": "🆔",
            "MELEE": "⚔️",
            "MISSILE": "🏹",
            "MAGIC": "✨",
            "SAVE": "🛡️",
            "MOVE": "👟",
            "JAWS": "🗻",
            "CLAW": "🦅",
            "BELLY": "🛡️",
            "TAIL": "🐉",
            "TREASURE": "💎",
            "BULLSEYE": "🎯",
            "TELEPORT": "🌀",
            "FLY": "🪶",
            "SUMMON": "🔮",
        }
        return icon_map.get(face_type.upper(), "⚫")

    def __str__(self) -> str:
        if self.value:
            return f"{self.icon} {self.display_name} ({self.value})"
        return f"{self.icon} {self.display_name}"

    def __repr__(self) -> str:
        return f"DieFaceModel(face_type='{self.face_type}', display_name='{self.display_name}', value={self.value})"


# Core die face data - organized by category and common variations
DIE_FACES_DATA = {
    # Basic Combat Faces - Core game mechanics
    "ID_1": DieFaceModel(
        face_type="ID",
        display_name="ID",
        description="Counts as one point of whatever the owning army is rolling for.",
        value=1,
        category="basic",
    ),
    "ID_2": DieFaceModel(
        face_type="ID",
        display_name="ID",
        description="Counts as two points of whatever the owning army is rolling for.",
        value=2,
        category="basic",
    ),
    "ID_3": DieFaceModel(
        face_type="ID",
        display_name="ID",
        description="Counts as three points of whatever the owning army is rolling for.",
        value=3,
        category="basic",
    ),
    "ID_4": DieFaceModel(
        face_type="ID",
        display_name="ID",
        description="Counts as four points of whatever the owning army is rolling for.",
        value=4,
        category="basic",
    ),
    # Melee Combat Faces
    "MELEE_1": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as one melee hit point.",
        value=1,
        category="combat",
    ),
    "MELEE_2": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as two melee hit points.",
        value=2,
        category="combat",
    ),
    "MELEE_3": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as three melee hit points.",
        value=3,
        category="combat",
    ),
    "MELEE_4": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as four melee hit points.",
        value=4,
        category="combat",
    ),
    "MELEE_5": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as five melee hit points.",
        value=5,
        category="combat",
    ),
    "MELEE_6": DieFaceModel(
        face_type="MELEE",
        display_name="Melee",
        description="Counts as six melee hit points.",
        value=6,
        category="combat",
    ),
    # Missile Combat Faces
    "MISSILE_1": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as one missile hit point.",
        value=1,
        category="combat",
    ),
    "MISSILE_2": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as two missile hit points.",
        value=2,
        category="combat",
    ),
    "MISSILE_3": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as three missile hit points.",
        value=3,
        category="combat",
    ),
    "MISSILE_4": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as four missile hit points.",
        value=4,
        category="combat",
    ),
    "MISSILE_5": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as five missile hit points.",
        value=5,
        category="combat",
    ),
    "MISSILE_6": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile",
        description="Counts as six missile hit points.",
        value=6,
        category="combat",
    ),
    # Magic Combat Faces
    "MAGIC_1": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as one spell point.",
        value=1,
        category="combat",
    ),
    "MAGIC_2": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as two spell points.",
        value=2,
        category="combat",
    ),
    "MAGIC_3": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as three spell points.",
        value=3,
        category="combat",
    ),
    "MAGIC_4": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as four spell points.",
        value=4,
        category="combat",
    ),
    "MAGIC_5": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as five spell points.",
        value=5,
        category="combat",
    ),
    "MAGIC_6": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic",
        description="Counts as six spell points.",
        value=6,
        category="combat",
    ),
    # Save Faces
    "SAVE_1": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as one save point.",
        value=1,
        category="defense",
    ),
    "SAVE_2": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as two save points.",
        value=2,
        category="defense",
    ),
    "SAVE_3": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as three save points.",
        value=3,
        category="defense",
    ),
    "SAVE_4": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as four save points.",
        value=4,
        category="defense",
    ),
    "SAVE_5": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as five save points.",
        value=5,
        category="defense",
    ),
    "SAVE_6": DieFaceModel(
        face_type="SAVE",
        display_name="Save",
        description="Counts as six save points.",
        value=6,
        category="defense",
    ),
    # Movement Faces
    "MOVE_1": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as one movement point.",
        value=1,
        category="movement",
    ),
    "MOVE_2": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as two movement points.",
        value=2,
        category="movement",
    ),
    "MOVE_3": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as three movement points.",
        value=3,
        category="movement",
    ),
    "MOVE_4": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as four movement points.",
        value=4,
        category="movement",
    ),
    "MOVE_5": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as five movement points.",
        value=5,
        category="movement",
    ),
    "MOVE_6": DieFaceModel(
        face_type="MOVE",
        display_name="Move",
        description="Counts as six movement points.",
        value=6,
        category="movement",
    ),
    # Dragon Specific Faces
    "DRAGON_JAWS": DieFaceModel(
        face_type="JAWS",
        display_name="Jaws",
        description='A dragon\'s jaws inflict twelve points of damage on an army. Also counts as the "ID" for ID based SAIs that effect Dragons.',
        value=12,
        category="dragon",
    ),
    "DRAGON_CLAW_6": DieFaceModel(
        face_type="CLAW",
        display_name="Claw",
        description="A dragon's claws inflict six points of damage on an army.",
        value=6,
        category="dragon",
    ),
    "DRAGON_BELLY": DieFaceModel(
        face_type="BELLY",
        display_name="Belly",
        description="The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
        value="vulnerable",
        category="dragon",
    ),
    "DRAGON_TAIL_3": DieFaceModel(
        face_type="TAIL",
        display_name="Tail",
        description="The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
        value=3,
        category="dragon",
    ),
    "DRAGON_TREASURE": DieFaceModel(
        face_type="TREASURE",
        display_name="Treasure",
        description="One unit in the target army may immediately be promoted.",
        value="promotion",
        category="dragon",
    ),
    # Special Action Icons (SAIs)
    "BULLSEYE": DieFaceModel(
        face_type="BULLSEYE",
        display_name="Bullseye",
        description="During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.",
        value="targeted",
        category="sai",
    ),
    "TELEPORT": DieFaceModel(
        face_type="TELEPORT",
        display_name="Teleport",
        description="Move this unit to any terrain in play.",
        value="movement",
        category="sai",
    ),
    "FLY": DieFaceModel(
        face_type="FLY",
        display_name="Fly",
        description="This unit may ignore terrain effects during movement.",
        value="movement",
        category="sai",
    ),
    "SUMMON_DRAGON": DieFaceModel(
        face_type="SUMMON",
        display_name="Summon Dragon",
        description="Summon a dragon to the battlefield.",
        value="summon",
        category="sai",
    ),
    # Minor Variants
    "ID_MINOR": DieFaceModel(
        face_type="ID",
        display_name="ID Minor",
        description="Counts as one point of saves, maneuvers, or melee hits, whatever the owning army is rolling for.",
        value="1_limited",
        category="basic",
    ),
    "MELEE_MINOR": DieFaceModel(
        face_type="MELEE",
        display_name="Melee Minor",
        description="Counts as one melee hit point (minor).",
        value="1_minor",
        category="combat",
    ),
    "MISSILE_MINOR": DieFaceModel(
        face_type="MISSILE",
        display_name="Missile Minor",
        description="Counts as one missile hit point (minor).",
        value="1_minor",
        category="combat",
    ),
    "MAGIC_MINOR": DieFaceModel(
        face_type="MAGIC",
        display_name="Magic Minor",
        description="Counts as one spell point (minor).",
        value="1_minor",
        category="combat",
    ),
    # Specialized Combat Faces
    "CHARGE": DieFaceModel(
        face_type="CHARGE",
        display_name="Charge",
        description="This unit gains additional melee attack bonuses when charging.",
        value="melee_bonus",
        category="combat_special",
    ),
    "TRAMPLE": DieFaceModel(
        face_type="TRAMPLE",
        display_name="Trample",
        description="This unit can trample smaller units.",
        value="trample",
        category="combat_special",
    ),
    "CRUSH": DieFaceModel(
        face_type="CRUSH",
        display_name="Crush",
        description="This unit can crush enemies with overwhelming force.",
        value="crush",
        category="combat_special",
    ),
    # Magical Abilities
    "FIREBREATH": DieFaceModel(
        face_type="FIREBREATH",
        display_name="Firebreath",
        description="Breathe fire on enemy units.",
        value="fire_attack",
        category="elemental",
    ),
    "FROST_BREATH": DieFaceModel(
        face_type="FROST_BREATH",
        display_name="Frost Breath",
        description="Breathe frost on enemy units.",
        value="frost_attack",
        category="elemental",
    ),
    "POISON": DieFaceModel(
        face_type="POISON",
        display_name="Poison",
        description="Inflict poison damage on enemies.",
        value="poison_attack",
        category="elemental",
    ),
    # Support Abilities
    "REGENERATE": DieFaceModel(
        face_type="REGENERATE",
        display_name="Regenerate",
        description="This unit can heal damage.",
        value="heal",
        category="support",
    ),
    "ELEVATE": DieFaceModel(
        face_type="ELEVATE",
        display_name="Elevate",
        description="Promote a unit in your army.",
        value="promotion",
        category="support",
    ),
    "CONVERT": DieFaceModel(
        face_type="CONVERT",
        display_name="Convert",
        description="Convert an enemy unit to your side.",
        value="conversion",
        category="support",
    ),
}


# Helper functions for die face management
def get_die_face(face_key: str) -> Optional[DieFaceModel]:
    """Get a specific die face by key."""
    return DIE_FACES_DATA.get(face_key)


def get_die_faces_by_type(face_type: str) -> List[DieFaceModel]:
    """Get all die faces of a specific type."""
    return [
        face
        for face in DIE_FACES_DATA.values()
        if face.face_type.upper() == face_type.upper()
    ]


def get_die_faces_by_category(category: str) -> List[DieFaceModel]:
    """Get all die faces in a specific category."""
    return [face for face in DIE_FACES_DATA.values() if face.category == category]


def get_basic_combat_faces() -> Dict[str, List[DieFaceModel]]:
    """Get basic combat faces organized by type."""
    combat_types = ["ID", "MELEE", "MISSILE", "MAGIC", "SAVE", "MOVE"]
    return {face_type: get_die_faces_by_type(face_type) for face_type in combat_types}


def get_dragon_faces() -> List[DieFaceModel]:
    """Get all dragon-specific die faces."""
    return get_die_faces_by_category("dragon")


def get_sai_faces() -> List[DieFaceModel]:
    """Get all Special Action Icon (SAI) faces."""
    return get_die_faces_by_category("sai")


def format_die_face_display(face: DieFaceModel) -> str:
    """Format a die face for display in UI."""
    if isinstance(face.value, int):
        return f"{face.icon} {face.display_name} ({face.value})"
    elif face.value:
        return f"{face.icon} {face.display_name}"
    else:
        return f"{face.icon} {face.display_name}"


def get_die_faces_for_unit_type(unit_type: str, health: int) -> list:
    """Get appropriate die faces based on unit type and health."""
    # ID face matches the unit's health value
    id_face = f"ID_{health}"

    if unit_type == "Heavy Melee":
        if health == 1:
            return [id_face, "MELEE_1", "MELEE_2", "SAVE_1", "MOVE_1", "MELEE_1"]
        elif health == 2:
            return [id_face, "MELEE_2", "MELEE_3", "SAVE_1", "SAVE_2", "MOVE_1"]
        elif health == 3:
            return [id_face, "MELEE_3", "MELEE_4", "SAVE_2", "SAVE_3", "MOVE_1"]
        elif health == 4:
            return [id_face, "MELEE_4", "MELEE_5", "SAVE_3", "SAVE_4", "MOVE_2"]

    elif unit_type == "Light Melee":
        if health == 1:
            return [id_face, "MELEE_1", "SAVE_1", "MOVE_2", "MOVE_3", "MELEE_1"]
        elif health == 2:
            return [id_face, "MELEE_2", "SAVE_1", "MOVE_2", "MOVE_3", "MELEE_2"]
        elif health == 3:
            return [id_face, "MELEE_2", "MELEE_3", "SAVE_2", "MOVE_3", "MOVE_4"]
        elif health == 4:
            return [id_face, "MELEE_3", "MELEE_4", "SAVE_2", "MOVE_3", "MOVE_4"]

    elif unit_type == "Cavalry":
        if health == 1:
            return [id_face, "MELEE_2", "CHARGE", "SAVE_1", "MOVE_3", "MOVE_4"]
        elif health == 2:
            return [id_face, "MELEE_3", "CHARGE", "SAVE_2", "MOVE_4", "MOVE_5"]
        elif health == 3:
            return [id_face, "MELEE_4", "CHARGE", "TRAMPLE", "SAVE_2", "MOVE_4"]
        elif health == 4:
            return [id_face, "MELEE_5", "CHARGE", "TRAMPLE", "SAVE_3", "MOVE_5"]

    elif unit_type == "Missile":
        if health == 1:
            return [id_face, "MISSILE_1", "MISSILE_2", "SAVE_1", "MOVE_1", "MISSILE_1"]
        elif health == 2:
            return [id_face, "MISSILE_2", "MISSILE_3", "BULLSEYE", "SAVE_1", "MOVE_2"]
        elif health == 3:
            return [id_face, "MISSILE_3", "MISSILE_4", "BULLSEYE", "SAVE_2", "MOVE_2"]
        elif health == 4:
            return [id_face, "MISSILE_4", "MISSILE_5", "BULLSEYE", "SAVE_3", "MOVE_2"]

    elif unit_type == "Magic":
        if health == 1:
            return [id_face, "MAGIC_1", "MAGIC_2", "SAVE_1", "MOVE_1", "TELEPORT"]
        elif health == 2:
            return [id_face, "MAGIC_2", "MAGIC_3", "SAVE_2", "MOVE_2", "TELEPORT"]
        elif health == 3:
            return [id_face, "MAGIC_3", "MAGIC_4", "SAVE_2", "MOVE_2", "SUMMON_DRAGON"]
        elif health == 4:
            return [id_face, "MAGIC_4", "MAGIC_5", "SAVE_3", "MOVE_3", "SUMMON_DRAGON"]

    elif unit_type == "Monster":
        # Monsters have 10 faces instead of 6
        if health == 1:
            return [
                id_face,
                "MELEE_2",
                "MISSILE_1",
                "SAVE_2",
                "MOVE_2",
                "REGENERATE",
                "MELEE_1",
                "MISSILE_1",
                "SAVE_1",
                "MOVE_1",
            ]
        elif health == 2:
            return [
                id_face,
                "MELEE_3",
                "MISSILE_2",
                "SAVE_2",
                "MOVE_2",
                "REGENERATE",
                "MELEE_2",
                "MISSILE_2",
                "SAVE_2",
                "MOVE_2",
            ]
        elif health == 3:
            return [
                id_face,
                "MELEE_4",
                "MISSILE_3",
                "SAVE_3",
                "MOVE_3",
                "REGENERATE",
                "MELEE_3",
                "MISSILE_3",
                "SAVE_3",
                "CRUSH",
            ]
        elif health == 4:
            return [
                id_face,
                "MELEE_5",
                "MISSILE_4",
                "SAVE_4",
                "MOVE_3",
                "REGENERATE",
                "CRUSH",
                "MELEE_4",
                "MISSILE_4",
                "SAVE_4",
            ]

    # Fallback for unknown unit types (6 faces)
    return [id_face, "MELEE_1", "SAVE_1", "MOVE_1", "MELEE_1", "SAVE_1"]


def validate_die_face_data() -> bool:
    """Validate all die face data."""
    try:
        print(f"✓ Loaded {len(DIE_FACES_DATA)} die face definitions")

        # Count by category
        categories = {}
        for face in DIE_FACES_DATA.values():
            categories[face.category] = categories.get(face.category, 0) + 1

        print("Categories:")
        for category, count in sorted(categories.items()):
            print(f"  - {category}: {count} faces")

        # Validate basic combat faces have proper value ranges
        for face_type in ["ID", "MELEE", "MISSILE", "MAGIC", "SAVE", "MOVE"]:
            faces = get_die_faces_by_type(face_type)
            values = [f.value for f in faces if isinstance(f.value, int)]
            if values:
                print(f"  - {face_type}: values {min(values)}-{max(values)}")

        return True
    except Exception as e:
        print(f"ERROR: Die face validation failed: {e}")
        return False
