from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_logic.engine import GameEngine

from .terrain_model import Terrain
from .army_model import ArmyModel
from .unit_model import (
    UnitModel,
)  # Import UnitModel (though AppDataModel might deal with ArmyModel dicts)
from utils.constants import DEFAULT_FORCE_SIZE, POINTS_PER_DRAGON
from .terrain_model import TERRAIN_DATA


class AppDataModel(QObject):
    """
    Manages the shared application state.
    Emits signals when data changes to allow UI updates.
    """

    num_players_changed = Signal(int)
    force_size_changed = Signal(int)
    player_setup_data_added = Signal(dict)
    all_player_setups_complete = Signal()
    frontier_set = Signal(str, str)
    all_distance_rolls_submitted = Signal(list)
    game_engine_initialized = Signal(object)  # Signal will carry GameEngine instance

    def __init__(self):
        super().__init__()
        # Validate all internal data at startup
        self._validate_internal_data()

        self._num_players = None
        self._force_size = DEFAULT_FORCE_SIZE
        self._player_setup_data_list: list[dict] = (
            []
        )  # Will be initialized based on num_players
        self._first_player_name = None
        self._frontier_terrain = None
        self._distance_rolls = []  # List of tuples: (player_name, distance)
        self._game_engine: Optional["GameEngine"] = None
        self._all_terrains: list[Terrain] = []
        self.current_setup_player_index: int = 0  # Track current player being set up
        self._terrain_display_options: list[str] = []
        self._initialize_terrains()

    def _initialize_terrains(self):
        try:
            # TERRAIN_DATA now contains Terrain objects directly
            self._all_terrains = list(TERRAIN_DATA.values())
            self._terrain_display_options = [
                str(terrain) for terrain in self._all_terrains
            ]
        except ValueError as e:
            print(f"Error initializing terrains in AppDataModel: {e}")
            self._all_terrains = []
            self._terrain_display_options = []

    def set_num_players(self, count):
        self._num_players = count
        # Initialize/reset player setup data list for the given number of players
        self._player_setup_data_list = [{} for _ in range(count)]
        self.current_setup_player_index = 0  # Reset to player 1
        self.num_players_changed.emit(count)

    def set_force_size(self, size: int):
        """Set the total force size for the game."""
        self._force_size = size
        self.force_size_changed.emit(size)

    def get_force_size(self) -> int:
        """Get the current force size setting."""
        return self._force_size

    def add_player_setup_data(self, player_index: int, player_data: dict):
        """Stores setup data for a specific player index."""
        if self._num_players is None or not (0 <= player_index < self._num_players):
            print(
                f"Error: Cannot add player data. Invalid player_index ({player_index}) or num_players not set."
            )
            return

        self._player_setup_data_list[player_index] = player_data
        self.player_setup_data_added.emit(
            player_data
        )  # Consider emitting (player_index, player_data)

        # Check if all players have submitted their data (i.e., no empty dicts left)
        if len([pd for pd in self._player_setup_data_list if pd]) == self._num_players:
            self.all_player_setups_complete.emit()

    def get_player_data(self, player_index: int) -> Optional[dict]:
        if self._num_players is not None and 0 <= player_index < len(
            self._player_setup_data_list
        ):
            return self._player_setup_data_list[player_index]
        return None

    def get_player_names(self):
        return [
            p_data.get("name", f"Player {i+1}")
            for i, p_data in enumerate(self._player_setup_data_list)
        ]

    def get_player_setup_data(self):
        return self._player_setup_data_list

    def get_all_terrains_list(self) -> list[Terrain]:
        return self._all_terrains

    def get_terrain_display_options(self) -> list[tuple]:
        """Returns terrain display options as list of tuples (name, colors) for PlayerSetupView."""
        return [
            (terrain.name, terrain.element_colors) for terrain in self._all_terrains
        ]

    def get_required_dragon_count(self) -> int:
        """Calculate required dragons based on current force size.

        Official Dragon Dice rules: 1 dragon per 24 points (or part thereof)
        """
        return self.calculate_required_dragons(self._force_size)

    @staticmethod
    def calculate_required_dragons(force_size_points: int) -> int:
        """Calculate required dragons based on force size points.

        Official rules: 1 dragon per 24 points (or part thereof)
        Examples: 15 pts = 1 dragon, 24 pts = 1 dragon, 30 pts = 2 dragons, 60 pts = 3 dragons
        """
        import math

        return math.ceil(force_size_points / POINTS_PER_DRAGON)

    def get_proposed_frontier_terrains(self):
        """Returns a list of tuples (player_name, proposed_terrain_type)"""
        return [
            (p_data.get("name"), p_data.get("frontier_terrain_proposal"))
            for p_data in self._player_setup_data_list
            if p_data.get("frontier_terrain_proposal")
        ]

    def set_frontier_and_first_player(self, first_player_name, frontier_terrain):
        self._first_player_name = first_player_name
        self._frontier_terrain = frontier_terrain
        print(
            f"AppDataModel: Frontier set - First Player: {self._first_player_name}, Terrain: {self._frontier_terrain}"
        )
        self.frontier_set.emit(self._first_player_name, self._frontier_terrain)

    def set_distance_rolls(self, rolls_data):
        # rolls_data is expected to be a list of tuples: (player_name, distance)
        self._distance_rolls = rolls_data
        print(f"AppDataModel: Distance rolls submitted: {self._distance_rolls}")
        self.all_distance_rolls_submitted.emit(self._distance_rolls)

    def initialize_game_engine(self):
        if (
            not self._player_setup_data_list
            or self._first_player_name is None
            or self._frontier_terrain is None
            or not self._distance_rolls
        ):
            print(
                "Error: Cannot initialize GameEngine. Required setup data is missing."
            )
            return None

        # Import GameEngine here to avoid circular import
        from game_logic.engine import GameEngine

        self._game_engine = GameEngine(
            self._player_setup_data_list,
            self._first_player_name,
            self._frontier_terrain,
            self._distance_rolls,
        )
        self.game_engine_initialized.emit(self._game_engine)
        return self._game_engine

    @staticmethod
    def validate_unit_die_faces() -> None:
        """
        Validate that all units have the correct number of die faces and that all face keys are valid.
        Raises ValueError with accumulated list of problems if validation fails.
        """
        from models.die_face_model import DIE_FACES_DATA
        from models.unit_data import UNIT_DATA

        problems = []

        for unit in UNIT_DATA:
            unit_name = f"{unit.name} ({unit.unit_id})"

            # Check face count
            expected_face_count = 10 if unit.unit_type == "Monster" else 6
            actual_face_count = len(unit.die_faces)

            if actual_face_count != expected_face_count:
                problems.append(
                    f"{unit_name}: Expected {expected_face_count} faces, got {actual_face_count}"
                )

            # Check ID face matches health
            if unit.die_faces:
                expected_id_face = f"ID_{unit.health}"
                actual_id_face = (
                    unit.die_faces[0] if unit.die_faces[0].startswith("ID_") else None
                )

                if actual_id_face != expected_id_face:
                    problems.append(
                        f"{unit_name}: Expected ID face '{expected_id_face}', got '{actual_id_face}'"
                    )

            # Check all face keys are valid
            for face_key in unit.die_faces:
                if face_key not in DIE_FACES_DATA:
                    problems.append(f"{unit_name}: Invalid die face key '{face_key}'")

        if problems:
            error_message = (
                f"Die face validation failed with {len(problems)} problems:\n"
                + "\n".join(f"  - {problem}" for problem in problems)
            )
            raise ValueError(error_message)

        print(f"✓ Die face validation passed for {len(UNIT_DATA)} units")

    def _validate_internal_data(self) -> None:
        """
        Comprehensive validation of all internal data at startup.
        Calls all individual validation functions to ensure data integrity.
        """
        print("🔍 Validating internal data...")

        try:
            # Validate die face data
            from models.die_face_model import validate_die_face_data

            validate_die_face_data()

            # Validate terrain data
            from models.terrain_model import validate_terrain_data

            validate_terrain_data()

            # Validate dragon data
            from models.dragon_model import validate_dragon_data

            validate_dragon_data()

            # Validate species data
            from models.species_model import validate_species_elements

            if not validate_species_elements():
                raise ValueError("Species validation failed")
            print("✓ All species data validated successfully")

            # Validate unit data integrity
            from models.unit_data import validate_unit_data_integrity

            if not validate_unit_data_integrity():
                raise ValueError("Unit data integrity validation failed")
            print("✓ Unit data integrity validated successfully")

            # Validate unit die face assignments
            self.validate_unit_die_faces()

            # Validate comprehensive unit data
            from models.unit_model import UnitModel

            validation_report = UnitModel.validate_all_unit_data()
            if validation_report.get("invalid_units"):
                invalid_count = len(validation_report["invalid_units"])
                total_count = validation_report["valid_units"] + invalid_count
                print(
                    f"⚠️  Warning: {invalid_count}/{total_count} units failed validation"
                )
                for invalid_unit in validation_report["invalid_units"][
                    :3
                ]:  # Show first 3
                    print(f"  - {invalid_unit['unit_id']}: {invalid_unit['error']}")
                if invalid_count > 3:
                    print(f"  ... and {invalid_count - 3} more")

            print("✅ All internal data validation passed")

        except Exception as e:
            error_msg = f"Internal data validation failed: {e}"
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)

    def get_unit_definitions(self) -> Dict[str, List[Dict]]:
        """Get unit definitions grouped by species for UI consumption."""
        try:
            from models.unit_data import UNIT_DATA

            # Convert flat UNIT_DATA list to grouped dictionary format
            units_by_species = {}
            for unit_instance in UNIT_DATA:
                species_name = unit_instance.species.name
                if species_name not in units_by_species:
                    units_by_species[species_name] = []

                # Convert UnitModel instance to dict format expected by UnitRosterModel
                unit_dict = {
                    "unit_type_id": unit_instance.unit_id,
                    "display_name": unit_instance.name,
                    "max_health": unit_instance.max_health,
                    "unit_class_type": unit_instance.unit_type,
                    "abilities": unit_instance.abilities,
                    "die_faces": unit_instance.die_faces,
                }
                units_by_species[species_name].append(unit_dict)

            return units_by_species
        except Exception as e:
            error_msg = f"Error getting unit definitions: {e}"
            print(f"ERROR: {error_msg}")
            return {}

    def get_species_definitions(self) -> Dict:
        """Get species definitions with element mappings."""
        try:
            from models.species_model import ALL_SPECIES

            return ALL_SPECIES
        except Exception as e:
            error_msg = f"Error getting species definitions: {e}"
            print(f"ERROR: {error_msg}")
            return {}
