from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QRadioButton, QButtonGroup, QSizePolicy, QSpacerItem, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot

from models.help_text_model import HelpTextModel

class WelcomeView(QWidget):
    """
    The Welcome Screen view.
    Allows selection of number of players and point value.
    """
    # Define signals for interactions
    proceed_signal = Signal()
    player_count_selected_signal = Signal(int) # Emits the selected player count (int)
    point_value_selected_signal = Signal(int) # Emits the selected point value (int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_model = HelpTextModel()
        self.setWindowTitle("Welcome Screen")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Welcome Title
        title_label = QLabel("Welcome to Dragon Dice Companion (PySide6)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Middle Section (Selections and Info Panel)
        middle_section_layout = QHBoxLayout()

        # Left Side (Selections)
        selections_group = QGroupBox() # Using QGroupBox to visually group selections
        selections_layout = QVBoxLayout(selections_group)

        # Player Count Selection
        player_count_group = QGroupBox("Select Number of Players:")
        player_count_hbox = QHBoxLayout()
        self.player_count_button_group = QButtonGroup(self)
        player_counts = [2, 3, 4]
        for count in player_counts:
            radio_button = QRadioButton(str(count))
            self.player_count_button_group.addButton(radio_button, count) # Use count as the ID
            player_count_hbox.addWidget(radio_button)
            if count == 2: # Default selection
                radio_button.setChecked(True)
        player_count_group.setLayout(player_count_hbox)
        # Connect to the signal that emits an integer ID
        self.player_count_button_group.idClicked.connect(self.player_count_selected_signal.emit)
        selections_layout.addWidget(player_count_group)

        # Point Value Selection
        point_value_group = QGroupBox("Select Army Point Value:")
        point_value_hbox = QHBoxLayout()
        self.point_value_button_group = QButtonGroup(self)
        point_values = [15, 24, 30, 36, 60]
        for pv in point_values:
            radio_button = QRadioButton(str(pv))
            self.point_value_button_group.addButton(radio_button, pv) # Use pv as the ID
            point_value_hbox.addWidget(radio_button)
            if pv == 30: # Default selection (or choose another)
                radio_button.setChecked(True)
        point_value_group.setLayout(point_value_hbox)
        # Connect to the signal that emits an integer ID
        self.point_value_button_group.idClicked.connect(self.point_value_selected_signal.emit)
        selections_layout.addWidget(point_value_group)

        middle_section_layout.addWidget(selections_group)

        # Right Side (Info Panel)
        help_group_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self._set_welcome_help_text()
        help_layout.addWidget(self.help_text_edit)
        middle_section_layout.addWidget(help_group_box, 1) # Add stretch factor

        main_layout.addLayout(middle_section_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Proceed Button
        self.proceed_button = QPushButton("Proceed to Player Setup")
        self.proceed_button.clicked.connect(self.proceed_signal.emit)
        main_layout.addWidget(self.proceed_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        # Emit initial default selections after layout is set up
        self.emit_current_selections()

    def emit_current_selections(self):
        """Emits the currently selected values for player count and point value."""
        selected_player_button = self.player_count_button_group.checkedButton()
        if selected_player_button:
            self.player_count_selected_signal.emit(self.player_count_button_group.id(selected_player_button))
        else: # Default if somehow none are checked (should be handled by default check)
            # Emit the ID of the first button added (which is the value itself)
            if self.player_count_button_group.buttons(): # Ensure buttons exist
                self.player_count_selected_signal.emit(self.player_count_button_group.buttons()[0].group().id(self.player_count_button_group.buttons()[0]))

        selected_point_button = self.point_value_button_group.checkedButton()
        if selected_point_button:
            self.point_value_selected_signal.emit(self.point_value_button_group.id(selected_point_button))
        else: # Default
            # Emit the ID of the first button added
            if self.point_value_button_group.buttons(): # Ensure buttons exist
                self.point_value_selected_signal.emit(self.point_value_button_group.buttons()[0].group().id(self.point_value_button_group.buttons()[0]))

    def _set_welcome_help_text(self):
        self.help_text_edit.setHtml(self.help_model.get_welcome_help())

