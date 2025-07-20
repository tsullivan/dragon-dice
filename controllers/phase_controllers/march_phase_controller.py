"""
March Phase Controller for Dragon Dice

Handles both First March and Second March phases with their shared interaction patterns:
- Army selection
- Maneuver decisions and counter-maneuvers
- Action decisions (melee, missile, magic, maneuver)
- Combat resolution coordination
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get_optional


class MarchPhaseController(QObject):
    """
    Controller for First March and Second March phases.

    Manages the shared flow: Army Selection → Maneuver → Action → Combat Resolution
    Coordinates with GameOrchestrator and existing dialog infrastructure.
    """

    # =============================================================================
    # SIGNALS
    # =============================================================================

    # Phase flow signals
    march_phase_completed = Signal(str)  # phase_name ("FIRST_MARCH" or "SECOND_MARCH")
    army_selection_required = Signal(str, list)  # player_name, available_armies
    maneuver_decision_required = Signal(str, str, dict)  # player_name, army_id, terrain_info
    action_decision_required = Signal(str, str, list)  # player_name, army_id, available_actions

    # Combat coordination signals
    combat_initiated = Signal(str, str, str)  # combat_type, attacker, defender
    combat_completed = Signal(dict)  # combat_results

    # Counter-maneuver signals
    counter_maneuver_opportunity = Signal(str, str, list)  # location, maneuvering_player, opposing_armies
    simultaneous_maneuver_required = Signal(dict)  # maneuver_context

    # Error and status signals
    march_error = Signal(str, str)  # error_type, error_message
    march_status_update = Signal(str)  # status_message

    def __init__(self, game_orchestrator, parent=None):
        super().__init__(parent)
        self.game_orchestrator = game_orchestrator
        self.core_engine = game_orchestrator.core_engine

        # Current march state
        self.current_march_phase = ""  # "FIRST_MARCH" or "SECOND_MARCH"
        self.current_player = ""
        self.current_acting_army = None
        self.current_march_step = ""  # "CHOOSE_ARMY", "MANEUVER", "ACTION", etc.

        # March context
        self.armies_that_marched = set()  # Track which armies have marched this turn
        self.maneuver_context = {}  # Store maneuver state for counter-maneuvers

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
    # PHASE ENTRY AND COORDINATION
    # =============================================================================

    @Slot(str)
    def _handle_phase_change(self, phase_display: str):
        """Handle phase changes from game orchestrator."""
        current_phase = self.game_orchestrator.get_current_phase()

        if current_phase in ["FIRST_MARCH", "SECOND_MARCH"]:
            self._enter_march_phase(current_phase)
        elif self.current_march_phase:
            # Exiting march phase
            self._exit_march_phase()

    @Slot(str)
    def _handle_player_change(self, player_name: str):
        """Handle player changes from game orchestrator."""
        self.current_player = player_name

    def _enter_march_phase(self, phase_name: str):
        """Enter a march phase."""
        self.current_march_phase = phase_name
        self.current_player = self.game_orchestrator.get_current_player_name()

        print(f"MarchPhaseController: Entering {phase_name} for {self.current_player}")

        # Reset march state for new phase
        if phase_name == "FIRST_MARCH":
            self.armies_that_marched.clear()

        # Start with army selection
        self._initiate_army_selection()

    def _exit_march_phase(self):
        """Exit current march phase."""
        print(f"MarchPhaseController: Exiting {self.current_march_phase}")

        self.current_march_phase = ""
        self.current_acting_army = None
        self.current_march_step = ""
        self.maneuver_context.clear()

    # =============================================================================
    # ARMY SELECTION STEP
    # =============================================================================

    def _initiate_army_selection(self):
        """Start the army selection step."""
        self.current_march_step = "CHOOSE_ARMY"

        # Get available armies for marching
        available_armies = self._get_available_marching_armies()

        if not available_armies:
            # No armies available, skip this march phase
            print(f"MarchPhaseController: No armies available for {self.current_march_phase}")
            self.march_phase_completed.emit(self.current_march_phase)
            return

        # Emit signal for UI to show army selection
        self.army_selection_required.emit(self.current_player, available_armies)

    def _get_available_marching_armies(self) -> List[Dict[str, Any]]:
        """Get armies available for marching."""
        all_armies = self.core_engine.get_player_armies_summary(self.current_player)
        available_armies = []

        for army_data in all_armies:
            army_id = strict_get_optional(army_data, "army_id", "")

            # Check if army already marched (for Second March)
            if army_id not in self.armies_that_marched:
                # Add additional context for UI
                enhanced_army_data = army_data.copy()
                enhanced_army_data["can_march"] = True
                enhanced_army_data["march_restrictions"] = self._get_army_march_restrictions(army_data)
                available_armies.append(enhanced_army_data)

        return available_armies

    def _get_army_march_restrictions(self, army_data: Dict[str, Any]) -> List[str]:
        """Get march restrictions for an army."""
        restrictions = []

        location = strict_get_optional(army_data, "location", "")
        if location == "reserves":
            restrictions.append("No maneuver step (in reserves)")
            restrictions.append("Magic action only")

        return restrictions

    @Slot(str, str)
    def select_acting_army(self, player_name: str, army_id: str):
        """Handle army selection from UI."""
        if player_name != self.current_player:
            self.march_error.emit("invalid_player", f"Not {player_name}'s turn")
            return

        if self.current_march_step != "CHOOSE_ARMY":
            self.march_error.emit("invalid_step", "Not in army selection step")
            return

        print(f"MarchPhaseController: {player_name} selected army {army_id}")

        self.current_acting_army = army_id
        self.armies_that_marched.add(army_id)

        # Proceed to maneuver decision
        self._initiate_maneuver_decision()

    # =============================================================================
    # MANEUVER DECISION STEP
    # =============================================================================

    def _initiate_maneuver_decision(self):
        """Start the maneuver decision step."""
        self.current_march_step = "MANEUVER"

        # Check if army is in reserves (skip maneuver)
        army_location = self._get_acting_army_location()
        if army_location == "reserves":
            print("MarchPhaseController: Army in reserves, skipping maneuver")
            self._initiate_action_decision()
            return

        # Get terrain and opposition info
        terrain_info = self._get_terrain_info_for_maneuver(army_location)

        # Emit signal for UI to show maneuver decision
        self.maneuver_decision_required.emit(self.current_player, self.current_acting_army, terrain_info)

    def _get_acting_army_location(self) -> str:
        """Get location of current acting army."""
        # This would delegate to game state manager via core engine
        return (
            self.game_orchestrator.game_state_manager.get_army_location_by_id(
                self.current_player, self.current_acting_army
            )
            or ""
        )

    def _get_terrain_info_for_maneuver(self, location: str) -> Dict[str, Any]:
        """Get terrain information relevant to maneuver decisions."""
        terrain_data = self.core_engine.get_all_terrain_data().get(location, {})

        # Add opposition information
        opposing_armies = self._get_opposing_armies_at_location(location)

        return {
            "location": location,
            "current_face": strict_get_optional(terrain_data, "current_face", 1),
            "terrain_type": strict_get_optional(terrain_data, "terrain_type", ""),
            "controller": strict_get_optional(terrain_data, "controller", ""),
            "opposing_armies": opposing_armies,
            "can_counter_maneuver": len(opposing_armies) > 0,
            "terrain_capture_opportunity": self._check_terrain_capture_opportunity(terrain_data),
        }

    def _get_opposing_armies_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get opposing armies at a location."""
        all_armies = self.game_orchestrator.game_state_manager.get_all_armies_at_location_all_players(location)
        opposing_armies = []

        for army_data in all_armies:
            army_player = strict_get_optional(army_data, "player_name", "")
            if army_player != self.current_player:
                opposing_armies.append(army_data)

        return opposing_armies

    def _check_terrain_capture_opportunity(self, terrain_data: Dict[str, Any]) -> bool:
        """Check if maneuver could lead to terrain capture."""
        current_face = strict_get_optional(terrain_data, "current_face", 1)
        controller = strict_get_optional(terrain_data, "controller", "")

        # Terrain capture happens when reaching 8th face and not controlling
        return current_face == 7 and controller != self.current_player

    @Slot(str, bool)
    def decide_maneuver(self, player_name: str, wants_to_maneuver: bool):
        """Handle maneuver decision from UI."""
        if player_name != self.current_player or self.current_march_step != "MANEUVER":
            self.march_error.emit("invalid_step", "Invalid maneuver decision context")
            return

        print(f"MarchPhaseController: {player_name} maneuver decision: {wants_to_maneuver}")

        if wants_to_maneuver:
            self._execute_maneuver_process()
        else:
            # Skip to action decision
            self._initiate_action_decision()

    def _execute_maneuver_process(self):
        """Execute the maneuver process with potential counter-maneuvers."""
        location = self._get_acting_army_location()
        opposing_armies = self._get_opposing_armies_at_location(location)

        if opposing_armies:
            # Request counter-maneuver decisions
            self._initiate_counter_maneuver_process(opposing_armies)
        else:
            # No opposition, maneuver automatically succeeds
            self._execute_automatic_maneuver()

    def _initiate_counter_maneuver_process(self, opposing_armies: List[Dict[str, Any]]):
        """Initiate counter-maneuver decision process."""
        location = self._get_acting_army_location()

        # Store maneuver context for later resolution
        self.maneuver_context = {
            "maneuvering_player": self.current_player,
            "maneuvering_army": self.current_acting_army,
            "location": location,
            "opposing_armies": opposing_armies,
            "counter_decisions": {},
        }

        # Emit signal for UI to handle counter-maneuver decisions
        self.counter_maneuver_opportunity.emit(location, self.current_player, opposing_armies)

    @Slot(str, bool)
    def respond_to_counter_maneuver(self, player_name: str, will_counter: bool):
        """Handle counter-maneuver response from opposing player."""
        if "counter_decisions" not in self.maneuver_context:
            self.march_error.emit("invalid_state", "No counter-maneuver context")
            return

        print(f"MarchPhaseController: {player_name} counter-maneuver response: {will_counter}")

        self.maneuver_context["counter_decisions"][player_name] = will_counter

        # Check if all opposing players have responded
        opposing_players = {
            strict_get_optional(army, "player_name", "") for army in self.maneuver_context["opposing_armies"]
        }

        if set(self.maneuver_context["counter_decisions"].keys()) >= opposing_players:
            self._resolve_maneuver_with_counters()

    def _resolve_maneuver_with_counters(self):
        """Resolve maneuver with counter-maneuver responses."""
        counter_decisions = self.maneuver_context["counter_decisions"]
        will_counter = any(counter_decisions.values())

        if will_counter:
            # Simultaneous maneuver rolls required
            self.simultaneous_maneuver_required.emit(self.maneuver_context)
        else:
            # No counters, maneuver succeeds automatically
            self._execute_automatic_maneuver()

    def _execute_automatic_maneuver(self):
        """Execute successful maneuver without rolls."""
        print("MarchPhaseController: Executing automatic maneuver success")

        # Apply maneuver results through game orchestrator
        maneuver_result = {
            "success": True,
            "automatic": True,
            "player": self.current_player,
            "army": self.current_acting_army,
            "location": self._get_acting_army_location(),
        }

        self._complete_maneuver_step(maneuver_result)

    @Slot(dict)
    def resolve_simultaneous_maneuver(self, maneuver_results: dict):
        """Handle results from simultaneous maneuver rolls."""
        print(f"MarchPhaseController: Resolving simultaneous maneuver: {maneuver_results}")

        # Process maneuver results through action resolver
        success = self.game_orchestrator.action_resolver.apply_maneuver_results(maneuver_results)

        maneuver_result = {
            "success": success,
            "automatic": False,
            "player": self.current_player,
            "army": self.current_acting_army,
            "location": self._get_acting_army_location(),
            "roll_results": maneuver_results,
        }

        self._complete_maneuver_step(maneuver_result)

    def _complete_maneuver_step(self, maneuver_result: Dict[str, Any]):
        """Complete the maneuver step and proceed to action."""
        success = maneuver_result.get("success", False)

        if success:
            self.march_status_update.emit(f"Maneuver successful for {self.current_player}")

            # Check for terrain capture (victory condition)
            if self._check_victory_after_maneuver(maneuver_result):
                return  # Game ends, don't proceed to action
        else:
            self.march_status_update.emit(f"Maneuver failed for {self.current_player}")

        # Clear maneuver context
        self.maneuver_context.clear()

        # Proceed to action decision
        self._initiate_action_decision()

    def _check_victory_after_maneuver(self, maneuver_result: Dict[str, Any]) -> bool:
        """Check if maneuver resulted in victory (2nd terrain capture)."""
        # This would check game state for victory conditions
        # For now, just return False (no victory)
        return False

    # =============================================================================
    # ACTION DECISION STEP
    # =============================================================================

    def _initiate_action_decision(self):
        """Start the action decision step."""
        self.current_march_step = "ACTION"

        # Get available actions for the army
        available_actions = self._get_available_actions()

        if not available_actions:
            # No actions available, complete march phase
            print("MarchPhaseController: No actions available, completing march")
            self.march_phase_completed.emit(self.current_march_phase)
            return

        # Emit signal for UI to show action decision
        self.action_decision_required.emit(self.current_player, self.current_acting_army, available_actions)

    def _get_available_actions(self) -> List[str]:
        """Get available actions for current acting army."""
        location = self._get_acting_army_location()

        if location == "reserves":
            # Reserves can only do magic
            return ["magic", "end_march"]

        # Get terrain face to determine allowed actions
        terrain_data = self.core_engine.get_all_terrain_data().get(location, {})
        current_face = strict_get_optional(terrain_data, "current_face", 1)
        controller = strict_get_optional(terrain_data, "controller", "")

        available_actions = []

        if current_face == 8:
            if controller == self.current_player:
                # Controlling player can choose any action
                available_actions.extend(["melee", "missile", "magic"])
            else:
                # Non-controlling player can only melee
                available_actions.append("melee")
        else:
            # Action determined by terrain face
            face_actions = {
                1: ["melee"],
                2: ["missile"],
                3: ["magic"],
                4: ["melee"],
                5: ["missile"],
                6: ["magic"],
                7: ["melee"],
            }
            available_actions.extend(face_actions.get(current_face, []))

        # Always allow ending march without action
        available_actions.append("end_march")

        return available_actions

    @Slot(str, str)
    def select_action(self, player_name: str, action_type: str):
        """Handle action selection from UI."""
        if player_name != self.current_player or self.current_march_step != "ACTION":
            self.march_error.emit("invalid_step", "Invalid action selection context")
            return

        print(f"MarchPhaseController: {player_name} selected action: {action_type}")

        if action_type == "end_march":
            # Complete march phase without action
            self.march_phase_completed.emit(self.current_march_phase)
        else:
            # Execute the selected action
            self._execute_action(action_type)

    def _execute_action(self, action_type: str):
        """Execute the selected action type."""
        self.current_march_step = f"EXECUTE_{action_type.upper()}"

        # Emit combat initiation signal
        # The specific combat handling would be done by existing combat dialogs
        # coordinated through the game orchestrator
        self.combat_initiated.emit(action_type, self.current_player, "")

        # The combat completion will be handled by combat resolution signals
        # which will eventually call _complete_action_step()

    @Slot(dict)
    def handle_combat_completion(self, combat_results: dict):
        """Handle completion of combat action."""
        print(f"MarchPhaseController: Combat completed: {combat_results}")

        self.combat_completed.emit(combat_results)
        self._complete_action_step(combat_results)

    def _complete_action_step(self, action_results: Dict[str, Any]):
        """Complete the action step and finish march phase."""
        action_type = strict_get_optional(action_results, "action_type", "unknown")
        self.march_status_update.emit(f"{action_type.title()} action completed for {self.current_player}")

        # Complete the march phase
        self.march_phase_completed.emit(self.current_march_phase)

    # =============================================================================
    # PUBLIC INTERFACE
    # =============================================================================

    def get_current_march_state(self) -> Dict[str, Any]:
        """Get current march phase state for UI display."""
        return {
            "phase": self.current_march_phase,
            "player": self.current_player,
            "acting_army": self.current_acting_army,
            "step": self.current_march_step,
            "armies_marched": list(self.armies_that_marched),
            "maneuver_active": bool(self.maneuver_context),
        }

    def can_start_second_march(self) -> bool:
        """Check if Second March can be started."""
        available_armies = self._get_available_marching_armies()
        return len(available_armies) > 0

    @Slot()
    def skip_march_phase(self):
        """Skip the current march phase."""
        print(f"MarchPhaseController: Skipping {self.current_march_phase}")
        self.march_phase_completed.emit(self.current_march_phase)
