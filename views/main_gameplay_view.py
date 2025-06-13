from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QGridLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Slot, Signal
from engine import GameEngine # Assuming engine.py is in the same directory level
from models.help_text_model import HelpTextModel

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

        # --- Game State Overview Layout ---
        self.game_state_layout = QGridLayout()
        self.game_state_layout.setContentsMargins(10, 10, 10, 10)
        
        # Player Army Details Section
        self.player_armies_group = QGroupBox("Player Armies")
        self.player_armies_layout = QVBoxLayout() # Each player's info will be a new label here
        self.player_armies_group.setLayout(self.player_armies_layout)
        self.game_state_layout.addWidget(self.player_armies_group, 0, 0)

        # Terrain Status Section
        self.terrain_status_group = QGroupBox("Terrain Status")
        self.terrain_status_layout = QVBoxLayout() # Each terrain's info will be a new label here
        self.terrain_status_group.setLayout(self.terrain_status_layout)
        self.game_state_layout.addWidget(self.terrain_status_group, 0, 1)

        layout.addLayout(self.game_state_layout)

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

        # --- Phase-Specific Prompts (e.g., Dragon Attack) ---
        self.phase_specific_layout = QVBoxLayout()
        self.dragon_attack_prompt_label = QLabel("<b>Dragon Attack Phase:</b> Resolve dragon attacks. (Details TBD)")
        self.dragon_attack_continue_button = QPushButton("Continue Past Dragon Attacks")
        self.dragon_attack_continue_button.clicked.connect(lambda: self.game_engine.advance_phase()) # Example action
        self.phase_specific_layout.addWidget(self.dragon_attack_prompt_label)
        self.phase_specific_layout.addWidget(self.dragon_attack_continue_button)

        self.eighth_face_prompt_label = QLabel("<b>Eighth Face Phase:</b> Resolve any 8th face abilities.")
        self.eighth_face_resolution_input = QLineEdit()
        self.eighth_face_resolution_input.setPlaceholderText("Optional: Note any resolutions (e.g., 'City used for recruit')")
        self.eighth_face_continue_button = QPushButton("Continue Past Eighth Face")
        self.eighth_face_continue_button.clicked.connect(lambda: self.game_engine.advance_phase())
        self.phase_specific_layout.addWidget(self.eighth_face_prompt_label)
        self.phase_specific_layout.addWidget(self.eighth_face_resolution_input)
        self.phase_specific_layout.addWidget(self.eighth_face_continue_button)

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
        layout.addLayout(self.phase_specific_layout)
        layout.addLayout(self.action_choice_layout)
        layout.addLayout(self.melee_input_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        # help_group_box.setMaximumHeight(int(self.height() * 0.3)) # Remove fixed height
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)
        layout.setStretchFactor(help_group_box, 1) # Allow help panel to stretch

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
        
        # Update Player Army Details
        # Clear previous army details
        for i in reversed(range(self.player_armies_layout.count())): 
            self.player_armies_layout.itemAt(i).widget().deleteLater()

        # TODO: Fetch actual army data from game_engine
        # Example: player_army_data = self.game_engine.get_all_player_army_details()
        # For now, using placeholder data based on initial setup:
        for player_info in self.game_engine.player_setup_data: # Assuming this structure exists
            name = player_info.get('name', 'N/A')
            # Points would be dynamic in a real game, this is initial setup points
            # TODO: Fetch dynamic army data (location, current points/health) from game_engine
            home_army_name = player_info.get('home_army_name', 'Home Army')
            home_army_points = player_info.get('home_army_points', 0)
            campaign_army_name = player_info.get('campaign_army_name', 'Campaign Army')
            campaign_army_points = player_info.get('campaign_army_points', 0)
            
            # Location and distance would be dynamic
            # Example: location = self.game_engine.get_army_location(name, home_army_name)
            # Example: distance = self.game_engine.get_army_distance_to_frontier(name, home_army_name)
            
            army_label_text = f"<b>{name}</b>:<br>"
            army_label_text += f"  Captured Terrains: {0}/2<br>" # Placeholder
            army_label_text += f"  <i>{home_army_name}</i>: {home_army_points} pts (at {player_info.get('home_terrain', 'N/A')})<br>"
            army_label_text += f"  <i>{campaign_army_name}</i>: {campaign_army_points} pts (at Frontier - Placeholder)<br>"
            if self.game_engine.num_players > 1: # Assuming num_players is accessible or passed
                horde_army_name = player_info.get('horde_army_name', 'Horde Army')
                horde_army_points = player_info.get('horde_army_points', 0)
                army_label_text += f"  <i>{horde_army_name}</i>: {horde_army_points} pts (at Opponent's Home - Placeholder)<br>"
            # This is a simplified display. You'd likely have more complex data structures
            # for armies, their locations (Home, Campaign, Horde, specific terrain name), etc.
            army_label = QLabel(army_label_text)
            self.player_armies_layout.addWidget(army_label)

        # Update Terrain Status
        # Clear previous terrain details
        for i in reversed(range(self.terrain_status_layout.count())):
            self.terrain_status_layout.itemAt(i).widget().deleteLater()
        # TODO: Fetch actual terrain status from game_engine
        # Example: terrain_statuses = self.game_engine.get_all_terrain_statuses()
        # For now, placeholder:
        terrain_status_label = QLabel(f"<b>{self.game_engine.frontier_terrain}</b> (Frontier): Face {self.game_engine.distance_rolls[0][1]} (Example)") # Placeholder
        self.terrain_status_layout.addWidget(terrain_status_label)
        # Add Home Terrains similarly

        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Default all interactive sections to hidden, then show the active one
        self.maneuver_yes_button.setVisible(False)
        self.maneuver_no_button.setVisible(False)
        self.maneuver_input_label.setVisible(False)
        self.maneuver_input_field.setVisible(False)
        self.submit_maneuver_button.setVisible(False)
        self.melee_action_button.setVisible(False)
        self.missile_action_button.setVisible(False)
        self.magic_action_button.setVisible(False)
        self.attacker_melee_label.setVisible(False)
        self.attacker_melee_input.setVisible(False)
        self.submit_attacker_melee_button.setVisible(False)
        self.defender_save_label.setVisible(False)
        self.defender_save_input.setVisible(False)
        self.submit_defender_save_button.setVisible(False)
        self.dragon_attack_prompt_label.setVisible(False)
        self.dragon_attack_continue_button.setVisible(False)
        self.eighth_face_prompt_label.setVisible(False)
        self.eighth_face_resolution_input.setVisible(False)
        self.eighth_face_continue_button.setVisible(False)
        # Add other phase-specific prompts to this default hiding list as they are created

        # Visibility for Maneuver Decision
        if current_march_step == "DECIDE_MANEUVER":
            self.maneuver_yes_button.setVisible(True)
            self.maneuver_no_button.setVisible(True)
        elif current_march_step == "AWAITING_MANEUVER_INPUT":
            self.maneuver_input_label.setVisible(True)
            self.maneuver_input_field.setVisible(True)
            self.submit_maneuver_button.setVisible(True)
        elif current_march_step == "SELECT_ACTION":
            self.melee_action_button.setVisible(True)
            self.missile_action_button.setVisible(True)
            self.magic_action_button.setVisible(True)
        elif current_action_step == "AWAITING_ATTACKER_MELEE_ROLL":
            self.attacker_melee_label.setVisible(True)
            self.attacker_melee_input.setVisible(True)
            self.attacker_melee_input.clear() # Clear previous input
            self.submit_attacker_melee_button.setVisible(True)
        elif current_action_step == "AWAITING_DEFENDER_SAVES":
            self.defender_save_label.setVisible(True)
            self.defender_save_input.setVisible(True)
            self.defender_save_input.clear() # Clear previous input
            self.submit_defender_save_button.setVisible(True)
        # Add elif for other action_steps (missile, magic) here

        # Visibility for Phase-Specific Prompts (only if no march/action step is active)
        elif not current_march_step and not current_action_step:
            if current_phase == "DRAGON_ATTACK":
                self.dragon_attack_prompt_label.setVisible(True)
                self.dragon_attack_continue_button.setVisible(True)
            elif current_phase == "EIGHTH_FACE":
                self.eighth_face_prompt_label.setVisible(True)
                self.eighth_face_resolution_input.setVisible(True)
                self.eighth_face_resolution_input.clear() # Clear previous input
                self.eighth_face_continue_button.setVisible(True)
            # Add other phases like SPECIES_ABILITIES, RESERVES here
        
        # Determine overall step for help text (can be phase, march_step, or action_step)
        help_step_key = current_action_step or current_march_step or current_phase
        self._set_main_gameplay_help_text(help_step_key)

    def _set_main_gameplay_help_text(self, current_step):
        self.help_text_edit.setHtml(
            self.help_model.get_main_gameplay_help(current_step)
        )
        # Add visibility logic for other steps (e.g., ROLL_FOR_MARCH) here
