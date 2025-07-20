"""
Turn Flow Controller for Dragon Dice

Coordinates the overall turn flow and phase transitions by orchestrating
all the focused phase controllers. Acts as the primary coordinator between
the GameOrchestrator and the specialized phase controllers.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from .automatic_phase_controller import AutomaticPhaseController
from .march_phase_controller import MarchPhaseController
from .reserves_phase_controller import ReservesPhaseController
from .species_abilities_controller import SpeciesAbilitiesController


class TurnFlowController(QObject):
    """
    Master controller for coordinating turn flow across all phase controllers.

    Manages phase transitions, player turn coordination, and ensures proper
    sequencing of the Dragon Dice turn structure.
    """

    # =============================================================================
    # SIGNALS
    # =============================================================================

    # Turn coordination signals
    turn_flow_initialized = Signal(str)  # player_name
    turn_completed = Signal(str)  # player_name
    game_flow_error = Signal(str, str)  # error_type, error_message

    # Phase coordination signals
    phase_controller_activated = Signal(str, str)  # phase_name, controller_type
    phase_transition_ready = Signal(str, str)  # from_phase, to_phase

    # Status signals
    turn_flow_status = Signal(str)  # status_message

    def __init__(self, game_orchestrator, parent=None):
        super().__init__(parent)
        self.game_orchestrator = game_orchestrator

        # Current turn state
        self.current_player = ""
        self.current_phase = ""
        self.active_controller = None

        # Initialize phase controllers
        self._initialize_phase_controllers()

        # Connect to game orchestrator
        self._setup_game_orchestrator_connections()

    def _initialize_phase_controllers(self):
        """Initialize all phase controllers."""
        self.march_controller = MarchPhaseController(self.game_orchestrator, self)
        self.automatic_controller = AutomaticPhaseController(self.game_orchestrator, self)
        self.reserves_controller = ReservesPhaseController(self.game_orchestrator, self)
        self.species_controller = SpeciesAbilitiesController(self.game_orchestrator, self)

        # Store controllers by phase mapping
        self.phase_controllers = {
            "FIRST_MARCH": self.march_controller,
            "SECOND_MARCH": self.march_controller,
            "EXPIRE_EFFECTS": self.automatic_controller,
            "EIGHTH_FACE": self.automatic_controller,
            "DRAGON_ATTACKS": self.automatic_controller,
            "SPECIES_ABILITIES": self.species_controller,
            "RESERVES": self.reserves_controller,
        }

        # Connect phase controller signals
        self._setup_phase_controller_connections()

    def _setup_game_orchestrator_connections(self):
        """Set up connections with game orchestrator."""
        # Connect to orchestrator phase/player signals
        self.game_orchestrator.current_phase_changed.connect(self._handle_phase_change)
        self.game_orchestrator.current_player_changed.connect(self._handle_player_change)

        # Connect to turn manager signals if available
        if hasattr(self.game_orchestrator, "turn_manager"):
            self.game_orchestrator.turn_manager.turn_changed.connect(self._handle_turn_change)

    def _setup_phase_controller_connections(self):
        """Set up connections with phase controllers."""
        # March controller connections
        self.march_controller.march_phase_completed.connect(self._handle_phase_completion)
        self.march_controller.march_error.connect(self._handle_controller_error)
        self.march_controller.march_status_update.connect(self._handle_controller_status)

        # Automatic controller connections
        self.automatic_controller.phase_completed.connect(self._handle_phase_completion)
        self.automatic_controller.phase_error.connect(self._handle_controller_error)
        self.automatic_controller.phase_status_update.connect(self._handle_controller_status)

        # Reserves controller connections (parameterless signal)
        self.reserves_controller.reserves_phase_completed.connect(self._handle_parameterless_completion)
        self.reserves_controller.reserves_error.connect(self._handle_controller_error)
        self.reserves_controller.reserves_status_update.connect(self._handle_controller_status)

        # Species abilities controller connections (parameterless signal)
        self.species_controller.species_phase_completed.connect(self._handle_parameterless_completion)
        self.species_controller.species_error.connect(self._handle_controller_error)
        self.species_controller.species_status_update.connect(self._handle_controller_status)

    # =============================================================================
    # GAME ORCHESTRATOR EVENT HANDLING
    # =============================================================================

    @Slot(str)
    def _handle_phase_change(self, phase_display: str):
        """Handle phase changes from game orchestrator."""
        new_phase = self.game_orchestrator.get_current_phase()
        old_phase = self.current_phase

        print(f"TurnFlowController: Phase change from {old_phase} to {new_phase}")

        # Deactivate previous controller
        if self.active_controller:
            self._deactivate_current_controller()

        # Update current phase
        self.current_phase = new_phase

        # Activate appropriate controller for new phase
        self._activate_phase_controller(new_phase)

        # Emit coordination signals
        self.phase_transition_ready.emit(old_phase, new_phase)

    @Slot(str)
    def _handle_player_change(self, player_name: str):
        """Handle player changes from game orchestrator."""
        old_player = self.current_player
        self.current_player = player_name

        print(f"TurnFlowController: Player change from {old_player} to {player_name}")

        if old_player and old_player != player_name:
            # Previous player's turn completed
            self.turn_completed.emit(old_player)

        # Initialize new player's turn
        self.turn_flow_initialized.emit(player_name)

    @Slot(int)
    def _handle_turn_change(self, turn_number: int):
        """Handle turn number changes."""
        print(f"TurnFlowController: Turn changed to {turn_number}")
        self.turn_flow_status.emit(f"Starting turn {turn_number}")

    # =============================================================================
    # PHASE CONTROLLER MANAGEMENT
    # =============================================================================

    def _activate_phase_controller(self, phase_name: str):
        """Activate the appropriate controller for a phase."""
        controller = self.phase_controllers.get(phase_name)

        if controller:
            self.active_controller = controller
            controller_type = controller.__class__.__name__

            print(f"TurnFlowController: Activating {controller_type} for {phase_name}")

            self.phase_controller_activated.emit(phase_name, controller_type)
            self.turn_flow_status.emit(f"Entered {phase_name} phase")
        else:
            print(f"TurnFlowController: No controller found for phase {phase_name}")
            self.game_flow_error.emit("no_controller", f"No controller for phase: {phase_name}")

    def _deactivate_current_controller(self):
        """Deactivate the currently active controller."""
        if self.active_controller:
            controller_type = self.active_controller.__class__.__name__
            print(f"TurnFlowController: Deactivating {controller_type}")

        self.active_controller = None

    # =============================================================================
    # PHASE CONTROLLER EVENT HANDLING
    # =============================================================================

    @Slot(str)
    def _handle_phase_completion(self, phase_name: str):
        """Handle phase completion from controllers."""
        if not phase_name:
            # Handle parameterless signals (like reserves_phase_completed)
            phase_name = self.current_phase

        print(f"TurnFlowController: Phase {phase_name} completed by controller")

        # Deactivate current controller
        self._deactivate_current_controller()

        # Now advance the phase through the game orchestrator
        self.turn_flow_status.emit(f"Completed {phase_name} phase")

        # Use the game orchestrator's turn manager to advance phase
        if hasattr(self.game_orchestrator, "turn_manager"):
            self.game_orchestrator.turn_manager.advance_phase()
        else:
            # Fallback to direct advance_phase call
            if hasattr(self.game_orchestrator, "advance_phase"):
                self.game_orchestrator.advance_phase()

    @Slot()
    def _handle_parameterless_completion(self):
        """Handle parameterless phase completion signals."""
        # Use the current phase as the completed phase
        self._handle_phase_completion(self.current_phase)

    @Slot(str, str)
    def _handle_controller_error(self, error_type: str, error_message: str):
        """Handle errors from phase controllers."""
        active_controller_name = ""
        if self.active_controller:
            active_controller_name = self.active_controller.__class__.__name__

        print(f"TurnFlowController: Error in {active_controller_name}: {error_type} - {error_message}")

        # Forward error with context
        contextual_error = f"[{active_controller_name}] {error_message}"
        self.game_flow_error.emit(error_type, contextual_error)

    @Slot(str)
    def _handle_controller_status(self, status_message: str):
        """Handle status updates from phase controllers."""
        active_controller_name = ""
        if self.active_controller:
            active_controller_name = self.active_controller.__class__.__name__

        # Forward status with controller context
        contextual_status = f"[{active_controller_name}] {status_message}"
        self.turn_flow_status.emit(contextual_status)

    # =============================================================================
    # TURN FLOW COORDINATION
    # =============================================================================

    def get_turn_flow_state(self) -> Dict[str, Any]:
        """Get comprehensive turn flow state."""
        active_controller_state = {}
        active_controller_name = ""

        if self.active_controller:
            active_controller_name = self.active_controller.__class__.__name__

            # Get controller-specific state
            if hasattr(self.active_controller, "get_current_march_state"):
                active_controller_state = self.active_controller.get_current_march_state()
            elif hasattr(self.active_controller, "get_current_phase_state"):
                active_controller_state = self.active_controller.get_current_phase_state()
            elif hasattr(self.active_controller, "get_current_reserves_state"):
                active_controller_state = self.active_controller.get_current_reserves_state()
            elif hasattr(self.active_controller, "get_current_species_state"):
                active_controller_state = self.active_controller.get_current_species_state()

        return {
            "current_player": self.current_player,
            "current_phase": self.current_phase,
            "active_controller": active_controller_name,
            "controller_state": active_controller_state,
            "available_controllers": list(self.phase_controllers.keys()),
        }

    def get_phase_controller_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all phase controllers and their states."""
        summary = {}

        for phase_name, controller in self.phase_controllers.items():
            controller_name = controller.__class__.__name__
            is_active = controller == self.active_controller

            controller_info: Dict[str, Any] = {"controller_class": controller_name, "is_active": is_active, "handles_phases": []}

            # Find all phases this controller handles
            for phase, ctrl in self.phase_controllers.items():
                if ctrl == controller:
                    controller_info["handles_phases"].append(phase)

            # Remove duplicates
            handles_phases_list: List[str] = controller_info["handles_phases"]
            controller_info["handles_phases"] = list(set(handles_phases_list))

            summary[phase_name] = controller_info

        return summary

    # =============================================================================
    # MANUAL CONTROL INTERFACE
    # =============================================================================

    @Slot(str)
    def force_phase_completion(self, phase_name: str):
        """Force completion of current phase (for testing/admin)."""
        print(f"TurnFlowController: Force completing phase {phase_name}")

        if self.active_controller:
            # Try to call skip method on active controller
            if hasattr(self.active_controller, "skip_march_phase"):
                self.active_controller.skip_march_phase()
            elif hasattr(self.active_controller, "skip_current_phase"):
                self.active_controller.skip_current_phase()
            elif hasattr(self.active_controller, "skip_reserves_phase"):
                self.active_controller.skip_reserves_phase()
            elif hasattr(self.active_controller, "skip_species_abilities_phase"):
                self.active_controller.skip_species_abilities_phase()
            else:
                # Fallback: directly emit completion
                self._handle_phase_completion(phase_name)
        else:
            # No active controller, just advance through orchestrator
            self.game_orchestrator.advance_phase()

    @Slot()
    def force_turn_advance(self):
        """Force advancement to next player's turn (for testing/admin)."""
        print("TurnFlowController: Force advancing to next player")

        # Complete current phase and advance through turn manager
        if hasattr(self.game_orchestrator, "turn_manager"):
            self.game_orchestrator.turn_manager.advance_player()
        else:
            self.game_flow_error.emit("no_turn_manager", "Turn manager not available")

    def get_controller_for_phase(self, phase_name: str) -> Optional[QObject]:
        """Get the controller responsible for a specific phase."""
        return self.phase_controllers.get(phase_name)

    # =============================================================================
    # PUBLIC DIAGNOSTIC INTERFACE
    # =============================================================================

    def diagnose_turn_flow(self) -> Dict[str, Any]:
        """Provide diagnostic information about turn flow state."""
        turn_info = {}
        if hasattr(self.game_orchestrator, "turn_manager"):
            turn_info = self.game_orchestrator.turn_manager.get_turn_info()

        return {
            "turn_flow_controller": {
                "current_player": self.current_player,
                "current_phase": self.current_phase,
                "active_controller": self.active_controller.__class__.__name__ if self.active_controller else None,
            },
            "game_orchestrator": {
                "current_player": self.game_orchestrator.get_current_player_name(),
                "current_phase": self.game_orchestrator.get_current_phase(),
            },
            "turn_manager": turn_info,
            "phase_controller_mapping": {
                phase: controller.__class__.__name__ for phase, controller in self.phase_controllers.items()
            },
        }
