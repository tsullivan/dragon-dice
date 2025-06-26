from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QSpacerItem,
    QSizePolicy,
    QListWidget,
    QLineEdit,
)
import constants
from PySide6.QtCore import Qt, Signal
from typing import List, Dict, Any, Optional


class ActionDialog(QDialog):
    """
    Dialog for handling proper Dragon Dice action flow:
    1. Show action summary and army information
    2. Attacker rolls dice and submits results
    3. Defender rolls saves and submits results
    4. Show action resolution and effects
    """

    action_completed = Signal(dict)  # Emits action results
    action_cancelled = Signal()

    def __init__(
        self,
        action_type: str,  # "MELEE", "MISSILE", or "MAGIC"
        current_player_name: str,
        acting_army: Dict[str, Any],
        all_players_data: Dict[str, Dict[str, Any]],
        terrain_data: Dict[str, Dict[str, Any]],
        parent=None,
    ):
        super().__init__(parent)
        self.action_type = action_type
        self.current_player_name = current_player_name
        self.acting_army = acting_army
        self.all_players_data = all_players_data
        self.terrain_data = terrain_data

        # Dialog state
        self.current_step = "attacker_roll"  # attacker_roll, defender_saves, results
        self.attacker_results = None
        self.defender_results = None
        self.final_result = None

        self.setWindowTitle(f"{action_type.title()} Action")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._update_step_display()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)

        # Step indicator
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.step_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.step_label.setFont(font)
        main_layout.addWidget(self.step_label)

        # Content area (will be dynamically updated)
        self.content_widget = QGroupBox()
        self.content_layout = QVBoxLayout(self.content_widget)
        main_layout.addWidget(self.content_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.setMaximumWidth(100)
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)

        button_layout.addSpacerItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.next_button = QPushButton("Next")
        self.next_button.setMaximumWidth(100)
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
        elif self.current_step == "results":
            self._show_results()

        self._update_buttons()

    def _show_attacker_roll(self):
        """Show attacker roll input."""
        action_icon = constants.ACTION_ICONS.get(self.action_type, "⚔️")
        self.step_label.setText(
            f"Step 1: {action_icon} {self.action_type.title()} Attack"
        )

        if not self.acting_army:
            return

        # Show action summary
        location = self.acting_army.get("location", "Unknown")
        army_name = self.acting_army.get("name", "Unknown Army")

        summary_text = f"{self.current_player_name}'s {army_name} performs a {self.action_type.lower()} attack at {location}."
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(summary_label)

        # Show units in the army
        units = self.acting_army.get("units", [])
        if units:
            units_label = QLabel("Units participating in the attack:")
            self.content_layout.addWidget(units_label)

            unit_list = QListWidget()
            unit_list.setMaximumHeight(100)
            for unit in units:
                unit_name = unit.get("name", "Unknown Unit")
                unit_health = unit.get("health", 0)
                unit_list.addItem(f"• {unit_name} (Health: {unit_health})")
            self.content_layout.addWidget(unit_list)

        # Dice roll input
        roll_group = QGroupBox(f"Roll Your {self.action_type.title()} Dice")
        roll_layout = QVBoxLayout(roll_group)

        instruction_text = f"Roll all {self.action_type.lower()} dice for your army and enter the results below:"
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        roll_layout.addWidget(instruction_label)

        self.attacker_dice_input = QLineEdit()
        self.attacker_dice_input.setPlaceholderText(
            "e.g., '3 melee, 2 saves, 1 SAI' or 'MM,S,SAI,M,S'"
        )
        roll_layout.addWidget(self.attacker_dice_input)

        self.content_layout.addWidget(roll_group)

    def _show_defender_saves(self):
        """Show defender save roll input."""
        self.step_label.setText("Step 2: 🛡️ Defender Save Rolls")

        # Show attack results summary
        if self.attacker_results:
            results_text = f"Attacker rolled: {self.attacker_results}\n\n"
            results_text += (
                "The defender must now roll save dice to defend against this attack."
            )

            results_label = QLabel(results_text)
            results_label.setWordWrap(True)
            results_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
            self.content_layout.addWidget(results_label)

        # Defender save input
        save_group = QGroupBox("Defender Save Rolls")
        save_layout = QVBoxLayout(save_group)

        instruction_text = (
            "Defending player: Roll your save dice and enter the results below:"
        )
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        save_layout.addWidget(instruction_label)

        self.defender_dice_input = QLineEdit()
        self.defender_dice_input.setPlaceholderText(
            "e.g., '2 saves, 1 SAI' or 'S,S,SAI'"
        )
        save_layout.addWidget(self.defender_dice_input)

        self.content_layout.addWidget(save_group)

    def _show_results(self):
        """Show action results."""
        action_icon = constants.ACTION_ICONS.get(self.action_type, "⚔️")
        self.step_label.setText(f"Step 3: {action_icon} Action Results")

        if not self.attacker_results or not self.defender_results:
            return

        # Simulate action resolution (simplified)
        result_text = f"Attacker rolled: {self.attacker_results}\n"
        result_text += f"Defender rolled: {self.defender_results}\n\n"
        result_text += f"{self.action_type.title()} action completed!"

        # Store the result for emission
        self.final_result = {
            "success": True,
            "action_type": self.action_type,
            "attacker": self.current_player_name,
            "attacker_results": self.attacker_results,
            "defender_results": self.defender_results,
            "army": self.acting_army,
            "location": self.acting_army.get("location", ""),
        }

        result_label = QLabel(result_text)
        result_label.setWordWrap(True)
        self.content_layout.addWidget(result_label)

    def _update_buttons(self):
        """Update button states based on current step."""
        if self.current_step == "attacker_roll":
            self.back_button.setEnabled(False)
            self.next_button.setText("Submit Attack")
            self.next_button.setEnabled(True)
        elif self.current_step == "defender_saves":
            self.back_button.setEnabled(True)
            self.next_button.setText("Submit Saves")
            self.next_button.setEnabled(True)
        elif self.current_step == "results":
            self.back_button.setEnabled(True)
            self.next_button.setText("Complete Action")
            self.next_button.setEnabled(True)

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "defender_saves":
            self.current_step = "attacker_roll"
        elif self.current_step == "results":
            self.current_step = "defender_saves"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "attacker_roll":
            attacker_input = self.attacker_dice_input.text().strip()
            if not attacker_input:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self,
                    "Input Required",
                    "Please enter your dice roll results before continuing.",
                    "Example formats: 'MM,S,SAI' or '2 melee, 1 save, 1 SAI'",
                )
                return

            self.attacker_results = attacker_input
            self.current_step = "defender_saves"

        elif self.current_step == "defender_saves":
            defender_input = self.defender_dice_input.text().strip()
            if not defender_input:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self,
                    "Input Required",
                    "Please enter the defender's save roll results before continuing.",
                    "Example formats: 'S,S,SAI' or '2 saves, 1 SAI'",
                )
                return

            self.defender_results = defender_input
            self.current_step = "results"

        elif self.current_step == "results":
            # Complete the action
            if hasattr(self, "final_result") and self.final_result:
                self.action_completed.emit(self.final_result)
            self.accept()
            return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.action_cancelled.emit()
        self.reject()
