import pytest
import os
from PySide6.QtWidgets import QApplication

from views.welcome_view import WelcomeView

# Ensure the output directory exists, as defined in CONTRIBUTING.md
VISUAL_TESTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-visuals", "views")
if not os.path.exists(VISUAL_TESTS_OUTPUT_DIR):
    os.makedirs(VISUAL_TESTS_OUTPUT_DIR, exist_ok=True)

# pytest-qt provides the qtbot fixture automatically
def capture_widget_screenshot(qtbot, widget_to_test, filename_base, sub_directory=""):
    """
    Helper function to show a widget, capture, and save a screenshot.
    """
    qtbot.addWidget(widget_to_test)
    widget_to_test.show()
    qtbot.waitExposed(widget_to_test)

    # Ensure all pending events are processed, allowing the widget to fully render
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

def test_welcome_view_direct_render(qtbot):
    """Captures a PNG of the WelcomeView rendered directly."""
    welcome_view = WelcomeView()
    capture_widget_screenshot(qtbot, welcome_view, "WelcomeView_direct")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.
