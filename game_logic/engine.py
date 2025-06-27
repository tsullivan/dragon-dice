from PySide6.QtCore import QObject, Signal, Slot
import uuid  # For generating unique effect IDs
from typing import Optional  # Import Optional
import constants
from game_logic.turn_manager import TurnManager
from game_logic.action_resolver import ActionResolver
from game_logic.effect_manager import EffectManager
from game_logic.game_state_manager import GameStateManager


class GameEngine(QObject):
    """
    Manages the core game logic and state for the PySide6 version.
    """

    game_state_updated = Signal()  # Emitted when significant game state changes
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)
    unit_selection_required = Signal(
        str, int, list
    )  # player_name, damage_amount, available_units
    damage_allocation_completed = Signal(str, int)  # player_name, total_damage_applied

    # New signals to replace direct calls
    march_step_change_requested = Signal(str)  # new_march_step
    action_step_change_requested = Signal(str)  # new_action_step
    phase_advance_requested = Signal()
    player_advance_requested = Signal()
    effect_expiration_requested = Signal(str)  # player_name
    dice_roll_submitted = Signal(
        str, str, str
    )  # roll_type, results_string, player_name
    damage_allocation_requested = Signal(
        str, str, str, int
    )  # player_name, army_id, unit_name, new_health

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
        # Extract player names and create a simple list of player objects or dicts if needed
        self.players_info = [
            {"name": p["name"], "home_terrain": p["home_terrain"]}
            for p in player_setup_data
        ]
        self.player_names = [p["name"] for p in self.players_info]
        self.num_players = len(self.player_names)

        self.first_player_name = first_player_name
        self.frontier_terrain = frontier_terrain
        self.distance_rolls = distance_rolls  # List of (player_name, distance)

        # Initialize state cache to avoid direct manager access
        self._current_phase = ""
        self._current_march_step = ""
        self._current_action_step = ""
        self._current_player_name = first_player_name
        self._is_very_first_turn = (
            True  # Track if this is the very first turn of the game
        )
        self._current_acting_army = None  # Store the acting army for the current march

        # Instantiate managers
        self.turn_manager = TurnManager(
            self.player_names, self.first_player_name, parent=self
        )
        self.effect_manager = EffectManager(parent=self)
        self.game_state_manager = GameStateManager(
            player_setup_data, frontier_terrain, distance_rolls, parent=self
        )
        self.action_resolver = ActionResolver(
            self.game_state_manager, self.effect_manager, parent=self
        )

        # Connect signals from managers to GameEngine signals or slots
        self.turn_manager.current_player_changed.connect(
            self.current_player_changed.emit
        )
        self.turn_manager.current_phase_changed.connect(
            self.current_phase_changed.emit
        )  # Assuming TurnManager will emit display string
        self.action_resolver.next_action_step_determined.connect(
            self._set_next_action_step
        )  # Connect new signal
        self.action_resolver.action_resolved.connect(
            self._handle_action_resolution
        )  # Connect action resolution signal
        self.game_state_manager.game_state_changed.connect(
            self.game_state_updated.emit
        )  # If game state changes, emit general update

        # Connect new signals to manager methods
        self.march_step_change_requested.connect(self.turn_manager.set_march_step)
        self.action_step_change_requested.connect(self.turn_manager.set_action_step)
        self.phase_advance_requested.connect(self.turn_manager.advance_phase)
        self.player_advance_requested.connect(self.turn_manager.advance_player)
        self.effect_expiration_requested.connect(
            self.effect_manager.process_effect_expirations
        )
        self.effect_manager.effects_changed.connect(
            self.game_state_updated.emit
        )  # If effects change, game state is updated

        self._initialize_turn_for_current_player()

        print(
            f"GameEngine Initialized: First Player: {self.get_current_player_name()}, Phase: {self.current_phase}, Step: {self.current_march_step}"
        )

    def _initialize_turn_for_current_player(self):
        self.turn_manager.initialize_turn()

        # Sync cached state from turn manager
        self._current_phase = self.turn_manager.current_phase
        self._current_march_step = self.turn_manager.current_march_step
        self._current_action_step = self.turn_manager.current_action_step

        self._handle_phase_entry()
        # current_player_changed and current_phase_changed will be emitted by TurnManager or after _handle_phase_entry
        # self.current_player_changed.emit(self.get_current_player_name())
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def _handle_phase_entry(self):
        """Logic to execute when entering a new phase."""
        current_phase = self._current_phase

        if (
            current_phase == constants.PHASE_FIRST_MARCH
            or current_phase == constants.PHASE_SECOND_MARCH
        ):
            # Request march step initialization through signal - start with choosing acting army
            self.march_step_change_requested.emit(
                constants.MARCH_STEP_CHOOSE_ACTING_ARMY
            )
            self._current_march_step = constants.MARCH_STEP_CHOOSE_ACTING_ARMY
        elif current_phase == constants.PHASE_EXPIRE_EFFECTS:
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            # Request effect expiration processing through signal
            self.effect_expiration_requested.emit(self.get_current_player_name())
            self.phase_advance_requested.emit()
        elif current_phase == constants.PHASE_EIGHTH_FACE:
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
        elif current_phase == constants.PHASE_DRAGON_ATTACK:
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
        else:
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")

    # Properties using cached state instead of direct manager access
    @property
    def current_phase(self):
        return self._current_phase

    @property
    def current_march_step(self):
        return self._current_march_step

    @property
    def current_action_step(self):
        return self._current_action_step

    def advance_phase(self):
        """Request phase advancement through signal emission."""
        self.phase_advance_requested.emit()
        self._handle_phase_entry()
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def advance_player(self):
        """Request player advancement through signal emission."""
        self.player_advance_requested.emit()
        self._initialize_turn_for_current_player()

    def get_current_player_name(self):
        return self._current_player_name

    def get_current_phase_display(self):
        # Special handling for the very first turn
        if (
            self._current_phase == constants.PHASE_FIRST_MARCH
            and self._is_very_first_turn
            and self._current_march_step == constants.MARCH_STEP_DECIDE_MANEUVER
        ):
            return "🎮 Game Start: First March Phase"

        phase_display = self._current_phase.replace("_", " ").title()
        if self._current_march_step:
            phase_display += f" - {self._current_march_step.replace('_', ' ').title()}"
        if self._current_action_step:
            phase_display += f" - {self._current_action_step.replace('_', ' ').title()}"
        return phase_display

    def decide_maneuver(self, wants_to_maneuver: bool):
        """Process maneuver decision according to Dragon Dice rules."""
        print(
            f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}"
        )

        # Mark that the first turn interaction has begun
        if self._is_very_first_turn:
            self._is_very_first_turn = False

        if not wants_to_maneuver:
            # No maneuver - proceed to action selection
            self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
            self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()
            return

        # Player wants to maneuver - check for opposing armies per Dragon Dice rules
        acting_army = self.get_current_acting_army()
        if not acting_army:
            print("GameEngine: No acting army selected for maneuver")
            return

        location = acting_army.get("location")
        if not location:
            print("GameEngine: Acting army has no location")
            return

        # Find opposing armies at the same terrain
        opposing_armies = self.game_state_manager.find_defending_armies_at_location(
            self.get_current_player_name(), location
        )

        if not opposing_armies:
            # No opposition - maneuver automatically succeeds per Dragon Dice rules
            print("GameEngine: No opposing armies - maneuver automatically succeeds")
            self._execute_automatic_maneuver_success(location)
        else:
            # Opposition exists - initiate counter-maneuver process
            print(
                f"GameEngine: Found {len(opposing_armies)} opposing armies - requesting counter-maneuver decisions"
            )
            self._initiate_counter_maneuver_process(location, opposing_armies)

    def submit_maneuver_input(self, details: str):
        """DEPRECATED: Old maneuver system - use new Dragon Dice compliant flow instead."""
        print(
            f"WARNING: submit_maneuver_input is deprecated - maneuver should use Dragon Dice rules flow"
        )
        print(f"Details received: {details}")
        # For backward compatibility, just proceed to action selection
        self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
        self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def apply_maneuver_results(self, maneuver_result: dict):
        """Apply the results of a completed maneuver, including terrain face changes."""
        print(f"GameEngine: Applying maneuver results: {maneuver_result}")

        if not maneuver_result.get("success", False):
            print("GameEngine: Maneuver failed, no terrain changes to apply")
            return

        # Extract terrain change information
        location = maneuver_result.get("location")
        old_face = maneuver_result.get("old_face")
        new_face = maneuver_result.get("new_face")
        direction = maneuver_result.get("direction", "UP")
        maneuver_icons = maneuver_result.get("maneuver_icons", 0)

        if not location or new_face is None:
            print("GameEngine: Missing terrain change information in maneuver result")
            return

        # Apply terrain face change to game state
        success = self.game_state_manager.update_terrain_face(location, str(new_face))

        if success:
            print(
                f"GameEngine: Successfully updated terrain '{location}' from face {old_face} to face {new_face} (turned {direction})"
            )
            print(f"GameEngine: Maneuver achieved {maneuver_icons} maneuver icons")
            self.game_state_updated.emit()
        else:
            print(f"GameEngine: Failed to update terrain face for '{location}'")

        return success

    def _execute_automatic_maneuver_success(self, location: str):
        """Execute automatic maneuver success when no opposition exists (no dice rolled)."""
        try:
            # Get current terrain face and ask player for direction choice
            terrain_data = self.game_state_manager.get_terrain_data(location)
            if not terrain_data:
                print(f"GameEngine: Could not find terrain data for '{location}'")
                return

            current_face = terrain_data.get("face", 1)
            print(
                f"GameEngine: Automatic maneuver success - requesting direction choice for '{location}' (current face: {current_face})"
            )

            # Store the location for when direction is chosen
            self._pending_terrain_change = {
                "location": location,
                "current_face": current_face,
                "reason": "automatic_success",
            }

            # Request direction choice from UI
            self.terrain_direction_choice_requested.emit(location, current_face)

        except Exception as e:
            print(f"GameEngine: Error in automatic maneuver: {e}")

    def _initiate_counter_maneuver_process(self, location: str, opposing_armies: list):
        """Initiate the counter-maneuver process per Dragon Dice rules."""
        # Store maneuver context for the counter-maneuver process
        self._pending_maneuver = {
            "location": location,
            "opposing_armies": opposing_armies,
            "counter_maneuver_responses": {},
            "maneuvering_player": self.get_current_player_name(),
            "maneuvering_army": self.get_current_acting_army(),
        }

        # Emit signal to UI to handle counter-maneuver decisions
        # This will trigger the UI to ask each opposing player if they want to counter-maneuver
        self.counter_maneuver_requested.emit(location, opposing_armies)

    def submit_counter_maneuver_decision(self, player_name: str, will_counter: bool):
        """Record a player's decision about counter-maneuvering."""
        if not hasattr(self, "_pending_maneuver") or not self._pending_maneuver:
            print("GameEngine: No pending maneuver for counter-maneuver decision")
            return

        print(
            f"GameEngine: Player {player_name} counter-maneuver decision: {will_counter}"
        )
        self._pending_maneuver["counter_maneuver_responses"][player_name] = will_counter

        # Check if we have all responses
        opposing_players = {
            army["player"] for army in self._pending_maneuver["opposing_armies"]
        }
        responses = self._pending_maneuver["counter_maneuver_responses"]

        if set(responses.keys()) >= opposing_players:
            # All responses received - process maneuver
            self._process_maneuver_with_responses()

    def _process_maneuver_with_responses(self):
        """Process the maneuver after receiving all counter-maneuver responses."""
        if not hasattr(self, "_pending_maneuver") or not self._pending_maneuver:
            return

        responses = self._pending_maneuver["counter_maneuver_responses"]
        any_opposition = any(responses.values())

        if not any_opposition:
            # No one chose to counter-maneuver - automatic success
            print(
                "GameEngine: No players chose to counter-maneuver - automatic success"
            )
            location = self._pending_maneuver["location"]
            self._execute_automatic_maneuver_success(location)
            # Clear pending maneuver after automatic success
            self._pending_maneuver = None
        else:
            # At least one player chose to counter-maneuver - initiate simultaneous rolls
            print(
                "GameEngine: Counter-maneuver detected - initiating simultaneous rolls"
            )
            self._execute_simultaneous_maneuver_rolls()
            # DON'T clear pending maneuver yet - wait for roll results

    def _execute_simultaneous_maneuver_rolls(self):
        """Execute simultaneous maneuver rolls between maneuvering and counter-maneuvering armies."""
        if not hasattr(self, "_pending_maneuver") or not self._pending_maneuver:
            return

        # Emit signal to UI to handle simultaneous rolling
        # This will show a dialog where both players roll their armies simultaneously
        self.simultaneous_maneuver_rolls_requested.emit(
            self._pending_maneuver["maneuvering_player"],
            self._pending_maneuver["maneuvering_army"],
            self._pending_maneuver["opposing_armies"],
            self._pending_maneuver["counter_maneuver_responses"],
        )

    def submit_maneuver_roll_results(
        self, maneuvering_results: int, counter_results: int
    ):
        """Process the results of simultaneous maneuver rolls."""
        if not hasattr(self, "_pending_maneuver") or not self._pending_maneuver:
            print("GameEngine: ERROR - No pending maneuver for roll results")
            print(
                f"GameEngine: Has _pending_maneuver attr: {hasattr(self, '_pending_maneuver')}"
            )
            if hasattr(self, "_pending_maneuver"):
                print(f"GameEngine: _pending_maneuver value: {self._pending_maneuver}")
            return

        print(
            f"GameEngine: Processing maneuver roll results - Maneuvering: {maneuvering_results}, Counter: {counter_results}"
        )

        location = self._pending_maneuver["location"]

        if maneuvering_results >= counter_results:
            # Maneuver succeeds
            print(
                "GameEngine: Maneuver successful (maneuvering >= counter-maneuvering)"
            )
            self._execute_automatic_maneuver_success(location)
        else:
            # Maneuver fails
            print("GameEngine: Maneuver failed (maneuvering < counter-maneuvering)")
            # Proceed to action selection without terrain change
            self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
            self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()

        # Clear pending maneuver
        print("GameEngine: Clearing pending maneuver")
        self._pending_maneuver = None

    def submit_terrain_direction_choice(self, direction: str):
        """Process the player's terrain direction choice."""
        if (
            not hasattr(self, "_pending_terrain_change")
            or not self._pending_terrain_change
        ):
            print("GameEngine: No pending terrain change for direction choice")
            return

        location = self._pending_terrain_change["location"]
        current_face = self._pending_terrain_change["current_face"]

        print(f"GameEngine: Player chose to turn terrain {direction} at {location}")

        # Calculate new face based on direction
        if direction == "UP":
            new_face = min(current_face + 1, 8)  # Dragon Dice faces 1-8
        elif direction == "DOWN":
            new_face = max(current_face - 1, 1)  # Dragon Dice faces 1-8
        else:
            print(f"GameEngine: Invalid direction '{direction}', defaulting to UP")
            new_face = min(current_face + 1, 8)

        # Apply terrain change
        success = self.game_state_manager.update_terrain_face(location, str(new_face))

        if success:
            print(
                f"GameEngine: Successfully turned terrain '{location}' {direction} from face {current_face} to {new_face}"
            )
        else:
            print(f"GameEngine: Failed to apply terrain change to '{location}'")

        # Clear pending terrain change
        self._pending_terrain_change = None

        # Proceed to action selection after terrain change
        self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
        self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def select_action(self, action_type: str):
        """Request action selection processing. Manager will emit signals to update state."""
        print(f"Player {self.get_current_player_name()} selected action: {action_type}")
        # Handle action selection
        if action_type == constants.ACTION_SKIP:
            print("Player chose to skip action - advancing to next phase")
            # Skip action - advance to next phase
            self.advance_phase()
            return
        elif action_type == constants.ACTION_MELEE:
            action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL
        elif action_type == constants.ACTION_MISSILE:
            action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MISSILE_ROLL
        elif action_type == constants.ACTION_MAGIC:
            action_step = constants.ACTION_STEP_AWAITING_MAGIC_ROLL
        else:
            print(f"Unknown action type: {action_type}")
            return

        # Emit signal to TurnManager to handle action selection
        self.action_step_change_requested.emit(action_step)
        self._current_action_step = action_step

        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_attacker_melee_results(self, results: str):
        """Request processing of attacker's melee roll results."""
        if (
            self._current_action_step
            != constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL
        ):
            print("Error: Not expecting attacker melee results now.")
            return
        print(
            f"Player {self.get_current_player_name()} (Attacker) submitted melee results: {results}"
        )

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_results = self.action_resolver.parse_dice_string(
            results, roll_type="MELEE"
        )
        if not parsed_results:
            error_msg = (
                "Could not parse the dice roll results. Please check the format."
            )
            details = f"Input received: '{results}'\nExpected format: 'MM,S,SAI' or '2 melee, 1 save, 1 SAI'"
            print(
                f"GameEngine: Error: Could not parse attacker melee results via ActionResolver."
            )
            # In a real implementation, this would emit a signal to show user error
            # For now, continue with empty results to avoid blocking the game
            parsed_results = {"melee": 0, "saves": 0, "sais": []}
        print(f"GameEngine: Parsed attacker melee via ActionResolver: {parsed_results}")

        # Set combat context for proper army targeting
        attacking_location = (
            self._current_acting_army.get("location")
            if self._current_acting_army
            else None
        )
        attacking_army_id = (
            self._current_acting_army.get("unique_id")
            if self._current_acting_army
            else None
        )

        # Note: determine_primary_defending_army_id expects the defending player name,
        # but we want to find the defending player. Let's use the more general method.
        defending_armies = (
            self.game_state_manager.find_defending_armies_at_location(
                self.get_current_player_name(), attacking_location
            )
            if attacking_location
            else []
        )

        defending_army_id = None
        if defending_armies:
            # Use Dragon Dice priority: home > campaign > horde
            for priority_type in ["home", "campaign", "horde"]:
                for army_info in defending_armies:
                    if army_info["army_id"] == priority_type:
                        defending_army_id = (
                            self.game_state_manager.generate_army_identifier(
                                army_info["player"], priority_type
                            )
                        )
                        break
                if defending_army_id:
                    break

            # Fallback to first defending army
            if not defending_army_id and defending_armies:
                first_army = defending_armies[0]
                defending_army_id = self.game_state_manager.generate_army_identifier(
                    first_army["player"], first_army["army_id"]
                )

        self.action_resolver.set_combat_context(
            location=attacking_location,
            attacking_army_id=attacking_army_id,
            defending_army_id=defending_army_id,
        )

        attacker_outcome = self.action_resolver.process_attacker_melee_roll(
            attacking_player_name=self.get_current_player_name(),
            parsed_dice_results=parsed_results,
        )
        self.pending_attacker_outcome = attacker_outcome
        print(
            f"GameEngine: Attacker melee outcome from ActionResolver: {attacker_outcome}"
        )
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    # def _resolve_dice_roll(self, army_units: list, rolled_icons: list, roll_type: str, acting_player: str, opponent_player: str = None) -> dict:
    #     """Core dice roll resolution logic."""
    #     # Placeholder: Implement full dice resolution as per rules (pg 27).
    #     print(f"Resolving {roll_type} roll for {acting_player} with icons: {rolled_icons}")
    #     # This function would handle SAIs, ID icons, modifiers, etc.
    #     return {"melee_damage": 0, "missile_damage": 0, "saves": 0, "magic_points": 0, "sais_triggered": []}

    def submit_defender_save_results(self, results: str):
        """Request processing of defender's save roll results."""
        if self._current_action_step != constants.ACTION_STEP_AWAITING_DEFENDER_SAVES:
            print("Error: Not expecting defender save results now.")
            return
        print(
            f"Player {self.get_current_player_name()}'s Opponent (Defender) submitted save results: {results}"
        )

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_save_results = self.action_resolver.parse_dice_string(
            results, roll_type="SAVE"
        )
        if not parsed_save_results:
            print("Error: Could not parse defender save results.")
            return
        print(f"Parsed defender saves: {parsed_save_results}")

        if (
            not hasattr(self, "pending_attacker_outcome")
            or not self.pending_attacker_outcome
        ):
            print(
                "Error: No pending attacker outcome to resolve defender saves against."
            )
            return

        # Determine the defending player based on the attacking army's location
        attacking_location = (
            self._current_acting_army.get("location")
            if self._current_acting_army
            else None
        )
        defending_player_name = (
            self.game_state_manager.determine_primary_defending_player(
                self.get_current_player_name(), attacking_location
            )
            or "No_Defender_Found"
        )

        defender_outcome = self.action_resolver.process_defender_save_roll(
            defending_player_name=defending_player_name,
            parsed_save_dice=parsed_save_results,
            attacker_outcome=self.pending_attacker_outcome,
        )
        print(
            f"GameEngine: Defender save outcome from ActionResolver: {defender_outcome}"
        )
        del self.pending_attacker_outcome

        # Check if action is complete using cached state
        if not self._current_action_step:
            print(f"Melee action in {self.current_phase} complete.")
            self.advance_phase()
        else:
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()

    @Slot(str)
    def _set_next_action_step(self, next_step: str):
        """Slot to update the current action step via cached state."""
        print(f"GameEngine: Setting next action step to: {next_step}")
        self._current_action_step = next_step

    @Slot(dict)
    def _handle_action_resolution(self, action_result: dict):
        """Handle the resolution of actions from ActionResolver."""
        action_type = action_result.get("type", "unknown")
        print(f"GameEngine: Handling action resolution of type: {action_type}")

        if action_type == "melee_complete":
            damage_dealt = action_result.get("damage_dealt", 0)
            print(f"GameEngine: Melee action complete, {damage_dealt} damage dealt")

            # Check for counter-attack
            if action_result.get("counter_attack_possible", False):
                print("GameEngine: Counter-attack is possible")
                # TODO: Implement counter-attack logic

            self._complete_current_action()

        elif action_type == "missile_complete":
            damage_dealt = action_result.get("damage_dealt", 0)
            print(f"GameEngine: Missile action complete, {damage_dealt} damage dealt")
            self._complete_current_action()

        elif action_type == "magic_complete":
            effects = action_result.get("effects", [])
            print(f"GameEngine: Magic action complete, effects: {effects}")
            self._complete_current_action()

        elif action_type == "melee_attacker_complete":
            # Intermediate step - attacker finished, now defender needs to save
            hits = action_result.get("hits", 0)
            print(
                f"GameEngine: Attacker melee complete, {hits} hits scored, awaiting defender saves"
            )
            # Update action step is handled by ActionResolver via signal

        self.game_state_updated.emit()

    def _complete_current_action(self):
        """Complete the current action and advance phase."""
        self._current_action_step = ""
        print(f"GameEngine: Action complete in {self.current_phase}, advancing phase")
        self.advance_phase()

    def _resolve_spell_effect(
        self,
        spell_name: str,
        caster_player_name: str,
        target_identifier: str,
        target_type: str,
        affected_player_name: Optional[str] = None,
    ):
        """Placeholder for resolving spell effects and adding active effects."""
        print(
            f"Resolving spell: {spell_name} by {caster_player_name} on {target_identifier}"
        )
        if spell_name == "Blizzard":  # Example from rulebook (pg. 46)
            self.effect_manager.add_effect(
                description="Melee results -3 for armies at this terrain",
                source="Spell: Blizzard",
                target_type=constants.EFFECT_TARGET_TERRAIN,
                target_identifier=target_identifier,  # e.g., "Frontier Terrain"
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_CASTER,
                duration_value=1,  # Duration until caster's next turn
                caster_player_name=caster_player_name,
            )

    # def _apply_damage_to_army(self, army_identifier: str, damage_amount: int):
    #     """Placeholder to apply damage to units in an army."""
    #     print(f"Applying {damage_amount} damage to {army_identifier}")
    #     # TODO: Implement logic to select units, reduce health, move to DUA.
    #     self.game_state_updated.emit()

    def get_all_player_summary_data(self):
        """
        Returns a list of dictionaries, each summarizing a player's status.
        Example: [{'name': 'P1', 'captured_terrains': 0, 'terrains_to_win': 2,
                   'armies': [{'name': 'Home', 'points': 10, 'location': 'Highland'}, ...]}, ...]
        This method will now primarily query GameStateManager.
        """
        summaries = []
        terrains_to_win = 2  # Example, could be dynamic

        all_players_state = self.game_state_manager.get_all_players_data()
        for player_name, player_state in all_players_state.items():
            army_list = []
            for army_key, army_data in player_state.get("armies", {}).items():
                army_list.append(
                    {
                        "name": army_data.get("name", army_key.title()),
                        "points": army_data.get(
                            "points_value", 0
                        ),  # Ensure key matches GameStateManager
                        "location": army_data.get(
                            "location", constants.DEFAULT_UNKNOWN_VALUE
                        ),
                    }
                )

            summaries.append(
                {
                    "name": player_name,
                    "captured_terrains": player_state.get("captured_terrains_count", 0),
                    "terrains_to_win": terrains_to_win,  # This could also come from a game settings manager
                    "armies": army_list,
                }
            )
        return summaries

    def get_relevant_terrains_info(self):
        """
        Returns a list of dictionaries for relevant terrains for the current player.
        
        Returns:
            List of terrain dictionaries with keys:
            - 'name': terrain name
            - 'type': terrain type ('Frontier', 'Home', etc.)
            - 'face': current face number (1-8)
            - 'controller': controlling player name or None
            - 'icon': terrain emoji icon
            - 'details': formatted details string
            
        Example: [{'name': 'Coastland', 'type': 'Frontier', 'face': 5, 'controller': None, 'details': 'Face 5'}, ...]
        This method queries GameStateManager.
        """
        relevant_terrains_info = []
        all_terrains_state = self.game_state_manager.get_all_terrain_data()

        # For now, let's consider all terrains "relevant".
        # Later, this could be filtered based on current player's army locations or game rules.
        for terrain_name, terrain_data in all_terrains_state.items():
            controller = terrain_data.get("controller", "None")
            face_number = terrain_data.get("face", 1)
            details = f"Face {face_number}"
            icon = constants.TERRAIN_ICONS.get(
                terrain_name, "❓"
            )  # Get icon, default to question mark
            if controller and controller != "None":
                details += f", Controlled by: {controller}"

            relevant_terrains_info.append(
                {
                    "icon": icon,
                    "name": terrain_name,
                    "type": terrain_data.get("type", constants.DEFAULT_UNKNOWN_VALUE),
                    "face": face_number,  # Add face field for UI access
                    "controller": controller if controller != "None" else None,  # Add controller field for UI access
                    "details": details,
                }
            )
        return relevant_terrains_info

    def _resolve_sai_effect(
        self,
        sai_name: str,
        rolling_player_name: str,
        target_army_identifier: str,
        target_army_player_name: Optional[str],
    ):
        """Placeholder for resolving SAI effects and adding active effects."""
        print(
            f"Resolving SAI: {sai_name} by {rolling_player_name} on {target_army_identifier}"
        )
        if sai_name == "Frost Breath":  # Example from rulebook (pg. 36)
            self.effect_manager.add_effect(
                description="All results halved",
                source="SAI: Frost Breath",
                target_type=constants.EFFECT_TARGET_ARMY,
                target_identifier=target_army_identifier,  # e.g., "Player 2 Home Army"
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_CASTER,  # "your next turn" refers to the player whose unit rolled the SAI
                duration_value=1,
                caster_player_name=rolling_player_name,
                affected_player_name=target_army_player_name,
            )

    def _resolve_dragon_breath_effect(
        self,
        breath_type: str,
        attacking_dragon_controller: str,
        target_army_identifier: str,
        target_army_player_name: Optional[str],
    ):
        """Placeholder for resolving dragon breath effects and adding active effects."""
        print(f"Resolving Dragon Breath: {breath_type} on {target_army_identifier}")
        if breath_type == "Air":  # Example from rulebook (pg. 19)
            self.effect_manager.add_effect(
                description="Melee results halved",
                source="Dragon Breath: Air",
                target_type=constants.EFFECT_TARGET_ARMY,
                target_identifier=target_army_identifier,
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_TARGET,  # "its next turn" refers to the target army's player.
                duration_value=1,
                caster_player_name=attacking_dragon_controller,  # Player who controls the attacking dragon
                affected_player_name=target_army_player_name,
            )

    def get_displayable_active_effects(self) -> list[str]:
        """Returns a list of strings representing active effects for UI display."""
        return self.effect_manager.get_displayable_effects()

    def get_available_units_for_damage(
        self, player_name: str, army_identifier: str = None
    ) -> list:
        """Get units that can receive damage for a specific player/army."""
        if army_identifier:
            # Get units from specific army
            player_data = self.game_state_manager.get_player_data(player_name)
            if not player_data:
                return []

            army = player_data.get("armies", {}).get(army_identifier, {})
            units = army.get("units", [])
        else:
            # Get units from active army
            units = self.game_state_manager.get_active_army_units(player_name)

        # Filter to only units that can take damage (health > 0)
        available_units = [unit for unit in units if unit.get("health", 0) > 0]

        return available_units

    def request_unit_damage_allocation(
        self, player_name: str, damage_amount: int, army_identifier: str = None
    ):
        """Request that the player allocate damage to specific units."""
        available_units = self.get_available_units_for_damage(
            player_name, army_identifier
        )

        if not available_units:
            print(f"GameEngine: No units available to take damage for {player_name}")
            self.damage_allocation_completed.emit(player_name, 0)
            return

        if damage_amount <= 0:
            print(f"GameEngine: No damage to allocate for {player_name}")
            self.damage_allocation_completed.emit(player_name, 0)
            return

        print(
            f"GameEngine: Requesting damage allocation for {player_name}: {damage_amount} damage, {len(available_units)} units available"
        )

        # Emit signal for UI to handle unit selection
        self.unit_selection_required.emit(player_name, damage_amount, available_units)

    def allocate_damage_to_units(
        self, player_name: str, damage_allocations: dict, army_identifier: str = None
    ):
        """Apply damage allocation decisions to specific units."""
        """
        damage_allocations format: {
            "unit_name_1": damage_amount_1,
            "unit_name_2": damage_amount_2,
            ...
        }
        """
        total_damage_applied = 0
        army_id = army_identifier or "home"  # Default to home army

        print(
            f"GameEngine: Allocating damage to {player_name}'s units: {damage_allocations}"
        )

        for unit_name, damage_amount in damage_allocations.items():
            if damage_amount <= 0:
                continue

            # Get current unit health first
            current_health = self.game_state_manager.get_unit_health(
                player_name, army_id, unit_name
            )
            if current_health is None:
                print(
                    f"GameEngine: Could not find unit {unit_name} for damage allocation"
                )
                continue

            # Calculate new health after damage
            new_health = max(0, current_health - damage_amount)

            success = self.game_state_manager.update_unit_health(
                player_name, army_id, unit_name, new_health
            )

            if success:
                total_damage_applied += damage_amount
                print(f"GameEngine: Applied {damage_amount} damage to {unit_name}")
            else:
                print(f"GameEngine: Failed to apply damage to {unit_name}")

        print(f"GameEngine: Total damage applied: {total_damage_applied}")
        self.damage_allocation_completed.emit(player_name, total_damage_applied)
        self.game_state_updated.emit()

    def auto_allocate_damage(
        self, player_name: str, damage_amount: int, army_identifier: str = None
    ):
        """Automatically allocate damage to units (for AI or quick resolution)."""
        available_units = self.get_available_units_for_damage(
            player_name, army_identifier
        )

        if not available_units or damage_amount <= 0:
            self.damage_allocation_completed.emit(player_name, 0)
            return

        damage_allocations = {}
        remaining_damage = damage_amount

        # Simple allocation: damage units in order until damage is exhausted
        for unit in available_units:
            if remaining_damage <= 0:
                break

            unit_name = unit.get("name", "Unknown")
            unit_health = unit.get("health", 0)

            # Allocate damage up to unit's current health
            damage_to_allocate = min(remaining_damage, unit_health)
            damage_allocations[unit_name] = damage_to_allocate
            remaining_damage -= damage_to_allocate

        print(f"GameEngine: Auto-allocating damage: {damage_allocations}")
        self.allocate_damage_to_units(player_name, damage_allocations, army_identifier)

    def get_player_armies_summary(self, player_name: str) -> dict:
        """Get a summary of all armies for a specific player."""
        player_data = self.game_state_manager.get_player_data(player_name)
        if not player_data:
            return {}

        armies_summary = {}
        for army_key, army_data in player_data.get("armies", {}).items():
            units = army_data.get("units", [])
            total_health = sum(unit.get("health", 0) for unit in units)
            unit_count = len(units)

            armies_summary[army_key] = {
                "name": army_data.get("name", army_key.title()),
                "location": army_data.get("location", "Unknown"),
                "unit_count": unit_count,
                "total_health": total_health,
                "points_value": army_data.get("points_value", 0),
            }

        return armies_summary

    def get_all_players_data(self):
        """Get all players data from the GameStateManager."""
        return self.game_state_manager.get_all_players_data()

    def get_all_terrain_data(self):
        """Get all terrain data from the GameStateManager."""
        return self.game_state_manager.get_all_terrain_data()

    def extract_terrain_type_from_location(self, location: str) -> str:
        """Extract the base terrain type from a location name for UI display."""
        return self.game_state_manager.extract_terrain_type_from_location(location)

    def choose_acting_army(self, army_data: dict):
        """Set the acting army for the current march phase."""
        self._current_acting_army = army_data
        print(
            f"Acting army chosen: {army_data.get('name')} at {army_data.get('location')}"
        )

        # Mark that the first turn interaction has begun
        if self._is_very_first_turn:
            self._is_very_first_turn = False

        # Proceed to maneuver decision step
        self.march_step_change_requested.emit(constants.MARCH_STEP_DECIDE_MANEUVER)
        self._current_march_step = constants.MARCH_STEP_DECIDE_MANEUVER
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def get_current_acting_army(self):
        """Get the current acting army."""
        return self._current_acting_army

    def decide_action(self, wants_to_take_action: bool):
        """Handle the decision whether to take an action with the acting army."""
        print(
            f"Player {self.get_current_player_name()} decided action: {wants_to_take_action}"
        )

        if wants_to_take_action:
            self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
            self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        else:
            # Skip action step, advance to next phase
            self.advance_phase()
            return

        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()
