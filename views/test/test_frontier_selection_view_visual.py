import pytest

from test.utils.visual_test_helpers import capture_widget_screenshot
from views.frontier_selection_view import FrontierSelectionView


def test_frontier_selection_view_render(qtbot):
    """Captures a PNG of the FrontierSelectionView with mock data."""
    mock_player_names = ["Gandalf", "Saruman"]
    mock_proposed_terrains = [
        ("Gandalf", "Highland"),
        ("Saruman", "Swampland"),
    ]
    frontier_view = FrontierSelectionView(
        player_names=mock_player_names,
        proposed_frontier_terrains=mock_proposed_terrains,
    )
    capture_widget_screenshot(qtbot, frontier_view, "FrontierSelectionView_initial")
