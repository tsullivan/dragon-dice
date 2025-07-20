"""
Automatic Phase Controller for Dragon Dice

Handles phases that are often automatic but may require user choices:
- Expire Effects Phase (automatic)
- Eighth Face Phase (automatic effects OR player choices)
- Dragon Attack Phase (automatic if dragons present, skip if none)
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get_optional


class AutomaticPhaseController(QObject):
    """
    Controller for automatic phases that may require user interaction.

    Handles the pattern: Evaluate Conditions → Apply Automatic Effects OR Present Choices → Continue
    """

    # =============================================================================
    # SIGNALS
    # =============================================================================

    # Phase completion signals
    phase_completed = Signal(str)  # phase_name

    # Eighth face signals
    eighth_face_choices_available = Signal(str, list)  # player_name, choices
    eighth_face_automatic_effect = Signal(str, dict)  # player_name, effect_data

    # Dragon attack signals
    dragon_attacks_initiated = Signal(str, list)  # player_name, attack_data
    dragon_attacks_completed = Signal(str, dict)  # player_name, results

    # Effect expiration signals
    effects_expired = Signal(str, list)  # player_name, expired_effects

    # Status signals
    phase_status_update = Signal(str, str)  # phase_name, status_message
    phase_error = Signal(str, str)  # error_type, error_message

    def __init__(self, game_orchestrator, parent=None):
        super().__init__(parent)
        self.game_orchestrator = game_orchestrator
        self.core_engine = game_orchestrator.core_engine

        # Current phase state
        self.current_phase = ""
        self.current_player = ""
        self.phase_context = {}  # Store phase-specific state

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

        if phase in ["EXPIRE_EFFECTS", "EIGHTH_FACE", "DRAGON_ATTACKS"]:
            self._enter_automatic_phase(phase)
        elif self.current_phase:
            # Exiting our managed phase
            self._exit_automatic_phase()

    @Slot(str)
    def _handle_player_change(self, player_name: str):
        """Handle player changes from game orchestrator."""
        self.current_player = player_name

    def _enter_automatic_phase(self, phase_name: str):
        """Enter an automatic phase."""
        self.current_phase = phase_name
        self.current_player = self.game_orchestrator.get_current_player_name()
        self.phase_context.clear()

        print(f"AutomaticPhaseController: Entering {phase_name} for {self.current_player}")

        # Dispatch to appropriate phase handler
        if phase_name == "EXPIRE_EFFECTS":
            self._process_expire_effects_phase()
        elif phase_name == "EIGHTH_FACE":
            self._process_eighth_face_phase()
        elif phase_name == "DRAGON_ATTACKS":
            self._process_dragon_attack_phase()

    def _exit_automatic_phase(self):
        """Exit current automatic phase."""
        print(f"AutomaticPhaseController: Exiting {self.current_phase}")

        self.current_phase = ""
        self.phase_context.clear()

    # =============================================================================
    # EXPIRE EFFECTS PHASE
    # =============================================================================

    def _process_expire_effects_phase(self):
        """Process the Expire Effects phase."""
        print(f"AutomaticPhaseController: Processing effect expiration for {self.current_player}")

        # Get current active effects
        self.game_orchestrator.effect_manager.get_active_effects_for_player(self.current_player)

        # Process expiration through effect manager
        expired_effects = self.game_orchestrator.effect_manager.process_effect_expirations(self.current_player)

        if expired_effects:
            self.effects_expired.emit(self.current_player, expired_effects)
            self.phase_status_update.emit("EXPIRE_EFFECTS", f"Expired {len(expired_effects)} effects")
        else:
            self.phase_status_update.emit("EXPIRE_EFFECTS", "No effects to expire")

        # Phase completes automatically
        self.phase_completed.emit("EXPIRE_EFFECTS")

    # =============================================================================
    # EIGHTH FACE PHASE
    # =============================================================================

    def _process_eighth_face_phase(self):
        """Process the Eighth Face phase."""
        print(f"AutomaticPhaseController: Processing eighth face for {self.current_player}")

        # Get terrains controlled by player at 8th face
        eighth_face_terrains = self._get_eighth_face_terrains()

        if not eighth_face_terrains:
            # No eighth face terrains, skip phase
            self.phase_status_update.emit("EIGHTH_FACE", "No eighth face terrains controlled")
            self.phase_completed.emit("EIGHTH_FACE")
            return

        # Process each eighth face terrain
        choices_required = False
        for terrain_data in eighth_face_terrains:
            if self._process_eighth_face_terrain(terrain_data):
                choices_required = True

        if not choices_required:
            # All effects were automatic
            self.phase_completed.emit("EIGHTH_FACE")

    def _get_eighth_face_terrains(self) -> List[Dict[str, Any]]:
        """Get terrains controlled by current player at 8th face."""
        all_terrain_data = self.core_engine.get_all_terrain_data()
        eighth_face_terrains = []

        for terrain_name, terrain_data in all_terrain_data.items():
            current_face = strict_get_optional(terrain_data, "current_face", 1)
            controller = strict_get_optional(terrain_data, "controller", "")
            terrain_type = strict_get_optional(terrain_data, "terrain_type", "")

            if current_face == 8 and controller == self.current_player:
                # Check if this terrain type has eighth face effects
                if terrain_type in ["City", "Temple"]:
                    enhanced_terrain_data = terrain_data.copy()
                    enhanced_terrain_data["terrain_name"] = terrain_name
                    eighth_face_terrains.append(enhanced_terrain_data)

        return eighth_face_terrains

    def _process_eighth_face_terrain(self, terrain_data: Dict[str, Any]) -> bool:
        """Process eighth face effects for a terrain. Returns True if user choices required."""
        terrain_type = strict_get_optional(terrain_data, "terrain_type", "")
        terrain_name = strict_get_optional(terrain_data, "terrain_name", "")

        if terrain_type == "City":
            return self._process_city_eighth_face(terrain_name, terrain_data)
        if terrain_type == "Temple":
            return self._process_temple_eighth_face(terrain_name, terrain_data)
        # Other terrain types with eighth face effects would go here
        return False

    def _process_city_eighth_face(self, terrain_name: str, terrain_data: Dict[str, Any]) -> bool:
        """Process City eighth face effects. Returns True if choices required."""
        # City eighth face: Recruitment OR Promotion

        # Check what options are available
        can_recruit = self._can_recruit_from_dua()
        can_promote = self._can_promote_units()

        if not can_recruit and not can_promote:
            # No options available, automatic effect (none)
            self.eighth_face_automatic_effect.emit(
                self.current_player,
                {"terrain": terrain_name, "effect": "none", "reason": "No recruitment or promotion available"},
            )
            return False

        # Player has choices to make
        choices = []
        if can_recruit:
            choices.append({"type": "recruit", "description": "Recruit units from DUA", "terrain": terrain_name})
        if can_promote:
            choices.append({"type": "promote", "description": "Promote existing units", "terrain": terrain_name})

        # Always allow skipping the effect
        choices.append({"type": "skip", "description": "Skip eighth face effect", "terrain": terrain_name})

        self.eighth_face_choices_available.emit(self.current_player, choices)
        return True

    def _process_temple_eighth_face(self, terrain_name: str, terrain_data: Dict[str, Any]) -> bool:
        """Process Temple eighth face effects. Returns True if choices required."""
        # Temple eighth face: Immunity to Death Magic (automatic)

        effect_data = {
            "terrain": terrain_name,
            "effect": "death_magic_immunity",
            "description": "All units gain immunity to Death Magic this turn",
            "duration": "until_end_of_turn",
        }

        # Apply immunity effect through game orchestrator
        self.game_orchestrator.effect_manager.add_terrain_effect(self.current_player, effect_data)

        self.eighth_face_automatic_effect.emit(self.current_player, effect_data)
        return False  # No choices required

    def _can_recruit_from_dua(self) -> bool:
        """Check if player can recruit units from DUA."""
        dua_units = self.core_engine.get_player_dua_units(self.current_player)
        return len(dua_units) > 0

    def _can_promote_units(self) -> bool:
        """Check if player has units that can be promoted."""
        promotion_opportunities = self.core_engine.find_promotion_opportunities(self.current_player, "eighth_face")
        total_opps = promotion_opportunities.get("total_opportunities", 0)
        return bool(total_opps > 0)

    @Slot(str, dict)
    def handle_eighth_face_choice(self, player_name: str, choice_data: dict):
        """Handle eighth face choice from UI."""
        if player_name != self.current_player or self.current_phase != "EIGHTH_FACE":
            self.phase_error.emit("invalid_context", "Invalid eighth face choice context")
            return

        choice_type = strict_get_optional(choice_data, "type", "")
        terrain_name = strict_get_optional(choice_data, "terrain", "")

        print(f"AutomaticPhaseController: {player_name} chose {choice_type} for {terrain_name}")

        if choice_type == "recruit":
            self._execute_city_recruitment(terrain_name)
        elif choice_type == "promote":
            self._execute_city_promotion(terrain_name)
        elif choice_type == "skip":
            self.phase_status_update.emit("EIGHTH_FACE", f"Skipped eighth face effect at {terrain_name}")
        else:
            self.phase_error.emit("invalid_choice", f"Unknown eighth face choice: {choice_type}")
            return

        # Check if all eighth face terrains have been processed
        self._check_eighth_face_completion()

    def _execute_city_recruitment(self, terrain_name: str):
        """Execute city recruitment from DUA."""
        # This would delegate to the eighth face manager
        if hasattr(self.game_orchestrator, "eighth_face_manager"):
            result = self.game_orchestrator.eighth_face_manager.process_eighth_face_action(
                self.current_player, terrain_name, "recruitment"
            )
            self.phase_status_update.emit("EIGHTH_FACE", f"Recruitment at {terrain_name}: {result}")

    def _execute_city_promotion(self, terrain_name: str):
        """Execute city promotion."""
        # This would delegate to the eighth face manager
        if hasattr(self.game_orchestrator, "eighth_face_manager"):
            result = self.game_orchestrator.eighth_face_manager.process_eighth_face_action(
                self.current_player, terrain_name, "promotion"
            )
            self.phase_status_update.emit("EIGHTH_FACE", f"Promotion at {terrain_name}: {result}")

    def _check_eighth_face_completion(self):
        """Check if all eighth face processing is complete."""
        # For now, assume completion after handling one choice
        # In a full implementation, this would track multiple terrains
        self.phase_completed.emit("EIGHTH_FACE")

    # =============================================================================
    # DRAGON ATTACK PHASE
    # =============================================================================

    def _process_dragon_attack_phase(self):
        """Process the Dragon Attack phase."""
        print(f"AutomaticPhaseController: Processing dragon attacks for {self.current_player}")

        # Get terrains with dragons where player has armies
        dragon_attack_opportunities = self._get_dragon_attack_opportunities()

        if not dragon_attack_opportunities:
            # No dragon attacks possible, skip phase
            self.phase_status_update.emit("DRAGON_ATTACKS", "No dragon attacks to resolve")
            self.phase_completed.emit("DRAGON_ATTACKS")
            return

        # Execute dragon attacks
        self._execute_dragon_attacks(dragon_attack_opportunities)

    def _get_dragon_attack_opportunities(self) -> List[Dict[str, Any]]:
        """Get locations where dragons can attack player's armies."""
        player_army_locations = self._get_player_army_locations()
        dragon_attacks = []

        for location in player_army_locations:
            dragons_at_location = self._get_dragons_at_location(location)
            if dragons_at_location:
                dragon_attacks.append(
                    {
                        "location": location,
                        "dragons": dragons_at_location,
                        "target_armies": self._get_player_armies_at_location(location),
                    }
                )

        return dragon_attacks

    def _get_player_army_locations(self) -> List[str]:
        """Get all locations where current player has armies."""
        armies_summary = self.core_engine.get_player_armies_summary(self.current_player)
        locations = set()

        for army_data in armies_summary:
            location = strict_get_optional(army_data, "location", "")
            if location and location != "reserves":
                locations.add(location)

        return list(locations)

    def _get_dragons_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get dragons present at a location."""
        # This would query the summoning pool manager for dragons
        if hasattr(self.game_orchestrator, "summoning_pool_manager"):
            dragons = self.game_orchestrator.summoning_pool_manager.get_dragons_at_location(location)
            return list(dragons)  # Type cast to List[Dict[str, Any]]
        return []

    def _get_player_armies_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get current player's armies at a location."""
        all_armies = self.game_orchestrator.game_state_manager.get_all_armies_at_location(self.current_player, location)
        return list(all_armies)  # Type cast to List[Dict[str, Any]]

    def _execute_dragon_attacks(self, attack_opportunities: List[Dict[str, Any]]):
        """Execute dragon attacks."""
        self.dragon_attacks_initiated.emit(self.current_player, attack_opportunities)

        total_attacks = 0
        attack_results = {}

        for opportunity in attack_opportunities:
            location = opportunity["location"]

            if hasattr(self.game_orchestrator, "dragon_attack_manager"):
                # Execute attacks through dragon attack manager
                result = self.game_orchestrator.dragon_attack_manager.execute_dragon_attacks(
                    self.current_player, location, opportunity
                )
                attack_results[location] = result
                total_attacks += result.get("attacks_executed", 0)

        self.dragon_attacks_completed.emit(
            self.current_player, {"total_attacks": total_attacks, "location_results": attack_results}
        )

        self.phase_status_update.emit("DRAGON_ATTACKS", f"Executed {total_attacks} dragon attacks")
        self.phase_completed.emit("DRAGON_ATTACKS")

    # =============================================================================
    # PUBLIC INTERFACE
    # =============================================================================

    def get_current_phase_state(self) -> Dict[str, Any]:
        """Get current automatic phase state for UI display."""
        return {"phase": self.current_phase, "player": self.current_player, "context": self.phase_context}

    @Slot(str)
    def skip_current_phase(self):
        """Skip the current automatic phase."""
        if self.current_phase:
            print(f"AutomaticPhaseController: Skipping {self.current_phase}")
            self.phase_completed.emit(self.current_phase)
