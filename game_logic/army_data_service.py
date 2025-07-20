"""
Army Data Transformation Service for Dragon Dice.

This service handles complex data transformations for army information,
providing formatted data for UI consumption while keeping business logic
separate from the presentation layer.
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get, strict_get_optional, strict_get_with_fallback


class ArmyDataService(QObject):
    """
    Service for transforming army data for UI consumption and handling
    complex army-related calculations and data formatting.
    """

    army_data_updated = Signal(dict)  # Emits formatted army data

    def __init__(self, game_state_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager

    def get_formatted_army_data(self, player_name: str) -> Dict[str, Any]:
        """
        Get formatted army data for UI display.

        Returns:
            Dictionary with formatted army information for UI consumption
        """
        player_data = self.game_state_manager.get_player_data(player_name)
        raw_armies = strict_get(player_data, "armies")

        formatted_armies = []

        for army_type, army_data in raw_armies.items():
            formatted_army = self._format_single_army(army_type, army_data)
            formatted_armies.append(formatted_army)

        result = {
            "player_name": player_name,
            "armies": formatted_armies,
            "total_armies": len(formatted_armies),
            "active_army_count": len([a for a in formatted_armies if a["has_units"]]),
            "total_units": sum(a["unit_count"] for a in formatted_armies),
            "total_points": sum(a["points"] for a in formatted_armies),
        }

        return result

    def _format_single_army(self, army_type: str, army_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single army for UI display."""
        units = strict_get_optional(army_data, "units", [])

        formatted_army = {
            "name": strict_get(army_data, "name"),
            "army_type": army_type,
            "location": strict_get(army_data, "location"),
            "units": self._format_units_for_display(units),
            "unit_count": len(units),
            "has_units": len(units) > 0,
            "unique_id": strict_get_with_fallback(army_data, "unique_id", "id", army_data),
            "points": strict_get_with_fallback(army_data, "points_value", "allocated_points", army_data),
            "is_at_terrain": self._is_army_at_terrain(army_data),
            "terrain_controlled": self._check_terrain_control(army_data),
            "available_actions": self._get_available_actions(army_data),
            "army_health": self._calculate_total_army_health(units),
            "army_status": self._determine_army_status(units, army_data),
        }

        return formatted_army

    def _format_units_for_display(self, units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format units for UI display."""
        formatted_units = []

        for unit in units:
            formatted_unit = {
                "name": strict_get(unit, "name"),
                "id": strict_get_optional(unit, "id", strict_get(unit, "name")),
                "species": strict_get(unit, "species"),
                "health": strict_get(unit, "health"),
                "max_health": strict_get(unit, "max_health"),
                "is_alive": strict_get(unit, "health") > 0,
                "is_wounded": strict_get(unit, "health") < strict_get(unit, "max_health"),
                "health_percentage": (strict_get(unit, "health") / strict_get(unit, "max_health")) * 100,
                "display_name": self._get_unit_display_name(unit),
                "species_elements": self._get_unit_elements(unit),
                "unit_class": strict_get_optional(unit, "unit_class", "Unknown"),
            }
            formatted_units.append(formatted_unit)

        return formatted_units

    def _get_unit_display_name(self, unit: Dict[str, Any]) -> str:
        """Get formatted display name for a unit."""
        name = strict_get(unit, "name")
        health = strict_get(unit, "health")
        max_health = strict_get(unit, "max_health")

        if health == max_health:
            return name
        elif health > 0:
            return f"{name} ({health}/{max_health})"
        else:
            return f"{name} (Dead)"

    def _get_unit_elements(self, unit: Dict[str, Any]) -> List[str]:
        """Get elements for a unit."""
        from models.species_model import get_species_elements

        species = strict_get(unit, "species")
        return get_species_elements(species)

    def _is_army_at_terrain(self, army_data: Dict[str, Any]) -> bool:
        """Check if army is at a terrain (not in reserves)."""
        location = strict_get(army_data, "location")
        return location.lower() not in ["reserve area", "reserves"]

    def _check_terrain_control(self, army_data: Dict[str, Any]) -> bool:
        """Check if army controls its current terrain."""
        if not self._is_army_at_terrain(army_data):
            return False

        location = strict_get(army_data, "location")
        army_id = strict_get_with_fallback(army_data, "unique_id", "id", army_data)

        try:
            controller = self.game_state_manager.get_terrain_controller(location)
            return controller is not None  # Simplified check
        except Exception:
            return False

    def _get_available_actions(self, army_data: Dict[str, Any]) -> List[str]:
        """Get available actions for an army."""
        actions = []

        if not self._is_army_at_terrain(army_data):
            return ["move_to_terrain"]  # Army in reserves can only move to terrain

        # Basic actions available to armies at terrains
        actions.extend(["melee", "missile", "magic", "maneuver"])

        # Check for special actions based on terrain/eighth face
        location = strict_get(army_data, "location")
        if self._check_terrain_control(army_data):
            actions.append("eighth_face_action")

        return actions

    def _calculate_total_army_health(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total army health statistics."""
        if not units:
            return {"current": 0, "maximum": 0, "percentage": 0}

        current_health = sum(strict_get(unit, "health") for unit in units)
        max_health = sum(strict_get(unit, "max_health") for unit in units)

        percentage = (current_health / max_health * 100) if max_health > 0 else 0

        return {"current": current_health, "maximum": max_health, "percentage": round(percentage, 1)}

    def _determine_army_status(self, units: List[Dict[str, Any]], army_data: Dict[str, Any]) -> str:
        """Determine army status for display."""
        if not units:
            return "empty"

        alive_units = [u for u in units if strict_get(u, "health") > 0]

        if not alive_units:
            return "eliminated"
        elif len(alive_units) == len(units):
            return "full_strength"
        else:
            return "damaged"

    def get_army_summary_for_selection(self, player_name: str) -> List[Dict[str, Any]]:
        """Get simplified army data for army selection dialogs."""
        formatted_data = self.get_formatted_army_data(player_name)

        army_summaries = []
        for army in formatted_data["armies"]:
            summary = {
                "name": army["name"],
                "army_type": army["army_type"],
                "location": army["location"],
                "unit_count": army["unit_count"],
                "total_health": army["army_health"]["current"],
                "max_health": army["army_health"]["maximum"],
                "unique_id": army["unique_id"],
                "points": army["points"],
                "status": army["army_status"],
                "can_act": army["has_units"] and army["army_status"] != "eliminated",
            }
            army_summaries.append(summary)

        return army_summaries

    def get_unit_selection_data(self, player_name: str, army_identifier: str) -> Dict[str, Any]:
        """Get unit data formatted for unit selection dialogs."""
        army_data = self.game_state_manager.get_army_data(player_name, army_identifier)
        units = strict_get(army_data, "units")

        selection_data = {
            "army_name": strict_get(army_data, "name"),
            "army_id": army_identifier,
            "player": player_name,
            "units": [],
            "total_units": len(units),
            "alive_units": 0,
            "species_breakdown": {},
            "element_breakdown": {},
        }

        for unit in units:
            unit_info = {
                "id": strict_get_optional(unit, "id", strict_get(unit, "name")),
                "name": strict_get(unit, "name"),
                "species": strict_get(unit, "species"),
                "health": strict_get(unit, "health"),
                "max_health": strict_get(unit, "max_health"),
                "is_alive": strict_get(unit, "health") > 0,
                "elements": self._get_unit_elements(unit),
                "selectable": strict_get(unit, "health") > 0,  # Only alive units selectable by default
            }

            selection_data["units"].append(unit_info)

            if unit_info["is_alive"]:
                selection_data["alive_units"] += 1

                # Update species breakdown
                species = unit_info["species"]
                selection_data["species_breakdown"][species] = selection_data["species_breakdown"].get(species, 0) + 1

                # Update element breakdown
                for element in unit_info["elements"]:
                    selection_data["element_breakdown"][element] = (
                        selection_data["element_breakdown"].get(element, 0) + 1
                    )

        return selection_data

    def get_terrain_army_info(self, location: str) -> Dict[str, Any]:
        """Get information about all armies at a specific terrain."""
        terrain_info = {
            "location": location,
            "armies": [],
            "total_armies": 0,
            "players_present": [],
            "controller": None,
            "contested": False,
        }

        all_players = self.game_state_manager.get_all_player_names()

        for player_name in all_players:
            armies_at_location = self.game_state_manager.get_all_armies_at_location(player_name, location)

            for army_data in armies_at_location:
                formatted_army = self._format_single_army(strict_get(army_data, "army_type"), army_data)
                formatted_army["player"] = player_name
                terrain_info["armies"].append(formatted_army)

                if player_name not in terrain_info["players_present"]:
                    terrain_info["players_present"].append(player_name)

        terrain_info["total_armies"] = len(terrain_info["armies"])
        terrain_info["contested"] = len(terrain_info["players_present"]) > 1

        # Determine terrain controller
        try:
            terrain_info["controller"] = self.game_state_manager.get_terrain_controller(location)
        except Exception:
            terrain_info["controller"] = None

        return terrain_info
