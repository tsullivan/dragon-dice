from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit)
from PySide6.QtCore import Qt, Slot, Signal
from ..engine import GameEngine # Assuming engine.py is in the same directory level

class MainGameplayView(QWidget):
    """
    The main view for displaying game state and player actions during gameplay.
    """
    # Define signals as class attributes
    maneuver_decision_signal = Signal(bool)
    maneuver_input_submitted_signal = Signal(str) # Emits maneuver details string

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.title_label = QLabel("Main Gameplay")
        font = self.title_label.font()
        font.setPointSize(28)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.current_player_label = QLabel()
        self.current_phase_label = QLabel()
        
        status_font = self.current_player_label.font()
        status_font.setPointSize(18)
        self.current_player_label.setFont(status_font)
        self.current_phase_label.setFont(status_font)

        layout.addWidget(self.current_player_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.current_phase_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Action Buttons Layout ---
        self.action_button_layout = QHBoxLayout()

        # Maneuver decision buttons
        self.maneuver_yes_button = QPushButton("Maneuver: Yes")
        self.maneuver_no_button = QPushButton("Maneuver: No")
        self.maneuver_yes_button.clicked.connect(lambda: self.maneuver_decision_signal.emit(True))
        self.maneuver_no_button.clicked.connect(lambda: self.maneuver_decision_signal.emit(False))
        self.action_button_layout.addWidget(self.maneuver_yes_button)
        self.action_button_layout.addWidget(self.maneuver_no_button)

        # Maneuver input elements (initially hidden)
        self.maneuver_input_label = QLabel("Enter Maneuver Details:")
        self.maneuver_input_field = QLineEdit()
        self.maneuver_input_field.setPlaceholderText("e.g., 'Flyers to hex 123'")
        self.submit_maneuver_button = QPushButton("Submit Maneuver")
        self.submit_maneuver_button.clicked.connect(self._on_submit_maneuver_input)
        self.action_button_layout.addWidget(self.maneuver_input_label)
        self.action_button_layout.addWidget(self.maneuver_input_field)
        self.action_button_layout.addWidget(self.submit_maneuver_button)

        layout.addLayout(self.action_button_layout)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(layout)
        self.update_ui() # Initial UI setup

        # Connect to game engine signals for UI updates
        self.game_engine.game_state_updated.connect(self.update_ui)

    def _on_submit_maneuver_input(self):
        maneuver_details = self.maneuver_input_field.text()
        self.maneuver_input_submitted_signal.emit(maneuver_details)
        self.maneuver_input_field.clear() # Clear after submission

    @Slot()
    def update_ui(self):
        self.current_player_label.setText(f"Current Player: {self.game_engine.get_current_player_name()}")
        self.current_phase_label.setText(f"Phase: {self.game_engine.get_current_phase_display()}")
        
        current_step = self.game_engine.current_march_step

        # Visibility for Maneuver Decision
        show_maneuver_decision = current_step == "DECIDE_MANEUVER"
        self.maneuver_yes_button.setVisible(show_maneuver_decision)
        self.maneuver_no_button.setVisible(show_maneuver_decision)

        # Visibility for Maneuver Input
        show_maneuver_input = current_step == "AWAITING_MANEUVER_INPUT"
        self.maneuver_input_label.setVisible(show_maneuver_input)
        self.maneuver_input_field.setVisible(show_maneuver_input)
        self.submit_maneuver_button.setVisible(show_maneuver_input)
        # Add visibility logic for other steps (e.g., ROLL_FOR_MARCH) here
