from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from .views.welcome_view import WelcomeView
from .views.player_setup_view import PlayerSetupView
from .app_data_model import AppDataModel

class MainWindow(QMainWindow):
    """
    The main window of the application.
    It will manage and display different views (screens).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice Companion (PySide6)")
        self.setGeometry(100, 100, 1280, 720) # x, y, width, height
        self.data_model = AppDataModel()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget_layout = QVBoxLayout(self.central_widget) # Renamed variable

        self._current_view = None
        self.show_welcome_view() # Start with the welcome screen

    def switch_view(self, new_view_widget):
        """Removes the current view and adds the new one."""
        if self._current_view:
            self.central_widget_layout.removeWidget(self._current_view)
            self._current_view.deleteLater()
        self._current_view = new_view_widget
        self.central_widget_layout.addWidget(self._current_view)

    def show_welcome_view(self):
        welcome_widget = WelcomeView()
        welcome_widget.proceed_signal.connect(self.show_player_setup_view)
        welcome_widget.player_count_selected_signal.connect(self.data_model.set_num_players)
        welcome_widget.point_value_selected_signal.connect(self.data_model.set_point_value)
        # Initialize with default values from WelcomeView's comboboxes
        welcome_widget.emit_current_selections() # Ensure initial values are set
        self.switch_view(welcome_widget)

    def show_player_setup_view(self):
        if self.data_model._num_players is None or self.data_model._point_value is None:
            print("Error: Number of players or point value not set before proceeding to player setup.")
            # Optionally, show an error message to the user or default to something
            # For now, let's prevent moving forward if data isn't set.
            return

        player_setup_widget = PlayerSetupView(num_players=self.data_model._num_players,
                                              point_value=self.data_model._point_value)
        self.switch_view(player_setup_widget)