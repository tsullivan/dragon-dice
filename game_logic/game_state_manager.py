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
                "reserve_pool": [],  # Available units not yet deployed (populated below)
                "reserve_area": [],  # Active game location for tactical repositioning
            }
            # Initialize armies for the player
            # 'home', 'campaign', 'horde'
            for army_type_key, army_details in p_data.get("armies", {}).items():
                location = ""
                if army_type_key == "home":
                    # Create unique home terrain name for this player
                    location = f"{player_name} {p_data['home_terrain']}"
                elif army_type_key == "campaign":
                    location = frontier_terrain_name
                elif army_type_key == "horde":
                    # Horde army is placed in opponent's home terrain
                    # For 2-player games, find the other player's home terrain
                    opponent_player_name = None
                    opponent_home_terrain_type = None
                    for other_player in initial_player_setup_data:
                        if other_player["name"] != player_name:
                            opponent_player_name = other_player["name"]
                            opponent_home_terrain_type = other_player["home_terrain"]
                            break
                    location = (
                        f"{opponent_player_name} {opponent_home_terrain_type}"
                        if opponent_player_name and opponent_home_terrain_type
                        else "Unknown Opponent Home"
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

            # Populate reserve pool with available units based on point allocation
            self._populate_reserve_pool(player_name, p_data)

        # Initialize frontier terrain with default face
        frontier_face = 1  # Default

        # Initialize terrains
        self.terrains[frontier_terrain_name] = {
            "name": frontier_terrain_name,
            "type": "Frontier",
            "face": frontier_face,  # Will be updated below if frontier roll is provided
            "controller": None,
            "armies_present": [],
        }

        for roll_data in distance_rolls:
            player_name, distance = roll_data

            # Handle frontier terrain roll
            if player_name == "__frontier__":
                self.terrains[frontier_terrain_name]["face"] = distance
                print(
                    f"GameStateManager: Set frontier terrain {frontier_terrain_name} to face {distance}"
                )
                continue

            # Handle home terrain rolls
            player_home_terrain_type = self.players[player_name]["home_terrain_name"]
            # Create unique home terrain name that matches army location naming
            unique_home_terrain_name = f"{player_name} {player_home_terrain_type}"
            self.terrains[unique_home_terrain_name] = {
                "name": unique_home_terrain_name,
                "type": "Home",
                "face": distance,
                "controller": player_name,
                "armies_present": [],
            }
        # Add unique identifiers to all armies
        self.update_army_identifiers_to_specific()

        print(
            f"GameStateManager: Initialized Players: {
              list(self.players.keys())}"
        )
        print(f"GameStateManager: Initialized Terrains: {self.terrains}")
        self.game_state_changed.emit()

    def _populate_reserve_pool(
        self, player_name: str, player_setup_data: Dict[str, Any]
    ):
        """
        Populate the reserve pool with units available for summoning/reinforcement.
        Based on Dragon Dice rules, this includes:
        1. Units from the total force allocation not deployed to armies
        2. Unassigned/excess units from force construction
        3. Special units like dragons (handled separately in summoning pool)
        """
        player_data = self.players.get(player_name)
        if not player_data:
            return

        # Calculate total points allocated to armies
        total_army_points = 0
        for army_type, army_data in player_data.get("armies", {}).items():
            total_army_points += army_data.get("points_value", 0)

        # Get force size from player setup data
        force_size = player_setup_data.get("force_size", 0)

        # Calculate reserve pool allocation (remaining points)
        reserve_points = max(0, force_size - total_army_points)

        print(
            f"GameStateManager: Player {player_name} - Force Size: {force_size}, "
            f"Army Points: {total_army_points}, Reserve Points: {reserve_points}"
        )

        # If there are reserve points, populate with available units
        if reserve_points > 0:
            # For now, create placeholder reserve units based on point allocation
            # In a full implementation, this would draw from the unit roster
            reserve_units = self._create_reserve_units(player_name, reserve_points)
            player_data["reserve_pool"].extend(reserve_units)

        # Also add any explicitly defined reserve units from setup
        if "reserve_units" in player_setup_data:
            for unit_data in player_setup_data["reserve_units"]:
                reserve_unit = UnitModel.from_dict(unit_data).to_dict()
                player_data["reserve_pool"].append(reserve_unit)

    def _create_reserve_units(
        self, player_name: str, points_available: int
    ) -> List[Dict[str, Any]]:
        """
        Create reserve units based on available points.
        This is a simplified implementation - in practice, this would use
        the unit roster to create appropriate units within the point limit.
        """
        reserve_units = []
        remaining_points = points_available

        # Create simple reserve units (1-point units for now)
        unit_count = 0
        while remaining_points > 0 and unit_count < 10:  # Cap at 10 units
            unit_count += 1
            reserve_unit = {
                "id": f"{player_name.lower().replace(' ', '_')}_reserve_{unit_count}",
                "name": f"Reserve Unit {unit_count}",
                "health": 1,
                "max_health": 1,
                "point_cost": 1,
                "unit_type": "reserve_infantry",
                "abilities": {
                    "id_results": {constants.ICON_MELEE: 1, constants.ICON_SAVE: 1}
                },
                "location": "Reserve Pool",
            }
            reserve_units.append(reserve_unit)
            remaining_points -= 1

        print(
            f"GameStateManager: Created {len(reserve_units)} reserve units for {player_name}"
        )
        return reserve_units

    def extract_terrain_type_from_location(self, location: str) -> str:
        """
        Extract the base terrain type from a location name.
        Examples:
        - "Player 1 Coastland" -> "Coastland"
        - "Swampland (Green, Yellow)" -> "Swampland (Green, Yellow)"
        """
        # If location contains a player name prefix, extract the terrain type
        import constants

        for terrain_name in constants.TERRAIN_ICONS.keys():
            if terrain_name in location:
                return terrain_name

        # Fallback: return the location as-is if no terrain type found
        return location

    def generate_army_identifier(self, player_name: str, army_type: str) -> str:
        """
        Generate a specific army identifier combining player and army type.
        Examples: "Player_1_home", "Player_2_campaign", "Gandalf_horde"
        """
        safe_player_name = player_name.replace(" ", "_").replace("'", "").lower()
        return f"{safe_player_name}_{army_type}"

    def parse_army_identifier(
        self, army_identifier: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Parse an army identifier back into player name and army type.
        Returns (player_name, army_type) or (None, None) if parsing fails.
        """
        # Handle legacy simple identifiers
        if army_identifier in ["home", "campaign", "horde"]:
            return None, army_identifier

        # Handle new specific identifiers
        parts = army_identifier.split("_")
        if len(parts) >= 2:
            army_type = parts[-1]  # Last part is army type
            player_part = "_".join(parts[:-1])  # Everything before last part

            # Find matching player by reconstructing their safe name
            for player_name in self.players.keys():
                safe_name = player_name.replace(" ", "_").replace("'", "").lower()
                if safe_name == player_part:
                    return player_name, army_type

        return None, None

    def get_army_by_identifier(
        self, army_identifier: str
    ) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Get army data by identifier. Returns (player_name, army_data) or (None, None).
        Supports both legacy ("home") and specific ("player_1_home") identifiers.
        """
        player_name, army_type = self.parse_army_identifier(army_identifier)

        if not army_type:
            return None, None

        # If no specific player parsed, try to find by context or current player
        if not player_name:
            # For legacy identifiers, we need context - this is a limitation
            # In practice, we'd need to track the current acting player
            return None, None

        player_data = self.get_player_data(player_name)
        if not player_data:
            return None, None

        army_data = player_data.get("armies", {}).get(army_type)
        return player_name, army_data

    def update_army_identifiers_to_specific(self):
        """
        Update all army references to use specific identifiers.
        This is for migrating from legacy "home" identifiers to "player_1_home" format.
        """
        for player_name, player_data in self.players.items():
            armies = player_data.get("armies", {})
            # Army keys are already specific (home, campaign, horde)
            # but we can add unique army IDs for tracking
            for army_type, army_data in armies.items():
                army_data["unique_id"] = self.generate_army_identifier(
                    player_name, army_type
                )
                army_data["player_name"] = player_name
                army_data["army_type"] = army_type

    # _parse_dragon_dice_description is removed as we are now getting structured dragon selections.

    # Army management methods
    def get_unit_health(
        self, player_name: str, army_identifier: str, unit_name: str
    ) -> Optional[int]:
        """Get the current health of a specific unit."""
        # Support both legacy and specific army identifiers
        if player_name and army_identifier in ["home", "campaign", "horde"]:
            # Legacy identifier - use provided player_name
            player_data = self.get_player_data(player_name)
            if not player_data:
                return None
            army = player_data.get("armies", {}).get(army_identifier)
        else:
            # Specific identifier - parse to get army
            parsed_player, army = self.get_army_by_identifier(army_identifier)
            if not army:
                return None

        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                return unit.get("health", 0)
        return None

    def update_unit_health(
        self, player_name: str, army_identifier: str, unit_name: str, new_health: int
    ) -> bool:
        """Update the health of a specific unit."""
        # Support both legacy and specific army identifiers
        if player_name and army_identifier in ["home", "campaign", "horde"]:
            # Legacy identifier - use provided player_name
            player_data = self.get_player_data(player_name)
            if not player_data:
                return False
            army = player_data.get("armies", {}).get(army_identifier)
            target_player = player_name
        else:
            # Specific identifier - parse to get army
            target_player, army = self.get_army_by_identifier(army_identifier)
            if not army or not target_player:
                return False

        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                unit["health"] = max(0, new_health)  # Ensure health doesn't go negative
                if unit["health"] <= 0:
                    self._move_unit_to_dua(target_player, unit)
                    army["units"].remove(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_between_armies(
        self, player_name: str, unit_name: str, from_army: str, to_army: str
    ) -> bool:
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

    def move_unit_to_bua(
        self, player_name: str, army_identifier: str, unit_name: str
    ) -> bool:
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

    def move_unit_to_reserve_area(
        self, player_name: str, army_identifier: str, unit_name: str
    ) -> bool:
        """Move a unit to the Reserve Area for tactical repositioning."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        army = player_data.get("armies", {}).get(army_identifier)
        if not army:
            return False

        for unit in army.get("units", []):
            if unit.get("name") == unit_name:
                army["units"].remove(unit)
                player_data.setdefault("reserve_area", []).append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_from_reserve_area(
        self, player_name: str, unit_name: str, target_army: str
    ) -> bool:
        """Move a unit from Reserve Area to an army."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        reserve_area = player_data.get("reserve_area", [])
        target_army_data = player_data.get("armies", {}).get(target_army)

        if not target_army_data:
            return False

        for unit in reserve_area:
            if unit.get("name") == unit_name:
                reserve_area.remove(unit)
                target_army_data["units"].append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_from_reserve_pool(
        self, player_name: str, unit_name: str, target_army: str
    ) -> bool:
        """Move a unit from Reserve Pool to an army (deployment)."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        reserve_pool = player_data.get("reserve_pool", [])
        target_army_data = player_data.get("armies", {}).get(target_army)

        if not target_army_data:
            return False

        for unit in reserve_pool:
            if unit.get("name") == unit_name:
                reserve_pool.remove(unit)
                target_army_data["units"].append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def update_army_location(
        self, player_name: str, army_identifier: str, location: str
    ) -> bool:
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

    def update_terrain_control(
        self, terrain_name: str, controlling_player: Optional[str]
    ) -> bool:
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
                    armies_at_location.append(
                        {"player": player_name, "army_id": army_id, "army": army}
                    )
        return armies_at_location

    def get_reserve_pool(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the reserve pool (available for deployment) for a player."""
        player_data = self.get_player_data(player_name)
        return player_data.get("reserve_pool", []) if player_data else []

    def get_reserve_area(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the reserve area (tactical repositioning) for a player."""
        player_data = self.get_player_data(player_name)
        return player_data.get("reserve_area", []) if player_data else []

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
                player_terrain_counts[controlling_player] = (
                    player_terrain_counts.get(controlling_player, 0) + 1
                )

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

    def set_active_army(self, player_name: str, army_type: str) -> bool:
        """Set the active army for a player based on current game context."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        # Validate that the army type exists
        if army_type not in player_data.get("armies", {}):
            return False

        player_data["active_army_type"] = army_type
        self.game_state_changed.emit()
        return True

    def determine_active_army_by_location(
        self, player_name: str, current_location: str
    ) -> Optional[str]:
        """
        Determine which army should be active based on the current game location.
        Returns the army type that should be active.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None

        armies = player_data.get("armies", {})

        # Find armies at the current location
        armies_at_location = []
        for army_type, army_data in armies.items():
            if army_data.get("location") == current_location:
                armies_at_location.append(army_type)

        # If only one army at location, it's the active one
        if len(armies_at_location) == 1:
            return armies_at_location[0]

        # If multiple armies, prefer by priority: home > campaign > horde
        priority_order = ["home", "campaign", "horde"]
        for army_type in priority_order:
            if army_type in armies_at_location:
                return army_type

        return None

    def determine_active_army_by_phase(
        self, player_name: str, current_phase: str, current_location: str = None
    ) -> Optional[str]:
        """
        Determine which army should be active based on the current game phase and context.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None

        armies = player_data.get("armies", {})

        # Phase-specific logic
        if current_phase in [constants.PHASE_FIRST_MARCH, constants.PHASE_SECOND_MARCH]:
            # During march phases, determine by location if provided
            if current_location:
                return self.determine_active_army_by_location(
                    player_name, current_location
                )
            # Otherwise, use current active army
            return player_data.get("active_army_type", "home")

        elif current_phase == constants.PHASE_DRAGON_ATTACK:
            # Dragons can attack any army, but usually home terrain
            home_terrain = player_data.get("home_terrain_name")
            if home_terrain:
                return self.determine_active_army_by_location(player_name, home_terrain)

        elif current_phase == constants.PHASE_RESERVES:
            # Reserve phase can involve any army
            return player_data.get("active_army_type", "home")

        # Default to current active army or home
        return player_data.get("active_army_type", "home")

    def get_active_army_type(self, player_name: str) -> Optional[str]:
        """Get the currently active army type for a player."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None
        return player_data.get("active_army_type", "home")

    def get_active_army_data(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get the data for the currently active army."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None

        active_army_type = self.get_active_army_type(player_name)
        if not active_army_type:
            return None

        return player_data.get("armies", {}).get(active_army_type)

    def get_active_army_units(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Returns the list of units for the currently active army of the specified player.
        The "active" army is determined by game flow context.
        """
        active_army = self.get_active_army_data(player_name)
        return active_army.get("units", []) if active_army else []

    def get_all_armies_at_location(
        self, player_name: str, location: str
    ) -> List[Dict[str, Any]]:
        """Get all armies for a player at a specific location."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return []

        armies_at_location = []
        for army_type, army_data in player_data.get("armies", {}).items():
            if army_data.get("location") == location:
                armies_at_location.append(
                    {
                        "army_type": army_type,
                        "army_data": army_data,
                        "unique_id": army_data.get(
                            "unique_id", f"{player_name}_{army_type}"
                        ),
                    }
                )

        return armies_at_location
