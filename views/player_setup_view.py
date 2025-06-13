from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QHBoxLayout, QComboBox, QFormLayout, QSpacerItem, QSizePolicy,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QPalette, QColor
from constants import TERRAIN_TYPES
from help_text_model import HelpTextModel

class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """
    # Emits (player_index, player_data_dict)
    player_data_finalized = Signal(int, dict)
    # No longer needed here, AppDataModel will signal completion
    # all_setups_complete_signal = Signal()


    def __init__(self, num_players, point_value, parent=None): # TODO: Add current_player_index etc. as params
        super().__init__(parent)
        self.num_players = num_players
        self.point_value = point_value
        self.help_model = HelpTextModel()
        self.current_player_index = 0 # Start with the first player

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.title_label = QLabel(f"Player {self.current_player_index + 1} Setup")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24) # Example: Make title larger
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        # Player Name
        self.name_input = QLineEdit()
        form_layout.addRow("Player Name:", self.name_input)

        # Home Terrain
        self.home_terrain_combo = QComboBox()
        self.home_terrain_combo.addItems(TERRAIN_TYPES)
        form_layout.addRow("Home Terrain:", self.home_terrain_combo)

        # Validators for points
        points_validator = QIntValidator(0, self.point_value, self) # Max points for any single field can be total game points

        # Army Details
        self.home_army_name_input = QLineEdit()
        self.home_army_points_input = QLineEdit()
        self.home_army_points_input.setValidator(points_validator)
        form_layout.addRow("Home Army Name:", self.home_army_name_input)
        form_layout.addRow("Home Army Points:", self.home_army_points_input)

        self.campaign_army_name_input = QLineEdit()
        self.campaign_army_points_input = QLineEdit()
        self.campaign_army_points_input.setValidator(points_validator)
        form_layout.addRow("Campaign Army Name:", self.campaign_army_name_input)
        form_layout.addRow("Campaign Army Points:", self.campaign_army_points_input)

        self.horde_army_name_input = QLineEdit()
        self.horde_army_points_input = QLineEdit()
        self.horde_army_points_input.setValidator(points_validator)
        self.horde_army_name_label = QLabel("Horde Army Name:")
        self.horde_army_points_label = QLabel("Horde Army Points:")

        # Connect textChanged signals for live point validation feedback (optional)
        # self.home_army_points_input.textChanged.connect(self._update_status_label)
        # self.campaign_army_points_input.textChanged.connect(self._update_status_label)
        # self.horde_army_points_input.textChanged.connect(self._update_status_label)


        if self.num_players > 1:
            form_layout.addRow(self.horde_army_name_label, self.horde_army_name_input)
            form_layout.addRow(self.horde_army_points_label, self.horde_army_points_input)
        else:
            self.horde_army_name_label.hide()
            self.horde_army_name_input.hide()
            self.horde_army_points_label.hide()
            self.horde_army_points_input.hide()

        # Frontier Terrain Proposal
        self.frontier_terrain_combo = QComboBox()
        self.frontier_terrain_combo.addItems(TERRAIN_TYPES)
        form_layout.addRow("Propose Frontier Terrain:", self.frontier_terrain_combo)

        layout.addLayout(form_layout)

        self.status_label = QLabel("") # For validation messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setFixedHeight(200) # Adjust height as needed
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)



        self.next_button = QPushButton("Next Player") # Text changes based on current player
        if self.num_players == 1:
            self.next_button.setText("Start Game")
        self.next_button.clicked.connect(self._handle_next_action)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.update_for_player(self.current_player_index) # Initial setup for player 1

    def _handle_next_action(self):
        player_name = self.name_input.text().strip()
        if not player_name:
            self._set_status_message("Player Name cannot be empty.", "red")
            return

        try:
            home_pts_str = self.home_army_points_input.text() or "0"
            campaign_pts_str = self.campaign_army_points_input.text() or "0"
            horde_pts_str = self.horde_army_points_input.text() or "0"

            home_pts = int(home_pts_str)
            campaign_pts = int(campaign_pts_str)
            horde_pts = 0
            if self.num_players > 1:
                horde_pts = int(horde_pts_str)

        except ValueError:
            self._set_status_message("Army points must be valid numbers.", "red")
            return

        total_allocated_points = home_pts + campaign_pts + horde_pts
        max_per_army = self.point_value // 2

        if total_allocated_points > self.point_value:
            self._set_status_message(f"Total points ({total_allocated_points}) exceed limit ({self.point_value}).", "red")
            return
        
        army_checks = [
            ("Home Army", home_pts),
            ("Campaign Army", campaign_pts)
        ]
        if self.num_players > 1:
            army_checks.append(("Horde Army", horde_pts))

        for army_name, army_points in army_checks:
            if army_points > max_per_army:
                self._set_status_message(f"{army_name} points ({army_points}) exceed max per army ({max_per_army}).", "red")
                return

        self._set_status_message("", "green") # Clear status on success

        player_data = {
            "name": player_name,
            "home_terrain": self.home_terrain_combo.currentText(),
            "home_army_name": self.home_army_name_input.text(),
            "home_army_points": home_pts,
            "campaign_army_name": self.campaign_army_name_input.text(),
            "campaign_army_points": campaign_pts,
            "frontier_terrain_proposal": self.frontier_terrain_combo.currentText(),
        }
        if self.num_players > 1:
            player_data["horde_army_name"] = self.horde_army_name_input.text()
            player_data["horde_army_points"] = horde_pts

        self.player_data_finalized.emit(self.current_player_index, player_data)
        self.current_player_index += 1
        if self.current_player_index < self.num_players:
            self.update_for_player(self.current_player_index)
        # else:
            # The AppDataModel will now emit all_player_setups_complete
            # self.all_setups_complete_signal.emit()
            # self.next_button.setEnabled(False) # Disable button after all setups

    def _set_status_message(self, message, color_name="black"):
        self.status_label.setText(message)
        palette = self.status_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color_name))
        self.status_label.setPalette(palette)

    # def _update_status_label(self):
        # This method could be used for live feedback on points.
        # For now, validation happens on button click.
        # self._set_status_message(f"Points: ... / {self.point_value}", "blue")

    def _set_player_setup_help_text(self):
        player_num = self.current_player_index + 1
        self.help_text_edit.setHtml(
            self.help_model.get_player_setup_help(
                player_num, self.num_players, self.point_value
            )
        )

    def update_for_player(self, player_index):
        self.current_player_index = player_index
        self.title_label.setText(f"Player {self.current_player_index + 1} Setup")
        self.name_input.clear()
        self.home_terrain_combo.setCurrentIndex(0)
        self.home_army_name_input.clear()
        self.home_army_points_input.clear()
        self.campaign_army_name_input.clear()
        self.campaign_army_points_input.clear()
        if self.num_players > 1:
            self.horde_army_name_input.clear()
            self.horde_army_points_input.clear()
        self.frontier_terrain_combo.setCurrentIndex(0)
        self._set_player_setup_help_text() # Update help text for the current player
        self._set_status_message("") # Clear status for new player
        self.name_input.setFocus() # Focus on the first input field

        if self.current_player_index == self.num_players - 1:
            self.next_button.setText("Start Game")
        else:
            self.next_button.setText("Next Player")