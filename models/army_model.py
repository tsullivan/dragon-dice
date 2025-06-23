# models/army_model.py
from typing import List, Dict, Any
from .unit_model import UnitModel

class ArmyModel:
    def __init__(self, name: str, army_type: str, location: str = ""):
        self.name = name
        self.army_type = army_type
        self.units: List[UnitModel] = []
        self.location = location

    def add_unit(self, unit: UnitModel) -> bool:
        # Point validation removed
        self.units.append(unit)
        return True

    def remove_unit(self, unit_id: str):
        self.units = [u for u in self.units if u.unit_id != unit_id]

    def __repr__(self):
        return f"ArmyModel(name='{self.name}', type='{self.army_type}', units={len(self.units)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "army_type": self.army_type,
            "units": [unit.to_dict() for unit in self.units],
            "location": self.location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArmyModel':
        army = cls(name=data["name"], army_type=data["army_type"], location=data.get("location", ""))
        army.units = [UnitModel.from_dict(u_data) for u_data in data.get("units", [])]
        return army