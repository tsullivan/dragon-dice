"""
Combat Analysis Controller for Dragon Dice.

This controller provides views with access to combat analysis services
without requiring direct imports from game_logic.
"""

from PySide6.QtCore import QObject, Signal, Slot

from controllers.combat_service import CombatService


class CombatAnalysisController(QObject):
    """
    Controller for combat analysis operations, providing a clean interface
    between UI components and combat services.
    """

    analysis_completed = Signal(dict)  # Emits analysis results
    sai_effects_available = Signal(dict)  # Emits SAI processing results

    def __init__(self, parent=None):
        super().__init__(parent)
        self.combat_service = CombatService(self)

        # Connect service signals
        self.combat_service.combat_results_calculated.connect(self.analysis_completed)
        self.combat_service.sai_effects_processed.connect(self.sai_effects_available)

    @Slot(dict, str, list, list, bool, bool, result=dict)
    def analyze_combat_roll(
        self,
        roll_results: dict,
        combat_type: str,
        army_units: list,
        terrain_elements: list = None,
        is_attacker: bool = True,
        terrain_eighth_face_controlled: bool = False,
    ) -> dict:
        """
        Analyze combat roll results through the service layer.

        This is the main interface for views to request combat analysis.
        """
        return self.combat_service.analyze_combat_roll(
            roll_results,
            combat_type,
            army_units,
            terrain_elements or [],
            is_attacker,
            terrain_eighth_face_controlled,
        )

    @Slot(dict, str, list, list, bool, bool, result=dict)
    def process_sai_effects(
        self,
        roll_results: dict,
        combat_type: str,
        army_units: list,
        terrain_elements: list = None,
        is_attacker: bool = True,
        terrain_eighth_face_controlled: bool = False,
    ) -> dict:
        """
        Process only SAI effects without full combat analysis.
        """
        return self.combat_service.process_sai_effects_only(
            roll_results,
            combat_type,
            army_units,
            terrain_elements or [],
            is_attacker,
            terrain_eighth_face_controlled,
        )

    @Slot(dict, list, str, result=dict)
    def analyze_unit_die_faces(self, unit_data: dict, face_results: list, combat_type: str) -> dict:
        """
        Analyze die face results for a single unit.
        """
        return self.combat_service.analyze_die_faces_only(unit_data, face_results, combat_type)

    @Slot(dict, str, result=list)
    def get_combat_actions(self, army_data: dict, location: str) -> list:
        """
        Get available combat actions for an army.
        """
        return self.combat_service.get_available_combat_actions(army_data, location)

    @Slot(dict, str, result=dict)
    def calculate_damage_potential(self, combat_results: dict, target_type: str = "army") -> dict:
        """
        Calculate potential damage from combat results.
        """
        return self.combat_service.calculate_damage_potential(combat_results, target_type)

    @Slot(dict, str, result=dict)
    def get_maneuver_options(self, army_data: dict, current_location: str) -> dict:
        """
        Get available maneuver options for an army.
        """
        return self.combat_service.get_maneuver_options(army_data, current_location)

    def get_combat_service(self) -> CombatService:
        """
        Get direct access to the combat service for advanced use cases.

        This should be used sparingly and only when the controller interface
        is insufficient.
        """
        return self.combat_service
