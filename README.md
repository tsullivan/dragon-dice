# Dragon Dice Digital - Architecture and Project Guide

This document outlines the architectural direction, domains of code, and file structure for the Dragon Dice digital companion project, built with Python and PySide6.

## Project Overview

This project is a **digital companion app** (or game tracker) for the physical tabletop game **Dragon Dice®**. It's a standalone desktop application designed to help manage game state, track turns and phases, and guide players through rules. It does not simulate the game; all dice rolling and physical army management are done by players, with results entered into this app.

### Technology Stack

- **Python:** A versatile, high-level programming language used for the entire application logic.
- **PySide6 (Qt for Python):** A set of Python bindings for the Qt cross-platform C++ framework. It is used for creating the graphical user interface (GUI), managing windows, widgets, and event handling.

## Architectural Direction

The core architecture is designed around two main principles: the **Companion App Paradigm** and a strict **Separation of Concerns**.

### Companion App Paradigm

The application is fundamentally **reactive**. It does not run on a self-contained timer. Instead, at almost every step, it presents the current game state, prompts the user to perform a physical action, and then **waits for user input** before proceeding. This makes the application a "digital game master" that guides play but does not replace the physical components.

## Operating the Project

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

To run the game, execute the main script from the project's root directory:

```bash
python dragon_dice.py
```

This will launch the Qt window and start the application, beginning with the Welcome Screen.

## Testing

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
