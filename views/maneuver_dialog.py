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
    
    def __init__(self, 
                 current_player_name: str,
                 available_armies: List[Dict[str, Any]],
                 all_players_data: Dict[str, Dict[str, Any]],
                 terrain_data: Dict[str, Dict[str, Any]],
                 parent=None):
        super().__init__(parent)
        self.current_player_name = current_player_name
        self.available_armies = available_armies
        self.all_players_data = all_players_data
        self.terrain_data = terrain_data
        
        # Dialog state
        self.selected_army = None
        self.maneuver_participants = []
        self.current_step = "select_army"  # select_army, counter_maneuver, roll_dice, results
        
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
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.back_button = QPushButton("Back")
        self.back_button.setMaximumWidth(100)
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)
        
        self.next_button = QPushButton("Next")
        self.next_button.setMaximumWidth(100)
        self.next_button.clicked.connect(self._on_next)
        button_layout.addWidget(self.next_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMaximumWidth(100)
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
        
        if self.current_step == "select_army":
            self._show_army_selection()
        elif self.current_step == "counter_maneuver":
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
            
            button_text = f"{army_name} ({army_type.title()}) - {location} ({unit_count} units)"
            radio_button = QRadioButton(button_text)
            self.army_button_group.addButton(radio_button, i)
            self.content_layout.addWidget(radio_button)
        
        if self.available_armies:
            self.army_button_group.buttons()[0].setChecked(True)
            self.selected_army = self.available_armies[0]
        
        self.army_button_group.idClicked.connect(self._on_army_selected)
    
    def _show_counter_maneuver(self):
        """Show counter-maneuver opportunity step."""
        self.step_label.setText("Step 2: Counter-Maneuver Opportunity")
        
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
                    other_armies.append({
                        "player": player_name,
                        "army": army_data,
                        "army_type": army_type
                    })
        
        if not other_armies:
            info_label = QLabel(f"No other armies at {location}. Maneuver will proceed unopposed.")
            self.content_layout.addWidget(info_label)
        else:
            info_label = QLabel(f"Other armies at {location} can counter-maneuver:")
            self.content_layout.addWidget(info_label)
            
            self.counter_list = QListWidget()
            for army_info in other_armies:
                item_text = f"{army_info['player']} - {army_info['army']['name']} ({army_info['army_type'].title()})"
                self.counter_list.addItem(f"☐ {item_text}")
            self.content_layout.addWidget(self.counter_list)
            
            counter_label = QLabel("In a real game, other players would now decide whether to counter-maneuver.\nFor this demo, assume no counter-maneuvers.")
            counter_label.setWordWrap(True)
            self.content_layout.addWidget(counter_label)
    
    def _show_dice_rolling(self):
        """Show dice rolling step."""
        self.step_label.setText("Step 3: Roll for Maneuver")
        
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
        
        result_label = QLabel(f"Maneuver Roll Result: {maneuver_results} maneuver icons")
        result_label.setStyleSheet("font-weight: bold; color: blue;")
        self.content_layout.addWidget(result_label)
        
        # Store results for next step
        self.maneuver_result = maneuver_results
    
    def _show_results(self):
        """Show maneuver results and terrain changes."""
        self.step_label.setText("Step 4: Maneuver Results")
        
        if not self.selected_army:
            return
        
        location = self.selected_army.get("location", "")
        terrain_info = self.terrain_data.get(location, {})
        current_face = terrain_info.get("face", 1)
        
        result_text = f"Maneuver succeeded with {getattr(self, 'maneuver_result', 1)} maneuver icons!\n\n"
        
        # Determine terrain change
        if hasattr(self, 'maneuver_result') and self.maneuver_result > 0:
            # For simplicity, assume terrain turns up one step
            new_face = min(current_face + 1, 8)  # Max face is 8
            result_text += f"Terrain '{location}' changes from face {current_face} to face {new_face}."
            
            # Store the result for emission
            self.final_result = {
                "success": True,
                "army": self.selected_army,
                "location": location,
                "old_face": current_face,
                "new_face": new_face,
                "maneuver_icons": self.maneuver_result
            }
        else:
            result_text += "Maneuver failed. No terrain changes."
            self.final_result = {
                "success": False,
                "army": self.selected_army,
                "location": location,
                "maneuver_icons": 0
            }
        
        result_label = QLabel(result_text)
        result_label.setWordWrap(True)
        self.content_layout.addWidget(result_label)
    
    def _update_buttons(self):
        """Update button states based on current step."""
        self.back_button.setEnabled(self.current_step != "select_army")
        
        if self.current_step == "select_army":
            self.next_button.setText("Check Counter-Maneuvers")
            self.next_button.setEnabled(bool(self.selected_army))
        elif self.current_step == "counter_maneuver":
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
        if self.current_step == "select_army":
            self.current_step = "counter_maneuver"
        elif self.current_step == "counter_maneuver":
            self.current_step = "roll_dice"
        elif self.current_step == "roll_dice":
            self.current_step = "results"
        elif self.current_step == "results":
            # Complete the maneuver
            if hasattr(self, 'final_result'):
                self.maneuver_completed.emit(self.final_result)
            self.accept()
            return
        
        self._update_step_display()
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.maneuver_cancelled.emit()
        self.reject()