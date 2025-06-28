# Dragon Dice Digital - Architecture and Project Guide (PySide6 Version)

This document outlines the architectural direction, domains of code, and file structure for the Dragon Dice digital companion project, built with Python and PySide6.

## 1. Project Overview

This project is a **digital companion app** (or game tracker) for the physical tabletop game **Dragon Dice®**. It's a standalone desktop application designed to help manage game state, track turns and phases, and guide players through rules. It does not simulate the game; all dice rolling and physical army management are done by players, with results entered into this app.

### Technology Stack

- **Python:** A versatile, high-level programming language used for the entire application logic.
- **PySide6 (Qt for Python):** A set of Python bindings for the Qt cross-platform C++ framework. It is used for creating the graphical user interface (GUI), managing windows, widgets, and event handling.

## 2. Architectural Direction

The core architecture is designed around two main principles: the **Companion App Paradigm** and a strict **Separation of Concerns**.

### a. Companion App Paradigm

The application is fundamentally **reactive**. It does not run on a self-contained timer. Instead, at almost every step, it presents the current game state, prompts the user to perform a physical action, and then **waits for user input** before proceeding. This makes the application a "digital game master" that guides play but does not replace the physical components.

### b. Separation of Concerns & Code Domains

To manage complexity, the codebase is divided into several distinct domains, each with a clear responsibility, generally following a Model-View-Controller (MVC) or Model-View-ViewModel (MVVM) inspired pattern.

| Domain                     | Responsibility                                                                                                                          | Key Files/Modules                                           |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **1. Application Core**    | Initializes the Qt application, manages the main window, and the application's lifecycle.                                               | `main.py`, `main_window.py`                             |
| **2. Views (UI Screens)**  | Individual screens or UI components that the user interacts with. They display data and emit signals based on user actions.             | `views/` (e.g., `welcome_view.py`, `main_gameplay_view.py`)                          |
| **3. Controllers**         | Mediate between Views and the Model/Engine. They handle user input logic from views and update the model or trigger engine actions.     | `controllers/` (e.g., `gameplay_controller.py`)             |
| **4. Game Logic & Engine** | The "Rules Lawyer." Enforces game rules, manages game state transitions, and processes player actions.                                  | `game_logic/` (e.g., `engine.py`, `turn_manager.py`, `action_resolver.py`) |
| **5. Data Models**         | Hold application-wide data (like player choices, game settings) and specific data structures (like help text). Emits signals on change. | `models/` (e.g., `app_data_model.py`, `help_text_model.py`) |
| **6. Shared Constants**    | Defines constants used across the application (e.g., terrain types, action types, phase definitions).                                                                    | `constants.py`                                              |
| **7. UI Components**       | Reusable custom UI widgets used across different views.                                                                                 | `components/` (e.g., `action_choice_widget.py`, `player_summary_widget.py`)                         |
| **8. Utilities**           | Helper functions for display formatting, file paths, and visual testing utilities.                                                     | `utils/` (e.g., `display_utils.py`), `config/` |
| **9. Testing**             | Comprehensive test suite including unit tests, integration tests, end-to-end tests, and visual regression tests.                       | `test/`, `components/test/`, `views/test/`, `game_logic/test/` |

## 3. File Structure

The file structure is organized to reflect these domains:

```
.
├── main.py                        # Domain 1: Application entry point
├── main_window.py                 # Domain 1: Main application window
├── constants.py                   # Domain 6: Shared constants and enums
├── requirements.txt               # Python dependencies
├── assets/                        # Game assets and documentation
│   ├── dragon dice rules v4.01d.txt
│   └── *.png                      # Game imagery
├── components/                    # Domain 7: Reusable UI widgets
│   ├── action_choice_widget.py    # Action selection buttons
│   ├── player_summary_widget.py   # Player army summaries
│   ├── maneuver_input_widget.py   # Maneuver decision widgets
│   └── test/                      # Component unit tests
├── config/                        # Domain 8: Configuration and paths
│   ├── paths.py                   # Project path management
│   ├── resource_manager.py        # Asset loading
│   └── test/                      # Config unit tests
├── controllers/                   # Domain 3: Controller classes
│   ├── gameplay_controller.py     # Main game flow controller
│   └── test/                      # Controller unit tests
├── data/                          # Static game data
│   └── unit_definitions.json      # Unit statistics and abilities
├── game_logic/                    # Domain 4: Core game logic and rules
│   ├── engine.py                  # Main game engine
│   ├── turn_manager.py            # Turn and phase management
│   ├── action_resolver.py         # Combat and action resolution
│   ├── game_state_manager.py      # Game state persistence
│   ├── effect_manager.py          # Special effects and abilities
│   ├── unit_manager.py            # Unit creation and management
│   └── test/                      # Game logic unit tests
├── models/                        # Domain 5: Data models and structures
│   ├── app_data_model.py          # Application-wide data
│   ├── help_text_model.py         # Help content and tooltips
│   ├── army_model.py              # Army composition data
│   └── test/                      # Model unit tests
├── test/                          # Domain 9: End-to-end and integration tests
│   ├── e2e/                       # End-to-end game flow tests
│   │   ├── run_all_e2e_tests.py   # E2E test runner
│   │   ├── test_action_flows.py   # Combat action testing
│   │   └── test_first_march_flows.py # Turn flow testing
│   └── utils/                     # Test utilities and helpers
│       └── visual_test_helpers.py # Screenshot testing utilities
├── test-visuals/                  # Visual regression test outputs
│   ├── components/                # Component screenshots
│   └── views/                     # View screenshots
├── utils/                         # Domain 8: Utility functions
│   └── display_utils.py           # Text formatting and display helpers
└── views/                         # Domain 2: UI screens and dialogs
    ├── welcome_view.py            # Initial game setup screen
    ├── player_setup_view.py       # Army configuration screen
    ├── main_gameplay_view.py      # Primary game interface
    ├── action_dialog.py           # Combat action dialogs
    ├── maneuver_dialog.py         # Maneuver resolution dialogs
    └── test/                      # View unit and visual tests
```

## 4. Operating the Project

This section provides instructions on how to set up and run the application.

### Prerequisites

Before running the application, ensure you have **Python** installed on your system (version 3.8 or newer is recommended).

### Installation

1.  **Navigate** to the root directory of the project in your terminal.
2.  **(Optional but Recommended)** Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```
3.  **Install** the required packages from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the game, execute the `main.py` script from the project's root directory:

```bash
python main.py
```

This will launch the Qt window and start the application, beginning with the Welcome Screen.

## 5. Testing

The project includes a comprehensive test suite with multiple testing approaches to ensure code quality and game rule compliance.

### Test Organization

- **Unit Tests**: Located in `*/test/` directories within each module
- **Integration Tests**: Located in `test/e2e/` for cross-module testing  
- **Visual Tests**: UI component screenshot tests for visual regression detection
- **End-to-End Tests**: Complete game flow testing from user perspective

### Running Tests

#### Run All Tests
```bash
python -m pytest
```

#### Run Tests with Verbose Output
```bash
python -m pytest -v
```

#### Run Tests by Category

**Unit Tests Only:**
```bash
python -m pytest components/test/ models/test/ game_logic/test/ config/test/
```

**Integration/E2E Tests Only:**
```bash
python -m pytest test/e2e/
```

**Visual/UI Tests Only:**
```bash
python -m pytest views/test/ components/test/ -k "visual"
```

#### Run Specific Test Files
```bash
# Test game engine functionality
python -m pytest game_logic/test/test_engine_integration.py

# Test action flows (combat, maneuvers)
python -m pytest test/e2e/test_action_flows.py

# Test UI components
python -m pytest views/test/test_main_gameplay_view_visual.py
```

#### Run End-to-End Tests with Custom Runner
```bash
python test/e2e/run_all_e2e_tests.py
```

### Test Types and Coverage

#### Unit Tests
- **Game Logic**: Engine, turn manager, action resolver, state management
- **UI Components**: Widgets, dialogs, input validation
- **Models**: Data structures, serialization, validation
- **Utilities**: Display formatting, configuration management

#### Integration Tests  
- **Game Flow**: Complete turn cycles, phase transitions
- **Combat System**: Melee, missile, magic action resolution
- **Maneuver System**: Territory control and counter-maneuvers
- **UI Integration**: Signal/slot connections, state synchronization

#### Visual Tests
- **Component Screenshots**: Automated UI component rendering tests
- **Layout Validation**: Ensure UI elements display correctly
- **Visual Regression**: Detect unintended visual changes

### Test Dependencies

The test suite uses these additional packages (included in `requirements.txt`):
- **pytest**: Primary testing framework
- **pytest-qt**: Qt application testing support for PySide6

### Continuous Testing

Tests are designed to be run frequently during development:
```bash
# Quick smoke test - run fastest tests
python -m pytest -k "not visual" --maxfail=1

# Full regression test - all tests with coverage
python -m pytest -v
```

### Test Data and Assets

- **Visual Test Outputs**: Stored in `test-visuals/` for manual inspection
- **Test Game Data**: Minimal test configurations for reliable testing
- **Mock Data**: Simulated dice rolls and user inputs for deterministic tests

## 6. Development Guidelines

### Code Organization Principles

- **Signal-Driven Architecture**: Qt signals/slots for loose coupling between components
- **Domain Separation**: Clear boundaries between UI, controllers, and game logic
- **Test-Driven Development**: Comprehensive testing at unit, integration, and E2E levels
- **Visual Testing**: Screenshot-based regression testing for UI components

### Recent Improvements

- **Enhanced Action Resolution**: Fixed action step persistence across phase transitions
- **UI Update Optimization**: Reduced redundant UI updates and improved performance  
- **Comprehensive Testing**: Added end-to-end tests for complete game flow validation
- **Debug Logging**: Enhanced logging throughout the application for troubleshooting
- **Dialog Management**: Improved modal dialog handling and auto-closing mechanisms

### Architecture Notes

- **Reactive Design**: App waits for user input rather than running autonomously
- **Game Rule Compliance**: Faithful implementation of Dragon Dice v4.01d rules
- **Companion App Focus**: Assists with game state tracking, does not replace physical dice
- **Cross-Platform**: Built with PySide6 for Windows, macOS, and Linux compatibility

### Contributing

When adding new features:

1. **Follow Domain Structure**: Place code in appropriate domain directories
2. **Add Tests**: Include unit tests and integration tests for new functionality  
3. **Update Documentation**: Keep README.md and code comments current
4. **Test Visual Changes**: Run visual tests if UI components are modified
5. **Verify Game Rules**: Ensure changes comply with official Dragon Dice rules

### Troubleshooting

**Common Issues:**

- **Import Errors**: Ensure virtual environment is activated and dependencies installed
- **Qt Application Errors**: Check PySide6 installation and system Qt libraries
- **Test Failures**: Run tests individually to isolate issues
- **Visual Test Changes**: Review `test-visuals/` outputs for intended vs actual changes

**Debug Mode:**
```bash
# Run with detailed logging
python main.py --debug
```

**Performance Profiling:**
```bash
# Run tests with timing information
python -m pytest --durations=10
```
