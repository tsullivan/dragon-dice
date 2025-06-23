from PySide6.QtCore import QObject, Signal
from typing import Optional

import constants

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
        self.current_phase = constants.TURN_PHASES[self.current_phase_idx]
        self.current_march_step = ""
        self.current_action_step = "" # For sub-steps within Melee, Missile, Magic
        
        # self.initialize_turn() # Initial call might be better handled by GameEngine after all managers are set up

    def _get_current_phase_display_string(self) -> str:
        phase_display = self.current_phase.replace('_', ' ').title()
        if self.current_march_step:
            phase_display += f" - {self.current_march_step.replace('_', ' ').title()}"
        if self.current_action_step:
            phase_display += f" - {self.current_action_step.replace('_', ' ').title()}"
        return phase_display

    def initialize_turn(self):
        """Resets phase and steps for the current player's turn."""
        self.current_phase_idx = 0
        self.current_phase = constants.TURN_PHASES[self.current_phase_idx]
        self.current_march_step = ""
        self.current_action_step = ""
        print(f"TurnManager: Initializing turn for {self.player_names[self.current_player_idx]}. Phase: {self.current_phase}")
        self.current_player_changed.emit(self.player_names[self.current_player_idx])
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    def advance_phase(self):
        """Advances to the next phase or next player if all phases are complete."""
        self.current_phase_idx += 1
        if self.current_phase_idx >= len(constants.TURN_PHASES):
            self.advance_player()
        else:
            self.current_phase = constants.TURN_PHASES[self.current_phase_idx]
            self.current_march_step = "" # Reset march step when advancing phase
            self.current_action_step = "" # Reset action step
            print(f"TurnManager: Advancing phase to {self.current_phase} for {self.player_names[self.current_player_idx]}")
            self.current_phase_changed.emit(self._get_current_phase_display_string())

    def advance_player(self):
        """Advances to the next player and initializes their turn."""
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players
        print(f"TurnManager: Advancing to next player: {self.player_names[self.current_player_idx]}")
        self.initialize_turn() # This will emit player_changed and phase_changed

    # TODO: Add methods for setting/getting current step, phase, player, and display strings.
