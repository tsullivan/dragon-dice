# models/army_model.py
from typing import Any, Dict, List, Optional, Union

from .location_model import LocationModel, get_location
from .unit_model import UnitModel


class ArmyModel:
    def __init__(
        self, name: str, army_type: str, location: Union[str, LocationModel, None] = None, max_points: int = 0
    ):
        self.name = name
        self.army_type = army_type
        self.units: List[UnitModel] = []
        self.location = self._process_location(location)
        self.max_points = max_points  # Max points this army can have (50% of total force)
        self.display_name = self._get_display_name()

    def _process_location(self, location: Union[str, LocationModel, None]) -> Optional[LocationModel]:
        """Convert location input to LocationModel if possible, otherwise store as string."""
        if location is None:
            return None
        if isinstance(location, LocationModel):
            return location
        if isinstance(location, str):
            # Try to get a LocationModel if it's a known location name
            location_model = get_location(location)
            if location_model:
                return location_model
            # For terrain names or custom locations, we'll store as string in a custom LocationModel
            return LocationModel(name=location.upper().replace(" ", "_"), display_name=location)
        raise ValueError(f"Invalid location type: {type(location)}")

    def _get_display_name(self) -> str:
        """Get the display name for this army type."""
        army_key = self.army_type.upper()
        if army_key in ARMY_DATA:
            return ARMY_DATA[army_key]["display_name"]
        # Fallback to army_type if not found - should add to ARMY_DATA instead
        return self.army_type.replace("_", " ").title()

    def get_location_name(self) -> str:
        """Get the location name as a string for compatibility."""
        if self.location is None:
            return ""
        return self.location.display_name

    def get_total_points(self) -> int:
        """Calculate total points used by units in this army (using max_health as point cost)."""
        return sum(unit.max_health for unit in self.units)

    def add_unit(self, unit: UnitModel) -> bool:
        """Add unit to army with official Dragon Dice validation rules."""
        if self.max_points > 0:
            # Check if adding this unit would exceed 50% army limit
            new_total = self.get_total_points() + unit.max_health
            if new_total > self.max_points:
                return False

        self.units.append(unit)
        return True

    def remove_unit(self, unit_id: str):
        self.units = [u for u in self.units if u.unit_id != unit_id]

    def __repr__(self):
        return f"ArmyModel(name='{self.name}', type='{self.army_type}', units={len(self.units)})"

    def has_minimum_units(self) -> bool:
        """Check if army has at least one unit (official Dragon Dice rule)."""
        return len(self.units) >= 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "army_type": self.army_type,
            "units": [unit.to_dict() for unit in self.units],
            "location": self.get_location_name(),  # Store as string for serialization
            "max_points": self.max_points,
            "display_name": self.display_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmyModel":
        army = cls(
            name=data["name"],
            army_type=data["army_type"],
            location=data.get("location"),
            max_points=data.get("max_points", 0),
        )
        army.units = [UnitModel.from_dict(u_data) for u_data in data.get("units", [])]
        # display_name will be automatically set by __init__
        return army


# Army type data
ARMY_DATA = {
    "HOME": {
        "name": "HOME",
        "display_name": "Home",
    },
    "CAMPAIGN": {
        "name": "CAMPAIGN",
        "display_name": "Campaign",
    },
    "HORDE": {
        "name": "HORDE",
        "display_name": "Horde",
    },
}


# Helper functions for army types


def get_army_display_name(army_type: str) -> str:
    """Return just the display_name without icon for army type."""
    army_key = army_type.upper()
    if army_key in ARMY_DATA:
        return ARMY_DATA[army_key]["display_name"]

    # Try case-insensitive match
    for key in ARMY_DATA:
        if key.upper() == army_type.upper():
            return ARMY_DATA[key]["display_name"]

    raise KeyError(f"Unknown army type: '{army_type}'. Valid types: {list(ARMY_DATA.keys())}")


def get_all_army_types() -> List[str]:
    """Get all army type names."""
    return list(ARMY_DATA.keys())


def validate_army_data() -> bool:
    """Validate all army data."""
    try:
        for army_name, army_info in ARMY_DATA.items():
            required_fields = ["name", "display_name"]
            for field in required_fields:
                if field not in army_info:
                    print(f"ERROR: Missing {field} in {army_name}")
                    return False
            if army_info["name"] != army_name:
                print(f"ERROR: Army name mismatch: {army_info['name']} != {army_name}")
                return False

        print(f"✓ All {len(ARMY_DATA)} army types validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Army data validation failed: {e}")
        return False
