from typing import List, Optional


class LocationModel:
    """
    Model for game location data with display name.
    """

    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name

    def __str__(self) -> str:
        return f"{self.display_name}"

    def __repr__(self) -> str:
        return f"LocationModel(name='{self.name}', display_name='{self.display_name}')"


# Location instances
LOCATION_DATA = {
    "HOME": LocationModel(name="HOME", display_name="Home"),
    "FRONTIER": LocationModel(name="FRONTIER", display_name="Frontier"),
    "DUA": LocationModel(name="DUA", display_name="Dead Units Area"),
    "BUA": LocationModel(name="BUA", display_name="Buried Units Area"),
    "RESERVES": LocationModel(name="RESERVES", display_name="Reserves"),
    "SUMMONING_POOL": LocationModel(name="SUMMONING_POOL", display_name="Summoning Pool"),
}


# Helper functions
def get_location(location_name: str) -> Optional[LocationModel]:
    """Get a location by name."""
    location_key = location_name.upper()
    return LOCATION_DATA.get(location_key)


def get_all_location_names() -> List[str]:
    """Get all location names."""
    return list(LOCATION_DATA.keys())


def validate_location_data() -> bool:
    """Validate all location data."""
    try:
        for location_name, location in LOCATION_DATA.items():
            if not isinstance(location, LocationModel):
                print(f"ERROR: {location_name} is not a LocationModel instance")
                return False
            if location.name != location_name:
                print(f"ERROR: Location name mismatch: {location.name} != {location_name}")
                return False

        print(f"✓ All {len(LOCATION_DATA)} locations validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Location validation failed: {e}")
        return False
