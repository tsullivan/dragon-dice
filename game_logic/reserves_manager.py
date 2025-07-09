"""
Reserves Area Manager for Dragon Dice.

This module handles the management of units in the Reserve Area, including:
1. Adding units to reserves (from terrain retreat, spell effects, etc.)
2. Removing units from reserves (for reinforcement)
3. Tracking Amazon Ivory magic generation
4. Managing reserve spell casting restrictions
5. Handling special reserve-related abilities
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models.spell_model import get_reserve_spells


@dataclass
class ReserveUnit:
    """Represents a unit in the Reserve Area."""

    name: str
    species: str
    health: int
    elements: List[str]
    owner: str
    original_terrain: str = ""  # Where the unit came from
    turn_entered: int = 0
    entry_reason: str = "retreat"  # retreat, spell, ability, etc.

    def can_generate_ivory_magic(self) -> bool:
        """Check if this unit can generate Ivory magic (Amazon Terrain Harmony)."""
        return self.species == "Amazons"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "species": self.species,
            "health": self.health,
            "elements": self.elements,
            "owner": self.owner,
            "original_terrain": self.original_terrain,
            "turn_entered": self.turn_entered,
            "entry_reason": self.entry_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReserveUnit":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            species=data["species"],
            health=data["health"],
            elements=data["elements"],
            owner=data["owner"],
            original_terrain=data.get("original_terrain", ""),
            turn_entered=data.get("turn_entered", 0),
            entry_reason=data.get("entry_reason", "retreat"),
        )


class ReservesManager:
    """Manages the Reserve Area for all players."""

    def __init__(self):
        # Reserve storage: player_name -> list of ReserveUnit
        self.reserves_by_player: Dict[str, List[ReserveUnit]] = {}

        # Current game turn for tracking
        self.current_turn = 1

        # Reserve spell casting restrictions
        self.reserve_spell_list = get_reserve_spells()

    def add_unit_to_reserves(
        self,
        unit_data: Dict[str, Any],
        owner: str,
        original_terrain: str = "",
        entry_reason: str = "retreat",
    ) -> ReserveUnit:
        """
        Add a unit to the Reserve Area.

        Args:
            unit_data: Dictionary containing unit information
            owner: Player who owns the unit
            original_terrain: Terrain the unit came from
            entry_reason: How the unit entered reserves

        Returns:
            The created ReserveUnit
        """
        # Create reserve unit
        reserve_unit = ReserveUnit(
            name=unit_data.get("name", "Unknown Unit"),
            species=unit_data.get("species", "Unknown"),
            health=unit_data.get("health", 1),
            elements=unit_data.get("elements", []),
            owner=owner,
            original_terrain=original_terrain,
            turn_entered=self.current_turn,
            entry_reason=entry_reason,
        )

        # Initialize player's reserves if needed
        if owner not in self.reserves_by_player:
            self.reserves_by_player[owner] = []

        # Add to player's reserves
        self.reserves_by_player[owner].append(reserve_unit)

        return reserve_unit

    def remove_unit_from_reserves(self, owner: str, unit_name: str) -> Optional[ReserveUnit]:
        """
        Remove a unit from the Reserve Area.

        Args:
            owner: Player who owns the unit
            unit_name: Name of the unit to remove

        Returns:
            The removed ReserveUnit if successful, None otherwise
        """
        if owner not in self.reserves_by_player:
            return None

        player_reserves = self.reserves_by_player[owner]

        for i, unit in enumerate(player_reserves):
            if unit.name == unit_name:
                return player_reserves.pop(i)

        return None

    def get_player_reserves(self, player_name: str) -> List[ReserveUnit]:
        """Get all units in a player's Reserve Area."""
        return self.reserves_by_player.get(player_name, [])

    def get_reserve_units_by_species(self, player_name: str, species: str) -> List[ReserveUnit]:
        """Get reserve units of a specific species."""
        player_reserves = self.get_player_reserves(player_name)
        return [unit for unit in player_reserves if unit.species == species]

    def get_amazon_ivory_magic_generation(self, player_name: str) -> int:
        """
        Calculate Ivory magic generation from Amazon units in reserves.

        Args:
            player_name: Player to calculate for

        Returns:
            Number of magic points available as Ivory magic
        """
        amazon_units = self.get_reserve_units_by_species(player_name, "Amazons")

        # Each Amazon unit in reserves generates 1 magic point as Ivory magic
        # This would be determined by actual die rolls, but for calculation purposes
        # we return the number of Amazon units (representing potential)
        return len(amazon_units)

    def can_cast_spell_from_reserves(self, spell_name: str) -> bool:
        """
        Check if a spell can be cast from the Reserve Area.

        Args:
            spell_name: Name of the spell to check

        Returns:
            True if the spell can be cast from reserves, False otherwise
        """
        for reserve_spell in self.reserve_spell_list:
            if reserve_spell.name.lower() == spell_name.lower():
                return True
        return False

    def get_available_reserve_spells(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Get list of spells that can be cast from reserves.

        Args:
            player_name: Player to get spells for

        Returns:
            List of spell dictionaries
        """
        available_spells = []

        for spell in self.reserve_spell_list:
            spell_dict = {
                "name": spell.name,
                "species": spell.species,
                "cost": spell.cost,
                "element": spell.element,
                "effect": spell.effect,
                "cantrip": spell.cantrip,
            }
            available_spells.append(spell_dict)

        return available_spells

    def process_reinforcement(self, player_name: str, reinforcement_plan: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Process a reinforcement plan (moving units from reserves to terrains).

        Args:
            player_name: Player executing the reinforcement
            reinforcement_plan: Dictionary of terrain -> list of unit names

        Returns:
            Dictionary with reinforcement results
        """
        results = {
            "success": True,
            "player_name": player_name,
            "reinforcements": {},
            "units_moved": 0,
            "errors": [],
        }

        for terrain, unit_names in reinforcement_plan.items():
            terrain_reinforcements = []

            for unit_name in unit_names:
                unit = self.remove_unit_from_reserves(player_name, unit_name)
                if unit:
                    terrain_reinforcements.append(unit.to_dict())
                    results["units_moved"] += 1
                else:
                    results["errors"].append(f"Unit {unit_name} not found in reserves")

            if terrain_reinforcements:
                results["reinforcements"][terrain] = terrain_reinforcements

        return results

    def process_retreat(
        self, player_name: str, retreat_plan: Dict[str, List[str]], terrain_armies: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a retreat plan (moving units from terrains to reserves).

        Args:
            player_name: Player executing the retreat
            retreat_plan: Dictionary of terrain -> list of unit names
            terrain_armies: Current army data at each terrain

        Returns:
            Dictionary with retreat results
        """
        results = {
            "success": True,
            "player_name": player_name,
            "retreats": {},
            "units_moved": 0,
            "errors": [],
        }

        for terrain, unit_names in retreat_plan.items():
            if terrain not in terrain_armies:
                results["errors"].append(f"No army found at terrain {terrain}")
                continue

            army_data = terrain_armies[terrain]
            army_units = army_data.get("units", [])
            terrain_retreats = []

            for unit_name in unit_names:
                # Find the unit in the army
                unit_data = None
                for unit in army_units:
                    if unit.get("name") == unit_name:
                        unit_data = unit
                        break

                if unit_data:
                    # Add to reserves
                    reserve_unit = self.add_unit_to_reserves(unit_data, player_name, terrain, "retreat")
                    terrain_retreats.append(reserve_unit.to_dict())
                    results["units_moved"] += 1
                else:
                    results["errors"].append(f"Unit {unit_name} not found at terrain {terrain}")

            if terrain_retreats:
                results["retreats"][terrain] = terrain_retreats

        return results

    def process_firewalker_air_flight(
        self, player_name: str, air_flight_plan: Dict[str, List[str]], terrain_armies: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process Firewalker Air Flight movement.

        Args:
            player_name: Player executing the air flight
            air_flight_plan: Dictionary of source_terrain -> list of unit names
            terrain_armies: Current army data at each terrain

        Returns:
            Dictionary with air flight results
        """
        results = {
            "success": True,
            "player_name": player_name,
            "air_flights": {},
            "units_moved": 0,
            "errors": [],
        }

        # Implementation would handle the complex Air Flight rules
        # For now, placeholder structure

        return results

    def get_reserves_statistics(self, player_name: str) -> Dict[str, Any]:
        """Get statistics about a player's Reserve Area."""
        player_reserves = self.get_player_reserves(player_name)

        stats = {
            "total_units": len(player_reserves),
            "total_health": sum(unit.health for unit in player_reserves),
            "species_breakdown": {},
            "element_breakdown": {},
            "amazon_ivory_magic_potential": self.get_amazon_ivory_magic_generation(player_name),
            "turns_in_reserves": {},
        }

        # Calculate breakdowns
        for unit in player_reserves:
            # Species breakdown
            species = unit.species
            if species not in stats["species_breakdown"]:
                stats["species_breakdown"][species] = 0
            stats["species_breakdown"][species] += 1

            # Element breakdown
            for element in unit.elements:
                if element not in stats["element_breakdown"]:
                    stats["element_breakdown"][element] = 0
                stats["element_breakdown"][element] += 1

            # Turns in reserves
            turns_in_reserves = self.current_turn - unit.turn_entered
            if turns_in_reserves not in stats["turns_in_reserves"]:
                stats["turns_in_reserves"][turns_in_reserves] = 0
            stats["turns_in_reserves"][turns_in_reserves] += 1

        return stats

    def clear_player_reserves(self, player_name: str):
        """Clear all units from a player's Reserve Area."""
        self.reserves_by_player[player_name] = []

    def set_current_turn(self, turn: int):
        """Set the current game turn."""
        self.current_turn = turn

    def export_reserves_state(self) -> Dict[str, Any]:
        """Export reserves state for save/load."""
        return {
            "reserves_by_player": {
                player: [unit.to_dict() for unit in units] for player, units in self.reserves_by_player.items()
            },
            "current_turn": self.current_turn,
        }

    def import_reserves_state(self, state: Dict[str, Any]):
        """Import reserves state from save/load."""
        self.reserves_by_player = {
            player: [ReserveUnit.from_dict(unit_data) for unit_data in units]
            for player, units in state.get("reserves_by_player", {}).items()
        }
        self.current_turn = state.get("current_turn", 1)

    def get_all_reserves(self) -> Dict[str, List[ReserveUnit]]:
        """Get all reserves for all players."""
        return self.reserves_by_player.copy()

    def has_units_in_reserves(self, player_name: str) -> bool:
        """Check if a player has any units in their Reserve Area."""
        return len(self.get_player_reserves(player_name)) > 0

    def can_target_reserves(self, attacker_player: str, target_player: str) -> bool:
        """
        Check if reserves can be targeted by certain abilities.

        Most attacks cannot target reserves, but some special abilities can.
        """
        # Most attacks cannot target Reserve Area
        # Only specific abilities like Tower eighth face, Mutate, etc.
        return False

    def apply_spell_effect_to_reserves(self, spell_name: str, effect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply spell effects that specifically target or affect the Reserve Area."""
        results = {
            "success": False,
            "spell_name": spell_name,
            "effect_applied": False,
            "message": "",
        }

        if spell_name == "Scent of Fear":
            # Move units to Reserve Area
            target_player = effect_data.get("target_player", "")
            target_units = effect_data.get("target_units", [])

            for unit_data in target_units:
                self.add_unit_to_reserves(unit_data, target_player, "", "spell_effect")

            results["success"] = True
            results["effect_applied"] = True
            results["message"] = f"Moved {len(target_units)} units to Reserve Area"

        elif spell_name == "Mirage":
            # Similar to Scent of Fear
            target_player = effect_data.get("target_player", "")
            target_units = effect_data.get("target_units", [])

            for unit_data in target_units:
                self.add_unit_to_reserves(unit_data, target_player, "", "spell_effect")

            results["success"] = True
            results["effect_applied"] = True
            results["message"] = f"Mirages moved {len(target_units)} units to Reserve Area"

        return results
