# models/unit_model.py
from typing import Dict, Any
import constants

class UnitModel:
    def __init__(self, unit_id: str, name: str, unit_type: str, health: int, max_health: int,
                 abilities: Dict[str, Any], points_cost: int):
        self.unit_id = unit_id # Unique instance ID, e.g., player1_home_goblin_1
        self.name = name # Could be specific like "Gragnok" or generic "Goblin Spearman"
        self.unit_type = unit_type # The general type of unit, e.g., "goblin_spearman" (roster key)
        self.health = health
        self.max_health = max_health
        self.abilities = abilities # e.g., {"id_results": {constants.ICON_MELEE: 1}, "sais": [constants.SAI_RECRUIT]}
        self.points_cost = points_cost

    def __repr__(self):
        return f"UnitModel(id={self.unit_id}, name='{self.name}', type='{self.unit_type}', hp={self.health}/{self.max_health}, cost={self.points_cost})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "name": self.name,
            "unit_type": self.unit_type,
            "health": self.health,
            "max_health": self.max_health,
            "abilities": self.abilities,
            "points_cost": self.points_cost
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitModel':
        return cls(
            unit_id=data.get("unit_id", "unknown_id"),  # Provide default string
            name=data.get("name", "Unknown Unit"),     # Provide default string
            unit_type=data.get("unit_type", "unknown_type"), # Provide default string
            health=data.get("health", 0),              # Provide default int
            max_health=data.get("max_health", 0),          # Provide default int
            abilities=data.get("abilities", {}),
            points_cost=data.get("points_cost", 0)     # Provide default int
        )