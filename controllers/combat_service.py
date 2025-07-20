"""
Combat Service for Dragon Dice.

This service provides a clean interface for combat-related operations,
abstracting away the underlying game logic components from the UI layer.
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal

from models.die_face_analyzer import DieFaceAnalyzer
from models.sai_processor import SAIProcessor
from utils.field_access import strict_get, strict_get_optional


class CombatService(QObject):
    """
    Service layer for combat operations, providing a clean interface
    between UI components and game logic processors.
    """

    combat_results_calculated = Signal(dict)  # Emits calculated combat results
    sai_effects_processed = Signal(dict)  # Emits SAI processing results

    def __init__(self, parent=None):
        super().__init__(parent)
        self.die_face_analyzer = DieFaceAnalyzer()
        self.sai_processor = SAIProcessor()

    def analyze_combat_roll(
        self,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        terrain_elements: List[str] = None,
        is_attacker: bool = True,
        terrain_eighth_face_controlled: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze combat roll results including SAI processing.

        Args:
            roll_results: Dictionary mapping unit names to their die face results
            combat_type: Type of combat ("melee", "missile", "magic", "maneuver")
            army_units: List of units participating in combat
            terrain_elements: Elements of the terrain (for SAI effects)
            is_attacker: Whether this army is the attacker
            terrain_eighth_face_controlled: Whether army controls terrain eighth face

        Returns:
            Dictionary with analyzed results and SAI effects
        """
        # Process SAI effects
        self.sai_processor.process_combat_roll(
            roll_results,
            combat_type,
            army_units,
            is_attacker=is_attacker,
            terrain_elements=terrain_elements or [],
            terrain_eighth_face_controlled=terrain_eighth_face_controlled,
        )

        # Analyze die face results
        analysis_results = {}
        for unit_name, face_results in roll_results.items():
            unit_data = next((u for u in army_units if strict_get(u, "name") == unit_name), None)
            if not unit_data:
                continue

            unit_analysis = self.die_face_analyzer.analyze_unit_results(unit_data, face_results, combat_type)
            analysis_results[unit_name] = unit_analysis

        # Compile comprehensive results
        combat_results = {
            "roll_results": roll_results,
            "combat_type": combat_type,
            "unit_analyses": analysis_results,
            "sai_effects": self.sai_processor.get_processed_effects(),
            "total_results": self._calculate_total_results(analysis_results),
        }

        self.combat_results_calculated.emit(combat_results)
        return combat_results

    def _calculate_total_results(self, unit_analyses: Dict[str, Any]) -> Dict[str, int]:
        """Calculate total results across all units."""
        totals = {
            "melee": 0,
            "missile": 0,
            "magic": 0,
            "save": 0,
            "id": 0,
            "maneuver": 0,
            "sai": 0,
        }

        for _unit_name, analysis in unit_analyses.items():
            results = strict_get_optional(analysis, "results", {})
            for result_type, count in results.items():
                if result_type.lower() in totals:
                    totals[result_type.lower()] += count

        return totals

    def process_sai_effects_only(
        self,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        terrain_elements: List[str] = None,
        is_attacker: bool = True,
        terrain_eighth_face_controlled: bool = False,
    ) -> Dict[str, Any]:
        """
        Process only SAI effects without full combat analysis.

        Useful for UI components that only need SAI processing.
        """
        self.sai_processor.process_combat_roll(
            roll_results,
            combat_type,
            army_units,
            is_attacker=is_attacker,
            terrain_elements=terrain_elements or [],
            terrain_eighth_face_controlled=terrain_eighth_face_controlled,
        )

        sai_results = {
            "sai_effects": self.sai_processor.get_processed_effects(),
            "combat_type": combat_type,
            "units_processed": len(army_units),
        }

        self.sai_effects_processed.emit(sai_results)
        return sai_results

    def analyze_die_faces_only(
        self, unit_data: Dict[str, Any], face_results: List[str], combat_type: str
    ) -> Dict[str, Any]:
        """
        Analyze die face results for a single unit without SAI processing.

        Useful for simple die face analysis in UI components.
        """
        return self.die_face_analyzer.analyze_unit_results(unit_data, face_results, combat_type)

    def get_available_combat_actions(self, army_data: Dict[str, Any], location: str) -> List[str]:
        """
        Get available combat actions for an army at a location.

        Returns list of available actions: ['melee', 'missile', 'magic', 'maneuver']
        """
        actions = []

        # Basic combat actions are always available if army has units
        army_units = strict_get_optional(army_data, "units", [])
        alive_units = [u for u in army_units if strict_get(u, "health") > 0]

        if alive_units:
            actions.extend(["melee", "missile", "magic", "maneuver"])

        # Additional actions based on terrain/special conditions could be added here
        # For example: eighth face actions, species abilities, etc.

        return actions

    def calculate_damage_potential(self, combat_results: Dict[str, Any], target_type: str = "army") -> Dict[str, Any]:
        """
        Calculate potential damage from combat results.

        Args:
            combat_results: Results from analyze_combat_roll
            target_type: Type of target ("army", "dragon", etc.)

        Returns:
            Dictionary with damage calculations
        """
        total_results = strict_get_optional(combat_results, "total_results", {})

        damage_potential = {
            "melee_damage": total_results.get("melee", 0),
            "missile_damage": total_results.get("missile", 0),
            "magic_damage": total_results.get("magic", 0),
            "total_offensive": total_results.get("melee", 0)
            + total_results.get("missile", 0)
            + total_results.get("magic", 0),
            "saves_available": total_results.get("save", 0),
            "special_effects": len(strict_get_optional(combat_results, "sai_effects", [])),
        }

        # Adjust damage based on target type
        if target_type == "dragon":
            # Dragons have specific vulnerabilities and resistances
            damage_potential["effective_damage"] = max(
                damage_potential["melee_damage"], damage_potential["missile_damage"]
            )  # Can't combine melee and missile vs dragons
        else:
            # Normal army vs army combat
            damage_potential["effective_damage"] = damage_potential["total_offensive"]

        return damage_potential

    def get_maneuver_options(self, army_data: Dict[str, Any], current_location: str) -> Dict[str, Any]:
        """
        Get available maneuver options for an army.

        Returns information about possible maneuver actions and requirements.
        """
        army_units = strict_get_optional(army_data, "units", [])
        alive_units = [u for u in army_units if strict_get(u, "health") > 0]

        maneuver_options = {
            "can_maneuver": len(alive_units) > 0,
            "current_location": current_location,
            "unit_count": len(alive_units),
            "maneuver_types": ["advance", "retreat", "flank"],  # Basic maneuver types
            "requirements": {
                "needs_maneuver_results": True,
                "can_be_countered": True,
                "affects_position": True,
            },
        }

        # Add location-specific maneuver considerations
        if current_location.lower() in ["reserve area", "reserves"]:
            maneuver_options["maneuver_types"] = ["advance"]  # Only advance from reserves
            maneuver_options["requirements"]["can_be_countered"] = False

        return maneuver_options
