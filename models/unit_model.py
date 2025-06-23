# models/unit_model.py
from typing import Dict, Any
import constants

class UnitModel:
    def __init__(self, unit_id: str, name: str, unit_type: str, health: int, max_health: int, abilities: Dict[str, Any]):
        self.unit_id = unit_id
        self.name = name
        self.unit_type = unit_type
        self.health = health
        self.max_health = max_health
        self.abilities = abilities

    def __repr__(self):
        return f"UnitModel(id={self.unit_id}, name='{self.name}', type='{self.unit_type}', hp={self.health}/{self.max_health})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "name": self.name,
            "unit_type": self.unit_type,
            "health": self.health,
            "max_health": self.max_health,
            "abilities": self.abilities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitModel':
        return cls(
            unit_id=data.get("unit_id", "unknown_id"),
            name=data.get("name", "Unknown Unit"),
            unit_type=data.get("unit_type", "unknown_type"),
            health=data.get("health", 0),
            max_health=data.get("max_health", 0),
            abilities=data.get("abilities", {}),
        )