from typing import List, Tuple
import utils.constants as constants


class Terrain:
    """
    Represents a terrain in the Dragon Dice game.
    Each terrain has a name and one or two associated elemental colors.
    """

    def __init__(self, name: str, colors: List[str]):
        self.name = name
        if not 1 <= len(colors) <= 2:
            raise ValueError("Terrain must have one or two colors.")
        # Get all valid element icons and color names from ELEMENT_ICONS
        valid_icons = [icon_data[0] for icon_data in constants.ELEMENT_ICONS.values()]
        valid_color_names = [
            icon_data[1] for icon_data in constants.ELEMENT_ICONS.values()
        ]
        valid_element_names = list(constants.ELEMENT_ICONS.keys())

        for color in colors:
            if (
                color not in valid_icons
                and color not in valid_color_names
                and color not in valid_element_names
            ):
                raise ValueError(
                    f"Invalid color/icon '{color}'. Must be one of {valid_color_names} or {valid_icons}"
                )
        self.colors = colors

    def __str__(self) -> str:
        return f"{self.name} ({', '.join(self.colors)})"

    def __repr__(self) -> str:
        return f"Terrain(name='{self.name}', colors={self.colors})"

    def get_elements(self) -> List[str]:
        """Returns the element names associated with the terrain's colors."""
        return [
            element
            for element, (icon, color_name) in constants.ELEMENT_ICONS.items()
            if color_name in self.colors or icon in self.colors
        ]
