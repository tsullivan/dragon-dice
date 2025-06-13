from PySide6.QtCore import QObject, Signal, QMetaObject
from typing import Optional
from engine import GameEngine # Import the new GameEngine

class AppDataModel(QObject):
    """
    Manages the shared application state.
    Emits signals when data changes to allow UI updates.
    """
    num_players_changed = Signal(int)
    point_value_changed = Signal(int)
    player_setup_data_added = Signal(dict) # Emits the data of the player just added
    all_player_setups_complete = Signal()
    frontier_set = Signal(str, str) # Emits (first_player_name, frontier_terrain)
    all_distance_rolls_submitted = Signal(list) # Emits list of (player_name, distance)
    game_engine_initialized = Signal(GameEngine) # Emits the engine instance

    def __init__(self):
        super().__init__()
        self._num_players = None
        self._point_value = None
        self._player_setup_data_list = []
        self._first_player_name = None
        self._frontier_terrain = None
        self._distance_rolls = [] # List of tuples: (player_name, distance)
        self._game_engine: Optional[GameEngine] = None

        # For MainWindow to track signal connections to prevent duplicates
        self._frontier_set_connection: Optional[QMetaObject.Connection] = None
        self._distance_rolls_connection: Optional[QMetaObject.Connection] = None
        self._game_engine_initialized_connection: Optional[QMetaObject.Connection] = None


    def set_num_players(self, count):
        self._num_players = count
        self.num_players_changed.emit(count)

    def set_point_value(self, value):
        self._point_value = value
        self.point_value_changed.emit(value)

    def add_player_setup_data(self, player_data):
        self._player_setup_data_list.append(player_data)
        self.player_setup_data_added.emit(player_data)
        if self._num_players is not None and len(self._player_setup_data_list) == self._num_players:
            self.all_player_setups_complete.emit()

    def get_player_names(self):
        return [p_data.get("name", f"Player {i+1}") for i, p_data in enumerate(self._player_setup_data_list)]

    def get_player_setup_data(self):
        return self._player_setup_data_list

    def set_frontier_and_first_player(self, first_player_name, frontier_terrain):
        self._first_player_name = first_player_name
        self._frontier_terrain = frontier_terrain
        print(f"AppDataModel: Frontier set - First Player: {self._first_player_name}, Terrain: {self._frontier_terrain}")
        self.frontier_set.emit(self._first_player_name, self._frontier_terrain)

    def set_distance_rolls(self, rolls_data):
        # rolls_data is expected to be a list of tuples: (player_name, distance)
        self._distance_rolls = rolls_data
        print(f"AppDataModel: Distance rolls submitted: {self._distance_rolls}")
        self.all_distance_rolls_submitted.emit(self._distance_rolls)

    def initialize_game_engine(self):
        if not self._player_setup_data_list or \
           self._first_player_name is None or \
           self._frontier_terrain is None or \
           not self._distance_rolls:
            print("Error: Cannot initialize GameEngine. Required setup data is missing.")
            return None

        self._game_engine = GameEngine(self._player_setup_data_list, self._first_player_name, self._frontier_terrain, self._distance_rolls)
        self.game_engine_initialized.emit(self._game_engine)
        return self._game_engine
