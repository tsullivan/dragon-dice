# components/dragon_selection_widget.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any

from components.carousel import CarouselInputWidget
import constants


class DragonSelectionWidget(QWidget):
    """Widget for selecting both dragon type and whether it's a dragon or wyrm."""

    valueChanged = Signal(dict)  # Emits {"dragon_type": str, "die_type": str}

    def __init__(self, dragon_number: int = 1, parent=None):
        super().__init__(parent)
        self.dragon_number = dragon_number

        # Initialize with default values
        self._current_dragon_type = constants.AVAILABLE_DRAGON_TYPES[0]
        self._current_die_type = constants.DRAGON_DIE_TYPE_DRAKE

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Dragon number label
        title_label = QLabel(f"Dragon {self.dragon_number}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Dragon type selection
        dragon_type_layout = QHBoxLayout()
        dragon_type_label = QLabel("Type:")
        dragon_type_label.setMinimumWidth(40)
        self.dragon_type_carousel = CarouselInputWidget(
            allowed_values=constants.AVAILABLE_DRAGON_TYPES,
            initial_value=self._current_dragon_type,
        )
        dragon_type_layout.addWidget(dragon_type_label)
        dragon_type_layout.addWidget(self.dragon_type_carousel, 1)
        main_layout.addLayout(dragon_type_layout)

        # Dragon vs Wyrm selection
        die_type_layout = QHBoxLayout()
        die_type_label = QLabel("Die:")
        die_type_label.setMinimumWidth(40)
        self.die_type_carousel = CarouselInputWidget(
            allowed_values=constants.AVAILABLE_DRAGON_DIE_TYPES,
            initial_value=self._current_die_type,
        )
        die_type_layout.addWidget(die_type_label)
        die_type_layout.addWidget(self.die_type_carousel, 1)
        main_layout.addLayout(die_type_layout)

    def _connect_signals(self):
        self.dragon_type_carousel.valueChanged.connect(self._on_dragon_type_changed)
        self.die_type_carousel.valueChanged.connect(self._on_die_type_changed)

    def _on_dragon_type_changed(self, new_type):
        self._current_dragon_type = new_type
        self._emit_current_value()

    def _on_die_type_changed(self, new_type):
        self._current_die_type = new_type
        self._emit_current_value()

    def _emit_current_value(self):
        current_value = {
            "dragon_type": self._current_dragon_type,
            "die_type": self._current_die_type,
        }
        self.valueChanged.emit(current_value)

    def value(self) -> Dict[str, Any]:
        """Get the current dragon selection as a dictionary."""
        return {
            "dragon_type": self._current_dragon_type,
            "die_type": self._current_die_type,
        }

    def setValue(self, dragon_data: Dict[str, Any]):
        """Set the dragon selection from a dictionary."""
        if not isinstance(dragon_data, dict):
            return

        # Update dragon type if provided
        dragon_type = dragon_data.get("dragon_type")
        if dragon_type and dragon_type in constants.AVAILABLE_DRAGON_TYPES:
            self._current_dragon_type = dragon_type
            self.dragon_type_carousel.setValue(dragon_type)

        # Update die type if provided
        die_type = dragon_data.get("die_type")
        if die_type and die_type in constants.AVAILABLE_DRAGON_DIE_TYPES:
            self._current_die_type = die_type
            self.die_type_carousel.setValue(die_type)

        self._emit_current_value()

    def clear(self):
        """Reset to default values."""
        self._current_dragon_type = constants.AVAILABLE_DRAGON_TYPES[0]
        self._current_die_type = constants.DRAGON_DIE_TYPE_DRAKE
        self.dragon_type_carousel.setValue(self._current_dragon_type)
        self.die_type_carousel.setValue(self._current_die_type)
        self._emit_current_value()

    def get_display_text(self) -> str:
        """Get a human-readable display text for the current selection."""
        return f"{self._current_dragon_type} ({self._current_die_type})"
