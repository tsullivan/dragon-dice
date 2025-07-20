"""
Reserves Phase Controller for Dragon Dice

Handles the final phase of each player's turn where they can:
- Deploy units from reserves to existing armies
- Form new armies from reserve units
- Make final strategic preparations before next player's turn
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get_optional


class ReservesPhaseController(QObject):
    """
    Controller for the Reserves Phase interaction patterns.

    Manages deployment decisions, army formation, and reserve management.
    Coordinates with GameOrchestrator and existing reserve infrastructure.
    """

    # =============================================================================
    # SIGNALS
    # =============================================================================

    # Phase completion signals
    reserves_phase_completed = Signal()

    # Deployment signals
    deployment_options_available = Signal(str, list)  # player_name, deployment_options
    deployment_required = Signal(str, dict)  # player_name, deployment_context
    deployment_completed = Signal(str, dict)  # player_name, deployment_results

    # Army formation signals
    army_formation_available = Signal(str, list)  # player_name, available_units
    army_formation_completed = Signal(str, str)  # player_name, new_army_id

    # Strategic signals
    spell_preparation_available = Signal(str, list)  # player_name, available_spells
    tactical_decision_required = Signal(str, dict)  # player_name, decision_context

    # Error and status signals
    reserves_error = Signal(str, str)  # error_type, error_message
    reserves_status_update = Signal(str)  # status_message

    def __init__(self, game_orchestrator, parent=None):
        super().__init__(parent)
        self.game_orchestrator = game_orchestrator
        self.core_engine = game_orchestrator.core_engine

        # Current reserves state
        self.current_player = ""
        self.reserves_context = {}  # Store deployment/formation state
        self.actions_taken = []  # Track what player has done this phase

        # Connect to game orchestrator signals
        self._setup_signal_connections()

    def _setup_signal_connections(self):
        """Set up signal connections with game orchestrator."""
        # Connect to orchestrator phase signals
        self.game_orchestrator.current_phase_changed.connect(self._handle_phase_change)
        self.game_orchestrator.current_player_changed.connect(self._handle_player_change)

        # Note: TurnFlowController will handle phase completion coordination
        # Individual controllers should not directly advance phases

    # =============================================================================
    # PHASE COORDINATION
    # =============================================================================

    @Slot(str)
    def _handle_phase_change(self, phase_display: str):
        """Handle phase changes from game orchestrator."""
        phase = self.game_orchestrator.get_current_phase()

        if phase == "RESERVES":
            self._enter_reserves_phase()
        elif self.current_player:
            # Exiting reserves phase
            self._exit_reserves_phase()

    @Slot(str)
    def _handle_player_change(self, player_name: str):
        """Handle player changes from game orchestrator."""
        self.current_player = player_name

    def _enter_reserves_phase(self):
        """Enter the reserves phase."""
        self.current_player = self.game_orchestrator.get_current_player_name()
        self.reserves_context.clear()
        self.actions_taken.clear()

        print(f"ReservesPhaseController: Entering reserves phase for {self.current_player}")

        # Analyze reserves and present options
        self._analyze_reserves_opportunities()

    def _exit_reserves_phase(self):
        """Exit reserves phase."""
        print("ReservesPhaseController: Exiting reserves phase")

        self.current_player = ""
        self.reserves_context.clear()
        self.actions_taken.clear()

    # =============================================================================
    # RESERVES ANALYSIS AND OPTIONS
    # =============================================================================

    def _analyze_reserves_opportunities(self):
        """Analyze reserve units and present deployment/formation options."""
        reserve_units = self._get_player_reserve_units()

        if not reserve_units:
            # No reserves, skip phase
            self.reserves_status_update.emit("No units in reserves")
            self.reserves_phase_completed.emit()
            return

        # Get deployment opportunities
        deployment_options = self._get_deployment_opportunities(reserve_units)
        formation_options = self._get_army_formation_opportunities(reserve_units)

        # Store options in context
        self.reserves_context = {
            "reserve_units": reserve_units,
            "deployment_options": deployment_options,
            "formation_options": formation_options,
            "can_skip": True,  # Reserves phase is optional
        }

        if deployment_options or formation_options:
            # Present options to player
            all_options = []

            if deployment_options:
                all_options.extend([{"type": "deploy", "data": opt} for opt in deployment_options])

            if formation_options:
                all_options.append({"type": "form_army", "data": {"available_units": reserve_units}})

            # Always allow skipping
            all_options.append({"type": "skip", "data": {}})

            self.deployment_options_available.emit(self.current_player, all_options)
        else:
            # No valid options, skip phase
            self.reserves_status_update.emit("No valid deployment or formation options")
            self.reserves_phase_completed.emit()

    def _get_player_reserve_units(self) -> List[Dict[str, Any]]:
        """Get units in player's reserves."""
        if hasattr(self.game_orchestrator, "reserves_manager"):
            reserves = self.game_orchestrator.reserves_manager.get_player_reserves(self.current_player)
            return list(reserves)  # Type cast to List[Dict[str, Any]]

        # Fallback to core engine
        fallback_reserves = self.core_engine.get_player_reserve_units(self.current_player)
        return list(fallback_reserves)  # Type cast to List[Dict[str, Any]]

    def _get_deployment_opportunities(self, reserve_units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get opportunities to deploy reserve units to existing armies."""
        deployment_options = []
        existing_armies = self.core_engine.get_player_armies_summary(self.current_player)

        for army_data in existing_armies:
            army_id = strict_get_optional(army_data, "army_id", "")
            location = strict_get_optional(army_data, "location", "")

            if location == "reserves":
                continue  # Can't deploy to reserves

            # Check if any reserve units can join this army
            compatible_units = self._get_compatible_reserve_units(reserve_units, army_data)

            if compatible_units:
                deployment_options.append(
                    {
                        "army_id": army_id,
                        "location": location,
                        "army_summary": army_data,
                        "compatible_units": compatible_units,
                        "deployment_limit": self._get_deployment_limit(army_data),
                    }
                )

        return deployment_options

    def _get_compatible_reserve_units(
        self, reserve_units: List[Dict[str, Any]], army_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get reserve units compatible with an existing army."""
        army_race = strict_get_optional(army_data, "race", "")
        compatible_units = []

        for unit in reserve_units:
            unit_race = strict_get_optional(unit, "race", "")

            # Basic compatibility: same race or neutral units
            if unit_race == army_race or unit_race == "neutral":
                compatible_units.append(unit)

        return compatible_units

    def _get_deployment_limit(self, army_data: Dict[str, Any]) -> int:
        """Get maximum units that can be deployed to an army."""
        # Standard Dragon Dice rule: armies have unit limits based on location
        strict_get_optional(army_data, "location", "")
        current_army_size = len(strict_get_optional(army_data, "units", []))

        # Most terrains allow 18 units (3 per health level * 6 levels)
        # This could be terrain-specific in a full implementation
        max_army_size = 18

        return max(0, max_army_size - current_army_size)

    def _get_army_formation_opportunities(self, reserve_units: List[Dict[str, Any]]) -> bool:
        """Check if new armies can be formed from reserves."""
        # Group units by race to see formation possibilities
        units_by_race: Dict[str, List[Dict[str, Any]]] = {}
        for unit in reserve_units:
            race = strict_get_optional(unit, "race", "")
            if race not in units_by_race:
                units_by_race[race] = []
            units_by_race[race].append(unit)

        # Can form army if we have at least 1 unit of any race
        return any(len(units) > 0 for units in units_by_race.values())

    # =============================================================================
    # DEPLOYMENT ACTIONS
    # =============================================================================

    @Slot(str, dict)
    def handle_reserves_choice(self, player_name: str, choice_data: dict):
        """Handle reserves phase choice from UI."""
        if player_name != self.current_player:
            self.reserves_error.emit("invalid_player", f"Not {player_name}'s turn")
            return

        choice_type = strict_get_optional(choice_data, "type", "")
        choice_data_payload: Dict[str, Any] = strict_get_optional(choice_data, "data", {})

        print(f"ReservesPhaseController: {player_name} chose {choice_type}")

        if choice_type == "deploy":
            self._execute_unit_deployment(choice_data_payload)
        elif choice_type == "form_army":
            self._execute_army_formation(choice_data_payload)
        elif choice_type == "skip":
            self._complete_reserves_phase()
        else:
            self.reserves_error.emit("invalid_choice", f"Unknown reserves choice: {choice_type}")

    def _execute_unit_deployment(self, deployment_data: Dict[str, Any]):
        """Execute deployment of reserve units to existing army."""
        army_id = strict_get_optional(deployment_data, "army_id", "")
        selected_units: List[Dict[str, Any]] = strict_get_optional(deployment_data, "selected_units", [])

        if not army_id or not selected_units:
            self.reserves_error.emit("invalid_deployment", "Missing army ID or units")
            return

        # Execute deployment through reserves manager
        if hasattr(self.game_orchestrator, "reserves_manager"):
            result = self.game_orchestrator.reserves_manager.deploy_units_to_army(
                self.current_player, selected_units, army_id
            )

            if result.get("success", False):
                self.actions_taken.append(
                    {"type": "deployment", "army_id": army_id, "units_deployed": len(selected_units)}
                )

                self.deployment_completed.emit(self.current_player, result)
                self.reserves_status_update.emit(f"Deployed {len(selected_units)} units to army {army_id}")

                # Check if more actions possible or complete phase
                self._check_additional_actions()
            else:
                error_msg = result.get("error", "Deployment failed")
                self.reserves_error.emit("deployment_failed", error_msg)

    def _execute_army_formation(self, formation_data: Dict[str, Any]):
        """Execute formation of new army from reserve units."""
        selected_units: List[Dict[str, Any]] = strict_get_optional(formation_data, "selected_units", [])
        target_location = strict_get_optional(formation_data, "target_location", "")

        if not selected_units:
            self.reserves_error.emit("invalid_formation", "No units selected for formation")
            return

        # Execute army formation through reserves manager
        if hasattr(self.game_orchestrator, "reserves_manager"):
            result = self.game_orchestrator.reserves_manager.form_new_army(
                self.current_player, selected_units, target_location
            )

            if result.get("success", False):
                new_army_id = result.get("army_id", "")

                self.actions_taken.append(
                    {"type": "formation", "army_id": new_army_id, "units_used": len(selected_units)}
                )

                self.army_formation_completed.emit(self.current_player, new_army_id)
                self.reserves_status_update.emit(f"Formed new army {new_army_id} with {len(selected_units)} units")

                # Check if more actions possible or complete phase
                self._check_additional_actions()
            else:
                error_msg = result.get("error", "Army formation failed")
                self.reserves_error.emit("formation_failed", error_msg)

    def _check_additional_actions(self):
        """Check if player can take additional reserve actions."""
        # Re-analyze remaining reserves after action
        remaining_reserves = self._get_player_reserve_units()

        if remaining_reserves:
            # Player might want to do more, re-present options
            self._analyze_reserves_opportunities()
        else:
            # No reserves left, complete phase
            self._complete_reserves_phase()

    def _complete_reserves_phase(self):
        """Complete the reserves phase."""
        actions_count = len(self.actions_taken)

        if actions_count == 0:
            self.reserves_status_update.emit("No reserves actions taken")
        else:
            self.reserves_status_update.emit(f"Completed {actions_count} reserves actions")

        self.reserves_phase_completed.emit()

    # =============================================================================
    # SPELL PREPARATION (ADVANCED FEATURE)
    # =============================================================================

    def _check_spell_preparation_opportunities(self):
        """Check if player can prepare spells during reserves phase."""
        # This would be for advanced spell preparation rules
        if hasattr(self.game_orchestrator, "spell_manager"):
            available_spells = self.game_orchestrator.spell_manager.get_preparable_spells(self.current_player)

            if available_spells:
                self.spell_preparation_available.emit(self.current_player, available_spells)

    @Slot(str, list)
    def handle_spell_preparation(self, player_name: str, selected_spells: list):
        """Handle spell preparation during reserves phase."""
        if player_name != self.current_player:
            self.reserves_error.emit("invalid_player", f"Not {player_name}'s turn")
            return

        # Execute spell preparation
        if hasattr(self.game_orchestrator, "spell_manager"):
            result = self.game_orchestrator.spell_manager.prepare_spells(player_name, selected_spells)

            if result.get("success", False):
                self.reserves_status_update.emit(f"Prepared {len(selected_spells)} spells")
            else:
                error_msg = result.get("error", "Spell preparation failed")
                self.reserves_error.emit("spell_preparation_failed", error_msg)

    # =============================================================================
    # PUBLIC INTERFACE
    # =============================================================================

    def get_current_reserves_state(self) -> Dict[str, Any]:
        """Get current reserves phase state for UI display."""
        return {
            "player": self.current_player,
            "context": self.reserves_context,
            "actions_taken": self.actions_taken.copy(),
            "can_take_more_actions": len(self._get_player_reserve_units()) > 0,
        }

    def get_reserve_summary(self) -> Dict[str, Any]:
        """Get summary of player's reserve status."""
        reserve_units = self._get_player_reserve_units()

        # Group by race for summary
        units_by_race = {}
        for unit in reserve_units:
            race = strict_get_optional(unit, "race", "unknown")
            if race not in units_by_race:
                units_by_race[race] = 0
            units_by_race[race] += 1

        return {
            "total_units": len(reserve_units),
            "units_by_race": units_by_race,
            "deployment_opportunities": len(self.reserves_context.get("deployment_options", [])),
            "can_form_armies": self.reserves_context.get("formation_options", False),
        }

    @Slot()
    def skip_reserves_phase(self):
        """Skip the reserves phase without taking actions."""
        print("ReservesPhaseController: Skipping reserves phase")
        self._complete_reserves_phase()
