from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from models.game_phase_model import get_turn_phases


class TurnManager(QObject):
    """Manages player turns, game phases, and march steps."""

    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)  # Emits a display string for the phase/step
    turn_changed = Signal(int)  # Emitted when turn number changes

    def __init__(
        self,
        player_names: List[str],
        first_player_name: str,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.player_names = player_names
        self.num_players = len(player_names)
        self.current_player_idx = (
            self.player_names.index(first_player_name) if first_player_name in self.player_names else 0
        )

        # Start with First March phase for the very first turn of the game
        self.current_phase_idx = get_turn_phases().index("FIRST_MARCH")
        self.current_phase = "FIRST_MARCH"
        self.current_march_step = ""
        self.current_action_step = ""  # For sub-steps within Melee, Missile, Magic
        self.is_first_turn_of_game = True  # Track if this is the very first turn
        self.current_turn = 1  # Track the current turn number

        # self.initialize_turn() # Initial call might be better handled by GameEngine after all managers are set up

    def _get_current_phase_display_string(self) -> str:
        phase_display = self.current_phase.replace("_", " ").title()
        if self.current_march_step:
            phase_display += f" - {self.current_march_step.replace('_', ' ').title()}"
        if self.current_action_step:
            phase_display += f" - {self.current_action_step.replace('_', ' ').title()}"
        return phase_display

    def initialize_turn(self):
        """Resets phase and steps for the current player's turn."""
        if self.is_first_turn_of_game:
            # Keep the First March phase for the first turn
            self.is_first_turn_of_game = False
            print(f"TurnManager: Starting FIRST TURN with First March for {self.player_names[self.current_player_idx]}")
        else:
            # Dragon Dice Rule: Each player's turn starts with First March
            self.current_phase_idx = get_turn_phases().index("FIRST_MARCH")
            self.current_phase = "FIRST_MARCH"
            print(
                f"TurnManager: Initializing turn for {self.player_names[self.current_player_idx]}. Phase: {self.current_phase}"
            )

        self.current_march_step = ""
        self.current_action_step = ""
        self.current_player_changed.emit(self.player_names[self.current_player_idx])
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    def advance_phase(self):
        """Advances to the next phase or next player based on Dragon Dice rules."""
        # Normal phase advancement within a player's turn
        self.current_phase_idx += 1
        if self.current_phase_idx >= len(get_turn_phases()):
            # All phases complete, advance to next player
            print(f"TurnManager: Completed {self.player_names[self.current_player_idx]}'s turn (all phases complete)")
            self.advance_player()
        else:
            self.current_phase = get_turn_phases()[self.current_phase_idx]
            self.current_march_step = ""  # Reset march step when advancing phase
            self.current_action_step = ""  # Reset action step
            print(
                f"TurnManager: Advancing phase to {self.current_phase} for {self.player_names[self.current_player_idx]}"
            )
            self.current_phase_changed.emit(self._get_current_phase_display_string())

    def skip_to_next_phase_group(self):
        """Skip to the next major phase group (e.g., from First March to Species Abilities)."""
        current_phase = self.current_phase

        if current_phase == "FIRST_MARCH":
            # Skip Second March and go to Species Abilities
            self.current_phase_idx = get_turn_phases().index("SPECIES_ABILITIES")
            self.current_phase = "SPECIES_ABILITIES"
            self.current_march_step = ""
            self.current_action_step = ""
            print(f"TurnManager: Skipping Second March, advancing to {self.current_phase}")
            self.current_phase_changed.emit(self._get_current_phase_display_string())
        elif current_phase == "SECOND_MARCH":
            # Normal advancement after Second March
            self.advance_phase()
        else:
            # For other phases, just advance normally
            self.advance_phase()

    def advance_player(self):
        """Advances to the next player and initializes their turn."""
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players

        # If we've cycled through all players, increment the turn number
        if self.current_player_idx == 0:
            self.advance_turn()

        print(f"TurnManager: Advancing to next player: {self.player_names[self.current_player_idx]}")
        self.initialize_turn()  # This will emit player_changed and phase_changed

    # Getter methods
    def get_current_player(self) -> str:
        """Get the current player's name."""
        return self.player_names[self.current_player_idx]

    def get_current_phase(self) -> str:
        """Get the current phase."""
        return self.current_phase

    def get_current_march_step(self) -> str:
        """Get the current march step."""
        return self.current_march_step

    def get_current_action_step(self) -> str:
        """Get the current action step."""
        return self.current_action_step

    def get_phase_display_string(self) -> str:
        """Get the formatted display string for the current phase/step."""
        return self._get_current_phase_display_string()

    def set_phase(self, phase_name: str) -> None:
        """Set the current phase directly (for testing purposes)."""
        turn_phases = get_turn_phases()
        if phase_name not in turn_phases:
            raise ValueError(f"Invalid phase name: {phase_name}. Valid phases: {turn_phases}")

        self.current_phase_idx = turn_phases.index(phase_name)
        self.current_phase = phase_name
        self.current_march_step = ""
        self.current_action_step = ""
        print(f"TurnManager: Setting phase to {phase_name} for {self.player_names[self.current_player_idx]}")
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    # Setter methods
    def set_march_step(self, step: str):
        """Set the current march step and emit phase change signal."""
        self.current_march_step = step
        print(f"TurnManager: Setting march step to {step}")
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    def set_action_step(self, step: str):
        """Set the current action step and emit phase change signal."""
        self.current_action_step = step
        print(f"TurnManager: Setting action step to {step}")
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    def clear_march_step(self):
        """Clear the current march step."""
        self.current_march_step = ""
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    def clear_action_step(self):
        """Clear the current action step."""
        self.current_action_step = ""
        self.current_phase_changed.emit(self._get_current_phase_display_string())

    # Utility methods
    def is_march_phase(self) -> bool:
        """Check if current phase is a march phase."""
        return self.current_phase in [
            "FIRST_MARCH",
            "SECOND_MARCH",
        ]

    def get_player_index(self) -> int:
        """Get the current player's index."""
        return self.current_player_idx

    def get_all_players(self) -> List[str]:
        """Get list of all player names."""
        return self.player_names.copy()

    def advance_turn(self):
        """Advance to the next turn number."""
        old_turn = self.current_turn
        self.current_turn += 1
        print(f"TurnManager: Turn advanced from {old_turn} to {self.current_turn}")
        self.turn_changed.emit(self.current_turn)

    def get_current_turn(self) -> int:
        """Get the current turn number."""
        return self.current_turn

    def set_current_turn(self, turn_number: int):
        """Set the current turn number."""
        if self.current_turn != turn_number:
            old_turn = self.current_turn
            self.current_turn = turn_number
            print(f"TurnManager: Turn changed from {old_turn} to {turn_number}")
            self.turn_changed.emit(turn_number)

    def get_current_player_name(self) -> str:
        """Get the current player's name (alias for get_current_player)."""
        return self.get_current_player()

    def get_turn_info(self) -> dict:
        """Get comprehensive turn information."""
        return {
            "turn": self.current_turn,
            "current_player": self.get_current_player(),
            "current_phase": self.current_phase,
            "player_names": self.player_names.copy(),
            "march_step": self.current_march_step,
            "action_step": self.current_action_step,
        }
