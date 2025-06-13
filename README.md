# Dragon Dice Digital - Architecture and Project Guide (PySide6 Version)

This document outlines the architectural direction, domains of code, and file structure for the Dragon Dice digital companion project, built with Python and PySide6.

## 1. Project Overview

This project is a standalone desktop application that serves as a **digital companion app** or **game tracker** for the physical tabletop game, **Dragon Dice®**. Its purpose is not to simulate the game, but rather to manage the complex game state, track turns and phases, and guide players through the rules. All dice rolling and army management is performed by the players in the physical world, and the results are entered into this application.

### Technology Stack

*   **Python:** A versatile, high-level programming language used for the entire application logic.
*   **PySide6 (Qt for Python):** A set of Python bindings for the Qt cross-platform C++ framework. It is used for creating the graphical user interface (GUI), managing windows, widgets, and event handling.

## 2. Architectural Direction

The core architecture is designed around two main principles: the **Companion App Paradigm** and a strict **Separation of Concerns**.

### a. Companion App Paradigm

The application is fundamentally **reactive**. It does not run on a self-contained timer. Instead, at almost every step, it presents the current game state, prompts the user to perform a physical action, and then **waits for user input** before proceeding. This makes the application a "digital game master" that guides play but does not replace the physical components.

### b. Separation of Concerns & Code Domains

To manage complexity, the codebase is divided into several distinct domains, each with a clear responsibility, generally following a Model-View-Controller (MVC) or Model-View-ViewModel (MVVM) inspired pattern.

| Domain                       | Responsibility                                                                                                                        | Key Files/Modules              |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **1. Application Core**    | Initializes the Qt application, manages the main window, and the application's lifecycle.                                               | `main_app.py`, `main_window.py` |
| **2. Views (UI Screens)**  | Individual screens or UI components that the user interacts with. They display data and emit signals based on user actions.             | `views/` (e.g., `welcome_view.py`) |
| **3. Controllers**         | Mediate between Views and the Model/Engine. They handle user input logic from views and update the model or trigger engine actions.     | `controllers/` (e.g., `gameplay_controller.py`) |
| **4. Game Logic & Engine** | The "Rules Lawyer." Enforces game rules, manages game state transitions, and processes player actions.                                  | `engine.py`                    |
| **5. Data Models**         | Hold application-wide data (like player choices, game settings) and specific data structures (like help text). Emits signals on change. | `models/` (e.g., `app_data_model.py`, `help_text_model.py`) |
| **6. Shared Constants**    | Defines constants used across the application (e.g., terrain types).                                                                  | `constants.py`                 |
| **7. UI Components**       | Reusable custom UI widgets used across different views.                                                                               | `components/` (e.g., `carousel.py`) |

## 3. File Structure

The file structure is organized to reflect these domains.

```
.
├── main_app.py               # Domain 1: Application entry point, QApplication setup.
├── main_window.py            # Domain 1: Main QMainWindow, manages view switching.
├── app_data_model.py         # Domain 5: Shared application state and setup data.
├── engine.py                 # Domain 4: Core game logic and state machine.
├── constants.py              # Domain 6: Shared application constants.
├── views/                    # Domain 2: Contains all UI screen widgets.
│   ├── __init__.py           # Makes 'views' a Python package.
│   ├── welcome_view.py       # UI for the initial welcome screen.
│   ├── player_setup_view.py  # UI for individual player setup.
│   └── ... (other view files)
├── controllers/              # Domain 3: Contains controller classes.
│   ├── __init__.py           # Makes 'controllers' a Python package.
│   └── gameplay_controller.py  # Handles logic for main gameplay interactions.
├── models/                   # Domain 5: Contains data model classes.
│   ├── __init__.py           # Makes 'models' a Python package.
│   ├── app_data_model.py     # Holds shared application state and setup data.
│   └── help_text_model.py    # Provides structured help text.
├── components/               # Domain 7: Contains reusable UI component widgets.
│   ├── __init__.py           # Makes 'components' a Python package.
│   └── carousel.py           # Custom carousel input widget.
└── requirements.txt          # Lists project dependencies (e.g., PySide6).
```

### Key File Descriptions

*   **`main_app.py`**: The entry point of the application. It initializes the `QApplication` and the `MainWindow`.
*   **`main_window.py`**: Defines the main application window (`QMainWindow`). It is responsible for managing and switching between different views (screens) and may instantiate controllers.
*   **`engine.py`**: Contains the core game logic, rules enforcement, and state machine for the game's progression.
*   **`views/` directory**: Each `.py` file in this directory typically defines a `QWidget` representing a specific screen or major UI component (e.g., `WelcomeView`, `PlayerSetupView`). These views are responsible for displaying information and emitting signals upon user interaction.
*   **`controllers/` directory**: Contains classes that act as intermediaries between views and the model/engine. They handle logic triggered by view signals and update the `AppDataModel` or `GameEngine`.
*   **`models/` directory**: Houses classes that manage application data. `app_data_model.py` holds shared application state (like player choices, game settings) and uses Qt signals for updates. `help_text_model.py` centralizes help text strings.
*   **`components/` directory**: Contains custom, reusable `QWidget` subclasses that can be incorporated into various views (e.g., `carousel.py` for a carousel input).
*   **`constants.py`**: Stores global constants used throughout the application.

## 4. Operating the Project

This section provides instructions on how to set up and run the application.

### Prerequisites

Before running the application, ensure you have **Python** installed on your system (version 3.8 or newer is recommended).

### Installation

1.  **Navigate** to the root directory of the project in your terminal.
2.  **(Optional but Recommended)** Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install** the required packages from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the game, execute the `main_app.py` script from the project's root directory:
```bash
python main_app.py
```

This will launch the Qt window and start the application, beginning with the Welcome Screen.
