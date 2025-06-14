from PySide6.QtCore import QObject, Signal
import uuid # For generating unique effect IDs

TURN_PHASES = [
    "EXPIRE_EFFECTS",
    "EIGHTH_FACE",
    "DRAGON_ATTACK",
    "SPECIES_ABILITIES",
    "FIRST_MARCH",
    "SECOND_MARCH",
    "RESERVES"
]

MARCH_STEPS = [
    "DECIDE_MANEUVER",
    "AWAITING_MANEUVER_INPUT", # If decided to maneuver
    "SELECT_ACTION" # Or directly to this if no maneuver
]

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

        self.current_player_idx = self.player_names.index(first_player_name) if first_player_name in self.player_names else 0
        self.current_phase_idx = 0 # Start with EXPIRE_EFFECTS
        self.current_phase = TURN_PHASES[self.current_phase_idx]
        self.current_march_step = "" # Will be set when entering a march phase
        self.active_effects = [] # To store active effects
        self.current_action_step = "" # For sub-steps within Melee, Missile, Magic

        self._initialize_turn_for_current_player()

        print(f"GameEngine Initialized: First Player: {self.get_current_player_name()}, Phase: {self.current_phase}, Step: {self.current_march_step}")

    def _initialize_turn_for_current_player(self):
        self.current_phase_idx = 0
        self.current_phase = TURN_PHASES[self.current_phase_idx]
        self._handle_phase_entry()
        self.current_player_changed.emit(self.get_current_player_name())
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def _handle_phase_entry(self):
        """Logic to execute when entering a new phase."""
        self.current_march_step = "" # Reset march step
        self.current_action_step = "" # Reset action step

        if self.current_phase == "FIRST_MARCH" or self.current_phase == "SECOND_MARCH":
            self.current_march_step = MARCH_STEPS[0] # DECIDE_MANEUVER
        elif self.current_phase == "EXPIRE_EFFECTS":
            # Example: Auto-advancing phase
            self._process_expire_effects_phase() # Process and then advance
            self.advance_phase() 
        elif self.current_phase == "EIGHTH_FACE":
            # TODO: Implement logic for eighth face effects
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")
            # This phase will wait for a "Continue" click from the UI
        elif self.current_phase == "DRAGON_ATTACK":
            # TODO: Implement logic for dragon attacks. This will likely involve new action_steps.
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")
            # This phase will wait for a "Continue" click or specific interactions
        else:
            # For other phases like SPECIES_ABILITIES, RESERVES,
            # they might have their own internal steps or auto-advance.
            # For now, let's assume they might also auto-advance or wait for a "continue"
            print(f"Phase: {self.current_phase} for {self.get_current_player_name()}")
            # self.advance_phase() # Placeholder: many phases will need user interaction

    def advance_phase(self):
        self.current_phase_idx += 1
        if self.current_phase_idx >= len(TURN_PHASES):
            # Current player's turn ends, advance to next player
            print(f"All phases complete for {self.get_current_player_name()}. Advancing player.")
            self.advance_player()
        else:
            self.current_phase = TURN_PHASES[self.current_phase_idx]
            self._handle_phase_entry()
            self.current_phase_changed.emit(self.get_current_phase_display())
            self.game_state_updated.emit()

    def advance_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.player_names)
        self._initialize_turn_for_current_player()

    def get_current_player_name(self):
        return self.player_names[self.current_player_idx]

    def get_current_phase_display(self):
        phase_display = self.current_phase.replace('_', ' ').title()
        if self.current_march_step:
            phase_display += f" - {self.current_march_step.replace('_', ' ').title()}"
        if self.current_action_step: # For Melee/Missile/Magic sub-steps
            phase_display += f" - {self.current_action_step.replace('_', ' ').title()}"
        return phase_display

    def decide_maneuver(self, wants_to_maneuver: bool):
        print(f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}")
        # Example state transition
        self.current_march_step = MARCH_STEPS[1] if wants_to_maneuver else MARCH_STEPS[2] # AWAITING_MANEUVER_INPUT or SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_maneuver_input(self, details: str):
        print(f"Player {self.get_current_player_name()} submitted maneuver details: {details}")
        # Process details if necessary
        self.current_march_step = MARCH_STEPS[2] # SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def select_action(self, action_type: str):
        """Handles selection of Melee, Missile, or Magic action."""
        print(f"Player {self.get_current_player_name()} selected action: {action_type}")
        if action_type == "MELEE":
            self.current_action_step = "AWAITING_ATTACKER_MELEE_ROLL"
        elif action_type == "MISSILE":
            self.current_action_step = "AWAITING_ATTACKER_MISSILE_ROLL" # Example
        elif action_type == "MAGIC":
            self.current_action_step = "AWAITING_MAGIC_ROLL" # Example
        else:
            print(f"Unknown action type: {action_type}")
            # Potentially revert to SELECT_ACTION or handle error
            return
        
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_attacker_melee_results(self, results: str):
        """Handles submission of attacker's melee roll results."""
        if self.current_action_step != "AWAITING_ATTACKER_MELEE_ROLL":
            print("Error: Not expecting attacker melee results now.")
            return
        print(f"Player {self.get_current_player_name()} (Attacker) submitted melee results: {results}")
        # TODO: Process results (calculate damage, apply SAIs etc.)
        self.current_action_step = "AWAITING_DEFENDER_SAVES"
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_defender_save_results(self, results: str):
        """Handles submission of defender's save roll results."""
        if self.current_action_step != "AWAITING_DEFENDER_SAVES":
            print("Error: Not expecting defender save results now.")
            return
        print(f"Player {self.get_current_player_name()}'s Opponent (Defender) submitted save results: {results}")
        # TODO: Process results (calculate final damage, check for counter-attack)
        # For now, let's assume the melee action ends here and we advance the phase.
        # In a full implementation, this would go to AWAITING_MELEE_COUNTER_ATTACK or similar.
        print(f"Melee action in {self.current_phase} complete.")
        self.current_action_step = "" # Clear action step # TODO: Refactor to controller
        # self.current_march_step = "" # Clear march step if action completes the march
        self.advance_phase() # Or advance march step if within a march
        # self.game_state_updated.emit() # advance_phase already emits

    def get_all_player_summary_data(self):
        """
        Returns a list of dictionaries, each summarizing a player's status.
        Example: [{'name': 'P1', 'captured_terrains': 0, 'terrains_to_win': 2, 
                   'armies': [{'name': 'Home', 'points': 10, 'location': 'Highland'}, ...]}, ...]
        """
        summaries = []
        # Placeholder: Actual captured terrains and locations would come from game state
        terrains_to_win = 2 # Example, could be dynamic
        for p_data in self.player_setup_data:
            player_summary = {
                "name": p_data.get("name", "N/A"),
                "captured_terrains": 0, # Placeholder
                "terrains_to_win": terrains_to_win,
                "armies": []
            }
            for army_type, army_details in p_data.get("armies", {}).items():
                player_summary["armies"].append({
                    "name": army_details.get("name", army_type.title()),
                    "points": army_details.get("points", 0),
                    "location": "Unknown" # Placeholder, actual location needed
                })
            summaries.append(player_summary)
        return summaries

    def get_relevant_terrains_info(self):
        """
        Returns a list of dictionaries for relevant terrains for the current player.
        Example: [{'name': 'Flatland', 'type': 'Frontier', 'details': 'Face 3'}, ...]
        """
        # Placeholder implementation
        current_player_info = self.players_info[self.current_player_idx]
        return [
            {"name": self.frontier_terrain, "type": "Frontier", "details": "Contested"},
            {"name": current_player_info.get("home_terrain", "N/A"), "type": "Home", "details": f"{current_player_info.get('name')}'s Home"},
            # Add opponent's home terrain if applicable and identifiable
        ]

    def _generate_unique_effect_id(self):
        return str(uuid.uuid4())

    def add_active_effect(self, description: str, source: str, target_type: str, target_identifier: str,
                          duration_type: str, duration_value: int,
                          caster_player_name: str, affected_player_name: str = None):
        """
        Adds a new active effect to the game.
        duration_type examples: "NEXT_TURN_CASTER", "NEXT_TURN_TARGET", "ROUNDS"
        """
        effect = {
            "id": self._generate_unique_effect_id(),
            "description": description,
            "source": source,
            "target_type": target_type,         # e.g., "ARMY", "PLAYER", "TERRAIN", "UNIT"
            "target_identifier": target_identifier, # e.g., "Player 1 Home Army", "Player 2", "Frontier Terrain", "Unit ID X"
            "duration_type": duration_type,
            "duration_value": duration_value,   # e.g., 1 for "next turn", or number of rounds
            "caster_player_name": caster_player_name,
            "affected_player_name": affected_player_name or caster_player_name
        }
        self.active_effects.append(effect)
        print(f"Effect added: {description} on {target_identifier} for {duration_value} {duration_type}")
        self.game_state_updated.emit()

    def _process_expire_effects_phase(self):
        """Processes and removes expired effects."""
        current_player_name = self.get_current_player_name()
        effects_to_remove = []

        for effect in self.active_effects:
            expired = False
            if effect["duration_type"] == "NEXT_TURN_CASTER" and effect["caster_player_name"] == current_player_name:
                # This assumes the effect was meant to last until the start of this specific player's next turn.
                # A more robust way might be to decrement a turn counter or use a specific turn number.
                # For simplicity, if it's their turn and it's a "next turn" effect, it expires.
                expired = True
            elif effect["duration_type"] == "NEXT_TURN_TARGET" and effect["affected_player_name"] == current_player_name:
                expired = True
            elif effect["duration_type"] == "ROUNDS":
                effect["duration_value"] -= 1
                if effect["duration_value"] <= 0:
                    expired = True
            
            if expired:
                effects_to_remove.append(effect)
        
        for expired_effect in effects_to_remove:
            self.active_effects.remove(expired_effect)
            print(f"Effect expired: {expired_effect['description']} on {expired_effect['target_identifier']}")

        if effects_to_remove:
            self.game_state_updated.emit()

    def get_displayable_active_effects(self) -> list[str]:
        """Returns a list of strings representing active effects for UI display."""
        return [f"[{effect['target_type']}: {effect['target_identifier']}] {effect['description']} ({effect['duration_value']} {effect['duration_type']}) - by {effect['caster_player_name']}" for effect in self.active_effects]
