from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Slot, Signal
from engine import GameEngine # Assuming engine.py is in the same directory level
from help_text_model import HelpTextModel

class MainGameplayView(QWidget):
    """
    The main view for displaying game state and player actions during gameplay.
    """
    # Define signals as class attributes
    maneuver_decision_signal = Signal(bool)
    maneuver_input_submitted_signal = Signal(str) # Emits maneuver details string
    melee_action_selected_signal = Signal()
    missile_action_selected_signal = Signal()
    magic_action_selected_signal = Signal()
    attacker_melee_results_submitted = Signal(str) # Emits attacker's melee roll string
    defender_save_results_submitted = Signal(str)  # Emits defender's save roll string

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.help_model = HelpTextModel()

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

        # --- Action Choice Layout (initially hidden) ---
        self.action_choice_layout = QHBoxLayout()
        self.melee_action_button = QPushButton("Melee Action")
        self.missile_action_button = QPushButton("Missile Action")
        self.magic_action_button = QPushButton("Magic Action")

        self.melee_action_button.clicked.connect(self.melee_action_selected_signal.emit)
        self.missile_action_button.clicked.connect(self.missile_action_selected_signal.emit)
        self.magic_action_button.clicked.connect(self.magic_action_selected_signal.emit)

        self.action_choice_layout.addWidget(self.melee_action_button)
        self.action_choice_layout.addWidget(self.missile_action_button)
        self.action_choice_layout.addWidget(self.magic_action_button)

        # --- Melee Action Input Layout (initially hidden) ---
        self.melee_input_layout = QVBoxLayout() # Use QVBoxLayout for vertical arrangement
        self.attacker_melee_label = QLabel("Attacker: Enter Melee Results:")
        self.attacker_melee_input = QLineEdit()
        self.attacker_melee_input.setPlaceholderText("e.g., '5 hits, 2 SAIs'")
        self.submit_attacker_melee_button = QPushButton("Submit Attacker Melee")
        self.submit_attacker_melee_button.clicked.connect(self._on_submit_attacker_melee)

        self.defender_save_label = QLabel("Defender: Enter Save Results:")
        self.defender_save_input = QLineEdit()
        self.defender_save_input.setPlaceholderText("e.g., '3 saves'")
        self.submit_defender_save_button = QPushButton("Submit Defender Saves")
        self.submit_defender_save_button.clicked.connect(self._on_submit_defender_saves)

        self.melee_input_layout.addWidget(self.attacker_melee_label)
        self.melee_input_layout.addWidget(self.attacker_melee_input)
        self.melee_input_layout.addWidget(self.submit_attacker_melee_button)
        self.melee_input_layout.addWidget(self.defender_save_label)
        self.melee_input_layout.addWidget(self.defender_save_input)
        self.melee_input_layout.addWidget(self.submit_defender_save_button)

        layout.addLayout(self.action_button_layout)
        layout.addLayout(self.action_choice_layout)
        layout.addLayout(self.melee_input_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setFixedHeight(200) # Adjust height as needed
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)

        self.setLayout(layout)
        self.update_ui() # Initial UI setup

        # Connect to game engine signals for UI updates
        self.game_engine.game_state_updated.connect(self.update_ui)

    def _on_submit_maneuver_input(self):
        maneuver_details = self.maneuver_input_field.text()
        self.maneuver_input_submitted_signal.emit(maneuver_details)
        self.maneuver_input_field.clear() # Clear after submission

    def _on_submit_attacker_melee(self):
        results = self.attacker_melee_input.text()
        self.attacker_melee_results_submitted.emit(results)
        # self.attacker_melee_input.clear() # Or clear later depending on flow

    def _on_submit_defender_saves(self):
        results = self.defender_save_input.text()
        self.defender_save_results_submitted.emit(results)
        # self.defender_save_input.clear()

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

        # Visibility for Action Choice
        # Assuming a state like "SELECT_ACTION" in game_engine.current_march_step
        show_action_choice = current_step == "SELECT_ACTION"
        self.melee_action_button.setVisible(show_action_choice)
        self.missile_action_button.setVisible(show_action_choice)
        self.magic_action_button.setVisible(show_action_choice)

        # Visibility for Melee Inputs
        show_attacker_melee_input = current_step == "AWAITING_ATTACKER_MELEE_ROLL"
        self.attacker_melee_label.setVisible(show_attacker_melee_input)
        self.attacker_melee_input.setVisible(show_attacker_melee_input)
        self.submit_attacker_melee_button.setVisible(show_attacker_melee_input)

        show_defender_save_input = current_step == "AWAITING_DEFENDER_SAVES"
        self.defender_save_label.setVisible(show_defender_save_input)
        self.defender_save_input.setVisible(show_defender_save_input)
        self.submit_defender_save_button.setVisible(show_defender_save_input)

        # Initially hide defender inputs if attacker inputs are shown first
        if show_attacker_melee_input:
            self.defender_save_label.setVisible(False)
            self.defender_save_input.setVisible(False)
            self.submit_defender_save_button.setVisible(False)
        
        self._set_main_gameplay_help_text(current_step)

    def _set_main_gameplay_help_text(self, current_step):
        self.help_text_edit.setHtml(
            self.help_model.get_main_gameplay_help(current_step)
        )
        # Add visibility logic for other steps (e.g., ROLL_FOR_MARCH) here
