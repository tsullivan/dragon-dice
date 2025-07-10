"""
BUA (Buried Units Area) Manager for Dragon Dice.

The BUA is where players can bury dead units during the Retreat step of the Reserves Phase.
Buried units are removed from the DUA and placed in the BUA.
Spells can target the BUA but not the Summoning Pool.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from models.unit_model import UnitModel


class BUAManager(QObject):
    """Manages the Buried Units Area (BUA) for all players."""

    bua_updated = Signal(str)  # Emitted when a player's BUA changes

    def __init__(self, parent=None):
        super().__init__(parent)
        # Player name -> List of UnitModel
        self._player_buas: Dict[str, List[UnitModel]] = {}

    def initialize_player_bua(self, player_name: str):
        """Initialize a player's BUA (starts empty)."""
        if player_name not in self._player_buas:
            self._player_buas[player_name] = []
            print(f"BUAManager: Initialized empty BUA for {player_name}")
            self.bua_updated.emit(player_name)

    def bury_unit(self, player_name: str, unit: UnitModel):
        """Bury a unit in a player's BUA (moved from DUA during Retreat step)."""
        if player_name not in self._player_buas:
            self.initialize_player_bua(player_name)

        self._player_buas[player_name].append(unit)
        print(f"BUAManager: Buried {unit.name} ({unit.species}) in {player_name}'s BUA")
        self.bua_updated.emit(player_name)

    def bury_units(self, player_name: str, units: List[UnitModel]):
        """Bury multiple units in a player's BUA."""
        if player_name not in self._player_buas:
            self.initialize_player_bua(player_name)

        self._player_buas[player_name].extend(units)
        unit_names = [f"{unit.name} ({unit.species})" for unit in units]
        print(f"BUAManager: Buried {len(units)} units in {player_name}'s BUA: {', '.join(unit_names)}")
        self.bua_updated.emit(player_name)

    def remove_unit_from_bua(self, player_name: str, unit_id: str) -> Optional[UnitModel]:
        """Remove a unit from a player's BUA (for special game effects)."""
        if player_name not in self._player_buas:
            return None

        bua = self._player_buas[player_name]
        for i, unit in enumerate(bua):
            if unit.get_id() == unit_id or unit.name == unit_id:
                removed_unit = bua.pop(i)
                print(f"BUAManager: Removed {removed_unit.name} from {player_name}'s BUA")
                self.bua_updated.emit(player_name)
                return removed_unit

        print(f"BUAManager: Unit {unit_id} not found in {player_name}'s BUA")
        return None

    def get_player_bua(self, player_name: str) -> List[UnitModel]:
        """Get all units in a player's BUA."""
        return self._player_buas.get(player_name, []).copy()

    def get_units_by_species(self, player_name: str, species: str) -> List[UnitModel]:
        """Get units in a player's BUA by species."""
        bua = self.get_player_bua(player_name)
        return [unit for unit in bua if unit.species == species]

    def get_units_by_element(self, player_name: str, element: str) -> List[UnitModel]:
        """Get units in a player's BUA that have a specific element."""
        bua = self.get_player_bua(player_name)
        return [unit for unit in bua if element in unit.elements]

    def has_units(self, player_name: str) -> bool:
        """Check if a player has any units in their BUA."""
        return len(self.get_player_bua(player_name)) > 0

    def get_unit_count(self, player_name: str) -> int:
        """Get the number of units in a player's BUA."""
        return len(self.get_player_bua(player_name))

    def get_species_count(self, player_name: str, species: str) -> int:
        """Get the count of a specific species in a player's BUA."""
        return len(self.get_units_by_species(player_name, species))

    def get_total_health(self, player_name: str) -> int:
        """Get the total health of all units in a player's BUA."""
        bua = self.get_player_bua(player_name)
        return sum(unit.health for unit in bua)

    def get_bua_statistics(self, player_name: str) -> Dict[str, Any]:
        """Get statistics about a player's BUA."""
        bua = self.get_player_bua(player_name)

        stats = {
            "total_units": len(bua),
            "total_health": 0,
            "species_breakdown": {},
            "element_breakdown": {},
        }

        for unit in bua:
            # Total health
            stats["total_health"] += unit.health

            # Species breakdown
            species = unit.species
            stats["species_breakdown"][species] = stats["species_breakdown"].get(species, 0) + 1

            # Element breakdown
            for element in unit.elements:
                stats["element_breakdown"][element] = stats["element_breakdown"].get(element, 0) + 1

        return stats

    def get_all_buas_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get a summary of all players' BUAs."""
        summary = {}
        for player_name in self._player_buas:
            summary[player_name] = self.get_bua_statistics(player_name)
        return summary

    def can_target_bua(self, player_name: str) -> bool:
        """Check if a player's BUA can be targeted by spells (must have units)."""
        return self.has_units(player_name)

    def find_unit_in_bua(self, player_name: str, unit_id: str) -> Optional[UnitModel]:
        """Find a specific unit in a player's BUA."""
        bua = self.get_player_bua(player_name)
        for unit in bua:
            if unit.get_id() == unit_id or unit.name == unit_id:
                return unit
        return None

    def clear_player_bua(self, player_name: str):
        """Clear all units from a player's BUA."""
        if player_name in self._player_buas:
            unit_count = len(self._player_buas[player_name])
            self._player_buas[player_name] = []
            print(f"BUAManager: Cleared {unit_count} units from {player_name}'s BUA")
            self.bua_updated.emit(player_name)

    def get_all_players(self) -> List[str]:
        """Get list of all players with BUAs."""
        return list(self._player_buas.keys())

    def transfer_unit_between_buas(self, from_player: str, to_player: str, unit_id: str) -> bool:
        """Transfer a unit from one player's BUA to another's (for special game effects)."""
        unit = self.remove_unit_from_bua(from_player, unit_id)
        if unit:
            self.bury_unit(to_player, unit)
            print(f"BUAManager: Transferred {unit.name} from {from_player}'s BUA to {to_player}'s BUA")
            return True
        return False

    def get_bua_export_data(self, player_name: str) -> List[Dict[str, Any]]:
        """Export a player's BUA data for saving/loading."""
        bua = self.get_player_bua(player_name)
        return [unit.to_dict() for unit in bua]

    def import_bua_data(self, player_name: str, bua_data: List[Dict[str, Any]]):
        """Import BUA data for a player (for loading saved games)."""
        units = []
        for unit_dict in bua_data:
            unit = UnitModel.from_dict(unit_dict)
            units.append(unit)

        if player_name not in self._player_buas:
            self.initialize_player_bua(player_name)

        self._player_buas[player_name] = units
        print(f"BUAManager: Imported {len(units)} units to {player_name}'s BUA")
        self.bua_updated.emit(player_name)

    def get_buriable_candidates(self, player_name: str, dua_units: List[UnitModel]) -> List[UnitModel]:
        """Get units from DUA that can be buried (typically all dead units can be buried)."""
        # In Dragon Dice, any dead unit can typically be buried
        # This method could be extended with specific burial rules if needed
        return dua_units.copy()

    def process_burial_selection(self, player_name: str, selected_units: List[UnitModel]) -> Dict[str, Any]:
        """Process the burial of selected units and return results."""
        if not selected_units:
            return {
                "success": False,
                "message": "No units selected for burial",
                "units_buried": 0,
            }

        # Bury the selected units
        self.bury_units(player_name, selected_units)

        return {
            "success": True,
            "message": f"Successfully buried {len(selected_units)} units",
            "units_buried": len(selected_units),
            "buried_units": [unit.to_dict() for unit in selected_units],
        }
