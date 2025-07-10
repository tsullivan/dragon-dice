"""
Turn State Singleton for Dragon Dice.

This singleton provides centralized turn state tracking that all managers can access
to ensure consistent turn information across the application.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class TurnStateSingleton(QObject):
    """
    Singleton class to track turn state across all game managers.
    
    This ensures that all advanced managers (DUA, BUA, Reserves, etc.) have
    access to consistent turn information without needing to pass it around.
    """
    
    _instance: Optional['TurnStateSingleton'] = None
    
    # Signals for turn state changes
    turn_changed = Signal(int)  # Emitted when turn number changes
    player_changed = Signal(str)  # Emitted when current player changes
    phase_changed = Signal(str)  # Emitted when phase changes
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        super().__init__()
        self._initialized = True
        
        # Turn state
        self._current_turn = 1
        self._current_player = ""
        self._current_phase = ""
        self._player_names = []
        
        print("TurnStateSingleton: Initialized")
    
    @classmethod
    def get_instance(cls) -> 'TurnStateSingleton':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)."""
        cls._instance = None
    
    def set_turn(self, turn_number: int):
        """Set the current turn number."""
        if self._current_turn != turn_number:
            old_turn = self._current_turn
            self._current_turn = turn_number
            print(f"TurnStateSingleton: Turn changed from {old_turn} to {turn_number}")
            self.turn_changed.emit(turn_number)
    
    def get_turn(self) -> int:
        """Get the current turn number."""
        return self._current_turn
    
    def set_current_player(self, player_name: str):
        """Set the current player."""
        if self._current_player != player_name:
            old_player = self._current_player
            self._current_player = player_name
            print(f"TurnStateSingleton: Player changed from '{old_player}' to '{player_name}'")
            self.player_changed.emit(player_name)
    
    def get_current_player(self) -> str:
        """Get the current player name."""
        return self._current_player
    
    def set_current_phase(self, phase_name: str):
        """Set the current phase."""
        if self._current_phase != phase_name:
            old_phase = self._current_phase
            self._current_phase = phase_name
            print(f"TurnStateSingleton: Phase changed from '{old_phase}' to '{phase_name}'")
            self.phase_changed.emit(phase_name)
    
    def get_current_phase(self) -> str:
        """Get the current phase name."""
        return self._current_phase
    
    def set_player_names(self, player_names: list):
        """Set the list of player names."""
        self._player_names = player_names.copy()
        print(f"TurnStateSingleton: Player names set to {player_names}")
    
    def get_player_names(self) -> list:
        """Get the list of player names."""
        return self._player_names.copy()
    
    def advance_turn(self):
        """Advance to the next turn."""
        self.set_turn(self._current_turn + 1)
    
    def get_turn_info(self) -> dict:
        """Get comprehensive turn information."""
        return {
            "turn": self._current_turn,
            "current_player": self._current_player,
            "current_phase": self._current_phase,
            "player_names": self._player_names.copy()
        }
    
    def update_from_turn_manager(self, turn_manager):
        """Update singleton state from TurnManager."""
        if hasattr(turn_manager, 'current_turn'):
            self.set_turn(turn_manager.current_turn)
        if hasattr(turn_manager, 'get_current_player_name'):
            self.set_current_player(turn_manager.get_current_player_name())
        if hasattr(turn_manager, 'current_phase'):
            self.set_current_phase(turn_manager.current_phase)
        if hasattr(turn_manager, 'player_names'):
            self.set_player_names(turn_manager.player_names)
    
    def __str__(self) -> str:
        return f"TurnState(turn={self._current_turn}, player='{self._current_player}', phase='{self._current_phase}')"
    
    def __repr__(self) -> str:
        return f"TurnStateSingleton(turn={self._current_turn}, player='{self._current_player}', phase='{self._current_phase}', players={self._player_names})"


# Convenience function to get the singleton instance
def get_turn_state() -> TurnStateSingleton:
    """Get the turn state singleton instance."""
    return TurnStateSingleton.get_instance()