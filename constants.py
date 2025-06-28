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


ELEMENT_COLORS = {
    "DEATH": "Black",
    "AIR": "Blue",
    "WATER": "Green",
    "FIRE": "Red",
    "EARTH": "Yellow",
    "IVORY": "Ivory",  # Lack of any elements
    "WHITE": "White",  # Presence of all elements
}

# Terrain Definitions (Name, List of Colors from ELEMENT_COLORS values)
TERRAIN_DATA = [
    ("COASTLAND", [ELEMENT_COLORS["AIR"], ELEMENT_COLORS["WATER"]]),
    ("DEADLAND", [ELEMENT_COLORS["DEATH"]]),
    ("FLATLAND", [ELEMENT_COLORS["AIR"], ELEMENT_COLORS["EARTH"]]),
    ("HIGHLAND", [ELEMENT_COLORS["FIRE"], ELEMENT_COLORS["EARTH"]]),
    ("SWAMPLAND", [ELEMENT_COLORS["WATER"], ELEMENT_COLORS["EARTH"]]),
    ("FEYLAND", [ELEMENT_COLORS["WATER"], ELEMENT_COLORS["FIRE"]]),
    ("WASTELAND", [ELEMENT_COLORS["AIR"], ELEMENT_COLORS["FIRE"]]),
]

TERRAIN_ICONS = {
    # Official Dragon Dice terrain types only (uppercase keys)
    "COASTLAND": "🌊",  # Water Wave - Air & Water (blue & green)
    "DEADLAND": "💀",  # Skull - Death only (black)
    "FLATLAND": "↔️",  # Left-Right Arrow - Air & Earth (blue & yellow)
    "HIGHLAND": "⛰️",  # Mountain - Fire & Earth (red & yellow)
    "SWAMPLAND": "🐸",  # Frog - Water & Earth (green & yellow)
    "FEYLAND": "✨",  # Sparkles - Water & Fire (green & red)
    "WASTELAND": "🏜️",  # Desert - Air & Fire (blue & red)
}

# Location/Category Icons (uppercase keys)
LOCATION_ICONS = {
    "HOME": "🏠",  # House - player's home terrain
    "FRONTIER": "🏔️",  # Mountain Peak - frontier terrain
    "DUA": "⚡",  # Lightning - Dead Units Area
    "RESERVES": "🏰",  # Castle - reserves area
    "SUMMONING_POOL": "🌀",  # Cyclone - summoning pool
}

# Army Type Icons - uppercase keys
ARMY_TYPE_ICONS = {
    "HOME": "🏰",  # Castle (representing home base)
    "CAMPAIGN": "🚩",  # Flag (representing campaign/expedition)
    "HORDE": "🌊",  # Wave (representing a horde surge)
}

# Action Icons (centralized from various components) - uppercase keys
ACTION_ICONS = {
    "MELEE": "⚔️",  # Crossed Swords
    "MISSILE": "🏹",  # Bow and Arrow
    "MAGIC": "🔮",  # Crystal Ball (consistent with display_utils)
    "SAVE": "🛡️",  # Shield
    "SAI": "💎",  # Diamond (Special Action Icon)
    "MANEUVER": "🏃",  # Running Person
    "SKIP": "⏭️",  # Fast Forward (from display_utils)
}

# Dragon Attack Icons - uppercase keys
DRAGON_ATTACK_ICONS = {
    "CLAW": "🗺️",  # Map (representing claw terrain changes)
    "BITE": "🦷",  # Tooth
    "TAIL": "🐉",  # Dragon
    "BREATH": "🔥",  # Fire
}

# UI Icons (general interface elements) - uppercase keys
UI_ICONS = {
    "DICE": "🎲",  # Die (from display_utils TERRAIN_FACE_SYMBOL)
    "RANDOMIZE": "🎲",  # Die (for randomize buttons)
}

# Game Phases
PHASE_EXPIRE_EFFECTS = "EXPIRE_EFFECTS"
PHASE_EIGHTH_FACE = "EIGHTH_FACE"
PHASE_DRAGON_ATTACK = "DRAGON_ATTACK"
PHASE_SPECIES_ABILITIES = "SPECIES_ABILITIES"
PHASE_FIRST_MARCH = "FIRST_MARCH"
PHASE_SECOND_MARCH = "SECOND_MARCH"
PHASE_RESERVES = "RESERVES"

TURN_PHASES = [
    PHASE_EXPIRE_EFFECTS,
    PHASE_EIGHTH_FACE,
    PHASE_DRAGON_ATTACK,
    PHASE_SPECIES_ABILITIES,
    PHASE_FIRST_MARCH,
    PHASE_SECOND_MARCH,
    PHASE_RESERVES,
]

# March Steps
MARCH_STEP_CHOOSE_ACTING_ARMY = "CHOOSE_ACTING_ARMY"
MARCH_STEP_DECIDE_MANEUVER = "DECIDE_MANEUVER"
MARCH_STEP_AWAITING_MANEUVER_INPUT = "AWAITING_MANEUVER_INPUT"
MARCH_STEP_DECIDE_ACTION = "DECIDE_ACTION"
MARCH_STEP_SELECT_ACTION = "SELECT_ACTION"

MARCH_STEPS = [
    MARCH_STEP_CHOOSE_ACTING_ARMY,
    MARCH_STEP_DECIDE_MANEUVER,
    MARCH_STEP_AWAITING_MANEUVER_INPUT,
    MARCH_STEP_DECIDE_ACTION,
    MARCH_STEP_SELECT_ACTION,
]

# Action Types
ACTION_MELEE = "MELEE"
ACTION_MISSILE = "MISSILE"
ACTION_MAGIC = "MAGIC"
ACTION_SKIP = "SKIP"

# Action Steps (Sub-steps within an action)
ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL = "AWAITING_ATTACKER_MELEE_ROLL"
ACTION_STEP_AWAITING_DEFENDER_SAVES = "AWAITING_DEFENDER_SAVES"
ACTION_STEP_AWAITING_MELEE_COUNTER_ATTACK_ROLL = "AWAITING_MELEE_COUNTER_ATTACK_ROLL"
ACTION_STEP_AWAITING_ATTACKER_MISSILE_ROLL = "AWAITING_ATTACKER_MISSILE_ROLL"
ACTION_STEP_AWAITING_MAGIC_ROLL = "AWAITING_MAGIC_ROLL"

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

DRAGON_TYPE_RED = "Red Dragon"
DRAGON_TYPE_BLUE = "Blue Dragon"
DRAGON_TYPE_GREEN = "Green Dragon"
DRAGON_TYPE_BLACK = "Black Dragon"
DRAGON_TYPE_GOLD = "Gold Dragon"
DRAGON_TYPE_UNDEAD = "Undead Dragon"
DRAGON_TYPE_SWAMP = "Swamp Dragon"
DRAGON_TYPE_IVORY = "Ivory Dragon"

AVAILABLE_DRAGON_TYPES = [
    DRAGON_TYPE_RED,
    DRAGON_TYPE_BLUE,
    DRAGON_TYPE_GREEN,
    DRAGON_TYPE_BLACK,
    DRAGON_TYPE_GOLD,
    DRAGON_TYPE_UNDEAD,
    DRAGON_TYPE_SWAMP,
    DRAGON_TYPE_IVORY,
]

# Dragon Die Types
DRAGON_DIE_TYPE_DRAKE = "Drake"
DRAGON_DIE_TYPE_WYRM = "Wyrm"

AVAILABLE_DRAGON_DIE_TYPES = [
    DRAGON_DIE_TYPE_DRAKE,
    DRAGON_DIE_TYPE_WYRM,
]

# UI Text
NO_UNITS_SELECTED_TEXT = "No units selected."
MANAGE_UNITS_BUTTON_TEXT = "Manage Units"
DEFAULT_ARMY_UNITS_SUMMARY = "Units: 0"

ARMY_TYPE_HOME = "Home"
ARMY_TYPE_CAMPAIGN = "Campaign"
ARMY_TYPE_HORDE = "Horde"
ARMY_TYPES_ALL = [ARMY_TYPE_HOME, ARMY_TYPE_CAMPAIGN, ARMY_TYPE_HORDE]

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
    if terrain_key not in TERRAIN_ICONS:
        raise KeyError(
            f"Unknown terrain type: '{terrain_name}'. Valid terrains: {
                       list(TERRAIN_ICONS.keys())}"
        )
    return TERRAIN_ICONS[terrain_key]


def get_location_icon(location_name: str) -> str:
    """Get location icon. Raises KeyError if location not found."""
    location_key = location_name.upper()
    if location_key not in LOCATION_ICONS:
        raise KeyError(
            f"Unknown location: '{location_name}'. Valid locations: {
                       list(LOCATION_ICONS.keys())}"
        )
    return LOCATION_ICONS[location_key]


def get_terrain_or_location_icon(name: str) -> str:
    """Get icon for terrain type or location, checking both maps. Raises KeyError if not found."""
    name_key = name.upper()

    # Check terrain types first
    if name_key in TERRAIN_ICONS:
        return TERRAIN_ICONS[name_key]

    # Then check locations
    if name_key in LOCATION_ICONS:
        return LOCATION_ICONS[name_key]

    # If not found in either, raise error
    valid_names = list(TERRAIN_ICONS.keys()) + list(LOCATION_ICONS.keys())
    raise KeyError(
        f"Unknown terrain or location: '{
                   name}'. Valid options: {valid_names}"
    )


def get_army_type_icon(army_type: str) -> str:
    """Get army type icon. Raises KeyError if army type not found."""
    army_key = army_type.upper()
    if army_key not in ARMY_TYPE_ICONS:
        raise KeyError(
            f"Unknown army type: '{army_type}'. Valid army types: {
                       list(ARMY_TYPE_ICONS.keys())}"
        )
    return ARMY_TYPE_ICONS[army_key]


def get_action_icon(action_type: str) -> str:
    """Get action icon. Raises KeyError if action type not found."""
    action_key = action_type.upper()
    if action_key not in ACTION_ICONS:
        raise KeyError(
            f"Unknown action type: '{action_type}'. Valid action types: {
                       list(ACTION_ICONS.keys())}"
        )
    return ACTION_ICONS[action_key]


def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon terrain_name' format for display."""
    icon = get_terrain_icon(terrain_name)
    return f"{icon} {terrain_name}"


def format_army_type_display(army_type: str) -> str:
    """Return 'icon army_type' format for display."""
    icon = get_army_type_icon(army_type)
    return f"{icon} {army_type}"


def format_action_display(action_type: str) -> str:
    """Return 'icon action_type' format for display."""
    # Handle both "MELEE" and "Melee Action" formats
    if "Action" in action_type:
        base_action = action_type.replace(" Action", "").upper()
    else:
        base_action = action_type.upper()

    icon = get_action_icon(base_action)
    return f"{icon} {action_type}"
