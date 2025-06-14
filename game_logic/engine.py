from PySide6.QtCore import QObject, Signal
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
        self.action_resolver = ActionResolver(parent=self)
        self.effect_manager = EffectManager(parent=self)
        self.game_state_manager = GameStateManager(player_setup_data, frontier_terrain, distance_rolls, parent=self)

        # Connect signals from managers to GameEngine signals or slots
        self.turn_manager.current_player_changed.connect(self.current_player_changed.emit)
        self.turn_manager.current_phase_changed.connect(self.current_phase_changed.emit) # Assuming TurnManager will emit display string
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

        # TODO: 1. Identify Attacking Army and its units/items from self.player_setup_data and current game state.
        # TODO: 2. Identify Defending Army and its units/items.
        # TODO: 3. Parse 'results' string into a list of icons/SAIs rolled by the attacker.
        #          Example: results_list = self._parse_dice_string(results)
        
        # TODO: 4. Perform Dice Roll Resolution for the attacker.
        #          attacker_calculated_results = self._resolve_dice_roll(
        #              army_units=attacker_army_units, # List of unit objects/dicts
        #              rolled_icons=results_list,
        #              roll_type="MELEE",
        #              acting_player=self.get_current_player_name()
        #          )
        #          This would involve:
        #              - Applying SAIs that modify the roll or have immediate effects.
        #              - Counting normal melee icons.
        #              - Converting ID icons to melee results (depends on unit).
        #              - Applying modifiers from active effects, spells, terrain.
        #              - Storing final melee damage, and any SAIs to be applied to defender's save roll.

        # For now, let's assume attacker_calculated_results is a dict:
        # attacker_calculated_results = {"melee_damage": 5, "sais_for_defender": ["SomeSAI"]}

        parsed_results = self._parse_dice_string(results, roll_type="MELEE")
        if not parsed_results:
            print("Error: Could not parse attacker melee results.")
            # Optionally, do not advance state or provide UI feedback
            return
        print(f"Parsed attacker melee: {parsed_results}")
        # self.pending_attacker_results = attacker_calculated_results # Store for defender's turn

        # Delegate to ActionResolver (conceptual)
        # self.action_resolver.resolve_melee_attack(attacker_army, defender_army, results)
        # ActionResolver would then emit signals or update state that GameEngine reacts to.

        self.turn_manager.current_action_step = constants.ACTION_STEP_AWAITING_DEFENDER_SAVES
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def _parse_dice_string(self, dice_string: str, roll_type: str) -> list:
        """
        Helper to parse a string like '3 melee, 1 sai:bullseye, 2 id' into a structured list.
        Returns an empty list if parsing fails.
        """
        # Very basic placeholder parser. This needs to be robust.
        # Example: "2m, 1s:doubler, 3id"
        # TODO: Implement robust parsing (regex, string splitting, error handling)
        # For now, just a conceptual print.
        print(f"Attempting to parse '{dice_string}' for roll type '{roll_type}'")
        parsed_list = []
        parts = dice_string.lower().split(',')
        for part in parts:
            part = part.strip()
            # This is highly simplified and needs proper logic for numbers, icon names, and SAI names.
            if "melee" in part or "m" in part: # Example
                parsed_list.append({"type": constants.ICON_MELEE, "count": int(part.split(' ')[0]) if part.split(' ')[0].isdigit() else 1})
        return parsed_list

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

        # TODO: 1. Identify Defending Army and its units/items.
        # TODO: 2. Identify Attacking Army (from self.pending_attacker_results or game state).
        # TODO: 3. Parse 'results' string for defender's save roll.
        parsed_save_results = self._parse_dice_string(results, roll_type="SAVE")
        if not parsed_save_results:
            print("Error: Could not parse defender save results.")
            # Optionally, do not advance state or provide UI feedback
            return
        print(f"Parsed defender saves: {parsed_save_results}")

        #          defender_rolled_icons = self._parse_dice_string(results)

        # TODO: 4. Perform Dice Roll Resolution for the defender's saves.
        #          defender_calculated_saves = self._resolve_dice_roll(
        #              army_units=defender_army_units,
        #              rolled_icons=defender_rolled_icons,
        #              roll_type="SAVE",
        #              acting_player=opponent_player_name, # Need to get opponent name
        #              # Pass attacker's SAIs that affect saves: self.pending_attacker_results.get("sais_for_defender")
        #          )
        #          This would involve:
        #              - Applying attacker's SAIs that affect saves.
        #              - Applying defender's SAIs that generate saves.
        #              - Counting normal save icons.
        #              - Converting ID icons to save results.
        #              - Applying modifiers.

        # TODO: 5. Calculate final damage:
        #          final_damage = self.pending_attacker_results.get("melee_damage", 0) - defender_calculated_saves.get("saves", 0)
        #          final_damage = max(0, final_damage) # Damage cannot be negative

        # TODO: 6. Apply damage to defending units (update health, move to DUA if killed).
        #          self._apply_damage_to_army(defender_army_identifier, final_damage)

        # TODO: 7. Check for counter-attack (Rulebook pg. 12).
        #          If counter-attack:
        #              self.current_action_step = "AWAITING_MELEE_COUNTER_ATTACK_ROLL"
        #              # Swap roles for the next submission.
        #          Else:
        #              print(f"Melee action in {self.current_phase} complete.")
        #              self.current_action_step = ""

        print(f"Melee action in {self.current_phase} complete.")
        self.turn_manager.current_action_step = ""
        self.advance_phase() # Or advance march step if within a march

    def _resolve_spell_effect(self, spell_name: str, caster_player_name: str, target_identifier: str, target_type: str, affected_player_name: Optional[str] = None):
        """Placeholder for resolving spell effects and adding active effects."""
        print(f"Resolving spell: {spell_name} by {caster_player_name} on {target_identifier}")
        if spell_name == "Blizzard": # Example from rulebook (pg. 46)
            self.effect_manager.add_effect(
                description="Melee results -3 for armies at this terrain",
                source="Spell: Blizzard",
                target_type="TERRAIN",
                target_identifier=target_identifier, # e.g., "Frontier Terrain"
                duration_type="NEXT_TURN_CASTER", 
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
                    "location": army_data.get("location", "Unknown")
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
            details = f"Face {terrain_data.get('face', 'N/A')}"
            if controller and controller != 'None':
                details += f", Controlled by: {controller}"
            
            relevant_terrains_info.append({
                "name": terrain_name,
                "type": terrain_data.get("type", "Unknown"),
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
                target_type="ARMY",
                target_identifier=target_army_identifier, # e.g., "Player 2 Home Army"
                duration_type="NEXT_TURN_CASTER", # "your next turn" refers to the player whose unit rolled the SAI
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
                target_type="ARMY",
                target_identifier=target_army_identifier,
                duration_type="NEXT_TURN_TARGET", # "its next turn" refers to the target army's player.
                duration_value=1,
                caster_player_name=attacking_dragon_controller, # Player who controls the attacking dragon
                affected_player_name=target_army_player_name
            )

    def get_displayable_active_effects(self) -> list[str]:
        """Returns a list of strings representing active effects for UI display."""
        return self.effect_manager.get_displayable_effects()
