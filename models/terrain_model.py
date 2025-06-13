from typing import List, Tuple
from constants import ELEMENT_COLORS # This import is fine

class Terrain:
    """
    Represents a terrain in the Dragon Dice game.
    Each terrain has a name and one or two associated elemental colors.
    """
    def __init__(self, name: str, colors: List[str]):
        self.name = name
        if not 1 <= len(colors) <= 2:
            raise ValueError("Terrain must have one or two colors.")
        for color in colors:
            if color not in ELEMENT_COLORS.values() and color not in ELEMENT_COLORS.keys():
                 # Allow referencing by element name or color name for flexibility
                actual_color_values = list(ELEMENT_COLORS.values())
                if color not in actual_color_values:
                    raise ValueError(f"Invalid color '{color}'. Must be one of {actual_color_values}")
        self.colors = colors

    def __str__(self) -> str:
        return f"{self.name} ({', '.join(self.colors)})"

    def __repr__(self) -> str:
        return f"Terrain(name='{self.name}', colors={self.colors})"

    def get_elements(self) -> List[str]:
        """Returns the element names associated with the terrain's colors."""
        # This assumes colors in ELEMENT_COLORS are unique, which they are.
        return [element for element, color_name in ELEMENT_COLORS.items() if color_name in self.colors]
