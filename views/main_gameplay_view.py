from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.acting_army_widget import ActingArmyWidget
from components.action_choice_widget import ActionChoiceWidget
from components.action_decision_widget import ActionDecisionWidget
from components.active_effects_widget import ActiveEffectsWidget
from components.maneuver_input_widget import ManeuverInputWidget
from components.melee_action_widget import MeleeActionWidget
from components.player_summary_widget import PlayerSummaryWidget
from components.reserves_widget import ReservesWidget
from components.summoning_pool_widget import SummoningPoolWidget
from components.tabbed_view_widget import TabbedViewWidget
from components.unit_areas_widget import UnitAreasWidget

# No change, good comment
from game_logic.game_orchestrator import GameOrchestrator as GameEngine
from models.help_text_model import HelpTextModel
from utils.field_access import strict_get, strict_get_optional, strict_get_with_fallback
from views.action_dialog import ActionDialog
from views.display_utils import (
    format_player_turn_label,
    format_terrain_summary_with_description,
)
from views.dragon_attack_dialog import DragonAttackDialog
from views.magic_action_dialog import MagicActionDialog
from views.maneuver_dialog import ManeuverDialog
from views.melee_combat_dialog import MeleeCombatDialog
from views.missile_combat_dialog import MissileCombatDialog
from views.reserves_phase_dialog import ReservesPhaseDialog
from views.species_abilities_phase_dialog import SpeciesAbilitiesPhaseDialog


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

    # Advanced phase signals
    species_abilities_phase_completed = Signal(dict)
    reserves_phase_completed = Signal(dict)
    dragon_attack_phase_completed = Signal(dict)

    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.help_model = HelpTextModel()

        # Track phase completion to control continue button
        self.phase_actions_completed = False
        self.current_phase_requirements_met = False

        # Track active dialogs to prevent duplicates
        self.active_action_dialog = None

        # Track phase state for UI updates
        self._last_phase_state: Optional[Tuple[Any, Any, Any]] = None

        self.setWindowTitle("Dragon Dice - Gameplay")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

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
        current_player_terrains_v_layout = QVBoxLayout(self.current_player_terrains_group)

        self.terrains_list_label = QTextEdit()
        self.terrains_list_label.setReadOnly(True)
        self.terrains_list_label.setPlaceholderText("Relevant terrains...")
        self.terrains_list_label.setMaximumHeight(120)  # Limit height to prevent excessive stretching
        self.terrains_list_label.setStyleSheet(
            "ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; }"
        )
        current_player_terrains_v_layout.addWidget(self.terrains_list_label)

        top_main_content_h_layout.addWidget(self.current_player_terrains_group, 1)
        main_content_v_layout.addLayout(top_main_content_h_layout)

        # 2.1.1.b Game Areas Section (Summoning Pool, Reserves, DUA/BUA)
        game_areas_layout = QHBoxLayout()
        game_areas_layout.setSpacing(8)

        # Summoning Pool Widget
        self.summoning_pool_widget = SummoningPoolWidget()
        self.summoning_pool_widget.dragon_selected.connect(self._handle_dragon_selected)
        self.summoning_pool_widget.refresh_requested.connect(self._refresh_summoning_pool)
        game_areas_layout.addWidget(self.summoning_pool_widget, 1)

        # Reserves Widget
        self.reserves_widget = ReservesWidget()
        self.reserves_widget.unit_selected.connect(self._handle_reserve_unit_selected)
        self.reserves_widget.refresh_requested.connect(self._refresh_reserves)
        self.reserves_widget.deploy_requested.connect(self._handle_deploy_unit)
        game_areas_layout.addWidget(self.reserves_widget, 1)

        # Unit Areas Widget (DUA/BUA)
        self.unit_areas_widget = UnitAreasWidget()
        self.unit_areas_widget.unit_selected.connect(self._handle_area_unit_selected)
        self.unit_areas_widget.refresh_requested.connect(self._refresh_unit_areas)
        self.unit_areas_widget.resurrect_requested.connect(self._handle_resurrect_unit)
        game_areas_layout.addWidget(self.unit_areas_widget, 1)

        main_content_v_layout.addLayout(game_areas_layout)

        # 2.1.1.c Active Effects Display
        self.active_effects_widget = ActiveEffectsWidget()
        main_content_v_layout.addWidget(self.active_effects_widget)

        # 2.1.2. Bottom part of main content: Phase Specific Actions
        self.phase_actions_group = QGroupBox()
        phase_actions_v_layout = QVBoxLayout(self.phase_actions_group)

        self.eighth_face_description_label = QLabel("Eighth Face Phase: Resolve any eighth face abilities")
        phase_actions_v_layout.addWidget(self.eighth_face_description_label)
        eighth_face_input_h_layout = QHBoxLayout()
        self.eighth_face_input_field = QLineEdit()
        self.eighth_face_input_field.setMaximumWidth(300)  # Prevent stretching across full width
        self.eighth_face_input_field.setPlaceholderText("Describe ability resolution...")
        self.eighth_face_add_button = QPushButton("Add ability")
        self.eighth_face_add_button.setMaximumWidth(120)  # Limit button width
        self.eighth_face_add_button.clicked.connect(self._on_eighth_face_add_ability)
        eighth_face_input_h_layout.addWidget(self.eighth_face_input_field)
        eighth_face_input_h_layout.addWidget(self.eighth_face_add_button)
        phase_actions_v_layout.addLayout(eighth_face_input_h_layout)

        self.dynamic_actions_layout = QVBoxLayout()

        # Acting Army Selection Widget
        self.acting_army_widget = ActingArmyWidget()
        self.acting_army_widget.acting_army_chosen.connect(self._handle_acting_army_chosen)
        self.dynamic_actions_layout.addWidget(self.acting_army_widget)
        self.acting_army_widget.hide()

        # Maneuver Input Widget
        self.maneuver_input_widget = ManeuverInputWidget()
        self.maneuver_input_widget.maneuver_decision_made.connect(self._handle_maneuver_decision)
        self.dynamic_actions_layout.addWidget(self.maneuver_input_widget)

        # Action Decision Widget
        self.action_decision_widget = ActionDecisionWidget()
        self.action_decision_widget.action_decision_made.connect(self._handle_action_decision)
        self.dynamic_actions_layout.addWidget(self.action_decision_widget)
        self.action_decision_widget.hide()

        # Action Choice Layout
        self.action_choice_widget = ActionChoiceWidget()
        self.action_choice_widget.action_selected.connect(self._handle_action_selected)
        self.dynamic_actions_layout.addWidget(self.action_choice_widget)
        self.action_choice_widget.hide()

        # Melee Action Input Layout
        self.melee_action_widget = MeleeActionWidget()
        self.melee_action_widget.attacker_results_submitted.connect(self.attacker_melee_results_submitted.emit)
        self.melee_action_widget.defender_results_submitted.connect(self.defender_save_results_submitted.emit)
        self.dynamic_actions_layout.addWidget(self.melee_action_widget)
        self.melee_action_widget.hide()

        self.dragon_attack_prompt_label = QLabel(
            "<b>Dragon Attack Phase:</b> Resolve dragon attacks at terrains with marching armies."
        )
        self.dragon_attack_execute_button = QPushButton("🐲 Execute Dragon Attacks")
        self.dragon_attack_execute_button.setMaximumWidth(250)  # Limit button width
        self.dragon_attack_execute_button.clicked.connect(self._show_dragon_attack_dialog)
        self.dragon_attack_continue_button = QPushButton("Continue Past Dragon Attacks")
        self.dragon_attack_continue_button.setMaximumWidth(250)  # Limit button width
        self.dragon_attack_continue_button.clicked.connect(lambda: self.game_engine.advance_phase())
        self.dynamic_actions_layout.addWidget(self.dragon_attack_prompt_label)
        self.dynamic_actions_layout.addWidget(self.dragon_attack_execute_button)
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
        self.continue_button.setEnabled(False)  # Disabled by default until phase actions are completed
        self.continue_button.clicked.connect(self._on_continue_clicked)
        player_continue_layout.addWidget(self.continue_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Skip Second March Button (only shown after First March)
        self.skip_second_march_button = QPushButton("Skip Second March")
        self.skip_second_march_button.setMaximumWidth(220)
        self.skip_second_march_button.setEnabled(False)
        self.skip_second_march_button.clicked.connect(self._on_skip_second_march_clicked)
        self.skip_second_march_button.hide()  # Hidden by default
        player_continue_layout.addWidget(self.skip_second_march_button, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(player_continue_layout)

        self.setLayout(main_layout)

        # Connect to game engine signals
        self.game_engine.game_state_updated.connect(self.update_ui)
        self.game_engine.current_phase_changed.connect(self.update_ui)
        self.game_engine.current_player_changed.connect(self.update_ui)

        # Connect dragon attack phase signals
        self.game_engine.dragon_attack_phase_started.connect(self._handle_dragon_attack_phase_started)
        self.game_engine.dragon_attack_phase_completed.connect(self._handle_dragon_attack_phase_completed)

        # Connect critical signals for debug logging
        self.game_engine.unit_selection_required.connect(self._handle_unit_selection_required)
        self.game_engine.damage_allocation_completed.connect(self._handle_damage_allocation_completed)
        self.game_engine.counter_maneuver_requested.connect(self._handle_counter_maneuver_request)
        self.game_engine.simultaneous_maneuver_rolls_requested.connect(self._handle_simultaneous_maneuver_rolls_request)
        self.game_engine.terrain_direction_choice_requested.connect(self._handle_terrain_direction_choice_request)

        self.update_ui()  # Initial call

    def _on_eighth_face_add_ability(self):
        ability_text = self.eighth_face_input_field.text()
        if ability_text:
            print(f"Eighth face ability logged: {ability_text}")
            # Here you might want to emit a signal or call an engine method
            self.eighth_face_input_field.clear()

    def _on_continue_clicked(self):
        print(f"MainGameplayView: Continue button clicked. Current phase: {self.game_engine.current_phase}")
        self.continue_to_next_phase_signal.emit()

    def _on_skip_second_march_clicked(self):
        print("MainGameplayView: Skip Second March button clicked")
        self.game_engine.skip_to_next_phase_group()

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
            # Use controller to handle state transition properly
            if hasattr(self, "gameplay_controller"):
                self.gameplay_controller.handle_march_step_transition("DECIDE_ACTION")
            else:
                self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
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
        if strict_get(maneuver_result, "success", "maneuver result"):
            success = self.game_engine.apply_maneuver_results(maneuver_result)
            if success:
                army_name = strict_get(maneuver_result, "army").get("name", "Unknown Army")
                location = strict_get(maneuver_result, "location", "maneuver result")
                direction = strict_get(maneuver_result, "direction", "maneuver result")
                old_face = strict_get(maneuver_result, "old_face", "maneuver result")
                new_face = strict_get(maneuver_result, "new_face", "maneuver result")
                result_text = f"{army_name} maneuvered at {location} - turned terrain {direction} from face {old_face} to {new_face}"
                self.maneuver_input_submitted_signal.emit(result_text)
            else:
                print("Failed to apply maneuver results")

        # Emit the maneuver decision signal
        self.maneuver_decision_signal.emit(True)

        # Transition to action decision step
        if hasattr(self, "gameplay_controller"):
            self.gameplay_controller.handle_march_step_transition("DECIDE_ACTION")
        else:
            self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")

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

        action_type = strict_get(action_result, "action_type", "action result")
        attacker = strict_get(action_result, "attacker")
        location = strict_get(action_result, "location", "action result")

        # Apply action results to game state if needed
        # For now, just advance to the next phase
        print(f"{attacker} completed {action_type} action at {location}")

        # Clear the action step before advancing phase
        if hasattr(self, "gameplay_controller"):
            self.gameplay_controller.handle_action_completed()
        print(f"[MainGameplayView] Cleared action step after completing {action_type}")

        # Advance to next phase
        self.game_engine.advance_phase()

    def _handle_action_cancelled(self):
        """Handle cancelled action from dialog."""
        print("Action cancelled")

        # Clear dialog reference
        self.active_action_dialog = None

        # Return to action selection
        if hasattr(self, "gameplay_controller"):
            self.gameplay_controller.handle_march_step_transition("SELECT_ACTION")
        else:
            self.game_engine.march_step_change_requested.emit("SELECT_ACTION")
        self.game_engine.game_state_updated.emit()

    def _update_continue_button_state(self):
        """Update the continue button state based on current phase requirements."""
        current_phase = self.game_engine.current_phase
        current_march_step = self.game_engine.current_march_step
        current_action_step = self.game_engine.current_action_step

        # Most phases should advance automatically, so hide the continue button in most cases
        should_show = False
        should_enable = False
        should_show_skip = False
        should_enable_skip = False

        # Only show continue button for phases that genuinely need manual progression
        if current_phase == "EIGHTH_FACE":
            # Eighth face has optional actions, allow manual continuation
            should_show = True
            should_enable = True
        elif current_phase == "DRAGON_ATTACK":
            # Dragon attack needs manual progression after resolution
            should_show = True
            should_enable = True
        elif current_phase in [
            "RESERVES",
            "EXPIRE_EFFECTS",
            "SPECIES_ABILITIES",
        ]:
            # These might need manual review/progression
            should_show = True
            should_enable = True
        elif current_phase == "FIRST_MARCH" and not current_march_step and not current_action_step:
            # First March is complete, offer option to skip Second March
            should_show = True
            should_enable = True
            should_show_skip = True
            should_enable_skip = True
        else:
            # March phases should advance automatically via actions/skips
            should_show = False
            should_enable = False

        # Set button visibility and state
        self.continue_button.setVisible(should_show)
        self.continue_button.setEnabled(should_enable)
        self.skip_second_march_button.setVisible(should_show_skip)
        self.skip_second_march_button.setEnabled(should_enable_skip)

        # Update button text based on phase
        if should_show and should_enable:
            if current_phase == "EIGHTH_FACE":
                self.continue_button.setText("Continue (Eighth Face Complete)")
            elif current_phase == "DRAGON_ATTACK":
                self.continue_button.setText("Continue (Dragon Attacks Complete)")
            elif current_phase == "SPECIES_ABILITIES":
                self.continue_button.setText("Start Species Abilities Phase")
            elif current_phase == "RESERVES":
                self.continue_button.setText("Start Reserves Phase")
            elif current_phase == "FIRST_MARCH":
                self.continue_button.setText("Continue to Second March")
            else:
                self.continue_button.setText("Continue to Next Phase")
        else:
            self.continue_button.setText("Phase Auto-Advancing...")

    def _handle_action_selected(self, action_type: str):
        print(f"[MainGameplayView] Action selected: {action_type}")

        if action_type == "MELEE":
            print("[MainGameplayView] Showing melee combat dialog")
            self._show_melee_combat_dialog()
        elif action_type == "MISSILE":
            print("[MainGameplayView] Showing missile combat dialog")
            self._show_missile_combat_dialog()
        elif action_type == "MAGIC":
            print("[MainGameplayView] Showing magic action dialog")
            self._show_magic_action_dialog()
        elif action_type == "SKIP":
            print("[MainGameplayView] Emitting skip action signal")
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
            print("MainGameplayView: Skipping redundant UI update")
            return

        print(
            f"MainGameplayView: UI Update - Phase: {current_phase}, March: {current_march_step}, Action: {current_action_step}"
        )

        # Reset phase actions completed when entering a new phase, march step, or action step
        if not hasattr(self, "_last_phase_state"):
            self._last_phase_state = current_state
        else:
            self.phase_actions_completed = False
            self._last_phase_state = current_state

        # Hide all dynamic widgets initially (moved after redundancy check)
        self.acting_army_widget.hide()
        self.maneuver_input_widget.hide()
        self.action_decision_widget.hide()
        self.action_choice_widget.hide()
        self.melee_action_widget.hide()
        self.dragon_attack_prompt_label.hide()
        self.dragon_attack_execute_button.hide()
        self.dragon_attack_continue_button.hide()

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
            player_name = strict_get(player_data, "name")
            summary_widget = PlayerSummaryWidget(player_name)
            summary_widget.update_summary(player_data, terrain_data)
            self.player_armies_info_layout.addWidget(summary_widget)
            widgets_added += 1

        print(f"[MainGameplayView] Added {widgets_added} player summary widgets")
        if not all_players_data:
            self.player_armies_info_layout.addWidget(QLabel("No player data available."))

        # Update Current Player Turn Label
        current_player_name = self.game_engine.get_current_player_name()
        self.player_turn_label.setText(format_player_turn_label(current_player_name))

        # Update Terrain Summaries
        terrains_html = "<ul style='margin-left:0px; padding-left:5px; list-style-position:inside;'>"

        relevant_terrains = self.game_engine.get_relevant_terrains_info()
        for terrain in relevant_terrains:
            terrain_name = strict_get(terrain, "name")
            terrain_type = strict_get(terrain, "type")
            strict_get(terrain, "face")
            controller = strict_get_optional(terrain, "controller")
            face_details = strict_get(terrain, "details")

            # Use utility function for consistent formatting but include face description
            formatted_summary = format_terrain_summary_with_description(
                terrain_name, terrain_type, face_details, controller
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

        is_eighth_face_phase = current_phase == "EIGHTH_FACE"
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
        if current_action_step == "AWAITING_ATTACKER_MELEE_ROLL":
            print("MainGameplayView: In melee action step - showing attacker input")
            self.melee_action_widget.show()
            self.melee_action_widget.show_attacker_input()
        elif current_action_step == "AWAITING_ATTACKER_MISSILE_ROLL":
            print("MainGameplayView: In missile action step")
            # For now, advance past missile since we don't have a widget yet
            self.game_engine.advance_phase()
        elif current_action_step == "AWAITING_MAGIC_ROLL":
            print("MainGameplayView: In magic action step")
            # For now, advance past magic since we don't have a widget yet
            self.game_engine.advance_phase()
        elif current_action_step == "AWAITING_DEFENDER_SAVES":
            print("MainGameplayView: In defender saves step - showing defender input")
            self.melee_action_widget.show()
            self.melee_action_widget.show_defender_input()
        # Show appropriate widgets based on current march step
        elif current_march_step == "CHOOSE_ACTING_ARMY":
            self.acting_army_widget.show()
            # Set available armies for the current player
            current_player = self.game_engine.get_current_player_name()
            all_players_data = self.game_engine.get_all_players_data()
            terrain_data = self.game_engine.get_all_terrain_data()
            player_data = strict_get(all_players_data, current_player, "players data")
            available_armies = []

            for army_type, army_data in strict_get(player_data, "armies", "player data").items():
                army_info = {
                    "name": strict_get(army_data, "name"),
                    "army_type": army_type,
                    "location": strict_get(army_data, "location", "army data"),
                    "units": strict_get_optional(army_data, "units", []),
                    "unique_id": strict_get_with_fallback(army_data, "unique_id", "id", "army data"),
                    "points": strict_get_with_fallback(army_data, "points_value", "allocated_points", "army data"),
                }
                available_armies.append(army_info)

            self.acting_army_widget.set_available_armies(available_armies, terrain_data)

        elif current_march_step == "DECIDE_MANEUVER":
            self.maneuver_input_widget.show()
            self.maneuver_input_widget.reset_to_decision()
            # Set the acting army for the maneuver widget
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.maneuver_input_widget.set_acting_army(acting_army, terrain_data)

        elif current_march_step == "DECIDE_ACTION":
            self.action_decision_widget.show()
            # Set the acting army for the action decision widget
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.action_decision_widget.set_acting_army(acting_army, terrain_data)

        elif current_march_step == "SELECT_ACTION":
            self.action_choice_widget.show()
            # Set available actions based on acting army's terrain die face
            acting_army = self.game_engine.get_current_acting_army()
            terrain_data = self.game_engine.get_all_terrain_data()
            if acting_army:
                self.action_choice_widget.set_available_actions(acting_army, terrain_data)
        elif not current_march_step and not current_action_step:
            if current_phase == "DRAGON_ATTACK":
                self.dragon_attack_prompt_label.show()
                self.dragon_attack_execute_button.show()
                self.dragon_attack_continue_button.show()
            elif current_phase == "SPECIES_ABILITIES":
                self._show_species_abilities_phase()
            elif current_phase == "RESERVES":
                self._show_reserves_phase()

        # Special handling for first turn
        # Check for very first turn using proper API
        is_very_first_turn = False
        if hasattr(self.game_engine, "is_very_first_turn"):
            is_very_first_turn = self.game_engine.is_very_first_turn()
        elif hasattr(self.game_engine, "_is_very_first_turn"):
            # Fallback to private access if public method not available
            is_very_first_turn = self.game_engine._is_very_first_turn

        if current_phase == "FIRST_MARCH" and is_very_first_turn and not current_march_step:
            help_key = "FIRST_MARCH"
        else:
            help_key = current_action_step or current_march_step or current_phase

        self.tabbed_widget.set_help_text(self.help_model.get_main_gameplay_help(help_key))

        # Update continue button state based on current phase requirements
        self._update_continue_button_state()

        # Update game areas displays
        self._update_summoning_pool_display()
        self._update_reserves_display()
        self._update_unit_areas_display()

    # Critical signal debug handlers
    def _handle_unit_selection_required(self, player_name: str, damage_amount: int, available_units: list):
        """Debug handler for unit selection requirement."""
        print(f"[MainGameplayView] Unit selection required signal received for {player_name}")
        print(f"[MainGameplayView] Damage amount: {damage_amount}")
        print(f"[MainGameplayView] Available units: {len(available_units)}")
        # TODO: Implement unit selection dialog for damage allocation

    def _handle_damage_allocation_completed(self, player_name: str, total_damage: int):
        """Debug handler for damage allocation completion."""
        print(f"[MainGameplayView] Damage allocation completed for {player_name}: {total_damage} damage")
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
        print("[MainGameplayView] Simultaneous maneuver rolls requested")
        print(f"[MainGameplayView] Maneuvering player: {maneuvering_player}")
        print(f"[MainGameplayView] Counter responses: {list(counter_responses.keys())}")
        # TODO: Show simultaneous roll UI

    def _handle_terrain_direction_choice_request(self, location: str, current_face: int):
        """Debug handler for terrain direction choice requests."""
        print(f"[MainGameplayView] Terrain direction choice requested at {location}, face {current_face}")
        # TODO: Show terrain direction choice UI

    def _show_species_abilities_phase(self):
        """Show the Species Abilities Phase dialog."""
        print("[MainGameplayView] Showing Species Abilities Phase dialog")

        current_player = self.game_engine.get_current_player_name()

        # Get required data for the dialog
        player_armies: List[Dict[str, Any]] = []  # TODO: Get actual player armies
        opponent_reserves: Dict[str, List[Dict[str, Any]]] = {}  # TODO: Get actual opponent reserves

        # Get managers from game engine (proper dependency injection)
        dua_manager = self.game_engine.dua_manager
        bua_manager = self.game_engine.bua_manager
        reserves_manager = self.game_engine.reserves_manager

        dialog = SpeciesAbilitiesPhaseDialog(
            current_player, player_armies, opponent_reserves, dua_manager, bua_manager, reserves_manager, parent=self
        )

        # Connect dialog signals
        dialog.abilities_completed.connect(self._on_species_abilities_completed)
        dialog.abilities_skipped.connect(lambda: self.game_engine.advance_phase())

        # Show dialog
        dialog.show()

    def _show_reserves_phase(self):
        """Show the Reserves Phase dialog."""
        print("[MainGameplayView] Showing Reserves Phase dialog")

        current_player = self.game_engine.get_current_player_name()

        # Get reserves units for current player (convert to dict format)
        # For now, use placeholder data - this would need real reserves data
        reserves_units: List[Dict[str, Any]] = []

        # Get terrain armies for current player
        terrain_armies = {}
        all_terrain_data = self.game_engine.get_all_terrain_data()
        for terrain_name, terrain_info in all_terrain_data.items():
            armies = strict_get_optional(terrain_info, "armies", {})
            player_armies = {
                army_id: army_data
                for army_id, army_data in armies.items()
                if strict_get(army_data, "player", "army data") == current_player
            }
            if player_armies:
                # For simplicity, use the first army found
                terrain_armies[terrain_name] = list(player_armies.values())[0]

        # Get available terrains
        available_terrains = list(all_terrain_data.keys())

        dialog = ReservesPhaseDialog(current_player, reserves_units, terrain_armies, available_terrains, parent=self)

        # Connect dialog signals
        dialog.phase_completed.connect(self._on_reserves_phase_completed)
        dialog.phase_cancelled.connect(lambda: self.game_engine.advance_phase())

        # Show dialog
        dialog.show()

    def _on_species_abilities_completed(self, results: dict):
        """Handle completion of Species Abilities Phase."""
        print(f"[MainGameplayView] Species Abilities Phase completed: {results}")

        # Emit signal for any listeners
        self.species_abilities_phase_completed.emit(results)

        # Advance to next phase
        self.game_engine.advance_phase()

    def _on_reserves_phase_completed(self, results: dict):
        """Handle completion of Reserves Phase."""
        print(f"[MainGameplayView] Reserves Phase completed: {results}")

        # Process reserves phase results
        strict_get_optional(results, "reinforce_step", {})
        strict_get_optional(results, "retreat_step", {})

        # TODO: Apply reserves phase changes to game state
        # This would involve:
        # 1. Moving units from reserves to terrains (reinforcement)
        # 2. Moving units from terrains to reserves (retreat)
        # 3. Creating new armies with specified names
        # 4. Processing burial operations

        # Emit signal for any listeners
        self.reserves_phase_completed.emit(results)

        # Advance to next phase/player
        self.game_engine.advance_phase()

    def _show_melee_combat_dialog(self):
        """Show the advanced melee combat dialog."""
        print("[MainGameplayView] Showing melee combat dialog")

        # Get current acting army and game state
        acting_army = self.game_engine.get_current_acting_army()
        if not acting_army:
            print("No acting army for melee combat")
            return

        current_player = self.game_engine.get_current_player_name()

        # TODO: Need to determine defender and location for melee combat
        defender_name = "Unknown Defender"  # This should come from game state
        defender_army: Dict[str, Any] = {}  # This should come from game state
        location = "Unknown Location"  # This should come from current action

        dialog = MeleeCombatDialog(current_player, acting_army, defender_name, defender_army, location, parent=self)

        # Connect dialog completion signal
        dialog.combat_completed.connect(self._on_combat_completed)
        dialog.combat_cancelled.connect(self._on_combat_cancelled)

        # Show dialog
        dialog.show()

    def _show_missile_combat_dialog(self):
        """Show the advanced missile combat dialog."""
        print("[MainGameplayView] Showing missile combat dialog")

        # Get current acting army and game state
        acting_army = self.game_engine.get_current_acting_army()
        if not acting_army:
            print("No acting army for missile combat")
            return

        current_player = self.game_engine.get_current_player_name()
        all_players_data = self.game_engine.get_all_player_summary_data()
        terrain_data = self.game_engine.get_all_terrain_data()

        dialog = MissileCombatDialog(current_player, acting_army, all_players_data, terrain_data, parent=self)

        # Connect dialog completion signal
        dialog.combat_completed.connect(self._on_combat_completed)
        dialog.combat_cancelled.connect(self._on_combat_cancelled)

        # Show dialog
        dialog.show()

    def _show_magic_action_dialog(self):
        """Show the advanced magic action dialog."""
        print("[MainGameplayView] Showing magic action dialog")

        # Get current acting army and game state
        acting_army = self.game_engine.get_current_acting_army()
        if not acting_army:
            print("No acting army for magic action")
            return

        current_player = self.game_engine.get_current_player_name()

        # TODO: Need to determine location for magic action
        location = "Unknown Location"  # This should come from current action

        dialog = MagicActionDialog(current_player, acting_army, location, parent=self)

        # Connect dialog completion signal
        dialog.magic_completed.connect(self._on_magic_completed)
        dialog.magic_cancelled.connect(self._on_magic_cancelled)

        # Show dialog
        dialog.show()

    def _on_combat_completed(self, results: dict):
        """Handle completion of combat actions."""
        print(f"[MainGameplayView] Combat completed: {results}")

        # Apply combat results to game state
        # TODO: Process combat results and update game state

        # Continue to next action step or phase
        self.game_engine.advance_phase()

    def _on_combat_cancelled(self):
        """Handle cancellation of combat actions."""
        print("[MainGameplayView] Combat cancelled")
        # Allow player to select a different action

    def _on_magic_completed(self, results: dict):
        """Handle completion of magic actions."""
        print(f"[MainGameplayView] Magic completed: {results}")

        # Apply magic results to game state
        if strict_get_optional(results, "cast_spells", False):
            spell_effects = self.game_engine.process_spell_effects(results)
            print(f"[MainGameplayView] Spell effects processed: {spell_effects}")

            # Show feedback for spell effects
            if strict_get_optional(spell_effects, "effects_applied", False):
                effects_msg = "\n".join(spell_effects["effects_applied"])
                print(f"Spell effects applied:\n{effects_msg}")

            if strict_get_optional(spell_effects, "errors", []):
                error_msg = "\n".join(spell_effects["errors"])
                print(f"Spell processing errors:\n{error_msg}")

        # Continue to next action step or phase
        self.game_engine.advance_phase()

    def _on_magic_cancelled(self):
        """Handle cancellation of magic actions."""
        print("[MainGameplayView] Magic cancelled")
        # Allow player to select a different action

    def _show_dragon_attack_dialog(self):
        """Show the Dragon Attack Phase dialog."""
        print("[MainGameplayView] Showing Dragon Attack Phase dialog")

        current_player = self.game_engine.get_current_player_name()

        # Find terrains where the marching player has armies
        terrains_with_armies = []
        all_terrain_data = self.game_engine.get_all_terrain_data()

        for terrain_name, terrain_info in all_terrain_data.items():
            armies = strict_get_optional(terrain_info, "armies", {})
            for _army_id, army_data in armies.items():
                if strict_get(army_data, "player", "army data") == current_player:
                    terrains_with_armies.append(terrain_name)
                    break

        if not terrains_with_armies:
            print(f"[MainGameplayView] No terrains with {current_player}'s armies found")
            # Skip dragon attack phase
            self.game_engine.advance_phase()
            return

        # For now, use the first terrain with armies (in a full implementation, would handle multiple terrains)
        target_terrain = terrains_with_armies[0]

        # Get dragons at this terrain
        dragons_present = self.game_engine.summoning_pool_manager.get_dragons_at_terrain(target_terrain)

        if not dragons_present:
            print(f"[MainGameplayView] No dragons at terrain {target_terrain}")
            # Skip dragon attack phase
            self.game_engine.advance_phase()
            return

        # Get marching army at this terrain
        terrain_info = all_terrain_data[target_terrain]
        marching_army = None
        for _army_id, army_data in strict_get_optional(terrain_info, "armies", {}).items():
            if strict_get(army_data, "player", "army data") == current_player:
                marching_army = army_data
                break

        if not marching_army:
            print(f"[MainGameplayView] No marching army found at {target_terrain}")
            self.game_engine.advance_phase()
            return

        # Create dragon attack dialog
        dialog = DragonAttackDialog(
            marching_player=current_player,
            terrain_name=target_terrain,
            dragons_present=dragons_present,
            marching_army=marching_army,
            parent=self,
        )

        # Connect dialog signals
        dialog.attack_completed.connect(self._on_dragon_attack_completed)
        dialog.attack_cancelled.connect(self._on_dragon_attack_cancelled)

        # Show dialog
        dialog.show()

    def _on_dragon_attack_completed(self, attack_results: dict):
        """Handle completion of dragon attack dialog."""
        print(f"[MainGameplayView] Dragon Attack completed: {attack_results}")

        # Process dragon attack results
        # TODO: Apply damage to armies, handle dragon kills, process promotions

        # Emit signal for any listeners
        self.dragon_attack_phase_completed.emit(attack_results)

        # Advance to next phase
        self.game_engine.advance_phase()

    def _on_dragon_attack_cancelled(self):
        """Handle cancellation of dragon attack dialog."""
        print("[MainGameplayView] Dragon Attack cancelled")
        # Continue without dragon attacks
        self.game_engine.advance_phase()

    def _handle_dragon_attack_phase_started(self, marching_player: str):
        """Handle when dragon attack phase starts."""
        print(f"[MainGameplayView] Dragon Attack Phase started for {marching_player}")
        # Update UI to show dragon attack is available
        self.update_ui()

    def _handle_dragon_attack_phase_completed(self, phase_result: dict):
        """Handle when dragon attack phase completes."""
        print(f"[MainGameplayView] Dragon Attack Phase completed: {phase_result}")
        # Process any game state changes from dragon attacks
        # Update UI to reflect completed dragon attacks

    # Game Areas Widget Handlers
    def _handle_dragon_selected(self, dragon_data: dict):
        """Handle dragon selection from summoning pool."""
        print(f"[MainGameplayView] Dragon selected: {strict_get(dragon_data, 'dragon_type')}")
        # Could show dragon details, enable summoning actions, etc.

    def _handle_reserve_unit_selected(self, unit_data: dict):
        """Handle reserve unit selection."""
        print(f"[MainGameplayView] Reserve unit selected: {strict_get(unit_data, 'name')}")
        # Could show unit details, enable deployment actions, etc.

    def _handle_area_unit_selected(self, unit_data: dict, area_type: str):
        """Handle unit selection from DUA/BUA."""
        print(f"[MainGameplayView] {area_type} unit selected: {strict_get(unit_data, 'name')}")
        # Could show unit details, enable resurrection actions for DUA, etc.

    def _handle_deploy_unit(self, unit_data: dict):
        """Handle unit deployment request from reserves."""
        print(f"[MainGameplayView] Deploy unit requested: {strict_get(unit_data, 'name')}")
        # TODO: Implement deployment logic
        # Would need to show terrain selection, handle deployment rules, etc.

    def _handle_resurrect_unit(self, unit_data: dict):
        """Handle unit resurrection request from DUA."""
        print(f"[MainGameplayView] Resurrect unit requested: {strict_get(unit_data, 'name')}")
        # TODO: Implement resurrection logic
        # Would need to check for resurrection spells, handle costs, etc.

    def _refresh_summoning_pool(self):
        """Refresh summoning pool data."""
        print("[MainGameplayView] Refreshing summoning pool")
        self._update_summoning_pool_display()

    def _refresh_reserves(self):
        """Refresh reserves data."""
        print("[MainGameplayView] Refreshing reserves")
        self._update_reserves_display()

    def _refresh_unit_areas(self):
        """Refresh DUA/BUA data."""
        print("[MainGameplayView] Refreshing unit areas")
        self._update_unit_areas_display()

    def _update_summoning_pool_display(self):
        """Update the summoning pool widget with current data."""
        try:
            # Get summoning pool data from game engine
            pool_data = {}
            all_players_data = self.game_engine.get_all_players_data()

            for player_name in all_players_data:
                # Get dragons for this player
                player_dragons = self.game_engine.summoning_pool_manager.get_player_pool(player_name)
                if player_dragons:
                    pool_data[player_name] = [dragon.to_dict() for dragon in player_dragons]

            self.summoning_pool_widget.update_pool_data(pool_data)
        except Exception as e:
            print(f"[MainGameplayView] Error updating summoning pool: {e}")

    def _update_reserves_display(self):
        """Update the reserves widget with current data."""
        try:
            # Get reserves data from game engine
            reserves_data = {}
            all_players_data = self.game_engine.get_all_players_data()

            for player_name in all_players_data:
                # Get reserve units for this player
                player_reserves = self.game_engine.reserves_manager.get_player_reserves(player_name)
                if player_reserves:
                    reserves_data[player_name] = [unit.to_dict() for unit in player_reserves]

            self.reserves_widget.update_reserves_data(reserves_data)
        except Exception as e:
            print(f"[MainGameplayView] Error updating reserves: {e}")

    def _update_unit_areas_display(self):
        """Update the unit areas widget with current DUA/BUA data."""
        try:
            # Get DUA data
            dua_data = {}
            bua_data = {}
            all_players_data = self.game_engine.get_all_players_data()

            for player_name in all_players_data:
                # Get DUA units for this player
                player_dua = self.game_engine.dua_manager.get_player_dua(player_name)
                if player_dua:
                    dua_data[player_name] = [unit.to_dict() for unit in player_dua]

                # Get BUA units for this player
                player_bua = self.game_engine.bua_manager.get_player_bua(player_name)
                if player_bua:
                    bua_data[player_name] = [unit.to_dict() for unit in player_bua]

            self.unit_areas_widget.update_dua_data(dua_data)
            self.unit_areas_widget.update_bua_data(bua_data)
        except Exception as e:
            print(f"[MainGameplayView] Error updating unit areas: {e}")
