## Development Flow

This section describes how to set up your development environment for an efficient workflow, including auto-reloading the application on code changes and generating visual snapshots of UI components.
### Running the Application with Auto-Reload

To streamline development, we can use a Python library that automatically restarts the application whenever source code changes are detected. A common choice for this is `watchdog`.

1.  **Prerequisites**:
    Ensure you have `watchdog` installed in your Python environment. You can install it via pip:
    `pip install watchdog`

    You might also consider adding it to a `requirements-dev.txt` file.

2.  **Running the Dev Server**:
    You can use the `watchmedo` utility (part of `watchdog`) or a custom script to monitor your project files and restart `main_app.py`.

    Example using `watchmedo` (run this from your project's root directory):
    `watchmedo shell-command --patterns="*.py" --recursive --command="python main_app.py" .`

    Alternatively, you could create a small Python script (e.g., `run_dev.py`) that uses `watchdog` to achieve this.

    This command will start the application. Any saved changes to Python source files should trigger an automatic restart, allowing you to see your changes quickly.

### Generating View Snapshots for Manual Verification

For UI development with PySide6, it's useful to generate PNG images of individual windows, dialogs, or specific widgets using mock data or predefined states. This allows for quick manual verification of layout and rendering.

1.  **Tools Used**:
    *   **Test Runner**: We suggest using a common Python test runner like [pytest](https://docs.pytest.org/) for orchestrating tests.
    *   **Screenshot**: PySide6's built-in capabilities (`QWidget.grab()` or `QPixmap.grabWindow()`) can be used to capture screenshots of your UI elements.

2.  **File Structure**:
    *   Tests are typically located in a top-level `tests/` directory (e.g., `tests/test_views.py`).
    *   Mock data can be defined within the test files or loaded from separate JSON/Python files.
    *   Generated PNG files should be saved to a dedicated directory, for example, `test-visuals/`. This directory should be added to your `.gitignore` file.

3.  **Dependencies**:
    Ensure you have the necessary development dependencies installed. For a `pytest` setup with PySide6:
    `pip install pytest pytest-qt`

    (`pytest-qt` provides useful fixtures and utilities for testing Qt applications).
    You may also need `Pillow` if you want more advanced image manipulation, though `QPixmap` can save to PNG directly.
    `pip install Pillow`