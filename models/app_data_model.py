from PySide6.QtCore import QObject, Signal, QMetaObject
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_logic.engine import GameEngine

from .terrain_model import Terrain
from .army_model import ArmyModel
from .unit_model import (
    UnitModel,
)  # Import UnitModel (though AppDataModel might deal with ArmyModel dicts)
from utils.constants import TERRAIN_DATA, DEFAULT_FORCE_SIZE, calculate_required_dragons


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
            for name, terrain_info in TERRAIN_DATA.items():
                self._all_terrains.append(
                    Terrain(name=name, colors=terrain_info["COLORS"])
                )
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
        return [(terrain.name, terrain.colors) for terrain in self._all_terrains]

    def get_required_dragon_count(self) -> int:
        """Calculate required dragons based on current force size.

        Official Dragon Dice rules: 1 dragon per 24 points (or part thereof)
        """
        return calculate_required_dragons(self._force_size)

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
