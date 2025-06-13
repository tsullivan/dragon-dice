from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QFormLayout, QSpacerItem, QSizePolicy, QHBoxLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QPalette, QColor
from models.help_text_model import HelpTextModel
from components.carousel import CarouselInputWidget # Updated import

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
        self.roll_inputs = {} # To store QLineEdit widgets: {player_name: QLineEdit}

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel("Enter Starting Distances")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        frontier_info_label = QLabel(f"Rolling distance to: {self.frontier_terrain}")
        frontier_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = frontier_info_label.font()
        font.setPointSize(16)
        frontier_info_label.setFont(font)
        layout.addWidget(frontier_info_label)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        # Allowed values for distance rolls (1-6 as per rules)
        distance_allowed_values = list(range(1, 7))

        for i, p_data in enumerate(self.player_setup_data):
            player_name = p_data.get("name", f"Player {i+1}")
            home_terrain = p_data.get("home_terrain", "N/A")
            
            label_text = f"{player_name} (Home: {home_terrain}):"
            roll_input = CarouselInputWidget(allowed_values=distance_allowed_values, initial_value=1)
            form_layout.addRow(label_text, roll_input)
            self.roll_inputs[player_name] = roll_input

        layout.addLayout(form_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_group_box.setMaximumHeight(int(self.height() * 0.3)) # Apply constraint to the GroupBox
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self._set_distance_rolls_help_text()
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)

        # Navigation buttons
        navigation_layout = QHBoxLayout() # Define navigation_layout
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        submit_button = QPushButton("Submit All Rolls")
        submit_button.clicked.connect(self._on_submit_rolls)
        navigation_layout.addWidget(submit_button)

        # Correct order: Add navigation buttons, THEN the help panel.
        # Instead of removing and re-adding, ensure correct add order.
        # The help_group_box was added directly to 'layout'.
        # We add navigation_layout first, then the help_group_box.
        layout.removeItem(layout.itemAt(layout.indexOf(help_group_box))) # Remove the help_group_box item
        layout.addLayout(navigation_layout)
        layout.addWidget(help_group_box)
        self.setLayout(layout)

    def _on_submit_rolls(self):
        submitted_rolls = []
        for player_name, roll_input_field in self.roll_inputs.items():
            try:
                roll_val = roll_input_field.value() # Get value from CarouselInputWidget
                # The carousel itself constrains to 1-6, so direct validation here is less critical
                # but can be kept as a safeguard if desired.
                submitted_rolls.append((player_name, roll_val))
            except AttributeError: # Should not happen
                self.status_label.setText(f"Error reading roll for {player_name}.")
                return 
        
        self.status_label.setText("") # Clear status on success
        self.rolls_submitted.emit(submitted_rolls)

    def _set_distance_rolls_help_text(self):
        self.help_text_edit.setHtml(
            self.help_model.get_distance_rolls_help(self.frontier_terrain)
        )
