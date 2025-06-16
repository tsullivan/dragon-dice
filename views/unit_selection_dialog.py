# views/unit_selection_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QListWidget, QListWidgetItem, QDialogButtonBox, QLineEdit, QSpinBox, QFormLayout)
from PySide6.QtCore import Qt, Signal, Slot
from typing import List, Dict, Any, Optional

from models.unit_roster_model import UnitRosterModel
from models.unit_model import UnitModel

class UnitSelectionDialog(QDialog):
    """
    A dialog for selecting units for an army.
    """
    units_selected_signal = Signal(list) # Emits a list of UnitModel instances

    def __init__(self, army_name: str, allocated_points: int, unit_roster: UnitRosterModel,
                 current_units: Optional[List[UnitModel]] = None, parent=None):
        super().__init__(parent)
        self.army_name = army_name
        self.allocated_points = allocated_points
        self.unit_roster = unit_roster
        self.selected_units: List[UnitModel] = list(current_units) if current_units else [] # Make a mutable copy

        self.setWindowTitle(f"Select Units for {self.army_name}")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Points display
        self.points_label = QLabel()
        self._update_points_label()
        layout.addWidget(self.points_label)

        # Main area: Available units and selected units
        main_area_layout = QHBoxLayout()

        # Available Units List
        available_units_group = QVBoxLayout()
        available_units_group.addWidget(QLabel("Available Unit Types:"))
        self.available_units_list = QListWidget()
        for unit_type_info in self.unit_roster.get_available_unit_types():
            item_text = f"{unit_type_info['name']} ({unit_type_info['cost']} pts)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, unit_type_info) # Store full info
            self.available_units_list.addItem(item)
        self.available_units_list.itemDoubleClicked.connect(self._add_selected_unit_type)
        available_units_group.addWidget(self.available_units_list)
        main_area_layout.addLayout(available_units_group, 1)

        # Selected Units List
        selected_units_group = QVBoxLayout()
        selected_units_group.addWidget(QLabel("Units in Army:"))
        self.selected_units_list = QListWidget()
        self.selected_units_list.itemDoubleClicked.connect(self._remove_selected_unit)
        selected_units_group.addWidget(self.selected_units_list)
        main_area_layout.addLayout(selected_units_group, 1)

        layout.addLayout(main_area_layout)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._populate_selected_units_list()

    def _update_points_label(self):
        current_total = sum(unit.points_cost for unit in self.selected_units)
        self.points_label.setText(f"Points Used: {current_total} / {self.allocated_points}")

    def _populate_selected_units_list(self):
        self.selected_units_list.clear()
        for unit in self.selected_units:
            item_text = f"{unit.name} ({unit.points_cost} pts) - Type: {unit.unit_type}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, unit.unit_id) # Store unit_id for removal
            self.selected_units_list.addItem(item)
        self._update_points_label()

    @Slot(QListWidgetItem)
    def _add_selected_unit_type(self, item: QListWidgetItem):
        unit_type_info = item.data(Qt.ItemDataRole.UserRole)
        if not unit_type_info: return

        current_total_points = sum(u.points_cost for u in self.selected_units)
        if current_total_points + unit_type_info["cost"] > self.allocated_points:
            # TODO: Show a message box
            print(f"Cannot add {unit_type_info['name']}: Exceeds army point limit.")
            return

        # Create a unique instance ID (simple for now)
        instance_id = f"{self.army_name.lower().replace(' ', '_')}_{unit_type_info['id']}_{len(self.selected_units) + 1}"
        new_unit = self.unit_roster.create_unit_instance(unit_type_info["id"], instance_id)
        if new_unit:
            self.selected_units.append(new_unit)
            self._populate_selected_units_list()

    @Slot(QListWidgetItem)
    def _remove_selected_unit(self, item: QListWidgetItem):
        unit_id_to_remove = item.data(Qt.ItemDataRole.UserRole)
        self.selected_units = [u for u in self.selected_units if u.unit_id != unit_id_to_remove]
        self._populate_selected_units_list()

    def get_selected_units(self) -> List[UnitModel]:
        return self.selected_units

    def accept(self):
        self.units_selected_signal.emit(self.get_selected_units())
        super().accept()