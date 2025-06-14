from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QSpacerItem, QSizePolicy, QHBoxLayout, QButtonGroup,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont # Added for QFont

from models.help_text_model import HelpTextModel
from components.help_panel_widget import HelpPanelWidget # Import the new component

class FrontierSelectionView(QWidget):
    """
    View for selecting the first player and the frontier terrain.
    """
    # Emits (first_player_name, frontier_terrain_type)
    frontier_data_submitted = Signal(str, str)
    back_signal = Signal()

    def __init__(self, player_names, proposed_frontier_terrains, parent=None):
        super().__init__(parent)
        self.player_names = player_names
        # proposed_frontier_terrains is expected to be a list of (player_name, terrain_type)
        self.proposed_frontier_terrains = proposed_frontier_terrains
        self.help_model = HelpTextModel()
        self.setWindowTitle("Determine Frontier and First Player")

        # Overall vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title
        title_label = QLabel("Determine Frontier and First Player")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(22) # Adjusted size
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Middle Section (Selections on Left, Help on Right)
        middle_section_layout = QHBoxLayout()

        # Left Side: Selections
        selections_widget = QWidget() # Container for left side selections
        selections_v_layout = QVBoxLayout(selections_widget)
        selections_v_layout.setContentsMargins(0,0,0,0) # Remove margins if groupbox is not used

        # First Player Selection
        first_player_group = QGroupBox("Select First Player") # Visually group
        first_player_v_layout = QVBoxLayout(first_player_group) # Vertical layout inside group

        self.first_player_button_group = QButtonGroup(self)
        # Using QHBoxLayout for buttons if they fit, or QVBoxLayout if many
        first_player_buttons_h_layout = QHBoxLayout()
        if self.player_names:
            for i, name in enumerate(self.player_names):
                button = QPushButton(name)
                button.setCheckable(True)
                self.first_player_button_group.addButton(button, i) # Use index as ID
                first_player_buttons_h_layout.addWidget(button)
            if self.first_player_button_group.buttons():
                self.first_player_button_group.buttons()[0].setChecked(True) # Default
        else:
            no_players_label = QLabel("No Players Available")
            no_players_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            first_player_buttons_h_layout.addWidget(no_players_label)
        first_player_v_layout.addLayout(first_player_buttons_h_layout)
        selections_v_layout.addWidget(first_player_group)

        # Frontier Terrain Selection
        frontier_terrain_group = QGroupBox("Select Frontier Terrain") # Visually group
        frontier_terrain_v_layout = QVBoxLayout(frontier_terrain_group)

        self.frontier_terrain_button_group = QButtonGroup(self)
        # Using QVBoxLayout for terrain buttons as text can be long
        terrain_buttons_internal_v_layout = QVBoxLayout()
        if self.proposed_frontier_terrains:
            for i, (player_name, terrain_type) in enumerate(self.proposed_frontier_terrains):
                # Assuming terrain_type might include color info like "Terrain A (colorA, colorB)"
                # If not, adjust button_text accordingly.
                button_text = f"{terrain_type} - Proposed by {player_name}"
                button = QPushButton(button_text)
                button.setCheckable(True)
                button.setProperty("terrain_type", terrain_type) # Store actual terrain type
                self.frontier_terrain_button_group.addButton(button, i)
                terrain_buttons_internal_v_layout.addWidget(button)
            if self.frontier_terrain_button_group.buttons():
                self.frontier_terrain_button_group.buttons()[0].setChecked(True) # Default
        else:
            no_terrains_label = QLabel("No Frontier Terrains Proposed")
            no_terrains_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            terrain_buttons_internal_v_layout.addWidget(no_terrains_label)
        frontier_terrain_v_layout.addLayout(terrain_buttons_internal_v_layout)
        selections_v_layout.addWidget(frontier_terrain_group)
        selections_v_layout.addStretch(1) # Push groups to top

        middle_section_layout.addWidget(selections_widget, 1) # Selections take some space

        # Right Side: Help Panel
        self.help_panel = HelpPanelWidget("Info (Help Panel)") # Use the new component
        self._set_frontier_help_text()
        middle_section_layout.addWidget(self.help_panel, 1) # Help panel takes some space

        main_layout.addLayout(middle_section_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        # Navigation Buttons (Bottom)
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit Selections")
        if not self.player_names or not self.proposed_frontier_terrains: # Disable if no options
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit)
        navigation_layout.addWidget(self.submit_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

    def _set_frontier_help_text(self):
        self.help_panel.set_help_text(self.help_model.get_frontier_selection_help())

    def _on_submit(self):
        selected_player_button = self.first_player_button_group.checkedButton()
        selected_frontier_button = self.frontier_terrain_button_group.checkedButton()

        if not selected_player_button or not selected_frontier_button:
            print("Error: A selection for first player and frontier terrain must be made.")
            # Optionally, show a QMessageBox to the user
            return

        # Player name is directly the button text
        selected_player_name = selected_player_button.text()
        # Retrieve the stored terrain type from the button's property
        selected_terrain_type = selected_frontier_button.property("terrain_type")

        self.frontier_data_submitted.emit(selected_player_name, selected_terrain_type)
