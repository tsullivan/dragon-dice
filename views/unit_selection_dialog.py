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
    units_selected_signal = Signal(list)

    def __init__(self, army_name: str, unit_roster: UnitRosterModel,
                 current_units: Optional[List[UnitModel]] = None, parent=None):
        super().__init__(parent)
        self.army_name = army_name
        self.unit_roster = unit_roster
        self.selected_units: List[UnitModel] = list(current_units) if current_units else []

        self.setWindowTitle(f"Select Units for {self.army_name}")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)
        main_area_layout = QHBoxLayout()

        # Available Units (Tabs with Tables)
        self.available_units_tabs = QTabWidget()
        self._populate_available_units_tabs()
        main_area_layout.addWidget(self.available_units_tabs, 2) # Give more space to tabs

        selected_units_group = QVBoxLayout()
        selected_units_group.addWidget(QLabel("Units in Army:"))
        self.selected_units_table = QTableWidget()
        self.selected_units_table.setColumnCount(3)
        self.selected_units_table.setHorizontalHeaderLabels(["Unit Name", "Class Type", "Health Points"])
        self.selected_units_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.selected_units_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.selected_units_table.doubleClicked.connect(self._remove_selected_unit_from_table)
        # Auto-resize columns to content
        header = self.selected_units_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        selected_units_group.addWidget(self.selected_units_table)
        main_area_layout.addLayout(selected_units_group, 1)

        layout.addLayout(main_area_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._populate_selected_units_table()

    def _sort_units_for_display(self, units_list):
        """
        Sort units by health points (ascending), then class type (ascending), then unit name (ascending).
        
        Args:
            units_list: List of unit dictionaries to sort
            
        Returns:
            List of sorted unit dictionaries
        """
        return sorted(units_list, key=lambda unit: (
            unit.get("max_health", 0),  # Health points ascending
            unit.get("unit_class_type", "N/A"),  # Class type ascending
            unit.get("display_name", "")  # Unit name ascending
        ))

    def _populate_available_units_tabs(self):
        units_by_species = self.unit_roster.get_available_unit_types_by_species()
        for species, units_in_species in sorted(units_by_species.items()):
            tab_content_widget = QWidget()
            tab_layout = QVBoxLayout(tab_content_widget)
            tab_layout.setContentsMargins(5,5,5,5)

            table = QTableWidget()
            table.setColumnCount(3) # Name, Class Type, Health Points
            table.setHorizontalHeaderLabels(["Unit Name", "Class Type", "Health Points"])
            table.setRowCount(len(units_in_species))
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Class Type
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Health Points

            # Sort units using the dedicated sorting method
            sorted_units = self._sort_units_for_display(units_in_species)
            
            for row_idx, unit_type_info in enumerate(sorted_units):
                name_item = QTableWidgetItem(unit_type_info["display_name"])
                class_type_item = QTableWidgetItem(unit_type_info.get("unit_class_type", "N/A"))
                health_item = QTableWidgetItem(str(unit_type_info.get("max_health", 0)))
                name_item.setData(Qt.ItemDataRole.UserRole, unit_type_info)

                table.setItem(row_idx, 0, name_item)
                table.setItem(row_idx, 1, class_type_item)
                table.setItem(row_idx, 2, health_item)
            table.cellClicked.connect(self._table_cell_clicked)
            tab_layout.addWidget(table)
            self.available_units_tabs.addTab(tab_content_widget, species)

    def _populate_selected_units_table(self):
        self.selected_units_table.setRowCount(len(self.selected_units))
        for row, unit in enumerate(self.selected_units):
            # Unit Name
            name_item = QTableWidgetItem(unit.name)
            name_item.setData(Qt.ItemDataRole.UserRole, unit.unit_id)
            self.selected_units_table.setItem(row, 0, name_item)
            
            # Class Type
            class_item = QTableWidgetItem(unit.unit_class_type)
            self.selected_units_table.setItem(row, 1, class_item)
            
            # Health Points
            health_item = QTableWidgetItem(str(unit.max_health))
            self.selected_units_table.setItem(row, 2, health_item)

    @Slot(int, int)
    def _table_cell_clicked(self, row: int, column: int):
        table_widget = self.sender()
        if not isinstance(table_widget, QTableWidget):
            return

        name_item = table_widget.item(row, 0)
        if not name_item:
            return
        
        unit_type_info = name_item.data(Qt.ItemDataRole.UserRole)
        if not unit_type_info: return

        unit_type_id = unit_type_info["id"]
        unit_display_name = unit_type_info["display_name"]
        instance_count = sum(1 for u in self.selected_units if u.unit_type == unit_type_id)
        instance_id = f"{self.army_name.lower().replace(' ', '_')}_{unit_type_id}_{instance_count + 1}"
        new_unit = self.unit_roster.create_unit_instance(unit_type_id, instance_id)
        if new_unit:
            self.selected_units.append(new_unit)
            print(f"Selected (added instance of): {new_unit.name}")
        self._populate_selected_units_table()

    @Slot()
    def _remove_selected_unit_from_table(self):
        current_row = self.selected_units_table.currentRow()
        if current_row >= 0 and current_row < len(self.selected_units):
            unit_to_remove = self.selected_units[current_row]
            self.selected_units = [u for u in self.selected_units if u.unit_id != unit_to_remove.unit_id]
            self._populate_selected_units_table()

    def get_selected_units(self) -> List[UnitModel]:
        return self.selected_units

    def accept(self):
        self.units_selected_signal.emit(self.get_selected_units())
        super().accept()