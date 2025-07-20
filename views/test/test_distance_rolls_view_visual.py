import pytest

from models.test.mock import create_player_setup_dict
from test.utils.visual_test_helpers import capture_widget_screenshot
from views.distance_rolls_view import DistanceRollsView


def test_distance_rolls_view_render(qtbot):
    """Captures a PNG of the DistanceRollsView with mock data."""
    mock_player_setup_data = [
        create_player_setup_dict(
            name="Aragorn", home_terrain="Highland", frontier_terrain_proposal="Flatland", force_size=24
        ),
        create_player_setup_dict(
            name="Legolas", home_terrain="Swampland", frontier_terrain_proposal="Flatland", force_size=24
        ),
    ]
    mock_frontier_terrain = "Flatland"
    distance_rolls_view = DistanceRollsView(
        player_setup_data=mock_player_setup_data, frontier_terrain=mock_frontier_terrain
    )
    capture_widget_screenshot(qtbot, distance_rolls_view, "DistanceRollsView_initial")
