"""
Utility functions for consistent display of game elements with emojis.
Provides centralized formatting for terrain types, army types, and other game elements.
"""

# Terrain type emoji mappings (consistent with constants.py where applicable)
TERRAIN_EMOJIS = {
    "Frontier": "🏔️",
    "Home": "🏠", 
    "Forest": "🌲",
    "Plains": "🌾",
    "Mountain": "⛰️",
    "Swamp": "🐸", 
    "Coastland": "🌊",
    "Highlands": "⛰️",
    "Highland": "⛰️",
    "Badlands": "🏜️",
    "Deadland": "💀",
    "Flatland": "↔️",
    "Swampland": "🐸",
    "Feyland": "✨",
    "Wasteland": "🏜️",
    "Frozen Wastes": "❄️"
}

# Army type emoji mappings (consistent with constants.py)
ARMY_EMOJIS = {
    "Home": "🏰",
    "Campaign": "🚩", 
    "Horde": "🌊",
    "home": "🏰", 
    "campaign": "🚩",
    "horde": "🌊"
}

# Terrain face symbols
TERRAIN_FACE_SYMBOL = "🎲"

# Action type emojis (already defined in constants, but centralized here)
ACTION_EMOJIS = {
    "MELEE": "⚔️",
    "MISSILE": "🏹", 
    "MAGIC": "🔮",
    "SKIP": "⏭️"
}


def format_terrain_type(terrain_type: str) -> str:
    """
    Format terrain type with emoji.
    
    Args:
        terrain_type: The terrain type string (e.g., "Frontier", "Home")
        
    Returns:
        Formatted string with emoji prefix (e.g., "🏔️ Frontier")
    """
    emoji = TERRAIN_EMOJIS.get(terrain_type, "🌍")
    return f"{emoji} {terrain_type}"


def format_terrain_name(terrain_name: str, terrain_type: str = None) -> str:
    """
    Format terrain name with type emoji.
    
    Args:
        terrain_name: The terrain name (e.g., "Mountain", "Player1 Forest")
        terrain_type: Optional terrain type for emoji selection
        
    Returns:
        Formatted string with emoji prefix
    """
    # Clean the terrain name first
    clean_name = clean_terrain_name(terrain_name)
    
    # Try to determine terrain type from name if not provided
    if terrain_type is None:
        if any(home_terrain in terrain_name for home_terrain in ["Forest", "Plains", "Mountain", "Swamp", "Coastland", "Highlands", "Badlands", "Frozen Wastes"]):
            # Extract the base terrain type from compound names like "Player1 Forest"
            for terrain_key in TERRAIN_EMOJIS.keys():
                if terrain_key in terrain_name:
                    terrain_type = terrain_key
                    break
            if terrain_type is None:
                terrain_type = "Home"  # Default for player terrains
        else:
            terrain_type = "Frontier"  # Default for non-player terrains
    
    emoji = TERRAIN_EMOJIS.get(terrain_type, "🌍")
    return f"{emoji} {clean_name}"


def format_army_type(army_type: str) -> str:
    """
    Format army type with emoji.
    
    Args:
        army_type: The army type string (e.g., "Home", "Campaign", "Horde")
        
    Returns:
        Formatted string with emoji prefix (e.g., "🏠 Home")
    """
    emoji = ARMY_EMOJIS.get(army_type, "🛡️")
    return f"{emoji} {army_type}"


def format_army_name(army_name: str, army_type: str = None) -> str:
    """
    Format army name with type emoji.
    
    Args:
        army_name: The army name
        army_type: The army type for emoji selection
        
    Returns:
        Formatted string with emoji prefix
    """
    if army_type:
        emoji = ARMY_EMOJIS.get(army_type, "🛡️")
        return f"{emoji} {army_name}"
    else:
        return f"🛡️ {army_name}"


def format_terrain_face(face_number: int) -> str:
    """
    Format terrain face number with dice emoji.
    
    Args:
        face_number: The face number (1-8)
        
    Returns:
        Formatted string with dice emoji (e.g., "🎲 Face 3")
    """
    return f"{TERRAIN_FACE_SYMBOL} Face {face_number}"


def format_action_type(action_type: str) -> str:
    """
    Format action type with emoji.
    
    Args:
        action_type: The action type (e.g., "MELEE", "MISSILE", "MAGIC")
        
    Returns:
        Formatted string with emoji prefix
    """
    emoji = ACTION_EMOJIS.get(action_type, "⚡")
    action_name = action_type.title() if action_type != "SKIP" else "Skip"
    return f"{emoji} {action_name}"


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


def format_terrain_summary(terrain_name: str, terrain_type: str, face_number: int, controller: str = None) -> str:
    """
    Format a complete terrain summary with emojis.
    
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
    
    terrain_emoji = TERRAIN_EMOJIS.get(terrain_type, "🌍")
    face_display = format_terrain_face(face_number)
    
    if terrain_type == "Frontier":
        return f"{terrain_emoji} {clean_name} ({face_display}) - Frontier Terrain"
    elif controller and terrain_type == "Home":
        return f"{terrain_emoji} {clean_name} ({face_display}) - {controller}'s Home"
    else:
        return f"{terrain_emoji} {clean_name} ({face_display})"


def format_player_turn_label(player_name: str) -> str:
    """
    Format the player turn label.
    
    Args:
        player_name: The current player's name
        
    Returns:
        Formatted player turn string
    """
    return f"👤 {player_name}'s Turn"