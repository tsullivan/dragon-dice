# models/die_face_model.py
from typing import Any, Dict, List, Optional, Tuple

from utils.field_access import strict_get, strict_get_optional

FACE_TYPE_SPECIAL = "SAI"


class DieFaceModel:
    """Represents a single die face with its properties and effects."""

    def __init__(
        self,
        name: str,
        description: str,
        base_value: int = 1,
        face_type: str = FACE_TYPE_SPECIAL,
        display_name: Optional[str] = None,
    ):
        self.name = name
        self.display_name = display_name or name
        self.description = description
        self.face_type = face_type  # ID, MOVE, MELEE, MISSILE, SAVE, MAGIC, SPECIAL
        self.base_value = base_value  # Numeric value for basic faces (0 for special abilities)

    def __repr__(self):
        return f"DieFaceModel(name='{self.name}', type='{self.face_type}', value={self.base_value})"

    def is_basic_face(self) -> bool:
        """Check if this is a basic combat face (ID, Move, Melee, Missile, Save, Magic)."""
        return self.face_type in ["ID", "MOVE", "MELEE", "MISSILE", "SAVE", "MAGIC"]

    def is_special_ability(self) -> bool:
        """Check if this is a special ability face."""
        return self.face_type == FACE_TYPE_SPECIAL

    def calculate_x_value(self, die_type: str) -> int:
        """
        Calculate X-value for SAI effects based on die type and face icons.

        From Special Action Icons rules:
        - On a six-sided die, X = number of icons on the face (stored in base_value)
        - On large equipment/large Dragonkin, X = 3 (fixed)
        - On monster/artifact/medallion/relic/champion, X = 4 (fixed)

        Args:
            die_type: Type of die ("six_sided", "large_equipment", "large_dragonkin",
                     "monster", "artifact", "medallion", "relic", "champion")

        Returns:
            X-value for SAI calculations
        """
        if die_type == "six_sided":
            return self.base_value  # Number of icons on this face
        elif die_type in ["large_equipment", "large_dragonkin"]:
            return 3  # Fixed value per rules
        elif die_type in ["monster", "artifact", "medallion", "relic", "champion"]:
            return 4  # Fixed value per rules
        else:
            # Default to base_value for unknown die types
            return self.base_value

    def get_face_icon(self) -> str:
        """Get display icon for this face type."""
        # Check for specific face name first (for special abilities)
        specific_icon_map = {
            # Dragon faces
            "Jaws": "🐉",
            "Dragon_Breath": "🔥",
            "Claw": "🦅",
            "Claw_Front_Left": "🦅",
            "Claw_Front_Right": "🦅",
            "Claw_Rear_Left": "🦅",
            "Claw_Rear_Right": "🦅",
            "Belly": "🎯",
            "Belly_Front": "🎯",
            "Belly_Rear": "🎯",
            "Tail": "🌪️",
            "Tail_Front": "🌪️",
            "Tail_Middle": "🌪️",
            "Tail_Tip": "🌪️",
            "Wing_Left": "🪶",
            "Wing_Right": "🪶",
            "Treasure": "💎",
            # Special combat abilities
            "Kick": "🦵",
            "Trample": "🐘",
            "Trample_3": "🐘",
            "Trample_4": "🐘",
            "Charge": "🏇",
            "Gore": "🐂",
            "Stomp": "🦶",
            "Bash": "🔨",
            "Rend": "💥",
            "Rend_3": "💥",
            "Rend_4": "💥",
            "Smite": "⚡",
            "Smite_3": "⚡",
            "Smite_4": "⚡",
            # Ranged abilities
            "Bullseye": "🎯",
            "Volley": "🏹",
            "Net": "🕸️",
            "Web": "🕸️",
            # Magic abilities
            "Flame": "🔥",
            "Firebreath": "🔥",
            "Teleport": "🌀",
            "Fly": "🪶",
            "Fly_1": "🪶",
            "Fly_2": "🪶",
            "Fly_3": "🪶",
            "Fly_4": "🪶",
            "Fly_5": "🪶",
            "Poison": "☠️",
            "Sleep": "😴",
            "Charm": "💫",
            "Confuse": "😵",
            "Stun": "💫",
            "Stone": "🗿",
            "Vanish": "👻",
            "Illusion": "🎭",
            # Healing/support
            "Regenerate": "💚",
            "Convert": "🔄",
            "Rise From Ashes": "🔥",
            "Flaming Shield": "🔥",
            "Flaming_Shield_1": "🔥",
            "Flaming_Shield_2": "🔥",
            "Flaming_Shield_3": "🔥",
            "Flaming_Shield_4": "🔥",
            "Scorching_Shield_1": "🔥",
            "Scorching_Shield_2": "🔥",
            "Scorching_Shield_4": "🔥",
            "Frost_Magic_1": "❄️",
            "Frost_Magic_2": "❄️",
            "Frost_Magic_3": "❄️",
            "Frost_Magic_4": "❄️",
            "Cantrip": "✨",
            "Cantrip_3": "✨",
            "Cantrip_4": "✨",
            # Animal abilities
            "Paw": "🐾",
            "Paw_1": "🐾",
            "Paw_2": "🐾",
            "Paw_3": "🐾",
            "Paw_4": "🐾",
            "Hoof": "🐴",
            "Hoof_1": "🐴",
            "Hoof_2": "🐴",
            "Hoof_3": "🐴",
            "Hoof_4": "🐴",
            "Roar": "🦁",
            "Screech": "🦅",
            "Hug": "🤗",
            "Scare": "😱",
            "Swallow": "🐍",
            "Bite": "🐍",
            "Sting": "🐍",
            # Special dragon abilities
            "SFR (Dragonhunter)": "🗡️",
            "SFR (Dragonzealot)": "⚔️",
            "TSR (Dragonmaster)": "🔮",
            # Dragonkin-specific abilities
            "SFR (Dragonkin Champion)": "🗡️",
            "Dragonkin Breath (Champion)": "🐉",
            "Dragonkin Breath (rare)": "🐉",
            "Counter": "🔄",
            "Counter (scorching)": "🔄",
            # Capture abilities
            "Seize": "🤗",
            # Additional special abilities
            "Choke": "💀",
            "Create Fireminions": "🔥",
            "Dispel Magic": "✨",
            "Double Strike": "⚔️",
            "Firecloud": "🔥",
            "Flaming Arrow": "🏹",
            "Frost Breath": "❄️",
            "Frost Cantrip": "❄️",
            "Hypnotic Glare": "👁️",
            "Rise From Ashes": "🔥",
            "Smother": "💨",
            "Surprise": "😲",
            "Trumpet": "🎺",
            "Wild Growth": "🌿",
            "Wither": "💀",
            "Ferry": "⛴️",
            "Firewalking": "🔥",
            "Portal": "🌀",
            "Cloak": "👻",
            "Entangle": "🌿",
            "Howl": "🦁",
            "Wave": "🌊",
            "Galeforce": "💨",
            "Plague": "☠️",
            "Coil": "🐍",
            "Slay": "💀",
            "Scorching Wings": "🔥",
        }

        # Check if we have a specific icon for this face name
        if self.name in specific_icon_map:
            return specific_icon_map[self.name]

        # Check if display_name has a specific icon
        if self.display_name in specific_icon_map:
            return specific_icon_map[self.display_name]

        # Fall back to face type icons
        type_icon_map = {
            "ID": "🆔",
            "MOVE": "🏃",
            "MELEE": "⚔️",
            "MISSILE": "🏹",
            "SAVE": "🛡️",
            "MAGIC": "✨",
            "DRAGON_ATTACK": "🐉",
            "DRAGON_VULNERABLE": "🎯",
            "DRAGON_SPECIAL": "💎",
            FACE_TYPE_SPECIAL: "⭐",
        }
        return strict_get(type_icon_map, self.face_type)

    def get_display_info(self) -> Tuple[str, str, str]:
        """Get display information for this die face.

        Returns:
            tuple: (display_text, background_color, tooltip)
        """
        # Get the icon for this face type
        icon = self.get_face_icon()

        # Show icon, display_name and base_value for die faces
        if self.base_value > 0 and self.is_basic_face():
            display_text = f"{icon} {self.display_name}: {self.base_value}"
        else:
            display_text = f"{icon} {self.display_name}"

        # Color coding by face type
        color_map = {
            "ID": "#FFD700",  # Gold
            "MOVE": "#87CEEB",  # Sky blue
            "MELEE": "#FF6B6B",  # Red
            "MISSILE": "#4ECDC4",  # Teal
            "SAVE": "#95E1D3",  # Light green
            "MAGIC": "#DDA0DD",  # Plum
            FACE_TYPE_SPECIAL: "#F7DC6F",  # Light yellow
        }
        background_color = strict_get(color_map, self.face_type)

        # Tooltip shows description
        tooltip = self.description if self.description else self.display_name

        return display_text, background_color, tooltip

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "face_type": self.face_type,
            "base_value": self.base_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DieFaceModel":
        return cls(
            name=strict_get(data, "name", "DieFaceModel"),
            display_name=strict_get_optional(data, "display_name"),
            description=strict_get(data, "description", "DieFaceModel"),
            face_type=strict_get(data, "face_type", "DieFaceModel"),
            base_value=strict_get(data, "base_value", "DieFaceModel"),
        )


def get_face_icon_by_name(face_name: str) -> str:
    """Get face icon by face name (static helper function)."""
    # For basic face types, determine the face_type from the name
    face_type_map = {
        "Melee": "MELEE",
        "Missile": "MISSILE",
        "Magic": "MAGIC",
        "Save": "SAVE",
        "ID": "ID",
        "Move": "MOVE",
        "Maneuver": "MOVE",  # Alias for Move
        "SAI": "MAGIC",  # SAI is a special magic type
    }

    face_type = strict_get(face_type_map, face_name)

    # Create a temporary face to use the icon lookup
    temp_face = DieFaceModel(name=face_name, display_name=face_name, description="", face_type=face_type)
    return temp_face.get_face_icon()


# Helper function to create basic faces
def _create_basic_face(face_type: str, value: int, display_name: str) -> DieFaceModel:
    """Create a basic face with standardized description."""
    descriptions = {
        "ID": f"Counts as {value} point{'s' if value != 1 else ''} of whatever the owning army is rolling for.",
        "MOVE": f"Counts as {value} movement point{'s' if value != 1 else ''}.",
        "MELEE": f"Counts as {value} melee hit point{'s' if value != 1 else ''}.",
        "MISSILE": f"Counts as {value} missile hit point{'s' if value != 1 else ''}.",
        "SAVE": f"Counts as {value} save point{'s' if value != 1 else ''}.",
        "MAGIC": f"Counts as {value} magic point{'s' if value != 1 else ''}.",
    }

    return DieFaceModel(
        name=f"{face_type}_{value}",
        display_name=display_name,
        description=descriptions[face_type],
        face_type=face_type,
        base_value=value,
    )


# ID Faces
ID_FACES = {
    "ID_1": _create_basic_face("ID", 1, "ID"),
    "ID_2": _create_basic_face("ID", 2, "ID"),
    "ID_3": _create_basic_face("ID", 3, "ID"),
    "ID_4": _create_basic_face("ID", 4, "ID"),
}

# Movement Faces
MOVE_FACES = {
    "Move_1": _create_basic_face("MOVE", 1, "Move"),
    "Move_2": _create_basic_face("MOVE", 2, "Move"),
    "Move_3": _create_basic_face("MOVE", 3, "Move"),
    "Move_4": _create_basic_face("MOVE", 4, "Move"),
    "Move_5": _create_basic_face("MOVE", 5, "Move"),
}

# Melee Faces
MELEE_FACES = {
    "Melee_1": _create_basic_face("MELEE", 1, "Melee"),
    "Melee_2": _create_basic_face("MELEE", 2, "Melee"),
    "Melee_3": _create_basic_face("MELEE", 3, "Melee"),
    "Melee_4": _create_basic_face("MELEE", 4, "Melee"),
    "Melee_5": _create_basic_face("MELEE", 5, "Melee"),
    "Melee_6": _create_basic_face("MELEE", 6, "Melee"),
}

# Missile Faces
MISSILE_FACES = {
    "Missile_1": _create_basic_face("MISSILE", 1, "Missile"),
    "Missile_2": _create_basic_face("MISSILE", 2, "Missile"),
    "Missile_3": _create_basic_face("MISSILE", 3, "Missile"),
    "Missile_4": _create_basic_face("MISSILE", 4, "Missile"),
    "Missile_5": _create_basic_face("MISSILE", 5, "Missile"),
    "Missile_6": _create_basic_face("MISSILE", 6, "Missile"),
}

# Save Faces
SAVE_FACES = {
    "Save_1": _create_basic_face("SAVE", 1, "Save"),
    "Save_2": _create_basic_face("SAVE", 2, "Save"),
    "Save_3": _create_basic_face("SAVE", 3, "Save"),
    "Save_4": _create_basic_face("SAVE", 4, "Save"),
}

# Magic Faces
MAGIC_FACES = {
    "Magic_1": _create_basic_face("MAGIC", 1, "Magic"),
    "Magic_2": _create_basic_face("MAGIC", 2, "Magic"),
    "Magic_3": _create_basic_face("MAGIC", 3, "Magic"),
    "Magic_4": _create_basic_face("MAGIC", 4, "Magic"),
    "Magic_5": _create_basic_face("MAGIC", 5, "Magic"),
    "Magic_6": _create_basic_face("MAGIC", 6, "Magic"),
}

# Movement Variant Faces
MOVEMENT_VARIANT_FACES = {
    "Fly_1": DieFaceModel(
        name="Fly_1",
        display_name="Fly",
        description="During any roll, Fly generates one maneuver or one save result.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Fly_2": DieFaceModel(
        name="Fly_2",
        display_name="Fly",
        description="During any roll, Fly generates two maneuver or two save results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Fly_3": DieFaceModel(
        name="Fly_3",
        display_name="Fly",
        description="During any roll, Fly generates three maneuver or three save results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Fly_4": DieFaceModel(
        name="Fly_4",
        display_name="Fly",
        description="During any roll, Fly generates four maneuver or four save results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Fly_5": DieFaceModel(
        name="Fly_5",
        display_name="Fly",
        description="During any roll, Fly generates five maneuver or five save results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=5,
    ),
    "Hoof_1": DieFaceModel(
        name="Hoof_1",
        display_name="Hoof",
        description="During any roll, Hoof generates one maneuver result.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Hoof_2": DieFaceModel(
        name="Hoof_2",
        display_name="Hoof",
        description="During any roll, Hoof generates two maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Hoof_3": DieFaceModel(
        name="Hoof_3",
        display_name="Hoof",
        description="During any roll, Hoof generates three maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Hoof_4": DieFaceModel(
        name="Hoof_4",
        display_name="Hoof",
        description="During any roll, Hoof generates four maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Paw_1": DieFaceModel(
        name="Paw_1",
        display_name="Paw",
        description="During any roll, Paw generates one maneuver result.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Paw_2": DieFaceModel(
        name="Paw_2",
        display_name="Paw",
        description="During any roll, Paw generates two maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Paw_3": DieFaceModel(
        name="Paw_3",
        display_name="Paw",
        description="During any roll, Paw generates three maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Paw_4": DieFaceModel(
        name="Paw_4",
        display_name="Paw",
        description="During any roll, Paw generates four maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Paw": DieFaceModel(
        name="Paw",
        display_name="Paw",
        description="During any roll, Paw generates six maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=6,
    ),
}

# Defensive Variant Faces
DEFENSIVE_VARIANT_FACES = {
    "Flaming_Shield_1": DieFaceModel(
        name="Flaming_Shield_1",
        display_name="Flaming Shield",
        description="During any roll, Flaming Shield generates one save result. During a save roll against a melee attack, Flaming Shield inflicts one point of damage on the attacking army.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Flaming_Shield_2": DieFaceModel(
        name="Flaming_Shield_2",
        display_name="Flaming Shield",
        description="During any roll, Flaming Shield generates two save results. During a save roll against a melee attack, Flaming Shield inflicts two points of damage on the attacking army.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Flaming_Shield_3": DieFaceModel(
        name="Flaming_Shield_3",
        display_name="Flaming Shield",
        description="During any roll, Flaming Shield generates three save results. During a save roll against a melee attack, Flaming Shield inflicts three points of damage on the attacking army.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Flaming_Shield_4": DieFaceModel(
        name="Flaming_Shield_4",
        display_name="Flaming Shield",
        description="During any roll, Flaming Shield generates four save results. During a save roll against a melee attack, Flaming Shield inflicts four points of damage on the attacking army.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Scorching_Shield_1": DieFaceModel(
        name="Scorching_Shield_1",
        display_name="Scorching Shield",
        description="During any roll, Scorching Shield generates one save result. During a save roll against a melee attack, Scorching Shield inflicts one point of damage on the attacking army with no save possible.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Scorching_Shield_2": DieFaceModel(
        name="Scorching_Shield_2",
        display_name="Scorching Shield",
        description="During any roll, Scorching Shield generates two save results. During a save roll against a melee attack, Scorching Shield inflicts two points of damage on the attacking army with no save possible.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Scorching_Shield_4": DieFaceModel(
        name="Scorching_Shield_4",
        display_name="Scorching Shield",
        description="During any roll, Scorching Shield generates four save results. During a save roll against a melee attack, Scorching Shield inflicts four points of damage on the attacking army with no save possible.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Frost_Magic_1": DieFaceModel(
        name="Frost_Magic_1",
        display_name="Frost Magic",
        description="During any roll, Frost Magic generates one magic result. During a magic action, Frost Magic may count as one magic result used to negate an opposing magic action instead of contributing to the spell casting cost.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=1,
    ),
    "Frost_Magic_2": DieFaceModel(
        name="Frost_Magic_2",
        display_name="Frost Magic",
        description="During any roll, Frost Magic generates two magic results. During a magic action, Frost Magic may count as two magic results used to negate an opposing magic action instead of contributing to the spell casting cost.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=2,
    ),
    "Frost_Magic_3": DieFaceModel(
        name="Frost_Magic_3",
        display_name="Frost Magic",
        description="During any roll, Frost Magic generates three magic results. During a magic action, Frost Magic may count as three magic results used to negate an opposing magic action instead of contributing to the spell casting cost.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Frost_Magic_4": DieFaceModel(
        name="Frost_Magic_4",
        display_name="Frost Magic",
        description="During any roll, Frost Magic generates four magic results. During a magic action, Frost Magic may count as four magic results used to negate an opposing magic action instead of contributing to the spell casting cost.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
}

# Combat Enhancement Faces
COMBAT_ENHANCEMENT_FACES = {
    "Trample_3": DieFaceModel(
        name="Trample_3",
        display_name="Trample",
        description="During any roll, Trample generates three maneuver and three melee results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Trample_4": DieFaceModel(
        name="Trample_4",
        display_name="Trample",
        description="During any roll, Trample generates four maneuver and four melee results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Rend_3": DieFaceModel(
        name="Rend_3",
        display_name="Rend",
        description="During a melee or dragon attack, Rend generates three melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates three maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Rend_4": DieFaceModel(
        name="Rend_4",
        display_name="Rend",
        description="During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Smite_3": DieFaceModel(
        name="Smite_3",
        display_name="Smite",
        description="During a melee attack, Smite inflicts three points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates three melee results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Smite_4": DieFaceModel(
        name="Smite_4",
        display_name="Smite",
        description="During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
    "Cantrip_3": DieFaceModel(
        name="Cantrip_3",
        display_name="Cantrip",
        description="During any roll, Cantrip generates three magic results. During a magic action, you may cast any cantrip spell for free.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=3,
    ),
    "Cantrip_4": DieFaceModel(
        name="Cantrip_4",
        display_name="Cantrip",
        description="During any roll, Cantrip generates four magic results. During a magic action, you may cast any cantrip spell for free.",
        face_type=FACE_TYPE_SPECIAL,
        base_value=4,
    ),
}

# Special Ability Faces (Individual-Targeting)
INDIVIDUAL_TARGET_FACES = {
    "Kick": DieFaceModel(
        name="Kick",
        display_name="Kick",
        description="During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Kick generates four save results.\n* During a dragon attack, Kick generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Gore": DieFaceModel(
        name="Gore",
        display_name="Gore",
        description="During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Gore generates four save results.\n* During a dragon attack, Gore generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Hug": DieFaceModel(
        name="Hug",
        display_name="Hug",
        description="During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Hug generates four save results.\n* During a dragon attack, Hug generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Coil": DieFaceModel(
        name="Coil",
        display_name="Coil",
        description="During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Coil generates four save results.\n* During a dragon attack, Coil generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Slay": DieFaceModel(
        name="Slay",
        display_name="Slay",
        description="During a melee attack, target one unit in the defending army. The target is killed and buried.\n* During a save roll, Slay generates four save results.\n* During a dragon attack, Slay generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Swallow": DieFaceModel(
        name="Swallow",
        display_name="Swallow",
        description="During a melee attack, target one unit in the defending army. The target is killed and buried.\n* During a save roll, Swallow generates four save results.\n* During a dragon attack, Swallow generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Plague": DieFaceModel(
        name="Plague",
        display_name="Plague",
        description="During a melee attack, target one unit in the defending army. The target makes a save roll. If the target does not generate a save result, it is killed.\n* During a save roll, Plague generates four save results.\n* During a dragon attack, Plague generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Bite": DieFaceModel(
        name="Bite",
        display_name="Bite",
        description="During a melee attack, target one unit in the defending army. The target makes a save roll. If the target does not generate a save result, it is killed.\n* During a save roll, Bite generates four save results.\n* During a dragon attack, Bite generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Sting": DieFaceModel(
        name="Sting",
        display_name="Sting",
        description="During a melee attack, target one unit in the defending army. The target makes a save roll. If the target does not generate a save result, it is killed.\n* During a save roll, Sting generates four save results.\n* During a dragon attack, Sting generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Special Ability Faces (Area-Effect)
AREA_EFFECT_FACES = {
    "Howl": DieFaceModel(
        name="Howl",
        display_name="Howl",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets flee to their Reserve Area.\n* During a save roll, Howl generates four save results.\n* During a dragon attack, Howl generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Screech": DieFaceModel(
        name="Screech",
        display_name="Screech",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are stunned.\n* During a save roll, Screech generates four save results.\n* During a dragon attack, Screech generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Wave": DieFaceModel(
        name="Wave",
        display_name="Wave",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are pushed back.\n* During a save roll, Wave generates four save results.\n* During a dragon attack, Wave generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Galeforce": DieFaceModel(
        name="Galeforce",
        display_name="Galeforce",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are moved to their Reserve Area.\n* During a save roll, Galeforce generates four save results.\n* During a dragon attack, Galeforce generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Frost_Breath": DieFaceModel(
        name="Frost_Breath",
        display_name="Frost Breath",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed.\n* During a save roll, Frost Breath generates four save results.\n* During a dragon attack, Frost Breath generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Status Effect Faces
STATUS_EFFECT_FACES = {
    "Sleep": DieFaceModel(
        name="Sleep",
        display_name="Sleep",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets cannot participate in counter-attacks until the end of the turn.\n* During a save roll, Sleep generates four save results.\n* During a dragon attack, Sleep generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Stun": DieFaceModel(
        name="Stun",
        display_name="Stun",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets cannot perform any actions until the end of the turn.\n* During a save roll, Stun generates four save results.\n* During a dragon attack, Stun generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Charm": DieFaceModel(
        name="Charm",
        display_name="Charm",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets join your army until the end of the turn.\n* During a save roll, Charm generates four save results.\n* During a dragon attack, Charm generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Confuse": DieFaceModel(
        name="Confuse",
        display_name="Confuse",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets attack their own army instead.\n* During a save roll, Confuse generates four save results.\n* During a dragon attack, Confuse generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Stone": DieFaceModel(
        name="Stone",
        display_name="Stone",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are turned to stone and cannot act.\n* During a save roll, Stone generates four save results.\n* During a dragon attack, Stone generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Net": DieFaceModel(
        name="Net",
        display_name="Net",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are entangled and cannot move.\n* During a save roll, Net generates four save results.\n* During a dragon attack, Net generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Web": DieFaceModel(
        name="Web",
        display_name="Web",
        description="During a melee attack, target up to two health-worth of units in the defending army. The targets are trapped and cannot act.\n* During a save roll, Web generates four save results.\n* During a dragon attack, Web generates four melee and four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Tactical Movement Faces
TACTICAL_MOVEMENT_FACES = {
    "Teleport": DieFaceModel(
        name="Teleport",
        display_name="Teleport",
        description="During any roll, move this unit to any other terrain where you have an army.\n* During a maneuver roll, Teleport generates four maneuver results.\n* During other rolls, Teleport generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Ferry": DieFaceModel(
        name="Ferry",
        display_name="Ferry",
        description="During any roll, move up to two health-worth of units from this army to any other terrain where you have an army.\n* During a maneuver roll, Ferry generates four maneuver results.\n* During other rolls, Ferry generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Vanish": DieFaceModel(
        name="Vanish",
        display_name="Vanish",
        description="During any roll, move this unit to your Reserve Area.\n* During a maneuver roll, Vanish generates four maneuver results.\n* During other rolls, Vanish generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Firewalking": DieFaceModel(
        name="Firewalking",
        display_name="Firewalking",
        description="During any roll, move this unit to any terrain containing fire where you have an army.\n* During a maneuver roll, Firewalking generates four maneuver results.\n* During other rolls, Firewalking generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Defensive Counter Faces
DEFENSIVE_COUNTER_FACES = {
    "Counter": DieFaceModel(
        name="Counter",
        display_name="Counter",
        description="During a save roll, Counter generates four save results. If this unit survives the attack, it immediately makes a counter-attack against the attacking army.\n* During other rolls, Counter generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Bash": DieFaceModel(
        name="Bash",
        display_name="Bash",
        description="During a save roll, target one unit in the attacking army. The target takes four points of damage.\n* During other rolls, Bash generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Volley": DieFaceModel(
        name="Volley",
        display_name="Volley",
        description="During a save roll against a melee attack, make a missile attack against the attacking army using this unit's missile results.\n* During other rolls, Volley generates four missile results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Regenerate": DieFaceModel(
        name="Regenerate",
        display_name="Regenerate",
        description="During a save roll, this unit heals one point of damage if it has taken any.\n* During other rolls, Regenerate generates four save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Instant Kill/Bury Faces
INSTANT_KILL_FACES = {
    "Flame": DieFaceModel(
        name="Flame",
        display_name="Flame",
        description="During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Entangle": DieFaceModel(
        name="Entangle",
        display_name="Entangle",
        description="During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Firebreath": DieFaceModel(
        name="Firebreath",
        display_name="Firebreath",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are killed and buried.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Poison": DieFaceModel(
        name="Poison",
        display_name="Poison",
        description="During a melee attack, target one unit in the defending army. The target is killed and buried.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Miscellaneous Special Faces
MISC_SPECIAL_FACES = {
    "Bullseye": DieFaceModel(
        name="Bullseye",
        display_name="Bullseye",
        description="During a missile attack, Bullseye inflicts four points of damage to the defending army with no save possible.\n* During a maneuver roll, Bullseye generates four maneuver results.\n* During a dragon attack, Bullseye generates four missile results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Portal": DieFaceModel(
        name="Portal",
        display_name="Portal",
        description="During any roll, move any army from your Reserve Area to this terrain.\n* During a maneuver roll, Portal generates four maneuver results.\n* During other rolls, Portal generates four results of the appropriate type.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Cloak": DieFaceModel(
        name="Cloak",
        display_name="Cloak",
        description="During any roll, Cloak generates four save results. This unit cannot be targeted by spells or special abilities until the end of the turn.\n* During a save roll, Cloak generates four additional save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Additional Special Ability Faces
ADDITIONAL_SPECIAL_FACES = {
    "Charge": DieFaceModel(
        name="Charge",
        display_name="Charge",
        description="During a melee attack, the attacking army counts all Maneuver results as if they were Melee results.\n* Instead of making a regular save roll or a counter-attack, the defending army makes a combination save and melee roll.\n* The attacking army takes damage equal to these melee results. Only save results generated by spells may reduce this damage.\n* Charge has no effect during a counter-attack.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Choke": DieFaceModel(
        name="Choke",
        display_name="Choke",
        description="During a melee attack, when the defending army rolls for saves, target up to four health-worth of units in the that army that rolled an ID result. The target units are killed. Their ID results are not counted towards the army's save results. Note: Choke works outside of the normal sequence of die roll resolution, applying it's effect immediately after the opponent's roll for saves is made, but before they resolve any SAIs",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Convert": DieFaceModel(
        name="Convert",
        display_name="Convert",
        description="During a melee attack, target up to three health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed.\n* The attacking player may return up to the amount of heath-worth killed this way from their DUA to the attacking army.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Counter (scorching)": DieFaceModel(
        name="Counter (scorching)",
        display_name="Counter (scorching)",
        description="During a save roll, Counter (scorching) generates four save results. If this unit survives the attack, it immediately makes a counter-attack against the attacking army with scorching effects.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Create Fireminions": DieFaceModel(
        name="Create Fireminions",
        display_name="Create Fireminions",
        description="During any army roll, Create Fireminions generates four magic, maneuver, melee, missile or save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Dispel Magic": DieFaceModel(
        name="Dispel Magic",
        display_name="Dispel Magic",
        description="Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, its army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Double Strike": DieFaceModel(
        name="Double Strike",
        display_name="Double Strike",
        description="During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Firecloud": DieFaceModel(
        name="Firecloud",
        display_name="Firecloud",
        description="During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Flaming Arrow": DieFaceModel(
        name="Flaming Arrow",
        display_name="Flaming Arrow",
        description="During a missile attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed.\n* Each unit killed must make another save roll. Those that do not generate a save result on this second roll are buried.\n* During a dragon attack, Flaming Arrow generates four missile results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Frost Breath": DieFaceModel(
        name="Frost Breath",
        display_name="Frost Breath",
        description="During a melee or missile attack, target an opposing army at the same terrain. Until the beginning of your next turn, the target army halves all results they roll.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Frost Cantrip": DieFaceModel(
        name="Frost Cantrip",
        display_name="Frost Cantrip",
        description="During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as 'Cantrip' from the spell list.\n* During a magic negation roll, Cantrip generates four anti-magic results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Hypnotic Glare": DieFaceModel(
        name="Hypnotic Glare",
        display_name="Hypnotic Glare",
        description="During a melee attack, when the defending army rolls for saves, all units that roll an ID result are Hypnotized and may not be rolled until the beginning of your next turn. Those ID results are not counted as saves.\n* The effect ends if the glaring unit leaves the terrain, is killed, or is rolled. The glaring unit may be excluded from any roll until the effect expires.\nNote: Hypnotic Glare works outside of the normal sequence of die roll resolution, applying it's effect immediately after the opponent's roll for saves is made, but before they resolve any SAIs",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Illusion": DieFaceModel(
        name="Illusion",
        display_name="Illusion",
        description="During a magic, melee or missile attack, target any of your armies. Until the beginning of your next turn, the target army cannot be targeted by any missile attacks or spells cast by opposing players.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Rise From Ashes": DieFaceModel(
        name="Rise From Ashes",
        display_name="Rise From Ashes",
        description="During a save roll, Rise from the Ashes generates four save results. Whenever a unit with this SAI is killed or buried, roll the unit. If Rise from the Ashes is rolled, the unit is moved to your Reserve Area. If an effect both kills and buries this unit, it may roll once when killed and again when buried. If the first roll is successful, the unit is not buried.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Roar": DieFaceModel(
        name="Roar",
        display_name="Roar",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Scare": DieFaceModel(
        name="Scare",
        display_name="Scare",
        description="During a melee attack, target up to three health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are immediately moved to their Reserve Area before the defending army rolls for saves. Those that roll their ID icon are killed.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Scorching Wings": DieFaceModel(
        name="Scorching Wings",
        display_name="Scorching Wings",
        description="During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Seize": DieFaceModel(
        name="Seize",
        display_name="Seize",
        description="During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Smother": DieFaceModel(
        name="Smother",
        display_name="Smother",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Stomp": DieFaceModel(
        name="Stomp",
        display_name="Stomp",
        description="During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed and must make a save roll. Those that do not generate a save result are buried.\n* During a dragon attack, Stomp generates four melee results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Surprise": DieFaceModel(
        name="Surprise",
        display_name="Surprise",
        description="During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Tail": DieFaceModel(
        name="Tail",
        display_name="Tail",
        description="During a dragon or melee attack, Tail generates two melee results. Roll this unit again and apply the new result as well.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Trumpet": DieFaceModel(
        name="Trumpet",
        display_name="Trumpet",
        description="During a dragon attack, melee attack or save roll, each Feral unit in this army doubles its melee and save results.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Wild Growth": DieFaceModel(
        name="Wild Growth",
        display_name="Wild Growth",
        description="During any non-maneuver roll, Wild Growth generates four save results or allows you to promote four health-worth of units in this army. Results may be split between saves and promotions in any way you choose. Any promotions happen all at once.",
        face_type=FACE_TYPE_SPECIAL,
    ),
    "Wither": DieFaceModel(
        name="Wither",
        display_name="Wither",
        description="During a melee attack, target any opposing army at the same terrain. Until the beginning of your next turn, the targeted army subtracts three results from all rolls it makes.",
        face_type=FACE_TYPE_SPECIAL,
    ),
}

# Combined dictionary of all die faces
ALL_DIE_FACES = {}
ALL_DIE_FACES.update(ID_FACES)
ALL_DIE_FACES.update(MOVE_FACES)
ALL_DIE_FACES.update(MELEE_FACES)
ALL_DIE_FACES.update(MISSILE_FACES)
ALL_DIE_FACES.update(SAVE_FACES)
ALL_DIE_FACES.update(MAGIC_FACES)
ALL_DIE_FACES.update(MOVEMENT_VARIANT_FACES)
ALL_DIE_FACES.update(DEFENSIVE_VARIANT_FACES)
ALL_DIE_FACES.update(COMBAT_ENHANCEMENT_FACES)
ALL_DIE_FACES.update(INDIVIDUAL_TARGET_FACES)
ALL_DIE_FACES.update(AREA_EFFECT_FACES)
ALL_DIE_FACES.update(STATUS_EFFECT_FACES)
ALL_DIE_FACES.update(TACTICAL_MOVEMENT_FACES)
ALL_DIE_FACES.update(DEFENSIVE_COUNTER_FACES)
ALL_DIE_FACES.update(INSTANT_KILL_FACES)
ALL_DIE_FACES.update(MISC_SPECIAL_FACES)
ALL_DIE_FACES.update(ADDITIONAL_SPECIAL_FACES)

# Dragon-specific die faces (moved here to avoid circular import)
DRAGON_DIE_FACES = {
    "Jaws": DieFaceModel(
        name="Jaws",
        display_name="Jaws",
        description="A dragon's jaws inflict twelve points of damage on an army. Also counts as the 'ID' for ID based SAIs that effect Dragons.",
        face_type="DRAGON_ATTACK",
        base_value=12,
    ),
    "Dragon_Breath": DieFaceModel(
        name="Dragon_Breath",
        display_name="Dragon Breath",
        description="Against another dragon, dragon breath inflicts five (ten for a White Dragon) points of damage; roll the dragon again and apply the new result as well.\\n* Against armies, five health-worth of units in the target army are killed.\\n* In addition, an effect based on the color affects the army:\\n** BLACK (Dragon Plague): The army ignores all of its ID results until the beginning of its next turn.\\n** BLUE (Lightning Bolt): The army's melee results are halved until the beginning of its next turn. Results are rounded down.\\n** YELLOW (Petrify): The army's maneuver results are halved until the beginning of its next turn. Results are rounded down.\\n** GREEN (Poisonous Cloud): The army's missile results are halved until the beginning of its next turn. Results are rounded down.\\n** RED (Dragon Fire): Roll the units killed by this dragon's breath attack. Those that do not generate a save result are buried.\\n** IVORY (Life Drain): No additional effect.\\n** WHITE (Terrain Empathy): An additional five health-worth of units in the army are killed. The army is affected by a breath of both colors of the terrain.",
        face_type="DRAGON_ATTACK",
        base_value=5,
    ),
    "Claw_Front_Left": DieFaceModel(
        name="Claw_Front_Left",
        display_name="Claw; Front Left",
        description="A dragon's claws inflict six points of damage on an army.",
        face_type="DRAGON_ATTACK",
        base_value=6,
    ),
    "Claw_Front_Right": DieFaceModel(
        name="Claw_Front_Right",
        display_name="Claw; Front Right",
        description="A dragon's claws inflict six points of damage on an army.",
        face_type="DRAGON_ATTACK",
        base_value=6,
    ),
    "Wing_Left": DieFaceModel(
        name="Wing_Left",
        display_name="Wing; Left",
        description="A dragon's wings inflict five points of damage on an army. After the attack, if the dragon is still alive, it flies away. It returns to it's summoning pool.",
        face_type="DRAGON_ATTACK",
        base_value=5,
    ),
    "Wing_Right": DieFaceModel(
        name="Wing_Right",
        display_name="Wing; Right",
        description="A dragon's wings inflict five points of damage on an army. After the attack, if the dragon is still alive, it flies away. It returns to it's summoning pool.",
        face_type="DRAGON_ATTACK",
        base_value=5,
    ),
    "Belly_Front": DieFaceModel(
        name="Belly_Front",
        display_name="Belly; Front",
        description="The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
        face_type="DRAGON_VULNERABLE",
        base_value=0,
    ),
    "Belly_Rear": DieFaceModel(
        name="Belly_Rear",
        display_name="Belly; Rear",
        description="The dragon's five automatic saves do not count during this attack. In other words, five points of damage will slay the dragon this turn.",
        face_type="DRAGON_VULNERABLE",
        base_value=0,
    ),
    "Claw_Rear_Left": DieFaceModel(
        name="Claw_Rear_Left",
        display_name="Claw; Rear Left",
        description="A dragon's claws inflict six points of damage on an army.",
        face_type="DRAGON_ATTACK",
        base_value=6,
    ),
    "Claw_Rear_Right": DieFaceModel(
        name="Claw_Rear_Right",
        display_name="Claw; Rear Right",
        description="A dragon's claws inflict six points of damage on an army.",
        face_type="DRAGON_ATTACK",
        base_value=6,
    ),
    "Tail_Front": DieFaceModel(
        name="Tail_Front",
        display_name="Tail; Front",
        description="The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
        face_type="DRAGON_ATTACK",
        base_value=3,
    ),
    "Tail_Middle": DieFaceModel(
        name="Tail_Middle",
        display_name="Tail; Middle",
        description="The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
        face_type="DRAGON_ATTACK",
        base_value=3,
    ),
    "Tail_Tip": DieFaceModel(
        name="Tail_Tip",
        display_name="Tail; Tip",
        description="The dragon's tail inflicts three points of damage on an army; roll the dragon again and apply the new results as well.",
        face_type="DRAGON_ATTACK",
        base_value=3,
    ),
    "Treasure": DieFaceModel(
        name="Treasure",
        display_name="Treasure",
        description="One unit in the target army may immediately be promoted.",
        face_type="DRAGON_SPECIAL",
        base_value=0,
    ),
}

ALL_DIE_FACES.update(DRAGON_DIE_FACES)


# Helper functions for die face access
def get_die_face(face_name: str) -> Optional[DieFaceModel]:
    """Get a specific die face by name."""
    return ALL_DIE_FACES.get(face_name)


def get_faces_by_type(face_type: str) -> List[DieFaceModel]:
    """Get all die faces of a specific type."""
    return [face for face in ALL_DIE_FACES.values() if face.face_type == face_type]


def get_basic_faces() -> List[DieFaceModel]:
    """Get all basic die faces (ID, Move, Melee, Missile, Save, Magic)."""
    return [face for face in ALL_DIE_FACES.values() if face.is_basic_face()]


def get_special_ability_faces() -> List[DieFaceModel]:
    """Get all special ability faces."""
    return [face for face in ALL_DIE_FACES.values() if face.is_special_ability()]


def search_faces_by_description(search_term: str) -> List[DieFaceModel]:
    """Search for die faces by description content."""
    search_lower = search_term.lower()
    return [face for face in ALL_DIE_FACES.values() if search_lower in face.description.lower()]


def get_faces_by_value_range(min_value: int, max_value: int) -> List[DieFaceModel]:
    """Get die faces within a specific value range."""
    return [face for face in ALL_DIE_FACES.values() if min_value <= face.base_value <= max_value]


def validate_die_faces() -> bool:
    """Validate that all die face data is consistent."""
    total_faces = len(ALL_DIE_FACES)

    # Check for required fields
    for face_name, face in ALL_DIE_FACES.items():
        if not face.name:
            print(f"ERROR: Die face '{face_name}' has no name")
            return False
        if not face.description:
            print(f"ERROR: Die face '{face_name}' has no description")
            return False
        if not face.face_type:
            print(f"ERROR: Die face '{face_name}' has no face_type")
            return False

    print(f"✓ All {total_faces} die faces validated successfully")
    return True


def get_die_face_statistics() -> Dict[str, Any]:
    """Get statistics about the die face collection."""
    faces_by_type: Dict[str, int] = {}
    value_distribution: Dict[int, int] = {}

    # Count by type
    for face in ALL_DIE_FACES.values():
        face_type = face.face_type
        faces_by_type[face_type] = strict_get(faces_by_type, face_type) + 1

    # Count by value
    for face in ALL_DIE_FACES.values():
        value = face.base_value
        value_distribution[value] = strict_get(value_distribution, value) + 1

    stats = {
        "total_faces": len(ALL_DIE_FACES),
        "faces_by_type": faces_by_type,
        "basic_faces": len(get_basic_faces()),
        "special_faces": len(get_special_ability_faces()),
        "value_distribution": value_distribution,
    }

    return stats
