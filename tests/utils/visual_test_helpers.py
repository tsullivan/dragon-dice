# tests/utils/visual_test_helpers.py
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QApplication

from config.paths import ProjectPaths


class VisualTestConfig:
    """Configuration for visual tests."""

    def __init__(self, base_output_dir: Optional[Path] = None):
        self.base_output_dir = base_output_dir or self._get_default_output_dir()

    def _get_default_output_dir(self) -> Path:
        """Get default output directory for visual tests."""
        paths = ProjectPaths()
        return paths.test_visuals_dir / "views"

    def get_output_path(self, filename_base: str, sub_directory: str = "") -> Path:
        """Get output path for a test file, creating directories as needed."""
        if sub_directory:
            output_dir = self.base_output_dir / sub_directory
        else:
            output_dir = self.base_output_dir

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{filename_base}.png"


def capture_widget_screenshot(
    qtbot,
    widget_to_test: QWidget,
    filename_base: str,
    sub_directory: str = "",
    config: Optional[VisualTestConfig] = None,
):
    """Helper function to show a widget, capture, and save a screenshot."""
    config = config or VisualTestConfig()

    qtbot.addWidget(widget_to_test)
    widget_to_test.show()
    qtbot.waitExposed(widget_to_test)
    QApplication.processEvents()

    output_path = config.get_output_path(filename_base, sub_directory)
    pixmap = widget_to_test.grab()
    pixmap.save(str(output_path))

    print(f"Screenshot saved: {output_path}")
    assert output_path.exists()
    return output_path
