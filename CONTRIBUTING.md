# Contributing to Dragon Dice Digital Companion

First off, thank you for considering contributing to the Dragon Dice Digital Companion! We appreciate your help in making this project better.

This document provides guidelines for setting up your development environment on Windows.

## Getting Started

### Prerequisites

*   **Python**: Ensure you have Python installed on your Windows system. Version 3.8 or newer is recommended. You can download it from the [official Python website](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH".
*   **Git**: You'll need Git to clone the repository and manage your changes. You can download it from [git-scm.com](https://git-scm.com/download/win).

### Setting Up the Development Environment

1.  **Clone the Repository**:
    Open Git Bash, Command Prompt, or PowerShell and navigate to the directory where you want to store the project. Then, clone the repository:
    ```bash
    git clone https://github.com/your-username/dragon-dice.git # Replace with the actual repository URL
    cd dragon-dice
    ```

2.  **Create and Activate a Virtual Environment**:
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # Navigate to the project root directory (e.g., dragon-dice)
    python -m venv venv
    ```
    Activate the virtual environment:
    ```bash
    venv\Scripts\activate
    ```
    Your command prompt should now be prefixed with `(venv)`.

3.  **Install Dependencies**:
    With the virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the application for development or testing:
```bash
python src/main.py
```

## Making Changes

1.  **Create a Branch**: Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name  # or bugfix/your-bug-fix-name
    ```
2.  **Write Code**: Make your changes to the codebase.
3.  **Test**: Ensure your changes work as expected and don't break existing functionality.
4.  **Commit**: Commit your changes with a clear and descriptive commit message.
5.  **Push**: Push your branch to your fork on GitHub.
6.  **Pull Request**: Open a pull request from your branch to the main project repository.

## Code Style

Please try to follow PEP 8 style guidelines for Python code.

Thank you for contributing!