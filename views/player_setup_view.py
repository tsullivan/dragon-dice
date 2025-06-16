from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QGroupBox, QGridLayout, QTextEdit,
                               QComboBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette, QColor
import random
import os
from typing import Optional # Import Optional

from components.carousel import CarouselInputWidget
from components.army_setup_widget import ArmySetupWidget
from components.player_identity_widget import PlayerIdentityWidget
from components.help_panel_widget import HelpPanelWidget
from views.unit_selection_dialog import UnitSelectionDialog # Import the dialog
from models.help_text_model import HelpTextModel
from models.unit_roster_model import UnitRosterModel # Import UnitRosterModel
from models.unit_model import UnitModel # Import UnitModel
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
        # self.army_points_combos: dict[str, QComboBox] = {} # Removed
        self.army_units_data: dict[str, list[dict]] = {} # {army_type: list of unit dicts}
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
        inputs_grid_layout = QGridLayout(inputs_group)
        inputs_grid_layout.setContentsMargins(10, 10, 10, 10)
        inputs_grid_layout.setSpacing(10)
        left_side_layout.addWidget(inputs_group) # Add the inputs_group to the left_side_layout

        # Player Identity Widget (Name, Home Terrain, Frontier Proposal)
        # The QGroupBox `inputs_group` already provides a title like "Setup for Player X"
        # So, PlayerIdentityWidget itself doesn't need a group box title.
        # We pass current_player_index + 1 for the placeholder text.
        self.player_identity_widget = PlayerIdentityWidget(self.current_player_index + 1, self.all_terrain_options)
        # PlayerIdentityWidget uses QFormLayout, which creates its own label-field pairs.
        inputs_grid_layout.addWidget(self.player_identity_widget, 0, 0, 1, 2) # Span 2 columns of the main grid

        # Army Setups
        army_types = ["Home", "Campaign", "Horde"]
        self.army_setup_widgets = {} # To store ArmySetupWidget instances
        self.army_labels = {} # To store labels for show/hide
        self.army_manage_buttons: dict[str, QPushButton] = {} # {army_type: QPushButton}
        self.army_units_summary_labels: dict[str, QLabel] = {} # {army_type: QLabel}

        # army_points_allowed = list(range(0, self.max_points_per_army + 1)) # No longer needed here

        for i, army_type in enumerate(army_types):
            row = 1 + i # Start army setups from the next row after player identity
            army_label = QLabel(f"{army_type} Army:") # External label for the army type
            army_key = army_type.lower()
            self.army_labels[army_type] = army_label
            inputs_grid_layout.addWidget(army_label, row, 0, Qt.AlignmentFlag.AlignTop) # Align label to top

            # Manage Units Button
            manage_button = QPushButton("Manage Units")
            manage_button.clicked.connect(lambda checked, at=army_type: self._open_unit_selection_dialog(at))
            self.army_manage_buttons[army_type] = manage_button
            inputs_grid_layout.addWidget(manage_button, row, 1) # Button in second column

            # Units Summary Label
            units_summary_label = QLabel("Units: 0 (0 pts)")
            self.army_units_summary_labels[army_type] = units_summary_label
            inputs_grid_layout.addWidget(units_summary_label, row, 2, Qt.AlignmentFlag.AlignVCenter) # Summary in third column
        # Set column stretch factors for better spacing
        inputs_grid_layout.setColumnStretch(0, 0) # Column for labels like "Home Army:"
        inputs_grid_layout.setColumnStretch(1, 1) # Column for PlayerIdentityWidget fields and ArmySetupWidgets

        self.inputs_group = inputs_group # Assign to instance variable after local use
        middle_section_layout.addLayout(left_side_layout, 1) # Add the left_side_layout to the middle_section with stretch

        # Right Side (Help Panel)
        self.help_panel = HelpPanelWidget("Help") # Use the new component
        middle_section_layout.addWidget(self.help_panel, 1) # Add stretch factor
        
        # Status Label below Help Panel (now part of middle_section_layout's parent, main_layout)
        # To achieve this, we'll add it to main_layout after middle_section_layout

        main_layout.addLayout(middle_section_layout)
        self.status_label = QLabel("") # For validation messages
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label) # Add status_label below middle_section
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
        self.player_identity_widget.name_changed.connect(self._validate_and_update_button_state)
        self.player_identity_widget.home_terrain_changed.connect(self._validate_and_update_button_state)
        self.player_identity_widget.frontier_proposal_changed.connect(self._validate_and_update_button_state)
        # No points combo boxes to connect anymore for validation trigger,
        # unit selection will trigger validation.

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
        home_terrain_val = self.player_identity_widget.get_home_terrain()
        frontier_proposal_val = self.player_identity_widget.get_frontier_proposal()

        player_data = {
            "player_index": self.current_player_index,
            "name": player_name,
            "home_terrain": home_terrain_val,
            "frontier_terrain_proposal": frontier_proposal_val,
            "armies": {}
        }
        for army_type, army_widget in self.army_setup_widgets.items():
            army_key = army_type.lower()
            if army_key == "horde" and self.num_players <= 1: # Skip Horde for 1 player
                continue
            # Points are now derived from units
            army_units = self.army_units_data.get(army_key, [])
            army_allocated_points = sum(u.get("points_cost", 0) for u in army_units)
            player_data["armies"][army_key] = {
                "name": army_type, # Army name is now just the type
                "allocated_points": army_allocated_points, # This is the sum of unit costs
                "units": self.army_units_data.get(army_key, []) # Get units from stored data
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
        armies_to_check = ["Home", "Campaign"]
        if self.num_players > 1:
            armies_to_check.append("Horde")

        for army_type in armies_to_check:
            army_key = army_type.lower()
            army_points = sum(u.get("points_cost", 0) for u in self.army_units_data.get(army_key, []))
            total_allocated_points += army_points

        if total_allocated_points != self.point_value:
            self._set_status_message(f"Total points ({total_allocated_points}) must equal game limit ({self.point_value}).", "red")
            return False
            
            # Validate units vs points allocated
            units_data = self.army_units_data.get(army_key, [])
            points_used_by_units = sum(u.get("points_cost", 0) for u in units_data)
            if points_used_by_units > self.max_points_per_army: # Check against max_points_per_army
                 self._set_status_message(f"{army_type} Army units ({points_used_by_units} pts) exceed individual army limit ({self.max_points_per_army}).", "red")
                 return False
            if points_used_by_units > 0 and not units_data: # This case should be prevented by unit selection
                 self._set_status_message(f"{army_type} Army has points but no units (this shouldn't happen).", "red")
                 pass # For now, allow 0 points if total is met.
        
        # If all checks pass
        is_valid_so_far = True # Placeholder, actual logic above determines validity
        # The following logic assumes that if we reach here, it's valid,
        # otherwise a 'return False' would have been hit.
        if not player_name: # This check is redundant if logic above is correct, but as a safeguard
            is_valid_so_far = False # Should have been caught

        if is_valid_so_far: # All checks passed
            self._set_status_message("", "black") # Clear message if valid
            return True
        
        # Fallback, should ideally not be reached if logic is tight
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

    def _open_unit_selection_dialog(self, army_type: str):
        army_key = army_type.lower()
        # The dialog needs the MAX points this army can have, not its current points.
        # The dialog itself will sum up selected units and check against this max.
        max_allowed_for_this_army = self.max_points_per_army
        current_units = [UnitModel.from_dict(u_data) for u_data in self.army_units_data.get(army_key, [])]

        dialog = UnitSelectionDialog(army_type, max_allowed_for_this_army, self.unit_roster, current_units, self)
        dialog.units_selected_signal.connect(lambda units: self._handle_units_selected(army_type, units))
        dialog.exec() # Show as modal

    @Slot(str, list)
    def _handle_units_selected(self, army_type: str, selected_units: list[UnitModel]):
        army_key = army_type.lower()
        self.army_units_data[army_key] = [unit.to_dict() for unit in selected_units]
        self._update_specific_army_summary_label(army_type)
        self._validate_and_update_button_state() # Re-validate units vs points

    def _update_specific_army_summary_label(self, army_type: str):
        army_key = army_type.lower()
        units_in_army = self.army_units_data.get(army_key, [])
        points_used = sum(unit.get("points_cost", 0) for unit in units_in_army) # Use units_in_army and .get() for safety
        self.army_units_summary_labels[army_type].setText(f"Units: {len(units_in_army)} ({points_used} pts)")

    def update_for_player(self, player_index, player_data_to_load: Optional[dict] = None):
        self.current_player_index = player_index
        player_display_num = self.current_player_index + 1
        self.title_label.setText(f"Player {player_display_num} Setup")
        self.inputs_group.setTitle(f"Setup for Player {player_display_num}")
        self.player_identity_widget.set_player_display_number(player_display_num)

        if player_data_to_load:
            self.player_identity_widget.set_name(player_data_to_load.get("name", ""))
            self.player_identity_widget.set_home_terrain(player_data_to_load.get("home_terrain"))
            self.player_identity_widget.set_frontier_proposal(player_data_to_load.get("frontier_terrain_proposal"))

            armies_data = player_data_to_load.get("armies", {})
            for army_key, details in armies_data.items(): # army_key is 'home', 'campaign', 'horde'
                army_type_title_case = army_key.title()
                if army_type_title_case in self.army_labels: # Check if this army type exists
                    # No points combo to set anymore

                    # Load units if present
                    units_data = details.get("units", [])
                    self.army_units_data[army_key] = units_data
                    self._update_specific_army_summary_label(army_type_title_case)

        else: # No data to load, set defaults
            self.player_identity_widget.clear_inputs() # Resets name placeholder and terrain carousels
            self.player_identity_widget.set_player_display_number(player_display_num) # Ensure placeholder is correct

            # Set default points to 0 and clear units for all armies
            for army_type in ["Home", "Campaign", "Horde"]:
                if army_type in self.army_labels: # Check if this army type exists
                    army_key = army_type.lower()
                    self.army_units_data[army_key] = [] # Clear units
                    self._update_specific_army_summary_label(army_type) # Update summary to 0 units, 0 pts

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
        self.army_labels["Horde"].setVisible(show_horde)
        if "Horde" in self.army_manage_buttons: # Check if widgets exist
            # self.army_points_combos["Horde"].setVisible(show_horde) # Removed
            self.army_manage_buttons["Horde"].setVisible(show_horde)
            self.army_units_summary_labels["Horde"].setVisible(show_horde)
