from PySide6.QtCore import QObject, Slot
from game_logic.engine import GameEngine # Or AppDataModel if it holds the engine
import constants # Import action constants

class GameplayController(QObject):
    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine

    @Slot(bool)
    def handle_maneuver_decision(self, wants_to_maneuver: bool):
        # Logic that was previously a direct lambda or method in the view
        # or MainWindow
        print(f"[GameplayController] Handling maneuver: {wants_to_maneuver}")
        self.game_engine.decide_maneuver(wants_to_maneuver)
        # The controller could also emit signals if the MainWindow or other
        # components need to react to the outcome of this action.

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
