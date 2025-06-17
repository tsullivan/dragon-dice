# models/army_model.py
from typing import List, Dict, Any
from .unit_model import UnitModel

class ArmyModel:
    def __init__(self, name: str, army_type: str, allocated_points: int, location: str = ""):
        self.name = name
        self.army_type = army_type
        self.allocated_points = allocated_points
        self.units: List[UnitModel] = []
        self.location = location

    def add_unit(self, unit: UnitModel) -> bool:
        if self.current_points_total() + unit.points_cost <= self.allocated_points:
            self.units.append(unit)
            return True
        print(f"Cannot add unit {unit.name} ({unit.points_cost} pts). Army '{self.name}' points exceed limit ({self.current_points_total() + unit.points_cost}/{self.allocated_points}).")
        return False

    def remove_unit(self, unit_id: str):
        self.units = [u for u in self.units if u.unit_id != unit_id]

    def current_points_total(self) -> int:
        return sum(unit.points_cost for unit in self.units)

    def __repr__(self):
        return f"ArmyModel(name='{self.name}', type='{self.army_type}', points={self.current_points_total()}/{self.allocated_points}, units={len(self.units)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "army_type": self.army_type,
            "allocated_points": self.allocated_points,
            "units": [unit.to_dict() for unit in self.units],
            "location": self.location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArmyModel':
        army = cls(name=data["name"], army_type=data["army_type"], allocated_points=data["allocated_points"], location=data.get("location", ""))
        army.units = [UnitModel.from_dict(u_data) for u_data in data.get("units", [])]
        return army