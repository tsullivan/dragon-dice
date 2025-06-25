from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QTextEdit,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont  # Added for QFont

# No change, good comment
from models.help_text_model import HelpTextModel
from components.tabbed_view_widget import TabbedViewWidget


class DistanceRollsView(QWidget):
    """
    View for players to input their distance rolls to the frontier.
    """

    rolls_submitted = Signal(list)
    back_signal = Signal()

    def __init__(
        self, player_setup_data, frontier_terrain, first_player_name=None, parent=None
    ):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        self.frontier_terrain = frontier_terrain
        self.first_player_name = first_player_name
        self.help_model = HelpTextModel()
        self.roll_inputs = {}
        self.setWindowTitle("Enter Starting Distances")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # Title
        title_label = QLabel("Enter Starting Distances")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(22)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Sub-title for Frontier Terrain
        frontier_info_label = QLabel(
            f"Rolling distance to: {
                                     self.frontier_terrain}"
        )
        frontier_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = frontier_info_label.font()
        font.setPointSize(16)
        frontier_info_label.setFont(font)
        main_layout.addWidget(frontier_info_label)

        # Tabbed Interface (Game and Help)
        self.tabbed_widget = TabbedViewWidget()

        # Game Tab Content (Distance Roll Inputs)
        inputs_widget = QWidget()
        inputs_v_layout = QVBoxLayout(inputs_widget)
        inputs_v_layout.setContentsMargins(0, 0, 0, 0)

        distance_rolls_group = QGroupBox("Player Distance Rolls")
        form_layout = QFormLayout(distance_rolls_group)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(10)

        distance_allowed_values = list(range(1, 7))

        for i, p_data in enumerate(self.player_setup_data):
            player_name = p_data.get("name", f"Player {i+1}")
            home_terrain = p_data.get("home_terrain", "N/A")
            frontier_terrain_proposal = p_data.get("frontier_terrain_proposal", "")

            # Create section for this player
            player_group = QGroupBox(f"{player_name} (Home: {home_terrain})")
            player_layout = QVBoxLayout(player_group)

            # Home terrain roll
            home_terrain_label = QLabel(f"Roll for {home_terrain} (Home Terrain):")
            home_terrain_label.setStyleSheet("font-weight: bold;")
            player_layout.addWidget(home_terrain_label)

            # Radio buttons for home terrain distance (1-6)
            home_button_group = QButtonGroup(self)
            home_buttons_layout = QHBoxLayout()

            for val in distance_allowed_values:
                radio_button = QRadioButton(str(val))
                home_button_group.addButton(radio_button, val)
                home_buttons_layout.addWidget(radio_button)
                if val == 1:  # Default selection
                    radio_button.setChecked(True)

            player_layout.addLayout(home_buttons_layout)
            self.roll_inputs[f"{player_name}_home"] = home_button_group

            # Frontier terrain roll (only for the first player)
            if player_name == self.first_player_name:
                frontier_terrain_label = QLabel(
                    f"Roll for {self.frontier_terrain} (Frontier Terrain - you are the first player):"
                )
                frontier_terrain_label.setStyleSheet(
                    "font-weight: bold; color: #006600;"
                )
                player_layout.addWidget(frontier_terrain_label)

                # Radio buttons for frontier terrain distance (1-6)
                frontier_button_group = QButtonGroup(self)
                frontier_buttons_layout = QHBoxLayout()

                for val in distance_allowed_values:
                    radio_button = QRadioButton(str(val))
                    frontier_button_group.addButton(radio_button, val)
                    frontier_buttons_layout.addWidget(radio_button)
                    if val == 1:  # Default selection
                        radio_button.setChecked(True)

                player_layout.addLayout(frontier_buttons_layout)
                self.roll_inputs[f"{player_name}_frontier"] = frontier_button_group

            form_layout.addRow("", player_group)

        inputs_v_layout.addWidget(distance_rolls_group)

        # Add inputs to Game tab
        self.tabbed_widget.add_game_content(inputs_widget)

        # Set help content for Help tab
        self._set_distance_rolls_help_text()

        main_layout.addWidget(self.tabbed_widget)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        main_layout.addSpacerItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # Navigation Buttons (Bottom)
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.setMaximumWidth(120)  # Limit button width
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit All Rolls")
        self.submit_button.setMaximumWidth(180)  # Limit button width
        if not self.player_setup_data:
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit_rolls)
        navigation_layout.addWidget(self.submit_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

    def _on_submit_rolls(self):
        submitted_rolls = []
        all_valid = True

        for input_key, button_group in self.roll_inputs.items():
            checked_button = button_group.checkedButton()

            if checked_button is None:
                terrain_type = "home" if "_home" in input_key else "frontier"
                player_name = input_key.replace("_home", "").replace("_frontier", "")
                self.status_label.setText(
                    f"Error: No roll value selected for {player_name}'s {terrain_type} terrain."
                )
                all_valid = False
                break

            roll_val = button_group.id(checked_button)

            # Convert input key to player name and terrain type for submission
            if "_home" in input_key:
                player_name = input_key.replace("_home", "")
                submitted_rolls.append((player_name, roll_val))
            elif "_frontier" in input_key:
                # Frontier terrain roll - this sets the frontier terrain face
                # We'll handle this separately as it affects the frontier terrain itself
                frontier_roll_val = roll_val
                # Store frontier terrain roll for later processing
                submitted_rolls.append(("__frontier__", frontier_roll_val))

        if all_valid:
            self.status_label.setText("")
            self.rolls_submitted.emit(submitted_rolls)

    def _set_distance_rolls_help_text(self):
        self.tabbed_widget.set_help_text(
            self.help_model.get_distance_rolls_help(self.frontier_terrain)
        )
