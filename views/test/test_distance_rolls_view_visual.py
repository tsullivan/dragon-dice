import pytest

from test.utils.visual_test_helpers import capture_widget_screenshot
from views.distance_rolls_view import DistanceRollsView


def test_distance_rolls_view_render(qtbot):
    """Captures a PNG of the DistanceRollsView with mock data."""
    mock_player_setup_data = [
        {"name": "Aragorn", "home_terrain": "Highland"},
        {"name": "Legolas", "home_terrain": "Swampland"},
    ]
    mock_frontier_terrain = "Flatland"
    distance_rolls_view = DistanceRollsView(
        player_setup_data=mock_player_setup_data, frontier_terrain=mock_frontier_terrain
    )
    capture_widget_screenshot(qtbot, distance_rolls_view, "DistanceRollsView_initial")
