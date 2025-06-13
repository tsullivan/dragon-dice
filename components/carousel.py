from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from typing import List, Any, Union, Optional

class CarouselInputWidget(QWidget):
    valueChanged = Signal(object) # Can emit int or str

    def __init__(self, allowed_values: Optional[List[Any]] = None, min_val: int = 0, max_val: int = 10, step: int = 1, initial_value: Any = None, parent=None):
        super().__init__(parent)
        
        if allowed_values is not None:
            # Keep original type, just ensure uniqueness and sort if they are sortable
            # For terrains, sorting might be alphabetical by default if they are strings
            temp_values = []
            seen_hashable_representations = set()
            for original_item in allowed_values:
                # Create a hashable representation for uniqueness checking
                # Specifically for items like ('Name', [list_of_elements])
                if isinstance(original_item, tuple) and len(original_item) > 0 and any(isinstance(el, list) for el in original_item):
                    hashable_item = tuple(tuple(el) if isinstance(el, list) else el for el in original_item)
                else:
                    hashable_item = original_item # Assume it's already hashable or a primitive type

                if hashable_item not in seen_hashable_representations:
                   temp_values.append(original_item) # Store the original item
                   seen_hashable_representations.add(hashable_item)
            try: # Try sorting, will work for numbers and strings
                self._allowed_values = sorted(temp_values)
            except TypeError: # If values are not sortable (e.g. mixed types, though not expected here)
                self._allowed_values = temp_values
        else:
            self._allowed_values = list(range(min_val, max_val + 1, step))

        if not self._allowed_values:
            self._allowed_values = [0] # Default for numeric if empty

        self._current_index = 0
        
        # Determine initial index
        current_val_to_set = self._allowed_values[0] # Default to first value
        if initial_value is not None:
            if initial_value in self._allowed_values:
                self._current_index = self._allowed_values.index(initial_value)
                current_val_to_set = initial_value

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0) 

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
        if self._current_index > 0:
            self._current_index -= 1
            self._update_display_and_emit()

    def _next_value(self):
        if self._current_index < len(self._allowed_values) - 1:
            self._current_index += 1
            self._update_display_and_emit()

    def _update_display_and_emit(self):
        current_val = self._allowed_values[self._current_index]
        self.value_label.setText(str(current_val))
        self._update_button_states()
        self.valueChanged.emit(current_val)

    def _update_button_states(self):
        self.prev_button.setEnabled(self._current_index > 0)
        self.next_button.setEnabled(self._current_index < len(self._allowed_values) - 1)

    def value(self) -> Any:
        return self._allowed_values[self._current_index]

    def setValue(self, new_value: Any):
        if new_value in self._allowed_values:
            self._current_index = self._allowed_values.index(new_value)
            self._update_display_and_emit()

    def clear(self): # Reset to the first allowed value
        self._current_index = 0
        self._update_display_and_emit()

    def text(self) -> str: # For compatibility with QLineEdit if needed
        return str(self.value())
