# views/unit_selection_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QListWidget, QListWidgetItem, QDialogButtonBox, QTabWidget, QTableWidget,
                               QTableWidgetItem, QAbstractItemView, QHeaderView, QWidget)
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
        self.setMinimumSize(700, 500) # Adjusted size for tabs

        layout = QVBoxLayout(self)

        # Points display
        self.points_label = QLabel()
        self._update_points_label()
        layout.addWidget(self.points_label)
        # Main area: Available units and selected units
        main_area_layout = QHBoxLayout()

        # Available Units (Tabs with Tables)
        self.available_units_tabs = QTabWidget()
        self._populate_available_units_tabs()
        main_area_layout.addWidget(self.available_units_tabs, 2) # Give more space to tabs

        # Selected Units List
        selected_units_group = QVBoxLayout()
        selected_units_group.addWidget(QLabel("Units in Army:"))
        self.selected_units_list = QListWidget()
        self.selected_units_list.itemDoubleClicked.connect(self._remove_selected_unit)
        selected_units_group.addWidget(self.selected_units_list)
        main_area_layout.addLayout(selected_units_group, 1) # Selected units take less space

        layout.addLayout(main_area_layout)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._populate_selected_units_list()

    def _populate_available_units_tabs(self):
        units_by_species = self.unit_roster.get_available_unit_types_by_species()
        for species, units_in_species in sorted(units_by_species.items()):
            tab_content_widget = QWidget() # Create a container widget for the tab
            tab_layout = QVBoxLayout(tab_content_widget) # Layout for the container
            tab_layout.setContentsMargins(5,5,5,5)

            table = QTableWidget()
            table.setColumnCount(2) # Name, Cost
            table.setHorizontalHeaderLabels(["Unit Name", "Cost (pts)"])
            table.setRowCount(len(units_in_species))
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Select whole row
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Read-only
            table.verticalHeader().setVisible(False) # Hide row numbers
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name column stretches
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Cost column fits content

            for row_idx, unit_type_info in enumerate(units_in_species):
                name_item = QTableWidgetItem(unit_type_info["display_name"])
                cost_item = QTableWidgetItem(str(unit_type_info["points_cost"]))
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Store the full unit_type_info (which is the unit definition dict) for when a cell is clicked
                name_item.setData(Qt.ItemDataRole.UserRole, unit_type_info)

                table.setItem(row_idx, 0, name_item)
                table.setItem(row_idx, 1, cost_item)
            table.cellClicked.connect(self._table_cell_clicked)
            tab_layout.addWidget(table)
            self.available_units_tabs.addTab(tab_content_widget, species)

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

    @Slot(int, int)
    def _table_cell_clicked(self, row: int, column: int):
        table_widget = self.sender()
        if not isinstance(table_widget, QTableWidget):
            return

        # We stored the unit_type_info on the first column's item
        name_item = table_widget.item(row, 0)
        if not name_item:
            return
        
        unit_type_info = name_item.data(Qt.ItemDataRole.UserRole) # This is the unit definition dict
        if not unit_type_info: return

        unit_type_id = unit_type_info["id"]
        unit_cost = unit_type_info["points_cost"]
        unit_display_name = unit_type_info["display_name"]

        # Always try to add a new instance when a unit type is clicked in the table.
        # Removal of specific instances is handled by the selected_units_list.
        current_total_points = sum(u.points_cost for u in self.selected_units)
        if current_total_points + unit_cost > self.allocated_points:
            print(f"Cannot add {unit_display_name}: Exceeds army point limit.")
            # TODO: Show a message box to the user
            return
        
        # Create a unique instance ID (simple for now, might need improvement for many identical units)
        instance_count = sum(1 for u in self.selected_units if u.unit_type == unit_type_id)
        instance_id = f"{self.army_name.lower().replace(' ', '_')}_{unit_type_id}_{instance_count + 1}"
        new_unit = self.unit_roster.create_unit_instance(unit_type_id, instance_id)
        if new_unit:
            self.selected_units.append(new_unit)
            print(f"Selected (added instance of): {new_unit.name}")
        
        self._populate_selected_units_list() # Refresh the "Units in Army" list

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