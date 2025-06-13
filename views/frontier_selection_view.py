from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QSpacerItem, QSizePolicy, QHBoxLayout, QButtonGroup,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from models.help_text_model import HelpTextModel

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
        self.proposed_frontier_terrains = proposed_frontier_terrains # List of (player_name, terrain_type)
        self.help_model = HelpTextModel()
        self.selected_frontier_terrain_type = None # To store just the terrain type

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel("Determine Frontier & First Player")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        # First Player Selection with Buttons
        first_player_label = QLabel("Select First Player:")
        first_player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(first_player_label)

        self.first_player_button_group = QButtonGroup(self)
        first_player_buttons_layout = QHBoxLayout()
        if self.player_names:
            for i, name in enumerate(self.player_names):
                button = QPushButton(name)
                button.setCheckable(True)
                self.first_player_button_group.addButton(button, i) # Use index as ID
                first_player_buttons_layout.addWidget(button)
            if self.first_player_button_group.buttons():
                self.first_player_button_group.buttons()[0].setChecked(True) # Default to first player
        else:
            no_players_label = QLabel("No Players Available")
            no_players_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            first_player_buttons_layout.addWidget(no_players_label)
        layout.addLayout(first_player_buttons_layout)

        # Frontier Terrain Selection with Buttons
        frontier_terrain_label = QLabel("Select Frontier Terrain (Proposed by Players):")
        frontier_terrain_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(frontier_terrain_label)

        self.frontier_terrain_button_group = QButtonGroup(self)
        frontier_terrain_buttons_layout = QVBoxLayout() # Use QVBoxLayout for potentially many proposals

        if self.proposed_frontier_terrains:
            for i, (player_name, terrain_type) in enumerate(self.proposed_frontier_terrains):
                button_text = f"{terrain_type} (Proposed by {player_name})"
                button = QPushButton(button_text)
                button.setCheckable(True)
                # Store the actual terrain type with the button for easy retrieval
                button.setProperty("terrain_type", terrain_type)
                self.frontier_terrain_button_group.addButton(button, i)
                frontier_terrain_buttons_layout.addWidget(button)
            if self.frontier_terrain_button_group.buttons():
                self.frontier_terrain_button_group.buttons()[0].setChecked(True) # Default
        else:
            no_terrains_label = QLabel("No Frontier Terrains Proposed")
            no_terrains_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frontier_terrain_buttons_layout.addWidget(no_terrains_label)
        layout.addLayout(frontier_terrain_buttons_layout)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_group_box.setMaximumHeight(int(self.height() * 0.3)) # Apply constraint to the GroupBox
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self._set_frontier_help_text()
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)

        # Navigation buttons
        navigation_layout = QHBoxLayout() # Define navigation_layout
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit Selections")
        if not self.player_names:
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit)
        navigation_layout.addWidget(self.submit_button)

        # Correct order: Add navigation buttons, THEN the help panel.
        # Find the layout item containing help_group_box to remove it
        item_to_remove = layout.itemAt(layout.indexOf(help_group_box))
        if item_to_remove: layout.removeItem(item_to_remove)
        layout.addLayout(navigation_layout) # Add navigation
        layout.addWidget(help_group_box) # Re-add help panel at the end
        self.setLayout(layout)

    def _set_frontier_help_text(self):
        self.help_text_edit.setHtml(self.help_model.get_frontier_selection_help())

    def _on_submit(self):
        selected_player_button = self.first_player_button_group.checkedButton()
        selected_frontier_button = self.frontier_terrain_button_group.checkedButton()

        if not selected_player_button or not selected_frontier_button:
            # Handle error: a selection must be made, though defaults should prevent this
            print("Error: A selection for first player and frontier terrain must be made.")
            return

        selected_player_name = selected_player_button.text()
        # Retrieve the stored terrain type from the button's property
        selected_terrain_type = selected_frontier_button.property("terrain_type")

        self.frontier_data_submitted.emit(selected_player_name, selected_terrain_type)
