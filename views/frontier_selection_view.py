from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.tabbed_view_widget import TabbedViewWidget

# No change, good comment
from models.help_text_model import HelpTextModel
from views.display_utils import format_terrain_type


class FrontierSelectionView(QWidget):
    """
    View for selecting the first player and the frontier terrain.
    """

    frontier_data_submitted = Signal(str, str)
    back_signal = Signal()

    def __init__(self, player_names, proposed_frontier_terrains, parent=None):
        super().__init__(parent)
        self.player_names = player_names
        self.proposed_frontier_terrains = proposed_frontier_terrains
        self.help_model = HelpTextModel()
        self.setWindowTitle("Determine Frontier and First Player")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title
        title_label = QLabel("Determine Frontier and First Player")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(22)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Tabbed Interface (Game and Help)
        self.tabbed_widget = TabbedViewWidget()

        # Game Tab Content (Selections)
        selections_widget = QWidget()
        selections_v_layout = QVBoxLayout(selections_widget)
        selections_v_layout.setContentsMargins(0, 0, 0, 0)

        # First Player Selection
        first_player_group = QGroupBox("Select First Player")
        first_player_v_layout = QVBoxLayout(first_player_group)

        self.first_player_button_group = QButtonGroup(self)
        first_player_buttons_h_layout = QHBoxLayout()
        if self.player_names:
            for i, name in enumerate(self.player_names):
                radio_button = QRadioButton(name)
                radio_button.setMaximumWidth(150)  # Prevent excessive stretching
                self.first_player_button_group.addButton(radio_button, i)
                first_player_buttons_h_layout.addWidget(radio_button)
                if i == 0:  # Default selection for first player
                    radio_button.setChecked(True)
        else:
            no_players_label = QLabel("No Players Available")
            no_players_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            first_player_buttons_h_layout.addWidget(no_players_label)
        first_player_v_layout.addLayout(first_player_buttons_h_layout)
        selections_v_layout.addWidget(first_player_group)

        # Frontier Terrain Selection
        frontier_terrain_group = QGroupBox("Select Frontier Terrain")
        frontier_terrain_v_layout = QVBoxLayout(frontier_terrain_group)

        self.frontier_terrain_button_group = QButtonGroup(self)
        terrain_buttons_internal_v_layout = QVBoxLayout()
        if self.proposed_frontier_terrains:
            for i, (player_name, terrain_type) in enumerate(self.proposed_frontier_terrains):
                formatted_terrain = format_terrain_type(terrain_type)
                button_text = f"{formatted_terrain} - Proposed by {player_name}"
                radio_button = QRadioButton(button_text)
                radio_button.setMaximumWidth(300)  # Prevent excessive stretching
                radio_button.setProperty("terrain_type", terrain_type)
                self.frontier_terrain_button_group.addButton(radio_button, i)
                terrain_buttons_internal_v_layout.addWidget(radio_button)
                if i == 0:  # Default selection for first terrain
                    radio_button.setChecked(True)
        else:
            no_terrains_label = QLabel("No Frontier Terrains Proposed")
            no_terrains_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            terrain_buttons_internal_v_layout.addWidget(no_terrains_label)
        frontier_terrain_v_layout.addLayout(terrain_buttons_internal_v_layout)
        selections_v_layout.addWidget(frontier_terrain_group)

        # Add selections to Game tab
        self.tabbed_widget.add_game_content(selections_widget)

        # Set help content for Help tab
        self._set_frontier_help_text()

        main_layout.addWidget(self.tabbed_widget)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Navigation Buttons (Bottom)
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.setMaximumWidth(120)  # Limit button width
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit Selections")
        self.submit_button.setMaximumWidth(180)  # Limit button width
        if not self.player_names or not self.proposed_frontier_terrains:
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit)
        navigation_layout.addWidget(self.submit_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

    def _set_frontier_help_text(self):
        self.tabbed_widget.set_help_text(self.help_model.get_frontier_selection_help())

    def _on_submit(self):
        selected_player_button = self.first_player_button_group.checkedButton()
        selected_frontier_button = self.frontier_terrain_button_group.checkedButton()

        if not selected_player_button or not selected_frontier_button:
            print("Error: A selection for first player and frontier terrain must be made.")
            return

        selected_player_name = selected_player_button.text()
        selected_terrain_type = selected_frontier_button.property("terrain_type")

        self.frontier_data_submitted.emit(selected_player_name, selected_terrain_type)
