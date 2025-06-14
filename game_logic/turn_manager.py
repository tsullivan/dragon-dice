from PySide6.QtCore import QObject, Signal
from typing import Optional

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
    "AWAITING_MANEUVER_INPUT",
    "SELECT_ACTION"
]

class TurnManager(QObject):
    """Manages player turns, game phases, and march steps."""
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str) # Emits a display string for the phase/step

    def __init__(self, player_names: list[str], first_player_name: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.player_names = player_names
        self.num_players = len(player_names)
        self.current_player_idx = self.player_names.index(first_player_name) if first_player_name in self.player_names else 0
        
        self.current_phase_idx = 0
        self.current_phase = TURN_PHASES[self.current_phase_idx]
        self.current_march_step = ""
        self.current_action_step = "" # For sub-steps within Melee, Missile, Magic

    def initialize_turn(self):
        """Resets phase and steps for the current player's turn."""
        self.current_phase_idx = 0
        self.current_phase = TURN_PHASES[self.current_phase_idx]
        self.current_march_step = ""
        self.current_action_step = ""
        # TODO: Emit signals after initialization

    def advance_phase(self):
        """Advances to the next phase or next player if all phases are complete."""
        # TODO: Implement phase advancement logic
        pass

    def advance_player(self):
        """Advances to the next player and initializes their turn."""
        # TODO: Implement player advancement logic
        pass

    # TODO: Add methods for setting/getting current step, phase, player, and display strings.
