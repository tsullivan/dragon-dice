# models/unit_roster_model.py
from typing import List, Dict, Any, Optional
import constants
from .unit_model import UnitModel

class UnitRosterModel:
    """
    Holds definitions for all available unit types in the game.
    In a real app, this might load from a JSON/YAML file or database.
    """
    def __init__(self):
        self._unit_definitions: Dict[str, Dict[str, Any]] = {}
        self._load_default_units()

    def _load_default_units(self):
        # Example unit definitions
        self.add_unit_definition(
            unit_type_id="goblin_spearman",
            display_name="Goblin Spearman",
            max_health=1,
            points_cost=1,
            abilities={"id_results": {constants.ICON_MELEE: 1, constants.ICON_SAVE: 1}}
        )
        self.add_unit_definition(
            unit_type_id="orc_archer",
            display_name="Orc Archer",
            max_health=2,
            points_cost=2,
            abilities={"id_results": {constants.ICON_MISSILE: 1}}
        )
        self.add_unit_definition(
            unit_type_id="elf_mage",
            display_name="Elf Mage",
            max_health=1,
            points_cost=3,
            abilities={"id_results": {constants.ICON_MAGIC: 1}, "sais": [constants.SAI_MAGIC_BOLT]}
        )

    def add_unit_definition(self, unit_type_id: str, display_name: str, max_health: int, points_cost: int, abilities: Dict[str, Any]):
        if unit_type_id in self._unit_definitions:
            print(f"Warning: Unit type '{unit_type_id}' already defined. Overwriting.")
        self._unit_definitions[unit_type_id] = {
            "display_name": display_name, "max_health": max_health,
            "points_cost": points_cost, "abilities": abilities
        }

    def get_available_unit_types(self) -> List[Dict[str, Any]]:
        """Returns a list of unit types for UI selection (id, display_name, cost)."""
        return [{"id": unit_id, "name": data["display_name"], "cost": data["points_cost"]}
                for unit_id, data in self._unit_definitions.items()]

    def get_unit_definition(self, unit_type_id: str) -> Optional[Dict[str, Any]]:
        return self._unit_definitions.get(unit_type_id)

    def create_unit_instance(self, unit_type_id: str, instance_id: str, custom_name: Optional[str] = None) -> Optional[UnitModel]:
        definition = self.get_unit_definition(unit_type_id)
        if not definition: return None
        return UnitModel(unit_id=instance_id, name=custom_name or definition["display_name"], unit_type=unit_type_id,
                         health=definition["max_health"], max_health=definition["max_health"],
                         abilities=definition["abilities"].copy(), points_cost=definition["points_cost"])