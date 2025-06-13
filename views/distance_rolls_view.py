from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QFormLayout, QSpacerItem, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QPalette, QColor

class DistanceRollsView(QWidget):
    """
    View for players to input their distance rolls to the frontier.
    """
    # Emits a list of tuples: [(player_name, distance_roll_value), ...]
    rolls_submitted = Signal(list)

    def __init__(self, player_setup_data, frontier_terrain, parent=None):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        self.frontier_terrain = frontier_terrain
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

        # Validator for distance rolls (e.g., 1-12, or whatever the dice allow)
        # For now, let's assume a reasonable range like 1-20.
        roll_validator = QIntValidator(1, 20, self)

        for i, p_data in enumerate(self.player_setup_data):
            player_name = p_data.get("name", f"Player {i+1}")
            home_terrain = p_data.get("home_terrain", "N/A")
            
            label_text = f"{player_name} (Home: {home_terrain}):"
            roll_input = QLineEdit()
            roll_input.setValidator(roll_validator)
            roll_input.setPlaceholderText("e.g., 7")
            form_layout.addRow(label_text, roll_input)
            self.roll_inputs[player_name] = roll_input

        layout.addLayout(form_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        submit_button = QPushButton("Submit All Rolls")
        submit_button.clicked.connect(self._on_submit_rolls)
        layout.addWidget(submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _on_submit_rolls(self):
        submitted_rolls = []
        for player_name, roll_input_field in self.roll_inputs.items():
            roll_value_str = roll_input_field.text()
            if not roll_value_str: # Basic validation: ensure field is not empty
                self.status_label.setText(f"Error: Roll for {player_name} cannot be empty.")
                palette = self.status_label.palette()
                palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
                self.status_label.setPalette(palette)
                return
            submitted_rolls.append((player_name, int(roll_value_str)))
        
        self.status_label.setText("") # Clear status on success
        self.rolls_submitted.emit(submitted_rolls)
