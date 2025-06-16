# components/army_setup_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from typing import List, Optional

from models.unit_roster_model import UnitRosterModel # For type hinting
from models.unit_model import UnitModel # For type hinting
from views.unit_selection_dialog import UnitSelectionDialog

class ArmySetupWidget(QWidget):
    """
    A widget for setting up a single army (name, points, and units).
    """
    name_changed = Signal(str) # This signal is no longer actively used by this widget for its own name
    points_changed = Signal(str, int) # Emit army_type_name and points
    # Signal to emit the list of UnitModel instances (as dicts) for this army
    units_updated_signal = Signal(str, list) # Emit army_type_name and list of units (as dicts)

    def __init__(self, army_type_name: str, points_options: list[int],
                 unit_roster: Optional[UnitRosterModel] = None, parent=None):
        super().__init__(parent)
        self.army_type_name = army_type_name
        self.unit_roster = unit_roster # Store the roster
        self.current_units: List[UnitModel] = [] # Store UnitModel instances for this army

        # This widget's layout will be managed by PlayerSetupView's QGridLayout.
        # It no longer needs its own main_layout or units_summary_label.
        # PlayerSetupView will create the points combo and manage units button next to this widget's label.

        # The ArmySetupWidget itself might become very minimal or even be removed if
        # PlayerSetupView handles all its constituent parts directly.
        # For now, let's assume it might still hold some logic or be a container,
        # but its UI elements are largely managed by the parent view.

        # If this widget is still intended to be a distinct visual component,
        # it would need its own layout and elements. However, based on the
        # PlayerSetupView refactor, it seems PlayerSetupView is taking over
        # the direct placement of points combo and manage units button.

        # Let's simplify this widget to primarily manage its internal state (current_units)
        # and provide methods to interact with the UnitSelectionDialog.
        # The UI elements (points combo, manage button, summary label) are now in PlayerSetupView.

    def _emit_name_changed(self):
        # This method is kept for consistency but the name input is removed.
        # If a name were still part of this widget, it would emit here.
        # self.name_changed.emit(self.name_input.text())
        pass

    def _emit_points_changed(self, points: int):
        # This method would be called if the points combo was part of this widget.
        # Now, PlayerSetupView handles the points combo directly.
        # We keep the signal definition for potential future use or if the design changes.
        self.points_changed.emit(self.army_type_name.lower(), points)


    def get_name(self) -> str:
        # Army name is no longer managed by this widget directly.
        # It's implicitly the army_type_name.
        return self.army_type_name

    def set_name(self, name: str):
        # No QLineEdit for name in this widget anymore.
        pass

    def get_points(self) -> Optional[int]:
        # Points are managed by a QComboBox in PlayerSetupView.
        # This method would need to be called by PlayerSetupView if it wants this widget
        # to report points, but PlayerSetupView has direct access to its own QComboBox.
        # For now, returning None as this widget doesn't own the points combo.
        return None

    def set_points(self, points: int):
        # Points QComboBox is in PlayerSetupView.
        pass

    # This method is now effectively called by PlayerSetupView directly
    # when its "Manage Units" button for this army type is clicked.
    # PlayerSetupView will instantiate and exec the dialog.
    # def _open_unit_selection_dialog(self):
    #     if not self.unit_roster:
    #         return
    #
    #     # allocated_points would need to be passed in or fetched from PlayerSetupView
    #     allocated_points = self.get_points() # This won't work as is
    #     if allocated_points is None:
    #         print("Error: Army points not set, cannot manage units.")
    #         return
    #
    #     dialog = UnitSelectionDialog(self.army_type_name, allocated_points, self.unit_roster, self.current_units, self)
    #     dialog.units_selected_signal.connect(self._handle_units_selected)
    #     dialog.exec()

    @Slot(list) # This slot would be connected by PlayerSetupView
    def handle_units_selected_from_dialog(self, selected_units: List[UnitModel]):
        """
        Called by PlayerSetupView after the UnitSelectionDialog for this army type closes.
        """
        self.current_units = selected_units
        # The summary label update and units_updated_signal emission
        # will be handled by PlayerSetupView's own _handle_units_selected method.
        # This widget primarily just stores the current_units list if PlayerSetupView
        # chooses to update it this way.

    def get_current_units_as_dicts(self) -> List[dict]:
        return [unit.to_dict() for unit in self.current_units]

    def load_units_from_dicts(self, unit_dicts: List[dict]):
        self.current_units = [UnitModel.from_dict(u_data) for u_data in unit_dicts]


    # The units summary label is now in PlayerSetupView.
    # def _update_units_summary(self):
    #     points_used = sum(u.points_cost for u in self.current_units)
    #     # self.units_summary_label.setText(f"Units: {len(self.current_units)} ({points_used} pts)")
