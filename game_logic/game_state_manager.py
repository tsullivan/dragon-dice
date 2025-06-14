from PySide6.QtCore import QObject, Signal
from typing import List, Dict, Any, Optional

class GameStateManager(QObject):
    """
    Manages the dynamic state of the game during gameplay.
    This includes army compositions, unit health, terrain control, etc.
    """
    game_state_changed = Signal() # Emitted when any significant part of the game state changes

    def __init__(self, initial_player_setup_data: List[Dict[str, Any]],
                 frontier_terrain: str, distance_rolls: List[tuple[str, int]],
                 parent: Optional[QObject] = None):
        super().__init__(parent)

        self.players_data: List[Dict[str, Any]] = [] # Will hold dynamic player data
        self.terrain_states: Dict[str, Dict[str, Any]] = {} # To store terrain control, face, etc.
        # Example: {"Frontier Terrain Name": {"controller": None, "face": 3, "minor_terrain": None}}
        #          {"Player 1 Home Terrain Name": {"controller": "Player 1", "face": 1}}

        self._initialize_state(initial_player_setup_data, frontier_terrain, distance_rolls)

    def _initialize_state(self, initial_player_setup_data: List[Dict[str, Any]],
                          frontier_terrain_name: str, distance_rolls: List[tuple[str, int]]):
        """Initializes the game state from the setup data."""
        print("GameStateManager: Initializing state...")
        self.players_data = initial_player_setup_data # Or a deep copy / transformed version
        # TODO: Populate self.players_data with more dynamic fields like unit_health, DUA, BUA, army_locations
        # TODO: Initialize self.terrain_states based on home terrains, frontier_terrain, and distance_rolls
        
        # Example initialization for terrain states
        self.terrain_states[frontier_terrain_name] = {"controller": None, "face": 1, "type": "Frontier"} # Default face
        for roll_data in distance_rolls:
            player_name, distance = roll_data
            # Find player's home terrain from initial_player_setup_data
            for p_data in initial_player_setup_data:
                if p_data["name"] == player_name:
                    home_terrain_name = p_data["home_terrain"]
                    self.terrain_states[home_terrain_name] = {"controller": player_name, "face": distance, "type": "Home"}
                    break
        print(f"GameStateManager: Initial terrain states: {self.terrain_states}")
        self.game_state_changed.emit()

    # TODO: Add methods to:
    # - Get and update unit health
    # - Move units between armies, DUA, BUA, Reserve
    # - Update army locations
    # - Update terrain control and face
    # - Get army compositions for a specific location
    # - Manage summoning pool
    # - Check victory conditions (captured terrains)
