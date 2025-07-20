"""
Game Orchestrator for Dragon Dice - Game Flow Coordination

This module manages game flow coordination, UI signal emission, manager composition,
and user input processing without containing core game rules.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from game_logic.action_resolver import ActionResolver
from game_logic.core_engine import CoreEngine
from game_logic.dragon_attack_manager import DragonAttackManager
from game_logic.eighth_face_manager import EighthFaceManager
from game_logic.minor_terrain_manager import MinorTerrainManager
from game_logic.promotion_manager import PromotionManager
from game_logic.turn_manager import TurnManager
from models.effect_state.effect_manager import EffectManager
from models.game_state.bua_manager import BUAManager
from models.game_state.dua_manager import DUAManager
from models.game_state.game_state_manager import GameStateManager
from models.game_state.reserves_manager import ReservesManager
from models.game_state.summoning_pool_manager import SummoningPoolManager
from models.sai_processor import SAIProcessor
from models.spell_targeting import SpellTargetingManager
from utils.field_access import strict_get_optional


class GameOrchestrator(QObject):
    """
    Game flow coordination and UI signal management for Dragon Dice.

    Handles game flow control, phase transitions, UI signal emission,
    and manager coordination without containing core game rules.
    """

    # =============================================================================
    # UI SIGNALS
    # =============================================================================

    game_state_updated = Signal()  # Emitted when significant game state changes
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)
    unit_selection_required = Signal(str, int, list)  # player_name, damage_amount, available_units
    damage_allocation_completed = Signal(str, int)  # player_name, total_damage_applied
    promotion_opportunities_available = Signal(dict)  # promotion_data with trigger, player, opportunities

    # Dragon Attack Phase signals
    dragon_attack_phase_started = Signal(str)  # marching_player
    dragon_attack_phase_completed = Signal(dict)  # phase_result

    # Flow control signals
    march_step_change_requested = Signal(str)  # new_march_step
    action_step_change_requested = Signal(str)  # new_action_step
    phase_advance_requested = Signal()
    phase_skip_requested = Signal()  # Skip to next phase group (e.g., skip Second March)
    player_advance_requested = Signal()
    effect_expiration_requested = Signal(str)  # player_name
    dice_roll_submitted = Signal(str, str, str)  # roll_type, results_string, player_name
    damage_allocation_requested = Signal(str, str, str, int)  # player_name, army_id, unit_name, new_health

    # Maneuver-related signals for Dragon Dice rules compliance
    counter_maneuver_requested = Signal(str, list)  # location, opposing_armies
    simultaneous_maneuver_rolls_requested = Signal(
        str, dict, list, dict
    )  # maneuvering_player, maneuvering_army, opposing_armies, counter_responses
    terrain_direction_choice_requested = Signal(str, int)  # location, current_face

    def __init__(
        self,
        player_setup_data,
        first_player_name,
        frontier_terrain,
        distance_rolls,
        parent=None,
    ):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        self.players_info = [{"name": p["name"], "home_terrain": p["home_terrain"]} for p in player_setup_data]
        self.player_names = [p["name"] for p in self.players_info]
        self.num_players = len(self.player_names)

        self.first_player_name = first_player_name
        self.frontier_terrain = frontier_terrain
        self.distance_rolls = distance_rolls

        # UI state cache to avoid direct manager access
        self._current_phase = ""
        self._current_march_step = ""
        self._current_action_step = ""
        self._current_player_name = first_player_name
        self._is_very_first_turn = True
        self._current_acting_army = None

        # Initialize all managers
        self._initialize_managers()

        # Create core engine with manager references
        self.core_engine = CoreEngine(self._get_managers_dict())

        # Set up signal connections
        self._setup_signal_connections()

        # Initialize phase controllers (after core engine is created)
        self._initialize_phase_controllers()

        # Initialize player data in managers
        self._initialize_player_data()

        # Initialize turn state
        self._initialize_turn_for_current_player()

        print(
            f"GameOrchestrator Initialized: First Player: {self.get_current_player_name()}, "
            f"Phase: {self.current_phase}, Step: {self.current_march_step}"
        )

    def _initialize_managers(self):
        """Initialize all manager components."""
        # Core managers
        self.turn_manager = TurnManager(self.player_names, self.first_player_name, parent=self)
        self.effect_manager = EffectManager(parent=self)
        self.game_state_manager = GameStateManager(
            self.player_setup_data, self.frontier_terrain, self.distance_rolls, parent=self
        )
        self.minor_terrain_manager = MinorTerrainManager(parent=self)

        # Create spell resolver
        from game_logic.spell_resolver import SpellResolver

        self.spell_resolver = SpellResolver(self.game_state_manager, self.effect_manager, parent=self)

        # Create action resolver with dependencies
        self.action_resolver = ActionResolver(
            self.game_state_manager, self.effect_manager, self.minor_terrain_manager, self.spell_resolver, parent=self
        )

        # Advanced managers
        self.dua_manager = DUAManager(turn_manager=self.turn_manager, parent=self)
        self.bua_manager = BUAManager(parent=self)
        self.summoning_pool_manager = SummoningPoolManager(parent=self)
        self.reserves_manager = ReservesManager(parent=self)
        self.sai_processor = SAIProcessor(dua_manager=self.dua_manager)

        # Dependent managers
        self.spell_targeting_manager = SpellTargetingManager(
            self.dua_manager, self.bua_manager, self.summoning_pool_manager
        )
        self.promotion_manager = PromotionManager(
            dua_manager=self.dua_manager, summoning_pool_manager=self.summoning_pool_manager, parent=self
        )
        self.dragon_attack_manager = DragonAttackManager(parent=self)
        self.eighth_face_manager = EighthFaceManager(
            self.game_state_manager, self.dua_manager, self.bua_manager, self.summoning_pool_manager, parent=self
        )

    def _initialize_phase_controllers(self):
        """Initialize the focused phase controllers."""
        from controllers.phase_controllers import TurnFlowController

        # Initialize the master turn flow controller
        # This will create and manage all individual phase controllers
        self.turn_flow_controller = TurnFlowController(self, parent=self)

        # Connect turn flow controller signals to orchestrator
        self.turn_flow_controller.turn_flow_status.connect(self._handle_turn_flow_status)
        self.turn_flow_controller.game_flow_error.connect(self._handle_game_flow_error)

        print("GameOrchestrator: Phase controllers initialized")

    def _get_managers_dict(self) -> Dict[str, Any]:
        """Get dictionary of all managers for core engine initialization."""
        return {
            "game_state_manager": self.game_state_manager,
            "bua_manager": self.bua_manager,
            "dua_manager": self.dua_manager,
            "reserves_manager": self.reserves_manager,
            "summoning_pool_manager": self.summoning_pool_manager,
            "effect_manager": self.effect_manager,
            "turn_manager": self.turn_manager,
            "action_resolver": self.action_resolver,
            "promotion_manager": self.promotion_manager,
            "eighth_face_manager": self.eighth_face_manager,
            "dragon_attack_manager": self.dragon_attack_manager,
            "minor_terrain_manager": self.minor_terrain_manager,
            "species_ability_manager": getattr(self, "species_ability_manager", None),
            "spell_resolver": self.spell_resolver,
        }

    def _setup_signal_connections(self):
        """Set up all signal connections between managers and orchestrator."""
        # Connect manager signals to orchestrator signals
        self.turn_manager.current_player_changed.connect(self._sync_player_state_from_turn_manager)
        self.turn_manager.current_phase_changed.connect(self._sync_phase_state_from_turn_manager)
        self.action_resolver.next_action_step_determined.connect(self._set_next_action_step)
        self.action_resolver.action_resolved.connect(self._handle_action_resolution)
        self.game_state_manager.game_state_changed.connect(self.game_state_updated.emit)

        # Connect orchestrator signals to manager methods
        self.march_step_change_requested.connect(self.turn_manager.set_march_step)
        self.action_step_change_requested.connect(self.turn_manager.set_action_step)
        self.phase_advance_requested.connect(self.turn_manager.advance_phase)
        self.phase_skip_requested.connect(self.turn_manager.skip_to_next_phase_group)
        self.player_advance_requested.connect(self.turn_manager.advance_player)
        self.effect_expiration_requested.connect(self.effect_manager.process_effect_expirations)
        self.effect_manager.effects_changed.connect(self.game_state_updated.emit)

        # Connect advanced manager signals
        self.dua_manager.dua_updated.connect(lambda: self.game_state_updated.emit())
        self.bua_manager.bua_updated.connect(lambda: self.game_state_updated.emit())
        self.bua_manager.minor_terrain_bua_updated.connect(lambda: self.game_state_updated.emit())
        self.summoning_pool_manager.pool_updated.connect(lambda: self.game_state_updated.emit())
        self.summoning_pool_manager.minor_terrain_pool_updated.connect(lambda: self.game_state_updated.emit())
        self.reserves_manager.reserves_updated.connect(lambda: self.game_state_updated.emit())
        self.minor_terrain_manager.placement_updated.connect(lambda: self.game_state_updated.emit())
        self.minor_terrain_manager.minor_terrain_buried.connect(lambda: self.game_state_updated.emit())

    def _initialize_player_data(self):
        """Initialize all players in advanced managers."""
        for player_name in self.player_names:
            self.dua_manager.initialize_player_dua(player_name)
            self.bua_manager.initialize_player_bua(player_name)
            self.summoning_pool_manager.initialize_player_pool(player_name, [])
            self.summoning_pool_manager.initialize_player_minor_terrain_pool(player_name)
            self.reserves_manager.initialize_player_reserves(player_name)

    # =============================================================================
    # GAME FLOW COORDINATION
    # =============================================================================

    def _initialize_turn_for_current_player(self):
        """Initialize turn for current player."""
        self.turn_manager.initialize_turn()

        # Sync cached state from turn manager
        self._current_phase = self.turn_manager.current_phase
        self._current_march_step = self.turn_manager.current_march_step
        self._current_action_step = self.turn_manager.current_action_step

        self._handle_phase_entry()
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def _handle_phase_entry(self):
        """Logic to execute when entering a new phase."""
        # If phase controllers are active, let them handle phase entry
        if hasattr(self, "turn_flow_controller"):
            print(f"GameOrchestrator: Phase entry delegated to TurnFlowController for {self._current_phase}")
            # Don't emit any automatic signals - let phase controllers handle it
            return

        # Legacy phase entry logic (when phase controllers are not available)
        current_phase = self._current_phase

        if current_phase == "FIRST_MARCH" or current_phase == "SECOND_MARCH":
            self.march_step_change_requested.emit("CHOOSE_ACTING_ARMY")
            self._current_march_step = "CHOOSE_ACTING_ARMY"
        elif current_phase == "EXPIRE_EFFECTS":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            self.effect_expiration_requested.emit(self.get_current_player_name())
            # Auto-advance after effect expiration
            self.phase_advance_requested.emit()
        elif current_phase == "SPECIES_ABILITIES":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            # Species abilities phase would be implemented here
            # For now, auto-advance
            self.phase_advance_requested.emit()
        elif current_phase == "DRAGON_ATTACKS":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            self._execute_dragon_attack_phase()
        elif current_phase == "EIGHTH_FACE":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            self.enter_eighth_face_phase()

    def advance_phase(self):
        """Advance to next phase with signal emission."""
        self.phase_advance_requested.emit()

    def skip_to_next_phase_group(self):
        """Skip to next phase group with signal emission."""
        self.phase_skip_requested.emit()

    def advance_player(self):
        """Advance to next player with signal emission."""
        self.player_advance_requested.emit()

    # =============================================================================
    # PHASE TRANSITION MANAGEMENT
    # =============================================================================

    def _sync_phase_state_from_turn_manager(self):
        """Sync phase state when TurnManager changes phases."""
        self._current_phase = self.turn_manager.current_phase
        self._current_march_step = self.turn_manager.current_march_step
        self._current_action_step = self.turn_manager.current_action_step

        print(f"GameOrchestrator: Phase synced to {self._current_phase}")
        self._handle_phase_entry()

    def _sync_player_state_from_turn_manager(self):
        """Sync player state when TurnManager changes players."""
        self._current_player_name = self.turn_manager.get_current_player()
        print(f"GameOrchestrator: Player synced to {self._current_player_name}")
        self.current_player_changed.emit(self._current_player_name)

    def _set_next_action_step(self, action_step: str):
        """Set next action step based on action resolver."""
        if action_step:
            self.action_step_change_requested.emit(action_step)
            self._current_action_step = action_step
            print(f"GameOrchestrator: Action step set to {action_step}")
        else:
            # Empty string means end current action and advance phase
            self._complete_current_action()

    def _complete_current_action(self):
        """Complete current action and advance phase."""
        print("GameOrchestrator: Action completed, advancing phase")
        self._current_action_step = ""
        self.action_step_change_requested.emit("")
        self.phase_advance_requested.emit()

    # =============================================================================
    # USER INPUT PROCESSING
    # =============================================================================

    @Slot(str, str)
    def decide_maneuver(self, maneuvering_player: str, maneuvering_army_id: str):
        """Process maneuver decision from user."""
        print(f"GameOrchestrator: Processing maneuver decision for {maneuvering_player}")

        # Get army location for maneuver
        army_location = self.game_state_manager.get_army_location_by_id(maneuvering_player, maneuvering_army_id)
        if not army_location:
            print(f"GameOrchestrator: Could not find location for army {maneuvering_army_id}")
            return

        # Check for opposing armies that might counter-maneuver
        opposing_armies = self._get_opposing_armies_at_location(army_location, maneuvering_player)

        if opposing_armies:
            # Request counter-maneuver decisions
            self.counter_maneuver_requested.emit(army_location, opposing_armies)
        else:
            # No opposition, proceed directly to maneuver roll
            self._proceed_to_maneuver_roll(maneuvering_player, maneuvering_army_id)

    @Slot(str, str)
    def submit_maneuver_input(self, maneuvering_player: str, maneuver_decision: str):
        """Process maneuver input submission."""
        print(f"GameOrchestrator: Maneuver input from {maneuvering_player}: {maneuver_decision}")

        # Parse maneuver decision and proceed accordingly
        if maneuver_decision == "advance":
            self._process_advance_maneuver(maneuvering_player)
        elif maneuver_decision == "retreat":
            self._process_retreat_maneuver(maneuvering_player)
        else:
            print(f"GameOrchestrator: Unknown maneuver decision: {maneuver_decision}")

    @Slot(str, str)
    def submit_counter_maneuver_decision(self, player_name: str, decision: str):
        """Process counter-maneuver decision from player."""
        print(f"GameOrchestrator: Counter-maneuver decision from {player_name}: {decision}")
        # Implementation would handle counter-maneuver logic

    @Slot(str, str)
    def submit_maneuver_roll_results(self, player_name: str, results_string: str):
        """Process maneuver roll results from player."""
        print(f"GameOrchestrator: Maneuver roll results from {player_name}: {results_string}")

        # Use action resolver to process maneuver results
        self.action_resolver.resolve_maneuver_action(player_name, results_string)

    @Slot(str, int)
    def submit_terrain_direction_choice(self, terrain_location: str, chosen_face: int):
        """Process terrain direction choice from player."""
        print(f"GameOrchestrator: Terrain direction choice for {terrain_location}: face {chosen_face}")

        # Apply terrain direction change through game state manager
        self.game_state_manager.set_terrain_face(terrain_location, chosen_face)
        self.game_state_updated.emit()

    @Slot(str)
    def select_action(self, action_type: str):
        """Process action selection from player."""
        print(f"GameOrchestrator: Action selected: {action_type}")

        self.get_current_player_name()

        # Set action step and wait for dice roll
        if action_type in ["melee", "missile", "magic", "maneuver"]:
            self.action_step_change_requested.emit(f"ROLL_{action_type.upper()}")
            self._current_action_step = f"ROLL_{action_type.upper()}"
        else:
            print(f"GameOrchestrator: Unknown action type: {action_type}")

    @Slot(str, str, str)
    def submit_attacker_melee_results(self, attacking_player: str, defending_player: str, results_string: str):
        """Process attacker melee results."""
        print(f"GameOrchestrator: Melee results from {attacking_player} vs {defending_player}: {results_string}")

        # Set combat context in action resolver
        current_location = self.game_state_manager.get_army_location(attacking_player)
        if current_location:
            attacking_army_id = self.game_state_manager.generate_army_identifier(attacking_player, "active")
            defending_army_id = self.game_state_manager.generate_army_identifier(defending_player, "active")
            self.action_resolver.set_combat_context(current_location, attacking_army_id, defending_army_id)

        # Process melee attack
        self.action_resolver.resolve_melee_attack(attacking_player, defending_player, results_string)

    @Slot(str, str)
    def submit_defender_save_results(self, defending_player: str, results_string: str):
        """Process defender save results."""
        print(f"GameOrchestrator: Save results from {defending_player}: {results_string}")

        # Process save response
        self.action_resolver.resolve_defender_save_response(defending_player, results_string)

    @Slot(str, str, dict)
    def submit_magic_results(self, casting_player: str, results_string: str, spell_data: dict):
        """Process magic results with spell casting."""
        print(f"GameOrchestrator: Magic results from {casting_player}: {results_string}")

        # Process magic action with optional spell casting
        self.action_resolver.resolve_magic_action(casting_player, results_string, spell_data)

    @Slot(str, str, str)
    def submit_attacker_missile_results(self, attacking_player: str, defending_player: str, results_string: str):
        """Process attacker missile results."""
        print(f"GameOrchestrator: Missile results from {attacking_player} vs {defending_player}: {results_string}")

        # Process missile attack
        self.action_resolver.resolve_missile_attack(attacking_player, defending_player, results_string)

    @Slot(str)
    def choose_acting_army(self, army_identifier: str):
        """Process acting army choice."""
        print(f"GameOrchestrator: Acting army chosen: {army_identifier}")

        self._current_acting_army = army_identifier

        # Advance to next march step
        self.march_step_change_requested.emit("SELECT_ACTION")
        self._current_march_step = "SELECT_ACTION"

    @Slot(str)
    def decide_action(self, action_decision: str):
        """Process action decision from player."""
        print(f"GameOrchestrator: Action decision: {action_decision}")

        if action_decision == "end_march":
            # End march phase
            self.phase_advance_requested.emit()
        else:
            # Select specific action
            self.select_action(action_decision)

    # =============================================================================
    # STATE CACHING & DISPLAY
    # =============================================================================

    @property
    def current_phase(self) -> str:
        """Get current phase (cached)."""
        return self._current_phase

    @property
    def current_march_step(self) -> str:
        """Get current march step (cached)."""
        return self._current_march_step

    @property
    def current_action_step(self) -> str:
        """Get current action step (cached)."""
        return self._current_action_step

    def get_current_phase_display(self) -> str:
        """Get formatted display string for current phase."""
        return self.turn_manager.get_phase_display_string()

    def get_current_phase(self) -> str:
        """Get current phase."""
        return self._current_phase

    def get_current_march_step(self) -> str:
        """Get current march step."""
        return self._current_march_step

    def get_current_action_step(self) -> str:
        """Get current action step."""
        return self._current_action_step

    def get_current_player_name(self) -> str:
        """Get current player name."""
        return self._current_player_name

    def get_available_acting_armies(self, player_name: str) -> List[Dict[str, Any]]:
        """Get armies available for acting."""
        return self.game_state_manager.get_player_armies_summary(player_name)

    def get_current_acting_army(self) -> Optional[str]:
        """Get current acting army identifier."""
        return self._current_acting_army

    def get_displayable_active_effects(self, player_name: str) -> List[Dict[str, Any]]:
        """Get active effects formatted for display."""
        effects = self.effect_manager.get_active_effects_for_player(player_name)

        displayable_effects = []
        for effect in effects:
            displayable_effects.append(
                {
                    "name": strict_get_optional(effect, "spell_name", "Unknown Effect"),
                    "type": strict_get_optional(effect, "type", "unknown"),
                    "target": strict_get_optional(effect, "target_identifier", ""),
                    "duration": strict_get_optional(effect, "duration", "unknown"),
                    "description": self._format_effect_description(effect),
                }
            )

        return displayable_effects

    def _format_effect_description(self, effect: Dict[str, Any]) -> str:
        """Format effect description for UI display."""
        effect_type = strict_get_optional(effect, "type", "unknown")
        spell_name = strict_get_optional(effect, "spell_name", "Unknown")

        if effect_type == "spell":
            return f"{spell_name} - Active until next turn"
        return f"{effect_type.title()} effect"

    # =============================================================================
    # DELEGATION TO CORE ENGINE
    # =============================================================================

    def get_all_player_summary_data(self) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.get_all_player_summary_data()

    def get_relevant_terrains_info(self, player_names: List[str]) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.get_relevant_terrains_info(player_names)

    def get_all_players_data(self) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.get_all_players_data()

    def get_all_terrain_data(self) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.get_all_terrain_data()

    def find_promotion_opportunities(self, player_name: str, trigger: str) -> Dict[str, Any]:
        """Delegate to core engine and emit signal."""
        opportunities = self.core_engine.find_promotion_opportunities(player_name, trigger)

        if opportunities.get("total_opportunities", 0) > 0:
            self.promotion_opportunities_available.emit(opportunities)

        return opportunities

    def execute_single_promotion(self, player_name: str, unit_id: str, target_health: int) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.execute_single_promotion(player_name, unit_id, target_health)

    def execute_mass_promotion(self, player_name: str, promotions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Delegate to core engine."""
        return self.core_engine.execute_mass_promotion(player_name, promotions)

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _get_opposing_armies_at_location(self, location: str, exclude_player: str) -> List[Dict[str, Any]]:
        """Get opposing armies at a location."""
        all_armies = self.game_state_manager.get_all_armies_at_location_all_players(location)
        opposing_armies = []

        for army_data in all_armies:
            army_player = strict_get_optional(army_data, "player_name", "")
            if army_player != exclude_player:
                opposing_armies.append(army_data)

        return opposing_armies

    def _proceed_to_maneuver_roll(self, player_name: str, army_id: str):
        """Proceed to maneuver roll without opposition."""
        print(f"GameOrchestrator: Proceeding to maneuver roll for {player_name}")
        self.action_step_change_requested.emit("ROLL_MANEUVER")
        self._current_action_step = "ROLL_MANEUVER"

    def _process_advance_maneuver(self, player_name: str):
        """Process advance maneuver."""
        print(f"GameOrchestrator: Processing advance maneuver for {player_name}")
        # Implementation would handle advance logic

    def _process_retreat_maneuver(self, player_name: str):
        """Process retreat maneuver."""
        print(f"GameOrchestrator: Processing retreat maneuver for {player_name}")
        # Implementation would handle retreat logic

    def _handle_action_resolution(self, action_result: Dict[str, Any]):
        """Handle action resolution from action resolver."""
        action_type = strict_get_optional(action_result, "type", "unknown")
        print(f"GameOrchestrator: Action resolved: {action_type}")

        # Check for promotion opportunities after combat actions
        if action_type in ["melee_complete", "missile_complete", "counter_attack_complete"]:
            damage_dealt = action_result.get("damage_dealt", 0)
            if damage_dealt > 0:
                current_player = self.get_current_player_name()
                self._check_promotion_after_combat(current_player, damage_dealt)

        # Emit game state update after action resolution
        self.game_state_updated.emit()

    def _check_promotion_after_combat(self, player_name: str, damage_dealt: int):
        """Check for promotion opportunities after combat."""
        trigger = f"combat_damage_{damage_dealt}"
        self.find_promotion_opportunities(player_name, trigger)

    def _execute_dragon_attack_phase(self):
        """Execute dragon attack phase."""
        current_player = self.get_current_player_name()
        print(f"GameOrchestrator: Executing dragon attack phase for {current_player}")

        self.dragon_attack_phase_started.emit(current_player)

        # Dragon attack phase logic would be implemented here
        # For now, auto-advance
        phase_result = {"player": current_player, "attacks_executed": 0}
        self.dragon_attack_phase_completed.emit(phase_result)
        self.phase_advance_requested.emit()

    def enter_eighth_face_phase(self):
        """Enter eighth face phase."""
        current_player = self.get_current_player_name()
        print(f"GameOrchestrator: Entering eighth face phase for {current_player}")

        # Get eighth face options and emit if choices available
        eighth_face_options = (
            self.core_engine.get_eighth_face_options() if hasattr(self.core_engine, "get_eighth_face_options") else []
        )

        if eighth_face_options:
            # Player has choices to make
            # This would emit signals for UI to show eighth face options
            pass
        else:
            # No eighth face actions, auto-advance
            self.phase_advance_requested.emit()

    # =============================================================================
    # TURN FLOW CONTROLLER SIGNAL HANDLERS
    # =============================================================================

    @Slot(str)
    def _handle_turn_flow_status(self, status_message: str):
        """Handle status updates from turn flow controller."""
        print(f"GameOrchestrator: Turn Flow Status - {status_message}")
        # Could emit to UI or log as needed

    @Slot(str, str)
    def _handle_game_flow_error(self, error_type: str, error_message: str):
        """Handle errors from turn flow controller."""
        print(f"GameOrchestrator: Game Flow Error [{error_type}] - {error_message}")
        # Could emit error signal to UI or handle error recovery


# Alias for backward compatibility during transition
GameEngine = GameOrchestrator
