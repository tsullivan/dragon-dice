from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QGridLayout,
    QTextEdit,
    QGroupBox,
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont  # Added for QFont usage

# No change, good comment
from game_logic.engine import GameEngine
from models.help_text_model import HelpTextModel
from components.player_summary_widget import PlayerSummaryWidget
from components.melee_action_widget import MeleeActionWidget
from components.acting_army_widget import ActingArmyWidget
from components.maneuver_input_widget import ManeuverInputWidget
from components.action_decision_widget import ActionDecisionWidget
from components.action_choice_widget import ActionChoiceWidget
from components.tabbed_view_widget import TabbedViewWidget
from components.active_effects_widget import ActiveEffectsWidget
from views.maneuver_dialog import ManeuverDialog
import constants


class MainGameplayView(QWidget):
    """
    The main view for displaying game state and player actions during gameplay.
    """

    maneuver_decision_signal = Signal(bool)
    maneuver_input_submitted_signal = Signal(str)
    melee_action_selected_signal = Signal()
    missile_action_selected_signal = Signal()
    magic_action_selected_signal = Signal()
    attacker_melee_results_submitted = Signal(str)
    defender_save_results_submitted = Signal(str)
    continue_to_next_phase_signal = Signal()

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.help_model = HelpTextModel()

        # Track phase completion to control continue button
        self.phase_actions_completed = False
        self.current_phase_requirements_met = False

        self.setWindowTitle("Dragon Dice - Gameplay")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # 1. Phase Title
        self.phase_title_label = QLabel("Phase: Initializing...")
        phase_font = self.phase_title_label.font()
        phase_font.setPointSize(22)
        phase_font.setBold(True)
        self.phase_title_label.setFont(phase_font)
        self.phase_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.phase_title_label)

        # 2. Tabbed Interface (Game and Help)
        self.tabbed_widget = TabbedViewWidget()

        # Game Tab Content (Main Gameplay Content)
        main_content_widget = QWidget()
        main_content_v_layout = QVBoxLayout(main_content_widget)
        main_content_v_layout.setContentsMargins(0, 0, 0, 0)

        # 2.1.1. Top part of main content: Player Info and Current Player/Terrains
        top_main_content_h_layout = QHBoxLayout()

        self.player_armies_info_group = QGroupBox("Player Summaries")
        self.player_armies_info_layout = QVBoxLayout(self.player_armies_info_group)
        top_main_content_h_layout.addWidget(self.player_armies_info_group, 1)

        self.current_player_terrains_group = QGroupBox("Player X's Turn")
        current_player_terrains_v_layout = QVBoxLayout(
            self.current_player_terrains_group
        )

        self.terrains_list_label = QTextEdit()
        self.terrains_list_label.setReadOnly(True)
        self.terrains_list_label.setPlaceholderText("Relevant terrains...")
        self.terrains_list_label.setMaximumHeight(
            120
        )  # Limit height to prevent excessive stretching
        self.terrains_list_label.setStyleSheet(
            "ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; }"
        )
        current_player_terrains_v_layout.addWidget(self.terrains_list_label)

        top_main_content_h_layout.addWidget(self.current_player_terrains_group, 1)
        main_content_v_layout.addLayout(top_main_content_h_layout)

        # 2.1.1.c Active Effects Display
        self.active_effects_widget = ActiveEffectsWidget()
        main_content_v_layout.addWidget(self.active_effects_widget)

        # 2.1.2. Bottom part of main content: Phase Specific Actions
        self.phase_actions_group = QGroupBox()
        phase_actions_v_layout = QVBoxLayout(self.phase_actions_group)

        self.eighth_face_description_label = QLabel(
            "Eighth Face Phase: Resolve any eighth face abilities"
        )
        phase_actions_v_layout.addWidget(self.eighth_face_description_label)
        eighth_face_input_h_layout = QHBoxLayout()
        self.eighth_face_input_field = QLineEdit()
        self.eighth_face_input_field.setMaximumWidth(
            300
        )  # Prevent stretching across full width
        self.eighth_face_input_field.setPlaceholderText(
            "Describe ability resolution..."
        )
        self.eighth_face_add_button = QPushButton("Add ability")
        self.eighth_face_add_button.setMaximumWidth(120)  # Limit button width
        self.eighth_face_add_button.clicked.connect(self._on_eighth_face_add_ability)
        eighth_face_input_h_layout.addWidget(self.eighth_face_input_field)
        eighth_face_input_h_layout.addWidget(self.eighth_face_add_button)
        phase_actions_v_layout.addLayout(eighth_face_input_h_layout)

        self.dynamic_actions_layout = QVBoxLayout()

        # Acting Army Selection Widget
        self.acting_army_widget = ActingArmyWidget()
        self.acting_army_widget.acting_army_chosen.connect(
            self._handle_acting_army_chosen
        )
        self.dynamic_actions_layout.addWidget(self.acting_army_widget)
        self.acting_army_widget.hide()

        # Maneuver Input Widget
        self.maneuver_input_widget = ManeuverInputWidget()
        self.maneuver_input_widget.maneuver_decision_made.connect(
            self._handle_maneuver_decision
        )
        self.dynamic_actions_layout.addWidget(self.maneuver_input_widget)

        # Action Decision Widget
        self.action_decision_widget = ActionDecisionWidget()
        self.action_decision_widget.action_decision_made.connect(
            self._handle_action_decision
        )
        self.dynamic_actions_layout.addWidget(self.action_decision_widget)
        self.action_decision_widget.hide()

        # Action Choice Layout
        self.action_choice_widget = ActionChoiceWidget()
        self.action_choice_widget.action_selected.connect(self._handle_action_selected)
        self.dynamic_actions_layout.addWidget(self.action_choice_widget)
        self.action_choice_widget.hide()

        # Melee Action Input Layout
        self.melee_action_widget = MeleeActionWidget()
        self.melee_action_widget.attacker_results_submitted.connect(
            self.attacker_melee_results_submitted.emit
        )
        self.melee_action_widget.defender_results_submitted.connect(
            self.defender_save_results_submitted.emit
        )
        self.dynamic_actions_layout.addWidget(self.melee_action_widget)
        self.melee_action_widget.hide()

        self.dragon_attack_prompt_label = QLabel(
            "<b>Dragon Attack Phase:</b> Resolve dragon attacks."
        )
        self.dragon_attack_continue_button = QPushButton("Continue Past Dragon Attacks")
        self.dragon_attack_continue_button.setMaximumWidth(250)  # Limit button width
        self.dragon_attack_continue_button.clicked.connect(
            lambda: self.game_engine.advance_phase()
        )
        self.dynamic_actions_layout.addWidget(self.dragon_attack_prompt_label)
        self.dynamic_actions_layout.addWidget(self.dragon_attack_continue_button)

        phase_actions_v_layout.addLayout(self.dynamic_actions_layout)

        main_content_v_layout.addWidget(self.phase_actions_group)

        # Add main content to Game tab
        self.tabbed_widget.add_game_content(main_content_widget)

        main_layout.addWidget(self.tabbed_widget)

        # 3. Continue Button
        self.continue_button = QPushButton("Continue to Next Phase")
        self.continue_button.setMaximumWidth(220)  # Limit button width
        self.continue_button.setEnabled(
            False
        )  # Disabled by default until phase actions are completed
        self.continue_button.clicked.connect(self._on_continue_clicked)
        main_layout.addWidget(self.continue_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        # Connect to game engine signals
        self.game_engine.game_state_updated.connect(self.update_ui)
        self.game_engine.current_phase_changed.connect(self.update_ui)
        self.game_engine.current_player_changed.connect(self.update_ui)

        self.update_ui()  # Initial call

    def _on_eighth_face_add_ability(self):
        ability_text = self.eighth_face_input_field.text()
        if ability_text:
            print(f"Eighth face ability logged: {ability_text}")
            # Here you might want to emit a signal or call an engine method
            self.eighth_face_input_field.clear()

    def _on_continue_clicked(self):
        print(
            f"MainGameplayView: Continue button clicked. Current phase: {
              self.game_engine.current_phase}"
        )
        self.continue_to_next_phase_signal.emit()

    def _handle_acting_army_chosen(self, army_data: dict):
        """Handle acting army selection."""
        print(f"Acting army chosen: {army_data.get('name')}")
        self.game_engine.choose_acting_army(army_data)

    def _handle_maneuver_decision(self, wants_to_maneuver: bool):
        """Handle maneuver decision - show dialog if yes, proceed if no."""
        if wants_to_maneuver:
            self._show_maneuver_dialog()
        else:
            # Player chose not to maneuver, proceed to action decision
            self.maneuver_decision_signal.emit(False)
            self.game_engine.march_step_change_requested.emit(
                constants.MARCH_STEP_DECIDE_ACTION
            )
            self.game_engine._current_march_step = constants.MARCH_STEP_DECIDE_ACTION
            self.game_engine.game_state_updated.emit()

    def _handle_action_decision(self, wants_to_take_action: bool):
        """Handle action decision."""
        print(f"Action decision: {wants_to_take_action}")
        self.game_engine.decide_action(wants_to_take_action)

    def _show_maneuver_dialog(self):
        """Show the maneuver dialog for proper maneuver flow."""
        try:
            # Get the current acting army
            acting_army = self.game_engine.get_current_acting_army()
            if not acting_army:
                print("No acting army selected")
                return

            current_player = self.game_engine.get_current_player_name()
            all_players_data = self.game_engine.get_all_players_data()
            terrain_data = self.game_engine.get_all_terrain_data()

            # Create and show maneuver dialog with the acting army
            dialog = ManeuverDialog(
                current_player_name=current_player,
                acting_army=acting_army,
                all_players_data=all_players_data,
                terrain_data=terrain_data,
                parent=self,
            )

            dialog.maneuver_completed.connect(self._handle_maneuver_completed)
            dialog.maneuver_cancelled.connect(self._handle_maneuver_cancelled)

            dialog.exec()

        except Exception as e:
            print(f"Error showing maneuver dialog: {e}")
            # Fallback to simple decision
            self.maneuver_decision_signal.emit(True)

    def _handle_maneuver_completed(self, maneuver_result: dict):
        """Handle completed maneuver from dialog."""
        print(f"Maneuver completed: {maneuver_result}")

        # Apply maneuver results to game state (including terrain face changes)
        if maneuver_result.get("success"):
            success = self.game_engine.apply_maneuver_results(maneuver_result)
            if success:
                army_name = maneuver_result.get("army", {}).get("name", "Unknown Army")
                location = maneuver_result.get("location", "Unknown")
                direction = maneuver_result.get("direction", "UP")
                old_face = maneuver_result.get("old_face", "?")
                new_face = maneuver_result.get("new_face", "?")
                result_text = f"{army_name} maneuvered at {location} - turned terrain {direction} from face {old_face} to {new_face}"
                self.maneuver_input_submitted_signal.emit(result_text)
            else:
                print("Failed to apply maneuver results")
        
        # Emit the maneuver decision signal
        self.maneuver_decision_signal.emit(True)

        # Transition to action decision step
        self.game_engine.march_step_change_requested.emit(
            constants.MARCH_STEP_DECIDE_ACTION
        )
        self.game_engine._current_march_step = constants.MARCH_STEP_DECIDE_ACTION

        # Update UI
        self.game_state_updated.emit()

    def _handle_maneuver_cancelled(self):
        """Handle cancelled maneuver from dialog."""
        print("Maneuver cancelled")
        # Reset the maneuver widget to decision state
        self.maneuver_input_widget.reset_to_decision()

    def _update_continue_button_state(self):
        """Update the continue button state based on current phase requirements."""
        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Determine if continue button should be enabled
        should_enable = False

        if current_phase in [constants.PHASE_FIRST_MARCH, constants.PHASE_SECOND_MARCH]:
            # March phases require either maneuver decision or action completion
            if current_march_step == constants.MARCH_STEP_DECIDE_MANEUVER:
                should_enable = False  # Must make maneuver decision first
            elif current_march_step == constants.MARCH_STEP_SELECT_ACTION:
                should_enable = False  # Must select an action first
            elif current_action_step:
                should_enable = self.phase_actions_completed
            else:
                should_enable = self.phase_actions_completed
        elif current_phase == constants.PHASE_EIGHTH_FACE:
            # Can always continue from eighth face (optional actions)
            should_enable = True
        elif current_phase == constants.PHASE_DRAGON_ATTACK:
            # Can always continue from dragon attack
            should_enable = True
        else:
            # Other phases can be continued
            should_enable = True

        self.continue_button.setEnabled(should_enable)

        # Update button text based on state
        if should_enable:
            self.continue_button.setText("Continue to Next Phase")
        else:
            if current_march_step == constants.MARCH_STEP_DECIDE_MANEUVER:
                self.continue_button.setText("Make Maneuver Decision First")
            elif current_march_step == constants.MARCH_STEP_SELECT_ACTION:
                self.continue_button.setText("Select an Action First")
            else:
                self.continue_button.setText("Complete Required Actions")

    def _handle_action_selected(self, action_type: str):
        if action_type == constants.ACTION_MELEE:
            self.melee_action_selected_signal.emit()
        elif action_type == constants.ACTION_MISSILE:
            self.missile_action_selected_signal.emit()
        elif action_type == constants.ACTION_MAGIC:  # Use constant
            self.magic_action_selected_signal.emit()

        # Mark that an action has been selected
        self.phase_actions_completed = True
        self._update_continue_button_state()

    @Slot()
    def update_ui(self):
        # Check if phase changed to reset completion state
        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step

        # Reset phase actions completed when entering a new phase or step
        if not hasattr(self, "_last_phase_state"):
            self._last_phase_state = (current_phase, current_march_step)
        elif self._last_phase_state != (current_phase, current_march_step):
            self.phase_actions_completed = False
            self._last_phase_state = (current_phase, current_march_step)

        # Update Phase Title
        current_phase_display = self.game_engine.get_current_phase_display()
        phase_text = f"Phase: {current_phase_display}"
        self.phase_title_label.setText(phase_text)

        # Update Player Army Summaries
        for i in reversed(range(self.player_armies_info_layout.count())):
            widget = self.player_armies_info_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        all_players_data = self.game_engine.get_all_player_summary_data()
        terrain_data = self.game_engine.get_all_terrain_data()
        for player_data in all_players_data:
            player_name = player_data.get("name", "Unknown Player")
            summary_widget = PlayerSummaryWidget(player_name)
            summary_widget.update_summary(player_data, terrain_data)
            self.player_armies_info_layout.addWidget(summary_widget)
        if not all_players_data:
            self.player_armies_info_layout.addWidget(
                QLabel("No player data available.")
            )

        # Update Current Player and Terrains
        current_player_name = self.game_engine.get_current_player_name()
        self.current_player_terrains_group.setTitle(f"{current_player_name}'s Turn")

        terrains_html = "<ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"

        relevant_terrains = self.game_engine.get_relevant_terrains_info()
        for terrain in relevant_terrains:
            terrains_html += f"<li>{terrain.get('icon', '')} {terrain.get('name', 'N/A')} ({
                terrain.get('type', 'N/A')}) - {terrain.get('details', '')}</li>"
        terrains_html += "</ul>"
        self.terrains_list_label.setHtml(terrains_html)
        if not relevant_terrains:
            self.terrains_list_label.setText("No terrain data available.")

        # Update Active Effects Display
        displayable_effects = self.game_engine.get_displayable_active_effects()
        self.active_effects_widget.update_effects(displayable_effects)

        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Hide all dynamic widgets initially
        self.acting_army_widget.hide()
        self.maneuver_input_widget.hide()
        self.action_decision_widget.hide()
        self.action_choice_widget.hide()
        self.melee_action_widget.hide()
        self.dragon_attack_prompt_label.hide()
        self.dragon_attack_continue_button.hide()

        is_eighth_face_phase = current_phase == constants.PHASE_EIGHTH_FACE
        self.eighth_face_description_label.setVisible(is_eighth_face_phase)
        self.eighth_face_input_field.setVisible(is_eighth_face_phase)
        self.eighth_face_add_button.setVisible(is_eighth_face_phase)
        if is_eighth_face_phase:
            self.eighth_face_input_field.clear()

        # Show appropriate widgets based on current march step
        if current_march_step == constants.MARCH_STEP_CHOOSE_ACTING_ARMY:
            self.acting_army_widget.show()
            # Set available armies for the current player
            current_player = self.game_engine.get_current_player_name()
            all_players_data = self.game_engine.get_all_players_data()
            terrain_data = self.game_engine.get_all_terrain_data()
            player_data = all_players_data.get(current_player, {})
            available_armies = []

            for army_type, army_data in player_data.get("armies", {}).items():
                army_info = {
                    "name": army_data.get("name", f"{army_type.title()} Army"),
                    "army_type": army_type,
                    "location": army_data.get("location", "Unknown"),
                    "units": army_data.get("units", []),
                    "unique_id": army_data.get(
                        "unique_id", f"{current_player}_{army_type}"
                    ),
                }
                available_armies.append(army_info)

            self.acting_army_widget.set_available_armies(available_armies, terrain_data)

        elif current_march_step == constants.MARCH_STEP_DECIDE_MANEUVER:
            self.maneuver_input_widget.show()
            self.maneuver_input_widget.reset_to_decision()

        elif current_march_step == constants.MARCH_STEP_DECIDE_ACTION:
            self.action_decision_widget.show()
            # Set the acting army for the action decision widget
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.action_decision_widget.set_acting_army(acting_army, terrain_data)

        elif current_march_step == constants.MARCH_STEP_SELECT_ACTION:
            self.action_choice_widget.show()
            # Set available actions based on acting army's terrain die face
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.action_choice_widget.set_available_actions(
                    acting_army, terrain_data
                )
        elif current_action_step == constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL:
            self.melee_action_widget.show()
            self.melee_action_widget.show_attacker_input()
        elif current_action_step == constants.ACTION_STEP_AWAITING_DEFENDER_SAVES:
            self.melee_action_widget.show()
            self.melee_action_widget.show_defender_input()
        elif not current_march_step and not current_action_step:
            if current_phase == constants.PHASE_DRAGON_ATTACK:
                self.dragon_attack_prompt_label.show()
                self.dragon_attack_continue_button.show()

        # Special handling for first turn
        if (
            current_phase == constants.PHASE_FIRST_MARCH
            and hasattr(self.game_engine, "_is_very_first_turn")
            and self.game_engine._is_very_first_turn
            and not current_march_step
        ):
            help_key = constants.PHASE_FIRST_MARCH
        else:
            help_key = current_action_step or current_march_step or current_phase

        self.tabbed_widget.set_help_text(
            self.help_model.get_main_gameplay_help(help_key)
        )

        # Update continue button state based on current phase requirements
        self._update_continue_button_state()
