# components/dragon_selection_widget.py
from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from components.carousel import CarouselInputWidget
from models.dragon_model import get_available_dragon_types
from models.element_model import ELEMENT_DATA, get_all_element_names


class DragonSelectionWidget(QWidget):
    """Widget for selecting both dragon type and whether it's a dragon or wyrm."""

    valueChanged = Signal(dict)  # Emits {"dragon_type": str, "die_type": str}

    def __init__(self, dragon_number: int = 1, parent=None):
        super().__init__(parent)
        self.dragon_number = dragon_number

        # Initialize with default values
        self._current_dragon_type = get_all_element_names()[0]  # Start with first element
        self._current_die_type = get_available_dragon_types()[0]  # Drake or Wyrm

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

        # Dragon element/color selection
        dragon_type_layout = QHBoxLayout()
        dragon_type_label = QLabel("Color:")
        dragon_type_label.setMinimumWidth(40)
        # Create element display values with icons
        element_display_values = [ELEMENT_DATA[elem].get_display_format() for elem in get_all_element_names()]
        self.dragon_type_carousel = CarouselInputWidget(
            allowed_values=element_display_values,
            initial_value=ELEMENT_DATA[self._current_dragon_type].get_display_format(),
        )
        dragon_type_layout.addWidget(dragon_type_label)
        dragon_type_layout.addWidget(self.dragon_type_carousel, 1)
        main_layout.addLayout(dragon_type_layout)

        # Dragon vs Wyrm selection
        die_type_layout = QHBoxLayout()
        die_type_label = QLabel("Die:")
        die_type_label.setMinimumWidth(40)
        self.die_type_carousel = CarouselInputWidget(
            allowed_values=get_available_dragon_types(),
            initial_value=self._current_die_type,
        )
        die_type_layout.addWidget(die_type_label)
        die_type_layout.addWidget(self.die_type_carousel, 1)
        main_layout.addLayout(die_type_layout)

    def _connect_signals(self):
        self.dragon_type_carousel.valueChanged.connect(self._on_dragon_type_changed)
        self.die_type_carousel.valueChanged.connect(self._on_die_type_changed)

    def _on_dragon_type_changed(self, new_type):
        # Convert from display format back to element name
        for element_name in get_all_element_names():
            if ELEMENT_DATA[element_name].get_display_format() == new_type:
                self._current_dragon_type = element_name
                break
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
        if dragon_type and dragon_type in get_all_element_names():
            self._current_dragon_type = dragon_type
            self.dragon_type_carousel.setValue(ELEMENT_DATA[dragon_type].get_display_format())

        # Update die type if provided
        die_type = dragon_data.get("die_type")
        if die_type and die_type in get_available_dragon_types():
            self._current_die_type = die_type
            self.die_type_carousel.setValue(die_type)

        self._emit_current_value()

    def clear(self):
        """Reset to default values."""
        self._current_dragon_type = get_all_element_names()[0]
        self._current_die_type = get_available_dragon_types()[0]
        self.dragon_type_carousel.setValue(ELEMENT_DATA[self._current_dragon_type].get_display_format())
        self.die_type_carousel.setValue(self._current_die_type)
        self._emit_current_value()

    def get_display_text(self) -> str:
        """Get a human-readable display text for the current selection."""
        return f"{self._current_dragon_type} ({self._current_die_type})"
