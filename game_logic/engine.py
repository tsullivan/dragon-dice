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
    unit_selection_required = Signal(str, int, list)  # player_name, damage_amount, available_units
    damage_allocation_completed = Signal(str, int)  # player_name, total_damage_applied
    
    # New signals to replace direct calls
    march_step_change_requested = Signal(str)  # new_march_step
    action_step_change_requested = Signal(str)  # new_action_step
    phase_advance_requested = Signal()
    player_advance_requested = Signal()
    effect_expiration_requested = Signal(str)  # player_name
    dice_roll_submitted = Signal(str, str, str)  # roll_type, results_string, player_name
    damage_allocation_requested = Signal(str, str, str, int)  # player_name, army_id, unit_name, new_health

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
        self.effect_expiration_requested.connect(self.effect_manager.process_effect_expirations)
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
            # Request march step initialization through signal
            self.march_step_change_requested.emit(constants.MARCH_STEP_DECIDE_MANEUVER)
            self._current_march_step = constants.MARCH_STEP_DECIDE_MANEUVER
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
        """Request maneuver decision processing. Manager will emit signals to update state."""
        print(
            f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}"
        )

        # Mark that the first turn interaction has begun
        if self._is_very_first_turn:
            self._is_very_first_turn = False

        # Emit signal to TurnManager to handle decision
        if wants_to_maneuver:
            self.march_step_change_requested.emit(constants.MARCH_STEP_AWAITING_MANEUVER_INPUT)
            self._current_march_step = constants.MARCH_STEP_AWAITING_MANEUVER_INPUT
        else:
            self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
            self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_maneuver_input(self, details: str):
        """Request maneuver input processing. Manager will emit signals to update state."""
        print(
            f"Player {self.get_current_player_name()} submitted maneuver details: {details}"
        )
        # Emit signal to TurnManager to handle input
        self.march_step_change_requested.emit(constants.MARCH_STEP_SELECT_ACTION)
        self._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def select_action(self, action_type: str):
        """Request action selection processing. Manager will emit signals to update state."""
        print(f"Player {self.get_current_player_name()} selected action: {action_type}")
        # Emit signal to TurnManager to handle action selection
        if action_type == constants.ACTION_MELEE:
            action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL
        elif action_type == constants.ACTION_MISSILE:
            action_step = constants.ACTION_STEP_AWAITING_ATTACKER_MISSILE_ROLL
        elif action_type == constants.ACTION_MAGIC:
            action_step = constants.ACTION_STEP_AWAITING_MAGIC_ROLL
        else:
            print(f"Unknown action type: {action_type}")
            return
        
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
            print(
                "GameEngine: Error: Could not parse attacker melee results via ActionResolver."
            )
            return
        print(f"GameEngine: Parsed attacker melee via ActionResolver: {parsed_results}")

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

        defending_player_name = constants.PLACEHOLDER_OPPONENT_NAME

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
        Example: [{'name': 'Flatland', 'type': 'Frontier', 'details': 'Face 3'}, ...]
        This method queries GameStateManager.
        """
        relevant_terrains_info = []
        all_terrains_state = self.game_state_manager.get_all_terrain_data()

        # For now, let's consider all terrains "relevant".
        # Later, this could be filtered based on current player's army locations or game rules.
        for terrain_name, terrain_data in all_terrains_state.items():
            controller = terrain_data.get("controller", "None")
            details = f"Face {terrain_data.get('face', constants.DEFAULT_NA_VALUE)}"
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
    
    def get_available_units_for_damage(self, player_name: str, army_identifier: str = None) -> list:
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
        available_units = [
            unit for unit in units 
            if unit.get("health", 0) > 0
        ]
        
        return available_units
    
    def request_unit_damage_allocation(self, player_name: str, damage_amount: int, army_identifier: str = None):
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
        
        print(f"GameEngine: Requesting damage allocation for {player_name}: {damage_amount} damage, {len(available_units)} units available")
        
        # Emit signal for UI to handle unit selection
        self.unit_selection_required.emit(player_name, damage_amount, available_units)
    
    def allocate_damage_to_units(self, player_name: str, damage_allocations: dict, army_identifier: str = None):
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
            
            success = self.game_state_manager.update_unit_health(
                player_name, 
                army_id, 
                unit_name, 
                new_health
            )
            
            if success:
                total_damage_applied += damage_amount
                print(f"GameEngine: Applied {damage_amount} damage to {unit_name}")
            else:
                print(f"GameEngine: Failed to apply damage to {unit_name}")
        
        print(f"GameEngine: Total damage applied: {total_damage_applied}")
        self.damage_allocation_completed.emit(player_name, total_damage_applied)
        self.game_state_updated.emit()
    
    def auto_allocate_damage(self, player_name: str, damage_amount: int, army_identifier: str = None):
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
                "points_value": army_data.get("points_value", 0)
            }
        
        return armies_summary
