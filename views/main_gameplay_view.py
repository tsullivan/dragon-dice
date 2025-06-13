from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QGridLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont # Added for QFont usage

from engine import GameEngine # Assuming engine.py is in the same directory level
from models.help_text_model import HelpTextModel

class MainGameplayView(QWidget):
    """
    The main view for displaying game state and player actions during gameplay.
    """
    # Define signals as class attributes from existing code
    maneuver_decision_signal = Signal(bool)
    maneuver_input_submitted_signal = Signal(str)
    melee_action_selected_signal = Signal()
    missile_action_selected_signal = Signal()
    magic_action_selected_signal = Signal()
    attacker_melee_results_submitted = Signal(str)
    defender_save_results_submitted = Signal(str)
    continue_to_next_phase_signal = Signal() # New signal

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.help_model = HelpTextModel()
        self.setWindowTitle("Dragon Dice - Gameplay")

        # Overall layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # 1. Phase Title
        self.phase_title_label = QLabel("Phase: Initializing...")
        phase_font = self.phase_title_label.font()
        phase_font.setPointSize(22) # Adjusted size
        phase_font.setBold(True)
        self.phase_title_label.setFont(phase_font)
        self.phase_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.phase_title_label)

        # 2. Middle Section (Main Content + Help Panel)
        middle_section_layout = QHBoxLayout()

        # 2.1. Left Side: Main Gameplay Content
        main_content_widget = QWidget()
        main_content_v_layout = QVBoxLayout(main_content_widget)
        main_content_v_layout.setContentsMargins(0,0,0,0)

        # 2.1.1. Top part of main content: Player Info and Current Player/Terrains
        top_main_content_h_layout = QHBoxLayout()

        # 2.1.1.a Player Armies Info (for all players)
        self.player_armies_info_group = QGroupBox() # No title, border for structure
        self.player_armies_info_layout = QVBoxLayout(self.player_armies_info_group)
        # This layout will be populated with QLabel or QTextEdit for each player's summary
        top_main_content_h_layout.addWidget(self.player_armies_info_group, 1)

        # 2.1.1.b Current Player and Terrains
        self.current_player_terrains_group = QGroupBox("Player X's Turn") # Title will be updated
        current_player_terrains_v_layout = QVBoxLayout(self.current_player_terrains_group)

        self.terrains_list_label = QTextEdit()
        self.terrains_list_label.setReadOnly(True)
        self.terrains_list_label.setPlaceholderText("Relevant terrains...")
        self.terrains_list_label.setStyleSheet("ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; }")
        current_player_terrains_v_layout.addWidget(self.terrains_list_label)
        current_player_terrains_v_layout.addStretch(1)

        top_main_content_h_layout.addWidget(self.current_player_terrains_group, 1)
        main_content_v_layout.addLayout(top_main_content_h_layout)

        # 2.1.2. Bottom part of main content: Phase Specific Actions
        self.phase_actions_group = QGroupBox() # No title, border for structure
        phase_actions_v_layout = QVBoxLayout(self.phase_actions_group)

        # Eighth Face (as per HTML)
        self.eighth_face_description_label = QLabel("Eighth Face Phase: Resolve any eighth face abilities")
        phase_actions_v_layout.addWidget(self.eighth_face_description_label)
        eighth_face_input_h_layout = QHBoxLayout()
        self.eighth_face_input_field = QLineEdit()
        self.eighth_face_input_field.setPlaceholderText("Describe ability resolution...")
        self.eighth_face_add_button = QPushButton("Add ability") # This button might trigger engine logic
        self.eighth_face_add_button.clicked.connect(self._on_eighth_face_add_ability)
        eighth_face_input_h_layout.addWidget(self.eighth_face_input_field)
        eighth_face_input_h_layout.addWidget(self.eighth_face_add_button)
        phase_actions_v_layout.addLayout(eighth_face_input_h_layout)
        
        # Container for other dynamic action buttons/inputs from old MainGameplayView
        self.dynamic_actions_layout = QVBoxLayout() # Will hold various action widgets
        
        # Maneuver decision buttons
        self.maneuver_decision_buttons_layout = QHBoxLayout()
        self.maneuver_yes_button = QPushButton("Maneuver: Yes")
        self.maneuver_no_button = QPushButton("Maneuver: No")
        self.maneuver_yes_button.clicked.connect(lambda: self.maneuver_decision_signal.emit(True))
        self.maneuver_no_button.clicked.connect(lambda: self.maneuver_decision_signal.emit(False))
        self.maneuver_decision_buttons_layout.addWidget(self.maneuver_yes_button)
        self.maneuver_decision_buttons_layout.addWidget(self.maneuver_no_button)
        self.dynamic_actions_layout.addLayout(self.maneuver_decision_buttons_layout)

        # Maneuver input elements
        self.maneuver_input_layout = QHBoxLayout()
        self.maneuver_input_label = QLabel("Enter Maneuver Details:")
        self.maneuver_input_field = QLineEdit()
        self.maneuver_input_field.setPlaceholderText("e.g., 'Flyers to hex 123'")
        self.submit_maneuver_button = QPushButton("Submit Maneuver")
        self.submit_maneuver_button.clicked.connect(self._on_submit_maneuver_input)
        self.maneuver_input_layout.addWidget(self.maneuver_input_label)
        self.maneuver_input_layout.addWidget(self.maneuver_input_field)
        self.maneuver_input_layout.addWidget(self.submit_maneuver_button)
        self.dynamic_actions_layout.addLayout(self.maneuver_input_layout)

        # Action Choice Layout
        self.action_choice_buttons_layout = QHBoxLayout()
        self.melee_action_button = QPushButton("Melee Action")
        self.missile_action_button = QPushButton("Missile Action")
        self.magic_action_button = QPushButton("Magic Action")
        self.melee_action_button.clicked.connect(self.melee_action_selected_signal.emit)
        self.missile_action_button.clicked.connect(self.missile_action_selected_signal.emit)
        self.magic_action_button.clicked.connect(self.magic_action_selected_signal.emit)
        self.action_choice_buttons_layout.addWidget(self.melee_action_button)
        self.action_choice_buttons_layout.addWidget(self.missile_action_button)
        self.action_choice_buttons_layout.addWidget(self.magic_action_button)
        self.dynamic_actions_layout.addLayout(self.action_choice_buttons_layout)

        # Melee Action Input Layout
        self.melee_inputs_layout_widget = QWidget() # Container for melee inputs
        melee_specific_inputs_v_layout = QVBoxLayout(self.melee_inputs_layout_widget)
        self.attacker_melee_label = QLabel("Attacker: Enter Melee Results:")
        self.attacker_melee_input = QLineEdit()
        self.attacker_melee_input.setPlaceholderText("e.g., '5 hits, 2 SAIs'")
        self.submit_attacker_melee_button = QPushButton("Submit Attacker Melee")
        self.submit_attacker_melee_button.clicked.connect(self._on_submit_attacker_melee)
        melee_specific_inputs_v_layout.addWidget(self.attacker_melee_label)
        melee_specific_inputs_v_layout.addWidget(self.attacker_melee_input)
        melee_specific_inputs_v_layout.addWidget(self.submit_attacker_melee_button)

        self.defender_save_label = QLabel("Defender: Enter Save Results:")
        self.defender_save_input = QLineEdit()
        self.defender_save_input.setPlaceholderText("e.g., '3 saves'")
        self.submit_defender_save_button = QPushButton("Submit Defender Saves")
        self.submit_defender_save_button.clicked.connect(self._on_submit_defender_saves)
        melee_specific_inputs_v_layout.addWidget(self.defender_save_label)
        melee_specific_inputs_v_layout.addWidget(self.defender_save_input)
        melee_specific_inputs_v_layout.addWidget(self.submit_defender_save_button)
        self.dynamic_actions_layout.addWidget(self.melee_inputs_layout_widget)
        
        # Other phase-specific prompts (like Dragon Attack) from old code
        self.dragon_attack_prompt_label = QLabel("<b>Dragon Attack Phase:</b> Resolve dragon attacks.")
        self.dragon_attack_continue_button = QPushButton("Continue Past Dragon Attacks")
        self.dragon_attack_continue_button.clicked.connect(lambda: self.game_engine.advance_phase()) # Example
        self.dynamic_actions_layout.addWidget(self.dragon_attack_prompt_label)
        self.dynamic_actions_layout.addWidget(self.dragon_attack_continue_button)

        phase_actions_v_layout.addLayout(self.dynamic_actions_layout) # Add all dynamic action widgets
        phase_actions_v_layout.addStretch(1)

        main_content_v_layout.addWidget(self.phase_actions_group)
        middle_section_layout.addWidget(main_content_widget, 3) # Main content takes more space

        # 2.2. Right Side: Help Panel
        help_panel_group = QGroupBox("Info (Help Panel)")
        help_panel_layout = QVBoxLayout(help_panel_group)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setStyleSheet("ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; } li { margin-bottom: 3px; }")
        help_panel_layout.addWidget(self.help_text_edit)
        middle_section_layout.addWidget(help_panel_group, 1)

        main_layout.addLayout(middle_section_layout)

        # 3. Continue Button
        self.continue_button = QPushButton("Continue to Next Phase")
        self.continue_button.clicked.connect(self._on_continue_clicked)
        main_layout.addWidget(self.continue_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        # Connect signals and initial updates
        self.game_engine.game_state_updated.connect(self.update_ui)
        # self.game_engine.phase_changed.connect(self.update_ui) # game_state_updated should cover phase changes
        # self.game_engine.current_player_changed.connect(self.update_ui) # Covered by game_state_updated
        
        self.update_ui() # Initial call

    def _on_submit_maneuver_input(self):
        maneuver_details = self.maneuver_input_field.text()
        self.maneuver_input_submitted_signal.emit(maneuver_details)
        self.maneuver_input_field.clear()

    def _on_submit_attacker_melee(self):
        results = self.attacker_melee_input.text()
        self.attacker_melee_results_submitted.emit(results)

    def _on_submit_defender_saves(self):
        results = self.defender_save_input.text()
        self.defender_save_results_submitted.emit(results)

    def _on_eighth_face_add_ability(self):
        ability_text = self.eighth_face_input_field.text()
        if ability_text:
            print(f"Eighth face ability logged: {ability_text}")
            # Here you might want to emit a signal or call an engine method
            # self.game_engine.log_eighth_face_resolution(ability_text)
            self.eighth_face_input_field.clear()
        # This button might not advance the phase directly;
        # "Continue to Next Phase" button usually does that.

    def _on_continue_clicked(self):
        print(f"MainGameplayView: Continue button clicked. Current phase: {self.game_engine.current_phase}")
        self.continue_to_next_phase_signal.emit()
        

    @Slot()
    def update_ui(self):
        # Update Phase Title
        self.phase_title_label.setText(f"Phase: {self.game_engine.get_current_phase_display()}")

        # Update Player Army Summaries
        for i in reversed(range(self.player_armies_info_layout.count())):
            widget = self.player_armies_info_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        
        # Assuming game_engine.get_all_player_summary_data() returns a list of dicts:
        # [{'name': 'P1', 'captured_terrains': 0, 'terrains_to_win': 2, 
        #   'armies': [{'name': 'Home', 'points': 10, 'location': 'Highland'}, ...]}, ...]
        all_players_data = self.game_engine.get_all_player_summary_data() # You'll need to implement this in GameEngine
        for player_data in all_players_data:
            summary_html = f"<b>{player_data.get('name', 'N/A')}'s Army:</b><ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"
            summary_html += f"<li>Captured Terrains: {player_data.get('captured_terrains', 0)}/{player_data.get('terrains_to_win', 2)}</li>"
            for army in player_data.get('armies', []):
                summary_html += f"<li>{army.get('name', 'N/A')}: {army.get('points', 0)}pts (at {army.get('location', 'N/A')})</li>"
            summary_html += "</ul>" # Removed <hr/> for cleaner list item separation if desired, or keep if you like the line.
            player_summary_label = QLabel(summary_html)
            player_summary_label.setWordWrap(True)
            self.player_armies_info_layout.addWidget(player_summary_label)
        if not all_players_data:
             self.player_armies_info_layout.addWidget(QLabel("No player data available."))


        # Update Current Player and Terrains
        current_player_name = self.game_engine.get_current_player_name()
        self.current_player_terrains_group.setTitle(f"{current_player_name}'s Turn")

        terrains_html = "<ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"
        # Assuming game_engine.get_relevant_terrains_info() returns:
        # [{'name': 'Flatland', 'type': 'Frontier', 'details': 'Face 3'}, 
        #  {'name': 'Highland', 'type': 'Home', 'details': 'Player 1 Home'}, ...]
        relevant_terrains = self.game_engine.get_relevant_terrains_info() # Implement in GameEngine
        for terrain in relevant_terrains:
            terrains_html += f"<li>{terrain.get('name', 'N/A')} ({terrain.get('type', 'N/A')})</li>"
        terrains_html += "</ul>"
        self.terrains_list_label.setHtml(terrains_html)
        if not relevant_terrains:
            self.terrains_list_label.setText("No terrain data available.")

        # Manage visibility of action elements based on game state
        current_phase = self.game_engine.current_phase # Use the direct attribute
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Hide all dynamic action widgets by default
        self.maneuver_yes_button.hide()
        self.maneuver_no_button.hide()
        self.maneuver_input_label.hide()
        self.maneuver_input_field.hide()
        self.submit_maneuver_button.hide()
        self.melee_action_button.hide()
        self.missile_action_button.hide()
        self.magic_action_button.hide()
        self.melee_inputs_layout_widget.hide() # Hide the whole group
        self.dragon_attack_prompt_label.hide()
        self.dragon_attack_continue_button.hide()
        
        # Eighth Face elements specific to the HTML structure
        is_eighth_face_phase = (current_phase == "EIGHTH_FACE")
        self.eighth_face_description_label.setVisible(is_eighth_face_phase)
        self.eighth_face_input_field.setVisible(is_eighth_face_phase)
        self.eighth_face_add_button.setVisible(is_eighth_face_phase)
        if is_eighth_face_phase:
             self.eighth_face_input_field.clear()


        # Show relevant widgets based on current game step
        if current_march_step == "DECIDE_MANEUVER":
            self.maneuver_yes_button.show()
            self.maneuver_no_button.show()
        elif current_march_step == "AWAITING_MANEUVER_INPUT":
            self.maneuver_input_label.show()
            self.maneuver_input_field.show()
            self.maneuver_input_field.clear()
            self.submit_maneuver_button.show()
        elif current_march_step == "SELECT_ACTION":
            self.melee_action_button.show()
            self.missile_action_button.show()
            self.magic_action_button.show()
        elif current_action_step == "AWAITING_ATTACKER_MELEE_ROLL":
            self.melee_inputs_layout_widget.show()
            self.attacker_melee_label.show()
            self.attacker_melee_input.show()
            self.attacker_melee_input.clear()
            self.submit_attacker_melee_button.show()
            self.defender_save_label.hide() # Hide defender parts
            self.defender_save_input.hide()
            self.submit_defender_save_button.hide()
        elif current_action_step == "AWAITING_DEFENDER_SAVES":
            self.melee_inputs_layout_widget.show()
            self.attacker_melee_label.hide() # Hide attacker parts
            self.attacker_melee_input.hide()
            self.submit_attacker_melee_button.hide()
            self.defender_save_label.show()
            self.defender_save_input.show()
            self.defender_save_input.clear()
            self.submit_defender_save_button.show()
        elif not current_march_step and not current_action_step: # General phase prompts
            if current_phase == "DRAGON_ATTACK":
                self.dragon_attack_prompt_label.show()
                self.dragon_attack_continue_button.show()
            # Eighth face is handled above its own section
            # Add other general phase UIs here

        # Update Help Text
        help_key = current_action_step or current_march_step or current_phase
        self.help_text_edit.setHtml(self.help_model.get_main_gameplay_help(help_key))
