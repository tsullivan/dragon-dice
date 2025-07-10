"""
DUA (Dead Unit Area) Manager for Dragon Dice.

This module handles the management of dead units, including:
1. Adding killed units to the DUA
2. Checking for burial conditions
3. Handling resurrection spells
4. Managing unit return from DUA
5. Special DUA-related effects
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal


class DUAState(Enum):
    """Possible states for units in the DUA."""

    DEAD = "dead"  # Normal dead state, can be resurrected
    BURIED = "buried"  # Permanently removed, cannot be resurrected
    RETURNING = "returning"  # Being returned to play via spell/ability


@dataclass
class DUAUnit:
    """Represents a unit in the DUA."""

    name: str
    species: str
    health: int
    elements: List[str]
    original_owner: str
    state: DUAState = DUAState.DEAD
    death_cause: str = "combat"  # combat, spell, dragon_attack, etc.
    death_location: str = ""
    death_turn: int = 0
    burial_conditions: List[str] = field(default_factory=list)

    def can_be_resurrected(self) -> bool:
        """Check if this unit can be resurrected."""
        return self.state == DUAState.DEAD

    def can_be_buried(self) -> bool:
        """Check if this unit can be buried."""
        return self.state == DUAState.DEAD

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "species": self.species,
            "health": self.health,
            "elements": self.elements,
            "original_owner": self.original_owner,
            "state": self.state.value,
            "death_cause": self.death_cause,
            "death_location": self.death_location,
            "death_turn": self.death_turn,
            "burial_conditions": self.burial_conditions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DUAUnit":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            species=data["species"],
            health=data["health"],
            elements=data["elements"],
            original_owner=data["original_owner"],
            state=DUAState(data.get("state", "dead")),
            death_cause=data.get("death_cause", "combat"),
            death_location=data.get("death_location", ""),
            death_turn=data.get("death_turn", 0),
            burial_conditions=data.get("burial_conditions", []),
        )


class DUAManager(QObject):
    """Manages the Dead Unit Area for all players."""

    dua_updated = Signal(str)  # Emitted when a player's DUA changes

    def __init__(self, turn_manager, parent=None):
        super().__init__(parent)
        # DUA storage: player_name -> list of DUAUnit
        self.dua_by_player: Dict[str, List[DUAUnit]] = {}

        # Burial conditions that apply to all units
        self.global_burial_conditions: List[str] = []

        # Reference to turn manager for turn tracking
        self.turn_manager = turn_manager

    def add_killed_unit(
        self,
        unit_data: Dict[str, Any],
        owner: str,
        death_cause: str = "combat",
        death_location: str = "",
        burial_conditions: Optional[List[str]] = None,
    ) -> DUAUnit:
        """
        Add a killed unit to the DUA.

        Args:
            unit_data: Dictionary containing unit information
            owner: Player who owned the unit
            death_cause: How the unit died
            death_location: Where the unit died
            burial_conditions: Special conditions that might cause burial

        Returns:
            The created DUAUnit
        """
        if burial_conditions is None:
            burial_conditions = []

        # Create DUA unit
        dua_unit = DUAUnit(
            name=unit_data.get("name", "Unknown Unit"),
            species=unit_data.get("species", "Unknown"),
            health=unit_data.get("health", 1),
            elements=unit_data.get("elements", []),
            original_owner=owner,
            death_cause=death_cause,
            death_location=death_location,
            death_turn=self.turn_manager.get_current_turn(),
            burial_conditions=burial_conditions,
        )

        # Initialize player's DUA if needed
        if owner not in self.dua_by_player:
            self.dua_by_player[owner] = []

        # Add to player's DUA
        self.dua_by_player[owner].append(dua_unit)

        # Emit signal
        self.dua_updated.emit(owner)

        # Check for immediate burial conditions
        self._check_burial_conditions(dua_unit)

        return dua_unit

    def add_multiple_killed_units(
        self, killed_units: List[Dict[str, Any]], owner: str, death_cause: str = "combat", death_location: str = ""
    ) -> List[DUAUnit]:
        """Add multiple killed units to the DUA at once."""
        dua_units = []

        for unit_data in killed_units:
            dua_unit = self.add_killed_unit(unit_data, owner, death_cause, death_location)
            dua_units.append(dua_unit)

        return dua_units

    def get_player_dua(self, player_name: str) -> List[DUAUnit]:
        """Get all units in a player's DUA."""
        return self.dua_by_player.get(player_name, [])

    def get_resurrectable_units(self, player_name: str) -> List[DUAUnit]:
        """Get units that can be resurrected for a player."""
        player_dua = self.get_player_dua(player_name)
        return [unit for unit in player_dua if unit.can_be_resurrected()]

    def get_units_by_element(self, player_name: str, element: str) -> List[DUAUnit]:
        """Get units in DUA that contain a specific element."""
        player_dua = self.get_player_dua(player_name)
        return [unit for unit in player_dua if element in unit.elements and unit.can_be_resurrected()]

    def get_units_by_species(self, player_name: str, species: str) -> List[DUAUnit]:
        """Get units in DUA of a specific species."""
        player_dua = self.get_player_dua(player_name)
        return [unit for unit in player_dua if unit.species == species and unit.can_be_resurrected()]

    def resurrect_unit(self, player_name: str, unit_name: str) -> Optional[DUAUnit]:
        """
        Resurrect a unit from the DUA.

        Args:
            player_name: Player who owns the unit
            unit_name: Name of the unit to resurrect

        Returns:
            The resurrected unit if successful, None otherwise
        """
        player_dua = self.get_player_dua(player_name)

        for unit in player_dua:
            if unit.name == unit_name and unit.can_be_resurrected():
                # Mark as returning (will be removed when added to army)
                unit.state = DUAState.RETURNING
                return unit

        return None

    def remove_unit_from_dua(self, player_name: str, unit_name: str) -> bool:
        """
        Remove a unit from the DUA (after resurrection).

        Args:
            player_name: Player who owns the unit
            unit_name: Name of the unit to remove

        Returns:
            True if unit was removed, False otherwise
        """
        player_dua = self.get_player_dua(player_name)

        for i, unit in enumerate(player_dua):
            if unit.name == unit_name:
                player_dua.pop(i)
                return True

        return False

    def bury_unit(self, player_name: str, unit_name: str, burial_reason: str = "spell") -> bool:
        """
        Bury a unit (permanently remove from game).

        Args:
            player_name: Player who owns the unit
            unit_name: Name of the unit to bury
            burial_reason: Reason for burial

        Returns:
            True if unit was buried, False otherwise
        """
        player_dua = self.get_player_dua(player_name)

        for unit in player_dua:
            if unit.name == unit_name and unit.can_be_buried():
                unit.state = DUAState.BURIED
                unit.burial_conditions.append(burial_reason)
                return True

        return False

    def _check_burial_conditions(self, unit: DUAUnit):
        """Check if a unit should be immediately buried based on conditions."""
        # Check for Soiled Ground spell effect
        if "soiled_ground" in self.global_burial_conditions:
            if unit.death_location and self._location_has_soiled_ground(unit.death_location):
                # Unit must make save roll, if no save result -> buried
                # This would be handled by the spell effect system
                pass

        # Check for Swamp Fever spell effect
        if "swamp_fever" in unit.burial_conditions:
            # Units killed by Swamp Fever make second roll, if ID -> buried
            # This would be handled by the spell effect system
            pass

        # Check for Exhume spell effect
        if "exhume" in unit.burial_conditions:
            # Units that don't generate save result are buried
            # This would be handled by the spell effect system
            pass

    def _location_has_soiled_ground(self, location: str) -> bool:
        """Check if a location is affected by Soiled Ground spell."""
        # This would check active spell effects
        # For now, placeholder implementation
        return False

    def apply_spell_effect(self, spell_name: str, effect_data: Dict[str, Any]):
        """Apply spell effects that affect the DUA."""
        if spell_name == "Soiled Ground":
            # Add burial condition for terrain
            target_terrain = effect_data.get("target_terrain", "")
            self.global_burial_conditions.append(f"soiled_ground_{target_terrain}")

        elif spell_name == "Open Grave":
            # Units killed by army-targeting effects go to Reserve Area instead
            # This would be handled by the combat system
            pass

        elif spell_name == "Exhume":
            # Handle Exhume spell targeting DUA units
            target_player = effect_data.get("target_player", "")
            target_units = effect_data.get("target_units", [])

            for unit_name in target_units:
                # Unit makes save roll, if no save -> buried
                # Return equal health-worth to caster
                pass

    def get_dua_statistics(self, player_name: str) -> Dict[str, Any]:
        """Get statistics about a player's DUA."""
        player_dua = self.get_player_dua(player_name)

        stats = {
            "total_units": len(player_dua),
            "dead_units": len([u for u in player_dua if u.state == DUAState.DEAD]),
            "buried_units": len([u for u in player_dua if u.state == DUAState.BURIED]),
            "returning_units": len([u for u in player_dua if u.state == DUAState.RETURNING]),
            "resurrectable_units": len(self.get_resurrectable_units(player_name)),
            "total_health": sum(u.health for u in player_dua),
            "species_breakdown": {},
            "element_breakdown": {},
        }

        # Calculate species breakdown
        for unit in player_dua:
            species = unit.species
            if species not in stats["species_breakdown"]:
                stats["species_breakdown"][species] = 0
            stats["species_breakdown"][species] += 1

        # Calculate element breakdown
        for unit in player_dua:
            for element in unit.elements:
                if element not in stats["element_breakdown"]:
                    stats["element_breakdown"][element] = 0
                stats["element_breakdown"][element] += 1

        return stats

    def get_all_dua_units(self) -> Dict[str, List[DUAUnit]]:
        """Get all DUA units for all players."""
        return self.dua_by_player.copy()

    def clear_player_dua(self, player_name: str):
        """Clear all units from a player's DUA."""
        self.dua_by_player[player_name] = []

    def set_current_turn(self, turn: int):
        """Set the current game turn (delegates to turn manager)."""
        self.turn_manager.set_current_turn(turn)

    def initialize_player_dua(self, player_name: str):
        """Initialize DUA for a player."""
        if player_name not in self.dua_by_player:
            self.dua_by_player[player_name] = []

    def add_unit_to_dua(self, dua_unit: DUAUnit):
        """Add a DUA unit directly to the DUA."""
        owner = dua_unit.original_owner
        if owner not in self.dua_by_player:
            self.dua_by_player[owner] = []

        self.dua_by_player[owner].append(dua_unit)
        self.dua_updated.emit(owner)

        # Check for immediate burial conditions
        self._check_burial_conditions(dua_unit)

    def export_dua_state(self) -> Dict[str, Any]:
        """Export DUA state for save/load."""
        return {
            "dua_by_player": {
                player: [unit.to_dict() for unit in units] for player, units in self.dua_by_player.items()
            },
            "global_burial_conditions": self.global_burial_conditions,
            "current_turn": self.turn_manager.get_current_turn(),
        }

    def import_dua_state(self, state: Dict[str, Any]):
        """Import DUA state from save/load."""
        self.dua_by_player = {
            player: [DUAUnit.from_dict(unit_data) for unit_data in units]
            for player, units in state.get("dua_by_player", {}).items()
        }
        self.global_burial_conditions = state.get("global_burial_conditions", [])
        self.turn_manager.set_current_turn(state.get("current_turn", 1))
