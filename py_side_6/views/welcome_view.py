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

        # Placeholder for player count selection (e.g., QComboBox)
        self.player_count_combo = QComboBox()
        self.player_count_combo.addItems(["2 Players", "3 Players", "4 Players"]) # Example
        layout.addWidget(QLabel("Select Number of Players:"))
        layout.addWidget(self.player_count_combo)

        # Placeholder for point value selection (e.g., QComboBox)
        self.point_value_combo = QComboBox()
        self.point_value_combo.addItems(["100 Points", "150 Points", "200 Points"]) # Example
        layout.addWidget(QLabel("Select Army Point Value:"))
        layout.addWidget(self.point_value_combo)

        proceed_button = QPushButton("Proceed to Player Setup")
        proceed_button.clicked.connect(self.proceed_signal.emit) # Emit the signal
        layout.addWidget(proceed_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
