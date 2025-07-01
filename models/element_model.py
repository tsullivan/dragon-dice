from typing import List


class ElementModel:
    """
    Model for element data with icon and color name.
    """

    def __init__(self, name: str, icon: str, color_name: str):
        self.name = name
        self.icon = icon
        self.color_name = color_name

    def __str__(self) -> str:
        return f"{self.icon} {self.name}"

    def __repr__(self) -> str:
        return f"ElementModel(name='{self.name}', icon='{self.icon}', color_name='{self.color_name}')"

    def get_display_format(self) -> str:
        """Return 'icon element_name' format for display."""
        return f"{self.icon} {self.name}"


# Element instances
ELEMENT_DATA = {
    "DEATH": ElementModel(name="DEATH", icon="⬛", color_name="Black"),
    "AIR": ElementModel(name="AIR", icon="🟦", color_name="Blue"),
    "WATER": ElementModel(name="WATER", icon="🟩", color_name="Green"),
    "FIRE": ElementModel(name="FIRE", icon="🟥", color_name="Red"),
    "EARTH": ElementModel(name="EARTH", icon="🟨", color_name="Yellow"),
    "IVORY": ElementModel(name="IVORY", icon="🟫", color_name="Ivory"),
    "WHITE": ElementModel(name="WHITE", icon="⬜", color_name="White"),
}


# Helper functions
def get_element(element_name: str) -> ElementModel:
    """Get an element by name."""
    element_key = element_name.upper()
    return ELEMENT_DATA.get(element_key)


def get_all_element_names() -> List[str]:
    """Get all element names."""
    return list(ELEMENT_DATA.keys())


def get_element_icon(element_name: str) -> str:
    """Get element icon. Raises KeyError if element not found."""
    element_key = element_name.upper()
    if element_key not in ELEMENT_DATA:
        raise KeyError(
            f"Unknown element: '{element_name}'. Valid elements: {
                list(ELEMENT_DATA.keys())}"
        )
    return ELEMENT_DATA[element_key].icon


def get_element_color_name(element_name: str) -> str:
    """Get element color name. Raises KeyError if element not found."""
    element_key = element_name.upper()
    if element_key not in ELEMENT_DATA:
        raise KeyError(
            f"Unknown element: '{element_name}'. Valid elements: {
                list(ELEMENT_DATA.keys())}"
        )
    return ELEMENT_DATA[element_key].color_name


def format_element_display(element_name: str) -> str:
    """Return 'icon element_name' format for display."""
    element = get_element(element_name)
    if not element:
        raise KeyError(
            f"Unknown element: '{element_name}'. Valid elements: {get_all_element_names()}"
        )
    return element.get_display_format()


def get_elements_by_color(color_name: str) -> List[ElementModel]:
    """Get all elements that have a specific color name."""
    return [
        element
        for element in ELEMENT_DATA.values()
        if element.color_name.lower() == color_name.lower()
    ]


def validate_element_data() -> bool:
    """Validate all element data."""
    try:
        for element_name, element in ELEMENT_DATA.items():
            if not isinstance(element, ElementModel):
                print(f"ERROR: {element_name} is not an ElementModel instance")
                return False
            if element.name != element_name:
                print(f"ERROR: Element name mismatch: {element.name} != {element_name}")
                return False
            if not element.icon or not element.color_name:
                print(f"ERROR: Element {element_name} missing icon or color_name")
                return False

        print(f"✓ All {len(ELEMENT_DATA)} elements validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Element validation failed: {e}")
        return False
