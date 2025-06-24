from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal, Slot

from models.help_text_model import HelpTextModel
from components.tabbed_view_widget import TabbedViewWidget
import constants


class WelcomeView(QWidget):
    """
    The Welcome Screen view.
    Allows selection of number of players and point value.
    """

    proceed_signal = Signal()
    # Emits the selected player count (int)
    player_count_selected_signal = Signal(int)
    # Emits the selected force size (int)
    force_size_selected_signal = Signal(int)

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

        # Tabbed Interface (Game and Help)
        self.tabbed_widget = TabbedViewWidget()

        # Game Tab Content (Selections)
        selections_group = QGroupBox()
        selections_layout = QVBoxLayout(selections_group)

        # Player Count Selection
        player_count_group = QGroupBox("Select Number of Players:")
        player_count_hbox = QHBoxLayout()
        self.player_count_button_group = QButtonGroup(self)
        player_counts = [2, 3, 4]
        for count in player_counts:
            radio_button = QRadioButton(str(count))
            self.player_count_button_group.addButton(radio_button, count)
            player_count_hbox.addWidget(radio_button)
            if count == 2:
                radio_button.setChecked(True)
        player_count_group.setLayout(player_count_hbox)
        self.player_count_button_group.idClicked.connect(
            self.player_count_selected_signal.emit
        )
        selections_layout.addWidget(player_count_group)

        # Force Size Selection
        force_size_group = QGroupBox("Select Total Force Size:")
        force_size_hbox = QHBoxLayout()
        self.force_size_button_group = QButtonGroup(self)
        for size in constants.FORCE_SIZE_OPTIONS:
            # Calculate required dragons for display
            required_dragons = constants.calculate_required_dragons(size)
            radio_button = QRadioButton(
                f"{size} pts ({required_dragons} dragon{
                                        's' if required_dragons > 1 else ''})"
            )
            self.force_size_button_group.addButton(radio_button, size)
            force_size_hbox.addWidget(radio_button)
            if size == constants.DEFAULT_FORCE_SIZE:
                radio_button.setChecked(True)
        force_size_group.setLayout(force_size_hbox)
        self.force_size_button_group.idClicked.connect(
            self.force_size_selected_signal.emit
        )
        selections_layout.addWidget(force_size_group)

        # Add selections to Game tab
        self.tabbed_widget.add_game_content(selections_group)

        # Set help content for Help tab
        self._set_welcome_help_text()

        main_layout.addWidget(self.tabbed_widget)
        main_layout.addSpacerItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # Proceed Button
        self.proceed_button = QPushButton("Proceed to Player Setup")
        self.proceed_button.setMaximumWidth(220)  # Limit button width
        self.proceed_button.clicked.connect(self.proceed_signal.emit)
        main_layout.addWidget(self.proceed_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        self.emit_current_selections()

    def emit_current_selections(self):
        """Emits the currently selected values for player count and force size."""
        # Emit player count
        selected_player_button = self.player_count_button_group.checkedButton()
        if selected_player_button:
            self.player_count_selected_signal.emit(
                self.player_count_button_group.id(selected_player_button)
            )
        else:
            if self.player_count_button_group.buttons():
                self.player_count_selected_signal.emit(
                    self.player_count_button_group.id(
                        self.player_count_button_group.buttons()[0]
                    )
                )

        # Emit force size
        selected_force_button = self.force_size_button_group.checkedButton()
        if selected_force_button:
            self.force_size_selected_signal.emit(
                self.force_size_button_group.id(selected_force_button)
            )
        else:
            if self.force_size_button_group.buttons():
                self.force_size_selected_signal.emit(constants.DEFAULT_FORCE_SIZE)

    def _set_welcome_help_text(self):
        self.tabbed_widget.set_help_text(self.help_model.get_welcome_help())
