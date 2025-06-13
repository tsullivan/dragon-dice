# Shared constants for the PySide6 application



# Elements and Colors (Rulebook pg. 5)
ELEMENT_COLORS = {
    "Death": "Black",
    "Air": "Blue",
    "Water": "Green",
    "Fire": "Red",
    "Earth": "Yellow",
    "Ivory": "Ivory", # Lack of any elements
    "White": "White"  # Presence of all elements
}

# Terrain Definitions (Name, List of Colors from ELEMENT_COLORS values)
# Rulebook pg. 5
TERRAIN_DATA = [
    ("Coastland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Water"]]),
    ("Deadland", [ELEMENT_COLORS["Death"]]),
    ("Flatland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Earth"]]),
    ("Highland", [ELEMENT_COLORS["Fire"], ELEMENT_COLORS["Earth"]]),
    ("Swampland", [ELEMENT_COLORS["Water"], ELEMENT_COLORS["Earth"]]),
    ("Feyland", [ELEMENT_COLORS["Water"], ELEMENT_COLORS["Fire"]]),
    ("Wasteland", [ELEMENT_COLORS["Air"], ELEMENT_COLORS["Fire"]]),
]