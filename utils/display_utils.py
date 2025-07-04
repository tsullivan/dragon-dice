"""
Utility functions for consistent display of game elements with icons.
Provides centralized formatting for terrain types, army types, and other game elements.
All icon declarations are in constants.py - this module imports what it needs.
"""

from typing import Optional

# Import all icon mappings from constants
import utils.constants as constants
from models.action_model import get_action_icon
from models.army_model import get_army_type_icon
from models.location_model import LOCATION_DATA
from models.terrain_model import TERRAIN_DATA, get_terrain_or_location_icon


def format_terrain_type(terrain_type: str) -> str:
    """
    Format terrain type or location with icon and display name.

    Args:
        terrain_type: The terrain type or location string (e.g., "Coastland", "Frontier", "Home")

    Returns:
        Formatted string with icon prefix (e.g., "🌊 Coastland", "🏔️ Frontier")
    """
    icon = get_terrain_or_location_icon(terrain_type)

    # Use display_name from terrain/location objects
    terrain_key = terrain_type.upper()
    if terrain_key in TERRAIN_DATA:
        terrain = TERRAIN_DATA[terrain_key]
        display_name = terrain.display_name
        return f"{icon} {display_name}"
    if terrain_key in LOCATION_DATA:
        location = LOCATION_DATA[terrain_key]
        display_name = location.display_name
        return f"{icon} {display_name}"
    # Fallback to original terrain_type if not found in constants
    return f"{icon} {terrain_type}"


def format_terrain_name(terrain_name: str, terrain_type: Optional[str] = None) -> str:
    """
    Format terrain name with type icon.

    Args:
        terrain_name: The terrain name (e.g., "Coastland", "Player1 Coastland")
        terrain_type: Optional terrain type for icon selection

    Returns:
        Formatted string with icon prefix
    """
    # Clean the terrain name first
    clean_name = clean_terrain_name(terrain_name)

    # Try to determine terrain type from name if not provided
    if terrain_type is None:
        # Check if the clean name matches any terrain type or location
        terrain_type = clean_name

    icon = get_terrain_or_location_icon(terrain_type)
    return f"{icon} {clean_name}"


def format_army_type(army_type: str) -> str:
    """
    Format army type with icon.

    Args:
        army_type: The army type string (e.g., "Home", "Campaign", "Horde")

    Returns:
        Formatted string with icon prefix (e.g., "🏠 Home")
    """
    icon = get_army_type_icon(army_type)
    return f"{icon} {army_type}" if icon else army_type


def format_army_name(army_name: str, army_type: Optional[str] = None) -> str:
    """
    Format army name with type icon.

    Args:
        army_name: The army name
        army_type: The army type for icon selection

    Returns:
        Formatted string with icon prefix
    """
    if army_type:
        icon = get_army_type_icon(army_type)
        return f"{icon} {army_name}" if icon else army_name
    return army_name


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


def clean_terrain_name(terrain_name: str) -> str:
    """
    Clean terrain name by removing color information in parentheses.

    Args:
        terrain_name: The terrain name (e.g., "Coastland (Blue, Green)" or "Player 1 Coastland (Blue, Green)")

    Returns:
        Cleaned terrain name (e.g., "Coastland" or "Player 1 Coastland")
    """
    # Remove everything in parentheses (colors)
    if "(" in terrain_name and ")" in terrain_name:
        # Find the last occurrence of "(" to handle names like "Player 1 Coastland (Blue, Green)"
        paren_start = terrain_name.rfind("(")
        cleaned_name = terrain_name[:paren_start].strip()
        return cleaned_name
    return terrain_name


def format_terrain_summary(terrain_name: str, terrain_type: str, face_number: int, controller: Optional[str] = None) -> str:
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
    # Clean the terrain name to remove color information
    clean_name = clean_terrain_name(terrain_name)

    # Extract base terrain type and use DISPLAY_NAME from constants
    display_name = clean_name
    if " " in clean_name:
        # Handle names like "Player 1 Coastland" -> extract "Coastland"
        parts = clean_name.split()
        if len(parts) >= 3 and parts[0] == "Player":
            base_terrain = " ".join(parts[2:])
            terrain_key = base_terrain.upper()
            if terrain_key in TERRAIN_DATA:
                terrain = TERRAIN_DATA[terrain_key]
                display_name = terrain.display_name
            else:
                display_name = base_terrain
        else:
            # Check if entire name is a terrain type
            terrain_key = clean_name.upper()
            if terrain_key in TERRAIN_DATA:
                terrain = TERRAIN_DATA[terrain_key]
                display_name = terrain.display_name
    else:
        # Single word - check if it's a known terrain type
        terrain_key = clean_name.upper()
        if terrain_key in TERRAIN_DATA:
            terrain = TERRAIN_DATA[terrain_key]
            display_name = terrain.display_name

    # For terrain types, get_terrain_or_location_icon now returns color icons
    # For locations (HOME, FRONTIER), it returns location icons
    location_icon = get_terrain_or_location_icon(terrain_type)

    # Get terrain color icons separately for terrain names
    terrain_colors = ""
    terrain_key = display_name.upper()
    if terrain_key in TERRAIN_DATA:
        terrain = TERRAIN_DATA[terrain_key]
        terrain_colors = terrain.get_color_string()
    else:
        # Fallback - try to extract base terrain type from complex names
        if " " in display_name:
            parts = display_name.split()
            if len(parts) >= 3 and parts[0] == "Player":
                base_terrain = " ".join(parts[2:])
                base_terrain_key = base_terrain.upper()
                if base_terrain_key in TERRAIN_DATA:
                    terrain = TERRAIN_DATA[base_terrain_key]
                    terrain_colors = terrain.get_color_string()

    face_display = format_terrain_face(face_number)

    if terrain_type.upper() == "FRONTIER":
        return f"{location_icon} Frontier Terrain: {terrain_colors} {display_name} ({face_display})"
    if controller and terrain_type.upper() == "HOME":
        return f"{location_icon} {controller}'s Home: {terrain_colors} {display_name} ({face_display})"
    return f"{terrain_colors} {display_name} ({face_display})"


def format_player_turn_label(player_name: str) -> str:
    """
    Format the player turn label.

    Args:
        player_name: The current player's name

    Returns:
        Formatted player turn string
    """
    return f"👤 {player_name}'s Turn"
