from typing import Any, Dict, List, Optional  # Import typing

from PySide6.QtCore import QObject, Signal, Slot

import constants
from game_logic.action_resolver import ActionResolver
from game_logic.bua_manager import BUAManager
from game_logic.dragon_attack_manager import DragonAttackManager
from game_logic.dua_manager import DUAManager, DUAUnit
from game_logic.effect_manager import EffectManager
from game_logic.game_state_manager import GameStateManager
from game_logic.promotion_manager import PromotionManager
from game_logic.reserves_manager import ReservesManager, ReserveUnit
from game_logic.sai_processor import SAIProcessor
from game_logic.spell_database import SpellDatabase
from game_logic.spell_targeting import SpellTargetingManager
from game_logic.summoning_pool_manager import SummoningPoolManager
from game_logic.turn_manager import TurnManager
from models.terrain_model import get_terrain_icon
from models.unit_model import UnitModel


class GameEngine(QObject):
    """
    Manages the core game logic and state for the PySide6 version.
    """

    game_state_updated = Signal()  # Emitted when significant game state changes
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)
    unit_selection_required = Signal(str, int, list)  # player_name, damage_amount, available_units
    damage_allocation_completed = Signal(str, int)  # player_name, total_damage_applied
    promotion_opportunities_available = Signal(dict)  # promotion_data with trigger, player, opportunities

    # Dragon Attack Phase signals
    dragon_attack_phase_started = Signal(str)  # marching_player
    dragon_attack_phase_completed = Signal(dict)  # phase_result

    # New signals to replace direct calls
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
        # Extract player names and create a simple list of player objects or dicts if needed
        self.players_info = [{"name": p["name"], "home_terrain": p["home_terrain"]} for p in player_setup_data]
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
        self._is_very_first_turn = True  # Track if this is the very first turn of the game
        self._current_acting_army = None  # Store the acting army for the current march

        # Instantiate managers
        self.turn_manager = TurnManager(self.player_names, self.first_player_name, parent=self)
        self.effect_manager = EffectManager(parent=self)
        self.game_state_manager = GameStateManager(player_setup_data, frontier_terrain, distance_rolls, parent=self)
        self.action_resolver = ActionResolver(self.game_state_manager, self.effect_manager, parent=self)

        # Advanced managers
        self.dua_manager = DUAManager(turn_manager=self.turn_manager, parent=self)
        self.bua_manager = BUAManager(parent=self)
        self.summoning_pool_manager = SummoningPoolManager(parent=self)
        self.reserves_manager = ReservesManager(parent=self)
        self.sai_processor = SAIProcessor(dua_manager=self.dua_manager)
        self.spell_database = SpellDatabase()

        # Spell targeting manager (depends on other managers)
        self.spell_targeting_manager = SpellTargetingManager(
            self.dua_manager, self.bua_manager, self.summoning_pool_manager
        )

        # Promotion manager (depends on DUA and Summoning Pool managers)
        self.promotion_manager = PromotionManager(
            dua_manager=self.dua_manager, summoning_pool_manager=self.summoning_pool_manager, parent=self
        )

        # Dragon Attack manager (depends on summoning pool manager)
        self.dragon_attack_manager = DragonAttackManager(parent=self)

        # Connect signals from managers to GameEngine signals or slots
        self.turn_manager.current_player_changed.connect(self._sync_player_state_from_turn_manager)
        self.turn_manager.current_phase_changed.connect(
            self._sync_phase_state_from_turn_manager
        )  # Sync cached state when TurnManager changes phases
        self.action_resolver.next_action_step_determined.connect(self._set_next_action_step)  # Connect new signal
        self.action_resolver.action_resolved.connect(self._handle_action_resolution)  # Connect action resolution signal
        self.game_state_manager.game_state_changed.connect(
            self.game_state_updated.emit
        )  # If game state changes, emit general update

        # Connect new signals to manager methods
        self.march_step_change_requested.connect(self.turn_manager.set_march_step)
        self.action_step_change_requested.connect(self.turn_manager.set_action_step)
        self.phase_advance_requested.connect(self.turn_manager.advance_phase)
        self.phase_skip_requested.connect(self.turn_manager.skip_to_next_phase_group)
        self.player_advance_requested.connect(self.turn_manager.advance_player)
        self.effect_expiration_requested.connect(self.effect_manager.process_effect_expirations)
        self.effect_manager.effects_changed.connect(
            self.game_state_updated.emit
        )  # If effects change, game state is updated

        # Connect advanced manager signals
        self.dua_manager.dua_updated.connect(lambda: self.game_state_updated.emit())
        self.bua_manager.bua_updated.connect(lambda: self.game_state_updated.emit())
        self.summoning_pool_manager.pool_updated.connect(lambda: self.game_state_updated.emit())
        self.reserves_manager.reserves_updated.connect(lambda: self.game_state_updated.emit())

        # Initialize all players in advanced managers
        for player_name in self.player_names:
            self.dua_manager.initialize_player_dua(player_name)
            self.bua_manager.initialize_player_bua(player_name)
            self.summoning_pool_manager.initialize_player_pool(player_name, [])
            self.reserves_manager.initialize_player_reserves(player_name)

        # Turn manager already has player names and current player set

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

        if current_phase == "FIRST_MARCH" or current_phase == "SECOND_MARCH":
            # Request march step initialization through signal - start with choosing acting army
            self.march_step_change_requested.emit("CHOOSE_ACTING_ARMY")
            self._current_march_step = "CHOOSE_ACTING_ARMY"
        elif current_phase == "EXPIRE_EFFECTS":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            # Request effect expiration processing through signal
            self.effect_expiration_requested.emit(self.get_current_player_name())
            self.phase_advance_requested.emit()
        elif current_phase == "EIGHTH_FACE":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            # Eighth Face phase is handled by UI dialogs
        elif current_phase == "DRAGON_ATTACK":
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            self._execute_dragon_attack_phase()
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

    def skip_to_next_phase_group(self):
        """Skip to next phase group (e.g., skip Second March)."""
        self.phase_skip_requested.emit()
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
            self._current_phase == "FIRST_MARCH"
            and self._is_very_first_turn
            and self._current_march_step == "DECIDE_MANEUVER"
        ):
            return "🎮 Game Start: First March Phase"

        phase_display = self._current_phase.replace("_", " ").title()
        if self._current_march_step:
            phase_display += f" - {self._current_march_step.replace('_', ' ').title()}"
        if self._current_action_step:
            phase_display += f" - {self._current_action_step.replace('_', ' ').title()}"
        return phase_display

    def get_current_phase(self):
        """Get the current phase."""
        return self._current_phase

    def get_current_march_step(self):
        """Get the current march step."""
        return self._current_march_step

    def get_current_action_step(self):
        """Get the current action step."""
        return self._current_action_step

    def get_available_acting_armies(self):
        """Get available armies that can act for the current player."""
        current_player = self.get_current_player_name()
        if not current_player:
            return []

        player_data = self.game_state_manager.get_player_data(current_player)
        if not player_data or "armies" not in player_data:
            return []

        available_armies = []
        for army_type, army_data in player_data["armies"].items():
            if army_data.get("units") and len(army_data["units"]) > 0:
                available_armies.append(
                    {
                        "name": army_data.get("name", f"{army_type.title()} Army"),
                        "army_type": army_type,
                        "location": army_data.get("location", "Unknown"),
                        "unique_id": army_data.get("unique_id"),
                        "units": army_data.get("units", []),
                    }
                )
        return available_armies

    def decide_maneuver(self, wants_to_maneuver: bool):
        """Process maneuver decision according to Dragon Dice rules."""
        print(f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}")

        # Mark that the first turn interaction has begun
        if self._is_very_first_turn:
            self._is_very_first_turn = False

        if not wants_to_maneuver:
            # No maneuver - proceed to action selection
            self.march_step_change_requested.emit("SELECT_ACTION")
            self._current_march_step = "SELECT_ACTION"
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
            print(f"GameEngine: Found {len(opposing_armies)} opposing armies - requesting counter-maneuver decisions")
            self._initiate_counter_maneuver_process(location, opposing_armies)

    def submit_maneuver_input(self, details: str):
        """DEPRECATED: Old maneuver system - use new Dragon Dice compliant flow instead."""
        print("WARNING: submit_maneuver_input is deprecated - maneuver should use Dragon Dice rules flow")
        print(f"Details received: {details}")
        # Proceed to action selection
        self.march_step_change_requested.emit("SELECT_ACTION")
        self._current_march_step = "SELECT_ACTION"
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def apply_maneuver_results(self, maneuver_result: dict):
        """Apply the results of a completed maneuver, including terrain face changes."""
        print(f"GameEngine: Applying maneuver results: {maneuver_result}")

        if not maneuver_result.get("success", False):
            print("GameEngine: Maneuver failed, no terrain changes to apply")
            return None

        # Extract terrain change information
        location = maneuver_result.get("location")
        old_face = maneuver_result.get("old_face")
        new_face = maneuver_result.get("new_face")
        direction = maneuver_result.get("direction", "UP")
        maneuver_icons = maneuver_result.get("maneuver_icons", 0)

        if not location or new_face is None:
            print("GameEngine: Missing terrain change information in maneuver result")
            return None

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

        print(f"GameEngine: Player {player_name} counter-maneuver decision: {will_counter}")
        self._pending_maneuver["counter_maneuver_responses"][player_name] = will_counter

        # Check if we have all responses
        opposing_players = {army["player"] for army in self._pending_maneuver["opposing_armies"]}
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
            print("GameEngine: No players chose to counter-maneuver - automatic success")
            location = self._pending_maneuver["location"]
            self._execute_automatic_maneuver_success(location)
            # Clear pending maneuver after automatic success
            self._pending_maneuver = None
        else:
            # At least one player chose to counter-maneuver - initiate simultaneous rolls
            print("GameEngine: Counter-maneuver detected - initiating simultaneous rolls")
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

    def submit_maneuver_roll_results(self, maneuvering_results: int, counter_results: int):
        """Process the results of simultaneous maneuver rolls."""
        if not hasattr(self, "_pending_maneuver") or not self._pending_maneuver:
            print("GameEngine: ERROR - No pending maneuver for roll results")
            print(f"GameEngine: Has _pending_maneuver attr: {hasattr(self, '_pending_maneuver')}")
            if hasattr(self, "_pending_maneuver"):
                print(f"GameEngine: _pending_maneuver value: {self._pending_maneuver}")
            return

        print(
            f"GameEngine: Processing maneuver roll results - Maneuvering: {maneuvering_results}, Counter: {counter_results}"
        )

        location = self._pending_maneuver["location"]

        if maneuvering_results >= counter_results:
            # Maneuver succeeds - maneuvering player wins ties per Dragon Dice rules
            print("GameEngine: Maneuver successful (maneuvering >= counter-maneuvering)")
            self._execute_automatic_maneuver_success(location)
        else:
            # Maneuver fails - counter-maneuver beats maneuvering
            print("GameEngine: Maneuver failed (maneuvering < counter-maneuvering)")
            # Proceed to action selection without terrain change
            self.march_step_change_requested.emit("SELECT_ACTION")
            self._current_march_step = "SELECT_ACTION"
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()

        # Clear pending maneuver
        print("GameEngine: Clearing pending maneuver")
        self._pending_maneuver = None

    def submit_terrain_direction_choice(self, direction: str):
        """Process the player's terrain direction choice."""
        if not hasattr(self, "_pending_terrain_change") or not self._pending_terrain_change:
            print("GameEngine: No pending terrain change for direction choice")
            return

        location = self._pending_terrain_change["location"]
        current_face = self._pending_terrain_change["current_face"]

        print(f"GameEngine: Player chose to turn terrain {direction} at {location}")

        # Calculate new face based on direction (Dragon Dice faces wrap 1-8)
        if direction == "UP":
            new_face = (current_face % 8) + 1  # Wrap from 8 to 1
        elif direction == "DOWN":
            new_face = ((current_face - 2 + 8) % 8) + 1  # Handle negative wraparound properly
        else:
            print(f"GameEngine: Invalid direction '{direction}', defaulting to UP")
            new_face = (current_face % 8) + 1

        print(f"GameEngine: Attempting to update terrain '{location}' from face {current_face} to {new_face}")

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
        self.march_step_change_requested.emit("SELECT_ACTION")
        self._current_march_step = "SELECT_ACTION"
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def select_action(self, action_type: str):
        """Request action selection processing. Manager will emit signals to update state."""
        print(f"Player {self.get_current_player_name()} selected action: {action_type}")
        # Handle action selection
        if action_type == "SKIP":
            print("Player chose to skip action - advancing to next phase")
            # Skip action - advance to next phase
            self.advance_phase()
            return
        if action_type == "MELEE":
            action_step = "AWAITING_ATTACKER_MELEE_ROLL"
        elif action_type == "MISSILE":
            action_step = "AWAITING_ATTACKER_MISSILE_ROLL"
        elif action_type == "MAGIC":
            action_step = "AWAITING_MAGIC_ROLL"
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
        if self._current_action_step != "AWAITING_ATTACKER_MELEE_ROLL":
            print("Error: Not expecting attacker melee results now.")
            return
        print(f"Player {self.get_current_player_name()} (Attacker) submitted melee results: {results}")

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_results = self.action_resolver.parse_dice_string(results, roll_type="MELEE")
        if not parsed_results:
            print("GameEngine: Error: Could not parse attacker melee results via ActionResolver.")
            # In a real implementation, this would emit a signal to show user error
            # For now, continue with empty results to avoid blocking the game
            parsed_results = {"melee": 0, "saves": 0, "sais": []}
        print(f"GameEngine: Parsed attacker melee via ActionResolver: {parsed_results}")

        # Set combat context for proper army targeting
        attacking_location = self._current_acting_army.get("location") if self._current_acting_army else None
        attacking_army_id = self._current_acting_army.get("unique_id") if self._current_acting_army else None

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
                        defending_army_id = self.game_state_manager.generate_army_identifier(
                            army_info["player"], priority_type
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
        print(f"GameEngine: Attacker melee outcome from ActionResolver: {attacker_outcome}")
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
        if self._current_action_step != "AWAITING_DEFENDER_SAVES":
            print("Error: Not expecting defender save results now.")
            return
        print(f"Player {self.get_current_player_name()}'s Opponent (Defender) submitted save results: {results}")

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_save_results = self.action_resolver.parse_dice_string(results, roll_type="SAVE")
        if not parsed_save_results:
            print("Error: Could not parse defender save results.")
            return
        print(f"Parsed defender saves: {parsed_save_results}")

        if not hasattr(self, "pending_attacker_outcome") or not self.pending_attacker_outcome:
            print("Error: No pending attacker outcome to resolve defender saves against.")
            return

        # Determine the defending player based on the attacking army's location
        attacking_location = self._current_acting_army.get("location") if self._current_acting_army else None
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
        print(f"GameEngine: Defender save outcome from ActionResolver: {defender_outcome}")
        del self.pending_attacker_outcome

        # Check if action is complete using cached state
        if not self._current_action_step:
            print(f"Melee action in {self.current_phase} complete.")
            self.advance_phase()
        else:
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()

    def submit_magic_results(self, results: str):
        """Request processing of magic roll results."""
        if self._current_action_step != "AWAITING_MAGIC_ROLL":
            print("Error: Not expecting magic results now.")
            return
        print(f"Player {self.get_current_player_name()} submitted magic results: {results}")

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_results = self.action_resolver.parse_dice_string(results, roll_type="MAGIC")
        if not parsed_results:
            print("GameEngine: Error: Could not parse magic results via ActionResolver.")
            # In a real implementation, this would emit a signal to show user error
            # For now, continue with empty results to avoid blocking the game
            parsed_results = {"magic": 0, "sais": []}

        # Process magic effects
        magic_outcome = self.action_resolver.resolve_magic(str(parsed_results))
        print(f"GameEngine: Parsed magic via ActionResolver: {parsed_results}")

        print(f"GameEngine: Magic outcome from ActionResolver: {magic_outcome}")

        # Clear action step to indicate completion
        self._current_action_step = ""
        print(f"Magic action in {self.current_phase} complete.")

        # Emit signals to update UI
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_attacker_missile_results(self, results: str):
        """Request processing of attacker's missile roll results."""
        if self._current_action_step != "AWAITING_ATTACKER_MISSILE_ROLL":
            print("Error: Not expecting attacker missile results now.")
            return
        print(f"Player {self.get_current_player_name()} (Attacker) submitted missile results: {results}")

        # TODO: Replace direct calls with signals to ActionResolver
        # For now, use direct calls until signal system is fully implemented
        parsed_results = self.action_resolver.parse_dice_string(results, roll_type="MISSILE")
        if not parsed_results:
            print("GameEngine: Error: Could not parse attacker missile results via ActionResolver.")
            # In a real implementation, this would emit a signal to show user error
            # For now, continue with empty results to avoid blocking the game
            parsed_results = {"missile": 0, "saves": 0, "sais": []}

        # Process missile attack
        missile_outcome = self.action_resolver.resolve_attacker_missile(str(parsed_results))
        print(f"GameEngine: Parsed attacker missile via ActionResolver: {parsed_results}")

        print(f"GameEngine: Missile outcome from ActionResolver: {missile_outcome}")

        # Clear action step to indicate completion
        self._current_action_step = ""
        print(f"Missile action in {self.current_phase} complete.")

        # Emit signals to update UI
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    @Slot(str)
    def _set_next_action_step(self, next_step: str):
        """Slot to update the current action step via cached state."""
        print(f"GameEngine: Setting next action step to: {next_step}")
        self._current_action_step = next_step

    @Slot()
    def _sync_phase_state_from_turn_manager(self):
        """Slot to sync cached phase state when TurnManager changes phases."""
        # Update cached state from TurnManager
        old_phase = self._current_phase
        old_action_step = self._current_action_step
        self._current_phase = self.turn_manager.get_current_phase()
        self._current_march_step = self.turn_manager.get_current_march_step()
        self._current_action_step = self.turn_manager.get_current_action_step()

        print(f"GameEngine: Synced phase state - {old_phase} → {self._current_phase}")
        print(f"GameEngine: Synced action step - {old_action_step} → {self._current_action_step}")

        # Re-emit the corrected phase display
        self.current_phase_changed.emit(self.get_current_phase_display())

    @Slot()
    def _sync_player_state_from_turn_manager(self):
        """Slot to sync cached player state when TurnManager advances players."""
        # Update cached state from TurnManager
        old_player = self._current_player_name
        self._current_player_name = self.turn_manager.get_current_player()

        print(f"GameEngine: Synced player state - {old_player} → {self._current_player_name}")

        # Re-emit the corrected player name
        self.current_player_changed.emit(self._current_player_name)

    @Slot(dict)
    def _handle_action_resolution(self, action_result: dict):
        """Handle the resolution of actions from ActionResolver."""
        action_type = action_result.get("type", "unknown")
        print(f"GameEngine: Handling action resolution of type: {action_type}")

        if action_type == "melee_complete":
            damage_dealt = action_result.get("damage_dealt", 0)
            action_result.get("units_killed", [])
            print(f"GameEngine: Melee action complete, {damage_dealt} damage dealt")

            # Check for promotion opportunities after successful melee combat
            if damage_dealt > 0:
                self._check_promotion_after_combat("melee", action_result)

            # Check for counter-attack
            if action_result.get("counter_attack_possible", False):
                print("GameEngine: Counter-attack is possible")
                # TODO: Implement counter-attack logic

            self._complete_current_action()

        elif action_type == "missile_complete":
            damage_dealt = action_result.get("damage_dealt", 0)
            action_result.get("units_killed", [])
            print(f"GameEngine: Missile action complete, {damage_dealt} damage dealt")

            # Check for promotion opportunities after successful missile combat
            if damage_dealt > 0:
                self._check_promotion_after_combat("missile", action_result)

            self._complete_current_action()

        elif action_type == "magic_complete":
            effects = action_result.get("effects", [])
            print(f"GameEngine: Magic action complete, effects: {effects}")
            self._complete_current_action()

        elif action_type == "melee_attacker_complete":
            # Intermediate step - attacker finished, now defender needs to save
            hits = action_result.get("hits", 0)
            print(f"GameEngine: Attacker melee complete, {hits} hits scored, awaiting defender saves")
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
        print(f"Resolving spell: {spell_name} by {caster_player_name} on {target_identifier}")
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
                # Calculate actual unit points instead of allocated points
                units = army_data.get("units", [])
                total_unit_points = sum(unit.get("max_health", 0) for unit in units)

                army_list.append(
                    {
                        "name": army_data.get("name", army_key.title()),
                        "army_type": army_key,  # Include army type (home, campaign, horde)
                        "points": total_unit_points,  # Show actual unit points, not allocated points
                        "location": army_data.get("location", constants.DEFAULT_UNKNOWN_VALUE),
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

            # Get face description from terrain model
            face_description = self._get_terrain_face_description(terrain_name, face_number)
            details = f"Face {face_number}: {face_description}" if face_description else f"Face {face_number}"

            try:
                icon = get_terrain_icon(terrain_name)
            except KeyError:
                icon = "❓"  # Default to question mark
            if controller and controller != "None":
                details += f", Controlled by: {controller}"

            relevant_terrains_info.append(
                {
                    "icon": icon,
                    "name": terrain_name,
                    "type": terrain_data.get("type", constants.DEFAULT_UNKNOWN_VALUE),
                    "face": face_number,  # Add face field for UI access
                    "controller": (controller if controller != "None" else None),  # Add controller field for UI access
                    "details": details,
                }
            )
        return relevant_terrains_info

    def _get_terrain_face_description(self, terrain_name: str, face_number: int) -> str:
        """Get the description for a specific face of a terrain die.

        Args:
            terrain_name: Name of the terrain (e.g., "Coastland Castle", "Player 1 Highland")
            face_number: Face number (1-8)

        Returns:
            Face description string, or empty string if not found
        """
        try:
            from models.terrain_model import TERRAIN_DATA

            # Convert terrain name to terrain key format if needed
            # Handle both "Coastland Castle" and "Player 1 Coastland Castle" formats
            clean_name = terrain_name
            if " " in terrain_name:
                parts = terrain_name.split()
                if len(parts) >= 3 and parts[0] == "Player":
                    # Extract base terrain from "Player 1 Coastland Castle"
                    clean_name = " ".join(parts[2:])

            # Convert to terrain key format (e.g., "Coastland Castle" -> "COASTLAND_CASTLE")
            terrain_key = clean_name.upper().replace(" ", "_")

            if terrain_key in TERRAIN_DATA:
                terrain = TERRAIN_DATA[terrain_key]
                if hasattr(terrain, "faces") and terrain.faces:
                    # Terrain faces are 1-indexed, list is 0-indexed
                    face_index = face_number - 1
                    if 0 <= face_index < len(terrain.faces):
                        face = terrain.faces[face_index]
                        return face.description if hasattr(face, "description") else face.name

        except Exception as e:
            print(f"Warning: Could not get face description for {terrain_name} face {face_number}: {e}")

        return ""

    def _resolve_sai_effect(
        self,
        sai_name: str,
        rolling_player_name: str,
        target_army_identifier: str,
        target_army_player_name: Optional[str],
    ):
        """Placeholder for resolving SAI effects and adding active effects."""
        print(f"Resolving SAI: {sai_name} by {rolling_player_name} on {target_army_identifier}")
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

    def get_displayable_active_effects(self) -> List[str]:
        """Returns a list of strings representing active effects for UI display."""
        return self.effect_manager.get_displayable_effects()

    def get_available_units_for_damage(
        self, player_name: str, army_identifier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
        self, player_name: str, damage_amount: int, army_identifier: Optional[str] = None
    ):
        """Request that the player allocate damage to specific units."""
        available_units = self.get_available_units_for_damage(player_name, army_identifier)

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
        self, player_name: str, damage_allocations: Dict[str, int], army_identifier: Optional[str] = None
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
        units_killed = []

        print(f"GameEngine: Allocating damage to {player_name}'s units: {damage_allocations}")

        for unit_name, damage_amount in damage_allocations.items():
            if damage_amount <= 0:
                continue

            # Get current unit health first
            current_health = self.game_state_manager.get_unit_health(player_name, army_id, unit_name)
            if current_health is None:
                print(f"GameEngine: Could not find unit {unit_name} for damage allocation")
                continue

            # Calculate new health after damage
            new_health = max(0, current_health - damage_amount)

            # Track if unit was killed
            if current_health > 0 and new_health == 0:
                units_killed.append(
                    {"name": unit_name, "player": player_name, "army": army_id, "pre_damage_health": current_health}
                )

            try:
                self.game_state_manager.update_unit_health(player_name, army_id, unit_name, new_health)
                total_damage_applied += damage_amount
                print(f"GameEngine: Applied {damage_amount} damage to {unit_name}")
            except Exception as e:
                print(f"GameEngine: Failed to apply damage to {unit_name}: {e}")

        # Check for promotion opportunities for attacking player after dealing damage
        if total_damage_applied > 0 and units_killed:
            self._check_promotion_after_unit_kills(units_killed)

        print(f"GameEngine: Total damage applied: {total_damage_applied}")
        self.damage_allocation_completed.emit(player_name, total_damage_applied)
        self.game_state_updated.emit()

    def auto_allocate_damage(self, player_name: str, damage_amount: int, army_identifier: Optional[str] = None):
        """Automatically allocate damage to units (for AI or quick resolution)."""
        available_units = self.get_available_units_for_damage(player_name, army_identifier)

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
        print(f"Acting army chosen: {army_data.get('name')} at {army_data.get('location')}")

        # Set the active army type in the game state manager
        current_player = self.get_current_player_name()
        army_type = army_data.get("army_type")
        if army_type:
            try:
                self.game_state_manager.set_active_army(current_player, army_type)
                print(f"Set active army type to '{army_type}' for {current_player}")
            except Exception as e:
                print(f"Failed to set active army type '{army_type}' for {current_player}: {e}")

        # Mark that the first turn interaction has begun
        if self._is_very_first_turn:
            self._is_very_first_turn = False

        # Proceed to maneuver decision step
        self.march_step_change_requested.emit("DECIDE_MANEUVER")
        self._current_march_step = "DECIDE_MANEUVER"
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def get_current_acting_army(self):
        """Get the current acting army."""
        return self._current_acting_army

    def decide_action(self, wants_to_take_action: bool):
        """Handle the decision whether to take an action with the acting army."""
        print(f"Player {self.get_current_player_name()} decided action: {wants_to_take_action}")

        if wants_to_take_action:
            self.march_step_change_requested.emit("SELECT_ACTION")
            self._current_march_step = "SELECT_ACTION"
        else:
            # Skip action step, advance to next phase
            self.advance_phase()
            return

        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    # Data conversion methods for advanced manager integration
    def dict_to_dua_unit(self, unit_dict: Dict[str, Any], death_info: Optional[Dict[str, Any]] = None) -> DUAUnit:
        """Convert dictionary unit data to DUAUnit object."""
        death_info = death_info or {}
        return DUAUnit(
            name=unit_dict.get("name", "Unknown Unit"),
            species=unit_dict.get("species", "Unknown"),
            health=unit_dict.get("health", 1),
            elements=unit_dict.get("elements", []),
            original_owner=unit_dict.get("owner", "Unknown"),
            death_cause=death_info.get("cause", "combat"),
            death_location=death_info.get("location", ""),
            death_turn=death_info.get("turn", self.turn_manager.current_turn),
        )

    def dict_to_reserve_unit(
        self, unit_dict: Dict[str, Any], entry_info: Optional[Dict[str, Any]] = None
    ) -> ReserveUnit:
        """Convert dictionary unit data to ReserveUnit object."""
        entry_info = entry_info or {}
        return ReserveUnit(
            name=unit_dict.get("name", "Unknown Unit"),
            species=unit_dict.get("species", "Unknown"),
            health=unit_dict.get("health", 1),
            elements=unit_dict.get("elements", []),
            owner=unit_dict.get("owner", "Unknown"),
            original_terrain=entry_info.get("terrain", ""),
            turn_entered=entry_info.get("turn", self.turn_manager.current_turn),
            entry_reason=entry_info.get("reason", "retreat"),
        )

    def dua_unit_to_dict(self, dua_unit: DUAUnit) -> Dict[str, Any]:
        """Convert DUAUnit object back to dictionary format."""
        return {
            "name": dua_unit.name,
            "species": dua_unit.species,
            "health": dua_unit.health,
            "elements": dua_unit.elements,
            "owner": dua_unit.original_owner,
        }

    def reserve_unit_to_dict(self, reserve_unit: ReserveUnit) -> Dict[str, Any]:
        """Convert ReserveUnit object back to dictionary format."""
        return {
            "name": reserve_unit.name,
            "species": reserve_unit.species,
            "health": reserve_unit.health,
            "elements": reserve_unit.elements,
            "owner": reserve_unit.owner,
        }

    def get_units_as_dua_objects(self, player_name: str, army_id: str) -> List[DUAUnit]:
        """Get army units as DUA objects for advanced manager integration."""
        units_dict = self.game_state_manager.get_army_units(player_name, army_id)
        return [self.dict_to_dua_unit(unit) for unit in units_dict]

    def get_units_as_reserve_objects(self, player_name: str, army_id: str) -> List[ReserveUnit]:
        """Get army units as Reserve objects for advanced manager integration."""
        units_dict = self.game_state_manager.get_army_units(player_name, army_id)
        return [self.dict_to_reserve_unit(unit) for unit in units_dict]

    # Advanced manager access methods
    def add_unit_to_dua(self, unit_dict: Dict[str, Any], death_info: Optional[Dict[str, Any]] = None):
        """Add a unit to the DUA when it dies."""
        dua_unit = self.dict_to_dua_unit(unit_dict, death_info)
        self.dua_manager.add_unit_to_dua(dua_unit)

    def add_unit_to_reserves(self, unit_dict: Dict[str, Any], entry_info: Optional[Dict[str, Any]] = None):
        """Add a unit to reserves."""
        entry_info = entry_info or {}
        self.reserves_manager.add_unit_to_reserves(
            unit_dict,
            unit_dict.get("owner", "Unknown"),
            entry_info.get("terrain", ""),
            entry_info.get("reason", "retreat"),
        )

    def bury_unit_in_bua(self, player_name: str, unit_dict: Dict[str, Any]):
        """Bury a unit in the BUA."""
        # Convert dict to UnitModel for BUA manager

        unit_model = UnitModel(
            unit_id=unit_dict.get("id", unit_dict.get("name", "unknown")),
            name=unit_dict.get("name", "Unknown Unit"),
            unit_type=unit_dict.get("type", "standard"),
            health=unit_dict.get("health", 1),
            max_health=unit_dict.get("max_health", unit_dict.get("health", 1)),
            species=None,  # Would need to resolve from species name
            faces=[],  # Would need to resolve from unit type
        )
        self.bua_manager.bury_unit(player_name, unit_model)

    def get_player_dua_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get DUA units for a player as dictionaries."""
        dua_units = self.dua_manager.get_player_dua(player_name)
        return [self.dua_unit_to_dict(unit) for unit in dua_units]

    def get_player_reserve_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get reserve units for a player as dictionaries."""
        reserve_units = self.reserves_manager.get_player_reserves(player_name)
        return [self.reserve_unit_to_dict(unit) for unit in reserve_units]

    def is_terrain_eighth_face_controlled(self, location: str, player_name: str) -> bool:
        """Check if a player controls the eighth face of a terrain."""
        # This is a stub implementation - would need actual game logic
        # to check terrain face control
        return False

    def get_player_bua_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get BUA units for a player as dictionaries."""
        bua_units = self.bua_manager.get_player_bua(player_name)
        return [unit.to_dict() for unit in bua_units]

    def process_spell_effects(self, spell_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process the effects of cast spells."""
        results = {"spells_processed": [], "effects_applied": [], "errors": []}

        cast_spells = spell_results.get("cast_spells", [])
        for spell_data in cast_spells:
            try:
                spell_result = self._process_single_spell(spell_data)
                results["spells_processed"].append(spell_result)
                if spell_result.get("effects"):
                    results["effects_applied"].extend(spell_result["effects"])
            except Exception as e:
                error_msg = f"Error processing spell {spell_data.get('name', 'Unknown')}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"Spell processing error: {error_msg}")

        return results

    def _process_single_spell(self, spell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single spell's effects."""
        from models.spell_model import get_spell

        spell_name = spell_data.get("name", "")
        spell_model = get_spell(spell_name)

        if not spell_model:
            raise ValueError(f"Unknown spell: {spell_name}")

        result = {"spell_name": spell_name, "success": False, "effects": [], "message": ""}

        # Handle dragon summoning spells
        if spell_name.upper() in ["SUMMON_DRAGON", "SUMMON_WHITE_DRAGON"]:
            summon_result = self._process_dragon_summon_spell(spell_data, spell_model)
            result.update(summon_result)
        elif spell_name.upper() == "SUMMON_DRAGONKIN":
            summon_result = self._process_dragonkin_summon_spell(spell_data, spell_model)
            result.update(summon_result)
        else:
            # For now, other spells are not implemented
            result["message"] = f"{spell_name} effect not yet implemented"
            result["success"] = True  # Consider it successful but without effects

        return result

    def _process_dragon_summon_spell(self, spell_data: Dict[str, Any], spell_model) -> Dict[str, Any]:
        """Process Summon Dragon or Summon White Dragon spells."""
        caster_player = spell_data.get("caster", "")
        target_terrain = spell_data.get("target_terrain", "")
        element_used = spell_data.get("element_used", "")

        if not all([caster_player, target_terrain, element_used]):
            raise ValueError("Missing required data for dragon summoning")

        # Find available dragons
        available_dragons = []

        if spell_model.name == "Summon White Dragon":
            # White dragons can only be summoned from pools
            white_dragons = self.summoning_pool_manager.get_dragons_by_type(caster_player, "WHITE")
            available_dragons = white_dragons
        else:
            # Regular dragon summoning
            if element_used.upper() in ["IVORY", "ANY"]:
                # Ivory or Ivory Hybrid dragons from pools
                ivory_dragons = self.summoning_pool_manager.get_dragons_by_type(caster_player, "IVORY")
                ivory_hybrid_dragons = self.summoning_pool_manager.get_dragons_by_type(caster_player, "IVORY_HYBRID")
                available_dragons = ivory_dragons + ivory_hybrid_dragons
            else:
                # Elemental dragons from pools or terrains
                pool_dragons = self.summoning_pool_manager.get_dragons_by_element(caster_player, element_used)
                # TODO: Add logic to get dragons from terrains as well
                available_dragons = pool_dragons

        if not available_dragons:
            return {
                "success": False,
                "message": f"No suitable dragons available for summoning with {element_used} magic",
                "effects": [],
            }

        # For now, summon the first available dragon
        # In a full implementation, this would show a selection dialog
        dragon_to_summon = available_dragons[0]

        # Remove dragon from pool
        summoned_dragon = self.summoning_pool_manager.remove_dragon_from_pool(caster_player, dragon_to_summon.get_id())

        if summoned_dragon:
            # Add dragon to target terrain (this would need terrain army management)
            # For now, we'll just track that the summoning happened
            effect_msg = f"{summoned_dragon.get_display_name()} summoned to {target_terrain}"

            return {
                "success": True,
                "message": f"Successfully summoned {summoned_dragon.get_display_name()}",
                "effects": [effect_msg],
                "summoned_dragon": summoned_dragon.to_dict(),
                "target_terrain": target_terrain,
            }
        return {"success": False, "message": "Failed to remove dragon from summoning pool", "effects": []}

    def _process_dragonkin_summon_spell(self, spell_data: Dict[str, Any], spell_model) -> Dict[str, Any]:
        """Process Summon Dragonkin spell."""
        caster_player = spell_data.get("caster", "")
        element_used = spell_data.get("element_used", "")

        # Find dragonkin in summoning pool
        dragonkin = self.summoning_pool_manager.get_dragonkin_by_element(caster_player, element_used)

        if not dragonkin:
            return {
                "success": False,
                "message": f"No {element_used} Dragonkin available in summoning pool",
                "effects": [],
            }

        # For simplicity, summon one health worth (first available)
        unit_to_summon = dragonkin[0]

        # This would need to integrate with army management
        return {
            "success": True,
            "message": f"Summoned {unit_to_summon.name} to casting army",
            "effects": [f"Added {unit_to_summon.name} to army"],
            "summoned_unit": unit_to_summon.to_dict(),
        }

    def find_promotion_opportunities(self, player_name: str, army_type: str = None) -> Dict[str, Any]:
        """Find all promotion opportunities for a player's armies."""
        promotion_data = {"player": player_name, "opportunities": [], "total_count": 0}

        # Get armies to check
        armies_to_check = []
        if army_type:
            army_data = self.game_state_manager.get_army_data(player_name, army_type)
            if army_data:
                armies_to_check.append({"type": army_type, "data": army_data})
        else:
            # Check all armies
            for army_type in ["home", "campaign", "horde"]:
                army_data = self.game_state_manager.get_army_data(player_name, army_type)
                if army_data and army_data.get("units"):
                    armies_to_check.append({"type": army_type, "data": army_data})

        # Find promotion options for each army
        for army_info in armies_to_check:
            army_units = army_info["data"].get("units", [])
            if army_units:
                options = self.promotion_manager.find_promotion_options(army_units, player_name)
                if options:
                    promotion_data["opportunities"].append(
                        {
                            "army_type": army_info["type"],
                            "army_name": army_info["data"].get("name", f"{army_info['type']} Army"),
                            "options": [self._promotion_option_to_dict(option) for option in options],
                        }
                    )
                    promotion_data["total_count"] += len(options)

        return promotion_data

    def _promotion_option_to_dict(self, option) -> Dict[str, Any]:
        """Convert a PromotionOption to a dictionary for serialization."""
        return {
            "source_unit": option.source_unit,
            "target_unit": option.target_unit,
            "health_increase": option.health_increase,
            "source_location": option.source_location,
            "promotion_type": "single_unit",
        }

    def execute_single_promotion(
        self, player_name: str, army_type: str, unit_id: str, target_unit_id: str, source_location: str
    ) -> Dict[str, Any]:
        """Execute a single unit promotion."""
        try:
            # Get the army data
            army_data = self.game_state_manager.get_army_data(player_name, army_type)
            if not army_data:
                return {"success": False, "message": f"Army {army_type} not found for {player_name}"}

            # Find the source unit in the army
            army_units = army_data.get("units", [])
            source_unit = None
            for unit in army_units:
                if unit.get("unit_id") == unit_id:
                    source_unit = unit
                    break

            if not source_unit:
                return {"success": False, "message": f"Unit {unit_id} not found in {army_type} army"}

            # Find the target unit in DUA or Summoning Pool
            target_unit = None
            if source_location == "DUA":
                dua_units = self.dua_manager.get_player_dua(player_name)
                for dua_unit in dua_units:
                    if dua_unit.unit_data.get("unit_id") == target_unit_id:
                        target_unit = dua_unit.unit_data
                        break
            elif source_location == "SUMMONING_POOL":
                # For now, not implemented
                return {"success": False, "message": "Summoning Pool promotion not yet implemented"}

            if not target_unit:
                return {"success": False, "message": f"Target unit {target_unit_id} not found in {source_location}"}

            # Create promotion option and execute
            from game_logic.promotion_manager import PromotionOption

            promotion_option = PromotionOption(
                source_unit=source_unit, target_unit=target_unit, health_increase=1, source_location=source_location
            )

            result = self.promotion_manager.execute_promotion(promotion_option, player_name)

            if result.success:
                # Update the game state (this is a simplified version)
                # In a full implementation, this would update the actual army data
                print(f"Promotion successful: {result.message}")
                self.game_state_updated.emit()

            return {
                "success": result.success,
                "message": result.message,
                "promoted_units": result.promoted_units,
                "errors": result.errors,
            }

        except Exception as e:
            return {"success": False, "message": f"Promotion failed: {str(e)}"}

    def execute_mass_promotion(
        self, player_name: str, army_type: str, promotion_type: str = "as_many_as_possible"
    ) -> Dict[str, Any]:
        """Execute mass promotion for an army (e.g., after killing a dragon)."""
        try:
            # Get the army data
            army_data = self.game_state_manager.get_army_data(player_name, army_type)
            if not army_data:
                return {"success": False, "message": f"Army {army_type} not found for {player_name}"}

            army_units = army_data.get("units", [])
            if not army_units:
                return {"success": False, "message": f"No units in {army_type} army to promote"}

            result = self.promotion_manager.execute_mass_promotion(army_units, player_name, promotion_type)

            if result.success:
                print(f"Mass promotion completed: {result.message}")
                self.game_state_updated.emit()

            return {
                "success": result.success,
                "message": result.message,
                "promoted_count": len(result.promoted_units),
                "promoted_units": result.promoted_units,
                "errors": result.errors,
            }

        except Exception as e:
            return {"success": False, "message": f"Mass promotion failed: {str(e)}"}

    def check_promotion_after_dragon_kill(
        self, victorious_army_data: Dict[str, Any], player_name: str
    ) -> Dict[str, Any]:
        """Check and potentially execute promotions after killing a dragon."""
        army_units = victorious_army_data.get("units", [])
        if not army_units:
            return {"success": False, "message": "No units in army to promote"}

        # Find promotion opportunities
        opportunities = self.promotion_manager.find_promotion_options(army_units, player_name)

        if not opportunities:
            return {
                "success": True,
                "message": "No promotion opportunities available",
                "promotions_available": False,
                "opportunities": [],
            }

        return {
            "success": True,
            "message": f"Found {len(opportunities)} promotion opportunities after dragon kill",
            "promotions_available": True,
            "opportunities": [self._promotion_option_to_dict(option) for option in opportunities],
            "auto_promote": True,  # Dragon kills allow "as many as possible" promotion
        }

    def add_promotion_trigger_to_spell_effect(self, spell_data: Dict[str, Any], spell_model) -> Dict[str, Any]:
        """Add promotion effects to spell processing."""
        enhanced_data = spell_data.copy()

        # Check if this spell provides promotion effects
        spell_name = spell_model.name
        if "growth" in spell_name.lower() or "promote" in spell_model.effect.lower():
            enhanced_data["promotion_effect"] = {
                "type": "single_unit",
                "health_increase": 1,
                "requires_selection": True,
            }

        return enhanced_data

    def _check_promotion_after_combat(self, combat_type: str, action_result: Dict[str, Any]):
        """Check for promotion opportunities after successful combat."""
        try:
            attacking_player = self.get_current_player_name()
            attacking_army_data = self.get_current_acting_army()

            if not attacking_army_data:
                print(f"GameEngine: No attacking army data for promotion check after {combat_type}")
                return

            army_units = attacking_army_data.get("units", [])
            if not army_units:
                print(f"GameEngine: No units in attacking army for promotion check after {combat_type}")
                return

            # Check for promotion opportunities
            opportunities = self.promotion_manager.find_promotion_options(army_units, attacking_player)

            if opportunities:
                print(
                    f"GameEngine: Found {len(opportunities)} promotion opportunities after successful {combat_type} combat"
                )

                # Emit signal to UI for promotion selection (low priority - don't force promotion)
                promotion_data = {
                    "trigger": f"{combat_type}_combat",
                    "player_name": attacking_player,
                    "army_data": attacking_army_data,
                    "opportunities": [self._promotion_option_to_dict(option) for option in opportunities],
                    "auto_promote": False,  # Combat promotions require player choice
                    "priority": "low",
                }

                # Emit signal for UI to handle promotion selection
                self.promotion_opportunities_available.emit(promotion_data)
                print(f"GameEngine: Promotion opportunity available for {attacking_player} after {combat_type}")
            else:
                print(f"GameEngine: No promotion opportunities available after {combat_type} combat")

        except Exception as e:
            print(f"GameEngine: Error checking promotion after {combat_type} combat: {e}")

    def _check_promotion_after_unit_kills(self, units_killed: List[Dict[str, Any]]):
        """Check for promotion opportunities after killing enemy units."""
        try:
            attacking_player = self.get_current_player_name()
            attacking_army_data = self.get_current_acting_army()

            if not attacking_army_data:
                print("GameEngine: No attacking army data for promotion check after unit kills")
                return

            # Calculate total health-worth of killed units for promotion eligibility
            total_health_worth = sum(unit.get("pre_damage_health", 1) for unit in units_killed)

            if total_health_worth >= 2:  # Minimum threshold for promotion rewards
                army_units = attacking_army_data.get("units", [])
                opportunities = self.promotion_manager.find_promotion_options(army_units, attacking_player)

                if opportunities:
                    # Scale promotion opportunities based on health-worth killed
                    max_promotions = min(len(opportunities), total_health_worth // 2)
                    available_promotions = opportunities[:max_promotions]

                    print(
                        f"GameEngine: Earned {max_promotions} promotion opportunities from killing {total_health_worth} health-worth of units"
                    )

                    promotion_data = {
                        "trigger": "unit_kills",
                        "player_name": attacking_player,
                        "army_data": attacking_army_data,
                        "opportunities": [self._promotion_option_to_dict(option) for option in available_promotions],
                        "health_worth_killed": total_health_worth,
                        "max_promotions": max_promotions,
                        "auto_promote": False,
                        "priority": "medium",
                    }

                    # Emit signal for UI to handle promotion selection
                    self.promotion_opportunities_available.emit(promotion_data)
                    print(
                        f"GameEngine: {max_promotions} promotion opportunities earned by {attacking_player} for unit kills"
                    )
                else:
                    print(
                        f"GameEngine: No promotion opportunities available despite killing {total_health_worth} health-worth"
                    )
            else:
                print(f"GameEngine: Insufficient health-worth killed ({total_health_worth}) for promotion eligibility")

        except Exception as e:
            print(f"GameEngine: Error checking promotion after unit kills: {e}")

    def _execute_dragon_attack_phase(self):
        """Execute the Dragon Attack Phase for the current marching player."""
        try:
            marching_player = self.get_current_player_name()
            print(f"GameEngine: Executing Dragon Attack Phase for {marching_player}")

            # Emit signal that Dragon Attack Phase has started
            self.dragon_attack_phase_started.emit(marching_player)

            # Execute the phase using the Dragon Attack Manager
            phase_result = self.dragon_attack_manager.execute_dragon_attack_phase(
                marching_player=marching_player,
                game_state_manager=self.game_state_manager,
                dua_manager=self.dua_manager,
                summoning_pool_manager=self.summoning_pool_manager,
            )

            # Process phase results
            if phase_result.phase_completed:
                print(f"GameEngine: Dragon Attack Phase completed - {phase_result.message}")

                # Handle dragon kills and promotions
                if phase_result.dragons_killed:
                    print(f"GameEngine: {len(phase_result.dragons_killed)} dragon(s) were killed")

                    # Check for promotion opportunities after killing dragons
                    for army_id in phase_result.armies_affected:
                        self._check_promotion_after_dragon_kill_victory(
                            army_id, marching_player, len(phase_result.dragons_killed)
                        )

                # Apply any breath effects to armies
                self._apply_dragon_breath_effects(phase_result)

                # Emit completion signal
                self.dragon_attack_phase_completed.emit({"result": phase_result, "marching_player": marching_player})

                # Advance to next phase
                print("GameEngine: Dragon Attack Phase completed, advancing to next phase")
                self.advance_phase()
            else:
                print(f"GameEngine: Dragon Attack Phase incomplete: {phase_result.message}")

        except Exception as e:
            print(f"GameEngine: Error executing Dragon Attack Phase: {e}")
            # Skip to next phase if there's an error
            self.advance_phase()

    def _check_promotion_after_dragon_kill_victory(self, army_id: str, player_name: str, dragons_killed: int):
        """Check for promotion opportunities after successfully killing dragons."""
        try:
            # Parse army identifier to get army data
            army_parts = army_id.split("_")
            if len(army_parts) >= 2:
                army_type = army_parts[-1]  # Assume last part is army type
                army_data = self.game_state_manager.get_army_data(player_name, army_type)

                if army_data:
                    result = self.check_promotion_after_dragon_kill(army_data, player_name)

                    if result.get("promotions_available", False):
                        print(f"GameEngine: Army {army_id} earned promotions for killing {dragons_killed} dragon(s)")

                        # Create promotion data for UI
                        promotion_data = {
                            "trigger": "dragon_kill_victory",
                            "player_name": player_name,
                            "army_data": army_data,
                            "opportunities": result.get("opportunities", []),
                            "dragons_killed": dragons_killed,
                            "auto_promote": True,  # Dragon kills allow automatic mass promotion
                            "priority": "high",
                        }

                        # Emit promotion opportunity signal
                        self.promotion_opportunities_available.emit(promotion_data)
                    else:
                        print(f"GameEngine: No promotion opportunities available for army {army_id}")

        except Exception as e:
            print(f"GameEngine: Error checking promotion after dragon kill victory: {e}")

    def _apply_dragon_breath_effects(self, phase_result):
        """Apply lingering dragon breath effects from the attack phase."""
        try:
            for terrain_attack in phase_result.terrain_attacks:
                for attack_result in terrain_attack.get("attack_results", []):
                    breath_effects = attack_result.get("breath_effects", [])

                    for breath_effect in breath_effects:
                        if breath_effect.get("duration") == "next_turn":
                            # Apply temporary effect to the army
                            army_id = terrain_attack.get("armies_affected", [""])[0]
                            if army_id:
                                self._apply_temporary_breath_effect(army_id, breath_effect)

        except Exception as e:
            print(f"GameEngine: Error applying dragon breath effects: {e}")

    def _apply_temporary_breath_effect(self, army_id: str, breath_effect: Dict[str, Any]):
        """Apply a temporary breath effect to an army."""
        try:
            effect_name = breath_effect.get("name", "Dragon Breath")
            effect_description = breath_effect.get("effect", "")
            modifier_type = breath_effect.get("modifier_type", "")

            # Use the effect manager to apply the breath effect
            self.effect_manager.add_effect(
                description=f"{effect_name}: {effect_description}",
                source="Dragon Breath Attack",
                target_type=constants.EFFECT_TARGET_ARMY,
                target_identifier=army_id,
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_TARGET,
                duration_value=1,
                caster_player_name=self.get_current_player_name(),
                effect_data={"modifier_type": modifier_type},
            )

            print(f"GameEngine: Applied breath effect '{effect_name}' to army {army_id}")

        except Exception as e:
            print(f"GameEngine: Error applying temporary breath effect: {e}")
