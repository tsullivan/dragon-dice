from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QGridLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont # Added for QFont usage

from game_logic.engine import GameEngine # Assuming engine.py is in the same directory level
from models.help_text_model import HelpTextModel
from components.player_summary_widget import PlayerSummaryWidget # Import the new component
from components.melee_action_widget import MeleeActionWidget # Import MeleeActionWidget
from components.maneuver_input_widget import ManeuverInputWidget # Import ManeuverInputWidget
from components.action_choice_widget import ActionChoiceWidget # Import ActionChoiceWidget
from components.help_panel_widget import HelpPanelWidget # Import the new component
from components.active_effects_widget import ActiveEffectsWidget # Import ActiveEffectsWidget
import constants

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
        self.player_armies_info_group = QGroupBox("Player Summaries") # Give it a title
        self.player_armies_info_layout = QVBoxLayout(self.player_armies_info_group)
        # This layout will be populated with PlayerSummaryWidget instances
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

        # 2.1.1.c Active Effects Display
        self.active_effects_widget = ActiveEffectsWidget()
        main_content_v_layout.addWidget(self.active_effects_widget)


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
        
        # Maneuver Input Widget
        self.maneuver_input_widget = ManeuverInputWidget()
        self.maneuver_input_widget.maneuver_decision_made.connect(self.maneuver_decision_signal.emit)
        self.maneuver_input_widget.maneuver_details_submitted.connect(self.maneuver_input_submitted_signal.emit)
        self.dynamic_actions_layout.addWidget(self.maneuver_input_widget)

        # Action Choice Layout
        self.action_choice_widget = ActionChoiceWidget()
        self.action_choice_widget.action_selected.connect(self._handle_action_selected)
        self.dynamic_actions_layout.addWidget(self.action_choice_widget)
        self.action_choice_widget.hide() # Initially hidden

        # Melee Action Input Layout
        self.melee_action_widget = MeleeActionWidget()
        self.melee_action_widget.attacker_results_submitted.connect(self.attacker_melee_results_submitted.emit)
        self.melee_action_widget.defender_results_submitted.connect(self.defender_save_results_submitted.emit)
        self.dynamic_actions_layout.addWidget(self.melee_action_widget)
        self.melee_action_widget.hide() # Initially hidden
        
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
        self.help_panel = HelpPanelWidget("Info (Help Panel)") # Use the new component
        middle_section_layout.addWidget(self.help_panel, 1)

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
        
    def _handle_action_selected(self, action_type: str):
        if action_type == constants.ACTION_MELEE: # Use constant
            self.melee_action_selected_signal.emit()
        elif action_type == constants.ACTION_MISSILE: # Use constant
            self.missile_action_selected_signal.emit()
        elif action_type == constants.ACTION_MAGIC: # Use constant
            self.magic_action_selected_signal.emit()


    @Slot()
    def update_ui(self):
        # Update Phase Title
        self.phase_title_label.setText(f"Phase: {self.game_engine.get_current_phase_display()}")

        # Update Player Army Summaries
        for i in reversed(range(self.player_armies_info_layout.count())):
            widget = self.player_armies_info_layout.itemAt(i).widget()
            if widget: 
                widget.deleteLater()
        
        # Assuming game_engine.get_all_player_summary_data() returns a list of dicts:
        # [{'name': 'P1', 'captured_terrains': 0, 'terrains_to_win': 2, 
        #   'armies': [{'name': 'Home', 'points': 10, 'location': 'Highland'}, ...]}, ...]
        all_players_data = self.game_engine.get_all_player_summary_data() # You'll need to implement this in GameEngine
        for player_data in all_players_data:
            player_name = player_data.get("name", "Unknown Player")
            summary_widget = PlayerSummaryWidget(player_name) # Pass initial name
            summary_widget.update_summary(player_data) # Update with full data
            self.player_armies_info_layout.addWidget(summary_widget)
        if not all_players_data:
             self.player_armies_info_layout.addWidget(QLabel("No player data available."))


        # Update Current Player and Terrains
        current_player_name = self.game_engine.get_current_player_name()
        self.current_player_terrains_group.setTitle(f"{current_player_name}'s Turn")

        terrains_html = "<ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"
        # Example item from game_engine.get_relevant_terrains_info():
        # {'icon': '⛰️', 'name': 'Highland', 'type': 'Home', 'details': 'Face 1, Controlled by: Player 1'}

        relevant_terrains = self.game_engine.get_relevant_terrains_info() # Implement in GameEngine
        for terrain in relevant_terrains:
            terrains_html += f"<li>{terrain.get('icon', '')} {terrain.get('name', 'N/A')} ({terrain.get('type', 'N/A')}) - {terrain.get('details', '')}</li>"
        terrains_html += "</ul>"
        self.terrains_list_label.setHtml(terrains_html)
        if not relevant_terrains:
            self.terrains_list_label.setText("No terrain data available.")

        # Update Active Effects Display
        displayable_effects = self.game_engine.get_displayable_active_effects()
        self.active_effects_widget.update_effects(displayable_effects)

        # Manage visibility of action elements based on game state
        current_phase = self.game_engine.current_phase # Use the direct attribute
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Hide all dynamic action widgets by default
        self.maneuver_input_widget.hide()
        self.action_choice_widget.hide()
        self.melee_action_widget.hide() # Hide the MeleeActionWidget
        self.dragon_attack_prompt_label.hide()
        self.dragon_attack_continue_button.hide()
        
        # Eighth Face elements specific to the HTML structure
        is_eighth_face_phase = (current_phase == constants.PHASE_EIGHTH_FACE)
        self.eighth_face_description_label.setVisible(is_eighth_face_phase)
        self.eighth_face_input_field.setVisible(is_eighth_face_phase)
        self.eighth_face_add_button.setVisible(is_eighth_face_phase)
        if is_eighth_face_phase:
             self.eighth_face_input_field.clear()

        # Show relevant widgets based on current game step
        if current_march_step == constants.MARCH_STEP_DECIDE_MANEUVER:
            self.maneuver_input_widget.show()
            self.maneuver_input_widget.reset_to_decision() # Ensure it's showing Yes/No
        elif current_march_step == constants.MARCH_STEP_AWAITING_MANEUVER_INPUT:
            self.maneuver_input_widget.show() # The widget itself handles showing the input field
        elif current_march_step == constants.MARCH_STEP_SELECT_ACTION:
            self.action_choice_widget.show()
        elif current_action_step == constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL:
            self.melee_action_widget.show()
            self.melee_action_widget.show_attacker_input()
        elif current_action_step == constants.ACTION_STEP_AWAITING_DEFENDER_SAVES:
            self.melee_action_widget.show()
            self.melee_action_widget.show_defender_input()
        elif not current_march_step and not current_action_step: # General phase prompts
            if current_phase == constants.PHASE_DRAGON_ATTACK:
                self.dragon_attack_prompt_label.show()
                self.dragon_attack_continue_button.show()
            # Eighth face is handled above its own section
            # Add other general phase UIs here
            # e.g., elif current_phase == PHASE_SPECIES_ABILITIES: ...

        # Update Help Text
        help_key = current_action_step or current_march_step or current_phase
        self.help_panel.set_help_text(self.help_model.get_main_gameplay_help(help_key))
