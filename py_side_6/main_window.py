from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from .views.welcome_view import WelcomeView
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
        self.central_widget_layout = QVBoxLayout(self.central_widget) # Renamed variable

        self._current_view = None
        self.show_welcome_view() # Start with the welcome screen

    def switch_view(self, new_view_widget):
        """Removes the current view and adds the new one."""
        if self._current_view:
            self.central_widget_layout.removeWidget(self._current_view)
            self._current_view.deleteLater()
        self._current_view = new_view_widget
        self.central_widget_layout.addWidget(self._current_view)

    def show_welcome_view(self):
        welcome_widget = WelcomeView()
        # Connect signals from welcome_widget to methods in MainWindow or a controller
        # e.g., welcome_widget.proceed_signal.connect(self.show_player_setup_view)
        self.switch_view(welcome_widget)