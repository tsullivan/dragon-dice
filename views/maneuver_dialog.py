from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QSpacerItem,
    QSizePolicy,
    QListWidget,
    QComboBox,
)
import constants
from PySide6.QtCore import Qt, Signal
from typing import List, Dict, Any, Optional


class ManeuverDialog(QDialog):
    """
    Dialog for handling proper Dragon Dice maneuver flow:
    1. Player selects which army to maneuver
    2. Check for counter-maneuvers from other players
    3. Roll dice for maneuver results
    4. Apply terrain changes based on results
    """

    maneuver_completed = Signal(dict)  # Emits maneuver results
    maneuver_cancelled = Signal()

    def __init__(
        self,
        current_player_name: str,
        acting_army: Dict[str, Any],
        all_players_data: Dict[str, Dict[str, Any]],
        terrain_data: Dict[str, Dict[str, Any]],
        parent=None,
    ):
        super().__init__(parent)
        self.current_player_name = current_player_name
        self.acting_army = acting_army
        self.all_players_data = all_players_data
        self.terrain_data = terrain_data

        # Dialog state
        self.selected_army = acting_army  # Use the pre-selected acting army
        self.maneuver_participants = []
        self.current_step = "counter_maneuver"  # Skip army selection, start with counter_maneuver, roll_dice, results

        self.setWindowTitle("Army Maneuver")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._update_step_display()

    def _setup_ui(self):
        """Set up the dialog UI with different sections for each step."""
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel(f"{self.current_player_name} - Army Maneuver")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Step indicator
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.step_label)

        # Main content area (will be populated based on current step)
        self.content_widget = QGroupBox()
        self.content_layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.content_widget)

        # Button area - allow buttons to stretch across the dialog
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._on_next)
        button_layout.addWidget(self.next_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _update_step_display(self):
        """Update the dialog content based on current step."""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if self.current_step == "counter_maneuver":
            self._show_counter_maneuver()
        elif self.current_step == "roll_dice":
            self._show_dice_rolling()
        elif self.current_step == "results":
            self._show_results()

        self._update_buttons()

    def _show_army_selection(self):
        """Show army selection step."""
        self.step_label.setText("Step 1: Select Army to Maneuver")

        instruction_label = QLabel("Choose which army you want to maneuver:")
        self.content_layout.addWidget(instruction_label)

        self.army_button_group = QButtonGroup(self)

        for i, army_info in enumerate(self.available_armies):
            army_name = army_info.get("name", "Unknown Army")
            army_type = army_info.get("army_type", "unknown")
            location = army_info.get("location", "Unknown")
            unit_count = len(army_info.get("units", []))

            # Add terrain icons to make locations much clearer
            location_icon = ""
            for terrain_name, icon in constants.TERRAIN_ICONS.items():
                if terrain_name in location:
                    location_icon = icon
                    break
            if not location_icon:
                location_icon = "🗺️"  # Default terrain icon

            # Add army type indicators
            army_type_indicator = constants.ARMY_TYPE_ICONS.get(army_type, "⚔️")

            button_text = f"{army_type_indicator} {army_name} ({army_type.title()} Army)\nLOCATION: {location_icon} {location} ({unit_count} units)"
            radio_button = QRadioButton(button_text)
            self.army_button_group.addButton(radio_button, i)
            self.content_layout.addWidget(radio_button)

        if self.available_armies:
            self.army_button_group.buttons()[0].setChecked(True)
            self.selected_army = self.available_armies[0]

        self.army_button_group.idClicked.connect(self._on_army_selected)

    def _show_counter_maneuver(self):
        """Show counter-maneuver opportunity step."""
        self.step_label.setText("Step 1: Counter-Maneuver Opportunity")

        # Show which army is maneuvering
        army_name = self.selected_army.get("name", "Unknown Army")
        army_type = self.selected_army.get("army_type", "unknown")
        army_type_indicator = (
            "[HOME]"
            if army_type == "home"
            else "[CAMPAIGN]" if army_type == "campaign" else "[HORDE]"
        )

        acting_army_label = QLabel(
            f"ACTING ARMY: {army_type_indicator} {army_name} is attempting to maneuver..."
        )
        acting_army_label.setStyleSheet(
            "font-weight: bold; color: blue; background-color: #e6f3ff; padding: 8px; border: 1px solid #0066cc; border-radius: 4px;"
        )
        acting_army_label.setWordWrap(True)
        self.content_layout.addWidget(acting_army_label)

        if not self.selected_army:
            return

        location = self.selected_army.get("location", "")

        # Find other players with armies at the same location
        other_armies = []
        for player_name, player_data in self.all_players_data.items():
            if player_name == self.current_player_name:
                continue

            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("location") == location:
                    other_armies.append(
                        {
                            "player": player_name,
                            "army": army_data,
                            "army_type": army_type,
                        }
                    )

        # Add terrain icon for location (WSL-friendly)
        location_icon = ""
        if "Highland" in location:
            location_icon = "[HIGHLAND]"
        elif "Coastland" in location:
            location_icon = "[COAST]"
        elif "Deadland" in location:
            location_icon = "[DEAD]"
        elif "Flatland" in location:
            location_icon = "[FLAT]"
        elif "Swampland" in location:
            location_icon = "[SWAMP]"
        elif "Feyland" in location:
            location_icon = "[FEY]"
        elif "Wasteland" in location:
            location_icon = "[WASTE]"

        if not other_armies:
            info_label = QLabel(
                f"LOCATION: No other armies at {location_icon} {location}.\n\n>> Your maneuver will proceed unopposed!"
            )
            info_label.setStyleSheet("color: green; font-weight: bold;")
            info_label.setWordWrap(True)
            self.content_layout.addWidget(info_label)
        else:
            info_label = QLabel(
                f"LOCATION: Other armies at {location_icon} {location} have the option to counter-maneuver:"
            )
            info_label.setWordWrap(True)
            self.content_layout.addWidget(info_label)

            self.counter_list = QListWidget()
            for army_info in other_armies:
                army_type = army_info["army_type"]
                army_type_indicator = (
                    "[HOME]"
                    if army_type == "home"
                    else "[CAMPAIGN]" if army_type == "campaign" else "[HORDE]"
                )
                item_text = f"{army_type_indicator} {army_info['player']} - {army_info['army']['name']} ({army_type.title()} Army)"
                self.counter_list.addItem(f"WARNING: {item_text}")
            self.content_layout.addWidget(self.counter_list)

            counter_label = QLabel(
                "INFO: <b>Note:</b> Counter-maneuvering is <u>optional</u> for opposing players.<br>In a real game, they would now choose whether to counter-maneuver.<br><br>SIMULATION: <b>For this simulation:</b> Assuming no players choose to counter-maneuver."
            )
            counter_label.setWordWrap(True)
            counter_label.setStyleSheet(
                "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
            )
            self.content_layout.addWidget(counter_label)

    def _show_dice_rolling(self):
        """Show dice rolling step."""
        self.step_label.setText("Step 2: Roll for Maneuver")

        if not self.selected_army:
            return

        army_name = self.selected_army.get("name", "Unknown Army")
        units = self.selected_army.get("units", [])

        instruction_label = QLabel(f"Rolling maneuver dice for {army_name}...")
        self.content_layout.addWidget(instruction_label)

        # Show army composition
        army_info = QLabel(f"Army has {len(units)} units:")
        self.content_layout.addWidget(army_info)

        unit_list = QTextEdit()
        unit_list.setMaximumHeight(100)
        unit_list.setReadOnly(True)
        unit_text = ""
        for unit in units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_health = unit.get("health", 0)
            unit_text += f"• {unit_name} ({unit_health} HP)\n"
        unit_list.setPlainText(unit_text)
        self.content_layout.addWidget(unit_list)

        # Simulate dice roll results
        import random

        maneuver_results = random.randint(1, len(units) + 2)  # Simple simulation

        result_label = QLabel(
            f"Maneuver Roll Result: {maneuver_results} maneuver icons"
        )
        result_label.setStyleSheet("font-weight: bold; color: blue;")
        self.content_layout.addWidget(result_label)

        # Store results for next step
        self.maneuver_result = maneuver_results

    def _show_results(self):
        """Show maneuver results and terrain changes."""
        self.step_label.setText("Step 3: Maneuver Results")

        if not self.selected_army:
            return

        location = self.selected_army.get("location", "")
        terrain_info = self.terrain_data.get(location, {})
        current_face = terrain_info.get("face", 1)

        # Determine terrain change
        if hasattr(self, "maneuver_result") and self.maneuver_result > 0:
            result_text = f"Maneuver succeeded with {getattr(self, 'maneuver_result', 1)} maneuver icons!\n\n"
            result_text += f"Current terrain '{location}' is on face {current_face}.\n"
            result_text += "Choose whether to turn the terrain UP or DOWN by one step:"

            result_label = QLabel(result_text)
            result_label.setWordWrap(True)
            self.content_layout.addWidget(result_label)

            # Add terrain direction choice
            direction_group = QGroupBox("Terrain Direction Choice")
            direction_layout = QVBoxLayout(direction_group)
            
            self.terrain_direction_group = QButtonGroup(self)
            
            # UP option
            up_face = min(current_face + 1, 8)  # Max face is 8
            up_radio = QRadioButton(f"⬆️ Turn UP to face {up_face}")
            if current_face < 8:  # Only enable if not already at max
                up_radio.setEnabled(True)
                up_radio.setChecked(True)  # Default selection
            else:
                up_radio.setEnabled(False)
            self.terrain_direction_group.addButton(up_radio, 1)  # 1 = UP
            direction_layout.addWidget(up_radio)
            
            # DOWN option  
            down_face = max(current_face - 1, 1)  # Min face is 1
            down_radio = QRadioButton(f"⬇️ Turn DOWN to face {down_face}")
            if current_face > 1:  # Only enable if not already at min
                down_radio.setEnabled(True)
                if current_face >= 8:  # If at max face, default to DOWN
                    down_radio.setChecked(True)
            else:
                down_radio.setEnabled(False)
            self.terrain_direction_group.addButton(down_radio, -1)  # -1 = DOWN
            direction_layout.addWidget(down_radio)

            self.content_layout.addWidget(direction_group)

            # Store initial result data (will be updated when direction is chosen)
            self.terrain_location = location
            self.terrain_current_face = current_face
            
        else:
            result_text = f"Maneuver failed with {getattr(self, 'maneuver_result', 0)} maneuver icons.\n\n"
            result_text += "No terrain changes."
            
            result_label = QLabel(result_text)
            result_label.setWordWrap(True)
            self.content_layout.addWidget(result_label)
            
            self.final_result = {
                "success": False,
                "army": self.selected_army,
                "location": location,
                "maneuver_icons": 0,
            }

    def _update_buttons(self):
        """Update button states based on current step."""
        self.back_button.setEnabled(
            False
        )  # No back button since we skip army selection

        if self.current_step == "counter_maneuver":
            self.next_button.setText("Roll Dice")
            self.next_button.setEnabled(True)
        elif self.current_step == "roll_dice":
            self.next_button.setText("Apply Results")
            self.next_button.setEnabled(True)
        elif self.current_step == "results":
            self.next_button.setText("Complete Maneuver")
            self.next_button.setEnabled(True)

    def _on_army_selected(self, army_index: int):
        """Handle army selection."""
        if 0 <= army_index < len(self.available_armies):
            self.selected_army = self.available_armies[army_index]
            self._update_buttons()

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "counter_maneuver":
            self.current_step = "select_army"
        elif self.current_step == "roll_dice":
            self.current_step = "counter_maneuver"
        elif self.current_step == "results":
            self.current_step = "roll_dice"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "counter_maneuver":
            self.current_step = "roll_dice"
        elif self.current_step == "roll_dice":
            self.current_step = "results"
        elif self.current_step == "results":
            # Complete the maneuver
            if hasattr(self, "maneuver_result") and self.maneuver_result > 0:
                # Calculate final result based on player's terrain direction choice
                if hasattr(self, "terrain_direction_group"):
                    selected_direction = self.terrain_direction_group.checkedButton()
                    if selected_direction:
                        direction_value = self.terrain_direction_group.id(selected_direction)
                        new_face = self.terrain_current_face + direction_value
                        new_face = max(1, min(8, new_face))  # Clamp between 1 and 8
                        
                        direction_text = "UP" if direction_value > 0 else "DOWN"
                        
                        self.final_result = {
                            "success": True,
                            "army": self.selected_army,
                            "location": self.terrain_location,
                            "old_face": self.terrain_current_face,
                            "new_face": new_face,
                            "direction": direction_text,
                            "maneuver_icons": self.maneuver_result,
                        }
                    else:
                        # No direction selected, default to UP for backwards compatibility
                        new_face = min(self.terrain_current_face + 1, 8)
                        self.final_result = {
                            "success": True,
                            "army": self.selected_army,
                            "location": self.terrain_location,
                            "old_face": self.terrain_current_face,
                            "new_face": new_face,
                            "direction": "UP",
                            "maneuver_icons": self.maneuver_result,
                        }
            
            if hasattr(self, "final_result"):
                self.maneuver_completed.emit(self.final_result)
            self.accept()
            return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.maneuver_cancelled.emit()
        self.reject()
