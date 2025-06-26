from PySide6.QtCore import QObject, Slot
from game_logic.engine import GameEngine
import constants  # Import action constants


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
        self.game_engine.select_action(constants.ACTION_MELEE)

    @Slot()
    def handle_missile_action_selected(self):
        print("[GameplayController] Missile action selected")
        self.game_engine.select_action(constants.ACTION_MISSILE)

    @Slot()
    def handle_magic_action_selected(self):
        print("[GameplayController] Magic action selected")
        self.game_engine.select_action(constants.ACTION_MAGIC)

    @Slot()
    def handle_skip_action_selected(self):
        print("[GameplayController] Skip action selected")
        self.game_engine.select_action(constants.ACTION_SKIP)

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
        print(f"[GameplayController] Available units: {[unit.get('name', 'Unknown') for unit in available_units]}")
        # TODO: Show unit selection dialog for damage allocation
        # For now, just log the requirement
        
    @Slot(str, int)
    def handle_damage_allocation_completed(self, player_name: str, total_damage: int):
        print(f"[GameplayController] Damage allocation completed for {player_name}: {total_damage} total damage applied")
        # TODO: Handle UI updates after damage allocation
        
    @Slot(str, list)
    def handle_counter_maneuver_request(self, location: str, opposing_armies: list):
        print(f"[GameplayController] Counter-maneuver requested at {location}")
        print(f"[GameplayController] Opposing armies: {[army.get('name', 'Unknown') for army in opposing_armies]}")
        # TODO: Show counter-maneuver decision dialog
        
    @Slot(str, dict, list, dict)
    def handle_simultaneous_maneuver_rolls_request(self, maneuvering_player: str, maneuvering_army: dict, opposing_armies: list, counter_responses: dict):
        print(f"[GameplayController] Simultaneous maneuver rolls requested")
        print(f"[GameplayController] Maneuvering player: {maneuvering_player}")
        print(f"[GameplayController] Maneuvering army: {maneuvering_army.get('name', 'Unknown')}")
        print(f"[GameplayController] Counter responses: {counter_responses}")
        # TODO: Show simultaneous maneuver roll dialog
        
    @Slot(str, int)
    def handle_terrain_direction_choice_request(self, location: str, current_face: int):
        print(f"[GameplayController] Terrain direction choice requested at {location}, current face: {current_face}")
        # TODO: Show terrain direction choice dialog
