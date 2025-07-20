"""
Species Ability Management System for Dragon Dice.

This module handles species ability validation, eligibility checking,
and ability activation according to Dragon Dice rules.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get


class SpeciesAbilityManager(QObject):
    """
    Manages species abilities including validation, eligibility,
    and activation according to Dragon Dice rules.
    """

    ability_activated = Signal(str, str, dict)  # player_name, ability_name, results
    ability_availability_changed = Signal(str, dict)  # player_name, available_abilities

    def __init__(self, game_state_manager, dua_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.dua_manager = dua_manager

    def get_available_abilities(self, player_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all available species abilities for a player.

        Returns:
            Dictionary mapping ability names to availability data
        """
        available_abilities = {}

        # Check each species ability
        if self._can_use_mutate(player_name):
            available_abilities["Mutate"] = {
                "species": "Swamp Stalkers",
                "description": "Move enemy units from Reserves to their DUA",
                "requirements_met": True,
                "cost": "Bury Swamp Stalker from DUA",
                "max_targets": self._get_mutate_max_targets(player_name),
            }

        if self._can_use_feralization(player_name):
            available_abilities["Feralization"] = {
                "species": "Feral",
                "description": "Promote Feral units using only ID results",
                "requirements_met": True,
                "cost": "None",
                "eligible_units": self._get_feralization_eligible_units(player_name),
            }

        if self._can_use_winters_fortitude(player_name):
            available_abilities["Winter's Fortitude"] = {
                "species": "Frostwings",
                "description": "Gain additional saves against magic damage",
                "requirements_met": True,
                "cost": "None",
                "effect": "One extra save per magic damage point",
            }

        return available_abilities

    def _can_use_mutate(self, player_name: str) -> bool:
        """Check if Swamp Stalkers' Mutate ability can be used."""
        # Must have at least one army containing a Swamp Stalker at a terrain
        player_armies = self._get_player_armies_at_terrains(player_name)
        has_swamp_stalker_army = any(
            any(strict_get(unit, "species") == "Swamp Stalkers" for unit in army.get("units", []))
            for army in player_armies
        )
        if not has_swamp_stalker_army:
            return False

        # Must have at least one Swamp Stalker unit in DUA
        player_dua = self.dua_manager.get_player_dua(player_name)
        dead_swamp_stalkers = [unit for unit in player_dua if strict_get(unit, "species") == "Swamp Stalkers"]
        if not dead_swamp_stalkers:
            return False

        # An opposing player must have at least one unit in their Reserves Area
        opponent_reserves = self._get_all_opponent_reserves(player_name)
        total_opponent_reserves = sum(len(units) for units in opponent_reserves.values())
        return total_opponent_reserves > 0

    def _can_use_feralization(self, player_name: str) -> bool:
        """Check if Feral Feralization ability can be used."""
        player_armies = self._get_player_armies_at_terrains(player_name)

        for army in player_armies:
            has_feral = any(strict_get(unit, "species") == "Feral" for unit in army.get("units", []))
            if not has_feral:
                continue

            # Check if terrain has earth or air elements
            terrain_elements = self._get_army_terrain_elements(army)
            has_earth_or_air = any(elem.upper() in ["EARTH", "AIR"] for elem in terrain_elements)
            if has_earth_or_air:
                return True

        return False

    def _can_use_winters_fortitude(self, player_name: str) -> bool:
        """Check if Frostwings Winter's Fortitude ability can be used."""
        # This ability is passive and always available if player has Frostwings
        player_armies = self._get_player_armies_at_terrains(player_name)

        for army in player_armies:
            has_frostwings = any(strict_get(unit, "species") == "Frostwings" for unit in army.get("units", []))
            if has_frostwings:
                return True

        return False

    def _get_mutate_max_targets(self, player_name: str) -> int:
        """Calculate maximum targets for Mutate ability based on S-value scaling."""
        # Get game points to calculate S-value
        game_points = self.game_state_manager.get_total_game_points()
        s_value = max(1, game_points // 24)

        # Get count of dead Swamp Stalkers
        player_dua = self.dua_manager.get_player_dua(player_name)
        dead_swamp_stalkers_count = len(
            [unit for unit in player_dua if strict_get(unit, "species") == "Swamp Stalkers"]
        )

        return min(dead_swamp_stalkers_count, s_value)

    def _get_feralization_eligible_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get Feral units eligible for Feralization promotion."""
        eligible_units = []
        player_armies = self._get_player_armies_at_terrains(player_name)

        for army in player_armies:
            terrain_elements = self._get_army_terrain_elements(army)
            has_earth_or_air = any(elem.upper() in ["EARTH", "AIR"] for elem in terrain_elements)

            if has_earth_or_air:
                feral_units = [unit for unit in army.get("units", []) if strict_get(unit, "species") == "Feral"]
                eligible_units.extend(feral_units)

        return eligible_units

    def activate_mutate(self, player_name: str, target_selections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Activate Swamp Stalkers' Mutate ability.

        Args:
            player_name: Player using the ability
            target_selections: List of {opponent, unit_name} selections

        Returns:
            Results of the ability activation
        """
        if not self._can_use_mutate(player_name):
            return {"success": False, "error": "Mutate ability not available"}

        max_targets = self._get_mutate_max_targets(player_name)
        if len(target_selections) > max_targets:
            return {"success": False, "error": f"Cannot target more than {max_targets} units"}

        results = {"success": True, "units_moved": [], "swamp_stalker_buried": None}

        # Move selected units from opponent reserves to their DUA
        for selection in target_selections:
            opponent = strict_get(selection, "opponent")
            unit_name = strict_get(selection, "unit_name")

            # Move unit from reserves to DUA
            move_result = self._move_unit_reserves_to_dua(opponent, unit_name)
            if move_result["success"]:
                results["units_moved"].append({"opponent": opponent, "unit_name": unit_name})

        # Bury one Swamp Stalker from player's DUA
        if results["units_moved"]:
            buried_stalker = self._bury_swamp_stalker_from_dua(player_name)
            results["swamp_stalker_buried"] = buried_stalker

        self.ability_activated.emit(player_name, "Mutate", results)
        return results

    def activate_feralization(
        self, player_name: str, unit_selections: List[Dict[str, Any]], id_results_count: int
    ) -> Dict[str, Any]:
        """
        Activate Feral Feralization ability.

        Args:
            player_name: Player using the ability
            unit_selections: List of Feral units to promote
            id_results_count: Number of ID results available for promotion

        Returns:
            Results of the ability activation
        """
        if not self._can_use_feralization(player_name):
            return {"success": False, "error": "Feralization ability not available"}

        if len(unit_selections) > id_results_count:
            return {
                "success": False,
                "error": f"Cannot promote more units ({len(unit_selections)}) than ID results available ({id_results_count})",
            }

        results = {"success": True, "units_promoted": [], "id_results_used": len(unit_selections)}

        # Promote selected Feral units
        for selection in unit_selections:
            unit_id = strict_get(selection, "unit_id")
            army_id = strict_get(selection, "army_id")

            promotion_result = self.game_state_manager.promote_unit(player_name, army_id, unit_id)
            if promotion_result["success"]:
                results["units_promoted"].append(
                    {
                        "unit_id": unit_id,
                        "old_health": promotion_result["old_health"],
                        "new_health": promotion_result["new_health"],
                    }
                )

        self.ability_activated.emit(player_name, "Feralization", results)
        return results

    def apply_winters_fortitude(self, player_name: str, magic_damage: int, target_army_id: str) -> Dict[str, Any]:
        """
        Apply Frostwings Winter's Fortitude ability to magic damage.

        Returns:
            Modified damage calculation with extra saves
        """
        if not self._can_use_winters_fortitude(player_name):
            return {"extra_saves": 0, "applied": False}

        # Get Frostwings units in target army
        army_data = self.game_state_manager.get_army_data(player_name, target_army_id)
        frostwings_count = len(
            [unit for unit in strict_get(army_data, "units") if strict_get(unit, "species") == "Frostwings"]
        )

        if frostwings_count == 0:
            return {"extra_saves": 0, "applied": False}

        # One extra save per point of magic damage
        extra_saves = magic_damage

        return {"extra_saves": extra_saves, "applied": True, "frostwings_count": frostwings_count}

    def _get_player_armies_at_terrains(self, player_name: str) -> List[Dict[str, Any]]:
        """Get all player armies currently at terrains (not in reserves)."""
        all_armies = self.game_state_manager.get_player_armies(player_name)
        return [army for army in all_armies if strict_get(army, "location").lower() not in ["reserve area", "reserves"]]

    def _get_army_terrain_elements(self, army: Dict[str, Any]) -> List[str]:
        """Get terrain elements for an army's current location."""
        from models.terrain_model import get_terrain_elements

        location = strict_get(army, "location")
        return get_terrain_elements(location)

    def _get_all_opponent_reserves(self, player_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get reserves for all opposing players."""
        all_players = self.game_state_manager.get_all_player_names()
        opponent_reserves = {}

        for opponent in all_players:
            if opponent != player_name:
                reserves = self.game_state_manager.get_player_reserves(opponent)
                opponent_reserves[opponent] = reserves

        return opponent_reserves

    def _move_unit_reserves_to_dua(self, player_name: str, unit_name: str) -> Dict[str, Any]:
        """Move a unit from reserves to DUA."""
        # This would interact with the reserves manager and DUA manager
        try:
            # Remove from reserves
            reserves_manager = self.game_state_manager.reserves_manager
            remove_result = reserves_manager.remove_unit_from_reserves(player_name, unit_name)

            if remove_result["success"]:
                unit_data = remove_result["unit_data"]
                # Add to DUA
                self.dua_manager.add_unit_to_dua(player_name, unit_data)
                return {"success": True, "unit_data": unit_data}
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "Unit not found in reserves"}

    def _bury_swamp_stalker_from_dua(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Bury a Swamp Stalker from player's DUA."""
        player_dua = self.dua_manager.get_player_dua(player_name)

        # Find first Swamp Stalker
        swamp_stalker = next((unit for unit in player_dua if strict_get(unit, "species") == "Swamp Stalkers"), None)

        if swamp_stalker:
            self.dua_manager.remove_unit_from_dua(player_name, strict_get(swamp_stalker, "id"))
            return swamp_stalker

        return None
