# models/unit_roster_model.py
from typing import Any, Dict, List, Optional

import constants
from utils import strict_get

from .app_data_model import AppDataModel
from .unit_model import UnitModel


class UnitRosterModel:
    """
    Holds definitions for all available unit types in the game.
    """

    def __init__(self, app_data_model: AppDataModel):
        self._unit_definitions: Dict[str, Dict[str, Any]] = {}
        self.app_data_model = app_data_model
        self._load_default_units()

    def _load_default_units(self):
        units_by_species_data = self.app_data_model.get_unit_definitions()

        for species_name, units_in_species_list in units_by_species_data.items():
            for unit_data in units_in_species_list:
                self.add_unit_definition(
                    unit_type_id=unit_data["unit_type_id"],
                    display_name=unit_data["display_name"],
                    species=species_name,  # Species is now the key from the JSON object
                    max_health=unit_data["max_health"],
                    abilities=self._map_abilities_to_constants(unit_data.get("abilities", {})),
                    unit_class_type=strict_get(unit_data, "unit_class_type"),
                    die_faces=unit_data.get("die_faces", []),
                )

    def add_unit_definition(
        self,
        unit_type_id: str,
        display_name: str,
        species: str,
        max_health: int,
        abilities: Dict[str, Any],
        unit_class_type: str,
        die_faces: List[str],
    ):
        if unit_type_id in self._unit_definitions:
            print(f"Warning: Unit type '{unit_type_id}' already defined. Overwriting.")
        self._unit_definitions[unit_type_id] = {
            "id": unit_type_id,
            "display_name": display_name,
            "species": species,
            "max_health": max_health,
            "abilities": abilities,
            "unit_class_type": unit_class_type,
            "die_faces": die_faces or [],
        }

    def get_available_unit_types(self) -> List[Dict[str, Any]]:
        """Returns a list of unit types for UI selection (id, display_name, health-based cost)."""
        return [
            {"id": unit_id, "name": data["display_name"], "cost": data["max_health"]}
            for unit_id, data in self._unit_definitions.items()
        ]  # Using max_health as cost proxy

    def get_available_unit_types_by_species(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns a dict of unit types grouped by species."""
        units_by_species: Dict[str, List[Dict[str, Any]]] = {}
        # First, group units by species
        for _unit_id, data in self._unit_definitions.items():
            species = strict_get(data, "species")
            if species not in units_by_species:
                units_by_species[species] = []
            units_by_species[species].append(data)

        # Then, sort units within each species
        for species in units_by_species:
            units_by_species[species].sort(
                key=lambda x: (
                    strict_get(x, "unit_class_type"),  # Primary sort key: unit_class_type
                    strict_get(x, "max_health"),  # Secondary sort key: max_health
                )
            )
        return units_by_species

    def get_unit_definition(self, unit_type_id: str) -> Optional[Dict[str, Any]]:
        return self._unit_definitions.get(unit_type_id)

    def create_unit_instance(
        self, unit_type_id: str, instance_id: str, custom_name: Optional[str] = None
    ) -> Optional[UnitModel]:
        definition = self.get_unit_definition(unit_type_id)
        if not definition:
            return None

        # Use UnitModel.from_unit_data factory method which handles the new constructor properly
        try:
            unit_instance = UnitModel.from_unit_data(unit_type_id)
            # Update with custom values
            unit_instance.unit_id = instance_id
            unit_instance.unit_type = unit_type_id  # Ensure unit_type matches the requested ID
            if custom_name:
                unit_instance.name = custom_name
            return unit_instance
        except Exception:
            # Fallback: return None if unit data not found
            return None

    def _map_abilities_to_constants(self, abilities_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps string representations of icons/SAIs in abilities data to their constant values.
        """
        mapped_abilities = abilities_data.copy()

        if "id_results" in mapped_abilities and isinstance(mapped_abilities["id_results"], dict):
            new_id_results = {}
            for key_str, value in mapped_abilities["id_results"].items():
                constant_key = getattr(constants, f"ICON_{key_str.upper()}", key_str)
                new_id_results[constant_key] = value
            mapped_abilities["id_results"] = new_id_results

        if "sais" in mapped_abilities and isinstance(mapped_abilities["sais"], list):
            mapped_abilities["sais"] = [
                getattr(constants, f"SAI_{sai_str.upper()}", sai_str) for sai_str in mapped_abilities["sais"]
            ]

        return mapped_abilities
