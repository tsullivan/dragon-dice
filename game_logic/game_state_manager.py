from PySide6.QtCore import QObject, Signal
from typing import List, Dict, Any, Optional
import constants

# For type hinting and potential reconstruction
from models.army_model import ArmyModel
from models.die_model import DieModel  # Import DieModel

# For type hinting and potential reconstruction
from models.unit_model import UnitModel


class GameStateManager(QObject):
    """
    Manages the dynamic state of the game during gameplay.
    This includes army compositions, unit health, terrain control, etc.
    """

    game_state_changed = (
        Signal()
    )  # Emitted when any significant part of the game state changes

    def __init__(
        self,
        initial_player_setup_data: List[Dict[str, Any]],
        frontier_terrain: str,
        distance_rolls: List[tuple[str, int]],
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        # Keep original setup for reference
        self.initial_player_setup_data = initial_player_setup_data

        # Dynamic game state
        self.players: Dict[str, Dict[str, Any]] = {}  # Keyed by player name
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
        #     "selected_dragons": ["Red Dragon", "Blue Dragon"], # New player-level field
        #     "buried_unit_area": [],
        #     "reserve_pool": [] # Units available to be brought into reserves
        # }

        self.terrains: Dict[str, Dict[str, Any]] = {}  # Keyed by terrain name
        # Example terrain entry:
        # "Frontier Name": {"name": "Frontier Name", "type": "Frontier", "face": 3, "controller": None, "armies_present": ["P1_Campaign", "P2_Campaign"]}
        # "Player 1 Home": {"name": "Player 1 Home", "type": "Home", "face": 1, "controller": "Player 1", "armies_present": ["P1_Home"]}

        self._initialize_state(
            initial_player_setup_data, frontier_terrain, distance_rolls
        )

    def _initialize_state(
        self,
        initial_player_setup_data: List[Dict[str, Any]],
        frontier_terrain_name: str,
        distance_rolls: List[tuple[str, int]],
    ):
        """Initializes the game state from the setup data."""
        print("GameStateManager: Initializing state...")

        # Initialize players
        for p_data in initial_player_setup_data:
            player_name = p_data["name"]
            self.players[player_name] = {
                "name": player_name,
                "home_terrain_name": p_data["home_terrain"],
                # Default active army, can be changed by maneuver/action selection
                "active_army_type": "home",
                "armies": {},  # Will be populated below
                # Store selected dragons
                "selected_dragons": p_data.get("selected_dragons", []),
                "captured_terrains_count": 0,
                "dead_unit_area": [],
                "buried_unit_area": [],
                "reserve_pool": [],  # TODO: Populate with actual units based on point value later
            }
            # Initialize armies for the player
            # 'home', 'campaign', 'horde'
            for army_type_key, army_details in p_data.get("armies", {}).items():
                location = ""
                if army_type_key == "home":
                    location = p_data["home_terrain"]
                elif army_type_key == "campaign":
                    location = frontier_terrain_name
                elif army_type_key == "horde":
                    # Horde location is more complex, depends on opponent. Placeholder for now.
                    # For simplicity, we might just mark it as "Horde" and resolve during gameplay.
                    location = (
                        "Horde Staging"  # Needs actual opponent home terrain later
                    )
                # dragon_dice_description = army_details.get("dragon_dice_description", "") # Removed
                # parsed_dice = self._parse_dragon_dice_description(dragon_dice_description) # Removed
                self.players[player_name]["armies"][army_type_key] = {
                    "name": army_details["name"],
                    "points_value": army_details.get(
                        "allocated_points", army_details.get("points", 0)
                    ),
                    "units": [
                        UnitModel.from_dict(u_data).to_dict()
                        for u_data in army_details.get("units", [])
                    ],
                    "location": location,
                }

        # Initialize terrains
        self.terrains[frontier_terrain_name] = {
            # Default face, will be updated by distance roll if applicable
            "name": frontier_terrain_name,
            "type": "Frontier",
            "face": 1,
            "controller": None,
            "armies_present": [],
        }
        for roll_data in distance_rolls:
            player_name, distance = roll_data
            player_home_terrain = self.players[player_name]["home_terrain_name"]
            self.terrains[player_home_terrain] = {
                "name": player_home_terrain,
                "type": "Home",
                "face": distance,
                "controller": player_name,
                "armies_present": [],
            }
        print(
            f"GameStateManager: Initialized Players: {
              list(self.players.keys())}"
        )
        print(f"GameStateManager: Initialized Terrains: {self.terrains}")
        self.game_state_changed.emit()

    # _parse_dragon_dice_description is removed as we are now getting structured dragon selections.

    # Army management methods
    def get_unit_health(self, player_name: str, army_identifier: str, unit_name: str) -> Optional[int]:
        """Get the current health of a specific unit."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None
        
        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return None
        
        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                return unit.get("health", 0)
        return None
    
    def update_unit_health(self, player_name: str, army_identifier: str, unit_name: str, new_health: int) -> bool:
        """Update the health of a specific unit."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return False
        
        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                unit["health"] = max(0, new_health)  # Ensure health doesn't go negative
                if unit["health"] <= 0:
                    self._move_unit_to_dua(player_name, unit)
                    army["units"].remove(unit)
                self.game_state_changed.emit()
                return True
        return False
    
    def move_unit_between_armies(self, player_name: str, unit_name: str, from_army: str, to_army: str) -> bool:
        """Move a unit from one army to another."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        armies = player_data.get("armies", {})
        source_army = armies.get(from_army)
        target_army = armies.get(to_army)
        
        if not source_army or not target_army:
            return False
        
        # Find and remove unit from source army
        unit_to_move = None
        for unit in source_army.get("units", []):
            if unit.get("name") == unit_name:
                unit_to_move = unit
                break
        
        if unit_to_move:
            source_army["units"].remove(unit_to_move)
            target_army["units"].append(unit_to_move)
            self.game_state_changed.emit()
            return True
        return False
    
    def _move_unit_to_dua(self, player_name: str, unit: Dict[str, Any]):
        """Move a defeated unit to the Dead Unit Area (DUA)."""
        player_data = self.get_player_data(player_name)
        if player_data:
            player_data.setdefault("dead_unit_area", []).append(unit)
    
    def move_unit_to_bua(self, player_name: str, army_identifier: str, unit_name: str) -> bool:
        """Move a unit to the Buried Unit Area (BUA)."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return False
        
        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                army["units"].remove(unit)
                player_data.setdefault("buried_unit_area", []).append(unit)
                self.game_state_changed.emit()
                return True
        return False
    
    def move_unit_to_reserve(self, player_name: str, army_identifier: str, unit_name: str) -> bool:
        """Move a unit to the Reserve Pool."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return False
        
        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                army["units"].remove(unit)
                player_data.setdefault("reserve_pool", []).append(unit)
                self.game_state_changed.emit()
                return True
        return False
    
    def update_army_location(self, player_name: str, army_identifier: str, location: str) -> bool:
        """Update the location of an army."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return False
        
        army["location"] = location
        self.game_state_changed.emit()
        return True
    
    def update_terrain_control(self, terrain_name: str, controlling_player: Optional[str]) -> bool:
        """Update which player controls a terrain."""
        terrain = self.get_terrain_data(terrain_name)
        if not terrain:
            return False
        
        terrain["controlling_player"] = controlling_player
        self.game_state_changed.emit()
        return True
    
    def update_terrain_face(self, terrain_name: str, face: str) -> bool:
        """Update the face-up terrain."""
        terrain = self.get_terrain_data(terrain_name)
        if not terrain:
            return False
        
        terrain["current_face"] = face
        self.game_state_changed.emit()
        return True
    
    def get_armies_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all armies at a specific location."""
        armies_at_location = []
        for player_name, player_data in self.players.items():
            for army_id, army in player_data.get("armies", {}).items():
                if army.get("location") == location:
                    armies_at_location.append({
                        "player": player_name,
                        "army_id": army_id,
                        "army": army
                    })
        return armies_at_location
    
    def get_summoning_pool(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the summoning pool for a player."""
        player_data = self.get_player_data(player_name)
        return player_data.get("summoning_pool", []) if player_data else []
    
    def add_to_summoning_pool(self, player_name: str, unit: Dict[str, Any]) -> bool:
        """Add a unit to the summoning pool."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False
        
        player_data.setdefault("summoning_pool", []).append(unit)
        self.game_state_changed.emit()
        return True
    
    def check_victory_conditions(self) -> Optional[str]:
        """Check if any player has won by capturing required terrains."""
        # Simple victory condition: control majority of terrains
        player_terrain_counts = {}
        total_terrains = len(self.terrains)
        
        for terrain_data in self.terrains.values():
            controlling_player = terrain_data.get("controlling_player")
            if controlling_player:
                player_terrain_counts[controlling_player] = player_terrain_counts.get(controlling_player, 0) + 1
        
        # Check if any player controls more than half the terrains
        for player, count in player_terrain_counts.items():
            if count > total_terrains // 2:
                return player
        
        return None

    def apply_damage_to_units(
        self, player_name: str, army_identifier: str, damage_amount: int
    ):
        """
        Applies damage to units in a specific army.
        This is a placeholder and needs actual unit selection/damage distribution logic.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            print(
                f"GameStateManager: Player {
                  player_name} not found for applying damage."
            )
            return

        # TODO: The army_identifier needs to be more specific, e.g., "home", "campaign", or a unique ID.
        # For now, let's assume army_identifier refers to the 'active_army_type' if it's generic,
        # or we need a way to map it to the correct army key ('home', 'campaign', 'horde').
        # This is a simplification.
        target_army_key = player_data.get(
            "active_army_type", "home"
        )  # Fallback, needs improvement
        if (
            army_identifier != "Placeholder_Defending_Army_ID"
            and army_identifier in player_data.get("armies", {})
        ):
            target_army_key = army_identifier

        army = player_data.get("armies", {}).get(target_army_key)
        if not army:
            print(
                f"GameStateManager: Army '{
                  target_army_key}' for player {player_name} not found."
            )
            return

        print(
            f"GameStateManager: Applying {damage_amount} damage to {
              player_name}'s {army.get('name', target_army_key)} army."
        )

        remaining_damage = damage_amount
        units_affected = False
        # Iterate over a copy in case we remove items
        for unit in list(army["units"]):
            if remaining_damage <= 0:
                break

            damage_to_unit = min(remaining_damage, unit["health"])
            unit["health"] -= damage_to_unit
            remaining_damage -= damage_to_unit
            units_affected = True
            print(
                f"GameStateManager: Unit {unit['name']} took {
                  damage_to_unit} damage, health now {unit['health']}."
            )

            if unit["health"] <= 0:
                print(f"GameStateManager: Unit {unit['name']} defeated.")
                army["units"].remove(unit)
                player_data.setdefault("dead_unit_area", []).append(unit)

        if units_affected:
            self.game_state_changed.emit()

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
        active_army_type = player_data.get(
            "active_army_type", "home"
        )  # Fallback to home
        return player_data.get("armies", {}).get(active_army_type, {}).get("units", [])
