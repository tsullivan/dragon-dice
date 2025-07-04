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

## Development Scripts

The project includes several development scripts to maintain code quality and streamline the development workflow:

### Code Quality Scripts

#### Type Checking
```bash
python scripts/run_typecheck.py
```
- Uses mypy for static type analysis
- Configuration in `mypy.ini` with 120-character line length
- Reports type errors with file locations and error codes
- Excludes test directories to focus on production code

#### Code Linting and Formatting
```bash
python scripts/run_linter.py
```
- Uses ruff for fast linting and style checking
- Configuration in `ruff.toml` with 120-character line length
- Checks code quality AND formatting consistency
- Reports issues with auto-fix suggestions

#### Auto-Format Code
```bash
python scripts/format_code.py
```
- Automatically fixes many linting and formatting issues
- Uses ruff's auto-fix capabilities
- Safe to run - only applies non-breaking changes

### Development Environment Setup

#### Automated Setup
```bash
python scripts/setup_dev_env.py
```
- Installs all Python dependencies from requirements.txt
- Sets up development tools (pip-tools, twine)
- Configures pre-commit hooks (if pre-commit is available)
- Runs initial validation checks
- Provides setup completion status and next steps

### Git Hooks

#### Pre-Commit Hook Management
```bash
python scripts/setup_git_hooks.py
```
Interactive script that offers:
- **LENIENT mode**: Shows warnings but allows commits (current setting)
- **STRICT mode**: Blocks commits if type/lint checks fail
- **Remove hooks**: Disable automatic checking
- **Status check**: See current hook configuration

The pre-commit hook automatically runs type checking and linting before each commit, helping maintain code quality standards.

### Development Workflow

1. **Before coding**: Run type check to understand current state
   ```bash
   python scripts/run_typecheck.py
   ```

2. **During development**: Use linter for immediate feedback
   ```bash
   python scripts/run_linter.py
   ```

3. **Before committing**: Auto-fix issues and verify clean state
   ```bash
   python scripts/format_code.py
   python scripts/run_linter.py
   python scripts/run_typecheck.py
   ```

4. **Testing**: Run comprehensive test suite
   ```bash
   python -m pytest
   ```

### Code Style Standards

- **Line length**: 120 characters (consistent between ruff and mypy)
- **Import sorting**: Alphabetical with first-party modules separated
- **Type hints**: Required for function parameters and return values  
- **Docstrings**: Required for public functions and classes
- **Variable naming**: Use descriptive names, avoid single letters (except loop counters)

### Running Tests

#### Run All Tests
```bash
python -m pytest
```
