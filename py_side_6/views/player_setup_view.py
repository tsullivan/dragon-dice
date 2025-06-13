from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """
    # Define signals for interactions
    next_player_signal = Signal()
    # Add more signals as needed, e.g., for terrain selection changes

    def __init__(self, num_players, point_value, parent=None): # TODO: Add current_player_index etc. as params
        super().__init__(parent)
        self.num_players = num_players
        self.point_value = point_value
        self.current_player_index = 0 # Start with the first player

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(f"Player {self.current_player_index + 1} Setup")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Consider using QFont for styling, similar to WelcomeView
        font = self.title_label.font()
        font.setPointSize(24) # Example: Make title larger
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Player Name Input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Player Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Placeholder for Home Terrain Selection
        layout.addWidget(QLabel("Home Terrain: [Terrain Selector Placeholder]"))

        # Placeholder for Army Details (Name, Points)
        layout.addWidget(QLabel("Home Army Name: [Input] Points: [Input]"))
        layout.addWidget(QLabel("Campaign Army Name: [Input] Points: [Input]"))
        if self.num_players > 1: # Conditional based on num_players
            layout.addWidget(QLabel("Horde Army Name: [Input] Points: [Input]"))

        # Placeholder for Frontier Terrain Proposal
        layout.addWidget(QLabel("Propose Frontier Terrain: [Terrain Selector Placeholder]"))

        next_button = QPushButton("Next Player / Start Game") # Text changes based on current player
        next_button.clicked.connect(self.next_player_signal.emit)
        layout.addWidget(next_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def update_for_player(self, player_index):
        self.current_player_index = player_index
        self.title_label.setText(f"Player {self.current_player_index + 1} Setup")
        # TODO: Clear/reset input fields for the new player
        # TODO: Change "Next Player" button text to "Start Game" if it's the last player