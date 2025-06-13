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

4.  **Writing a Snapshot Test (Conceptual Example)**:
    A typical test to generate a PNG would:
    *   Prepare mock data/props for the view.
    *   Instantiate the Qt widget/window.
    *   Apply the mock data or set the state of the widget.
    *   Allow the Qt event loop to process events to ensure the widget is rendered.
    *   Use `widget.grab().save(filepath)` to capture the screenshot.
    *   Save the screenshot to the designated output directory (e.g., `test-visuals/MyWindow-state.png`).

    Here's a conceptual example of a test file using `pytest` and PySide6 (e.g., `tests/test_main_window_visuals.py`):

    ```python
    # tests/test_main_window_visuals.py
    import pytest
    import os
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    # Assuming your MainWindow is in main_window.py at the project root
    from main_window import MainWindow # Adjust import as per your project structure

    # Ensure the output directory exists
    VISUAL_TESTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-visuals", "views")
    if not os.path.exists(VISUAL_TESTS_OUTPUT_DIR):
        os.makedirs(VISUAL_TESTS_OUTPUT_DIR, exist_ok=True)

    @pytest.fixture(scope="session")
    def qapp_session(request):
        """Session-scoped QApplication instance."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def capture_widget_screenshot(widget, filename_suffix, data_for_view=None):
        """
        Helper function to show a widget, apply data, capture, and save a screenshot.
        """
        if data_for_view:
            # This is highly dependent on how your MainWindow or other views
            # accept and display data. You'll need to implement methods
            # in your view classes to set them up with mock data.
            # Example: widget.load_data(data_for_view)
            # Example: widget.some_label.setText(data_for_view.get("title", "Default Title"))
            print(f"Applying data: {data_for_view} (mock implementation)")

        widget.show()

        # Allow Qt to process events and render the widget
        QApplication.processEvents()
        # For more complex UIs or async operations, a QTimer might be needed
        # or pytest-qt's qtbot.waitExposed(widget)

        output_path = os.path.join(VISUAL_TESTS_OUTPUT_DIR, f"{widget.__class__.__name__}-{filename_suffix}.png")
        pixmap = widget.grab()
        pixmap.save(output_path)
        print(f"Screenshot saved: {output_path}")
        widget.close() # Clean up the widget
        return output_path

    def test_main_window_default_state(qapp_session):
        main_win = MainWindow()
        # Mock data for the default state, if applicable
        # mock_data = {"initial_text": "Welcome!"}
        # main_win.set_some_state(mock_data) # Example method
        capture_widget_screenshot(main_win, "default_state")
        # No specific pytest assertions are strictly needed if the goal is manual image verification.
        # However, you could assert that the file was created:
        # assert os.path.exists(os.path.join(VISUAL_TESTS_OUTPUT_DIR, "MainWindow-default_state.png"))

    def test_main_window_with_specific_data(qapp_session):
        main_win = MainWindow()
        mock_data = {"title": "Player Scores", "scores": {"Player1": 100, "Player2": 150}}
        # You would need a method in MainWindow to apply this data
        # e.g., main_win.display_scores(mock_data)
        capture_widget_screenshot(main_win, "specific_data_state", data_for_view=mock_data)

    # Add more tests for different views/widgets or different states.
    # Example for a hypothetical DiceRollView widget:
    # from my_project.dice_roll_view import DiceRollView
    #
    # def test_dice_roll_view_empty(qapp_session):
    #     dice_view = DiceRollView()
    #     capture_widget_screenshot(dice_view, "empty_state")
    #
    # def test_dice_roll_view_with_results(qapp_session):
    #     dice_view = DiceRollView()
    #     mock_results = {"dice": [6, 4, 5], "total": 15}
    #     # dice_view.show_results(mock_results) # Example method
    #     capture_widget_screenshot(dice_view, "results_state", data_for_view=mock_results)
    ```

    **Note**: The method for applying mock data and preparing your PySide6 widgets for screenshots (inside `capture_widget_screenshot` or similar helper functions) will be specific to how your UI components are designed. You'll need to implement ways to set their state or provide them with data programmatically. Using `pytest-qt`'s `qtbot` fixture can also be very helpful for interacting with widgets and waiting for signals or UI updates.

5.  **Running the Snapshot Generation Tests**:
    You can run these tests using `pytest`.

    To run all tests in the project:
    `python -m pytest`
    or (if pytest is in your PATH):
    `pytest`

    To run a specific visual test file:
    `python -m pytest tests/test_main_window_visuals.py`

    To run tests matching a specific pattern (e.g., all visual tests if named consistently):
    `python -m pytest -k "_visual"`
 
     After running, check the `test-visuals/views/` directory (or your configured output directory) for the generated PNG files. Developers can then open these images to manually verify the layout and rendering.
 

