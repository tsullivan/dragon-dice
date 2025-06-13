from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QFormLayout, QSpacerItem, QSizePolicy, QHBoxLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont # Added for QFont

from models.help_text_model import HelpTextModel
from components.carousel import CarouselInputWidget

class DistanceRollsView(QWidget):
    """
    View for players to input their distance rolls to the frontier.
    """
    # Emits a list of tuples: [(player_name, distance_roll_value), ...]
    rolls_submitted = Signal(list)
    back_signal = Signal()

    def __init__(self, player_setup_data, frontier_terrain, parent=None):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        self.frontier_terrain = frontier_terrain
        self.help_model = HelpTextModel()
        self.roll_inputs = {} # To store CarouselInputWidget widgets: {player_name: CarouselInputWidget}
        self.setWindowTitle("Enter Starting Distances")

        # Overall vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title
        title_label = QLabel("Enter Starting Distances")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(22) # Adjusted size
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Sub-title for Frontier Terrain
        frontier_info_label = QLabel(f"Rolling distance to: {self.frontier_terrain}")
        frontier_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = frontier_info_label.font()
        font.setPointSize(16)
        frontier_info_label.setFont(font)
        main_layout.addWidget(frontier_info_label)

        # Middle Section (Inputs on Left, Help on Right)
        middle_section_layout = QHBoxLayout()

        # Left Side: Distance Roll Inputs
        inputs_widget = QWidget() # Container for left side inputs
        inputs_v_layout = QVBoxLayout(inputs_widget)
        inputs_v_layout.setContentsMargins(0,0,0,0)

        distance_rolls_group = QGroupBox("Player Distance Rolls")
        form_layout = QFormLayout(distance_rolls_group) # Use QFormLayout for label-input pairs
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(10)

        # Allowed values for distance rolls (1-6 as per rules)
        distance_allowed_values = list(range(1, 7))

        for i, p_data in enumerate(self.player_setup_data):
            player_name = p_data.get("name", f"Player {i+1}")
            home_terrain = p_data.get("home_terrain", "N/A")
            
            label_text = f"{player_name} (Home: {home_terrain}):"
            roll_input_widget = CarouselInputWidget(allowed_values=distance_allowed_values, initial_value=1)
            form_layout.addRow(label_text, roll_input_widget)
            self.roll_inputs[player_name] = roll_input_widget
        
        inputs_v_layout.addWidget(distance_rolls_group)
        inputs_v_layout.addStretch(1) # Push group to top

        middle_section_layout.addWidget(inputs_widget, 1) # Inputs take some space

        # Right Side: Help Panel
        help_panel_group = QGroupBox("Info (Help Panel)")
        help_panel_layout = QVBoxLayout(help_panel_group)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setStyleSheet("ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; } li { margin-bottom: 3px; }")
        self._set_distance_rolls_help_text()
        help_panel_layout.addWidget(self.help_text_edit)
        middle_section_layout.addWidget(help_panel_group, 1) # Help panel takes some space

        main_layout.addLayout(middle_section_layout)
        
        self.status_label = QLabel("") # For any error messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Navigation Buttons (Bottom)
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit All Rolls")
        if not self.player_setup_data: # Disable if no players
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit_rolls)
        navigation_layout.addWidget(self.submit_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

    def _on_submit_rolls(self):
        submitted_rolls = []
        all_valid = True
        for player_name, roll_input_carousel in self.roll_inputs.items():
            roll_val = roll_input_carousel.value()
            # CarouselInputWidget should inherently provide a valid value from its allowed_values
            if roll_val is None: # Should not happen if carousel is initialized properly
                self.status_label.setText(f"Error: No roll value for {player_name}.")
                all_valid = False
                break
            submitted_rolls.append((player_name, roll_val))
        
        if all_valid:
            self.status_label.setText("") # Clear status on success
            self.rolls_submitted.emit(submitted_rolls)
        else:
            # Status label already set by the loop
            pass


    def _set_distance_rolls_help_text(self):
        self.help_text_edit.setHtml(
            self.help_model.get_distance_rolls_help(self.frontier_terrain)
        )
