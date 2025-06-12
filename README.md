# Dragon Dice Digital - Architecture and Project Guide (PyGame Version)

This document outlines the architectural direction, domains of code, and file structure for the Dragon Dice digital companion project, built with Python and PyGame.

## 1. Project Overview

This project is a standalone desktop application that serves as a **digital companion app** or **game tracker** for the physical tabletop game, **Dragon Dice®**. Its purpose is not to simulate the game, but rather to manage the complex game state, track turns and phases, and guide players through the rules. All dice rolling and army management is performed by the players in the physical world, and the results are entered into this application.

### Technology Stack

* **Python:** A versatile, high-level programming language used for the entire application logic.
* **PyGame:** A cross-platform set of Python modules designed for writing video games. It is used to create the window, handle user input (mouse, keyboard), and render all graphics and UI elements.

## 2. Architectural Direction

The core architecture is designed around two main principles: the **Companion App Paradigm** and a strict **Separation of Concerns**.

### a. Companion App Paradigm

The application is fundamentally **reactive**. It does not run on a self-contained timer. Instead, at almost every step, it presents the current game state, prompts the user to perform a physical action, and then **waits for user input** before proceeding. This makes the application a "digital game master" that guides play but does not replace the physical components.

### b. Separation of Concerns & Code Domains

To manage complexity, the codebase is divided into four distinct domains, each with a clear responsibility.

| Domain                       | Responsibility                                                                                                                        | Key Files/Modules              |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **1. App Flow & Control** | The "Orchestrator." Manages the main game loop, high-level screen transitions (e.g., Welcome, Setup, Gameplay), and event handling.      | `src/main.py`                  |
| **2. UI Rendering & Mgmt.** | The "View." Creates, draws, and manages all interactive UI elements like buttons and input boxes. It relies on callbacks to signal actions. | `src/ui_manager.py`            |
| **3. Game Logic & Engine** | The "Rules Lawyer." Enforces the official game rules. It contains the logic for turn sequences and processing player actions.      | `src/engine.py`                |
| **4. Data Models** | The "Game Board." Pure data containers that represent the game state (players, terrains, etc.). They contain no logic.            | `src/models.py`                |

## 3. File Structure

The file structure is organized to reflect these four domains.

```
.
├── src/
│   ├── ui_manager.py         # Domain 2: Creates/manages all UI elements.
│   ├── engine.py             # Domain 3: Implements game rules and logic.
│   ├── models.py             # Domain 4: All data classes (GameState, Player, etc.).
│   └── main.py               # Domain 1: The application's entry point and game loop.
├── assets/                   # For images, fonts, etc.
└── requirements.txt          # Lists project dependencies (e.g., pygame).
```


### Key File Descriptions

* **`src/main.py`**: The root of the application. It initializes PyGame, creates the main window, and runs the game loop. It holds the high-level application state (e.g., `app_state`) and the "controller" logic that responds to UI events and calls methods on the `GameEngine`.
* **`src/ui_manager.py`**: This module handles all UI rendering and interaction. It contains classes for `Button` and `TextInputBox`, and a main `UIManager` class to create, draw, and manage the UI for each screen.
* **`src/engine.py`**: The core of the game's logic. It accepts player input through public methods like `submit_frontier_selection()` and `submit_distance_rolls()`. It validates these actions against the rules and updates the `GameState` accordingly.
* **`src/models.py`**: A collection of data classes (`GameState`, `Player`, `Terrain`) and type definitions (`PlayerSetupData`) that serve as the single source of truth for the game's state.

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

To run the game, execute the `main.py` script from the project's root directory:

```bash
python src/main.py
```

This will launch the PyGame window and start the application, beginning with the Welcome Screen.