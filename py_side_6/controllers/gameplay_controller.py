from PySide6.QtCore import QObject, Slot
from ..engine import GameEngine # Or AppDataModel if it holds the engine

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
