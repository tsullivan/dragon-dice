import pytest

from test.utils.visual_test_helpers import capture_widget_screenshot
from views.welcome_view import WelcomeView


def test_welcome_view_direct_render(qtbot):
    """Captures a PNG of the WelcomeView rendered directly."""
    welcome_view = WelcomeView()
    capture_widget_screenshot(qtbot, welcome_view, "WelcomeView_direct")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.
