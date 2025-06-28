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
from views.action_dialog import ActionDialog
import constants
from utils.display_utils import format_terrain_summary, format_player_turn_label


class MainGameplayView(QWidget):
    """
    The main view for displaying game state and player actions during gameplay.
    """

    maneuver_decision_signal = Signal(bool)
    maneuver_input_submitted_signal = Signal(str)
    melee_action_selected_signal = Signal()
    missile_action_selected_signal = Signal()
    magic_action_selected_signal = Signal()
    skip_action_selected_signal = Signal()
    attacker_melee_results_submitted = Signal(str)
    defender_save_results_submitted = Signal(str)
    continue_to_next_phase_signal = Signal()
    game_state_updated = Signal()

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.help_model = HelpTextModel()

        # Track phase completion to control continue button
        self.phase_actions_completed = False
        self.current_phase_requirements_met = False

        # Track active dialogs to prevent duplicates
        self.active_action_dialog = None

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

        self.current_player_terrains_group = QGroupBox("Terrain Summaries")
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

        # 3. Player Turn and Continue Section
        player_continue_layout = QVBoxLayout()
        player_continue_layout.setContentsMargins(0, 10, 0, 0)

        # Player turn label
        self.player_turn_label = QLabel("👤 Player's Turn")
        player_turn_font = self.player_turn_label.font()
        player_turn_font.setPointSize(14)
        player_turn_font.setBold(True)
        self.player_turn_label.setFont(player_turn_font)
        self.player_turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_continue_layout.addWidget(self.player_turn_label)

        # Continue Button
        self.continue_button = QPushButton("Continue to Next Phase")
        self.continue_button.setMaximumWidth(220)  # Limit button width
        self.continue_button.setEnabled(
            False
        )  # Disabled by default until phase actions are completed
        self.continue_button.clicked.connect(self._on_continue_clicked)
        player_continue_layout.addWidget(
            self.continue_button, 0, Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addLayout(player_continue_layout)

        self.setLayout(main_layout)

        # Connect to game engine signals
        self.game_engine.game_state_updated.connect(self.update_ui)
        self.game_engine.current_phase_changed.connect(self.update_ui)
        self.game_engine.current_player_changed.connect(self.update_ui)

        # Connect critical signals for debug logging
        self.game_engine.unit_selection_required.connect(
            self._handle_unit_selection_required
        )
        self.game_engine.damage_allocation_completed.connect(
            self._handle_damage_allocation_completed
        )
        self.game_engine.counter_maneuver_requested.connect(
            self._handle_counter_maneuver_request
        )
        self.game_engine.simultaneous_maneuver_rolls_requested.connect(
            self._handle_simultaneous_maneuver_rolls_request
        )
        self.game_engine.terrain_direction_choice_requested.connect(
            self._handle_terrain_direction_choice_request
        )

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
                game_engine=self.game_engine,
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

    def _show_action_dialog(self, action_type: str):
        """Show the action dialog for proper action flow."""
        # Check if dialog is already active
        if self.active_action_dialog is not None:
            print(f"Action dialog already active for {action_type}, skipping")
            return

        try:
            # Get the current acting army
            acting_army = self.game_engine.get_current_acting_army()
            if not acting_army:
                print("No acting army selected")
                return

            current_player = self.game_engine.get_current_player_name()
            all_players_data = self.game_engine.get_all_players_data()
            terrain_data = self.game_engine.get_all_terrain_data()

            # Create and show action dialog with the acting army
            dialog = ActionDialog(
                action_type=action_type,
                current_player_name=current_player,
                acting_army=acting_army,
                all_players_data=all_players_data,
                terrain_data=terrain_data,
                parent=self,
            )

            # Track the active dialog
            self.active_action_dialog = dialog

            dialog.action_completed.connect(self._handle_action_completed)
            dialog.action_cancelled.connect(self._handle_action_cancelled)

            # Clear dialog reference when it's finished
            dialog.finished.connect(lambda: setattr(self, "active_action_dialog", None))

            dialog.exec()

        except Exception as e:
            print(f"Error showing action dialog: {e}")
            # Clear dialog reference on error
            self.active_action_dialog = None
            # Fallback: advance phase
            self.game_engine.advance_phase()

    def _handle_action_completed(self, action_result: dict):
        """Handle completed action from dialog."""
        print(f"Action completed: {action_result}")

        # Clear dialog reference
        self.active_action_dialog = None

        action_type = action_result.get("action_type", "UNKNOWN")
        attacker = action_result.get("attacker", "Unknown")
        location = action_result.get("location", "Unknown")

        # Apply action results to game state if needed
        # For now, just advance to the next phase
        print(f"{attacker} completed {action_type} action at {location}")

        # Clear the action step before advancing phase
        self.game_engine._current_action_step = ""
        print(f"[MainGameplayView] Cleared action step after completing {action_type}")
        
        # Advance to next phase
        self.game_engine.advance_phase()

    def _handle_action_cancelled(self):
        """Handle cancelled action from dialog."""
        print("Action cancelled")

        # Clear dialog reference
        self.active_action_dialog = None

        # Return to action selection
        self.game_engine.march_step_change_requested.emit(
            constants.MARCH_STEP_SELECT_ACTION
        )
        self.game_engine._current_march_step = constants.MARCH_STEP_SELECT_ACTION
        self.game_engine.game_state_updated.emit()

    def _update_continue_button_state(self):
        """Update the continue button state based on current phase requirements."""
        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Most phases should advance automatically, so hide the continue button in most cases
        should_show = False
        should_enable = False

        # Only show continue button for phases that genuinely need manual progression
        if current_phase == constants.PHASE_EIGHTH_FACE:
            # Eighth face has optional actions, allow manual continuation
            should_show = True
            should_enable = True
        elif current_phase == constants.PHASE_DRAGON_ATTACK:
            # Dragon attack needs manual progression after resolution
            should_show = True
            should_enable = True
        elif current_phase in [
            constants.PHASE_RESERVES,
            constants.PHASE_EXPIRE_EFFECTS,
        ]:
            # These might need manual review/progression
            should_show = True
            should_enable = True
        else:
            # March phases should advance automatically via actions/skips
            should_show = False
            should_enable = False

        # Set button visibility and state
        self.continue_button.setVisible(should_show)
        self.continue_button.setEnabled(should_enable)

        # Update button text based on phase
        if should_show and should_enable:
            if current_phase == constants.PHASE_EIGHTH_FACE:
                self.continue_button.setText("Continue (Eighth Face Complete)")
            elif current_phase == constants.PHASE_DRAGON_ATTACK:
                self.continue_button.setText("Continue (Dragon Attacks Complete)")
            else:
                self.continue_button.setText("Continue to Next Phase")
        else:
            self.continue_button.setText("Phase Auto-Advancing...")

    def _handle_action_selected(self, action_type: str):
        print(f"[MainGameplayView] Action selected: {action_type}")
        
        if action_type == constants.ACTION_MELEE:
            print(f"[MainGameplayView] Emitting melee action signal")
            self.melee_action_selected_signal.emit()
        elif action_type == constants.ACTION_MISSILE:
            print(f"[MainGameplayView] Emitting missile action signal")
            self.missile_action_selected_signal.emit()
        elif action_type == constants.ACTION_MAGIC:  # Use constant
            print(f"[MainGameplayView] Emitting magic action signal")
            self.magic_action_selected_signal.emit()
        elif action_type == constants.ACTION_SKIP:
            print(f"[MainGameplayView] Emitting skip action signal")
            self.skip_action_selected_signal.emit()

        # Mark that an action has been selected
        self.phase_actions_completed = True
        self._update_continue_button_state()

    @Slot()
    def update_ui(self):
        # Check if phase/step changed to reset completion state
        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step
        
        current_state = (current_phase, current_march_step, current_action_step)
        
        # Check if this is a redundant update
        if hasattr(self, "_last_phase_state") and self._last_phase_state == current_state:
            print(f"MainGameplayView: Skipping redundant UI update")
            return
        
        print(f"MainGameplayView: UI Update - Phase: {current_phase}, March: {current_march_step}, Action: {current_action_step}")

        # Reset phase actions completed when entering a new phase, march step, or action step
        if not hasattr(self, "_last_phase_state"):
            self._last_phase_state = current_state
        else:
            self.phase_actions_completed = False
            self._last_phase_state = current_state

        # Update Phase Title
        current_phase_display = self.game_engine.get_current_phase_display()
        phase_text = f"Phase: {current_phase_display}"
        self.phase_title_label.setText(phase_text)

        # Update Player Army Summaries
        widgets_removed = 0
        for i in reversed(range(self.player_armies_info_layout.count())):
            widget = self.player_armies_info_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                widgets_removed += 1
        
        if widgets_removed > 0:
            print(f"[MainGameplayView] Cleared {widgets_removed} existing player summary widgets")

        all_players_data = self.game_engine.get_all_player_summary_data()
        terrain_data = self.game_engine.get_all_terrain_data()
        widgets_added = 0
        for player_data in all_players_data:
            player_name = player_data.get("name", "Unknown Player")
            summary_widget = PlayerSummaryWidget(player_name)
            summary_widget.update_summary(player_data, terrain_data)
            self.player_armies_info_layout.addWidget(summary_widget)
            widgets_added += 1
        
        print(f"[MainGameplayView] Added {widgets_added} player summary widgets")
        if not all_players_data:
            self.player_armies_info_layout.addWidget(
                QLabel("No player data available.")
            )

        # Update Current Player Turn Label
        current_player_name = self.game_engine.get_current_player_name()
        self.player_turn_label.setText(format_player_turn_label(current_player_name))

        # Update Terrain Summaries
        terrains_html = "<ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"

        relevant_terrains = self.game_engine.get_relevant_terrains_info()
        for terrain in relevant_terrains:
            terrain_name = terrain.get("name", "N/A")
            terrain_type = terrain.get("type", "N/A")
            face_number = terrain.get("face", 1)
            controller = terrain.get("controller", None)

            # Use utility function for consistent formatting
            formatted_summary = format_terrain_summary(
                terrain_name, terrain_type, face_number, controller
            )
            terrains_html += f"<li>{formatted_summary}</li>"

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

        # Debug current state
        print(
            f"MainGameplayView: UI Update - Phase: {current_phase}, March: {current_march_step}, Action: {current_action_step}"
        )

        # Check action steps first - they take precedence over march steps
        if current_action_step == constants.ACTION_STEP_AWAITING_ATTACKER_MELEE_ROLL:
            print("MainGameplayView: Triggering melee action dialog")
            self._show_action_dialog("MELEE")
        elif (
            current_action_step == constants.ACTION_STEP_AWAITING_ATTACKER_MISSILE_ROLL
        ):
            self._show_action_dialog("MISSILE")
        elif current_action_step == constants.ACTION_STEP_AWAITING_MAGIC_ROLL:
            self._show_action_dialog("MAGIC")
        elif current_action_step == constants.ACTION_STEP_AWAITING_DEFENDER_SAVES:
            # This will be handled within the action dialog itself
            pass
        # Show appropriate widgets based on current march step
        elif current_march_step == constants.MARCH_STEP_CHOOSE_ACTING_ARMY:
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
            # Set the acting army for the maneuver widget
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.maneuver_input_widget.set_acting_army(acting_army, terrain_data)

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

    # Critical signal debug handlers
    def _handle_unit_selection_required(
        self, player_name: str, damage_amount: int, available_units: list
    ):
        """Debug handler for unit selection requirement."""
        print(
            f"[MainGameplayView] Unit selection required signal received for {player_name}"
        )
        print(f"[MainGameplayView] Damage amount: {damage_amount}")
        print(f"[MainGameplayView] Available units: {len(available_units)}")
        # TODO: Implement unit selection dialog for damage allocation

    def _handle_damage_allocation_completed(self, player_name: str, total_damage: int):
        """Debug handler for damage allocation completion."""
        print(
            f"[MainGameplayView] Damage allocation completed for {player_name}: {total_damage} damage"
        )
        # TODO: Update UI to reflect damage changes

    def _handle_counter_maneuver_request(self, location: str, opposing_armies: list):
        """Debug handler for counter-maneuver requests."""
        print(f"[MainGameplayView] Counter-maneuver request at {location}")
        print(f"[MainGameplayView] Opposing armies count: {len(opposing_armies)}")
        # TODO: Show counter-maneuver decision UI

    def _handle_simultaneous_maneuver_rolls_request(
        self,
        maneuvering_player: str,
        maneuvering_army: dict,
        opposing_armies: list,
        counter_responses: dict,
    ):
        """Debug handler for simultaneous maneuver roll requests."""
        print(f"[MainGameplayView] Simultaneous maneuver rolls requested")
        print(f"[MainGameplayView] Maneuvering player: {maneuvering_player}")
        print(f"[MainGameplayView] Counter responses: {list(counter_responses.keys())}")
        # TODO: Show simultaneous roll UI

    def _handle_terrain_direction_choice_request(
        self, location: str, current_face: int
    ):
        """Debug handler for terrain direction choice requests."""
        print(
            f"[MainGameplayView] Terrain direction choice requested at {location}, face {current_face}"
        )
        # TODO: Show terrain direction choice UI
