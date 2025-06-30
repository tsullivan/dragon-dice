import pytest

# Assuming your MainWindow is in main_window.py at the project root
# Adjust this import if your project structure is different or main_window.py is elsewhere
# from main_window import MainWindow # No longer needed for this direct view test
from views.player_setup_view import PlayerSetupView
from test.utils.visual_test_helpers import capture_widget_screenshot
from models.terrain_model import TERRAIN_DATA  # For mock terrain options


def test_player_setup_view_direct_render(qtbot):  # Use qtbot fixture
    """Captures a PNG of the PlayerSetupView rendered directly with mock data."""

    # Mock data for PlayerSetupView - convert new structure to expected format
    mock_num_players = 2
    mock_terrain_options = [
        (terrain.name, terrain.element_colors) for terrain in TERRAIN_DATA.values()
    ]
    mock_required_dragons = 2  # As per AppDataModel.get_required_dragon_count()
    mock_force_size = 24  # Add required force_size parameter

    player_setup_view = PlayerSetupView(
        num_players=mock_num_players,
        terrain_display_options=mock_terrain_options,
        required_dragons=mock_required_dragons,
        force_size=mock_force_size,
    )

    capture_widget_screenshot(qtbot, player_setup_view, "PlayerSetupView_direct")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.
