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
    "Death": "Black",
    "Air": "Blue",
    "Water": "Green",
    "Fire": "Red",
    "Earth": "Yellow",
    "Ivory": "Ivory",  # Lack of any elements
    "White": "White",  # Presence of all elements
}

# Terrain Definitions (Name, List of Colors from ELEMENT_COLORS values)
TERRAIN_DATA = [
    ("Coastland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Water"]]),
    ("Deadland", [ELEMENT_COLORS["Death"]]),
    ("Flatland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Earth"]]),
    ("Highland", [ELEMENT_COLORS["Fire"], ELEMENT_COLORS["Earth"]]),
    ("Swampland", [ELEMENT_COLORS["Water"], ELEMENT_COLORS["Earth"]]),
    ("Feyland", [ELEMENT_COLORS["Water"], ELEMENT_COLORS["Fire"]]),
    ("Wasteland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Fire"]]),
]

TERRAIN_ICONS = {
    "Coastland": "🌊",  # Water Wave
    "Deadland": "💀",  # Skull
    "Flatland": "↔️",  # Left-Right Arrow (representing open space)
    "Highland": "⛰️",  # Mountain
    "Swampland": "🐸",  # Frog (or some other swampy icon)
    "Feyland": "✨",  # Sparkles
    "Wasteland": "🏜️",  # Desert
}

# Army Type Icons
ARMY_TYPE_ICONS = {
    "home": "🏰",  # Castle (representing home base)
    "campaign": "🚩",  # Flag (representing campaign/expedition)
    "horde": "🌊",  # Wave (representing a horde surge)
}

# Action Icons (centralized from various components)
ACTION_ICONS = {
    "MELEE": "⚔️",  # Crossed Swords
    "MISSILE": "🏹",  # Bow and Arrow
    "MAGIC": "✨",  # Sparkles
    "SAVE": "🛡️",  # Shield
    "SAI": "💎",  # Diamond (Special Action Icon)
    "MANEUVER": "🏃",  # Running Person
}

# Dragon Attack Icons
DRAGON_ATTACK_ICONS = {
    "CLAW": "🗺️",  # Map (representing claw terrain changes)
    "BITE": "🦷",  # Tooth
    "TAIL": "🐉",  # Dragon
    "BREATH": "🔥",  # Fire
}

# UI Icons (general interface elements)
UI_ICONS = {
    "DICE": "🎲",  # Die
    "DEFAULT_TERRAIN": "🗺️",  # Map (fallback for unknown terrains)
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


# Utility Functions for Centralized Emoji Application
def get_terrain_icon(terrain_name: str) -> str:
    """Get terrain icon with fallback to default."""
    return TERRAIN_ICONS.get(terrain_name, UI_ICONS["DEFAULT_TERRAIN"])


def get_army_type_icon(army_type: str) -> str:
    """Get army type icon with fallback to empty string."""
    # Convert display names to lowercase keys
    army_key = army_type.lower()
    return ARMY_TYPE_ICONS.get(army_key, "")


def get_action_icon(action_type: str) -> str:
    """Get action icon with fallback to empty string."""
    return ACTION_ICONS.get(action_type.upper(), "")


def format_terrain_display(terrain_name: str) -> str:
    """Return 'icon terrain_name' format for display."""
    icon = get_terrain_icon(terrain_name)
    return f"{icon} {terrain_name}" if icon else terrain_name


def format_army_type_display(army_type: str) -> str:
    """Return 'icon army_type' format for display."""
    icon = get_army_type_icon(army_type)
    return f"{icon} {army_type}" if icon else army_type


def format_action_display(action_type: str) -> str:
    """Return 'icon action_type' format for display."""
    # Handle both "MELEE" and "Melee Action" formats
    if "Action" in action_type:
        base_action = action_type.replace(" Action", "").upper()
    else:
        base_action = action_type.upper()

    icon = get_action_icon(base_action)
    return f"{icon} {action_type}" if icon else action_type
