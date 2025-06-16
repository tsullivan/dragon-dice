# views/player_setup_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QGroupBox, QGridLayout, QTextEdit,
                               QComboBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette, QColor
import random
import os
from typing import Optional # Import Optional

from components.army_setup_widget import ArmySetupWidget
from components.carousel import CarouselInputWidget
from components.player_identity_widget import PlayerIdentityWidget
from components.terrain_selection_widget import TerrainSelectionWidget # Import new widget
from components.help_panel_widget import HelpPanelWidget
from views.unit_selection_dialog import UnitSelectionDialog # Import the dialog
from models.help_text_model import HelpTextModel
from models.unit_roster_model import UnitRosterModel # Import UnitRosterModel
from models.unit_model import UnitModel # Import UnitModel
import constants # Import constants for AVAILABLE_DRAGON_TYPES

class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """
    # Emits (player_index, player_data_dict)
    player_data_finalized = Signal(int, dict)
    back_signal = Signal(int) # Emit the current player index

    def __init__(self, num_players: int,
                 point_value: int,
                 terrain_display_options: list, # List of tuples (name, colors)
                 required_dragons: int,
                 initial_player_data: Optional[dict] = None, # New parameter to accept pre-filled data
                 parent=None,
                 current_player_index: int = 0):
        super().__init__(parent)
        self.num_players = num_players
        self.initial_player_data = initial_player_data
        self.point_value = point_value
        self.terrain_display_options = terrain_display_options
        # Extract just names for combo box if terrain_display_options contains more complex data
        if self.terrain_display_options and isinstance(self.terrain_display_options[0], tuple):
            self.all_terrain_options = [name for name, _ in self.terrain_display_options]
        else:
            self.all_terrain_options = self.terrain_display_options # Assume it's already a list of names
            
        self.required_dragons = required_dragons
        self.unit_roster = UnitRosterModel() # Instantiate the roster
        self.help_model = HelpTextModel()
        self.current_player_index = current_player_index

        self.max_points_per_army = self.point_value // 2
        self.preselected_names = self._load_preselected_names()

        self.player_data: dict = {} # To store data for the current player
        self.army_units_data: dict[str, list[dict]] = {} # {army_type: list of unit dicts}
        self.army_detailed_units_labels: dict[str, QLabel] = {} # {army_type: QLabel for detailed unit list}
        # self.army_dragon_dice_inputs: dict[str, QLineEdit] = {} # Removed
        self.dragon_selection_carousels: list[CarouselInputWidget] = []
        self.setWindowTitle(f"Player {self.current_player_index + 1} Setup")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title and Global Randomize Button
        title_layout = QHBoxLayout()
        title_layout.addStretch(1) # Add stretch to push title and button towards center/right
        self.title_label = QLabel(f"Player {self.current_player_index + 1} Setup")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.global_randomize_button = QPushButton("🎲")
        self.global_randomize_button.setToolTip("Randomize all names")
        self.global_randomize_button.clicked.connect(self._randomize_all_names)
        title_layout.addWidget(self.global_randomize_button, alignment=Qt.AlignmentFlag.AlignBaseline)
        title_layout.addStretch(1) # Add stretch to balance
        main_layout.addLayout(title_layout)

        # Informational text for required dragons
        self.dragon_info_label = QLabel(f"Reminder: You must bring {self.required_dragons} dragon(s) to this game (1 per 24 points or part thereof).")
        dragon_font = self.dragon_info_label.font()
        dragon_font.setPointSize(dragon_font.pointSize() - 2) # Slightly smaller
        self.dragon_info_label.setFont(dragon_font)
        main_layout.addWidget(self.dragon_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Middle Section (Inputs and Help Panel)
        middle_section_layout = QHBoxLayout()

        # Left Side (Inputs Table)
        left_side_layout = QVBoxLayout() # Create a QVBoxLayout for the left side

        inputs_group = QGroupBox(f"Setup for Player {self.current_player_index + 1}") # Define locally first
        self.inputs_grid_layout = QGridLayout(inputs_group) # Assign to self
        self.inputs_grid_layout.setContentsMargins(10, 10, 10, 10)
        self.inputs_grid_layout.setSpacing(5) # Reduced spacing
        left_side_layout.addWidget(inputs_group) # Add the inputs_group to the left_side_layout
        
        # Instantiate PlayerIdentityWidget to get its components
        self.player_identity_widget = PlayerIdentityWidget(self.current_player_index + 1)

        # Player Name
        self.inputs_grid_layout.addWidget(QLabel("Player Name:"), 0, 0)
        self.inputs_grid_layout.addWidget(self.player_identity_widget.player_name_input, 0, 1, 1, 2) # Span 2 columns

        # Terrain Selections Widget
        self.terrain_selection_widget = TerrainSelectionWidget(self.all_terrain_options)
        self.inputs_grid_layout.addWidget(self.terrain_selection_widget, 1, 0, 1, 3) # Span all 3 columns for its internal grid

        # Dragon Selection Section (New)
        dragon_selection_group = QGroupBox(f"Select Your {self.required_dragons} Dragon(s)")
        dragon_selection_layout = QGridLayout(dragon_selection_group) # Use QGridLayout for labels and carousels
        self.dragon_selection_carousels = []
        for i in range(self.required_dragons):
            dragon_label = QLabel(f"Dragon {i+1}:")
            dragon_carousel = CarouselInputWidget(constants.AVAILABLE_DRAGON_TYPES)
            self.dragon_selection_carousels.append(dragon_carousel)
            dragon_carousel.valueChanged.connect(self._validate_and_update_button_state) # Connect for validation
            dragon_selection_layout.addWidget(dragon_label, i, 0)
            dragon_selection_layout.addWidget(dragon_carousel, i, 1)
        dragon_selection_layout.setColumnStretch(1,1) # Allow carousel to expand
        self.inputs_grid_layout.addWidget(dragon_selection_group, 2, 0, 1, 3) # Add below terrain selection

        # Army Setups
        # army_types = ["Home", "Campaign", "Horde"] # Replaced by constants.ARMY_TYPES_ALL
        self.army_setup_widgets: dict[str, ArmySetupWidget] = {} # Store ArmySetupWidget instances
        self.army_labels = {} # To store labels for show/hide

        # army_points_options = list(range(0, self.max_points_per_army + 1)) # No longer needed

        base_row_for_armies = 3 # Starting row after Dragon Selection group
        for i, army_type in enumerate(constants.ARMY_TYPES_ALL):
            current_army_main_row = base_row_for_armies + (i * 2) # Each army block takes 2 rows now

            army_label = QLabel(f"{army_type} Army:") # External label for the army type
            self.army_labels[army_type] = army_label
            self.inputs_grid_layout.addWidget(army_label, current_army_main_row, 0, Qt.AlignmentFlag.AlignTop)
            
            # Pass max_points_per_army to the widget constructor
            army_widget = ArmySetupWidget(army_type, self.max_points_per_army, self.unit_roster)
            self.army_setup_widgets[army_type] = army_widget
            self.inputs_grid_layout.addWidget(army_widget, current_army_main_row, 1, 1, 2) # Span 2 columns

            detailed_units_label = QLabel(constants.NO_UNITS_SELECTED_TEXT)
            detailed_units_label.setWordWrap(True)
            self.army_detailed_units_labels[army_type] = detailed_units_label
            self.inputs_grid_layout.addWidget(detailed_units_label, current_army_main_row + 1, 1, 1, 2) # Below army_widget
        # Set column stretch factors for better spacing
        self.inputs_grid_layout.setColumnStretch(0, 0) # Labels
        self.inputs_grid_layout.setColumnStretch(1, 1) # Inputs / Buttons
        self.inputs_grid_layout.setColumnStretch(2, 1) # Summaries / Spanned inputs

        self.inputs_group = inputs_group # Assign to instance variable after local use
        middle_section_layout.addLayout(left_side_layout, 1) # Add the left_side_layout to the middle_section with stretch

        # Right Side (Help Panel)
        self.help_panel = HelpPanelWidget("Help") # Use the new component
        middle_section_layout.addWidget(self.help_panel, 1) # Add stretch factor
        
        main_layout.addLayout(middle_section_layout)
        self.status_label = QLabel("") # For validation messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label) # Add status_label below middle_section
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        # Navigation Buttons
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: self.back_signal.emit(self.current_player_index))
        navigation_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next Player")
        self.next_button.clicked.connect(self._handle_next_action)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

        # Connect signals for live validation
        self.player_identity_widget.name_changed.connect(self._validate_and_update_button_state)
        self.terrain_selection_widget.home_terrain_changed.connect(self._validate_and_update_button_state)
        self.terrain_selection_widget.frontier_proposal_changed.connect(self._validate_and_update_button_state)
        for army_widget in self.army_setup_widgets.values():
            # army_widget.points_changed.connect(self._validate_and_update_button_state) # No longer needed
            army_widget.units_updated_signal.connect(self._handle_units_updated_from_widget)

        self._set_player_setup_help_text() # Set initial help text
        self.update_for_player(self.current_player_index, self.initial_player_data) # Pass initial data

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
            self.player_identity_widget.set_name(random.choice(self.preselected_names["Player"]))

    def _set_random_army_name_for_input(self, line_edit_widget: QLineEdit):
        pass # Army name input removed, this method is no longer needed for armies

    def _randomize_all_names(self):
        # Only randomize player name now
        self._set_random_player_name() # This now calls set_name on player_identity_widget
        # Army names are removed from setup, no army names to randomize here.


    def _handle_next_action(self):
        if not self._validate_inputs(): # Validate before proceeding
            return # Stop if validation fails, error message is shown by _validate_inputs

        player_name = self.player_identity_widget.get_name()
        home_terrain_val = self.terrain_selection_widget.get_home_terrain()
        frontier_proposal_val = self.terrain_selection_widget.get_frontier_proposal()

        player_data = {
            "player_index": self.current_player_index,
            "name": player_name,
            "home_terrain": home_terrain_val,
            "frontier_terrain_proposal": frontier_proposal_val,
            "selected_dragons": [carousel.value() for carousel in self.dragon_selection_carousels], # Collect selected dragons
            "armies": {}
        }
        for army_type in constants.ARMY_TYPES_ALL: # Iterate using constants
            army_key = army_type.lower()
            if army_key == "horde" and self.num_players <= 1: # Skip Horde for 1 player
                continue
            # Get the correct army_widget instance for the current army_type
            current_army_widget = self.army_setup_widgets[army_type]
            army_allocated_points = current_army_widget.get_points()
            army_units_data = current_army_widget.get_current_units_as_dicts()
            # dragon_dice_description = self.army_dragon_dice_inputs[army_type].text() # Removed
            player_data["armies"][army_key] = {
                "name": army_type,
                "allocated_points": army_allocated_points,
                "units": army_units_data,
            }
        self.player_data_finalized.emit(self.current_player_index, player_data)
        self.current_player_index += 1
        if self.current_player_index < self.num_players:
            self.update_for_player(self.current_player_index) # For new player, no initial data is passed
        # If all players are done, the MainWindow will handle the transition
        # based on the signal from AppDataModel.

    def _set_status_message(self, message, color_name="black"):
        self.status_label.setText(message)
        palette = self.status_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color_name))
        self.status_label.setPalette(palette)

    def _validate_inputs(self) -> bool:
        player_name = self.player_identity_widget.get_name()
        if not player_name:
            self._set_status_message("Player Name cannot be empty.", "red")
            return False
        
        # Validate points allocation
        total_allocated_points = 0
        armies_to_check = [constants.ARMY_TYPE_HOME, constants.ARMY_TYPE_CAMPAIGN]
        if self.num_players > 1:
            armies_to_check.append(constants.ARMY_TYPE_HORDE)

        for army_type in armies_to_check: # army_type here is "Home", "Campaign", or "Horde"
            army_key = army_type.lower()
            army_widget = self.army_setup_widgets[army_type]
            army_points = army_widget.get_points()
            if army_points is None: army_points = 0 # Should have a value
            total_allocated_points += army_points
            
            points_used_by_units = army_widget.get_points() 
            if points_used_by_units is None: points_used_by_units = 0 # Ensure it's an int for comparison
            if points_used_by_units > self.max_points_per_army: # Check against max_points_per_army
                 self._set_status_message(f"{army_type} Army units ({points_used_by_units} pts) exceed individual army limit ({self.max_points_per_army}).", "red")
                 return False
            # The check `points_used_by_units != army_points` is now redundant because army_points IS points_used_by_units
            if army_points > 0 and not army_widget.current_units:
                 self._set_status_message(f"{army_type} Army has points ({army_points}) but no units. Please add units or set points to 0 via unit management.", "red")
                 # This state (points > 0 but no units) should ideally be prevented by how UnitSelectionDialog works
                 # or how ArmySetupWidget clears units if points are reduced.
                 # For now, this validation is a good catch-all.
                 # return False # Optionally make this a hard fail
        
        if total_allocated_points != self.point_value:
            self._set_status_message(f"Total points ({total_allocated_points}) must equal game limit ({self.point_value}).", "red")
            return False

        # If all checks pass
        is_valid_so_far = True 
        if not player_name: 
            is_valid_so_far = False

        if is_valid_so_far: 
            self._set_status_message("", "black") 
            return True
        
        return False 

    def _set_player_setup_help_text(self):
        player_num_for_display = self.current_player_index + 1
        self.help_panel.set_help_text(
            self.help_model.get_player_setup_help(
                player_num_for_display, self.num_players, self.point_value
            )
        )

    def _validate_and_update_button_state(self):
        is_valid = self._validate_inputs() # This will also set the status message
        self.next_button.setEnabled(is_valid)

    @Slot(str, int)
    def _handle_army_points_changed(self, army_type: str, points: int): # No longer used
        pass

    # This method is now part of ArmySetupWidget
    # def _open_unit_selection_dialog(self, army_type: str): ...

    @Slot(str, list)
    def _handle_units_updated_from_widget(self, army_type_key: str, unit_dicts: list):
        # army_type_key is already lowercase from ArmySetupWidget's signal
        self.army_units_data[army_type_key] = unit_dicts # Store the dicts
        self._update_specific_army_detailed_units_label(army_type_key.title()) # Update detailed list
        self._validate_and_update_button_state()

    def _update_specific_army_summary_label(self, army_type: str): # Renamed for clarity
        # This updates the ArmySetupWidget's internal summary
        if army_type in self.army_setup_widgets:
            self.army_setup_widgets[army_type]._update_units_summary()

    def _update_specific_army_detailed_units_label(self, army_type: str): # New method
        army_key = army_type.lower()
        units_in_army = self.army_units_data.get(army_key, [])
        if units_in_army:
            unit_names = [unit.get("name", "Unknown Unit") for unit in units_in_army]
            self.army_detailed_units_labels[army_type].setText(f"Selected: {', '.join(unit_names)}")
        else:
            self.army_detailed_units_labels[army_type].setText(constants.NO_UNITS_SELECTED_TEXT)

    def update_for_player(self, player_index, player_data_to_load: Optional[dict] = None):
        self.current_player_index = player_index
        player_display_num = self.current_player_index + 1
        self.title_label.setText(f"Player {player_display_num} Setup")
        self.inputs_group.setTitle(f"Setup for Player {player_display_num}")
        self.player_identity_widget.set_player_display_number(player_display_num)

        if player_data_to_load:
            self.player_identity_widget.set_name(player_data_to_load.get("name", ""))
            self.terrain_selection_widget.set_home_terrain(player_data_to_load.get("home_terrain"))
            self.terrain_selection_widget.set_frontier_proposal(player_data_to_load.get("frontier_terrain_proposal"))

            selected_dragons_data = player_data_to_load.get("selected_dragons", [])
            for i, carousel in enumerate(self.dragon_selection_carousels):
                if i < len(selected_dragons_data):
                    carousel.setValue(selected_dragons_data[i])
                elif constants.AVAILABLE_DRAGON_TYPES: # Default if not enough data
                    carousel.setValue(constants.AVAILABLE_DRAGON_TYPES[0])

            armies_data = player_data_to_load.get("armies", {})
            for army_key, details in armies_data.items(): # army_key is 'home', 'campaign', 'horde'
                army_type_title_case = army_key.title()
                if army_type_title_case in self.army_setup_widgets:
                    army_widget = self.army_setup_widgets[army_type_title_case]
                    army_widget.load_units_from_dicts(details.get("units", []))
                    army_widget._update_units_summary() # Trigger internal update
                    self._update_specific_army_detailed_units_label(army_type_title_case)
                    # self.army_dragon_dice_inputs[army_type_title_case].setText(details.get("dragon_dice_description", "")) # Removed
                    self.army_units_data[army_key] = army_widget.get_current_units_as_dicts() # Keep local copy in sync

        else: # No data to load, set defaults
            self.player_identity_widget.clear_inputs() # Resets name placeholder and terrain carousels
            self.terrain_selection_widget.clear_selections()
            self.player_identity_widget.set_player_display_number(player_display_num) # Ensure placeholder is correct

            for carousel in self.dragon_selection_carousels: # Reset dragon carousels
                if constants.AVAILABLE_DRAGON_TYPES: # Check if list is not empty
                    carousel.setValue(constants.AVAILABLE_DRAGON_TYPES[0])

            for army_type in constants.ARMY_TYPES_ALL: # Iterate using constants
                army_widget = self.army_setup_widgets[army_type]
                army_widget.load_units_from_dicts([]) # Clear units
                army_widget._update_units_summary()
                self.army_units_data[army_widget.army_type_name.lower()] = []
                self._update_specific_army_detailed_units_label(army_widget.army_type_name) # Update after clearing the cache

            if self.num_players > 1:
                pass # Visibility handled below
        self._update_horde_visibility()

        # Perform initial validation which will set messages and button state
        self._validate_and_update_button_state() 
        self._set_player_setup_help_text()
        self.player_identity_widget.player_name_input.setFocus()

        if self.current_player_index == self.num_players - 1:
            self.next_button.setText("Finalize Setup & Start Game")
        else:
            self.next_button.setText(f"Next Player ({self.current_player_index + 2}/{self.num_players})")

    def _update_horde_visibility(self):
        show_horde = self.num_players > 1
        self.army_labels[constants.ARMY_TYPE_HORDE].setVisible(show_horde)
        if constants.ARMY_TYPE_HORDE in self.army_setup_widgets: # Check if widget exists
            self.army_setup_widgets[constants.ARMY_TYPE_HORDE].setVisible(show_horde)
            if constants.ARMY_TYPE_HORDE in self.army_detailed_units_labels: # Also hide/show the detailed summary label
                self.army_detailed_units_labels[constants.ARMY_TYPE_HORDE].setVisible(show_horde)
