import pytest
import os
from PySide6.QtWidgets import QApplication

# Assuming your MainWindow is in main_window.py at the project root
# Adjust this import if your project structure is different or main_window.py is elsewhere
# from main_window import MainWindow # No longer needed for this direct view test
from views.player_setup_view import PlayerSetupView
from constants import TERRAIN_DATA # For mock terrain options

# Ensure the output directory exists, as defined in CONTRIBUTING.md
VISUAL_TESTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-visuals", "views")
if not os.path.exists(VISUAL_TESTS_OUTPUT_DIR):
    os.makedirs(VISUAL_TESTS_OUTPUT_DIR, exist_ok=True)

# pytest-qt provides the qtbot fixture automatically, which manages QApplication.
def capture_widget_screenshot(qtbot, widget_to_test, filename_base, sub_directory=""):
    """
    Helper function to show a widget, capture, and save a screenshot.
    """
    qtbot.addWidget(widget_to_test) # Register widget with qtbot for cleanup and interaction
    widget_to_test.show()
    qtbot.waitExposed(widget_to_test) # Wait until the widget is shown and processed

    # If the widget is MainWindow, wait for its custom view_switched_and_ready signal
    # This is now handled in the test function itself after calling a view switch.
    # you might need qtbot.waitUntil or QTimer.singleShot with a subsequent processEvents.

    output_dir_path = os.path.join(VISUAL_TESTS_OUTPUT_DIR, sub_directory)
    if not os.path.exists(output_dir_path) and sub_directory:
        os.makedirs(output_dir_path, exist_ok=True)

    # Ensure all pending events are processed, allowing the widget to fully render
    QApplication.processEvents()

    output_path = os.path.join(output_dir_path, f"{filename_base}.png")
    pixmap = widget_to_test.grab()
    pixmap.save(output_path)
    print(f"Screenshot saved: {output_path}")
    # widget.close() # qtbot will handle cleanup
    assert os.path.exists(output_path) # Verify file was created
    return output_path

def test_player_setup_view_direct_render(qtbot): # Use qtbot fixture
    """Captures a PNG of the PlayerSetupView rendered directly with mock data."""

    # Mock data for PlayerSetupView
    mock_num_players = 2
    # TERRAIN_DATA is imported from constants.py, which AppDataModel uses
    mock_terrain_options = TERRAIN_DATA
    mock_required_dragons = 2 # As per AppDataModel.get_required_dragon_count()

    player_setup_view = PlayerSetupView(num_players=mock_num_players,
                                        terrain_display_options=mock_terrain_options,
                                        required_dragons=mock_required_dragons)

    capture_widget_screenshot(qtbot, player_setup_view, "PlayerSetupView_direct")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.
