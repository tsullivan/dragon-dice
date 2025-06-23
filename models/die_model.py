# models/die_model.py
from typing import Dict, Any

class DieModel:
    def __init__(self, die_type: str, count: int = 1, rarity: str = "common"):
        self.die_type = die_type  # e.g., "Goblin", "Elf", "Dwarf" - could be more specific like "Goblin_Common_Melee"
        self.count = count
        self.rarity = rarity # e.g., "common", "uncommon", "rare"

    def __repr__(self):
        return f"DieModel(type='{self.die_type}', count={self.count}, rarity='{self.rarity}')"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "die_type": self.die_type,
            "count": self.count,
            "rarity": self.rarity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DieModel':
        return cls(die_type=data.get("die_type", "unknown"),
                   count=data.get("count", 1),
                   rarity=data.get("rarity", "common"))