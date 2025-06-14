from PySide6.QtCore import QObject, Signal
from typing import List, Dict, Any, Optional
import constants

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
        #     "active_army_type": "home", # Tracks which army is currently acting in a march
        #     "armies": {
        #         "home": {
        #             "name": "Home Guard", "points_value": 10, "location": "Highland",
        #             "units": [
        #                 {"id": "unit1", "name": "Goblin Infantry", "health": 1, "max_health": 1, "abilities": {"id_results": {constants.ICON_MELEE: 1}}},
        #                 {"id": "unit2", "name": "Orc Archer", "health": 2, "max_health": 2, "abilities": {"id_results": {constants.ICON_MISSILE: 1}}}
        #             ]
        #         },
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
                "active_army_type": "home", # Default active army, can be changed by maneuver/action selection
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
                    "units": self._populate_initial_units(army_details["points"], army_type_key), # Populate placeholder units
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

    def _populate_initial_units(self, army_points: int, army_type: str) -> List[Dict[str, Any]]:
        """
        Creates a list of placeholder units based on army points.
        This is a very basic placeholder. Real implementation needs dice/unit data.
        """
        units = []
        # Example: 1 unit per 2 points, very simplified
        num_units = army_points // 2
        for i in range(num_units):
            unit_name = f"{army_type.title()} Unit {i+1}"
            units.append({
                "id": f"{army_type.lower()}_unit_{i+1}",
                "name": unit_name,
                "health": 1, "max_health": 1, # Placeholder health
                "abilities": {"id_results": {constants.ICON_MELEE: 1}} # Placeholder ability
            })
        return units

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

    def get_active_army_units(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Returns the list of units for the currently active army of the specified player.
        The "active" army is determined by game flow (e.g., which army marched).
        This is a simplification; a more robust system would track the selected army.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            return []
        
        # TODO: Determine active army more dynamically (e.g., based on current march phase or selected army)
        # For now, assume 'home' army is active if nothing else is specified.
        active_army_type = player_data.get("active_army_type", "home") # Fallback to home
        return player_data.get("armies", {}).get(active_army_type, {}).get("units", [])
