"""
Utility functions for consistent display of game elements with icons.
Provides centralized formatting for terrain types, army types, and other game elements.
All icon declarations are in constants.py - this module imports what it needs.
"""

from typing import Optional

# Import all icon mappings from constants
import constants
from models.action_model import get_action_icon
from models.location_model import LOCATION_DATA
from models.terrain_model import TERRAIN_DATA, get_terrain_icon, resolve_terrain_name, get_clean_terrain_display_name


def format_terrain_type(terrain_type: str) -> str:
    """
    Format terrain type or location with icon and display name.

    Args:
        terrain_type: The terrain type or location string (e.g., "Coastland", "Frontier", "Home")

    Returns:
        Formatted string with icon prefix (e.g., "🌊 Coastland", "🏔️ Frontier")
    """
    # For terrains, get color icons; for locations, use empty string
    # Convert display name format to key format if needed (e.g., "Coastland Castle" -> "COASTLAND_CASTLE")
    terrain_key = terrain_type.upper().replace(" ", "_")
    try:
        icon = get_terrain_icon(terrain_key)
    except KeyError:
        # Try with original terrain_type in case it's already in key format
        try:
            icon = get_terrain_icon(terrain_type)
        except KeyError:
            # Handle locations by returning empty string
            icon = ""

    # Use display_name from terrain/location objects
    # Try terrain key first (converted format)
    if terrain_key in TERRAIN_DATA:
        terrain = TERRAIN_DATA[terrain_key]
        display_name = terrain.display_name
        return f"{icon} {display_name}" if icon else display_name

    # Try original terrain_type format
    original_key = terrain_type.upper()
    if original_key in TERRAIN_DATA:
        terrain = TERRAIN_DATA[original_key]
        display_name = terrain.display_name
        return f"{icon} {display_name}" if icon else display_name
    if original_key in LOCATION_DATA:
        location = LOCATION_DATA[original_key]
        display_name = location.display_name
        return f"{icon} {display_name}" if icon else display_name

    # Fallback to original terrain_type if not found in constants
    return f"{icon} {terrain_type}" if icon else terrain_type


def format_terrain_name(terrain_name: str, terrain_type: Optional[str] = None) -> str:
    """
    Format terrain name with type icon.

    Args:
        terrain_name: The terrain name (e.g., "Coastland", "Player1 Coastland")
        terrain_type: Optional terrain type for icon selection

    Returns:
        Formatted string with icon prefix
    """
    # Use terrain model to get clean display name
    clean_name = get_clean_terrain_display_name(terrain_name)

    # Try to determine terrain type from name if not provided
    if terrain_type is None:
        # Check if the clean name matches any terrain type or location
        terrain_type = clean_name

    try:
        icon = get_terrain_icon(terrain_type)
    except KeyError:
        # Handle locations by returning empty string
        icon = ""
    return f"{icon} {clean_name}" if icon else clean_name


def format_terrain_face(face_number: int) -> str:
    """
    Format terrain face number with dice icon.

    Args:
        face_number: The face number (1-8)

    Returns:
        Formatted string with dice icon (e.g., "🎲 Face 3")
    """
    dice_icon = constants.UI_ICONS["RANDOMIZE"]
    return f"{dice_icon} Face {face_number}"


def format_action_type(action_type: str) -> str:
    """
    Format action type with icon.

    Args:
        action_type: The action type (e.g., "MELEE", "MISSILE", "MAGIC")

    Returns:
        Formatted string with icon prefix
    """
    icon = get_action_icon(action_type)
    action_name = action_type.title() if action_type != "SKIP" else "Skip"
    return f"{icon} {action_name}" if icon else action_name


def format_terrain_summary(
    terrain_name: str, terrain_type: str, face_number: int, controller: Optional[str] = None
) -> str:
    """
    Format a complete terrain summary with icons.

    Args:
        terrain_name: The terrain name
        terrain_type: The terrain type
        face_number: The current face number
        controller: Optional controller name

    Returns:
        Formatted terrain summary string
    """
    # Use terrain model to get clean display name and terrain object
    display_name = get_clean_terrain_display_name(terrain_name)
    terrain = resolve_terrain_name(terrain_name)

    # For terrain types, get_terrain_icon returns color icons
    # For locations (HOME, FRONTIER), use empty string
    try:
        location_icon = get_terrain_icon(terrain_type)
    except KeyError:
        # Handle locations by returning empty string
        location_icon = ""

    # Get terrain color icons from resolved terrain object
    terrain_colors = ""
    if terrain:
        terrain_colors = terrain.get_color_string()

    face_display = format_terrain_face(face_number)

    if terrain_type.upper() == "FRONTIER":
        return f"{location_icon} Frontier Terrain: {terrain_colors} {display_name} ({face_display})"
    if controller and terrain_type.upper() == "HOME":
        return f"{location_icon} {controller}'s Home: {terrain_colors} {display_name} ({face_display})"
    return f"{terrain_colors} {display_name} ({face_display})"


def format_terrain_summary_with_description(
    terrain_name: str, terrain_type: str, face_details: str, controller: Optional[str] = None
) -> str:
    """
    Format a complete terrain summary with face description.

    Args:
        terrain_name: The terrain name
        terrain_type: The terrain type
        face_details: Face details including description (e.g., "Face 3: Protects against Magic attacks")
        controller: Optional controller name

    Returns:
        Formatted terrain summary string with face description
    """
    from models.terrain_model import TERRAIN_DATA
    from models.location_model import LOCATION_DATA

    # Use terrain model to get clean display name and terrain object
    display_name = get_clean_terrain_display_name(terrain_name)
    terrain = resolve_terrain_name(terrain_name)

    # For terrain types, get_terrain_icon returns color icons
    # For locations (HOME, FRONTIER), use empty string
    try:
        location_icon = get_terrain_icon(terrain_type)
    except KeyError:
        # Handle locations by returning empty string
        location_icon = ""

    # Get terrain color icons from resolved terrain object
    terrain_colors = ""
    if terrain:
        terrain_colors = terrain.get_color_string()

    if terrain_type.upper() == "FRONTIER":
        return f"{location_icon} Frontier Terrain: {terrain_colors} {display_name} ({face_details})"
    if controller and terrain_type.upper() == "HOME":
        return f"{location_icon} {controller}'s Home: {terrain_colors} {display_name} ({face_details})"
    return f"{terrain_colors} {display_name} ({face_details})"


def format_player_turn_label(player_name: str) -> str:
    """
    Format the player turn label.

    Args:
        player_name: The current player's name

    Returns:
        Formatted player turn string
    """
    return f"👤 {player_name}'s Turn"
