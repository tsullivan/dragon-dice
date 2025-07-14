"""
Damage Allocation Dialog for Dragon Dice - handles interactive damage distribution.

This dialog provides:
1. Interactive damage allocation to units
2. Unit selection for DUA placement
3. Visual damage tracking and validation
4. Health reduction and unit removal logic
5. Special damage rules handling
"""

from typing import Any, Dict, List, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from utils import strict_get


class UnitDamageWidget(QWidget):
    """Widget for managing damage allocation to a single unit."""

    damage_changed = Signal(str, int)  # unit_name, damage_amount

    def __init__(self, unit_name: str, unit_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.unit_name = unit_name
        self.unit_data = unit_data
        self.max_health = strict_get(unit_data, "health")
        self.current_health = self.max_health
        self.damage_taken = 0
        self.is_killed = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the unit damage allocation UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Unit info
        species = strict_get(self.unit_data, "species")
        elements = strict_get(self.unit_data, "elements")
        element_text = f" ({'/'.join(elements)})" if elements else ""

        self.unit_label = QLabel(f"{self.unit_name} - {species}{element_text}")
        self.unit_label.setMinimumWidth(200)
        self.unit_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.unit_label)

        # Health display
        self.health_label = QLabel(f"Health: {self.current_health}/{self.max_health}")
        self.health_label.setMinimumWidth(100)
        layout.addWidget(self.health_label)

        # Damage input
        damage_layout = QHBoxLayout()
        damage_layout.addWidget(QLabel("Damage:"))

        self.damage_spinbox = QSpinBox()
        self.damage_spinbox.setMinimum(0)
        self.damage_spinbox.setMaximum(self.max_health)
        self.damage_spinbox.setValue(0)
        self.damage_spinbox.valueChanged.connect(self._on_damage_changed)
        damage_layout.addWidget(self.damage_spinbox)

        layout.addLayout(damage_layout)

        # Quick damage buttons
        quick_layout = QHBoxLayout()
        self.kill_button = QPushButton("Kill")
        self.kill_button.setMaximumWidth(50)
        self.kill_button.clicked.connect(self._kill_unit)
        quick_layout.addWidget(self.kill_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setMaximumWidth(50)
        self.clear_button.clicked.connect(self._clear_damage)
        quick_layout.addWidget(self.clear_button)

        layout.addLayout(quick_layout)

        # Status indicator
        self.status_label = QLabel("Alive")
        self.status_label.setMinimumWidth(60)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    def _on_damage_changed(self, damage: int):
        """Handle damage amount change."""
        self.damage_taken = damage
        self.current_health = max(0, self.max_health - damage)
        self.is_killed = self.current_health == 0

        # Update UI
        self.health_label.setText(f"Health: {self.current_health}/{self.max_health}")

        if self.is_killed:
            self.status_label.setText("Killed")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.unit_label.setStyleSheet("font-weight: bold; color: #666;")
        else:
            self.status_label.setText("Alive")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.unit_label.setStyleSheet("font-weight: bold; color: black;")

        # Emit signal
        self.damage_changed.emit(self.unit_name, damage)

    def _kill_unit(self):
        """Set damage to kill the unit."""
        self.damage_spinbox.setValue(self.max_health)

    def _clear_damage(self):
        """Clear all damage from the unit."""
        self.damage_spinbox.setValue(0)

    def get_damage_taken(self) -> int:
        """Get the amount of damage assigned to this unit."""
        return self.damage_taken

    def is_unit_killed(self) -> bool:
        """Check if the unit is killed by damage."""
        return self.is_killed

    def get_remaining_health(self) -> int:
        """Get the unit's remaining health after damage."""
        return self.current_health  # type: ignore[no-any-return]

    def set_damage(self, damage: int):
        """Set damage amount programmatically."""
        self.damage_spinbox.setValue(min(damage, self.max_health))


class DamageAllocationDialog(QDialog):
    """
    Dialog for allocating damage to units in an army.

    This dialog allows players to:
    1. Distribute damage among units in their army
    2. Choose which units to kill
    3. Validate that all damage is properly allocated
    4. Handle special damage rules (no saves, direct damage, etc.)
    """

    damage_allocated = Signal(dict)  # Emits damage allocation results
    damage_cancelled = Signal()

    def __init__(
        self,
        army_name: str,
        army_data: Dict[str, Any],
        damage_amount: int,
        damage_type: str = "normal",
        damage_source: str = "combat",
        allow_saves: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.army_name = army_name
        self.army_data = army_data
        self.damage_amount = damage_amount
        self.damage_type = damage_type
        self.damage_source = damage_source
        self.allow_saves = allow_saves

        # Damage allocation state
        self.unit_widgets: List[UnitDamageWidget] = []
        self.total_damage_allocated = 0
        self.remaining_damage = damage_amount

        self.setWindowTitle(f"💥 Damage Allocation - {army_name}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._update_damage_display()

    def _setup_ui(self):
        """Setup the damage allocation UI."""
        main_layout = QVBoxLayout(self)

        # Header info
        header_layout = QVBoxLayout()

        # Damage info
        damage_info = QLabel(
            f"<b>Allocate {self.damage_amount} damage to {self.army_name}</b><br>"
            f"Damage Type: {self.damage_type.title()}<br>"
            f"Source: {self.damage_source.title()}"
        )
        damage_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        damage_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fff2e6; border: 1px solid #ffab00;"
        )
        header_layout.addWidget(damage_info)

        # Save information
        if not self.allow_saves:
            no_saves_info = QLabel("⚠️ <b>No Save Possible:</b> Units cannot make save rolls against this damage")
            no_saves_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_saves_info.setStyleSheet(
                "color: #d32f2f; font-weight: bold; margin: 5px; padding: 5px; background-color: #ffebee;"
            )
            header_layout.addWidget(no_saves_info)

        main_layout.addLayout(header_layout)

        # Damage tracking
        self.damage_track_label = QLabel()
        self.damage_track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.damage_track_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px; padding: 10px; background-color: #e3f2fd; border: 1px solid #2196f3;"
        )
        main_layout.addWidget(self.damage_track_label)

        # Units list
        units_group = QGroupBox("Units in Army")
        units_layout = QVBoxLayout(units_group)

        # Scrollable area for units
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        units_widget = QWidget()
        self.units_layout = QVBoxLayout(units_widget)

        # Create unit widgets
        army_units = strict_get(self.army_data, "units")
        for unit in army_units:
            unit_name = strict_get(unit, "name")
            unit_widget = UnitDamageWidget(unit_name, unit)
            unit_widget.damage_changed.connect(self._on_unit_damage_changed)
            self.unit_widgets.append(unit_widget)
            self.units_layout.addWidget(unit_widget)

        scroll_area.setWidget(units_widget)
        units_layout.addWidget(scroll_area)
        main_layout.addWidget(units_group)

        # Quick allocation buttons
        quick_layout = QHBoxLayout()

        self.distribute_evenly_button = QPushButton("Distribute Evenly")
        self.distribute_evenly_button.clicked.connect(self._distribute_evenly)
        quick_layout.addWidget(self.distribute_evenly_button)

        self.kill_weakest_button = QPushButton("Kill Weakest Units")
        self.kill_weakest_button.clicked.connect(self._kill_weakest_units)
        quick_layout.addWidget(self.kill_weakest_button)

        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self._clear_all_damage)
        quick_layout.addWidget(self.clear_all_button)

        main_layout.addLayout(quick_layout)

        # Validation info
        self.validation_label = QLabel()
        self.validation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.validation_label.setStyleSheet("font-weight: bold; margin: 5px; padding: 5px;")
        main_layout.addWidget(self.validation_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.apply_button = QPushButton("✅ Apply Damage")
        self.apply_button.clicked.connect(self._on_apply_damage)
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)

    def _on_unit_damage_changed(self, unit_name: str, damage: int):
        """Handle damage change for a unit."""
        # Recalculate total damage
        self.total_damage_allocated = sum(widget.get_damage_taken() for widget in self.unit_widgets)
        self.remaining_damage = self.damage_amount - self.total_damage_allocated

        self._update_damage_display()
        self._validate_damage_allocation()

    def _update_damage_display(self):
        """Update the damage tracking display."""
        self.damage_track_label.setText(
            f"Damage Allocated: {self.total_damage_allocated}/{self.damage_amount} (Remaining: {self.remaining_damage})"
        )

        # Color coding
        if self.remaining_damage == 0:
            self.damage_track_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; margin: 10px; padding: 10px; background-color: #e8f5e8; border: 1px solid #4caf50; color: #2e7d32;"
            )
        elif self.remaining_damage > 0:
            self.damage_track_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; margin: 10px; padding: 10px; background-color: #fff3e0; border: 1px solid #ff9800; color: #ef6c00;"
            )
        else:  # over-allocated
            self.damage_track_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; margin: 10px; padding: 10px; background-color: #ffebee; border: 1px solid #f44336; color: #c62828;"
            )

    def _validate_damage_allocation(self):
        """Validate the current damage allocation."""
        if self.remaining_damage == 0:
            self.validation_label.setText("✅ All damage properly allocated")
            self.validation_label.setStyleSheet(
                "color: #4caf50; font-weight: bold; margin: 5px; padding: 5px; background-color: #e8f5e8;"
            )
            self.apply_button.setEnabled(True)
        elif self.remaining_damage > 0:
            self.validation_label.setText(f"⚠️ {self.remaining_damage} damage not allocated")
            self.validation_label.setStyleSheet(
                "color: #ff9800; font-weight: bold; margin: 5px; padding: 5px; background-color: #fff3e0;"
            )
            self.apply_button.setEnabled(False)
        else:
            over_damage = abs(self.remaining_damage)
            self.validation_label.setText(f"❌ {over_damage} too much damage allocated")
            self.validation_label.setStyleSheet(
                "color: #f44336; font-weight: bold; margin: 5px; padding: 5px; background-color: #ffebee;"
            )
            self.apply_button.setEnabled(False)

    def _distribute_evenly(self):
        """Distribute damage evenly among all units."""
        if not self.unit_widgets:
            return

        # Clear current damage
        for widget in self.unit_widgets:
            widget.set_damage(0)

        # Calculate even distribution
        units_count = len(self.unit_widgets)
        base_damage = self.damage_amount // units_count
        extra_damage = self.damage_amount % units_count

        for i, widget in enumerate(self.unit_widgets):
            damage = base_damage
            if i < extra_damage:
                damage += 1

            # Don't exceed unit's max health
            damage = min(damage, widget.max_health)
            widget.set_damage(damage)

    def _kill_weakest_units(self):
        """Kill the weakest units first to absorb damage."""
        # Clear current damage
        for widget in self.unit_widgets:
            widget.set_damage(0)

        # Sort units by health (weakest first)
        sorted_widgets = sorted(self.unit_widgets, key=lambda w: w.max_health)

        remaining_damage = self.damage_amount
        for widget in sorted_widgets:
            if remaining_damage <= 0:
                break

            damage_to_apply = min(remaining_damage, widget.max_health)
            widget.set_damage(damage_to_apply)
            remaining_damage -= damage_to_apply

    def _clear_all_damage(self):
        """Clear all damage from all units."""
        for widget in self.unit_widgets:
            widget.set_damage(0)

    def _on_apply_damage(self):
        """Apply the damage allocation."""
        if self.remaining_damage != 0:
            return  # Should not happen if validation is working

        # Collect damage allocation results
        damage_allocation = []
        killed_units = []
        surviving_units = []

        for widget in self.unit_widgets:
            unit_result = {
                "unit_name": widget.unit_name,
                "unit_data": widget.unit_data,
                "damage_taken": widget.get_damage_taken(),
                "remaining_health": widget.get_remaining_health(),
                "is_killed": widget.is_unit_killed(),
            }

            damage_allocation.append(unit_result)

            if widget.is_unit_killed():
                killed_units.append(unit_result)
            else:
                surviving_units.append(unit_result)

        # Create result dictionary
        result = {
            "success": True,
            "army_name": self.army_name,
            "army_data": self.army_data,
            "damage_amount": self.damage_amount,
            "damage_type": self.damage_type,
            "damage_source": self.damage_source,
            "allow_saves": self.allow_saves,
            "damage_allocation": damage_allocation,
            "killed_units": killed_units,
            "surviving_units": surviving_units,
            "total_units_killed": len(killed_units),
            "total_damage_dealt": self.damage_amount,
            "timestamp": "now",
        }

        self.damage_allocated.emit(result)
        self.accept()

    def _on_cancel(self):
        """Cancel damage allocation."""
        self.damage_cancelled.emit()
        self.reject()


class MultiArmyDamageDialog(QDialog):
    """Dialog for allocating damage to multiple armies (e.g., area effect spells)."""

    all_damage_allocated = Signal(list)  # Emits list of damage allocation results
    damage_cancelled = Signal()

    def __init__(
        self,
        affected_armies: List[Tuple[str, Dict[str, Any]]],  # (army_name, army_data)
        damage_amount: int,
        damage_type: str = "normal",
        damage_source: str = "spell",
        allow_saves: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.affected_armies = affected_armies
        self.damage_amount = damage_amount
        self.damage_type = damage_type
        self.damage_source = damage_source
        self.allow_saves = allow_saves

        # Track individual damage dialogs
        self.damage_results: List[Dict[str, Any]] = []
        self.current_army_index = 0

        self.setWindowTitle("💥 Multi-Army Damage Allocation")
        self.setModal(True)

        self._start_damage_allocation()

    def _start_damage_allocation(self):
        """Start damage allocation for the first army."""
        if self.current_army_index >= len(self.affected_armies):
            # All armies processed
            self.all_damage_allocated.emit(self.damage_results)
            self.accept()
            return

        army_name, army_data = self.affected_armies[self.current_army_index]

        # Create damage dialog for current army
        dialog = DamageAllocationDialog(
            army_name=army_name,
            army_data=army_data,
            damage_amount=self.damage_amount,
            damage_type=self.damage_type,
            damage_source=self.damage_source,
            allow_saves=self.allow_saves,
            parent=self,
        )

        dialog.damage_allocated.connect(self._on_army_damage_allocated)
        dialog.damage_cancelled.connect(self._on_damage_cancelled)

        dialog.exec()

    def _on_army_damage_allocated(self, result: Dict[str, Any]):
        """Handle damage allocation for one army."""
        self.damage_results.append(result)
        self.current_army_index += 1

        # Process next army
        self._start_damage_allocation()

    def _on_damage_cancelled(self):
        """Handle cancellation of damage allocation."""
        self.damage_cancelled.emit()
        self.reject()
