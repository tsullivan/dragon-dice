# components/army_setup_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton) # Removed QComboBox
from PySide6.QtCore import Qt, Signal, Slot
from typing import List, Optional

from models.unit_roster_model import UnitRosterModel # For type hinting
from models.unit_model import UnitModel # For type hinting
from views.unit_selection_dialog import UnitSelectionDialog
import constants # Import constants

class ArmySetupWidget(QWidget):
    """
    A widget for setting up a single army (points and units). The name is implicit by its type.
    """
    name_changed = Signal(str) # This signal is no longer actively used by this widget for its own name
    # points_changed = Signal(str, int) # No longer needed as points are derived from units
    # Signal to emit the list of UnitModel instances (as dicts) for this army
    units_updated_signal = Signal(str, list) # Emit army_type_name and list of units (as dicts)

    def __init__(self, army_type_name: str, unit_roster: Optional[UnitRosterModel] = None, parent=None):
        super().__init__(parent)
        self.army_type_name = army_type_name
        self.unit_roster = unit_roster
        self.current_units: List[UnitModel] = [] # Store UnitModel instances for this army

        # Layout: Button on the left, summary on the right
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5) # Minimal spacing

        self.manage_units_button = QPushButton(constants.MANAGE_UNITS_BUTTON_TEXT)
        self.manage_units_button.setMaximumWidth(180)  # Limit button width
        if self.unit_roster:
            self.manage_units_button.clicked.connect(self._open_unit_selection_dialog)
        else:
            self.manage_units_button.setEnabled(False)
            self.manage_units_button.setToolTip("Unit roster not available.")
        layout.addWidget(self.manage_units_button)
        self.units_summary_label = QLabel(constants.DEFAULT_ARMY_UNITS_SUMMARY)
        layout.addWidget(self.units_summary_label, 1, Qt.AlignmentFlag.AlignCenter) # Add stretch to summary

        self._update_units_summary()

    def _emit_name_changed(self):
        # This method is kept for consistency but the name input is removed.
        # If a name were still part of this widget, it would emit here.
        # self.name_changed.emit(self.name_input.text())
        pass

    @Slot(int) # Slot for the internal QComboBox's currentIndexChanged signal
    def _emit_points_changed_slot(self, index: int): # No longer used
        pass

    def get_name(self) -> str:
        # Army name is no longer managed by this widget directly.
        # It's implicitly the army_type_name.
        return self.army_type_name

    def set_name(self, name: str):
        # No QLineEdit for name in this widget anymore.
        pass

    def set_points(self, points: int):
        # Points are now derived from units, so this method is not for setting a target.
        # It could be used to clear units if points were externally set to 0, but
        # unit management is primarily through the dialog.
        pass

    def _open_unit_selection_dialog(self):
        if not self.unit_roster:
            return
        dialog = UnitSelectionDialog(self.army_type_name, self.unit_roster, self.current_units, self)
        dialog.units_selected_signal.connect(self._handle_units_selected_from_dialog)
        dialog.exec()

    @Slot(list)
    def _handle_units_selected_from_dialog(self, selected_units: List[UnitModel]):
        """
        Called when the UnitSelectionDialog emits its signal.
        """
        self.current_units = selected_units
        self._update_units_summary()
        self.units_updated_signal.emit(self.army_type_name.lower(), self.get_current_units_as_dicts())

    def get_current_units_as_dicts(self) -> List[dict]:
        return [unit.to_dict() for unit in self.current_units]

    def load_units_from_dicts(self, unit_dicts: List[dict]):
        self.current_units = [UnitModel.from_dict(u_data) for u_data in unit_dicts]

    def _update_units_summary(self):
        unit_count = len(self.current_units)
        total_points = sum(unit.max_health for unit in self.current_units)
        self.units_summary_label.setText(f"Units: {unit_count} ({total_points} pts)")
