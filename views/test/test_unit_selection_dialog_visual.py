import pytest

import utils.constants as constants
from models.unit_model import UnitModel
from models.unit_roster_model import UnitRosterModel
from test.utils.visual_test_helpers import capture_widget_screenshot
from views.unit_selection_dialog import UnitSelectionDialog


@pytest.fixture
def unit_roster():
    """Provides a UnitRosterModel instance."""
    return UnitRosterModel()


def test_unit_selection_dialog_empty(qtbot, unit_roster):
    """Captures a screenshot of the UnitSelectionDialog in its initial empty state."""
    army_name = "Test Home Army"
    # allocated_points = 10 # This value is no longer used by the dialog itself
    dialog = UnitSelectionDialog(army_name, unit_roster, current_units=None)
    capture_widget_screenshot(qtbot, dialog, "UnitSelectionDialog_Empty")
    # Test passes if no exceptions and screenshot is saved.
    # Dialog is modal, so we don't need to explicitly close it for screenshot.


def test_unit_selection_dialog_with_preselected_units(qtbot, unit_roster):
    """Captures a screenshot of the UnitSelectionDialog with some units already selected."""
    army_name = "Test Campaign Army"

    # Create some units to pre-select
    unit1 = unit_roster.create_unit_instance("goblin_spearman", "camp_gob_1")
    unit2 = unit_roster.create_unit_instance("orc_archer", "camp_orc_1")
    current_units = []
    if unit1:
        current_units.append(unit1)
    if unit2:
        current_units.append(unit2)

    dialog = UnitSelectionDialog(army_name, unit_roster, current_units=current_units)
    capture_widget_screenshot(qtbot, dialog, "UnitSelectionDialog_WithUnits")
