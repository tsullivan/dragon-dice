"""
Mutate Save Roll Dialog for Dragon Dice Swamp Stalkers' Mutate ability.

This dialog handles the save roll resolution for units targeted by the Mutate ability.
Targeted units in the opponent's Reserves Area must make save rolls, and those that
fail are killed, allowing the Swamp Stalker player to recruit/promote accordingly.
"""

from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class MutateSaveRollWidget(QWidget):
    """Widget for rolling saves for a single targeted unit."""

    def __init__(self, unit_data: Dict[str, Any], opponent_name: str, parent=None):
        super().__init__(parent)
        self.unit_data = unit_data
        self.opponent_name = opponent_name
        self.save_result = None  # Will be True (saved) or False (killed)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the save roll widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Unit info
        unit_name = self.unit_data.get("name", "Unknown Unit")
        unit_species = self.unit_data.get("species", "Unknown")
        unit_health = self.unit_data.get("health", 1)
        elements = self.unit_data.get("elements", [])
        element_text = f" ({'/'.join(elements)})" if elements else ""

        unit_label = QLabel(f"<b>{unit_name}</b> - {unit_species} (Health: {unit_health}){element_text}")
        unit_label.setWordWrap(True)
        layout.addWidget(unit_label)

        # Save roll input
        roll_layout = QHBoxLayout()
        roll_layout.addWidget(QLabel("Roll die faces:"))

        self.die_inputs: List[QLineEdit] = []
        for i in range(unit_health):  # Number of dice = health
            die_input = QLineEdit()
            die_input.setMaximumWidth(50)
            die_input.setPlaceholderText("Face")
            die_input.setToolTip("Enter die face result (S for save, others for no save)")
            self.die_inputs.append(die_input)
            roll_layout.addWidget(die_input)

        layout.addLayout(roll_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.evaluate_button = QPushButton("Evaluate Save")
        self.evaluate_button.clicked.connect(self._evaluate_save)
        button_layout.addWidget(self.evaluate_button)

        self.quick_save_button = QPushButton("Quick Save")
        self.quick_save_button.clicked.connect(self._quick_save)
        button_layout.addWidget(self.quick_save_button)

        self.quick_fail_button = QPushButton("Quick Fail")
        self.quick_fail_button.clicked.connect(self._quick_fail)
        button_layout.addWidget(self.quick_fail_button)

        layout.addLayout(button_layout)

        # Result display
        self.result_label = QLabel("Roll dice and evaluate save")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("margin: 5px; padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.result_label)

    def _evaluate_save(self):
        """Evaluate the save roll based on die face inputs."""
        # Count save results
        save_count = 0
        for die_input in self.die_inputs:
            face_result = die_input.text().strip().upper()
            if face_result in ["S", "SAVE"]:
                save_count += 1

        # Determine if unit is saved
        self.save_result = save_count > 0

        # Update display
        if self.save_result:
            self.result_label.setText(f"✅ SAVED ({save_count} save result{'s' if save_count != 1 else ''})")
            self.result_label.setStyleSheet(
                "margin: 5px; padding: 5px; background-color: #e8f5e8; color: #2e7d32; font-weight: bold;"
            )
        else:
            self.result_label.setText("❌ KILLED (no save results)")
            self.result_label.setStyleSheet(
                "margin: 5px; padding: 5px; background-color: #ffebee; color: #c62828; font-weight: bold;"
            )

        # Disable inputs after evaluation
        for die_input in self.die_inputs:
            die_input.setEnabled(False)
        self.evaluate_button.setEnabled(False)
        self.quick_save_button.setEnabled(False)
        self.quick_fail_button.setEnabled(False)

    def _quick_save(self):
        """Quickly set the unit as saved."""
        self.save_result = True
        self.result_label.setText("✅ SAVED (quick save)")
        self.result_label.setStyleSheet(
            "margin: 5px; padding: 5px; background-color: #e8f5e8; color: #2e7d32; font-weight: bold;"
        )
        self._disable_inputs()

    def _quick_fail(self):
        """Quickly set the unit as killed."""
        self.save_result = False
        self.result_label.setText("❌ KILLED (quick fail)")
        self.result_label.setStyleSheet(
            "margin: 5px; padding: 5px; background-color: #ffebee; color: #c62828; font-weight: bold;"
        )
        self._disable_inputs()

    def _disable_inputs(self):
        """Disable all input controls."""
        for die_input in self.die_inputs:
            die_input.setEnabled(False)
        self.evaluate_button.setEnabled(False)
        self.quick_save_button.setEnabled(False)
        self.quick_fail_button.setEnabled(False)

    def get_save_result(self) -> Optional[bool]:
        """Get the save result. Returns None if not evaluated yet."""
        return self.save_result

    def is_evaluated(self) -> bool:
        """Check if the save roll has been evaluated."""
        return self.save_result is not None


class MutateSaveRollDialog(QDialog):
    """
    Dialog for resolving save rolls for units targeted by Mutate ability.
    
    This dialog presents each targeted unit and allows the opponent to roll
    saves for them. Units that fail saves are killed, and the health-worth
    of killed units becomes available for Swamp Stalker recruitment/promotion.
    """

    mutate_resolved = Signal(dict)  # Emits mutate resolution results

    def __init__(self, mutate_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.mutate_data = mutate_data
        self.swamp_stalker_player = mutate_data["swamp_stalker_player"]
        self.targets = mutate_data["targets"]
        self.recruiting_army = mutate_data["recruiting_army"]

        # Resolution state
        self.save_widgets: List[MutateSaveRollWidget] = []
        self.killed_units: List[Dict[str, Any]] = []
        self.saved_units: List[Dict[str, Any]] = []
        self.total_health_killed = 0

        self.setWindowTitle(f"🧬 Mutate Save Rolls - {self.swamp_stalker_player}")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the mutate save roll UI."""
        main_layout = QVBoxLayout(self)

        # Header
        header_info = QLabel(
            f"<b>Mutate Save Roll Resolution</b><br>"
            f"{self.swamp_stalker_player} is using the Mutate ability.<br>"
            f"Targeted units must make save rolls. Those that fail are killed.<br>"
            f"<b>Targets:</b> {len(self.targets)} units"
        )
        header_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_info.setWordWrap(True)
        header_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fff8e1; border: 1px solid #ffb300;"
        )
        main_layout.addWidget(header_info)

        # Instructions
        instructions = QLabel(
            "For each targeted unit, roll dice equal to its health. "
            "If any die shows a save result (S), the unit survives. "
            "Otherwise, it is killed and contributes to recruitment/promotion."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f8ff; border: 1px solid #2196f3;")
        main_layout.addWidget(instructions)

        # Targeted units
        units_group = QGroupBox("Targeted Units")
        units_layout = QVBoxLayout(units_group)

        # Scrollable area for units
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        units_widget = QWidget()
        units_container_layout = QVBoxLayout(units_widget)

        # Group units by opponent
        units_by_opponent: Dict[str, List[Dict[str, Any]]] = {}
        for target in self.targets:
            opponent_name = target["opponent_name"]
            if opponent_name not in units_by_opponent:
                units_by_opponent[opponent_name] = []
            units_by_opponent[opponent_name].append(target)

        # Create save roll widgets for each unit
        for opponent_name, opponent_targets in units_by_opponent.items():
            opponent_label = QLabel(f"<b>{opponent_name}'s Units:</b>")
            opponent_label.setStyleSheet("font-size: 16px; margin: 10px 0 5px 0;")
            units_container_layout.addWidget(opponent_label)

            for target in opponent_targets:
                unit_data = target["unit_data"]
                save_widget = MutateSaveRollWidget(unit_data, opponent_name)
                self.save_widgets.append(save_widget)
                units_container_layout.addWidget(save_widget)

        scroll_area.setWidget(units_widget)
        units_layout.addWidget(scroll_area)
        main_layout.addWidget(units_group)

        # Results summary
        self.results_label = QLabel("Roll saves for all targeted units")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.setStyleSheet("font-weight: bold; margin: 10px; padding: 10px; background-color: #f0f0f0;")
        main_layout.addWidget(self.results_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.evaluate_all_button = QPushButton("📊 Evaluate All")
        self.evaluate_all_button.clicked.connect(self._evaluate_all)
        button_layout.addWidget(self.evaluate_all_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.resolve_button = QPushButton("✅ Resolve Mutate")
        self.resolve_button.clicked.connect(self._resolve_mutate)
        self.resolve_button.setEnabled(False)
        button_layout.addWidget(self.resolve_button)

        main_layout.addLayout(button_layout)

    def _evaluate_all(self):
        """Evaluate all save rolls and update summary."""
        # Check if all units have been evaluated
        all_evaluated = all(widget.is_evaluated() for widget in self.save_widgets)
        
        if not all_evaluated:
            self.results_label.setText("❌ Not all units have been evaluated yet")
            self.results_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 10px; background-color: #fff3e0; color: #ef6c00;"
            )
            return

        # Calculate results
        self.killed_units = []
        self.saved_units = []
        self.total_health_killed = 0

        for i, widget in enumerate(self.save_widgets):
            target = self.targets[i]
            unit_data = target["unit_data"]
            opponent_name = target["opponent_name"]
            
            if widget.get_save_result():
                # Unit saved
                self.saved_units.append({
                    "unit_data": unit_data,
                    "opponent_name": opponent_name,
                })
            else:
                # Unit killed
                unit_health = unit_data.get("health", 1)
                self.killed_units.append({
                    "unit_data": unit_data,
                    "opponent_name": opponent_name,
                    "health": unit_health,
                })
                self.total_health_killed += unit_health

        # Update results display
        killed_count = len(self.killed_units)
        saved_count = len(self.saved_units)
        
        results_text = (
            f"Results: {killed_count} killed ({self.total_health_killed} health-worth), "
            f"{saved_count} saved"
        )
        
        if killed_count > 0:
            results_text += f"\n{self.swamp_stalker_player} can recruit/promote {self.total_health_killed} health-worth of Swamp Stalkers"
        
        self.results_label.setText(results_text)
        self.results_label.setStyleSheet(
            "font-weight: bold; margin: 10px; padding: 10px; background-color: #e8f5e8; color: #2e7d32;"
        )

        # Enable resolve button
        self.resolve_button.setEnabled(True)

    def _resolve_mutate(self):
        """Resolve the Mutate ability and emit results."""
        # Make sure we have evaluated results
        if not self.killed_units and not self.saved_units:
            self._evaluate_all()
            if not self.killed_units and not self.saved_units:
                return

        # Create resolution results
        resolution_results = {
            "success": True,
            "ability_type": "mutate",
            "swamp_stalker_player": self.swamp_stalker_player,
            "targets": self.targets,
            "recruiting_army": self.recruiting_army,
            "killed_units": self.killed_units,
            "saved_units": self.saved_units,
            "total_health_killed": self.total_health_killed,
            "units_killed_count": len(self.killed_units),
            "units_saved_count": len(self.saved_units),
            "original_mutate_data": self.mutate_data,
            "timestamp": "now",
        }

        self.mutate_resolved.emit(resolution_results)
        self.accept()