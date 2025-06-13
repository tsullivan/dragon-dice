from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QTextEdit, QGroupBox, QButtonGroup, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal

from help_text_model import HelpTextModel
class WelcomeView(QWidget):
    """
    The Welcome Screen view.
    Allows selection of number of players and point value.
    """
    # Define signals for interactions
    proceed_signal = Signal()
    player_count_selected_signal = Signal(int)
    point_value_selected_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_model = HelpTextModel()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Welcome to Dragon Dice Companion (PySide6)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Consider using QFont for styling
        layout.addWidget(title_label)
        font = title_label.font()
        font.setPointSize(24) # Example: Make title larger
        title_label.setFont(font)

        # Player count selection with buttons
        layout.addWidget(QLabel("Select Number of Players:"))
        player_count_layout = QHBoxLayout()
        self.player_counts = {"2 Players": 2, "3 Players": 3, "4 Players": 4}
        self.player_count_button_group = QButtonGroup(self)
        self.player_count_buttons = {}
        for text, count in self.player_counts.items():
            button = QPushButton(text)
            button.setCheckable(True)
            player_count_layout.addWidget(button)
            self.player_count_button_group.addButton(button, count)
            self.player_count_buttons[count] = button
        # Connect to the signal that emits an integer ID
        self.player_count_button_group.idClicked.connect(self.player_count_selected_signal.emit)
        layout.addLayout(player_count_layout)

        # Point value selection with buttons
        layout.addWidget(QLabel("Select Army Point Value:"))
        point_value_layout = QHBoxLayout()
        self.point_values = {
            "15 Points": 15,
            "24 Points": 24,
            "30 Points": 30,
            "36 Points": 36,
            "60 Points": 60
        }
        self.point_value_button_group = QButtonGroup(self)
        self.point_value_buttons = {}
        for text, value in self.point_values.items():
            button = QPushButton(text)
            button.setCheckable(True)
            point_value_layout.addWidget(button)
            self.point_value_button_group.addButton(button, value)
            self.point_value_buttons[value] = button
        # Connect to the signal that emits an integer ID
        self.point_value_button_group.idClicked.connect(self.point_value_selected_signal.emit)
        layout.addLayout(point_value_layout)

        # Set default selections for buttons
        if self.player_count_buttons:
            # Select "2 Players" by default
            first_player_count_val = list(self.player_counts.values())[0]
            self.player_count_buttons[first_player_count_val].setChecked(True)
        if self.point_value_buttons:
            # Select "15 Points" by default
            first_point_val = list(self.point_values.values())[0]
            self.point_value_buttons[first_point_val].setChecked(True)

        # Spacer to push help text and proceed button down
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_group_box.setMaximumHeight(int(self.screen().geometry().height() * 0.6))
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self._set_welcome_help_text()
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)
        
        proceed_button = QPushButton("Proceed to Player Setup")
        proceed_button.clicked.connect(self.proceed_signal.emit) # Emit the signal
        layout.addWidget(proceed_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _set_welcome_help_text(self):
        self.help_text_edit.setHtml(self.help_model.get_welcome_help())

    def emit_current_selections(self):
        """Emits the currently selected values. Useful for initialization."""
        selected_player_button = self.player_count_button_group.checkedButton()
        if selected_player_button:
            self.player_count_selected_signal.emit(self.player_count_button_group.id(selected_player_button))
        else: # Default if somehow none are checked (should be handled by default check)
            self.player_count_selected_signal.emit(list(self.player_counts.values())[0])
            
        selected_point_button = self.point_value_button_group.checkedButton()
        if selected_point_button:
            self.point_value_selected_signal.emit(self.point_value_button_group.id(selected_point_button))
        else: # Default
            self.point_value_selected_signal.emit(list(self.point_values.values())[0])
