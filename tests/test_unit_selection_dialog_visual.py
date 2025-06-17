import pytest
import os
from PySide6.QtWidgets import QApplication

from views.unit_selection_dialog import UnitSelectionDialog
from models.unit_roster_model import UnitRosterModel
from models.unit_model import UnitModel
import constants

# Ensure the output directory exists, as defined in CONTRIBUTING.md
VISUAL_TESTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-visuals", "views")
if not os.path.exists(VISUAL_TESTS_OUTPUT_DIR):
    os.makedirs(VISUAL_TESTS_OUTPUT_DIR, exist_ok=True)

def capture_widget_screenshot(qtbot, widget_to_test, filename_base, sub_directory=""):
    """
    Helper function to show a widget, capture, and save a screenshot.
    """
    qtbot.addWidget(widget_to_test)
    widget_to_test.show()
    qtbot.waitExposed(widget_to_test)
    QApplication.processEvents()
    output_dir_path = os.path.join(VISUAL_TESTS_OUTPUT_DIR, sub_directory)
    if not os.path.exists(output_dir_path) and sub_directory:
        os.makedirs(output_dir_path, exist_ok=True)
    output_path = os.path.join(output_dir_path, f"{filename_base}.png")
    pixmap = widget_to_test.grab()
    pixmap.save(output_path)
    print(f"Screenshot saved: {output_path}")
    assert os.path.exists(output_path)
    return output_path

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
