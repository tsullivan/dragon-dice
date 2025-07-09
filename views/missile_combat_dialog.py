"""
Missile Combat Dialog for Dragon Dice - captures individual die face results for proper SAI and species ability tracking.

This dialog handles the complete missile combat flow:
1. Attacker selects target army and rolls missile dice
2. Defender rolls saves (with Coastal Dodge for Coral Elves)
3. Calculate and display final damage
4. Handle Coral Elf Defensive Volley counter-attack if applicable
"""

from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from game_logic.sai_processor import SAIProcessor


class MissileDieRollInputWidget(QWidget):
    """Widget for inputting individual die face results for missile combat."""

    def __init__(self, unit_name: str, unit_health: int, parent=None):
        super().__init__(parent)
        self.unit_name = unit_name
        self.unit_health = unit_health
        self.face_inputs: List[QLineEdit] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the die roll input UI."""
        layout = QVBoxLayout(self)

        # Unit header
        header_label = QLabel(f"{self.unit_name} (Health: {self.unit_health})")
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(header_label)

        # Face inputs
        faces_layout = QHBoxLayout()

        for i in range(6):  # 6-sided dice
            face_layout = QVBoxLayout()

            face_label = QLabel(f"Face {i + 1}")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_layout.addWidget(face_label)

            face_input = QLineEdit()
            face_input.setMaximumWidth(60)
            face_input.setPlaceholderText("M/Mi/Mg/S/ID/SAI/Ma")
            face_input.setToolTip(
                "Enter die face result:\n"
                "M = Melee\n"
                "Mi = Missile\n"
                "Mg = Magic\n"
                "S = Save\n"
                "ID = ID face\n"
                "SAI = Special Action Icon\n"
                "Ma = Maneuver"
            )
            face_layout.addWidget(face_input)

            self.face_inputs.append(face_input)
            faces_layout.addLayout(face_layout)

        layout.addLayout(faces_layout)

    def get_face_results(self) -> List[str]:
        """Get the face results from all inputs."""
        return [input_field.text().strip() for input_field in self.face_inputs]

    def clear_inputs(self):
        """Clear all input fields."""
        for input_field in self.face_inputs:
            input_field.clear()


class MissileCombatDialog(QDialog):
    """
    Dialog for handling missile combat with detailed die face input.

    This dialog captures individual die face results from both attacker and defender
    to properly calculate SAI effects, species abilities, and handle special Coral Elf abilities.
    """

    combat_completed = Signal(dict)  # Emits combat results
    combat_cancelled = Signal()

    def __init__(
        self,
        attacker_name: str,
        attacker_army: Dict[str, Any],
        available_targets: List[Dict[str, Any]],  # List of {player_name, army_data, location}
        location: str,
        parent=None,
    ):
        super().__init__(parent)
        self.attacker_name = attacker_name
        self.attacker_army = attacker_army
        self.available_targets = available_targets
        self.location = location

        # Combat state
        self.current_step = "select_target"  # select_target, attacker_roll, defender_saves, defensive_volley, results
        self.selected_target: Optional[Dict[str, Any]] = None
        self.attacker_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.defender_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.final_damage = 0
        self.can_defensive_volley = False
        self.defensive_volley_results: Dict[str, List[str]] = {}
        self.defensive_volley_damage = 0

        self.sai_processor = SAIProcessor()

        self.setWindowTitle(f"🏹 Missile Attack from {location}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._update_step_display()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)

        # Step indicator
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.step_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.step_label.setFont(font)
        main_layout.addWidget(self.step_label)

        # Combat info
        combat_info = QLabel(f"🏹 {self.attacker_name} launches missile attack from {self.location}")
        combat_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        combat_info.setStyleSheet("font-size: 14px; margin: 10px; padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(combat_info)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(150)
        self.results_display.setReadOnly(True)
        self.results_display.hide()
        main_layout.addWidget(self.results_display)

        # Buttons
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("◀ Back")
        self.back_button.setMaximumWidth(100)
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.next_button = QPushButton("Next ▶")
        self.next_button.setMaximumWidth(120)
        self.next_button.clicked.connect(self._on_next)
        button_layout.addWidget(self.next_button)

        main_layout.addLayout(button_layout)

    def _update_step_display(self):
        """Update the display based on current step."""
        # Clear content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if self.current_step == "select_target":
            self._show_select_target()
        elif self.current_step == "attacker_roll":
            self._show_attacker_roll()
        elif self.current_step == "defender_saves":
            self._show_defender_saves()
        elif self.current_step == "defensive_volley":
            self._show_defensive_volley()
        elif self.current_step == "results":
            self._show_results()

        self._update_buttons()

    def _show_select_target(self):
        """Show target selection for missile attack."""
        self.step_label.setText("Step 1: 🎯 Select Target")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            f"<b>{self.attacker_name}</b>: Select which army to target with your missile attack.<br>"
            f"Missile attacks can target any opposing army (with some restrictions)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #e8f4fd;")
        self.content_layout.addWidget(instructions)

        # Target selection
        target_group = QGroupBox("Available Targets")
        target_layout = QVBoxLayout(target_group)

        # Target dropdown
        target_select_layout = QHBoxLayout()
        target_select_layout.addWidget(QLabel("Target Army:"))

        self.target_combo = QComboBox()
        for i, target in enumerate(self.available_targets):
            player_name = target.get("player_name", "Unknown Player")
            army_name = target.get("army_data", {}).get("name", "Unknown Army")
            target_location = target.get("location", "Unknown Location")
            display_text = f"{player_name}'s {army_name} at {target_location}"
            self.target_combo.addItem(display_text, i)

        target_select_layout.addWidget(self.target_combo)
        target_layout.addLayout(target_select_layout)

        # Show target details when selection changes
        self.target_details = QLabel()
        self.target_details.setWordWrap(True)
        self.target_details.setStyleSheet("margin: 10px; padding: 10px; background-color: #f8f8f8;")
        target_layout.addWidget(self.target_details)

        self.target_combo.currentIndexChanged.connect(self._update_target_details)
        self._update_target_details()  # Initial update

        self.content_layout.addWidget(target_group)

        # Missile attack rules reminder
        rules_note = QLabel(
            "📝 <b>Missile Attack Rules:</b><br>"
            "• No counter-attack normally<br>"
            "• Coral Elves can counter-attack with Defensive Volley at air terrain<br>"
            "• Coral Elves can use Coastal Dodge (maneuver→saves) at water terrain"
        )
        rules_note.setWordWrap(True)
        rules_note.setStyleSheet("background-color: #fff9db; padding: 10px; border: 1px solid #ffd43b; margin: 10px;")
        self.content_layout.addWidget(rules_note)

    def _show_attacker_roll(self):
        """Show attacker missile roll input."""
        self.step_label.setText("Step 2: 🏹 Missile Attack Roll")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            f"<b>{self.attacker_name}</b>: Roll all units in your army and enter each die face result below."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #e8f4fd;")
        self.content_layout.addWidget(instructions)

        # Target reminder
        if self.selected_target:
            target_info = QLabel(
                f"🎯 <b>Target:</b> {self.selected_target.get('player_name', 'Unknown')}'s "
                f"{self.selected_target.get('army_data', {}).get('name', 'Unknown Army')}"
            )
            target_info.setStyleSheet("font-weight: bold; color: #d63384; margin: 10px;")
            self.content_layout.addWidget(target_info)

        # Army units
        self.attacker_roll_widgets = []
        army_units = self.attacker_army.get("units", [])

        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_health = unit.get("health", 1)

            unit_widget = MissileDieRollInputWidget(unit_name, unit_health)
            self.attacker_roll_widgets.append(unit_widget)
            self.content_layout.addWidget(unit_widget)

        # Helpful note
        note = QLabel(
            "💡 Tip: Use shortcuts like M=Melee, Mi=Missile, Mg=Magic, S=Save, ID=ID face, SAI=Special Action Icon, Ma=Maneuver"
        )
        note.setStyleSheet("font-style: italic; color: #666; margin: 10px;")
        note.setWordWrap(True)
        self.content_layout.addWidget(note)

    def _show_defender_saves(self):
        """Show defender save roll input."""
        self.step_label.setText("Step 3: 🛡️ Defender Save Roll")
        self.results_display.show()

        # Show attacker results with SAI processing
        terrain_elements = self._get_terrain_elements()
        attacker_army_units = self.attacker_army.get("units", [])
        attacker_result = self.sai_processor.process_combat_roll(
            self.attacker_results, "missile", attacker_army_units, is_attacker=True, terrain_elements=terrain_elements
        )
        attacker_summary = self.sai_processor.format_combat_summary(attacker_result, "missile")
        self.results_display.setText(f"Attacker Results:\n{attacker_summary}")

        # Instructions
        defender_name = self.selected_target.get("player_name", "Defender") if self.selected_target else "Defender"
        instructions = QLabel(
            f"<b>{defender_name}</b>: Roll all units in your army and enter each die face result below."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #fdf8e8;")
        self.content_layout.addWidget(instructions)

        # Check for Coral Elf abilities at target location
        if self.selected_target:
            target_location = self.selected_target.get("location", "")
            target_terrain_elements = self._get_terrain_elements(target_location)
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])

            # Check for species abilities at target location
            has_coral_elves = any(unit.get("species") == "Coral Elves" for unit in target_units)
            has_scalders = any(unit.get("species") == "Scalders" for unit in target_units)

            # Coastal Dodge (Coral Elves)
            if has_coral_elves and "water" in target_terrain_elements:
                coastal_dodge_note = QLabel(
                    "🌊 <b>Coastal Dodge:</b> Coral Elves can count maneuver results as save results at water terrain!"
                )
                coastal_dodge_note.setWordWrap(True)
                coastal_dodge_note.setStyleSheet(
                    "background-color: #e6f7ff; padding: 10px; border: 1px solid #52c41a; margin: 10px;"
                )
                self.content_layout.addWidget(coastal_dodge_note)

            # Intangibility (Scalders)
            if has_scalders and "water" in target_terrain_elements:
                intangibility_note = QLabel(
                    "👻 <b>Intangibility:</b> Scalders can count maneuver results as save results against missile damage at water terrain!"
                )
                intangibility_note.setWordWrap(True)
                intangibility_note.setStyleSheet(
                    "background-color: #f6ffed; padding: 10px; border: 1px solid #73d13d; margin: 10px;"
                )
                self.content_layout.addWidget(intangibility_note)

            # Defensive Volley potential (Coral Elves)
            if has_coral_elves and "air" in target_terrain_elements:
                self.can_defensive_volley = True
                defensive_volley_note = QLabel(
                    "💨 <b>Defensive Volley:</b> Coral Elves can counter-attack against missile attacks at air terrain!"
                )
                defensive_volley_note.setWordWrap(True)
                defensive_volley_note.setStyleSheet(
                    "background-color: #f0f9ff; padding: 10px; border: 1px solid #1890ff; margin: 10px;"
                )
                self.content_layout.addWidget(defensive_volley_note)

        # Army units
        self.defender_roll_widgets = []
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])

            for unit in target_units:
                unit_name = unit.get("name", "Unknown Unit")
                unit_health = unit.get("health", 1)

                unit_widget = MissileDieRollInputWidget(unit_name, unit_health)
                self.defender_roll_widgets.append(unit_widget)
                self.content_layout.addWidget(unit_widget)

    def _show_defensive_volley(self):
        """Show Coral Elf defensive volley counter-attack."""
        self.step_label.setText("Step 4: 🏹 Defensive Volley Counter-Attack")
        self.results_display.show()

        # Update results display with damage calculation
        self._update_results_display_for_defensive_volley()

        # Instructions
        defender_name = self.selected_target.get("player_name", "Defender") if self.selected_target else "Defender"
        instructions = QLabel(
            f"<b>{defender_name}</b>: Coral Elves can make a missile counter-attack (Defensive Volley).<br>"
            f"Roll your Coral Elf units again and count missile results for the counter-attack."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f9ff;")
        self.content_layout.addWidget(instructions)

        # Defensive volley choice
        choice_layout = QHBoxLayout()

        volley_btn = QPushButton("🏹 Use Defensive Volley")
        volley_btn.setStyleSheet("background-color: #1890ff; color: white; font-weight: bold; padding: 10px;")
        volley_btn.clicked.connect(self._use_defensive_volley)
        choice_layout.addWidget(volley_btn)

        skip_btn = QPushButton("⏭️ Skip Defensive Volley")
        skip_btn.setStyleSheet("background-color: #8c8c8c; color: white; font-weight: bold; padding: 10px;")
        skip_btn.clicked.connect(self._skip_defensive_volley)
        choice_layout.addWidget(skip_btn)

        choice_widget = QWidget()
        choice_widget.setLayout(choice_layout)
        self.content_layout.addWidget(choice_widget)

    def _show_results(self):
        """Show final missile combat results."""
        self.step_label.setText("Step 5: 📊 Combat Results")
        self.results_display.show()

        # Final results display
        self._update_final_results_display()

        # Combat summary
        summary_text = f"<b>Missile Combat Complete</b><br>"
        if self.final_damage > 0:
            summary_text += f"Defender takes {self.final_damage} damage.<br>"
        else:
            summary_text += "No damage dealt to defender.<br>"

        if self.defensive_volley_damage > 0:
            summary_text += f"Attacker takes {self.defensive_volley_damage} damage from Defensive Volley."

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f8f8f8; font-size: 14px;")
        self.content_layout.addWidget(summary_label)

    def _update_target_details(self):
        """Update target details display."""
        if not self.target_combo.currentData():
            return

        target_index = self.target_combo.currentData()
        target = self.available_targets[target_index]

        player_name = target.get("player_name", "Unknown Player")
        army_data = target.get("army_data", {})
        target_location = target.get("location", "Unknown Location")

        army_name = army_data.get("name", "Unknown Army")
        units = army_data.get("units", [])

        details_text = f"<b>Target Details:</b><br>"
        details_text += f"Player: {player_name}<br>"
        details_text += f"Army: {army_name}<br>"
        details_text += f"Location: {target_location}<br>"
        details_text += f"Units: {len(units)}<br><br>"

        # Check for special abilities at target location
        target_terrain_elements = self._get_terrain_elements(target_location)
        coral_elves = [unit for unit in units if unit.get("species") == "Coral Elves"]
        scalders = [unit for unit in units if unit.get("species") == "Scalders"]

        if coral_elves:
            details_text += "<b>Coral Elf Abilities:</b><br>"
            if "water" in target_terrain_elements:
                details_text += "🌊 Coastal Dodge: Maneuver → Save<br>"
            if "air" in target_terrain_elements:
                details_text += "💨 Defensive Volley: Can counter-attack<br>"

        if scalders:
            details_text += "<b>Scalder Abilities:</b><br>"
            if "water" in target_terrain_elements:
                details_text += "👻 Intangibility: Maneuver → Save vs missiles<br>"

        self.target_details.setText(details_text)

    def _use_defensive_volley(self):
        """Use Coral Elf defensive volley counter-attack."""
        # Clear content and show Coral Elf missile roll interface
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Instructions for defensive volley
        instructions = QLabel(
            f"<b>Defensive Volley:</b> Coral Elves roll missile dice for counter-attack.<br>"
            f"Enter die face results for Coral Elf units only."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f9ff;")
        self.content_layout.addWidget(instructions)

        # Show only Coral Elf units for defensive volley
        self.defensive_volley_widgets = []
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])
            coral_elf_units = [unit for unit in target_units if unit.get("species") == "Coral Elves"]

            if coral_elf_units:
                for unit in coral_elf_units:
                    unit_name = unit.get("name", "Unknown Unit")
                    unit_health = unit.get("health", 1)

                    unit_widget = MissileDieRollInputWidget(unit_name, unit_health)
                    self.defensive_volley_widgets.append(unit_widget)
                    self.content_layout.addWidget(unit_widget)
            else:
                no_coral_elves = QLabel("No Coral Elf units found for Defensive Volley.")
                no_coral_elves.setStyleSheet("color: red; margin: 10px;")
                self.content_layout.addWidget(no_coral_elves)

        # Submit button for defensive volley
        submit_volley_btn = QPushButton("🏹 Submit Defensive Volley")
        submit_volley_btn.setStyleSheet("background-color: #1890ff; color: white; font-weight: bold; padding: 10px;")
        submit_volley_btn.clicked.connect(self._calculate_defensive_volley)
        self.content_layout.addWidget(submit_volley_btn)

    def _skip_defensive_volley(self):
        """Skip defensive volley counter-attack."""
        self.defensive_volley_damage = 0
        self.current_step = "results"
        self._update_step_display()

    def _calculate_defensive_volley(self):
        """Calculate damage from Coral Elf defensive volley."""
        # Collect defensive volley results
        if not hasattr(self, "defensive_volley_widgets"):
            self.defensive_volley_damage = 0
            self.current_step = "results"
            self._update_step_display()
            return

        # Get Coral Elf die results
        defensive_volley_results = {}
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])
            coral_elf_units = [unit for unit in target_units if unit.get("species") == "Coral Elves"]

            for i, widget in enumerate(self.defensive_volley_widgets):
                if i < len(coral_elf_units):
                    unit_name = coral_elf_units[i].get("name", f"Coral Elf {i + 1}")
                    face_results = widget.get_face_results()
                    defensive_volley_results[unit_name] = face_results

        # Process defensive volley with SAI processor
        target_location = self.selected_target.get("location", "") if self.selected_target else ""
        target_terrain_elements = self._get_terrain_elements(target_location)

        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            coral_elf_units = [unit for unit in target_army.get("units", []) if unit.get("species") == "Coral Elves"]

            volley_result = self.sai_processor.process_combat_roll(
                defensive_volley_results,
                "missile",
                coral_elf_units,
                is_attacker=True,  # Coral Elves are counter-attacking
                terrain_elements=target_terrain_elements,
            )

            # Defensive volley targets the original attacker's army
            # For simplicity, assume no saves against defensive volley (or process attacker saves)
            self.defensive_volley_damage = volley_result.final_missile

            # Store results for final display
            self.defensive_volley_results = defensive_volley_results

        # Proceed to results
        self.current_step = "results"
        self._update_step_display()

    def _collect_attacker_results(self) -> bool:
        """Collect attacker roll results from input widgets."""
        if not hasattr(self, "attacker_roll_widgets"):
            return False

        self.attacker_results = {}
        army_units = self.attacker_army.get("units", [])

        for i, widget in enumerate(self.attacker_roll_widgets):
            if i < len(army_units):
                unit_name = army_units[i].get("name", f"Unit {i + 1}")
                face_results = widget.get_face_results()
                self.attacker_results[unit_name] = face_results

        return True

    def _collect_defender_results(self) -> bool:
        """Collect defender roll results from input widgets."""
        if not hasattr(self, "defender_roll_widgets"):
            return False

        self.defender_results = {}
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])

            for i, widget in enumerate(self.defender_roll_widgets):
                if i < len(target_units):
                    unit_name = target_units[i].get("name", f"Defender Unit {i + 1}")
                    face_results = widget.get_face_results()
                    self.defender_results[unit_name] = face_results

        return True

    def _calculate_missile_damage(self):
        """Calculate final missile damage with species abilities."""
        terrain_elements = self._get_terrain_elements()
        target_location = self.selected_target.get("location", "") if self.selected_target else ""
        target_terrain_elements = self._get_terrain_elements(target_location)

        # Process attacker results
        attacker_army_units = self.attacker_army.get("units", [])
        attacker_result = self.sai_processor.process_combat_roll(
            self.attacker_results, "missile", attacker_army_units, is_attacker=True, terrain_elements=terrain_elements
        )

        # Process defender results
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])
            defender_result = self.sai_processor.process_combat_roll(
                self.defender_results, "save", target_units, is_attacker=False, terrain_elements=target_terrain_elements
            )

            self.final_damage = max(0, attacker_result.final_missile - defender_result.final_save)
        else:
            self.final_damage = 0

    def _update_results_display_for_defensive_volley(self):
        """Update results display before defensive volley step."""
        self._calculate_missile_damage()

        results_text = f"MISSILE ATTACK RESULTS:\n"
        results_text += f"Missile damage to defender: {self.final_damage}\n\n"
        results_text += "Coral Elves can now make a Defensive Volley counter-attack at air terrain."

        self.results_display.setText(results_text)

    def _update_final_results_display(self):
        """Update final results display."""
        self._calculate_missile_damage()

        # Get detailed summaries
        terrain_elements = self._get_terrain_elements()
        target_location = self.selected_target.get("location", "") if self.selected_target else ""
        target_terrain_elements = self._get_terrain_elements(target_location)

        attacker_army_units = self.attacker_army.get("units", [])
        attacker_result = self.sai_processor.process_combat_roll(
            self.attacker_results, "missile", attacker_army_units, is_attacker=True, terrain_elements=terrain_elements
        )
        attacker_summary = self.sai_processor.format_combat_summary(attacker_result, "missile")

        defender_summary = ""
        if self.selected_target:
            target_army = self.selected_target.get("army_data", {})
            target_units = target_army.get("units", [])
            defender_result = self.sai_processor.process_combat_roll(
                self.defender_results, "save", target_units, is_attacker=False, terrain_elements=target_terrain_elements
            )
            defender_summary = self.sai_processor.format_combat_summary(defender_result, "save")

        results_text = f"""ATTACKER RESULTS:
{attacker_summary}

DEFENDER RESULTS:
{defender_summary}

FINAL DAMAGE:
{attacker_result.final_missile} missile - {defender_result.final_save if "defender_result" in locals() else 0} saves = {self.final_damage} damage"""

        if self.defensive_volley_damage > 0:
            results_text += f"\n\nDEFENSIVE VOLLEY:\n{self.defensive_volley_damage} damage to attacker"

        self.results_display.setText(results_text)

    def _complete_combat(self):
        """Complete the missile combat and emit results."""
        combat_result = {
            "success": True,
            "combat_type": "missile",
            "attacker": self.attacker_name,
            "defender": self.selected_target.get("player_name", "Unknown") if self.selected_target else "Unknown",
            "target_army": self.selected_target.get("army_data", {}) if self.selected_target else {},
            "location": self.location,
            "target_location": self.selected_target.get("location", "") if self.selected_target else "",
            "attacker_results": self.attacker_results,
            "defender_results": self.defender_results,
            "final_damage": self.final_damage,
            "defensive_volley_used": self.defensive_volley_damage > 0,
            "defensive_volley_damage": self.defensive_volley_damage,
            "timestamp": "now",
        }

        self.combat_completed.emit(combat_result)
        self.accept()

    def _get_terrain_elements(self, location: str = None) -> List[str]:
        """Get terrain elements for the specified location."""
        if location is None:
            location = self.location

        # Same logic as other combat dialogs
        terrain_mappings = {
            "Highland": ["fire", "earth"],
            "Flatland": ["air", "earth"],
            "Coastland": ["air", "water"],
            "Swampland": ["water", "earth"],
            "Wasteland": ["air", "fire"],
            "Feyland": ["water", "fire"],
            "Deadland": ["death"],
        }

        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in location.lower():
                return elements

        return []

    def _update_buttons(self):
        """Update button states based on current step."""
        if self.current_step == "select_target":
            self.back_button.setEnabled(False)
            self.next_button.setText("Select Target ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "attacker_roll":
            self.back_button.setEnabled(True)
            self.next_button.setText("Submit Attack ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "defender_saves":
            self.back_button.setEnabled(True)
            self.next_button.setText("Submit Saves ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "defensive_volley":
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(False)  # Choice buttons handle navigation
        elif self.current_step == "results":
            self.back_button.setEnabled(True)
            self.next_button.setText("Complete Combat ▶")
            self.next_button.setEnabled(True)

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "attacker_roll":
            self.current_step = "select_target"
        elif self.current_step == "defender_saves":
            self.current_step = "attacker_roll"
        elif self.current_step == "defensive_volley":
            self.current_step = "defender_saves"
        elif self.current_step == "results":
            if self.can_defensive_volley:
                self.current_step = "defensive_volley"
            else:
                self.current_step = "defender_saves"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "select_target":
            # Select target
            target_index = self.target_combo.currentData()
            if target_index is not None:
                self.selected_target = self.available_targets[target_index]
                self.current_step = "attacker_roll"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(self, "Target Required", "Please select a target army before proceeding.")
                return

        elif self.current_step == "attacker_roll":
            if self._collect_attacker_results():
                self.current_step = "defender_saves"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self, "Input Required", "Please enter die face results for all attacking units."
                )
                return

        elif self.current_step == "defender_saves":
            if self._collect_defender_results():
                self._calculate_missile_damage()
                if self.can_defensive_volley:
                    self.current_step = "defensive_volley"
                else:
                    self.current_step = "results"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self, "Input Required", "Please enter die face results for all defending units."
                )
                return

        elif self.current_step == "results":
            self._complete_combat()
            return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.combat_cancelled.emit()
        self.reject()
