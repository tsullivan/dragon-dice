from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

# Placeholder for views - you'll create these in separate files
# from .views.welcome_view import WelcomeView
# from .views.player_setup_view import PlayerSetupView

class MainWindow(QMainWindow):
    """
    The main window of the application.
    It will manage and display different views (screens).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice Companion (PySide6)")
        self.setGeometry(100, 100, 1280, 720) # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self._current_view = None
        self.show_welcome_screen() # Start with the welcome screen

    def show_welcome_screen(self):
        # In a real scenario, this would load WelcomeView
        # For now, a placeholder:
        if self._current_view:
            self.layout.removeWidget(self._current_view)
            self._current_view.deleteLater()
        self._current_view = QLabel("Welcome Screen Placeholder (PySide6)")
        self._current_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self._current_view)