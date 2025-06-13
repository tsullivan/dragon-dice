from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QComboBox, QHBoxLayout, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal

from help_text_model import HelpTextModel
class WelcomeView(QWidget):
    """
    The Welcome Screen view.
    Allows selection of number of players and point value.
    """
    # Define signals for interactions
    proceed_signal = Signal()
    player_count_selected_signal = Signal(int)
    point_value_selected_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_model = HelpTextModel()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Welcome to Dragon Dice Companion (PySide6)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Consider using QFont for styling
        layout.addWidget(title_label)
        font = title_label.font()
        font.setPointSize(24) # Example: Make title larger
        title_label.setFont(font)

        # Player count selection
        self.player_count_combo = QComboBox()
        self.player_counts = {"2 Players": 2, "3 Players": 3, "4 Players": 4}
        self.player_count_combo.addItems(list(self.player_counts.keys()))
        self.player_count_combo.currentIndexChanged.connect(self._on_player_count_changed)
        layout.addWidget(QLabel("Select Number of Players:"))
        layout.addWidget(self.player_count_combo)

        # Point value selection
        self.point_value_combo = QComboBox()
        self.point_values = {
            "15 Points": 15,
            "24 Points": 24,
            "30 Points": 30,
            "36 Points": 36,
            "60 Points": 60
        }
        self.point_value_combo.addItems(list(self.point_values.keys()))
        self.point_value_combo.currentIndexChanged.connect(self._on_point_value_changed)
        layout.addWidget(QLabel("Select Army Point Value:"))
        layout.addWidget(self.point_value_combo)

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setFixedHeight(150) # Adjust height as needed
        self._set_welcome_help_text()
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)

        proceed_button = QPushButton("Proceed to Player Setup")
        proceed_button.clicked.connect(self.proceed_signal.emit) # Emit the signal
        layout.addWidget(proceed_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def _set_welcome_help_text(self):
        self.help_text_edit.setHtml(self.help_model.get_welcome_help())

    def _on_player_count_changed(self, index):
        selected_text = self.player_count_combo.itemText(index)
        self.player_count_selected_signal.emit(self.player_counts[selected_text])

    def _on_point_value_changed(self, index):
        selected_text = self.point_value_combo.itemText(index)
        self.point_value_selected_signal.emit(self.point_values[selected_text])

    def emit_current_selections(self):
        """Emits the currently selected values. Useful for initialization."""
        current_player_text = self.player_count_combo.currentText()
        self.player_count_selected_signal.emit(self.player_counts[current_player_text])
        current_point_text = self.point_value_combo.currentText()
        self.point_value_selected_signal.emit(self.point_values[current_point_text])
