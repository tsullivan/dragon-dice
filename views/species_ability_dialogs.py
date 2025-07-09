"""
Species Ability Dialogs for Dragon Dice DUA-dependent abilities.

This module provides interactive dialogs for species abilities that require
player interaction and depend on units in the DUA (Dead Unit Area).
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MagicNegationDialog(QDialog):
    """
    Dialog for Frostwings Magic Negation ability.

    When an opponent takes a magic action at a terrain containing Frostwings,
    the Frostwing units may make a magic negation roll before the opponent totals their results.
    """

    negation_completed = Signal(dict)  # Emits negation results
    negation_declined = Signal()

    def __init__(
        self,
        frostwing_player: str,
        frostwing_army: Dict[str, Any],
        opponent_player: str,
        opponent_magic_results: Dict[str, List[str]],
        dead_frostwings_count: int,
        location: str,
        parent=None,
    ):
        super().__init__(parent)
        self.frostwing_player = frostwing_player
        self.frostwing_army = frostwing_army
        self.opponent_player = opponent_player
        self.opponent_magic_results = opponent_magic_results
        self.dead_frostwings_count = min(dead_frostwings_count, 5)  # Max 5 dead Frostwings
        self.location = location

        # Negation state
        self.frostwing_roll_results: Dict[str, List[str]] = {}
        self.magic_negation_amount = 0

        self.setWindowTitle(f"❄️ Magic Negation - {frostwing_player}")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the magic negation UI."""
        main_layout = QVBoxLayout(self)

        # Header info
        header_info = QLabel(
            f"<b>Magic Negation Opportunity</b><br>"
            f"{self.opponent_player} is taking a magic action at {self.location}.<br>"
            f"Your Frostwing units can attempt to negate their magic results.<br>"
            f"<b>Dead Frostwings Available:</b> {self.dead_frostwings_count}/5"
        )
        header_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #e8f4fd; border: 1px solid #2196f3;"
        )
        main_layout.addWidget(header_info)

        # Opponent's magic preview
        opponent_group = QGroupBox(f"{self.opponent_player}'s Magic Results (Before Negation)")
        opponent_layout = QVBoxLayout(opponent_group)

        opponent_text = self._format_opponent_magic_results()
        self.opponent_display = QTextEdit()
        self.opponent_display.setPlainText(opponent_text)
        self.opponent_display.setMaximumHeight(100)
        self.opponent_display.setReadOnly(True)
        opponent_layout.addWidget(self.opponent_display)

        main_layout.addWidget(opponent_group)

        # Frostwing negation roll
        negation_group = QGroupBox("Frostwing Magic Negation Roll")
        negation_layout = QVBoxLayout(negation_group)

        # Instructions
        instructions = QLabel(
            "Roll your Frostwing units and enter the die face results below. "
            "Your magic results will be subtracted from the opponent's total."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 5px; padding: 5px; background-color: #f0f8ff;")
        negation_layout.addWidget(instructions)

        # Frostwing units
        self.frostwing_widgets = []
        frostwing_units = [unit for unit in self.frostwing_army.get("units", []) if unit.get("species") == "Frostwings"]

        for unit in frostwing_units:
            unit_widget = self._create_frostwing_unit_widget(unit)
            self.frostwing_widgets.append(unit_widget)
            negation_layout.addWidget(unit_widget)

        main_layout.addWidget(negation_group)

        # Results preview
        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(100)
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc;")
        main_layout.addWidget(QLabel("Negation Results:"))
        main_layout.addWidget(self.results_display)

        # Buttons
        button_layout = QHBoxLayout()

        self.decline_button = QPushButton("❌ Decline Negation")
        self.decline_button.clicked.connect(self._on_decline)
        button_layout.addWidget(self.decline_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.calculate_button = QPushButton("🔄 Calculate Negation")
        self.calculate_button.clicked.connect(self._calculate_negation)
        button_layout.addWidget(self.calculate_button)

        self.apply_button = QPushButton("✅ Apply Negation")
        self.apply_button.clicked.connect(self._apply_negation)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)

    def _create_frostwing_unit_widget(self, unit: Dict[str, Any]) -> QWidget:
        """Create widget for Frostwing unit die input."""
        from views.magic_action_dialog import MagicDieRollInputWidget

        unit_name = unit.get("name", "Unknown Unit")
        unit_species = unit.get("species", "Unknown")
        unit_health = unit.get("health", 1)

        return MagicDieRollInputWidget(unit_name, unit_species, unit_health)

    def _format_opponent_magic_results(self) -> str:
        """Format opponent's magic results for display."""
        lines = [f"{self.opponent_player}'s Magic Roll:"]

        total_magic = 0
        for unit_name, face_results in self.opponent_magic_results.items():
            magic_count = sum(1 for face in face_results if face.lower().strip() in ["mg", "magic"])
            id_count = sum(1 for face in face_results if face.lower().strip() == "id")

            if magic_count > 0 or id_count > 0:
                lines.append(f"  {unit_name}: {magic_count} magic, {id_count} ID")
                total_magic += magic_count + id_count  # Simplified - actual calculation more complex

        lines.append(f"\nTotal Magic Results: {total_magic} (approximate)")
        return "\n".join(lines)

    def _calculate_negation(self):
        """Calculate magic negation results."""
        # Collect Frostwing roll results
        self.frostwing_roll_results = {}
        frostwing_units = [unit for unit in self.frostwing_army.get("units", []) if unit.get("species") == "Frostwings"]

        for i, widget in enumerate(self.frostwing_widgets):
            if i < len(frostwing_units):
                unit_name = frostwing_units[i].get("name", f"Frostwing {i + 1}")
                face_results = widget.get_face_results()
                self.frostwing_roll_results[unit_name] = face_results

        # Calculate magic negation
        negation_magic = 0
        for unit_name, face_results in self.frostwing_roll_results.items():
            magic_count = sum(1 for face in face_results if face.lower().strip() in ["mg", "magic"])
            id_count = sum(1 for face in face_results if face.lower().strip() == "id")

            # Find unit health for ID calculation
            unit_data = next((u for u in frostwing_units if u.get("name") == unit_name), None)
            if unit_data:
                health = unit_data.get("health", 1)
                negation_magic += magic_count + (id_count * health)

        # Apply DUA limit
        self.magic_negation_amount = min(negation_magic, self.dead_frostwings_count)

        # Update results display
        results_text = "Frostwing Magic Roll Results:\n"
        results_text += f"Raw Magic Generated: {negation_magic}\n"
        results_text += f"DUA Limit ({self.dead_frostwings_count} dead Frostwings): {self.magic_negation_amount}\n"
        results_text += f"\nFinal Magic Negation: {self.magic_negation_amount}"

        self.results_display.setPlainText(results_text)
        self.apply_button.setEnabled(True)

    def _apply_negation(self):
        """Apply the magic negation."""
        negation_result = {
            "success": True,
            "ability_type": "magic_negation",
            "frostwing_player": self.frostwing_player,
            "opponent_player": self.opponent_player,
            "location": self.location,
            "frostwing_roll_results": self.frostwing_roll_results,
            "magic_negation_amount": self.magic_negation_amount,
            "dead_frostwings_count": self.dead_frostwings_count,
            "opponent_magic_results": self.opponent_magic_results,
            "timestamp": "now",
        }

        self.negation_completed.emit(negation_result)
        self.accept()

    def _on_decline(self):
        """Decline to use magic negation."""
        self.negation_declined.emit()
        self.reject()


class FoulStenchDialog(QDialog):
    """
    Dialog for Goblins Foul Stench ability.

    When an army containing Goblins takes a melee action, the opposing player
    must select units that cannot perform a counter-attack.
    """

    stench_completed = Signal(dict)  # Emits selected units that cannot counter-attack

    def __init__(
        self,
        goblin_player: str,
        opponent_player: str,
        opponent_army: Dict[str, Any],
        dead_goblins_count: int,
        parent=None,
    ):
        super().__init__(parent)
        self.goblin_player = goblin_player
        self.opponent_player = opponent_player
        self.opponent_army = opponent_army
        self.dead_goblins_count = min(dead_goblins_count, 3)  # Max 3 dead Goblins

        # Selection state
        self.selected_units: List[str] = []
        self.unit_checkboxes: List[QCheckBox] = []

        self.setWindowTitle(f"🤢 Foul Stench - {opponent_player}")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the foul stench unit selection UI."""
        main_layout = QVBoxLayout(self)

        # Header info
        header_info = QLabel(
            f"<b>Foul Stench Effect</b><br>"
            f"{self.goblin_player}'s dead Goblins emit a foul stench!<br>"
            f"Select <b>{self.dead_goblins_count}</b> of your units that cannot counter-attack this turn.<br>"
            f"<b>Dead Goblins:</b> {self.dead_goblins_count}/3"
        )
        header_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fff8e1; border: 1px solid #ffb300;"
        )
        main_layout.addWidget(header_info)

        # Unit selection
        selection_group = QGroupBox(f"Select {self.dead_goblins_count} Units That Cannot Counter-Attack")
        selection_layout = QVBoxLayout(selection_group)

        # Scrollable unit list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        units_widget = QWidget()
        units_layout = QVBoxLayout(units_widget)

        opponent_units = self.opponent_army.get("units", [])
        for unit in opponent_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_species = unit.get("species", "Unknown")
            unit_health = unit.get("health", 1)

            checkbox = QCheckBox(f"{unit_name} - {unit_species} (Health: {unit_health})")
            checkbox.stateChanged.connect(self._on_unit_selection_changed)
            self.unit_checkboxes.append(checkbox)
            units_layout.addWidget(checkbox)

        scroll_area.setWidget(units_widget)
        selection_layout.addWidget(scroll_area)

        main_layout.addWidget(selection_group)

        # Selection status
        self.status_label = QLabel(f"Selected: 0/{self.dead_goblins_count}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; margin: 10px; padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self._clear_selection)
        button_layout.addWidget(self.clear_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.confirm_button = QPushButton("✅ Confirm Selection")
        self.confirm_button.clicked.connect(self._confirm_selection)
        self.confirm_button.setEnabled(False)
        button_layout.addWidget(self.confirm_button)

        main_layout.addLayout(button_layout)

    def _on_unit_selection_changed(self):
        """Handle unit selection change."""
        selected_count = sum(1 for checkbox in self.unit_checkboxes if checkbox.isChecked())

        # Update status
        self.status_label.setText(f"Selected: {selected_count}/{self.dead_goblins_count}")

        # Color coding
        if selected_count == self.dead_goblins_count:
            self.status_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 5px; background-color: #e8f5e8; color: #2e7d32;"
            )
            self.confirm_button.setEnabled(True)
        elif selected_count < self.dead_goblins_count:
            self.status_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 5px; background-color: #fff3e0; color: #ef6c00;"
            )
            self.confirm_button.setEnabled(False)
        else:  # Too many selected
            self.status_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 5px; background-color: #ffebee; color: #c62828;"
            )
            self.confirm_button.setEnabled(False)

            # Disable additional selections if limit reached
            if selected_count > self.dead_goblins_count:
                # Find last checked and uncheck it
                for checkbox in reversed(self.unit_checkboxes):
                    if checkbox.isChecked():
                        checkbox.setChecked(False)
                        break

    def _clear_selection(self):
        """Clear all unit selections."""
        for checkbox in self.unit_checkboxes:
            checkbox.setChecked(False)

    def _confirm_selection(self):
        """Confirm the unit selection."""
        selected_units = []
        opponent_units = self.opponent_army.get("units", [])

        for i, checkbox in enumerate(self.unit_checkboxes):
            if checkbox.isChecked() and i < len(opponent_units):
                unit_name = opponent_units[i].get("name", f"Unit {i + 1}")
                selected_units.append(unit_name)

        stench_result = {
            "success": True,
            "ability_type": "foul_stench",
            "goblin_player": self.goblin_player,
            "opponent_player": self.opponent_player,
            "selected_units": selected_units,
            "dead_goblins_count": self.dead_goblins_count,
            "units_affected": len(selected_units),
            "timestamp": "now",
        }

        self.stench_completed.emit(stench_result)
        self.accept()


class CursedBulletsDialog(QDialog):
    """
    Dialog for Lava Elves Cursed Bullets ability.

    Shows which missile results are cursed and can only be reduced by spell-generated saves.
    """

    def __init__(
        self,
        lava_elf_player: str,
        missile_results: Dict[str, List[str]],
        dead_lava_elves_count: int,
        target_army: Dict[str, Any],
        parent=None,
    ):
        super().__init__(parent)
        self.lava_elf_player = lava_elf_player
        self.missile_results = missile_results
        self.dead_lava_elves_count = min(dead_lava_elves_count, 3)  # Max 3 dead Lava Elves
        self.target_army = target_army

        self.setWindowTitle(f"💀 Cursed Bullets - {lava_elf_player}")
        self.setModal(True)
        self.setMinimumSize(500, 300)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the cursed bullets information UI."""
        main_layout = QVBoxLayout(self)

        # Header info
        header_info = QLabel(
            f"<b>Cursed Bullets Effect</b><br>"
            f"{self.lava_elf_player}'s dead Lava Elves curse some missile results!<br>"
            f"Cursed missiles can only be reduced by <b>spell-generated save results</b>.<br>"
            f"<b>Dead Lava Elves:</b> {self.dead_lava_elves_count}/3"
        )
        header_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fce4ec; border: 1px solid #e91e63;"
        )
        main_layout.addWidget(header_info)

        # Missile results breakdown
        results_group = QGroupBox("Missile Attack Results")
        results_layout = QVBoxLayout(results_group)

        # Calculate cursed bullets
        total_missiles = 0
        for unit_name, face_results in self.missile_results.items():
            missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])
            total_missiles += missile_count

        cursed_missiles = min(self.dead_lava_elves_count, total_missiles)
        normal_missiles = total_missiles - cursed_missiles

        results_text = QTextEdit()
        results_text.setPlainText(
            f"Total Missile Results: {total_missiles}\n"
            f"\n"
            f"💀 Cursed Missiles: {cursed_missiles}\n"
            f"   - Can only be reduced by spell-generated saves\n"
            f"   - Normal unit save results have no effect\n"
            f"\n"
            f"⚔️ Normal Missiles: {normal_missiles}\n"
            f"   - Can be reduced by any save results\n"
            f"\n"
            f"Defending army must account for this when allocating saves!"
        )
        results_text.setMaximumHeight(200)
        results_text.setReadOnly(True)
        results_layout.addWidget(results_text)

        main_layout.addWidget(results_group)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.understood_button = QPushButton("✅ Understood")
        self.understood_button.clicked.connect(self.accept)
        button_layout.addWidget(self.understood_button)

        main_layout.addLayout(button_layout)
