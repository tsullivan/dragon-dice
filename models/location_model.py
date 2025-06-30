class LocationModel:
    """
    Model for game location data with icon and display name.
    """

    def __init__(self, name: str, icon: str, display_name: str):
        self.name = name
        self.icon = icon
        self.display_name = display_name

    def __str__(self) -> str:
        return f"{self.icon} {self.display_name}"

    def __repr__(self) -> str:
        return f"LocationModel(name='{self.name}', icon='{self.icon}', display_name='{self.display_name}')"


# Location instances
LOCATION_DATA = {
    "HOME": LocationModel(name="HOME", icon="🏠", display_name="Home"),
    "FRONTIER": LocationModel(name="FRONTIER", icon="🏔️", display_name="Frontier"),
    "DUA": LocationModel(name="DUA", icon="⚡", display_name="Dead Units Area"),
    "BUA": LocationModel(name="BUA", icon="⚰️", display_name="Buried Units Area"),
    "RESERVES": LocationModel(name="RESERVES", icon="🏰", display_name="Reserves"),
    "SUMMONING_POOL": LocationModel(
        name="SUMMONING_POOL", icon="🌀", display_name="Summoning Pool"
    ),
}


# Helper functions
def get_location(location_name: str) -> LocationModel:
    """Get a location by name."""
    location_key = location_name.upper()
    return LOCATION_DATA.get(location_key)


def get_all_location_names() -> list[str]:
    """Get all location names."""
    return list(LOCATION_DATA.keys())


def get_location_icon(location_name: str) -> str:
    """Get location icon. Raises KeyError if location not found."""
    location_key = location_name.upper()
    if location_key not in LOCATION_DATA:
        raise KeyError(
            f"Unknown location: '{location_name}'. Valid locations: {list(LOCATION_DATA.keys())}"
        )
    return LOCATION_DATA[location_key].icon


def validate_location_data() -> bool:
    """Validate all location data."""
    try:
        for location_name, location in LOCATION_DATA.items():
            if not isinstance(location, LocationModel):
                print(f"ERROR: {location_name} is not a LocationModel instance")
                return False
            if location.name != location_name:
                print(
                    f"ERROR: Location name mismatch: {location.name} != {location_name}"
                )
                return False

        print(f"✓ All {len(LOCATION_DATA)} locations validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Location validation failed: {e}")
        return False
