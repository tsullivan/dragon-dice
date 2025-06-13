import pytest
import os
from PySide6.QtWidgets import QApplication

from views.main_gameplay_view import MainGameplayView
from engine import GameEngine # To instantiate the game engine for the view

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

def test_main_gameplay_view_initial_state(qtbot):
    """Captures a PNG of the MainGameplayView in its initial state."""

    # Mock data for GameEngine initialization
    mock_player_setup_data = [
        {"name": "Player 1", "home_terrain": "Highland", "armies": {"home": {"name": "P1 Home", "points": 10}, "campaign": {"name": "P1 Campaign", "points": 10}, "horde": {"name": "P1 Horde", "points": 4}}},
        {"name": "Player 2", "home_terrain": "Coastland", "armies": {"home": {"name": "P2 Home", "points": 12}, "campaign": {"name": "P2 Campaign", "points": 8}, "horde": {"name": "P2 Horde", "points": 4}}}
    ]
    mock_first_player_name = "Player 1"
    mock_frontier_terrain = "Flatland"
    mock_distance_rolls = [("Player 1", 3), ("Player 2", 5)]

    game_engine = GameEngine(
        player_setup_data=mock_player_setup_data,
        first_player_name=mock_first_player_name,
        frontier_terrain=mock_frontier_terrain,
        distance_rolls=mock_distance_rolls
    )

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_initial")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.
