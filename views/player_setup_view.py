from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QHBoxLayout, QSpacerItem, QSizePolicy, QGridLayout,
                               QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QPalette, QColor
from constants import TERRAIN_TYPES
from help_text_model import HelpTextModel 
from components.carousel import CarouselInputWidget # Updated import

class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """
    # Emits (player_index, player_data_dict)
    player_data_finalized = Signal(int, dict)
    back_signal = Signal()
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
        
        # Main Grid Layout for all inputs
        main_grid_layout = QGridLayout()
        main_grid_layout.setContentsMargins(20, 20, 20, 10)
        main_grid_layout.setSpacing(10)

        # Player Name
        player_name_label = QLabel("Player Name:")
        self.name_input = QLineEdit()
        main_grid_layout.addWidget(player_name_label, 0, 0)
        main_grid_layout.addWidget(self.name_input, 0, 1, 1, 2) # Spans 2 columns

        # Home Terrain
        home_terrain_label = QLabel("Home Terrain:")
        self.home_terrain_carousel = CarouselInputWidget(allowed_values=TERRAIN_TYPES, initial_value=TERRAIN_TYPES[0])
        main_grid_layout.addWidget(home_terrain_label, 1, 0)
        main_grid_layout.addWidget(self.home_terrain_carousel, 1, 1, 1, 2) # Spans 2 columns

        # Proposed Frontier Terrain
        proposed_frontier_label = QLabel("Proposed Frontier Terrain:")
        self.frontier_terrain_carousel = CarouselInputWidget(allowed_values=TERRAIN_TYPES, initial_value=TERRAIN_TYPES[0])
        main_grid_layout.addWidget(proposed_frontier_label, 2, 0)
        main_grid_layout.addWidget(self.frontier_terrain_carousel, 2, 1, 1, 2) # Spans 2 columns

        # Home Army
        home_army_label = QLabel("Home Army:")
        self.home_army_name_input = QLineEdit()
        self.home_army_points_input = CarouselInputWidget(min_val=0, max_val=self.point_value, initial_value=0)
        main_grid_layout.addWidget(home_army_label, 3, 0)
        main_grid_layout.addWidget(QLabel("Name:"), 3, 1)
        main_grid_layout.addWidget(self.home_army_name_input, 3, 2)
        main_grid_layout.addWidget(QLabel("Points:"), 3, 3)
        main_grid_layout.addWidget(self.home_army_points_input, 3, 4)

        # Campaign Army
        campaign_army_label = QLabel("Campaign Army:")
        self.campaign_army_name_input = QLineEdit()
        self.campaign_army_points_input = CarouselInputWidget(min_val=0, max_val=self.point_value, initial_value=0)
        main_grid_layout.addWidget(campaign_army_label, 4, 0)
        main_grid_layout.addWidget(QLabel("Name:"), 4, 1)
        main_grid_layout.addWidget(self.campaign_army_name_input, 4, 2)
        main_grid_layout.addWidget(QLabel("Points:"), 4, 3)
        main_grid_layout.addWidget(self.campaign_army_points_input, 4, 4)

        # Horde Army (conditionally added)
        self.horde_army_label = QLabel("Horde Army:")
        self.horde_army_name_input = QLineEdit()
        self.horde_army_points_input = CarouselInputWidget(min_val=0, max_val=self.point_value, initial_value=0)
        self.horde_army_name_widget_label = QLabel("Name:") # Label for the name input field
        self.horde_army_points_widget_label = QLabel("Points:") # Label for the points input field
        
        main_grid_layout.addWidget(self.horde_army_label, 5, 0)
        main_grid_layout.addWidget(self.horde_army_name_widget_label, 5, 1)
        main_grid_layout.addWidget(self.horde_army_name_input, 5, 2)
        main_grid_layout.addWidget(self.horde_army_points_widget_label, 5, 3)
        main_grid_layout.addWidget(self.horde_army_points_input, 5, 4)

        if self.num_players > 1:
            self.horde_army_label.show()
            self.horde_army_name_widget_label.show()
            self.horde_army_name_input.show()
            self.horde_army_points_widget_label.show()
            self.horde_army_points_input.show()
        else:
            self.horde_army_label.hide()
            self.horde_army_name_widget_label.hide()
            self.horde_army_name_input.hide()
            self.horde_army_points_widget_label.hide()
            self.horde_army_points_input.hide()
        
        # Set column stretch factors for the main grid
        # Column 0 (labels like "Home Army:")
        main_grid_layout.setColumnStretch(0, 1) 
        # Column 1 (labels like "Name:")
        main_grid_layout.setColumnStretch(1, 0) # Minimal width for "Name:" / "Points:"
        # Column 2 (name input fields)
        main_grid_layout.setColumnStretch(2, 2) # More space for name inputs
        # Column 3 (labels like "Points:")
        main_grid_layout.setColumnStretch(3, 0) # Minimal width
        # Column 4 (points carousels)
        main_grid_layout.setColumnStretch(4, 1)

        layout.addLayout(main_grid_layout)

        self.status_label = QLabel("") # For validation messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Help Text Panel
        help_group_box = QGroupBox("Help")
        help_group_box.setMaximumHeight(int(self.height() * 0.3)) # Apply constraint to the GroupBox
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        help_layout.addWidget(self.help_text_edit)
        layout.addWidget(help_group_box)

        # Navigation buttons
        navigation_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next Player") # Text changes based on current player
        if self.num_players == 1:
            self.next_button.setText("Start Game")
        self.next_button.clicked.connect(self._handle_next_action)
        navigation_layout.addWidget(self.next_button)
        
        layout.addLayout(navigation_layout)


        self.setLayout(layout)
        self.update_for_player(self.current_player_index) # Initial setup for player 1

    def _handle_next_action(self):
        player_name = self.name_input.text().strip()
        if not player_name:
            self._set_status_message("Player Name cannot be empty.", "red")
            return

        try:
            home_pts = self.home_army_points_input.value()
            campaign_pts = self.campaign_army_points_input.value()
            horde_pts = 0
            if self.num_players > 1:
                horde_pts = self.horde_army_points_input.value()
        except AttributeError: # Should not happen if CarouselInputWidget is used
            self._set_status_message("Error reading army points.", "red")
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
            "home_terrain": self.home_terrain_carousel.value(),
            "home_army_name": self.home_army_name_input.text(),
            "home_army_points": home_pts,
            "campaign_army_name": self.campaign_army_name_input.text(),
            "campaign_army_points": campaign_pts,
            "frontier_terrain_proposal": self.frontier_terrain_carousel.value(),
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
        self.home_terrain_carousel.clear() # Resets to the first terrain
        self.home_army_name_input.clear()
        self.home_army_points_input.clear()
        self.campaign_army_name_input.clear()
        self.campaign_army_points_input.clear()
        if self.num_players > 1:
            self.horde_army_name_input.clear()
            self.horde_army_points_input.clear()
        self.frontier_terrain_carousel.clear() # Resets to the first terrain
        self._set_player_setup_help_text() # Update help text for the current player
        self._set_status_message("") # Clear status for new player
        self.name_input.setFocus() # Focus on the first input field

        if self.current_player_index == self.num_players - 1:
            self.next_button.setText("Start Game")
        else:
            self.next_button.setText("Next Player")