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
| **1. Application Core**    | Initializes the Qt application, manages the main window, and the application's lifecycle.                                               | `main_app.py`, `main_window.py`                             |
| **2. Views (UI Screens)**  | Individual screens or UI components that the user interacts with. They display data and emit signals based on user actions.             | `views/` (e.g., `welcome_view.py`)                          |
| **3. Controllers**         | Mediate between Views and the Model/Engine. They handle user input logic from views and update the model or trigger engine actions.     | `controllers/` (e.g., `gameplay_controller.py`)             |
| **4. Game Logic & Engine** | The "Rules Lawyer." Enforces game rules, manages game state transitions, and processes player actions.                                  | `game_logic/engine.py` |
| **5. Data Models**         | Hold application-wide data (like player choices, game settings) and specific data structures (like help text). Emits signals on change. | `models/` (e.g., `app_data_model.py`, `help_text_model.py`) |
| **6. Shared Constants**    | Defines constants used across the application (e.g., terrain types).                                                                    | `constants.py`                                              |
| **7. UI Components**       | Reusable custom UI widgets used across different views.                                                                                 | `components/` (e.g., `carousel.py`)                         |

## 3. File Structure

The file structure is organized to reflect these domains:

```
.
├── controllers/                   # Domain 3: Contains controller classes
│   └── gameplay_controller.py
├── game_logic/                    # Domain 4: Core game logic and rules
│   ├── action_resolver.py
│   ├── effect_manager.py
│   ├── engine.py
│   ├── game_state_manager.py
│   └── turn_manager.py
├── models/                        # Domain 5: Data models and structures
│   ├── app_data_model.py
│   ├── army_model.py
│   ├── die_model.py
│   ├── help_text_model.py
│   ├── terrain_model.py
│   ├── unit_model.py
│   └── unit_roster_model.py
└── views/                         # Domain 2: Contains all UI screen widgets
    ├── welcome_view.py
    ├── player_setup_view.py
    ├── main_gameplay_view.py
    ├── distance_rolls_view.py
    ├── frontier_selection_view.py
    └── unit_selection_dialog.py
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

To run the game, execute the `main_app.py` script from the project's root directory:

```bash
python main_app.py
```

This will launch the Qt window and start the application, beginning with the Welcome Screen.

### Running the unit tests

```bash
python -m pytest
```
