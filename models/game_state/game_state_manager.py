from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

# For type hinting and potential reconstruction
# For type hinting and potential reconstruction
from models.unit_model import UnitModel
from utils.field_access import strict_get, strict_get_optional


# Custom exceptions for game state management
class GameStateError(Exception):
    """Base exception for game state errors."""

    pass


class PlayerNotFoundError(GameStateError):
    """Raised when a player cannot be found in the game state."""

    def __init__(self, player_name: str):
        super().__init__(f"Player '{player_name}' not found in game state")
        self.player_name = player_name


class ArmyNotFoundError(GameStateError):
    """Raised when an army cannot be found for a player."""

    def __init__(self, player_name: str, army_type: str):
        super().__init__(f"Army '{army_type}' not found for player '{player_name}'")
        self.player_name = player_name
        self.army_type = army_type


class TerrainNotFoundError(GameStateError):
    """Raised when terrain data cannot be found."""

    def __init__(self, terrain_name: str):
        super().__init__(f"Terrain '{terrain_name}' not found in game state")
        self.terrain_name = terrain_name


class UnitNotFoundError(GameStateError):
    """Raised when a unit cannot be found in an army."""

    def __init__(self, unit_name: str, army_identifier: str):
        super().__init__(f"Unit '{unit_name}' not found in army '{army_identifier}'")
        self.unit_name = unit_name
        self.army_identifier = army_identifier


class InvalidArmyIdentifierError(GameStateError):
    """Raised when an army identifier cannot be parsed."""

    def __init__(self, army_identifier: str):
        super().__init__(f"Invalid army identifier: '{army_identifier}'. Expected format: 'player_name_army_type'")
        self.army_identifier = army_identifier


class GameStateManager(QObject):
    """
    Manages the dynamic state of the game during gameplay.
    This includes army compositions, unit health, terrain control, etc.
    """

    game_state_changed = Signal()  # Emitted when any significant part of the game state changes

    def __init__(
        self,
        initial_player_setup_data: List[Dict[str, Any]],
        frontier_terrain: str,
        distance_rolls: List[Tuple[str, int]],
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
        # "Player 1 Home": {"name": "Player 1 Home", "type": "Home", "face": 1, "controller": None, "armies_present": ["P1_Home"]}

        self._initialize_state(initial_player_setup_data, frontier_terrain, distance_rolls)

    def _initialize_state(
        self,
        initial_player_setup_data: List[Dict[str, Any]],
        frontier_terrain_name: str,
        distance_rolls: List[Tuple[str, int]],
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
                "selected_dragons": strict_get(p_data, "selected_dragons"),
                "captured_terrains_count": 0,
                "dead_unit_area": [],
                "buried_unit_area": [],
                "reserve_pool": [],  # Available units not yet deployed (populated below)
                "reserve_area": [],  # Active game location for tactical repositioning
            }
            # Initialize armies for the player
            # 'home', 'campaign', 'horde'
            for army_type_key, army_details in strict_get(p_data, "armies").items():
                # Use provided location if specified, otherwise use default logic
                location = army_details.get("location")

                if not location:
                    # Apply default location logic only if no location provided
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
                self.players[player_name]["armies"][army_type_key] = {
                    "name": army_details["name"],
                    "points_value": strict_get(army_details, "allocated_points"),
                    "units": [UnitModel.from_dict(u_data).to_dict() for u_data in strict_get(army_details, "units")],
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
                print(f"GameStateManager: Set frontier terrain {frontier_terrain_name} to face {distance}")
                continue

            # Handle home terrain rolls
            player_home_terrain_type = self.players[player_name]["home_terrain_name"]
            # Create unique home terrain name that matches army location naming
            unique_home_terrain_name = f"{player_name} {player_home_terrain_type}"
            self.terrains[unique_home_terrain_name] = {
                "name": unique_home_terrain_name,
                "type": "Home",
                "face": distance,
                "controller": None,  # Terrains are only controlled when at eighth face
                "armies_present": [],
            }
        # Add unique identifiers to all armies
        self.update_army_identifiers_to_specific()

        print(f"GameStateManager: Initialized Players: {list(self.players.keys())}")
        print(f"GameStateManager: Initialized Terrains: {self.terrains}")
        self.game_state_changed.emit()

    def _populate_reserve_pool(self, player_name: str, player_setup_data: Dict[str, Any]):
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
        for _army_type, army_data in strict_get(player_data, "armies").items():
            total_army_points += strict_get(army_data, "points_value")

        # Get force size from player setup data
        force_size = strict_get(player_setup_data, "force_size")

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

    def _create_reserve_units(self, player_name: str, points_available: int) -> List[Dict[str, Any]]:
        """
        Create reserve units based on available points using actual unit roster.
        Uses a simplified cost system based on unit health (1 health = 1 point).
        """
        from models.app_data_model import AppDataModel
        from models.unit_roster_model import UnitRosterModel

        reserve_units = []
        remaining_points = points_available
        # Create a minimal app data model for unit roster
        app_data = AppDataModel()
        unit_roster = UnitRosterModel(app_data)

        # Get all available unit types
        available_units = []
        for species_units in unit_roster.get_available_unit_types_by_species().values():
            available_units.extend(species_units)

        # Sort by health (using health as cost proxy)
        available_units.sort(
            key=lambda u: unit_roster.get_unit_definition(u["id"])
            and unit_roster.get_unit_definition(u["id"])["max_health"]
            or 0
        )

        unit_count = 0
        unit_cycle_index = 0  # Track which units we've used for variety

        while remaining_points > 0 and unit_count < 15:  # Cap at 15 units
            # Find affordable units and cycle through them for variety
            affordable_units = [
                u
                for u in available_units
                if unit_roster.get_unit_definition(u["id"])
                and unit_roster.get_unit_definition(u["id"])["max_health"] <= remaining_points
            ]

            if not affordable_units:
                break  # No units fit within remaining points

            # Cycle through affordable units for variety
            selected_unit_info = affordable_units[unit_cycle_index % len(affordable_units)]
            selected_unit_id = selected_unit_info["id"]
            unit_cycle_index += 1

            unit_def = unit_roster.get_unit_definition(selected_unit_id)
            if not unit_def:
                continue
            unit_cost = unit_def["max_health"]

            unit_count += 1
            instance_id = f"{player_name.lower().replace(' ', '_')}_reserve_{unit_count}"

            # Create unit instance using roster
            unit_instance = unit_roster.create_unit_instance(
                selected_unit_id, instance_id, f"Reserve {unit_def['display_name']}"
            )

            if unit_instance:
                # Convert to dict format expected by game state
                reserve_unit = {
                    "id": unit_instance.unit_id,
                    "name": unit_instance.name,
                    "health": unit_instance.health,
                    "max_health": unit_instance.max_health,
                    "point_cost": unit_cost,
                    "unit_type": unit_instance.unit_type,
                    "faces": unit_instance.get_face_names(),  # Use faces instead of abilities
                    "location": "Reserve Pool",
                }
                reserve_units.append(reserve_unit)
                remaining_points -= unit_cost

        print(
            f"GameStateManager: Created {len(reserve_units)} reserve units for {player_name} "
            f"({points_available - remaining_points}/{points_available} points used)"
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
        from models.terrain_model import TERRAIN_DATA

        location_upper = location.upper()

        # Look for terrain prefixes (like HIGHLAND, COASTLAND, etc.)
        terrain_prefixes = set()
        for terrain_name in TERRAIN_DATA:
            if "_" in terrain_name:
                prefix = terrain_name.split("_")[0]
                terrain_prefixes.add(prefix)

        # Check if any terrain prefix matches a word in the location
        location_words = location.split()
        for word in location_words:
            word_upper = word.upper()
            if word_upper in terrain_prefixes:
                return word  # Return in original case

        # Fallback: check for exact terrain matches
        for terrain_name in TERRAIN_DATA:
            if terrain_name in location_upper:
                # Return the terrain name in its original case from the location string
                # Find the actual terrain name in the location (case-insensitive)
                for word in location_words:
                    if word.upper() == terrain_name:
                        return word
                # If not found as a separate word, return the uppercase version
                return terrain_name

        # No fallback - raise error if terrain type cannot be determined
        raise TerrainNotFoundError(f"Cannot extract terrain type from location: {location}")

    def generate_army_identifier(self, player_name: str, army_type: str) -> str:
        """
        Generate a specific army identifier combining player and army type.
        Examples: "Player_1_home", "Player_2_campaign", "Gandalf_horde"
        """
        safe_player_name = player_name.replace(" ", "_").replace("'", "").lower()
        return f"{safe_player_name}_{army_type}"

    def parse_army_identifier(self, army_identifier: str) -> Tuple[str, str]:
        """
        Parse an army identifier back into player name and army type.
        Returns (player_name, army_type) or raises InvalidArmyIdentifierError.
        """
        parts = army_identifier.split("_")
        if len(parts) < 2:
            raise InvalidArmyIdentifierError(army_identifier)

        army_type = parts[-1]  # Last part is army type
        if army_type not in ["home", "campaign", "horde"]:
            raise InvalidArmyIdentifierError(army_identifier)

        player_part = "_".join(parts[:-1])  # Everything before last part

        # Find matching player by reconstructing their safe name
        for player_name in self.players:
            safe_name = player_name.replace(" ", "_").replace("'", "").lower()
            if safe_name == player_part:
                return player_name, army_type

        raise InvalidArmyIdentifierError(army_identifier)

    def get_army_by_identifier(self, army_identifier: str) -> Tuple[str, Dict[str, Any]]:
        """
        Get army data by identifier. Returns (player_name, army_data).
        Raises appropriate exceptions if army cannot be found.
        """
        player_name, army_type = self.parse_army_identifier(army_identifier)

        player_data = self.get_player_data(player_name)
        if not player_data:
            raise PlayerNotFoundError(player_name)

        army_data = strict_get(player_data, "armies").get(army_type)
        if not army_data:
            raise ArmyNotFoundError(player_name, army_type)

        return player_name, army_data

    def update_army_identifiers_to_specific(self):
        """
        Update all army references to use specific identifiers.
        This is for migrating from old "home" identifiers to "player_1_home" format.
        """
        for player_name, player_data in self.players.items():
            armies = strict_get(player_data, "armies")
            # Army keys are already specific (home, campaign, horde)
            # but we can add unique army IDs for tracking
            for army_type, army_data in armies.items():
                army_data["unique_id"] = self.generate_army_identifier(player_name, army_type)
                army_data["player_name"] = player_name
                army_data["army_type"] = army_type

    # _parse_dragon_dice_description is removed as we are now getting structured dragon selections.

    # Army management methods
    def get_unit_health(self, player_name: str, army_identifier: str, unit_name: str) -> int:
        """Get the current health of a specific unit."""
        # Support both direct army types and specific army identifiers
        if army_identifier in ["home", "campaign", "horde"]:
            # Direct army type - use provided player_name
            player_data = self.get_player_data(player_name)
            if not player_data:
                raise PlayerNotFoundError(player_name)
            army = strict_get(player_data, "armies").get(army_identifier)
            if not army:
                raise ArmyNotFoundError(player_name, army_identifier)
        else:
            # Specific identifier - parse to get army
            parsed_player, army = self.get_army_by_identifier(army_identifier)

        if "units" not in army:
            raise ValueError(f"Army '{army_identifier}' missing required 'units' field")

        for unit in army["units"]:
            if "name" not in unit:
                raise ValueError(f"Unit in army '{army_identifier}' missing required 'name' field")
            if unit["name"] == unit_name:
                if "health" not in unit:
                    raise ValueError(f"Unit '{unit_name}' missing required 'health' field")
                return int(unit["health"])

        raise UnitNotFoundError(unit_name, army_identifier)

    def update_unit_health(self, player_name: str, army_identifier: str, unit_name: str, new_health: int) -> None:
        """Update the health of a specific unit."""
        # Support both direct army types and specific army identifiers
        if army_identifier in ["home", "campaign", "horde"]:
            # Direct army type - use provided player_name
            player_data = self.get_player_data(player_name)
            if not player_data:
                raise PlayerNotFoundError(player_name)
            army = strict_get(player_data, "armies").get(army_identifier)
            if not army:
                raise ArmyNotFoundError(player_name, army_identifier)
            target_player = player_name
        else:
            # Specific identifier - parse to get army
            target_player, army = self.get_army_by_identifier(army_identifier)

        if "units" not in army:
            raise ValueError(f"Army '{army_identifier}' missing required 'units' field")

        for unit in army["units"]:
            if "name" not in unit:
                raise ValueError(f"Unit in army '{army_identifier}' missing required 'name' field")
            if unit["name"] == unit_name:
                if new_health < 0:
                    raise ValueError(f"Cannot set negative health {new_health} for unit '{unit_name}'")
                unit["health"] = new_health
                if unit["health"] <= 0:
                    self._move_unit_to_dua(target_player, unit)
                    army["units"].remove(unit)
                self.game_state_changed.emit()
                return

        raise UnitNotFoundError(unit_name, army_identifier)

    def move_unit_between_armies(self, player_name: str, unit_name: str, from_army: str, to_army: str) -> None:
        """Move a unit from one army to another."""
        player_data = self.get_player_data(player_name)
        if "armies" not in player_data:
            raise ValueError(f"Player '{player_name}' missing required 'armies' field")
        armies = player_data["armies"]

        if from_army not in armies:
            raise ArmyNotFoundError(player_name, from_army)
        source_army = armies[from_army]

        if to_army not in armies:
            raise ArmyNotFoundError(player_name, to_army)
        target_army = armies[to_army]

        # Validate army structure
        if "units" not in source_army:
            raise ValueError(f"Source army '{from_army}' missing required 'units' field")
        if "units" not in target_army:
            raise ValueError(f"Target army '{to_army}' missing required 'units' field")

        # Find and remove unit from source army
        unit_to_move = None
        for unit in source_army["units"]:
            if "name" not in unit:
                raise ValueError(f"Unit in army '{from_army}' missing required 'name' field")
            if unit["name"] == unit_name:
                unit_to_move = unit
                break

        if not unit_to_move:
            raise UnitNotFoundError(unit_name, from_army)

        source_army["units"].remove(unit_to_move)
        target_army["units"].append(unit_to_move)
        self.game_state_changed.emit()

    def _move_unit_to_dua(self, player_name: str, unit: Dict[str, Any]):
        """Move a defeated unit to the Dead Unit Area (DUA)."""
        player_data = self.get_player_data_safe(player_name)
        if player_data:
            player_data.setdefault("dead_unit_area", []).append(unit)

    def move_unit_to_bua(self, player_name: str, army_identifier: str, unit_name: str) -> bool:
        """Move a unit to the Buried Unit Area (BUA)."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        army = strict_get(player_data, "armies").get(army_identifier)
        if not army:
            return False

        for unit in strict_get(army, "units"):
            if unit.get("name") == unit_name:
                army["units"].remove(unit)
                player_data.setdefault("buried_unit_area", []).append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_to_reserve_area(self, player_name: str, army_identifier: str, unit_name: str) -> bool:
        """Move a unit to the Reserve Area for tactical repositioning."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        army = strict_get(player_data, "armies").get(army_identifier)
        if not army:
            return False

        for unit in strict_get(army, "units"):
            if unit.get("name") == unit_name:
                army["units"].remove(unit)
                player_data.setdefault("reserve_area", []).append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_from_reserve_area(self, player_name: str, unit_name: str, target_army: str) -> bool:
        """Move a unit from Reserve Area to an army."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        reserve_area = strict_get(player_data, "reserve_area")
        target_army_data = strict_get(player_data, "armies").get(target_army)

        if not target_army_data:
            return False

        for unit in reserve_area:
            if unit.get("name") == unit_name:
                reserve_area.remove(unit)
                target_army_data["units"].append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def move_unit_from_reserve_pool(self, player_name: str, unit_name: str, target_army: str) -> bool:
        """Move a unit from Reserve Pool to an army (deployment)."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return False

        reserve_pool = strict_get(player_data, "reserve_pool")
        target_army_data = strict_get(player_data, "armies").get(target_army)

        if not target_army_data:
            return False

        for unit in reserve_pool:
            if unit.get("name") == unit_name:
                reserve_pool.remove(unit)
                target_army_data["units"].append(unit)
                self.game_state_changed.emit()
                return True
        return False

    def update_army_location(self, player_name: str, army_identifier: str, location: str) -> None:
        """Update the location of an army."""
        player_data = self.get_player_data(player_name)
        army = strict_get(player_data, "armies").get(army_identifier)
        if not army:
            raise ArmyNotFoundError(player_name, army_identifier)

        army["location"] = location
        self.game_state_changed.emit()

    def update_terrain_control(self, terrain_name: str, controlling_player: Optional[str]) -> None:
        """Update which player controls a terrain."""
        terrain = self.get_terrain_data(terrain_name)
        terrain["controlling_player"] = controlling_player
        self.game_state_changed.emit()

    def update_terrain_face(self, terrain_name: str, face: str) -> bool:
        """Update the face-up terrain. Returns True on success, False on failure."""
        try:
            terrain = self.get_terrain_data(terrain_name)
            terrain["face"] = int(face) if isinstance(face, str) else face
            self.game_state_changed.emit()
            return True
        except TerrainNotFoundError as e:
            print(f"GameStateManager: {e}")
            return False
        except (ValueError, TypeError) as e:
            print(f"GameStateManager: Invalid face value '{face}': {e}")
            return False

    def set_terrain_controller(self, terrain_name: str, controlling_player: Optional[str]) -> bool:
        """Set the controlling player for a terrain. Returns True on success."""
        try:
            terrain = self.get_terrain_data(terrain_name)
            terrain["controlling_player"] = controlling_player
            print(f"GameStateManager: Set {terrain_name} controller to {controlling_player}")
            self.game_state_changed.emit()
            return True
        except TerrainNotFoundError as e:
            print(f"GameStateManager: {e}")
            return False

    def get_terrain_controller(self, terrain_name: str) -> Optional[str]:
        """Get the controlling player for a terrain."""
        try:
            terrain = self.get_terrain_data(terrain_name)
            return terrain.get("controlling_player")
        except TerrainNotFoundError:
            return None

    def reset_terrain_control_when_lost(self, terrain_name: str) -> bool:
        """Reset terrain from eighth face to seventh when control is lost."""
        try:
            terrain = self.get_terrain_data(terrain_name)
            if terrain.get("face") == 8:
                terrain["face"] = 7
                terrain["controlling_player"] = None
                print(f"GameStateManager: Reset {terrain_name} from eighth to seventh face due to control loss")
                self.game_state_changed.emit()
                return True
            return False
        except TerrainNotFoundError as e:
            print(f"GameStateManager: {e}")
            return False

    def check_terrain_control_loss(self, player_name: str, army_id: str) -> List[str]:
        """Check if terrain control should be lost due to army destruction/abandonment."""
        terrains_lost = []

        # Find terrains controlled by this player
        for terrain_name, terrain_data in self.terrains.items():
            if terrain_data.get("controlling_player") == player_name:
                # Check if the controlling army still exists and has units
                try:
                    army_units = self.get_army_units(player_name, army_id)
                    if not army_units or all(strict_get(unit, "health") <= 0 for unit in army_units):
                        # Army destroyed or has no healthy units, lose control
                        self.reset_terrain_control_when_lost(terrain_name)
                        terrains_lost.append(terrain_name)
                except (PlayerNotFoundError, ArmyNotFoundError):
                    # Army no longer exists, lose control
                    self.reset_terrain_control_when_lost(terrain_name)
                    terrains_lost.append(terrain_name)

        return terrains_lost

    def get_army_location(self, player_name: str, army_id: Optional[str] = None) -> Optional[str]:
        """Get the location of a player's army."""
        try:
            player_data = self.get_player_data(player_name)

            # If no specific army specified, use active army
            if army_id is None:
                army_id = strict_get_optional(player_data, "active_army_type", "home")

            army_data = strict_get(player_data, "armies").get(army_id)
            if army_data:
                return army_data.get("location")

            return None
        except PlayerNotFoundError:
            return None

    def get_armies_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all armies at a specific location."""
        armies_at_location = []
        for player_name, player_data in self.players.items():
            for army_id, army in strict_get(player_data, "armies").items():
                if army.get("location") == location:
                    armies_at_location.append({"player": player_name, "army_id": army_id, "army": army})
        return armies_at_location

    def find_defending_armies_at_location(self, attacking_player_name: str, location: str) -> List[Dict[str, Any]]:
        """Find all enemy armies at the specified location that can be targeted."""
        all_armies_at_location = self.get_armies_at_location(location)
        defending_armies = []

        for army_info in all_armies_at_location:
            if army_info["player"] != attacking_player_name:  # Enemy army
                defending_armies.append(army_info)

        return defending_armies

    def determine_primary_defending_player(self, attacking_player_name: str, location: str) -> Optional[str]:
        """Determine the primary defending player at a location using Dragon Dice army priority."""
        defending_armies = self.find_defending_armies_at_location(attacking_player_name, location)

        if not defending_armies:
            return None

        # Priority: home > campaign > horde armies according to Dragon Dice rules
        for priority_type in ["home", "campaign", "horde"]:
            for army_info in defending_armies:
                if army_info["army_id"] == priority_type:
                    return str(army_info["player"])

        # Fallback to first defending player found
        return str(defending_armies[0]["player"])

    def determine_primary_defending_army_id(self, attacking_player_name: str, location: str) -> Optional[str]:
        """Determine the primary defending army identifier at a location."""
        defending_armies = self.find_defending_armies_at_location(attacking_player_name, location)

        if not defending_armies:
            return None

        # Priority: home > campaign > horde armies according to Dragon Dice rules
        for priority_type in ["home", "campaign", "horde"]:
            for army_info in defending_armies:
                if army_info["army_id"] == priority_type:
                    # Generate specific army identifier
                    return self.generate_army_identifier(army_info["player"], priority_type)

        # Fallback to first defending army found
        first_army = defending_armies[0]
        return self.generate_army_identifier(first_army["player"], first_army["army_id"])

    def get_reserve_pool(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the reserve pool (available for deployment) for a player."""
        player_data = self.get_player_data(player_name)
        return list(strict_get(player_data, "reserve_pool"))

    def get_reserve_area(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the reserve area (tactical repositioning) for a player."""
        player_data = self.get_player_data(player_name)
        return list(strict_get(player_data, "reserve_area"))

    def get_summoning_pool(self, player_name: str) -> List[Dict[str, Any]]:
        """Get the summoning pool for a player."""
        player_data = self.get_player_data(player_name)
        return list(strict_get(player_data, "summoning_pool"))

    def add_to_summoning_pool(self, player_name: str, unit: Dict[str, Any]) -> None:
        """Add a unit to the summoning pool."""
        player_data = self.get_player_data(player_name)
        player_data.setdefault("summoning_pool", []).append(unit)
        self.game_state_changed.emit()

    def check_victory_conditions(self) -> Optional[str]:
        """Check if any player has won by capturing required terrains."""
        # Simple victory condition: control majority of terrains
        player_terrain_counts: Dict[str, int] = {}
        total_terrains = len(self.terrains)

        for terrain_data in self.terrains.values():
            controlling_player = terrain_data.get("controlling_player")
            if controlling_player:
                player_terrain_counts[controlling_player] = strict_get(player_terrain_counts, controlling_player) + 1

        # Check if any player controls more than half the terrains
        for player, count in player_terrain_counts.items():
            if count > total_terrains // 2:
                return str(player)

        return None

    def apply_damage_to_units(self, player_name: str, army_identifier: str, damage_amount: int) -> None:
        """
        Applies damage to units in a specific army.
        Distributes damage across all units in the army.
        """
        # Support both direct army types and specific army identifiers
        if army_identifier in ["home", "campaign", "horde"]:
            # Direct army type - use provided player_name
            player_data = self.get_player_data(player_name)
            army = strict_get(player_data, "armies").get(army_identifier)
            if not army:
                raise ArmyNotFoundError(player_name, army_identifier)
            target_army_key = army_identifier
        else:
            # Specific identifier - parse to get army
            parsed_player, army = self.get_army_by_identifier(army_identifier)
            player_data = self.get_player_data(parsed_player)
            target_army_key = army_identifier
            player_name = parsed_player  # Use the parsed player name

        print(
            f"GameStateManager: Applying {damage_amount} damage to {player_name}'s {
                strict_get_optional(army, 'name', target_army_key)
            } army."
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
            print(f"GameStateManager: Unit {unit['name']} took {damage_to_unit} damage, health now {unit['health']}.")

            if unit["health"] <= 0:
                print(f"GameStateManager: Unit {unit['name']} defeated.")
                army["units"].remove(unit)
                player_data.setdefault("dead_unit_area", []).append(unit)

        if units_affected:
            # Check if army is now destroyed and automatically lose terrain control
            army_units = strict_get(army, "units")
            if not army_units or all(strict_get(unit, "health") <= 0 for unit in army_units):
                # Army is destroyed, check for terrain control loss
                terrains_lost = self.check_terrain_control_loss(player_name, target_army_key)
                if terrains_lost:
                    print(f"GameStateManager: Automatic terrain control lost for {player_name}: {terrains_lost}")
                    # Apply automatic terrain control loss
                    for terrain_name in terrains_lost:
                        self.reset_terrain_control_when_lost(terrain_name)

            self.game_state_changed.emit()

    def get_player_data(self, player_name: str) -> Dict[str, Any]:
        """Get player data or raise PlayerNotFoundError if player doesn't exist."""
        player_data = self.players.get(player_name)
        if not player_data:
            raise PlayerNotFoundError(player_name)
        return player_data

    def get_player_data_safe(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player data safely, returning None if player doesn't exist."""
        return self.players.get(player_name)

    def get_all_players_data(self) -> Dict[str, Dict[str, Any]]:
        return self.players

    def get_terrain_data(self, terrain_name: str) -> Dict[str, Any]:
        """Get terrain data or raise TerrainNotFoundError if terrain doesn't exist."""
        terrain_data = self.terrains.get(terrain_name)
        if not terrain_data:
            raise TerrainNotFoundError(terrain_name)
        return terrain_data

    def get_terrain_data_safe(self, terrain_name: str) -> Optional[Dict[str, Any]]:
        """Get terrain data safely, returning None if terrain doesn't exist."""
        return self.terrains.get(terrain_name)

    def get_all_terrain_data(self) -> Dict[str, Dict[str, Any]]:
        return self.terrains

    def get_player_home_terrain_name(self, player_name: str) -> str:
        """Get the home terrain name for a player."""
        player = self.get_player_data(player_name)
        home_terrain = player.get("home_terrain_name")
        if not home_terrain:
            raise GameStateError(f"Player '{player_name}' has no home terrain configured")
        return str(home_terrain)

    def set_active_army(self, player_name: str, army_type: str) -> None:
        """Set the active army for a player based on current game context."""
        player_data = self.get_player_data(player_name)

        # Validate that the army type exists
        if army_type not in strict_get(player_data, "armies"):
            raise ArmyNotFoundError(player_name, army_type)

        player_data["active_army_type"] = army_type
        self.game_state_changed.emit()

    def determine_active_army_by_location(self, player_name: str, current_location: str) -> Optional[str]:
        """
        Determine which army should be active based on the current game location.
        Returns the army type that should be active.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None

        armies = strict_get(player_data, "armies")

        # Find armies at the current location
        armies_at_location = []
        for army_type, army_data in armies.items():
            if army_data.get("location") == current_location:
                armies_at_location.append(army_type)

        # If only one army at location, it's the active one
        if len(armies_at_location) == 1:
            return str(armies_at_location[0])

        # If multiple armies, prefer by priority: home > campaign > horde
        priority_order = ["home", "campaign", "horde"]
        for army_type in priority_order:
            if army_type in armies_at_location:
                return army_type

        return None

    def determine_active_army_by_phase(
        self, player_name: str, current_phase: str, current_location: Optional[str] = None
    ) -> Optional[str]:
        """
        Determine which army should be active based on the current game phase and context.
        """
        player_data = self.get_player_data(player_name)
        if not player_data:
            return None

        strict_get(player_data, "armies")

        # Phase-specific logic
        if current_phase in ["FIRST_MARCH", "SECOND_MARCH"]:
            # During march phases, determine by location if provided
            if current_location:
                return self.determine_active_army_by_location(player_name, current_location)
            # Otherwise, use current active army
            return str(strict_get_optional(player_data, "active_army_type", "home"))

        if current_phase == "DRAGON_ATTACK":
            # Dragons can attack any army, but usually home terrain
            home_terrain = strict_get_optional(player_data, "home_terrain_name")
            if home_terrain:
                return self.determine_active_army_by_location(player_name, home_terrain)

        elif current_phase == "RESERVES":
            # Reserve phase can involve any army
            return str(strict_get_optional(player_data, "active_army_type", "home"))

        # Default to current active army or home
        return str(strict_get_optional(player_data, "active_army_type", "home"))

    def get_active_army_type(self, player_name: str) -> str:
        """Get the currently active army type for a player."""
        player_data = self.get_player_data(player_name)
        return str(strict_get_optional(player_data, "active_army_type", "home"))

    def get_active_army_data(self, player_name: str) -> Dict[str, Any]:
        """Get the data for the currently active army."""
        player_data = self.get_player_data(player_name)
        active_army_type = self.get_active_army_type(player_name)

        army_data = strict_get(player_data, "armies").get(active_army_type)
        if not army_data:
            raise ArmyNotFoundError(player_name, active_army_type)

        return army_data

    def get_active_army_units(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Returns the list of units for the currently active army of the specified player.
        The "active" army is determined by game flow context.
        """
        active_army = self.get_active_army_data(player_name)
        return strict_get(active_army, "units") if active_army else []

    def get_army_units(self, player_name: str, army_id: str) -> List[Dict[str, Any]]:
        """Get units for a specific army."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return []

        armies = strict_get(player_data, "armies")
        if army_id in armies:
            return armies[army_id].get("units", [])
        return []

    def get_all_armies_at_location(self, player_name: str, location: str) -> List[Dict[str, Any]]:
        """Get all armies for a player at a specific location."""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return []

        armies_at_location = []
        for army_type, army_data in strict_get(player_data, "armies").items():
            if army_data.get("location") == location:
                armies_at_location.append(
                    {
                        "army_type": army_type,
                        "army_data": army_data,
                        "unique_id": strict_get(army_data, "unique_id"),
                    }
                )

        return armies_at_location

    def get_all_terrain_names(self) -> List[str]:
        """Get a list of all terrain names in the game."""
        return list(self.terrains.keys())

    def get_armies_at_terrain(self, terrain_name: str) -> List[Dict[str, Any]]:
        """Get all armies present at a specific terrain from all players."""
        armies_at_terrain = []

        for player_name, player_data in self.players.items():
            armies = strict_get(player_data, "armies")

            for army_type, army_data in armies.items():
                if army_data.get("location") == terrain_name:
                    # Create army identifier for this army
                    army_identifier = f"{player_name}_{army_type}"

                    armies_at_terrain.append(
                        {
                            "owner": player_name,
                            "army_type": army_type,
                            "army_id": army_identifier,
                            "army_data": army_data,
                            "location": terrain_name,
                            "units": strict_get(army_data, "units"),
                            "points": strict_get(army_data, "points_value"),
                        }
                    )

        return armies_at_terrain

    def get_player_armies_summary(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Get a summary of all armies for a specific player.

        Returns a list of army summary dictionaries containing:
        - army_id: Unique identifier for the army
        - name: Display name of the army
        - location: Where the army is positioned (terrain name or "reserves")
        - race: Primary race/species of the army
        - unit_count: Number of units in the army
        - total_health: Sum of all unit health points
        - points_value: Total point value of the army
        - units: List of unit data for the army
        """
        player_data = self.get_player_data_safe(player_name)
        if not player_data:
            return []

        armies_summary = []
        armies_data = strict_get(player_data, "armies")

        for army_type, army_data in armies_data.items():
            # Get units and calculate summary stats
            units = strict_get_optional(army_data, "units", [])
            unit_count = len(units)
            total_health = sum(strict_get_optional(unit, "health", 1) for unit in units)
            points_value = strict_get_optional(army_data, "points_value", 0)

            # Determine primary race from units
            primary_race = self._determine_army_primary_race(units)

            # Get location - could be a terrain name or "reserves"
            location = strict_get_optional(army_data, "location", "unknown")

            # Generate army ID (using existing method if available)
            army_id = strict_get_optional(army_data, "unique_id", f"{player_name}_{army_type}")

            # Create army summary
            army_summary = {
                "army_id": army_id,
                "army_type": army_type,  # e.g., "home", "horde", "campaign"
                "name": strict_get_optional(army_data, "name", army_type.title() + " Army"),
                "location": location,
                "race": primary_race,
                "unit_count": unit_count,
                "total_health": total_health,
                "points_value": points_value,
                "units": units.copy(),  # Include full unit data for phase controllers
                "player_name": player_name,
            }

            armies_summary.append(army_summary)

        return armies_summary

    def _determine_army_primary_race(self, units: List[Dict[str, Any]]) -> str:
        """Determine the primary race/species of an army based on its units."""
        if not units:
            return "none"

        # Count units by race/species
        race_counts = {}
        for unit in units:
            # Try different possible field names for race/species
            # Ensure we get a string value, not a dict
            race_value = (
                strict_get_optional(unit, "race")
                or strict_get_optional(unit, "species")
                or strict_get_optional(unit, "type")
            )

            # Handle cases where the value might be a dict or other complex type
            if isinstance(race_value, dict):
                # If it's a dict, try to extract a name or id field
                race = race_value.get("name") or race_value.get("id") or str(race_value.get("type", "unknown"))
            elif isinstance(race_value, str):
                race = race_value
            elif race_value is not None:
                # Convert other types to string
                race = str(race_value)
            else:
                race = "unknown"

            race_counts[race] = race_counts.get(race, 0) + 1

        # Return the most common race, or "mixed" if tied
        if not race_counts:
            return "unknown"

        max_count = max(race_counts.values())
        primary_races = [race for race, count in race_counts.items() if count == max_count]

        if len(primary_races) == 1:
            return primary_races[0]
        return "mixed"  # Multiple races with equal representation

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current game state formatted for eighth face manager and other systems.

        Returns:
            Dictionary containing terrain_data and all_players_data
        """
        return {
            "terrain_data": self.terrains,
            "all_players_data": self.players,
        }
