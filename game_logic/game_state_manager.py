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
        self.initial_player_setup_data = initial_player_setup_data # Keep original setup for reference

        # Dynamic game state
        self.players: Dict[str, Dict[str, Any]] = {} # Keyed by player name
        # Example player entry:
        # "Player 1": {
        #     "name": "Player 1",
        #     "home_terrain_name": "Highland",
        #     "armies": {
        #         "home": {"name": "Home Guard", "points_value": 10, "units": [], "location": "Highland"},
        #         "campaign": {"name": "Vanguard", "points_value": 10, "units": [], "location": "Frontier"},
        #         "horde": {"name": "Raiders", "points_value": 4, "units": [], "location": "OpponentHome"}
        #     },
        #     "captured_terrains_count": 0,
        #     "dead_unit_area": [],
        #     "buried_unit_area": [],
        #     "reserve_pool": [] # Units available to be brought into reserves
        # }

        self.terrains: Dict[str, Dict[str, Any]] = {} # Keyed by terrain name
        # Example terrain entry:
        # "Frontier Name": {"name": "Frontier Name", "type": "Frontier", "face": 3, "controller": None, "armies_present": ["P1_Campaign", "P2_Campaign"]}
        # "Player 1 Home": {"name": "Player 1 Home", "type": "Home", "face": 1, "controller": "Player 1", "armies_present": ["P1_Home"]}

        self._initialize_state(initial_player_setup_data, frontier_terrain, distance_rolls)

    def _initialize_state(self, initial_player_setup_data: List[Dict[str, Any]],
                          frontier_terrain_name: str, distance_rolls: List[tuple[str, int]]):
        """Initializes the game state from the setup data."""
        print("GameStateManager: Initializing state...")

        # Initialize players
        for p_data in initial_player_setup_data:
            player_name = p_data["name"]
            self.players[player_name] = {
                "name": player_name,
                "home_terrain_name": p_data["home_terrain"],
                "armies": {}, # Will be populated below
                "captured_terrains_count": 0,
                "dead_unit_area": [],
                "buried_unit_area": [],
                "reserve_pool": [] # TODO: Populate with actual units based on point value later
            }
            # Initialize armies for the player
            for army_type_key, army_details in p_data.get("armies", {}).items(): # 'home', 'campaign', 'horde'
                location = ""
                if army_type_key == "home":
                    location = p_data["home_terrain"]
                elif army_type_key == "campaign":
                    location = frontier_terrain_name
                elif army_type_key == "horde":
                    # Horde location is more complex, depends on opponent. Placeholder for now.
                    # For simplicity, we might just mark it as "Horde" and resolve during gameplay.
                    location = "Horde Staging" # Needs actual opponent home terrain later
                
                self.players[player_name]["armies"][army_type_key] = {
                    "name": army_details["name"],
                    "points_value": army_details["points"],
                    "units": [], # TODO: Populate with actual units later
                    "location": location
                }

        # Initialize terrains
        self.terrains[frontier_terrain_name] = {
            "name": frontier_terrain_name, "type": "Frontier", "face": 1, # Default face, will be updated by distance roll if applicable
            "controller": None, "armies_present": []
        }
        for roll_data in distance_rolls:
            player_name, distance = roll_data
            player_home_terrain = self.players[player_name]["home_terrain_name"]
            self.terrains[player_home_terrain] = {
                "name": player_home_terrain, "type": "Home", "face": distance,
                "controller": player_name, "armies_present": []
            }
        print(f"GameStateManager: Initialized Players: {list(self.players.keys())}")
        print(f"GameStateManager: Initialized Terrains: {self.terrains}")
        self.game_state_changed.emit()

    # TODO: Add methods to:
    # - Get and update unit health
    # - Move units between armies, DUA, BUA, Reserve
    # - Update army locations
    # - Update terrain control and face
    # - Get army compositions for a specific location
    # - Manage summoning pool
    # - Check victory conditions (captured terrains)

    def get_player_data(self, player_name: str) -> Optional[Dict[str, Any]]:
        return self.players.get(player_name)

    def get_all_players_data(self) -> Dict[str, Dict[str, Any]]:
        return self.players

    def get_terrain_data(self, terrain_name: str) -> Optional[Dict[str, Any]]:
        return self.terrains.get(terrain_name)

    def get_all_terrain_data(self) -> Dict[str, Dict[str, Any]]:
        return self.terrains

    def get_player_home_terrain_name(self, player_name: str) -> Optional[str]:
        player = self.get_player_data(player_name)
        return player.get("home_terrain_name") if player else None
