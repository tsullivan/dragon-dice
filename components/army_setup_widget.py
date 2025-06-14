from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QLineEdit, QComboBox, QGroupBox)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional

class ArmySetupWidget(QWidget):
    """
    A widget for setting up a single army's name and points.
    """
    name_changed = Signal(str)
    points_changed = Signal(int)

    def __init__(self, army_type: str, army_points_allowed: List[int], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.army_type = army_type

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0) # No external margins, let parent handle

        # Army Name Input
        name_label = QLabel("Name:") # Changed to generic "Name:"
        self.name_input = QLineEdit(self.army_type) # Default name to type
        self.name_input.setMinimumWidth(150)
        self.name_input.textChanged.connect(self.name_changed.emit)

        # Army Points Input
        points_label = QLabel("Points:")
        self.points_combo = QComboBox()
        for val in army_points_allowed:
            self.points_combo.addItem(str(val), val)
        if army_points_allowed:
            self.points_combo.setCurrentIndex(0) # Default to 0 points
        self.points_combo.currentIndexChanged.connect(self._emit_points_changed)

        layout.addWidget(name_label)
        layout.addWidget(self.name_input, 1) # Name input takes more space
        layout.addSpacing(20)
        layout.addWidget(points_label)
        layout.addWidget(self.points_combo)

    def _emit_points_changed(self, index: int):
        self.points_changed.emit(self.points_combo.itemData(index))

    def get_name(self) -> str:
        return self.name_input.text().strip()

    def set_name(self, name: str):
        self.name_input.setText(name)

    def get_points(self) -> int:
        return self.points_combo.currentData()

    def set_points(self, points: int):
        for i in range(self.points_combo.count()):
            if self.points_combo.itemData(i) == points:
                self.points_combo.setCurrentIndex(i)
                break

    def setVisible(self, visible: bool):
        # Override setVisible to also control child label visibility if needed,
        # though typically the layout handles children of the main widget.
        # For now, just call super.
        super().setVisible(visible)

    # Optional: Add method to connect randomize button if that logic is moved here
    # def connect_randomize_button(self, button_callable):
    #     # e.g., self.random_button.clicked.connect(button_callable)
    #     pass
