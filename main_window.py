from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from views.welcome_view import WelcomeView
from views.player_setup_view import PlayerSetupView
from views.frontier_selection_view import FrontierSelectionView
from views.distance_rolls_view import DistanceRollsView
from views.main_gameplay_view import MainGameplayView
from controllers.gameplay_controller import GameplayController
from app_data_model import AppDataModel

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
        self.current_controller = None # To hold the active controller

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget_layout = QVBoxLayout(self.central_widget) # Renamed variable

        self._current_view = None
        self.show_welcome_view() # Start with the welcome screen

    def switch_view(self, new_view_widget):
        """Removes the current view and adds the new one."""
        if self._current_view:
            # If you have a controller associated with the old view,
            # you might want to clean it up or delete it here too.
            # self.current_controller = None 
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
        player_setup_widget.player_data_finalized.connect(self.handle_player_data_finalized)
        # The all_setups_complete_signal is now emitted by the data_model
        self.data_model.all_player_setups_complete.connect(self.show_frontier_selection_view)
        self.switch_view(player_setup_widget)

    def handle_player_data_finalized(self, player_index, data):
        print(f"Player {player_index + 1} data finalized: {data}")
        self.data_model.add_player_setup_data(data)

    def show_frontier_selection_view(self):
        print("All player setups complete. Transitioning to Frontier Selection...")
        player_names = self.data_model.get_player_names()
        if not player_names:
            print("Error: No player names available for frontier selection.")
            # Handle error, maybe go back to welcome or show an error message
            return
        
        frontier_view = FrontierSelectionView(player_names=player_names)
        frontier_view.frontier_data_submitted.connect(self.handle_frontier_submission)
        # Connect the model's signal to the next view transition
        if not hasattr(self.data_model, '_frontier_set_connection') or not self.data_model._frontier_set_connection:
            self.data_model._frontier_set_connection = self.data_model.frontier_set.connect(self.show_distance_rolls_view)
        self.switch_view(frontier_view)

    def handle_frontier_submission(self, first_player_name, frontier_terrain):
        self.data_model.set_frontier_and_first_player(first_player_name, frontier_terrain)

    def show_distance_rolls_view(self):
        print(f"Frontier '{self.data_model._frontier_terrain}' and first player '{self.data_model._first_player_name}' set. Transitioning to Distance Rolls...")
        player_setup_data = self.data_model.get_player_setup_data()
        frontier_terrain = self.data_model._frontier_terrain

        if not player_setup_data or not frontier_terrain:
            print("Error: Missing player data or frontier terrain for distance rolls.")
            return

        distance_view = DistanceRollsView(player_setup_data, frontier_terrain)
        distance_view.rolls_submitted.connect(self.data_model.set_distance_rolls)
        if not hasattr(self.data_model, '_distance_rolls_connection') or not self.data_model._distance_rolls_connection:
            # When all rolls are submitted, initialize the engine
            self.data_model._distance_rolls_connection = self.data_model.all_distance_rolls_submitted.connect(
                self.data_model.initialize_game_engine
            )
        # When engine is initialized, show the gameplay view
        if not hasattr(self.data_model, '_game_engine_initialized_connection') or not self.data_model._game_engine_initialized_connection:
            self.data_model._game_engine_initialized_connection = self.data_model.game_engine_initialized.connect(
                self.show_main_gameplay_view
            )
        self.switch_view(distance_view)

    def show_main_gameplay_view(self, game_engine_instance):
        if not game_engine_instance:
            print("Error: GameEngine instance not provided to show_main_gameplay_view.")
            # Potentially show an error view or go back
            return
        print(f"Game engine initialized. Transitioning to Main Gameplay View for player: {game_engine_instance.get_current_player_name()}")
        
        self.current_controller = GameplayController(game_engine_instance) # Store as current_controller
        gameplay_view = MainGameplayView(game_engine_instance)
        gameplay_view.maneuver_decision_signal.connect(self.current_controller.handle_maneuver_decision)
        gameplay_view.maneuver_input_submitted_signal.connect(self.current_controller.handle_maneuver_input_submission)
        # Add connections for other gameplay actions here
        self.switch_view(gameplay_view)