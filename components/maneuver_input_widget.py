from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from typing import Optional


class ManeuverInputWidget(QWidget):
    """
    A widget for handling maneuver decisions and input.
    It first shows Yes/No buttons for deciding to maneuver.
    If 'Yes' is clicked, it shows an input field for maneuver details.
    """

    maneuver_decision_made = Signal(bool)  # True if yes, False if no
    maneuver_details_submitted = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Decision Section ---
        self._decision_widget = QWidget()
        decision_layout = QHBoxLayout(self._decision_widget)
        decision_layout.setContentsMargins(0, 0, 0, 0)

        self._maneuver_yes_button = QPushButton("Choose Army & Maneuver: Yes")
        self._maneuver_yes_button.setMaximumWidth(250)  # Limit button width
        self._maneuver_yes_button.clicked.connect(self._on_maneuver_yes)
        decision_layout.addWidget(self._maneuver_yes_button)

        self._maneuver_no_button = QPushButton("Choose Army & Maneuver: No")
        self._maneuver_no_button.setMaximumWidth(250)  # Limit button width
        self._maneuver_no_button.clicked.connect(self._on_maneuver_no)
        decision_layout.addWidget(self._maneuver_no_button)

        self._main_layout.addWidget(self._decision_widget)

        # --- Input Section (initially hidden) ---
        self._input_widget = QWidget()
        input_layout = QHBoxLayout(self._input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self._maneuver_input_label = QLabel("Enter Army & Maneuver Details:")
        input_layout.addWidget(self._maneuver_input_label)

        self._maneuver_input_field = QLineEdit()
        self._maneuver_input_field.setMaximumWidth(400)  # Prevent excessive stretching
        self._maneuver_input_field.setPlaceholderText(
            "e.g., 'Home Army: Flyers to hex 123' or 'Campaign Army: Unopposed maneuver'"
        )
        input_layout.addWidget(self._maneuver_input_field)  # Remove stretch factor

        self._submit_maneuver_button = QPushButton("Submit Maneuver")
        self._submit_maneuver_button.setMaximumWidth(180)  # Limit button width
        self._submit_maneuver_button.clicked.connect(self._on_submit_details)
        input_layout.addWidget(self._submit_maneuver_button)

        self._main_layout.addWidget(self._input_widget)
        self._input_widget.hide()  # Initially hidden

    def _on_maneuver_yes(self):
        self.maneuver_decision_made.emit(True)
        self._decision_widget.hide()
        self._input_widget.show()
        self._maneuver_input_field.clear()
        self._maneuver_input_field.setFocus()

    def _on_maneuver_no(self):
        self.maneuver_decision_made.emit(False)
        # The parent view will typically hide this whole widget or move to the next step.

    def _on_submit_details(self):
        details = self._maneuver_input_field.text().strip()
        self.maneuver_details_submitted.emit(details)
        self._maneuver_input_field.clear()

    def reset_to_decision(self):
        self._input_widget.hide()
        self._decision_widget.show()
