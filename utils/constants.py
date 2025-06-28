# Shared constants for the PySide6 application

# Force Size Options (Points) - Official Dragon Dice v4.01d Rules
FORCE_SIZE_OPTIONS = [15, 24, 30, 36, 60]
DEFAULT_FORCE_SIZE = 24

# Dragon Requirements: 1 dragon per 24 points (or part thereof)
POINTS_PER_DRAGON = 24


def calculate_required_dragons(force_size_points: int) -> int:
    """Calculate required dragons based on force size points.

    Official rules: 1 dragon per 24 points (or part thereof)
    Examples: 15 pts = 1 dragon, 24 pts = 1 dragon, 30 pts = 2 dragons, 60 pts = 3 dragons
    """
    import math

    return math.ceil(force_size_points / POINTS_PER_DRAGON)


ELEMENT_ICONS = {
    "DEATH": ("⬛", "Black"),  # Black square
    "AIR": ("🟦", "Blue"),  # Blue square
    "WATER": ("🟩", "Green"),  # Green square
    "FIRE": ("🟥", "Red"),  # Red square
    "EARTH": ("🟨", "Yellow"),  # Yellow square
    "IVORY": ("🟫", "Ivory"),  # Brown square (representing ivory/bone)
    "WHITE": ("⬜", "White"),  # White square
}

# Structured Data Definitions

TERRAIN_DATA = {
    "COASTLAND": {
        "COLORS": [ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["WATER"][0]],
        "ICON": "🌊",  # Water Wave - Air & Water (blue & green)
        "DISPLAY_NAME": "Coastland",
    },
    "DEADLAND": {
        "COLORS": [ELEMENT_ICONS["DEATH"][0]],
        "ICON": "💀",  # Skull - Death only (black)
        "DISPLAY_NAME": "Deadland",
    },
    "FLATLAND": {
        "COLORS": [ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["EARTH"][0]],
        "ICON": "↔️",  # Left-Right Arrow - Air & Earth (blue & yellow)
        "DISPLAY_NAME": "Flatland",
    },
    "HIGHLAND": {
        "COLORS": [ELEMENT_ICONS["FIRE"][0], ELEMENT_ICONS["EARTH"][0]],
        "ICON": "⛰️",  # Mountain - Fire & Earth (red & yellow)
        "DISPLAY_NAME": "Highland",
    },
    "SWAMPLAND": {
        "COLORS": [ELEMENT_ICONS["WATER"][0], ELEMENT_ICONS["EARTH"][0]],
        "ICON": "🐸",  # Frog - Water & Earth (green & yellow)
        "DISPLAY_NAME": "Swampland",
    },
    "FEYLAND": {
        "COLORS": [ELEMENT_ICONS["WATER"][0], ELEMENT_ICONS["FIRE"][0]],
        "ICON": "🧚",  # Fairy - Water & Fire (green & red)
        "DISPLAY_NAME": "Feyland",
    },
    "WASTELAND": {
        "COLORS": [ELEMENT_ICONS["AIR"][0], ELEMENT_ICONS["FIRE"][0]],
        "ICON": "🏜️",  # Desert - Air & Fire (blue & red)
        "DISPLAY_NAME": "Wasteland",
    },
}

LOCATION_DATA = {
    "HOME": {"ICON": "🏠", "DISPLAY_NAME": "Home"},  # House - player's home terrain
    "FRONTIER": {
        "ICON": "🏔️",  # Mountain Peak - frontier terrain
        "DISPLAY_NAME": "Frontier",
    },
    "DUA": {
        "ICON": "⚡",  # Lightning - Dead Units Area
        "DISPLAY_NAME": "Dead Units Area",
    },
    "BUA": {
        "ICON": "⚰️",  # Coffin - Buried Units Area
        "DISPLAY_NAME": "Buried Units Area",
    },
    "RESERVES": {"ICON": "🏰", "DISPLAY_NAME": "Reserves"},  # Castle - reserves area
    "SUMMONING_POOL": {
        "ICON": "🌀",  # Cyclone - summoning pool
        "DISPLAY_NAME": "Summoning Pool",
    },
}

ARMY_DATA = {
    "HOME": {
        "ICON": "🏰",  # Castle (representing home base)
        "DISPLAY_NAME": "Home",
    },
    "CAMPAIGN": {
        "ICON": "🚩",  # Flag (representing campaign/expedition)
        "DISPLAY_NAME": "Campaign",
    },
    "HORDE": {
        "ICON": "👥",  # Group of people (representing a horde)
        "DISPLAY_NAME": "Horde",
    },
}

ACTION_DATA = {
    "MELEE": {
        "ICON": "⚔️",  # Crossed Swords
        "DISPLAY_NAME": "Melee",
        "SUBSTEPS": {
            "AWAITING_ATTACKER_MELEE_ROLL": {
                "DISPLAY_NAME": "Awaiting Attacker Melee Roll",
                "ORDER": 1,
            },
            "AWAITING_DEFENDER_SAVES": {
                "DISPLAY_NAME": "Awaiting Defender Saves",
                "ORDER": 2,
            },
            "AWAITING_MELEE_COUNTER_ATTACK_ROLL": {
                "DISPLAY_NAME": "Awaiting Melee Counter Attack Roll",
                "ORDER": 3,
            },
        },
    },
    "MISSILE": {
        "ICON": "🏹",  # Bow and Arrow
        "DISPLAY_NAME": "Missile",
        "SUBSTEPS": {
            "AWAITING_ATTACKER_MISSILE_ROLL": {
                "DISPLAY_NAME": "Awaiting Attacker Missile Roll",
                "ORDER": 1,
            },
            "AWAITING_DEFENDER_SAVES": {
                "DISPLAY_NAME": "Awaiting Defender Saves",
                "ORDER": 2,
            },
        },
    },
    "MAGIC": {
        "ICON": "🔮",  # Crystal Ball
        "DISPLAY_NAME": "Magic",
        "SUBSTEPS": {
            "AWAITING_MAGIC_ROLL": {"DISPLAY_NAME": "Awaiting Magic Roll", "ORDER": 1}
        },
    },
    "SAVE": {"ICON": "🛡️", "DISPLAY_NAME": "Save"},  # Shield
    "SAI": {
        "ICON": "💎",  # Diamond (Special Action Icon)
        "DISPLAY_NAME": "Special Action",
    },
    "MANEUVER": {"ICON": "🏃", "DISPLAY_NAME": "Maneuver"},  # Running Person
    "SKIP": {"ICON": "⏭️", "DISPLAY_NAME": "Skip"},  # Fast Forward
}

DRAGON_DATA = {
    "ATTACKS": {
        "CLAW": {
            "ICON": "🗺️",  # Map (representing claw terrain changes)
            "DISPLAY_NAME": "Claw Attack",
        },
        "BITE": {"ICON": "🦷", "DISPLAY_NAME": "Bite Attack"},  # Tooth
        "TAIL": {"ICON": "🐉", "DISPLAY_NAME": "Tail Attack"},  # Dragon
        "BREATH": {"ICON": "🔥", "DISPLAY_NAME": "Breath Attack"},  # Fire
    },
    "TYPES": {
        "RED": {"DISPLAY_NAME": "Red Dragon", "ELEMENT": "FIRE"},
        "BLUE": {"DISPLAY_NAME": "Blue Dragon", "ELEMENT": "AIR"},
        "GREEN": {"DISPLAY_NAME": "Green Dragon", "ELEMENT": "WATER"},
        "BLACK": {"DISPLAY_NAME": "Black Dragon", "ELEMENT": "DEATH"},
        "GOLD": {"DISPLAY_NAME": "Gold Dragon", "ELEMENT": "EARTH"},
        "UNDEAD": {"DISPLAY_NAME": "Undead Dragon", "ELEMENT": "DEATH"},
        "SWAMP": {"DISPLAY_NAME": "Swamp Dragon", "ELEMENT": "WATER"},
        "IVORY": {"DISPLAY_NAME": "Ivory Dragon", "ELEMENT": "IVORY"},
    },
    "DIE_TYPES": {
        "DRAKE": {"DISPLAY_NAME": "Drake", "DESCRIPTION": "Standard dragon die"},
        "WYRM": {"DISPLAY_NAME": "Wyrm", "DESCRIPTION": "Advanced dragon die"},
    },
}

# UI Icons (general interface elements) - uppercase keys
UI_ICONS = {
    "RANDOMIZE": "🎲",  # Die (for randomize buttons)
}

GAME_PHASE_DATA = {
    "EXPIRE_EFFECTS": {"DISPLAY_NAME": "Expire Effects", "ORDER": 1},
    "EIGHTH_FACE": {"DISPLAY_NAME": "Eighth Face", "ORDER": 2},
    "DRAGON_ATTACK": {"DISPLAY_NAME": "Dragon Attack", "ORDER": 3},
    "SPECIES_ABILITIES": {"DISPLAY_NAME": "Species Abilities", "ORDER": 4},
    "FIRST_MARCH": {
        "DISPLAY_NAME": "First March",
        "ORDER": 5,
        "SUBSTEPS": {
            "CHOOSE_ACTING_ARMY": {"DISPLAY_NAME": "Choose Acting Army", "ORDER": 1},
            "DECIDE_MANEUVER": {"DISPLAY_NAME": "Decide Maneuver", "ORDER": 2},
            "AWAITING_MANEUVER_INPUT": {
                "DISPLAY_NAME": "Awaiting Maneuver Input",
                "ORDER": 3,
            },
            "DECIDE_ACTION": {"DISPLAY_NAME": "Decide Action", "ORDER": 4},
            "SELECT_ACTION": {"DISPLAY_NAME": "Select Action", "ORDER": 5},
        },
    },
    "SECOND_MARCH": {
        "DISPLAY_NAME": "Second March",
        "ORDER": 6,
        "SUBSTEPS": {
            "CHOOSE_ACTING_ARMY": {"DISPLAY_NAME": "Choose Acting Army", "ORDER": 1},
            "DECIDE_MANEUVER": {"DISPLAY_NAME": "Decide Maneuver", "ORDER": 2},
            "AWAITING_MANEUVER_INPUT": {
                "DISPLAY_NAME": "Awaiting Maneuver Input",
                "ORDER": 3,
            },
            "DECIDE_ACTION": {"DISPLAY_NAME": "Decide Action", "ORDER": 4},
            "SELECT_ACTION": {"DISPLAY_NAME": "Select Action", "ORDER": 5},
        },
    },
    "RESERVES": {"DISPLAY_NAME": "Reserves", "ORDER": 7},
}

# Constants derived from structured data
TURN_PHASES = list(GAME_PHASE_DATA.keys())
MARCH_STEPS = list(GAME_PHASE_DATA["FIRST_MARCH"]["SUBSTEPS"].keys())

# Dice Icon Types
ICON_MELEE = "MELEE"
ICON_MISSILE = "MISSILE"
ICON_MAGIC = "MAGIC"
ICON_SAVE = "SAVE"
ICON_ID = "ID"
ICON_SAI = "SAI"
ICON_MANEUVER = "MANEUVER"  # Standard maneuver icon
ICON_DRAGON_ATTACK_CLAW = "DRAGON_CLAW"
ICON_DRAGON_ATTACK_BITE = "DRAGON_BITE"
ICON_DRAGON_ATTACK_TAIL = "DRAGON_TAIL"
ICON_DRAGON_BREATH = "DRAGON_BREATH"

# Special Action Icons (SAIs) - Name constants
SAI_BULLSEYE = "BULLSEYE"
SAI_DOUBLER = "DOUBLER"
SAI_TRIPLER = "TRIPLER"
SAI_RECRUIT = "RECRUIT"
SAI_MAGIC_BOLT = "MAGIC_BOLT"

AVAILABLE_DRAGON_TYPES = [
    info["DISPLAY_NAME"] for info in DRAGON_DATA["TYPES"].values()
]
AVAILABLE_DRAGON_DIE_TYPES = [
    info["DISPLAY_NAME"] for info in DRAGON_DATA["DIE_TYPES"].values()
]

# UI Text
NO_UNITS_SELECTED_TEXT = "No units selected."
MANAGE_UNITS_BUTTON_TEXT = "Manage Units"
DEFAULT_ARMY_UNITS_SUMMARY = "Units: 0"

ARMY_TYPES_ALL = list(ARMY_DATA.keys())

# Army/Combat Targeting System uses dynamic identification based on actual game state
# Placeholders removed - see GameStateManager targeting methods

# Effect System Strings
EFFECT_TARGET_TERRAIN = "TERRAIN"
EFFECT_TARGET_ARMY = "ARMY"
EFFECT_DURATION_NEXT_TURN_CASTER = "NEXT_TURN_CASTER"
EFFECT_DURATION_NEXT_TURN_TARGET = "NEXT_TURN_TARGET"

# Default/Fallback UI Strings
DEFAULT_UNKNOWN_VALUE = "Unknown"
DEFAULT_NA_VALUE = "N/A"


# Utility Functions for Centralized Icon Application
def get_terrain_icon(terrain_name: str) -> str:
    """Get terrain icon. Raises KeyError if terrain not found."""
    terrain_key = terrain_name.upper()
    if terrain_key not in TERRAIN_DATA:
        raise KeyError(
            f"Unknown terrain type: '{terrain_name}'. Valid terrains: {
                list(TERRAIN_DATA.keys())}"
        )
    return TERRAIN_DATA[terrain_key]["ICON"]


def get_location_icon(location_name: str) -> str:
    """Get location icon. Raises KeyError if location not found."""
    location_key = location_name.upper()
    if location_key not in LOCATION_DATA:
        raise KeyError(
            f"Unknown location: '{location_name}'. Valid locations: {
                list(LOCATION_DATA.keys())}"
        )
    return LOCATION_DATA[location_key]["ICON"]


def get_terrain_or_location_icon(name: str) -> str:
    """Get icon for terrain type or location, checking both maps. Raises KeyError if not found."""
    name_key = name.upper()

    # Check terrain types first
    if name_key in TERRAIN_DATA:
        return TERRAIN_DATA[name_key]["ICON"]

    # Then check locations
    if name_key in LOCATION_DATA:
        return LOCATION_DATA[name_key]["ICON"]

    # If not found in either, raise error
    valid_names = list(TERRAIN_DATA.keys()) + list(LOCATION_DATA.keys())
    raise KeyError(
        f"Unknown terrain or location: '{
            name}'. Valid options: {valid_names}"
    )


def get_army_type_icon(army_type: str) -> str:
    """Get army type icon. Raises KeyError if army type not found."""
    # Try exact match first (new format)
    army_key = army_type.upper()
    if army_key in ARMY_DATA:
        return ARMY_DATA[army_key]["ICON"]

    # Try case-insensitive match for backward compatibility
    for key in ARMY_DATA.keys():
        if key.upper() == army_type.upper():
            return ARMY_DATA[key]["ICON"]

    raise KeyError(
        f"Unknown army type: '{army_type}'. Valid army types: {
            list(ARMY_DATA.keys())}"
    )


def get_action_icon(action_type: str) -> str:
    """Get action icon. Raises KeyError if action type not found."""
    action_key = action_type.upper()
    if action_key not in ACTION_DATA:
        raise KeyError(
            f"Unknown action type: '{action_type}'. Valid action types: {
                list(ACTION_DATA.keys())}"
        )
    return ACTION_DATA[action_key]["ICON"]


def get_element_icon(element_name: str) -> str:
    """Get element icon. Raises KeyError if element not found."""
    element_key = element_name.upper()
    if element_key not in ELEMENT_ICONS:
        raise KeyError(
            f"Unknown element: '{element_name}'. Valid elements: {
                list(ELEMENT_ICONS.keys())}"
        )
    # Return the icon (first element of tuple)
    return ELEMENT_ICONS[element_key][0]


def get_element_color_name(element_name: str) -> str:
    """Get element color name. Raises KeyError if element not found."""
    element_key = element_name.upper()
    if element_key not in ELEMENT_ICONS:
        raise KeyError(
            f"Unknown element: '{element_name}'. Valid elements: {
                list(ELEMENT_ICONS.keys())}"
        )
    # Return the color name (second element of tuple)
    return ELEMENT_ICONS[element_key][1]


def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon display_name' format for display."""
    terrain_key = terrain_name.upper()
    if terrain_key not in TERRAIN_DATA:
        raise KeyError(f"Unknown terrain type: '{terrain_name}'")
    terrain_info = TERRAIN_DATA[terrain_key]
    return f"{terrain_info['ICON']} {terrain_info['DISPLAY_NAME']}"


def format_army_type_display(army_type: str) -> str:
    """Return 'icon display_name' format for display."""
    # Try exact match first (new format)
    army_key = army_type.upper()
    if army_key in ARMY_DATA:
        army_info = ARMY_DATA[army_key]
        return f"{army_info['ICON']} {army_info['DISPLAY_NAME']}"

    # Try case-insensitive match for backward compatibility
    for key in ARMY_DATA.keys():
        if key.upper() == army_type.upper():
            army_info = ARMY_DATA[key]
            return f"{army_info['ICON']} {army_info['DISPLAY_NAME']}"

    raise KeyError(
        f"Unknown army type: '{army_type}'. Valid types: {list(ARMY_DATA.keys())}"
    )


def format_action_display(action_type: str) -> str:
    """Return 'icon display_name' format for display."""
    # Handle both "MELEE" and "Melee Action" formats
    if "Action" in action_type:
        base_action = action_type.replace(" Action", "").upper()
    else:
        base_action = action_type.upper()

    if base_action not in ACTION_DATA:
        raise KeyError(f"Unknown action type: '{base_action}'")
    action_info = ACTION_DATA[base_action]
    return f"{action_info['ICON']} {action_info['DISPLAY_NAME']}"


def format_element_display(element_name: str) -> str:
    """Return 'icon element_name' format for display."""
    icon = get_element_icon(element_name)
    return f"{icon} {element_name}"
