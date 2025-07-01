# Shared constants for the PySide6 application

# Force Size Options (Points) - Official Dragon Dice v4.01d Rules
FORCE_SIZE_OPTIONS = [15, 24, 30, 36, 60]
DEFAULT_FORCE_SIZE = 24

# Dragon Requirements: 1 dragon per 24 points (or part thereof)
POINTS_PER_DRAGON = 24

# Import data from models
from models.element_model import (
    ELEMENT_DATA,
    get_element_icon,
    get_element_color_name,
    format_element_display,
)
from models.army_model import ARMY_DATA, get_army_type_icon
from models.action_model import ACTION_DATA, get_action_icon, format_action_display
from models.dragon_model import (
    DRAGON_DATA,
    get_available_dragon_types,
)
from models.game_phase_model import GAME_PHASE_DATA, get_turn_phases, get_march_steps
from models.terrain_model import (
    TERRAIN_DATA,
    get_terrain_icon,
    get_terrain_or_location_icon,
    format_terrain_display,
)


# Structured Data Definitions


# UI Icons (general interface elements) - uppercase keys
UI_ICONS = {
    "RANDOMIZE": "🎲",  # Die (for randomize buttons)
}


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

# Dragon constants
AVAILABLE_DRAGON_TYPES = get_available_dragon_types()
AVAILABLE_DRAGON_DIE_TYPES = [dragon.display_name for dragon in DRAGON_DATA.values()]

# Game phase constants
TURN_PHASES = get_turn_phases()
MARCH_STEPS = get_march_steps()

# Army constants
ARMY_TYPES_ALL = list(ARMY_DATA.keys())


# Dragon calculation function
def calculate_required_dragons(force_size_points: int) -> int:
    """Calculate required dragons based on force size points.

    Official rules: 1 dragon per 24 points (or part thereof)
    Examples: 15 pts = 1 dragon, 24 pts = 1 dragon, 30 pts = 2 dragons, 60 pts = 3 dragons
    """
    import math

    return math.ceil(force_size_points / POINTS_PER_DRAGON)


# UI Text
NO_UNITS_SELECTED_TEXT = "No units selected."
MANAGE_UNITS_BUTTON_TEXT = "Manage Units"
DEFAULT_ARMY_UNITS_SUMMARY = "Units: 0"


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
