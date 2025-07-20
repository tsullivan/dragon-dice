"""
Melee Combat Dialog for Dragon Dice - captures individual die face results for proper SAI tracking.

This dialog handles the complete melee combat flow:
1. Attacker rolls dice and inputs individual face results
2. Defender rolls saves and inputs individual face results
3. Calculate and display final damage after SAI processing
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
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

# Combat analysis handled through CombatAnalysisController


class DieRollInputWidget(QWidget):
    """Widget for inputting individual die face results."""

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
            face_input.setPlaceholderText("M/Mi/Mg/S/ID/SAI")
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


class MeleeCombatDialog(QDialog):
    """
    Dialog for handling melee combat with detailed die face input.

    This dialog captures individual die face results from both attacker and defender
    to properly calculate SAI effects and final damage.
    """

    combat_completed = Signal(dict)  # Emits combat results
    combat_cancelled = Signal()

    def __init__(
        self,
        attacker_name: str,
        attacker_army: Dict[str, Any],
        defender_name: str,
        defender_army: Dict[str, Any],
        location: str,
        combat_analysis_controller=None,
        parent=None,
    ):
        super().__init__(parent)
        self.attacker_name = attacker_name
        self.attacker_army = attacker_army
        self.defender_name = defender_name
        self.defender_army = defender_army
        self.location = location

        # Combat state
        self.current_step = "attacker_roll"  # attacker_roll, defender_saves, calculate_damage, counter_attack
        self.attacker_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.defender_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.final_damage = 0
        self.counter_attack_damage = 0

        # Combat analysis through controller or fallback
        self.combat_analysis_controller = combat_analysis_controller
        if not self.combat_analysis_controller:
            print("[MeleeCombatDialog] No combat analysis controller provided - using fallback")

        self.setWindowTitle(f"⚔️ Melee Combat at {location}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._update_step_display()

    def _analyze_combat_results(
        self,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        is_attacker: bool = True,
    ) -> Dict[str, Any]:
        """Analyze combat results using controller or fallback."""
        if self.combat_analysis_controller:
            terrain_elements = self._get_terrain_elements()
            return self.combat_analysis_controller.analyze_combat_roll(
                roll_results, combat_type, army_units, terrain_elements, is_attacker
            )
        # Fallback - simplified analysis without SAI processing
        return self._fallback_combat_analysis(roll_results, combat_type)

    def _fallback_combat_analysis(self, roll_results: Dict[str, List[str]], combat_type: str) -> Dict[str, Any]:
        """Simplified combat analysis fallback when no controller available."""
        print(f"[MeleeCombatDialog] Using fallback analysis for {combat_type}")
        # Simple counting without SAI effects
        total_results = {"melee": 0, "save": 0}
        for _unit_name, faces in roll_results.items():
            for face in faces:
                if face.lower() in ["m", "melee"]:
                    total_results["melee"] += 1
                elif face.lower() in ["s", "save"]:
                    total_results["save"] += 1
        return {"total_results": total_results, "summary": f"{combat_type}: {total_results}"}

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
        combat_info = QLabel(f"🏛️ {self.location}: {self.attacker_name} attacks {self.defender_name}")
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

        if self.current_step == "attacker_roll":
            self._show_attacker_roll()
        elif self.current_step == "defender_saves":
            self._show_defender_saves()
        elif self.current_step == "calculate_damage":
            self._show_damage_calculation()
        elif self.current_step == "counter_attack":
            self._show_counter_attack()

        self._update_buttons()

    def _show_attacker_roll(self):
        """Show attacker dice roll input."""
        self.step_label.setText("Step 1: ⚔️ Attacker Melee Roll")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            f"<b>{self.attacker_name}</b>: Roll all units in your army and enter each die face result below."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #e8f4fd;")
        self.content_layout.addWidget(instructions)

        # Army units
        self.attacker_roll_widgets = []
        army_units = self.attacker_army.get("units", [])

        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_health = unit.get("health", 1)

            unit_widget = DieRollInputWidget(unit_name, unit_health)
            self.attacker_roll_widgets.append(unit_widget)
            self.content_layout.addWidget(unit_widget)

        # Check for attacker species abilities
        terrain_elements = self._get_terrain_elements()
        attacker_units = self.attacker_army.get("units", [])

        # Flaming Shields: Saves → Melee at fire terrain (attacker only)
        if "fire" in terrain_elements and any(unit.get("species") == "Firewalkers" for unit in attacker_units):
            flaming_shields_note = QLabel(
                "🔥 <b>Flaming Shields:</b> Firewalkers can count save results as melee results at fire terrain!"
            )
            flaming_shields_note.setWordWrap(True)
            flaming_shields_note.setStyleSheet(
                "background-color: #fff4e6; padding: 10px; border: 1px solid #ff922b; margin: 10px;"
            )
            self.content_layout.addWidget(flaming_shields_note)

        # Helpful note
        note = QLabel(
            "💡 Tip: Use shortcuts like M=Melee, Mi=Missile, Mg=Magic, S=Save, ID=ID face, SAI=Special Action Icon, Ma=Maneuver"
        )
        note.setStyleSheet("font-style: italic; color: #666; margin: 10px;")
        note.setWordWrap(True)
        self.content_layout.addWidget(note)

    def _show_defender_saves(self):
        """Show defender save roll input."""
        self.step_label.setText("Step 2: 🛡️ Defender Save Roll")
        self.results_display.show()

        # Show attacker results with analysis
        attacker_army_units = self.attacker_army.get("units", [])
        attacker_result = self._analyze_combat_results(
            self.attacker_results, "melee", attacker_army_units, is_attacker=True
        )
        attacker_summary = attacker_result.get("summary", str(attacker_result))
        self.results_display.setText(f"Attacker Results:\n{attacker_summary}")

        # Instructions
        instructions = QLabel(
            f"<b>{self.defender_name}</b>: Roll all units in your army and enter each die face result below."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #fdf8e8;")
        self.content_layout.addWidget(instructions)

        # Army units
        self.defender_roll_widgets = []
        army_units = self.defender_army.get("units", [])

        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_health = unit.get("health", 1)

            unit_widget = DieRollInputWidget(unit_name, unit_health)
            self.defender_roll_widgets.append(unit_widget)
            self.content_layout.addWidget(unit_widget)

    def _show_damage_calculation(self):
        """Show damage calculation and resolution."""
        self.step_label.setText("Step 3: 🎯 Damage Calculation")
        self.results_display.show()

        # Get terrain elements (in a real implementation, this would come from game state)
        self._get_terrain_elements()

        # Process attacker results
        attacker_army_units = self.attacker_army.get("units", [])
        attacker_result = self._analyze_combat_results(
            self.attacker_results, "melee", attacker_army_units, is_attacker=True
        )

        # Process defender results
        defender_army_units = self.defender_army.get("units", [])
        defender_result = self._analyze_combat_results(
            self.defender_results, "save", defender_army_units, is_attacker=False
        )

        # Calculate final damage
        attacker_melee = attacker_result.get("total_results", {}).get("melee", 0)
        defender_saves = defender_result.get("total_results", {}).get("save", 0)
        self.final_damage = max(0, attacker_melee - defender_saves)

        # Format detailed results
        attacker_summary = attacker_result.get("summary", str(attacker_result))
        defender_summary = defender_result.get("summary", str(defender_result))

        # Display results
        results_text = f"""ATTACKER RESULTS:
{attacker_summary}

DEFENDER RESULTS:
{defender_summary}

FINAL DAMAGE CALCULATION:
{attacker_result.final_melee} melee - {defender_result.final_save} saves = {self.final_damage} damage"""

        # Check for species abilities used in this attack
        ability_activations = []
        for sai_result in attacker_result.sai_results:
            if sai_result.sai_type == "flaming_shields":
                ability_activations.append("🔥 Flaming Shields activated! (Saves counted as melee at fire terrain)")

        for sai_result in defender_result.sai_results:
            if sai_result.sai_type == "cantrip":
                ability_activations.append("✨ Cantrip magic available for defensive spells")

        if ability_activations:
            results_text += "\n\nSPECIES ABILITIES:\n" + "\n".join(ability_activations)

        self.results_display.setText(results_text)

        # Damage application instructions
        if self.final_damage > 0:
            damage_instructions = QLabel(
                f"<b>Damage Application:</b><br>"
                f"The defender must remove {self.final_damage} health worth of units from their army.<br>"
                f"You may choose which units to remove to equal this damage total."
            )
        else:
            damage_instructions = QLabel(
                "<b>No Damage:</b><br>The defender's saves completely negated the attack. No units are removed."
            )

        damage_instructions.setWordWrap(True)
        damage_instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f8f8f8;")
        self.content_layout.addWidget(damage_instructions)

    def _show_counter_attack(self):
        """Show counter-attack opportunity."""
        self.step_label.setText("Step 4: ⚔️ Counter-Attack")

        # Check for species abilities available during counter-attack
        terrain_elements = self._get_terrain_elements()
        defender_units = self.defender_army.get("units", [])

        counter_info_text = (
            f"<b>Counter-Attack Opportunity:</b><br>"
            f"The defender ({self.defender_name}) may now counter-attack using the same melee process.<br>"
            f"This is optional - you can choose to skip the counter-attack."
        )

        # Check for species abilities during counter-attack
        ability_notes = []

        # Dwarven Might: Saves → Melee at fire terrain
        if "fire" in terrain_elements and any(unit.get("species") == "Dwarves" for unit in defender_units):
            ability_notes.append(
                "⚡ <b>Dwarven Might:</b> Dwarves can count save results as melee results at fire terrain!"
            )

        # Stampede: Maneuver → Melee at earth+air terrain
        if (
            "earth" in terrain_elements
            and "air" in terrain_elements
            and any(unit.get("species") == "Feral" for unit in defender_units)
        ):
            ability_notes.append(
                "🐃 <b>Stampede:</b> Feral can count maneuver results as melee results at earth+air terrain!"
            )

        if ability_notes:
            counter_info_text += "<br><br>" + "<br>".join(ability_notes)

        counter_info = QLabel(counter_info_text)
        counter_info.setWordWrap(True)
        counter_info.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f8ff;")
        self.content_layout.addWidget(counter_info)

        # Counter-attack choice buttons
        choice_layout = QHBoxLayout()

        counter_attack_btn = QPushButton("⚔️ Counter-Attack")
        counter_attack_btn.clicked.connect(self._start_counter_attack)
        choice_layout.addWidget(counter_attack_btn)

        skip_counter_btn = QPushButton("⏭️ Skip Counter-Attack")
        skip_counter_btn.clicked.connect(self._skip_counter_attack)
        choice_layout.addWidget(skip_counter_btn)

        choice_widget = QWidget()
        choice_widget.setLayout(choice_layout)
        self.content_layout.addWidget(choice_widget)

    def _calculate_roll_summary(self, roll_results: Dict[str, List[str]], focus_type: str) -> str:
        """Calculate a summary of roll results."""
        if not roll_results:
            return "No results"

        total_counts: Dict[str, int] = {}
        unit_summaries = []

        for unit_name, face_results in roll_results.items():
            unit_counts: Dict[str, int] = {}
            for face_result in face_results:
                if face_result:
                    normalized = face_result.lower().strip()
                    # Map common abbreviations
                    if normalized in ["m", "melee"]:
                        key = "melee"
                    elif normalized in ["mi", "missile"]:
                        key = "missile"
                    elif normalized in ["mg", "magic"]:
                        key = "magic"
                    elif normalized in ["s", "save"]:
                        key = "save"
                    elif normalized in ["id"]:
                        key = "id"
                    elif normalized in ["sai"]:
                        key = "sai"
                    elif normalized in ["ma", "maneuver"]:
                        key = "maneuver"
                    else:
                        key = normalized

                    unit_counts[key] = unit_counts.get(key, 0) + 1
                    total_counts[key] = total_counts.get(key, 0) + 1

            # Create unit summary
            unit_summary_parts = []
            for result_type, count in unit_counts.items():
                if count > 0:
                    unit_summary_parts.append(f"{result_type}: {count}")

            unit_summaries.append(
                f"  {unit_name}: {', '.join(unit_summary_parts) if unit_summary_parts else 'no results'}"
            )

        # Create total summary
        total_summary_parts = []
        for result_type, count in total_counts.items():
            if count > 0:
                total_summary_parts.append(f"{result_type}: {count}")

        summary = f"Total: {', '.join(total_summary_parts) if total_summary_parts else 'no results'}\n"
        summary += "\n".join(unit_summaries)

        return summary

    def _count_result_type(self, roll_results: Dict[str, List[str]], target_types: List[str]) -> int:
        """Count specific result types from roll results."""
        count = 0
        for _unit_name, face_results in roll_results.items():
            for face_result in face_results:
                if face_result:
                    normalized = face_result.lower().strip()
                    if normalized in target_types:
                        count += 1
        return count

    def _collect_attacker_results(self) -> bool:
        """Collect attacker roll results from input widgets."""
        if not hasattr(self, "attacker_roll_widgets"):
            return False

        self.attacker_results = {}

        for i, widget in enumerate(self.attacker_roll_widgets):
            army_units = self.attacker_army.get("units", [])
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

        for i, widget in enumerate(self.defender_roll_widgets):
            army_units = self.defender_army.get("units", [])
            if i < len(army_units):
                unit_name = army_units[i].get("name", f"Unit {i + 1}")
                face_results = widget.get_face_results()
                self.defender_results[unit_name] = face_results

        return True

    def _start_counter_attack(self):
        """Start counter-attack process."""
        # Create counter-attack dialog with roles reversed
        counter_dialog = MeleeCombatDialog(
            attacker_name=self.defender_name,  # Defender becomes attacker
            attacker_army=self.defender_army,
            defender_name=self.attacker_name,  # Attacker becomes defender
            defender_army=self.attacker_army,
            location=self.location,
            parent=self,
        )

        # Connect signals
        counter_dialog.combat_completed.connect(self._handle_counter_attack_completed)
        counter_dialog.combat_cancelled.connect(self._handle_counter_attack_cancelled)

        # Show dialog
        counter_dialog.exec()

    def _handle_counter_attack_completed(self, counter_result: Dict[str, Any]):
        """Handle completed counter-attack."""
        self.counter_attack_damage = counter_result.get("final_damage", 0)

        # Add counter-attack info to results display
        current_text = self.results_display.toPlainText()
        counter_text = "\n\nCOUNTER-ATTACK RESULTS:\n"
        counter_text += f"Counter-attacker: {counter_result.get('attacker', 'Unknown')}\n"
        counter_text += f"Counter-damage: {self.counter_attack_damage}\n"

        # Check for species ability usage during counter-attack
        attacker_results = counter_result.get("attacker_results", {})
        if any("dwarven_might" in str(result) for result in attacker_results.values()):
            counter_text += "⚡ Dwarven Might activated! (Saves counted as melee at fire terrain)\n"
        if any("stampede" in str(result) for result in attacker_results.values()):
            counter_text += "🐃 Stampede activated! (Maneuver counted as melee at earth+air terrain)\n"

        self.results_display.setText(current_text + counter_text)

        # Complete the combat with both attack and counter-attack results
        self._complete_combat()

    def _handle_counter_attack_cancelled(self):
        """Handle cancelled counter-attack."""
        # Continue without counter-attack
        self._complete_combat()

    def _get_terrain_elements(self) -> List[str]:
        """Get terrain elements for the combat location."""
        # In a real implementation, this would get terrain data from the game state
        # For now, return a placeholder that includes fire for testing Dwarven Might
        # This would be replaced with actual terrain data lookup

        # Example terrain elements based on location name
        terrain_mappings = {
            "Highland": ["fire", "earth"],
            "Flatland": ["air", "earth"],
            "Coastland": ["air", "water"],
            "Swampland": ["water", "earth"],
            "Wasteland": ["air", "fire"],
            "Feyland": ["water", "fire"],
            "Deadland": ["death"],
        }

        # Extract terrain type from location (simplified)
        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in self.location.lower():
                return elements

        # Default to empty if terrain type not recognized
        return []

    def _skip_counter_attack(self):
        """Skip counter-attack and complete combat."""
        self._complete_combat()

    def _complete_combat(self):
        """Complete the combat and emit results."""
        combat_result = {
            "success": True,
            "combat_type": "melee",
            "attacker": self.attacker_name,
            "defender": self.defender_name,
            "location": self.location,
            "attacker_results": self.attacker_results,
            "defender_results": self.defender_results,
            "final_damage": self.final_damage,
            "counter_attack_damage": self.counter_attack_damage,
            "timestamp": "now",  # Could use actual timestamp
        }

        self.combat_completed.emit(combat_result)
        self.accept()

    def _update_buttons(self):
        """Update button states based on current step."""
        if self.current_step == "attacker_roll":
            self.back_button.setEnabled(False)
            self.next_button.setText("Submit Attack ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "defender_saves":
            self.back_button.setEnabled(True)
            self.next_button.setText("Submit Saves ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "calculate_damage":
            self.back_button.setEnabled(True)
            self.next_button.setText("Continue ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "counter_attack":
            self.back_button.setEnabled(True)
            self.next_button.setText("Complete Combat ▶")
            self.next_button.setEnabled(True)

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "defender_saves":
            self.current_step = "attacker_roll"
        elif self.current_step == "calculate_damage":
            self.current_step = "defender_saves"
        elif self.current_step == "counter_attack":
            self.current_step = "calculate_damage"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "attacker_roll":
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
                self.current_step = "calculate_damage"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self, "Input Required", "Please enter die face results for all defending units."
                )
                return

        elif self.current_step == "calculate_damage":
            self.current_step = "counter_attack"

        elif self.current_step == "counter_attack":
            self._complete_combat()
            return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.combat_cancelled.emit()
        self.reject()
