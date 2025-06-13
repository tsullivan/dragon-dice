from PySide6.QtCore import QObject, Signal

class AppDataModel(QObject):
    """
    Manages the shared application state.
    Emits signals when data changes to allow UI updates.
    """
    num_players_changed = Signal(int)
    point_value_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._num_players = None
        self._point_value = None

    def set_num_players(self, count):
        self._num_players = count
        self.num_players_changed.emit(count)

    def set_point_value(self, value):
        self._point_value = value
        self.point_value_changed.emit(value)

