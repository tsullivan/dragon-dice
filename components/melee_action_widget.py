from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Signal
from typing import Optional


class MeleeActionWidget(QWidget):
    """
    A widget for handling melee action inputs, including attacker rolls and defender saves.
    """

    attacker_results_submitted = Signal(str)
    defender_results_submitted = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Attacker Section
        self.attacker_group = QGroupBox("Attacker")
        attacker_layout = QVBoxLayout(self.attacker_group)

        self.attacker_melee_label = QLabel("Enter Melee Results:")
        self.attacker_melee_input = QLineEdit()
        self.attacker_melee_input.setMaximumWidth(250)  # Prevent excessive stretching
        self.attacker_melee_input.setPlaceholderText("e.g., '5 hits, 2 SAIs'")
        self.submit_attacker_melee_button = QPushButton("Submit Attacker Melee")
        self.submit_attacker_melee_button.setMaximumWidth(200)  # Limit button width
        self.submit_attacker_melee_button.clicked.connect(
            self._on_submit_attacker_melee
        )

        attacker_layout.addWidget(self.attacker_melee_label)
        attacker_layout.addWidget(self.attacker_melee_input)
        attacker_layout.addWidget(self.submit_attacker_melee_button)
        main_layout.addWidget(self.attacker_group)

        # Defender Section
        self.defender_group = QGroupBox("Defender")
        defender_layout = QVBoxLayout(self.defender_group)

        self.defender_save_label = QLabel("Enter Save Results:")
        self.defender_save_input = QLineEdit()
        self.defender_save_input.setMaximumWidth(250)  # Prevent excessive stretching
        self.defender_save_input.setPlaceholderText("e.g., '3 saves'")
        self.submit_defender_save_button = QPushButton("Submit Defender Saves")
        self.submit_defender_save_button.setMaximumWidth(200)  # Limit button width
        self.submit_defender_save_button.clicked.connect(self._on_submit_defender_saves)

        defender_layout.addWidget(self.defender_save_label)
        defender_layout.addWidget(self.defender_save_input)
        defender_layout.addWidget(self.submit_defender_save_button)
        main_layout.addWidget(self.defender_group)

        # Initially, the whole widget might be hidden, or specific parts.
        # Parent view will control overall visibility.
        # By default, show attacker, hide defender, or vice-versa based on game state.

    def _on_submit_attacker_melee(self):
        results = self.attacker_melee_input.text().strip()
        self.attacker_results_submitted.emit(results)

    def _on_submit_defender_saves(self):
        results = self.defender_save_input.text().strip()
        self.defender_results_submitted.emit(results)

    def show_attacker_input(self):
        self.attacker_group.setVisible(True)
        self.defender_group.setVisible(False)
        self.attacker_melee_input.clear()
        self.attacker_melee_input.setFocus()

    def show_defender_input(self):
        self.attacker_group.setVisible(False)
        self.defender_group.setVisible(True)
        self.defender_save_input.clear()
        self.defender_save_input.setFocus()

    def get_attacker_results(self) -> str:
        return self.attacker_melee_input.text().strip()

    def get_defender_results(self) -> str:
        return self.defender_save_input.text().strip()

    def clear_inputs(self):
        self.attacker_melee_input.clear()
        self.defender_save_input.clear()
