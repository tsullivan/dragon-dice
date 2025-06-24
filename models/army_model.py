# models/army_model.py
from typing import List, Dict, Any
from .unit_model import UnitModel


class ArmyModel:
    def __init__(
        self, name: str, army_type: str, location: str = "", max_points: int = 0
    ):
        self.name = name
        self.army_type = army_type
        self.units: List[UnitModel] = []
        self.location = location
        self.max_points = (
            max_points  # Max points this army can have (50% of total force)
        )

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
            "location": self.location,
            "max_points": self.max_points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArmyModel":
        army = cls(
            name=data["name"],
            army_type=data["army_type"],
            location=data.get("location", ""),
            max_points=data.get("max_points", 0),
        )
        army.units = [UnitModel.from_dict(u_data) for u_data in data.get("units", [])]
        return army
