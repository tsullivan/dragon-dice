from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
from typing import Optional


class ActionChoiceWidget(QWidget):
    """
    A widget for selecting an action type (Melee, Missile, Magic).
    """

    action_selected = Signal(str)  # Emits "MELEE", "MISSILE", or "MAGIC"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No external margins, let parent handle

        self.melee_button = QPushButton("Melee Action")
        self.melee_button.setMaximumWidth(150)  # Limit button width
        self.melee_button.clicked.connect(lambda: self.action_selected.emit("MELEE"))
        layout.addWidget(self.melee_button)

        self.missile_button = QPushButton("Missile Action")
        self.missile_button.setMaximumWidth(150)  # Limit button width
        self.missile_button.clicked.connect(
            lambda: self.action_selected.emit("MISSILE")
        )
        layout.addWidget(self.missile_button)

        self.magic_button = QPushButton("Magic Action")
        self.magic_button.setMaximumWidth(150)  # Limit button width
        self.magic_button.clicked.connect(lambda: self.action_selected.emit("MAGIC"))
        layout.addWidget(self.magic_button)

        self.setLayout(layout)
