from PySide6.QtCore import QObject, Signal, Slot
import uuid # For generating unique effect IDs
from typing import Optional # Import Optional
import constants
from game_logic.turn_manager import TurnManager
from game_logic.action_resolver import ActionResolver
from game_logic.effect_manager import EffectManager
from game_logic.game_state_manager import GameStateManager

class GameEngine(QObject):
    """
    Manages the core game logic and state for the PySide6 version.
    """
    game_state_updated = Signal() # Emitted when significant game state changes
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)

    def __init__(self, player_setup_data, first_player_name, frontier_terrain, distance_rolls, parent=None):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        # Extract player names and create a simple list of player objects or dicts if needed
        self.players_info = [{"name": p['name'], "home_terrain": p['home_terrain']} for p in player_setup_data]
        self.player_names = [p['name'] for p in self.players_info]
        self.num_players = len(self.player_names)

        self.first_player_name = first_player_name
        self.frontier_terrain = frontier_terrain
        self.distance_rolls = distance_rolls # List of (player_name, distance)

        # Instantiate managers
        self.turn_manager = TurnManager(self.player_names, self.first_player_name, parent=self)
        self.effect_manager = EffectManager(parent=self)
        self.game_state_manager = GameStateManager(player_setup_data, frontier_terrain, distance_rolls, parent=self)
        self.action_resolver = ActionResolver(self.game_state_manager, self.effect_manager, parent=self)

        # Connect signals from managers to GameEngine signals or slots
        self.turn_manager.current_player_changed.connect(self.current_player_changed.emit)
        self.turn_manager.current_phase_changed.connect(self.current_phase_changed.emit) # Assuming TurnManager will emit display string
        self.action_resolver.next_action_step_determined.connect(self._set_next_action_step) # Connect new signal
        self.game_state_manager.game_state_changed.connect(self.game_state_updated.emit) # If game state changes, emit general update
        self.effect_manager.effects_changed.connect(self.game_state_updated.emit) # If effects change, game state is updated

        self._initialize_turn_for_current_player()

        print(f"GameEngine Initialized: First Player: {self.get_current_player_name()}, Phase: {self.current_phase}, Step: {self.current_march_step}")

    def _initialize_turn_for_current_player(self):
        self.turn_manager.initialize_turn()
        self._handle_phase_entry()
        # current_player_changed and current_phase_changed will be emitted by TurnManager or after _handle_phase_entry
        # self.current_player_changed.emit(self.get_current_player_name())
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def _handle_phase_entry(self):
        """Logic to execute when entering a new phase."""
        # TurnManager.advance_phase() already resets march_step and action_step.
        # This method now focuses on setting the *initial* step for certain phases.

        current_phase = self.turn_manager.current_phase

        if current_phase == constants.PHASE_FIRST_MARCH or current_phase == constants.PHASE_SECOND_MARCH:
            self.turn_manager.current_march_step = constants.MARCH_STEP_DECIDE_MANEUVER
        elif current_phase == constants.PHASE_EXPIRE_EFFECTS:
            print(f"Phase: {current_phase} for {self.get_current_player_name()}")
            # Perform effect expirations
            self.effect_manager.process_effect_expirations(self.get_current_player_name())
            self.advance_phase() # GameEngine still controls advancing for now
        elif self.current_phase == constants.PHASE_EIGHTH_FACE:
            # TODO: Implement logic for eighth face effects
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")
            # This phase will wait for a "Continue" click from the UI
        elif self.current_phase == constants.PHASE_DRAGON_ATTACK:
            # TODO: Implement logic for dragon attacks. This will likely involve new action_steps.
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")
            # This phase will wait for a "Continue" click or specific interactions
        else:
            # For other phases like SPECIES_ABILITIES, RESERVES,
            # they might have their own internal steps or auto-advance.
            # For now, let's assume they might also auto-advance or wait for a "continue"
            # These phases will wait for a "Continue" click from the UI, which calls
            # game_engine.advance_phase() via the controller.
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")

    # Properties to access TurnManager's state for convenience
    @property
    def current_phase(self):
        return self.turn_manager.current_phase

    @property
    def current_march_step(self):
        return self.turn_manager.current_march_step

    @property
    def current_action_step(self):
        return self.turn_manager.current_action_step

    def advance_phase(self):
        self.turn_manager.advance_phase() # Assumes TurnManager now handles internal state and emits signals
        # After TurnManager advances, GameEngine needs to handle the entry into the new phase.
        self._handle_phase_entry()
        # Emit signals to ensure UI updates after phase entry logic.
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def advance_player(self):
        self.turn_manager.advance_player() # TurnManager will update its current_player_idx and emit
        self._initialize_turn_for_current_player()

    def get_current_player_name(self):
        return self.turn_manager.player_names[self.turn_manager.current_player_idx]

    def get_current_phase_display(self):
        phase_display = self.turn_manager.current_phase.replace('_', ' ').title()
        if self.turn_manager.current_march_step:
            phase_display += f" - {self.turn_manager.current_march_step.replace('_', ' ').title()}"
        if self.turn_manager.current_action_step:
            phase_display += f" - {self.turn_manager.current_action_step.replace('_', ' ').title()}"
        return phase_display

    def decide_maneuver(self, wants_to_maneuver: bool):
        print(f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}")
        if wants_to_maneuver:
            self.turn_manager.current_march_step = constants.MARCH_STEPS[constants.MARCH_STEPS.index(constants.MARCH_STEP_AWAITING_MANEUVER_INPUT)]
        else:
            self.turn_manager.current_march_step = constants.MARCH_STEPS[constants.MARCH_STEPS.index(constants.MARCH_STEP_SELECT_ACTION)]
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_maneuver_input(self, details: str):
        print(f"Player {self.get_current_player_name()} submitted maneuver details: {details}")
        # TODO: Process details if necessary (e.g., if it's a dice roll string)
        self.turn_manager.current_march_step = constants.MARCH_STEPS[constants.MARCH_STEPS.index(constants.MARCH_STEP_SELECT_ACTION)]
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def select_action(self, action_type: str):
        """Handles selection of Melee, Missile, or Magic action."""
        print(f"Player {self.get_current_player_name()} selected action: {action_type}")
        if action_type == constants.ACTION_MELEE:
            self.turn_manager.current_action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL
        elif action_type == constants.ACTION_MISSILE:
            self.turn_manager.current_action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MISSILE_ROLL
        elif action_type == constants.ACTION_MAGIC:
            self.turn_manager.current_action_step = constants.ACTION_STEP_AWAITING_MAGIC_ROLL
        else:
            print(f"Unknown action type: {action_type}")
            return
        
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()
    def submit_attacker_melee_results(self, results: str):
        """Handles submission of attacker's melee roll results."""
        if self.turn_manager.current_action_step != constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL:
            print("Error: Not expecting attacker melee results now.")
            return
        print(f"Player {self.get_current_player_name()} (Attacker) submitted melee results: {results}")

        parsed_results = self.action_resolver.parse_dice_string(results, roll_type="MELEE")
        if not parsed_results:
            print("GameEngine: Error: Could not parse attacker melee results via ActionResolver.")
            # Optionally, do not advance state or provide UI feedback
            return
        print(f"GameEngine: Parsed attacker melee via ActionResolver: {parsed_results}")

        # ActionResolver processes the roll and will emit `next_action_step_determined`
        # which is connected to self._set_next_action_step
        attacker_outcome = self.action_resolver.process_attacker_melee_roll(
            attacking_player_name=self.get_current_player_name(),
            parsed_dice_results=parsed_results
        )
        self.pending_attacker_outcome = attacker_outcome # Store attacker's outcome
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
        """Handles submission of defender's save roll results."""
        if self.turn_manager.current_action_step != constants.ACTION_STEP_AWAITING_DEFENDER_SAVES:
            print("Error: Not expecting defender save results now.")
            return
        print(f"Player {self.get_current_player_name()}'s Opponent (Defender) submitted save results: {results}")

        parsed_save_results = self.action_resolver.parse_dice_string(results, roll_type="SAVE")
        if not parsed_save_results:
            print("Error: Could not parse defender save results.")
            return
        print(f"Parsed defender saves: {parsed_save_results}")

        if not hasattr(self, 'pending_attacker_outcome') or not self.pending_attacker_outcome:
            print("Error: No pending attacker outcome to resolve defender saves against.")
            # Potentially reset state or log error
            return

        # TODO: Determine defending_player_name. This is complex as it depends on target.
        # For now, assume it's an opponent if more than one player.
        # This needs a robust way to identify the target of the attack.
        defending_player_name = constants.PLACEHOLDER_OPPONENT_NAME # This needs to be correctly identified

        defender_outcome = self.action_resolver.process_defender_save_roll(
            defending_player_name=defending_player_name, # Needs to be correctly identified
            parsed_save_dice=parsed_save_results,
            attacker_outcome=self.pending_attacker_outcome
        )
        print(f"GameEngine: Defender save outcome from ActionResolver: {defender_outcome}")
        del self.pending_attacker_outcome # Clear pending outcome

        # The next step (counter-attack or end action) is set by ActionResolver's signal.
        # If the next_action_step is "", it means the action is complete.
        if not self.turn_manager.current_action_step: # Check if ActionResolver cleared the step
            print(f"Melee action in {self.current_phase} complete.")
            self.advance_phase() # Or advance march step if within a march
        else:
            self.current_phase_changed.emit(self.get_current_phase_display()) # Update UI for counter-attack step
            self.game_state_updated.emit()

    @Slot(str)
    def _set_next_action_step(self, next_step: str):
        """Slot to update the current action step in TurnManager."""
        print(f"GameEngine: Setting next action step to: {next_step}")
        self.turn_manager.current_action_step = next_step

    def _resolve_spell_effect(self, spell_name: str, caster_player_name: str, target_identifier: str, target_type: str, affected_player_name: Optional[str] = None):
        """Placeholder for resolving spell effects and adding active effects."""
        print(f"Resolving spell: {spell_name} by {caster_player_name} on {target_identifier}")
        if spell_name == "Blizzard": # Example from rulebook (pg. 46)
            self.effect_manager.add_effect(
                description="Melee results -3 for armies at this terrain",
                source="Spell: Blizzard",
                target_type=constants.EFFECT_TARGET_TERRAIN,
                target_identifier=target_identifier, # e.g., "Frontier Terrain"
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_CASTER,
                duration_value=1, # Duration until caster's next turn
                caster_player_name=caster_player_name
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
        terrains_to_win = 2 # Example, could be dynamic

        all_players_state = self.game_state_manager.get_all_players_data()
        for player_name, player_state in all_players_state.items():
            army_list = []
            for army_key, army_data in player_state.get("armies", {}).items():
                army_list.append({
                    "name": army_data.get("name", army_key.title()),
                    "points": army_data.get("points_value", 0), # Ensure key matches GameStateManager
                    "location": army_data.get("location", constants.DEFAULT_UNKNOWN_VALUE)
                })

            summaries.append({
                "name": player_name,
                "captured_terrains": player_state.get("captured_terrains_count", 0),
                "terrains_to_win": terrains_to_win, # This could also come from a game settings manager
                "armies": army_list
            })
        return summaries

    def get_relevant_terrains_info(self):
        """
        Returns a list of dictionaries for relevant terrains for the current player.
        Example: [{'name': 'Flatland', 'type': 'Frontier', 'details': 'Face 3'}, ...]
        This method queries GameStateManager.
        """
        relevant_terrains_info = []
        all_terrains_state = self.game_state_manager.get_all_terrain_data()

        # For now, let's consider all terrains "relevant".
        # Later, this could be filtered based on current player's army locations or game rules.
        for terrain_name, terrain_data in all_terrains_state.items():
            controller = terrain_data.get('controller', 'None')
            details = f"Face {terrain_data.get('face', constants.DEFAULT_NA_VALUE)}"
            if controller and controller != 'None':
                details += f", Controlled by: {controller}"
            
            relevant_terrains_info.append({
                "name": terrain_name,
                "type": terrain_data.get("type", constants.DEFAULT_UNKNOWN_VALUE),
                "details": details
            })
        return relevant_terrains_info

    def _resolve_sai_effect(self, sai_name: str, rolling_player_name: str, target_army_identifier: str, target_army_player_name: Optional[str]):
        """Placeholder for resolving SAI effects and adding active effects."""
        print(f"Resolving SAI: {sai_name} by {rolling_player_name} on {target_army_identifier}")
        if sai_name == "Frost Breath": # Example from rulebook (pg. 36)
            self.effect_manager.add_effect(
                description="All results halved",
                source="SAI: Frost Breath",
                target_type=constants.EFFECT_TARGET_ARMY,
                target_identifier=target_army_identifier, # e.g., "Player 2 Home Army"
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_CASTER, # "your next turn" refers to the player whose unit rolled the SAI
                duration_value=1,
                caster_player_name=rolling_player_name,
                affected_player_name=target_army_player_name
            )

    def _resolve_dragon_breath_effect(self, breath_type: str, attacking_dragon_controller: str, target_army_identifier: str, target_army_player_name: Optional[str]):
        """Placeholder for resolving dragon breath effects and adding active effects."""
        print(f"Resolving Dragon Breath: {breath_type} on {target_army_identifier}")
        if breath_type == "Air": # Example from rulebook (pg. 19)
            self.effect_manager.add_effect(
                description="Melee results halved",
                source="Dragon Breath: Air",
                target_type=constants.EFFECT_TARGET_ARMY,
                target_identifier=target_army_identifier,
                duration_type=constants.EFFECT_DURATION_NEXT_TURN_TARGET, # "its next turn" refers to the target army's player.
                duration_value=1,
                caster_player_name=attacking_dragon_controller, # Player who controls the attacking dragon
                affected_player_name=target_army_player_name
            )

    def get_displayable_active_effects(self) -> list[str]:
        """Returns a list of strings representing active effects for UI display."""
        return self.effect_manager.get_displayable_effects()
