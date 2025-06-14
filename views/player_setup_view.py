from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QGroupBox, QGridLayout, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette, QColor
import random
import os

from components.carousel import CarouselInputWidget
from models.help_text_model import HelpTextModel
from constants import TERRAIN_DATA # For default terrain options

class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """
    # Emits (player_index, player_data_dict)
    player_data_finalized = Signal(int, dict)
    back_signal = Signal()

    def __init__(self, num_players: int,
                 point_value: int,
                 terrain_display_options: list, # List of tuples (name, colors)
                 required_dragons: int,
                 parent=None,
                 current_player_index: int = 0):
        super().__init__(parent)
        self.num_players = num_players
        self.point_value = point_value
        self.terrain_display_options = terrain_display_options
        # Extract just names for carousel if terrain_display_options contains more complex data
        if self.terrain_display_options and isinstance(self.terrain_display_options[0], tuple):
            self.all_terrain_options = [name for name, _ in self.terrain_display_options]
        else:
            self.all_terrain_options = self.terrain_display_options # Assume it's already a list of names
            
        self.required_dragons = required_dragons
        self.help_model = HelpTextModel()
        self.current_player_index = current_player_index

        self.preselected_names = self._load_preselected_names()

        self.player_data = {} # To store data for the current player
        self.setWindowTitle(f"Player {self.current_player_index + 1} Setup")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title
        self.title_label = QLabel(f"Player {self.current_player_index + 1} Setup")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        main_layout.addWidget(self.title_label)

        # Informational text for required dragons
        self.dragon_info_label = QLabel(f"Reminder: You must bring {self.required_dragons} dragon(s) to this game (1 per 24 points or part thereof).")
        dragon_font = self.dragon_info_label.font()
        dragon_font.setPointSize(dragon_font.pointSize() - 2) # Slightly smaller
        self.dragon_info_label.setFont(dragon_font)
        main_layout.addWidget(self.dragon_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Middle Section (Inputs and Help Panel)
        middle_section_layout = QHBoxLayout()

        # Left Side (Inputs Table)
        inputs_group = QGroupBox(f"Setup for Player {self.current_player_index + 1}")
        inputs_grid_layout = QGridLayout(inputs_group)
        inputs_grid_layout.setContentsMargins(10, 10, 10, 10)
        inputs_grid_layout.setSpacing(10)


        # Row 0: Player Name
        player_name_label = QLabel("Player Name:")
        self.player_name_input = QLineEdit()
        self.player_name_input.setMinimumWidth(200) # Give it some base width
        self.player_name_input.setPlaceholderText(f"Player {self.current_player_index + 1} Name")
        self.random_player_name_button = QPushButton("🎲")
        self.random_player_name_button.setToolTip("Set a random player name")
        self.random_player_name_button.clicked.connect(self._set_random_player_name)
        player_name_layout = QHBoxLayout()
        player_name_layout.addWidget(self.player_name_input, 1) # QLineEdit takes expanding space
        player_name_layout.addWidget(self.random_player_name_button)
        inputs_grid_layout.addWidget(player_name_label, 0, 0)
        inputs_grid_layout.addLayout(player_name_layout, 0, 1, 1, 4)

        # Row 1: Home Terrain
        home_terrain_label = QLabel("Home Terrain:")
        self.home_terrain_carousel = CarouselInputWidget(allowed_values=self.all_terrain_options, initial_value=self.all_terrain_options[0] if self.all_terrain_options else None)
        inputs_grid_layout.addWidget(home_terrain_label, 1, 0)
        inputs_grid_layout.addWidget(self.home_terrain_carousel, 1, 1, 1, 4)

        # Row 2: Proposed Frontier Terrain
        proposed_terrain_label = QLabel("Proposed Frontier Terrain:")
        self.proposed_terrain_carousel = CarouselInputWidget(allowed_values=self.all_terrain_options, initial_value=self.all_terrain_options[0] if self.all_terrain_options else None)
        inputs_grid_layout.addWidget(proposed_terrain_label, 2, 0)
        inputs_grid_layout.addWidget(self.proposed_terrain_carousel, 2, 1, 1, 4)

        # Army Setups
        army_types = ["Home", "Campaign", "Horde"]
        self.army_name_inputs = {}
        self.army_points_carousels = {}
        self.army_labels = {} # To store labels for show/hide
        self.army_name_widget_labels = {}
        self.army_points_widget_labels = {}
        self.random_army_name_buttons = {}

        army_points_allowed = list(range(0, self.point_value + 1))

        for i, army_type in enumerate(army_types):
            row = 3 + i
            army_label = QLabel(f"{army_type} Army:")
            self.army_labels[army_type] = army_label
            inputs_grid_layout.addWidget(army_label, row, 0)

            name_widget_label = QLabel("Name:")
            self.army_name_widget_labels[army_type] = name_widget_label
            name_input = QLineEdit(army_type)
            name_input.setMinimumWidth(150) # Give it some base width
            self.army_name_inputs[army_type] = name_input

            random_button = QPushButton("🎲")
            random_button.setToolTip(f"Set a random name for {army_type} Army")
            random_button.clicked.connect(lambda checked, le=name_input: self._set_random_army_name_for_input(le))
            self.random_army_name_buttons[army_type] = random_button
            army_name_field_layout = QHBoxLayout()
            army_name_field_layout.addWidget(name_input, 1)
            army_name_field_layout.addWidget(random_button)
            inputs_grid_layout.addWidget(name_widget_label, row, 1, alignment=Qt.AlignmentFlag.AlignRight)
            inputs_grid_layout.addLayout(army_name_field_layout, row, 2)

            points_widget_label = QLabel("Points:")
            self.army_points_widget_labels[army_type] = points_widget_label
            points_carousel = CarouselInputWidget(allowed_values=army_points_allowed, initial_value=0)
            self.army_points_carousels[army_type] = points_carousel
            inputs_grid_layout.addWidget(points_widget_label, row, 3, alignment=Qt.AlignmentFlag.AlignRight)
            inputs_grid_layout.addWidget(points_carousel, row, 4)

        # Set column stretch factors for better spacing
        inputs_grid_layout.setColumnStretch(0, 1) # Label column
        inputs_grid_layout.setColumnStretch(1, 0) # "Name:" label
        inputs_grid_layout.setColumnStretch(2, 2) # Name input
        inputs_grid_layout.setColumnStretch(3, 0) # "Points:" label
        inputs_grid_layout.setColumnStretch(4, 1) # Points carousel

        middle_section_layout.addWidget(inputs_group)

        # Right Side (Help Panel)
        help_group_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group_box)
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setStyleSheet("ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; } li { margin-bottom: 3px; }")
        help_layout.addWidget(self.help_text_edit)
        middle_section_layout.addWidget(help_group_box, 1) # Add stretch factor

        main_layout.addLayout(middle_section_layout)

        self.status_label = QLabel("") # For validation messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        # Navigation Buttons
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_signal.emit)
        navigation_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next Player")
        self.next_button.clicked.connect(self._handle_next_action)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

        # Connect signals for live validation
        self.player_name_input.textChanged.connect(self._validate_and_update_button_state)
        for army_type in army_types:
            self.army_name_inputs[army_type].textChanged.connect(self._validate_and_update_button_state)
            self.army_points_carousels[army_type].valueChanged.connect(self._validate_and_update_button_state)

        self.update_for_player(self.current_player_index) # Initial setup for player 1

    def _load_preselected_names(self):
        names_by_category = {"Player": [], "Army": []}
        current_category = None
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            names_file_path = os.path.join(project_root, "names.txt")
            with open(names_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        category = line[1:-1]
                        if category in names_by_category:
                            current_category = category
                        else:
                            current_category = None # Unknown category
                            print(f"Warning: Unknown category '{category}' in names.txt.")
                    elif current_category:
                        names_by_category[current_category].append(line)
            
            if not names_by_category["Player"] and not names_by_category["Army"]:
                print("Warning: names.txt does not contain valid [Player] or [Army] names.")
            elif not names_by_category["Player"]:
                print("Warning: No names found under [Player] category in names.txt.")
            elif not names_by_category["Army"]:
                print("Warning: No names found under [Army] category in names.txt.")
        except FileNotFoundError:
            print(f"Warning: names.txt not found at {names_file_path}. Random name feature will be limited.")
        return names_by_category

    def _set_random_player_name(self):
        if self.preselected_names.get("Player"):
            self.player_name_input.setText(random.choice(self.preselected_names["Player"]))

    def _set_random_army_name_for_input(self, line_edit_widget: QLineEdit):
        if self.preselected_names.get("Army"):
            line_edit_widget.setText(random.choice(self.preselected_names["Army"]))

    def _handle_next_action(self):
        if not self._validate_inputs():
            self.next_button.setEnabled(False) # Ensure button is disabled if validation fails
            return

        player_name = self.player_name_input.text().strip()
        home_terrain_val = self.home_terrain_carousel.value()
        frontier_proposal_val = self.proposed_terrain_carousel.value()

        player_data = {
            "player_index": self.current_player_index,
            "name": player_name,
            "home_terrain": home_terrain_val,
            "frontier_terrain_proposal": frontier_proposal_val,
            "armies": {}
        }
        for army_type in self.army_name_inputs.keys():
            if army_type == "Horde" and self.num_players <= 1: # Skip Horde for 1 player
                continue
            army_name = self.army_name_inputs[army_type].text().strip()
            army_points = self.army_points_carousels[army_type].value()
            player_data["armies"][army_type.lower()] = {"name": army_name, "points": army_points}

        self.player_data_finalized.emit(self.current_player_index, player_data)
        self.current_player_index += 1
        if self.current_player_index < self.num_players:
            self.update_for_player(self.current_player_index)
        # If all players are done, the MainWindow will handle the transition
        # based on the signal from AppDataModel.

    def _set_status_message(self, message, color_name="black"):
        self.status_label.setText(message)
        palette = self.status_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color_name))
        self.status_label.setPalette(palette)

    def _validate_inputs(self) -> bool:
        player_name = self.player_name_input.text().strip()
        if not player_name:
            self._set_status_message("Player Name cannot be empty.", "red")
            return False

        total_allocated_points = 0
        armies_to_validate = ["Home", "Campaign"]
        if self.num_players > 1:
            armies_to_validate.append("Horde")

        for army_type in armies_to_validate:
            army_name = self.army_name_inputs[army_type].text().strip()
            if not army_name:
                self._set_status_message(f"{army_type} Army Name cannot be empty.", "red")
                return False
            army_points = self.army_points_carousels[army_type].value()
            total_allocated_points += army_points

        if total_allocated_points != self.point_value:
            self._set_status_message(f"Total points ({total_allocated_points}) must equal game limit ({self.point_value}).", "red")
            return False

        # Rule: Each army must have at least one unit (which costs at least 1 point).
        # This rule is complex as "1 unit" isn't directly tied to points here.
        # For now, we'll assume any non-zero point value implies units.
        # A more detailed validation would require knowledge of unit costs.
        for army_type in armies_to_validate:
            army_points = self.army_points_carousels[army_type].value()
            if army_points == 0: # Or some other minimum if defined
                 # Allow 0 points for an army if the total points are met by other armies.
                 # This rule might need refinement based on game rules for "bringing" an army.
                 pass # For now, allow 0 points if total is met.
                 # self._set_status_message(f"{army_type} Army must have points allocated.", "red")
                 # return False

        # Max per army rule (e.g., point_value / 2) - if applicable
        # max_per_army = self.point_value // 2
        # for army_type in armies_to_validate:
        #     army_points = self.army_points_carousels[army_type].value()
        #     if army_points > max_per_army:
        #         self._set_status_message(f"{army_type} points ({army_points}) exceed max per army ({max_per_army}).", "red")
        #         return False

        self._set_status_message("Inputs valid.", "green")
        return True

    def _set_player_setup_help_text(self):
        player_num_for_display = self.current_player_index + 1
        self.help_text_edit.setHtml(
            self.help_model.get_player_setup_help(
                player_num_for_display, self.num_players, self.point_value
            )
        )

    def _validate_and_update_button_state(self):
        is_valid = self._validate_inputs()
        self.next_button.setEnabled(is_valid)

    def update_for_player(self, player_index):
        self.current_player_index = player_index
        self.title_label.setText(f"Player {self.current_player_index + 1} Setup")
        self.player_name_input.clear()
        self.player_name_input.setPlaceholderText(f"Player {self.current_player_index + 1} Name")

        if self.all_terrain_options:
            self.home_terrain_carousel.setValue(self.all_terrain_options[0])
            self.proposed_terrain_carousel.setValue(self.all_terrain_options[0])
        else:
            self.home_terrain_carousel.clear()
            self.proposed_terrain_carousel.clear()

        self.army_name_inputs["Home"].setText("Home")
        self.army_points_carousels["Home"].setValue(0)
        self.army_name_inputs["Campaign"].setText("Campaign")
        self.army_points_carousels["Campaign"].setValue(0)

        show_horde = self.num_players > 1
        self.army_labels["Horde"].setVisible(show_horde)
        self.army_name_widget_labels["Horde"].setVisible(show_horde)
        self.army_name_inputs["Horde"].setVisible(show_horde)
        self.army_points_widget_labels["Horde"].setVisible(show_horde)
        self.army_points_carousels["Horde"].setVisible(show_horde)
        if show_horde:
            self.random_army_name_buttons["Horde"].setVisible(show_horde)
            self.army_name_inputs["Horde"].setText("Horde")
            self.army_points_carousels["Horde"].setValue(0)


        self._set_player_setup_help_text()
        self._set_status_message("")
        self.player_name_input.setFocus()
        self._validate_and_update_button_state()

        if self.current_player_index == self.num_players - 1:
            self.next_button.setText("Finalize Setup & Start Game")
        else:
            self.next_button.setText(f"Next Player ({self.current_player_index + 2}/{self.num_players})")
