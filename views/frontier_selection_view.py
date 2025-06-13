from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QComboBox, QFormLayout, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from constants import TERRAIN_TYPES

class FrontierSelectionView(QWidget):
    """
    View for selecting the first player and the frontier terrain.
    """
    # Emits (first_player_name, frontier_terrain_type)
    frontier_data_submitted = Signal(str, str)

    def __init__(self, player_names, parent=None):
        super().__init__(parent)
        self.player_names = player_names

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel("Determine Frontier & First Player")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 40, 20, 20) # More top margin
        form_layout.setSpacing(15)

        # First Player Selection
        self.first_player_combo = QComboBox()
        if self.player_names:
            self.first_player_combo.addItems(self.player_names)
        else:
            self.first_player_combo.addItem("No Players Available")
            self.first_player_combo.setEnabled(False)
        form_layout.addRow("Select First Player:", self.first_player_combo)

        # Frontier Terrain Selection
        self.frontier_terrain_combo = QComboBox()
        self.frontier_terrain_combo.addItems(TERRAIN_TYPES)
        form_layout.addRow("Select Frontier Terrain:", self.frontier_terrain_combo)

        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.submit_button = QPushButton("Submit Selections")
        if not self.player_names:
            self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self._on_submit)
        layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _on_submit(self):
        selected_player = self.first_player_combo.currentText()
        selected_terrain = self.frontier_terrain_combo.currentText()
        self.frontier_data_submitted.emit(selected_player, selected_terrain)
