import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow


class DragonDiceApp(QApplication):
    """
    Main application class.
    Manages the lifecycle of the Qt application.
    """

    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = MainWindow()

    def run(self):
        self.main_window.show()
        return self.exec()


def run_pyside_app():
    """
    Entry point for the PySide6 application.
    """
    app = DragonDiceApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    run_pyside_app()
