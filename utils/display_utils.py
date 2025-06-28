"""
Utility functions for consistent display of game elements with icons.
Provides centralized formatting for terrain types, army types, and other game elements.
All icon declarations are in constants.py - this module imports what it needs.
"""

# Import all icon mappings from constants
import utils.constants as constants


def format_terrain_type(terrain_type: str) -> str:
    """
    Format terrain type or location with icon.

    Args:
        terrain_type: The terrain type or location string (e.g., "Coastland", "Frontier", "Home")

    Returns:
        Formatted string with icon prefix (e.g., "🌊 Coastland", "🏔️ Frontier")
    """
    icon = constants.get_terrain_or_location_icon(terrain_type)
    return f"{icon} {terrain_type}"


def format_terrain_name(terrain_name: str, terrain_type: str = None) -> str:
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

    icon = constants.get_terrain_or_location_icon(terrain_type)
    return f"{icon} {clean_name}"


def format_army_type(army_type: str) -> str:
    """
    Format army type with icon.

    Args:
        army_type: The army type string (e.g., "Home", "Campaign", "Horde")

    Returns:
        Formatted string with icon prefix (e.g., "🏠 Home")
    """
    icon = constants.get_army_type_icon(army_type)
    return f"{icon} {army_type}" if icon else army_type


def format_army_name(army_name: str, army_type: str = None) -> str:
    """
    Format army name with type icon.

    Args:
        army_name: The army name
        army_type: The army type for icon selection

    Returns:
        Formatted string with icon prefix
    """
    if army_type:
        icon = constants.get_army_type_icon(army_type)
        return f"{icon} {army_name}" if icon else army_name
    else:
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
    icon = constants.get_action_icon(action_type)
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


def format_terrain_summary(
    terrain_name: str, terrain_type: str, face_number: int, controller: str = None
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
    # Clean the terrain name to remove color information
    clean_name = clean_terrain_name(terrain_name)

    terrain_icon = constants.get_terrain_or_location_icon(terrain_type)
    face_display = format_terrain_face(face_number)

    if terrain_type.upper() == "FRONTIER":
        return f"{terrain_icon} {clean_name} ({face_display}) - Frontier Terrain"
    elif controller and terrain_type.upper() == "HOME":
        return f"{terrain_icon} {clean_name} ({face_display}) - {controller}'s Home"
    else:
        return f"{terrain_icon} {clean_name} ({face_display})"


def format_player_turn_label(player_name: str) -> str:
    """
    Format the player turn label.

    Args:
        player_name: The current player's name

    Returns:
        Formatted player turn string
    """
    return f"👤 {player_name}'s Turn"
