from PySide6.QtCore import QObject, Slot

from game_logic.game_orchestrator import GameOrchestrator as GameEngine
from utils import strict_get


class GameplayController(QObject):
    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine

    @Slot(bool)
    def handle_maneuver_decision(self, wants_to_maneuver: bool):
        print(f"[GameplayController] Handling maneuver: {wants_to_maneuver}")
        self.game_engine.decide_maneuver(wants_to_maneuver)

    @Slot(str)
    def handle_maneuver_input_submission(self, maneuver_details: str):
        print(f"[GameplayController] Handling maneuver input: {maneuver_details}")
        self.game_engine.submit_maneuver_input(maneuver_details)

    @Slot()
    def handle_melee_action_selected(self):
        print("[GameplayController] Melee action selected")
        self.game_engine.select_action("MELEE")

    @Slot()
    def handle_missile_action_selected(self):
        print("[GameplayController] Missile action selected")
        self.game_engine.select_action("MISSILE")

    @Slot()
    def handle_magic_action_selected(self):
        print("[GameplayController] Magic action selected")
        self.game_engine.select_action("MAGIC")

    @Slot()
    def handle_skip_action_selected(self):
        print("[GameplayController] Skip action selected")
        self.game_engine.select_action("SKIP")

    @Slot(str)
    def handle_attacker_melee_submission(self, results: str):
        print(f"[GameplayController] Attacker melee results: {results}")
        self.game_engine.submit_attacker_melee_results(results)

    @Slot(str)
    def handle_defender_save_submission(self, results: str):
        print(f"[GameplayController] Defender save results: {results}")
        self.game_engine.submit_defender_save_results(results)

    @Slot()
    def handle_continue_to_next_phase(self):
        print("[GameplayController] Continue to next phase requested.")
        self.game_engine.advance_phase()

    # Critical signal handlers with debug logging
    @Slot(str, int, list)
    def handle_unit_selection_required(self, player_name: str, damage_amount: int, available_units: list):
        print(f"[GameplayController] Unit selection required for {player_name}: {damage_amount} damage")
        print(f"[GameplayController] Available units: {[strict_get(unit, 'name') for unit in available_units]}")
        # TODO: Show unit selection dialog for damage allocation
        # For now, just log the requirement

    @Slot(str, int)
    def handle_damage_allocation_completed(self, player_name: str, total_damage: int):
        print(
            f"[GameplayController] Damage allocation completed for {player_name}: {total_damage} total damage applied"
        )
        # TODO: Handle UI updates after damage allocation

    @Slot(str, list)
    def handle_counter_maneuver_request(self, location: str, opposing_armies: list):
        print(f"[GameplayController] Counter-maneuver requested at {location}")
        print(f"[GameplayController] Opposing armies: {[strict_get(army, 'name') for army in opposing_armies]}")
        # TODO: Show counter-maneuver decision dialog

    @Slot(str, dict, list, dict)
    def handle_simultaneous_maneuver_rolls_request(
        self,
        maneuvering_player: str,
        maneuvering_army: dict,
        opposing_armies: list,
        counter_responses: dict,
    ):
        print("[GameplayController] Simultaneous maneuver rolls requested")
        print(f"[GameplayController] Maneuvering player: {maneuvering_player}")
        print(f"[GameplayController] Maneuvering army: {strict_get(maneuvering_army, 'name')}")
        print(f"[GameplayController] Counter responses: {counter_responses}")
        # TODO: Show simultaneous maneuver roll dialog

    @Slot(str, int)
    def handle_terrain_direction_choice_request(self, location: str, current_face: int):
        print(f"[GameplayController] Terrain direction choice requested at {location}, current face: {current_face}")
        # TODO: Show terrain direction choice dialog

    # March step management
    @Slot(str)
    def handle_march_step_transition(self, new_step: str):
        """Handle march step transitions through proper game engine API."""
        print(f"[GameplayController] Transitioning to march step: {new_step}")
        self.game_engine.march_step_change_requested.emit(new_step)

    @Slot(str)
    def handle_action_step_transition(self, new_step: str):
        """Handle action step transitions through proper game engine API."""
        print(f"[GameplayController] Transitioning to action step: {new_step}")
        self.game_engine.action_step_change_requested.emit(new_step)

    @Slot()
    def handle_action_completed(self):
        """Handle completion of an action."""
        print("[GameplayController] Action completed, clearing action step")
        self.game_engine.action_step_change_requested.emit("")

    @Slot(bool)
    def handle_maneuver_decision_response(self, wants_to_maneuver: bool):
        """Handle player's decision about maneuvering."""
        print(f"[GameplayController] Player maneuver decision: {wants_to_maneuver}")
        self.handle_maneuver_decision(wants_to_maneuver)

        if not wants_to_maneuver:
            # Proceed directly to action decision
            self.handle_march_step_transition("DECIDE_ACTION")

    @Slot(bool)
    def handle_action_decision_response(self, wants_to_take_action: bool):
        """Handle player's decision about taking an action."""
        print(f"[GameplayController] Player action decision: {wants_to_take_action}")

        if wants_to_take_action:
            self.handle_march_step_transition("SELECT_ACTION")
        else:
            # Skip action and advance phase
            self.handle_continue_to_next_phase()

    @Slot(dict)
    def handle_maneuver_completion(self, maneuver_result: dict):
        """Handle completion of maneuver."""
        print(f"[GameplayController] Maneuver completed: {maneuver_result}")

        # Apply maneuver results through game engine
        success = self.game_engine.apply_maneuver_results(maneuver_result)

        if success:
            # Transition to action decision
            self.handle_march_step_transition("DECIDE_ACTION")
        else:
            print("[GameplayController] Maneuver failed, staying at current step")

    @Slot(str, str)
    def handle_action_completion(self, action_type: str, player_name: str):
        """Handle completion of any action type."""
        print(f"[GameplayController] {action_type} action completed by {player_name}")

        # Clear action step and advance phase
        self.handle_action_completed()
        self.handle_continue_to_next_phase()
