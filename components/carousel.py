from typing import Any, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class CarouselInputWidget(QWidget):
    valueChanged = Signal(object)  # Can emit int or str

    def __init__(
        self,
        allowed_values: Optional[List[Any]] = None,
        min_val: int = 0,
        max_val: int = 10,
        step: int = 1,
        initial_value: Any = None,
        parent=None,
    ):
        super().__init__(parent)

        if allowed_values is not None:
            # Keep original type, just ensure uniqueness and sort if they are sortable
            # For terrains, sorting might be alphabetical by default if they are strings
            temp_values = []
            seen_hashable_representations = set()
            for original_item in allowed_values:
                # Create a hashable representation for uniqueness checking
                # Specifically for items like ('Name', [list_of_elements])
                if (
                    isinstance(original_item, tuple)
                    and len(original_item) > 0
                    and any(isinstance(el, list) for el in original_item)
                ):
                    hashable_item = tuple(tuple(el) if isinstance(el, list) else el for el in original_item)
                else:
                    hashable_item = original_item  # Assume it's already hashable or a primitive type

                if hashable_item not in seen_hashable_representations:
                    temp_values.append(original_item)  # Store the original item
                    seen_hashable_representations.add(hashable_item)
            try:  # Try sorting, will work for numbers and strings
                self._allowed_values = sorted(temp_values)
            except TypeError:  # If values are not sortable (e.g. mixed types, though not expected here)
                self._allowed_values = temp_values
        else:
            self._allowed_values = list(range(min_val, max_val + 1, step))

        if not self._allowed_values:  # Ensure there's at least one value to prevent errors
            self._allowed_values = [initial_value if initial_value is not None else 0]

        self._current_index = 0

        # Determine initial index
        current_val_to_set = self._allowed_values[0]  # Default to first value
        if initial_value is not None:
            if initial_value in self._allowed_values:
                self._current_index = self._allowed_values.index(initial_value)
                current_val_to_set = initial_value
            # If initial_value is not in allowed_values, it defaults to the first allowed_value
            # or the initial_value itself if allowed_values was empty and got populated by it.

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.prev_button = QPushButton("<")
        self.prev_button.setFixedWidth(30)
        self.prev_button.clicked.connect(self._previous_value)

        self.value_label = QLabel(str(current_val_to_set))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setMinimumWidth(40)

        self.next_button = QPushButton(">")
        self.next_button.setFixedWidth(30)
        self.next_button.clicked.connect(self._next_value)

        layout.addWidget(self.prev_button)
        layout.addWidget(self.value_label)
        layout.addWidget(self.next_button)

        self._update_button_states()

    def _previous_value(self):
        if not self._allowed_values:
            return
        try:
            current_index = self._allowed_values.index(self.value()) if self.value() in self._allowed_values else -1
            if (
                current_index == -1 and self._allowed_values or current_index == 0
            ):  # If current value is not in list, start from last
                new_index = len(self._allowed_values) - 1
            else:
                new_index = current_index - 1
            self.setValue(self._allowed_values[new_index])
        except (ValueError, IndexError):
            # Fallback to last item if something unexpected happens or list is empty
            if self._allowed_values:
                self.setValue(self._allowed_values[-1])

    def _next_value(self):
        if not self._allowed_values:
            return
        try:
            current_index = self._allowed_values.index(self.value()) if self.value() in self._allowed_values else -1
            if (
                current_index == -1 and self._allowed_values
            ):  # If current value is not in list (e.g. None), start from first
                new_index = 0
            elif current_index == len(self._allowed_values) - 1:  # If at the end, loop to the beginning
                new_index = 0
            else:
                new_index = current_index + 1
            self.setValue(self._allowed_values[new_index])
        except (
            ValueError,
            IndexError,
        ):  # ValueError if not found, IndexError if list is empty after check
            # Fallback to first item if something unexpected happens or list is empty
            if self._allowed_values:
                self.setValue(self._allowed_values[0])

    def _update_display_and_emit(self):
        if not self._allowed_values:  # Should not happen if constructor ensures _allowed_values is never empty
            self.value_label.setText("")
            self._update_button_states()
            self.valueChanged.emit(None)  # Or some other indicator of no value
            return

        current_val = self._allowed_values[self._current_index]
        # Check if this might be a terrain name and format with emoji
        display_text = self._format_display_value(current_val)
        self.value_label.setText(display_text)
        self._update_button_states()
        self.valueChanged.emit(current_val)

    def _format_display_value(self, value: Any) -> str:
        """Format display value with emoji if it's a known terrain type or dragon type."""
        if not value:
            return str(value)

        # Import utilities locally to avoid circular imports
        try:
            from utils.display_utils import clean_terrain_name, format_terrain_type

            value_str = str(value)

            # Extract clean terrain name from strings like "Coastland (Blue, Green)"
            clean_name = clean_terrain_name(value_str)

            # Try to format as terrain/location, but gracefully fall back to plain text
            try:
                return format_terrain_type(clean_name)
            except KeyError:
                # Not a terrain or location, return the original value as-is
                return value_str
        except ImportError:
            pass

        return str(value)

    def _update_button_states(self):
        # For circular navigation, buttons are always enabled if there are options
        can_navigate = len(self._allowed_values) > 1
        self.prev_button.setEnabled(can_navigate)
        self.next_button.setEnabled(can_navigate)

    def value(self) -> Any:
        if not self._allowed_values:  # Should ideally not happen
            return None
        return self._allowed_values[self._current_index]

    def setValue(self, new_value: Any):
        if not self._allowed_values:
            # If allowed_values is empty, we might want to update it
            # or handle this case based on expected behavior.
            # For now, if new_value is not None, make it the only option.
            if new_value is not None:
                self._allowed_values = [new_value]
                self._current_index = 0
                self._update_display_and_emit()
            else:  # new_value is None, and no allowed_values
                self.value_label.setText("")  # Or some placeholder
                self._update_button_states()  # Disables buttons
                self.valueChanged.emit(None)
            return

        if new_value in self._allowed_values:
            self._current_index = self._allowed_values.index(new_value)
            self._update_display_and_emit()
        elif new_value is None and self._allowed_values:  # Handle setting to None explicitly
            # This case might mean "no selection" or reset to default.
            # For now, let's reset to the first item if None is not an allowed value.
            # If None *is* an allowed value, the above `if new_value in self._allowed_values` handles it.
            self._current_index = 0  # Reset to first item
            self._update_display_and_emit()

    def clear(self):  # Reset to the first allowed value
        if not self._allowed_values:
            return
        self._current_index = 0
        self._update_display_and_emit()

    def text(self) -> str:  # For compatibility with QLineEdit if needed
        return str(self.value())

    def clear_options(self):  # Method to truly clear options and display
        self._allowed_values = []
        self._current_index = 0
        self.value_label.setText("")  # Or a placeholder like "N/A"
        self._update_button_states()  # Disables buttons
        self.valueChanged.emit(None)  # Emit that value is now None or invalid
