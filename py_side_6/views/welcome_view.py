from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout
from PySide6.QtCore import Qt, Signal

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
        self.point_values = {"100 Points": 100, "150 Points": 150, "200 Points": 200}
        self.point_value_combo.addItems(list(self.point_values.keys()))
        self.point_value_combo.currentIndexChanged.connect(self._on_point_value_changed)
        layout.addWidget(QLabel("Select Army Point Value:"))
        layout.addWidget(self.point_value_combo)

        proceed_button = QPushButton("Proceed to Player Setup")
        proceed_button.clicked.connect(self.proceed_signal.emit) # Emit the signal
        layout.addWidget(proceed_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

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
