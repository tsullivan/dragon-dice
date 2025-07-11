# components/dragon_selection_widget.py
from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

import constants
from components.carousel import CarouselInputWidget
from models.dragon_model import DRAGON_TYPE_DATA, DragonTypeModel, get_available_dragon_forms


class DragonSelectionWidget(QWidget):
    """Widget for selecting both dragon type and whether it's a dragon or wyrm."""

    value_changed = Signal(dict)  # Emits {"dragon_type": str, "dragon_form": str}

    def __init__(self, dragon_number: int = 1, parent=None):
        super().__init__(parent)
        self.dragon_number = dragon_number

        # Create mapping of dragon type display names to type keys
        self.dragon_type_display_options = {}  # Maps display name to type key
        self.type_to_display = {}  # Maps type key to display name

        # Build mappings from dragon types, filtering hybrids if disabled
        for type_key, dragon_type in DRAGON_TYPE_DATA.items():
            # Skip hybrid dragons if not allowed
            if not constants.ALLOW_HYBRID_DRAGONS and dragon_type.dragon_type in [
                DragonTypeModel.HYBRID,
                DragonTypeModel.IVORY_HYBRID,
            ]:
                continue

            display_name = dragon_type.get_display_name()
            self.dragon_type_display_options[display_name] = type_key
            self.type_to_display[type_key] = display_name

        # Initialize with default values
        self._current_dragon_type = list(self.type_to_display.keys())[0]
        self._current_dragon_form = get_available_dragon_forms()[0]  # Drake or Wyrm

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

        # Dragon type selection with proper display names
        dragon_type_layout = QHBoxLayout()
        dragon_type_label = QLabel("Type:")
        dragon_type_label.setMinimumWidth(40)
        # Use dragon type display names from the new dragon model
        dragon_display_values = list(self.dragon_type_display_options.keys())
        self.dragon_type_carousel = CarouselInputWidget(
            allowed_values=dragon_display_values,
            initial_value=self.type_to_display[self._current_dragon_type],
        )
        dragon_type_layout.addWidget(dragon_type_label)
        dragon_type_layout.addWidget(self.dragon_type_carousel, 1)
        main_layout.addLayout(dragon_type_layout)

        # Dragon form selection (Drake vs Wyrm)
        dragon_form_layout = QHBoxLayout()
        dragon_form_label = QLabel("Form:")
        dragon_form_label.setMinimumWidth(40)
        self.dragon_form_carousel = CarouselInputWidget(
            allowed_values=get_available_dragon_forms(),
            initial_value=self._current_dragon_form,
        )
        dragon_form_layout.addWidget(dragon_form_label)
        dragon_form_layout.addWidget(self.dragon_form_carousel, 1)
        main_layout.addLayout(dragon_form_layout)

    def _connect_signals(self):
        self.dragon_type_carousel.value_changed.connect(self._on_dragon_type_changed)
        self.dragon_form_carousel.value_changed.connect(self._on_dragon_form_changed)

    def _on_dragon_type_changed(self, new_display_name):
        # Convert from display name to type key
        if new_display_name in self.dragon_type_display_options:
            self._current_dragon_type = self.dragon_type_display_options[new_display_name]
        self._emit_current_value()

    def _on_dragon_form_changed(self, new_form):
        self._current_dragon_form = new_form
        self._emit_current_value()

    def _emit_current_value(self):
        current_value = {
            "dragon_type": self._current_dragon_type,
            "dragon_form": self._current_dragon_form,
        }
        self.value_changed.emit(current_value)

    def value(self) -> Dict[str, Any]:
        """Get the current dragon selection as a dictionary."""
        return {
            "dragon_type": self._current_dragon_type,
            "dragon_form": self._current_dragon_form,
        }

    def set_value(self, dragon_data: Dict[str, Any]):
        """Set the dragon selection from a dictionary."""
        if not isinstance(dragon_data, dict):
            return

        # Update dragon type if provided and allowed
        dragon_type = dragon_data.get("dragon_type")
        if dragon_type and dragon_type in self.type_to_display:
            # Check if hybrid dragons are allowed before setting
            if dragon_type in DRAGON_TYPE_DATA:
                dragon_type_model = DRAGON_TYPE_DATA[dragon_type]
                if not constants.ALLOW_HYBRID_DRAGONS and dragon_type_model.dragon_type in [
                    DragonTypeModel.HYBRID,
                    DragonTypeModel.IVORY_HYBRID,
                ]:
                    # Skip setting hybrid dragon if not allowed
                    return

            self._current_dragon_type = dragon_type
            self.dragon_type_carousel.set_value(self.type_to_display[dragon_type])

        # Update dragon form if provided
        dragon_form = dragon_data.get("dragon_form")
        if dragon_form and dragon_form in get_available_dragon_forms():
            self._current_dragon_form = dragon_form
            self.dragon_form_carousel.set_value(dragon_form)

        self._emit_current_value()

    def clear(self):
        """Reset to default values."""
        self._current_dragon_type = list(self.type_to_display.keys())[0]
        self._current_dragon_form = get_available_dragon_forms()[0]
        self.dragon_type_carousel.set_value(self.type_to_display[self._current_dragon_type])
        self.dragon_form_carousel.set_value(self._current_dragon_form)
        self._emit_current_value()

    def get_display_text(self) -> str:
        """Get a human-readable display text for the current selection."""
        display_name = self.type_to_display.get(self._current_dragon_type, self._current_dragon_type)
        return f"{display_name} ({self._current_dragon_form})"
