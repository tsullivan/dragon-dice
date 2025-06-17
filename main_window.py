from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
)
from PySide6.QtCore import Qt, Signal

from views.welcome_view import WelcomeView
from views.player_setup_view import PlayerSetupView
from views.frontier_selection_view import FrontierSelectionView
from views.distance_rolls_view import DistanceRollsView
from views.main_gameplay_view import MainGameplayView
from controllers.gameplay_controller import GameplayController
from models.app_data_model import AppDataModel


class MainWindow(QMainWindow):
    """
    The main window of the application.
    It will manage and display different views (screens).
    """

    view_switched_and_ready = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice Companion (PySide6)")
        self.setGeometry(100, 100, 1280, 720)
        self.data_model = AppDataModel()
        self.current_controller = None
        self.player_setup_view_instance: PlayerSetupView | None = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget_layout = QVBoxLayout(self.central_widget)

        self._current_view = None
        self.show_welcome_view()  # Start with the welcome screen

        # Connect data_model signals that trigger view changes once
        # This avoids reconnecting them every time a view is shown.
        self.data_model.all_player_setups_complete.connect(
            self.show_frontier_selection_view
        )
        self.data_model.frontier_set.connect(self.show_distance_rolls_view)
        self.data_model.all_distance_rolls_submitted.connect(
            self.data_model.initialize_game_engine
        )
        self.data_model.game_engine_initialized.connect(self.show_main_gameplay_view)

    def switch_view(self, new_view_widget):
        """Removes the current view and adds the new one."""
        if self._current_view:
            self._current_view.hide()
            self.central_widget_layout.removeWidget(self._current_view)
            self._current_view.deleteLater()
            if self._current_view == self.player_setup_view_instance:
                self.player_setup_view_instance = None
            self._current_view = None
        self._current_view = new_view_widget
        self.central_widget_layout.addWidget(self._current_view)
        QApplication.processEvents()
        self.view_switched_and_ready.emit()

    def show_welcome_view(self):
        welcome_widget = WelcomeView()
        welcome_widget.proceed_signal.connect(self.show_player_setup_view)
        welcome_widget.player_count_selected_signal.connect(
            self.data_model.set_num_players
        )
        welcome_widget.point_value_selected_signal.connect(
            self.data_model.set_point_value
        )
        welcome_widget.emit_current_selections()
        if self.player_setup_view_instance:
            self.player_setup_view_instance = None
        self.switch_view(welcome_widget)

    def show_player_setup_view(self):
        if self.data_model._num_players is None or self.data_model._point_value is None:
            print(
                "Error: Number of players or point value not set before proceeding to player setup."
            )
            return

        terrain_options = self.data_model.get_terrain_display_options()
        required_dragons = self.data_model.get_required_dragon_count()

        # Player 1 setup (index 0)
        self.data_model.current_setup_player_index = 0
        initial_data_for_player_1 = self.data_model.get_player_data(0)

        if not self.player_setup_view_instance:
            self.player_setup_view_instance = PlayerSetupView(
                num_players=self.data_model._num_players,
                point_value=self.data_model._point_value,
                terrain_display_options=terrain_options,
                required_dragons=required_dragons,
                current_player_index=0,
                initial_player_data=initial_data_for_player_1,
            )
            self.player_setup_view_instance.player_data_finalized.connect(
                self.handle_player_data_finalized
            )
            self.player_setup_view_instance.back_signal.connect(
                self.handle_player_setup_back
            )
        else:
            self.player_setup_view_instance.update_for_player(
                0, initial_data_for_player_1
            )

        self.switch_view(self.player_setup_view_instance)

    def handle_player_data_finalized(self, player_index: int, data: dict):
        print(f"Player {player_index + 1} data finalized: {data}")
        self.data_model.add_player_setup_data(player_index, data)

        next_player_index = player_index + 1
        num_players = self.data_model._num_players
        if num_players is not None and next_player_index < num_players:
            self.data_model.current_setup_player_index = next_player_index
            data_for_next_player = self.data_model.get_player_data(next_player_index)
            if self.player_setup_view_instance:
                self.player_setup_view_instance.update_for_player(
                    next_player_index, data_for_next_player
                )

    def handle_player_setup_back(self, emitted_player_index: int):
        if emitted_player_index > 0:  # Coming from Player 2 (index 1) or higher
            previous_player_index = emitted_player_index - 1
            self.data_model.current_setup_player_index = previous_player_index
            player_data_to_load = self.data_model.get_player_data(previous_player_index)
            if self.player_setup_view_instance:
                self.player_setup_view_instance.update_for_player(
                    previous_player_index, player_data_to_load
                )
                QApplication.processEvents()
        else:  # Coming from Player 1 (index 0)
            self.show_welcome_view()

    def show_frontier_selection_view(self):
        print("All player setups complete. Transitioning to Frontier Selection...")
        player_names = self.data_model.get_player_names()
        proposed_terrains = (
            self.data_model.get_proposed_frontier_terrains()
        )

        if not player_names or not proposed_terrains:
            print(
                "Error: No player names or proposed terrains available for frontier selection."
            )
            return
        frontier_view = FrontierSelectionView(
            player_names=player_names, proposed_frontier_terrains=proposed_terrains
        )
        frontier_view.frontier_data_submitted.connect(self.handle_frontier_submission)
        frontier_view.back_signal.connect(self._go_back_to_last_player_setup)
        self.switch_view(frontier_view)

    def handle_frontier_submission(self, first_player_name, frontier_terrain):
        self.data_model.set_frontier_and_first_player(
            first_player_name, frontier_terrain
        )

    def _go_back_to_last_player_setup(self):
        """Navigates back to the setup screen of the last configured player."""
        if self.data_model._num_players is not None and self.data_model._num_players > 0:
            last_player_idx = self.data_model._num_players - 1
            self.data_model.current_setup_player_index = last_player_idx

            if self.data_model._point_value is None:
                self.show_welcome_view()
                return

            terrain_options = self.data_model.get_terrain_display_options()
            required_dragons = self.data_model.get_required_dragon_count()
            player_data_to_load = self.data_model.get_player_data(last_player_idx)

            if not self.player_setup_view_instance:
                self.player_setup_view_instance = PlayerSetupView(
                    num_players=self.data_model._num_players,
                    point_value=self.data_model._point_value,
                    terrain_display_options=terrain_options,
                    required_dragons=required_dragons,
                    current_player_index=last_player_idx,
                    initial_player_data=player_data_to_load,
                )
                self.player_setup_view_instance.player_data_finalized.connect(self.handle_player_data_finalized)
                self.player_setup_view_instance.back_signal.connect(self.handle_player_setup_back)
            else:
                self.player_setup_view_instance.update_for_player(last_player_idx, player_data_to_load)
            self.switch_view(self.player_setup_view_instance)
        else:
            self.show_welcome_view()

    def show_distance_rolls_view(self):
        print(
            f"Frontier '{self.data_model._frontier_terrain}' and first player '{self.data_model._first_player_name}' set. Transitioning to Distance Rolls..."
        )
        player_setup_data = self.data_model.get_player_setup_data()
        frontier_terrain = self.data_model._frontier_terrain

        if not player_setup_data or not frontier_terrain:
            print("Error: Missing player data or frontier terrain for distance rolls.")
            return

        distance_view = DistanceRollsView(player_setup_data, frontier_terrain)
        distance_view.rolls_submitted.connect(self.data_model.set_distance_rolls)
        distance_view.back_signal.connect(self.show_frontier_selection_view)
        self.switch_view(distance_view)

    def show_main_gameplay_view(self, game_engine_instance):
        if not game_engine_instance:
            print("Error: GameEngine instance not provided to show_main_gameplay_view.")
            return
        print(
            f"Game engine initialized. Transitioning to Main Gameplay View for player: {game_engine_instance.get_current_player_name()}"
        )

        self.current_controller = GameplayController(
            game_engine_instance
        )
        gameplay_view = MainGameplayView(game_engine_instance)
        gameplay_view.maneuver_decision_signal.connect(
            self.current_controller.handle_maneuver_decision
        )
        gameplay_view.maneuver_input_submitted_signal.connect(
            self.current_controller.handle_maneuver_input_submission
        )
        gameplay_view.melee_action_selected_signal.connect(
            self.current_controller.handle_melee_action_selected
        )
        gameplay_view.missile_action_selected_signal.connect(
            self.current_controller.handle_missile_action_selected
        )
        gameplay_view.magic_action_selected_signal.connect(
            self.current_controller.handle_magic_action_selected
        )
        gameplay_view.attacker_melee_results_submitted.connect(
            self.current_controller.handle_attacker_melee_submission
        )
        gameplay_view.defender_save_results_submitted.connect(
            self.current_controller.handle_defender_save_submission
        )
        gameplay_view.continue_to_next_phase_signal.connect(
            self.current_controller.handle_continue_to_next_phase
        )
        self.switch_view(gameplay_view)
