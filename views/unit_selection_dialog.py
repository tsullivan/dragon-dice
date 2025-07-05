# views/unit_selection_dialog.py
from typing import List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from components.die_face_display_widget import DieFaceDisplayWidget
from models.unit_model import UnitModel
from models.unit_roster_model import UnitRosterModel


class UnitSelectionDialog(QDialog):
    """
    A dialog for selecting units for an army.
    """

    units_selected_signal = Signal(list)

    def __init__(
        self,
        army_name: str,
        unit_roster: UnitRosterModel,
        current_units: Optional[List[UnitModel]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.army_name = army_name
        self.unit_roster = unit_roster
        self.selected_units: List[UnitModel] = list(current_units) if current_units else []

        # Use army display name without icon (locations shouldn't have icons)
        from models.army_model import get_army_display_name

        army_display_name = get_army_display_name(self.army_name)
        self.setWindowTitle(f"Select Units for {army_display_name}")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)
        main_area_layout = QHBoxLayout()

        # Available Units (Tabs with Tables)
        self.available_units_tabs = QTabWidget()
        self.available_units_tabs.setMaximumWidth(500)  # Prevent excessive horizontal stretching
        self._populate_available_units_tabs()
        # Give more space to tabs
        main_area_layout.addWidget(self.available_units_tabs, 2)

        # Right side layout with selected units and die face display
        right_side_layout = QVBoxLayout()

        # Selected units section
        selected_units_group = QVBoxLayout()
        selected_units_group.addWidget(QLabel("Units in Army:"))
        self.selected_units_table = QTableWidget()
        self.selected_units_table.setMaximumWidth(350)  # Prevent excessive horizontal stretching
        self.selected_units_table.setColumnCount(3)
        self.selected_units_table.setHorizontalHeaderLabels(["Unit Name", "Class Type", "Health Points"])
        self.selected_units_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.selected_units_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.selected_units_table.doubleClicked.connect(self._remove_selected_unit_from_table)
        self.selected_units_table.selectionModel().selectionChanged.connect(self._on_selected_unit_changed)
        selected_units_group.addWidget(self.selected_units_table)
        right_side_layout.addLayout(selected_units_group)

        # Die face display section
        self.die_face_widget = DieFaceDisplayWidget()
        right_side_layout.addWidget(self.die_face_widget)

        main_area_layout.addLayout(right_side_layout, 1)

        layout.addLayout(main_area_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._populate_selected_units_table()

    def _get_species_display_name(self, species_name: str) -> str:
        """Get species display name with element color icons."""
        try:
            from models.species_model import ALL_SPECIES

            # Try direct lookup first
            species_key = species_name.upper().replace(" ", "_")
            species = ALL_SPECIES.get(species_key)

            # If not found, try matching by display name
            if not species:
                for species_obj in ALL_SPECIES.values():
                    if (
                        species_obj.name.lower() == species_name.lower()
                        or species_obj.display_name.lower() == species_name.lower()
                    ):
                        species = species_obj
                        break

            if species:
                element_icons = "".join(species.get_element_icons())
                return f"{element_icons} {species_name}"
        except:
            pass

        # Fallback to original species name
        return species_name

    def _sort_units_for_display(self, units_list):
        """
        Sort units by health points (ascending), then class type (ascending), then unit name (ascending).

        Args:
            units_list: List of unit dictionaries to sort

        Returns:
            List of sorted unit dictionaries
        """
        return sorted(
            units_list,
            key=lambda unit: (
                unit.get("max_health", 0),  # Health points ascending
                unit.get("unit_class_type", "N/A"),  # Class type ascending
                unit.get("display_name", ""),  # Unit name ascending
            ),
        )

    def _populate_available_units_tabs(self):
        units_by_species = self.unit_roster.get_available_unit_types_by_species()
        for species, units_in_species in sorted(units_by_species.items()):
            tab_content_widget = QWidget()
            tab_layout = QVBoxLayout(tab_content_widget)
            tab_layout.setContentsMargins(5, 5, 5, 5)

            table = QTableWidget()
            table.setColumnCount(3)  # Name, Class Type, Health Points
            table.setHorizontalHeaderLabels(["Unit Name", "Class Type", "Health Points"])
            table.setRowCount(len(units_in_species))
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.verticalHeader().setVisible(False)

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
            table.selectionModel().selectionChanged.connect(
                lambda selected, deselected, t=table: self._on_available_unit_selected(t)
            )
            tab_layout.addWidget(table)

            # Get species element colors and create tab name with icons
            tab_name = self._get_species_display_name(species)
            self.available_units_tabs.addTab(tab_content_widget, tab_name)

    def _populate_selected_units_table(self):
        self.selected_units_table.setRowCount(len(self.selected_units))
        for row, unit in enumerate(self.selected_units):
            # Unit Name
            name_item = QTableWidgetItem(unit.name)
            name_item.setData(Qt.ItemDataRole.UserRole, unit.unit_id)
            self.selected_units_table.setItem(row, 0, name_item)

            # Get unit definition data from the unit roster
            unit_def = self.unit_roster.get_unit_definition(unit.unit_type)

            # Class Type
            class_type = unit_def.get("unit_class_type", "Unknown") if unit_def else "Unknown"
            class_item = QTableWidgetItem(class_type)
            self.selected_units_table.setItem(row, 1, class_item)

            # Health Points
            health = unit_def.get("max_health", unit.max_health) if unit_def else unit.max_health
            health_item = QTableWidgetItem(str(health))
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
        if not unit_type_info:
            return

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

    def _on_available_unit_selected(self, table: QTableWidget):
        """Handle selection of a unit in the available units table."""
        current_row = table.currentRow()
        if current_row >= 0:
            name_item = table.item(current_row, 0)
            if name_item:
                unit_type_info = name_item.data(Qt.ItemDataRole.UserRole)
                if unit_type_info:
                    # Get die face data from unit definition
                    die_faces = unit_type_info.get("die_faces", [])
                    unit_type = unit_type_info.get("unit_class_type", "")
                    is_monster = unit_type == "Monster"
                    self.die_face_widget.set_die_faces(die_faces, is_monster)
                    return

        # Clear die face display if no valid selection
        self.die_face_widget.clear()

    def _on_selected_unit_changed(self):
        """Handle selection change in the selected units table."""
        current_row = self.selected_units_table.currentRow()
        if current_row >= 0 and current_row < len(self.selected_units):
            selected_unit = self.selected_units[current_row]
            # Get unit definition from unit roster
            unit_def = self.unit_roster.get_unit_definition(selected_unit.unit_type)
            if unit_def:
                die_faces = unit_def.get("die_faces", [])
                unit_type = unit_def.get("unit_class_type", "")
                is_monster = unit_type == "Monster"
                self.die_face_widget.set_die_faces(die_faces, is_monster)
                return

        # Clear die face display if no valid selection
        self.die_face_widget.clear()

    def accept(self):
        self.units_selected_signal.emit(self.get_selected_units())
        super().accept()
