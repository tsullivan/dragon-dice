"""
Enhanced Maneuver Dialog for Dragon Dice - captures individual die face results for proper SAI and species ability tracking.

This dialog handles the complete maneuver flow:
1. Player announces intention to maneuver
2. Opposing players decide whether to counter-maneuver
3. Both armies roll dice and input individual face results
4. Calculate final maneuver results with species abilities
5. Determine success and terrain direction changes
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from game_logic.sai_processor import SAIProcessor


class ManeuverDieRollInputWidget(QWidget):
    """Widget for inputting individual die face results for maneuver rolls."""

    def __init__(self, unit_name: str, unit_health: int, parent=None):
        super().__init__(parent)
        self.unit_name = unit_name
        self.unit_health = unit_health
        self.face_inputs: List[QLineEdit] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the die roll input UI."""
        layout = QVBoxLayout(self)

        # Unit header
        header_label = QLabel(f"{self.unit_name} (Health: {self.unit_health})")
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(header_label)

        # Face inputs
        faces_layout = QHBoxLayout()

        for i in range(6):  # 6-sided dice
            face_layout = QVBoxLayout()

            face_label = QLabel(f"Face {i + 1}")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_layout.addWidget(face_label)

            face_input = QLineEdit()
            face_input.setMaximumWidth(60)
            face_input.setPlaceholderText("M/Mi/Mg/S/ID/SAI/Ma")
            face_input.setToolTip(
                "Enter die face result:\n"
                "M = Melee\n"
                "Mi = Missile\n"
                "Mg = Magic\n"
                "S = Save\n"
                "ID = ID face\n"
                "SAI = Special Action Icon\n"
                "Ma = Maneuver"
            )
            face_layout.addWidget(face_input)

            self.face_inputs.append(face_input)
            faces_layout.addLayout(face_layout)

        layout.addLayout(faces_layout)

    def get_face_results(self) -> List[str]:
        """Get the face results from all inputs."""
        return [input_field.text().strip() for input_field in self.face_inputs]

    def clear_inputs(self):
        """Clear all input fields."""
        for input_field in self.face_inputs:
            input_field.clear()


class EnhancedManeuverDialog(QDialog):
    """
    Enhanced dialog for handling maneuver attempts with detailed die face input.

    This dialog captures individual die face results from both maneuvering and
    counter-maneuvering armies to properly calculate species abilities and SAI effects.
    """

    maneuver_completed = Signal(dict)  # Emits maneuver results
    maneuver_cancelled = Signal()

    def __init__(
        self,
        maneuvering_player: str,
        maneuvering_army: Dict[str, Any],
        location: str,
        current_terrain_face: int,
        opposing_players: Optional[List[str]] = None,
        opposing_armies: Optional[List[Dict[str, Any]]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.maneuvering_player = maneuvering_player
        self.maneuvering_army = maneuvering_army
        self.location = location
        self.current_terrain_face = current_terrain_face
        self.opposing_players = opposing_players or []
        self.opposing_armies = opposing_armies or []

        # Maneuver state
        self.current_step = (
            "announce_maneuver"  # announce_maneuver, counter_decision, simultaneous_rolls, choose_direction
        )
        self.will_be_opposed = False
        self.maneuvering_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.counter_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.final_maneuvering_total = 0
        self.final_counter_total = 0
        self.chosen_direction: Optional[str] = None

        self.sai_processor = SAIProcessor()

        self.setWindowTitle(f"🏃 Maneuver at {location}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._update_step_display()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)

        # Step indicator
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.step_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.step_label.setFont(font)
        main_layout.addWidget(self.step_label)

        # Maneuver info
        maneuver_info = QLabel(
            f"🏛️ {self.location} (Face {self.current_terrain_face}): {self.maneuvering_player} wants to maneuver"
        )
        maneuver_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        maneuver_info.setStyleSheet("font-size: 14px; margin: 10px; padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(maneuver_info)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(150)
        self.results_display.setReadOnly(True)
        self.results_display.hide()
        main_layout.addWidget(self.results_display)

        # Buttons
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("◀ Back")
        self.back_button.setMaximumWidth(100)
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.next_button = QPushButton("Next ▶")
        self.next_button.setMaximumWidth(120)
        self.next_button.clicked.connect(self._on_next)
        button_layout.addWidget(self.next_button)

        main_layout.addLayout(button_layout)

    def _update_step_display(self):
        """Update the display based on current step."""
        # Clear content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if self.current_step == "announce_maneuver":
            self._show_announce_maneuver()
        elif self.current_step == "counter_decision":
            self._show_counter_decision()
        elif self.current_step == "simultaneous_rolls":
            self._show_simultaneous_rolls()
        elif self.current_step == "choose_direction":
            self._show_choose_direction()

        self._update_buttons()

    def _show_announce_maneuver(self):
        """Show maneuver announcement and army info."""
        self.step_label.setText("Step 1: 🏃 Announce Maneuver")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            f"<b>{self.maneuvering_player}</b> announces intention to maneuver at {self.location}.<br>"
            f"The terrain will be turned UP or DOWN by one face if the maneuver succeeds."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #e8f4fd;")
        self.content_layout.addWidget(instructions)

        # Maneuvering army info
        army_group = QGroupBox("Maneuvering Army")
        army_layout = QVBoxLayout(army_group)

        army_name = self.maneuvering_army.get("name", "Unknown Army")
        army_units = self.maneuvering_army.get("units", [])

        army_info = QLabel(f"Army: {army_name}")
        army_info.setStyleSheet("font-weight: bold;")
        army_layout.addWidget(army_info)

        # Show units with species abilities
        terrain_elements = self._get_terrain_elements()
        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_species = unit.get("species", "Unknown")
            unit_health = unit.get("health", 1)

            unit_text = f"• {unit_name} ({unit_species}, Health: {unit_health})"

            # Add species ability notes
            if unit_species == "Dwarves" and "earth" in terrain_elements:
                unit_text += " ⛰️ Mountain Master: Melee → Maneuver"
            elif unit_species == "Goblins" and "earth" in terrain_elements:
                unit_text += " 🏔️ Swamp Master: Melee → Maneuver"
            elif unit_species == "Feral" and "earth" in terrain_elements and "air" in terrain_elements:
                unit_text += " 🐃 Stampede ready (for melee counter-attacks)"
            elif unit_species == "Firewalkers" and "fire" in terrain_elements:
                unit_text += " 🔥 Flaming Shields ready (for melee attacks)"

            unit_label = QLabel(unit_text)
            army_layout.addWidget(unit_label)

        self.content_layout.addWidget(army_group)

        # Opposing armies info
        if self.opposing_players:
            opposing_group = QGroupBox("Opposing Players at This Location")
            opposing_layout = QVBoxLayout(opposing_group)

            for _i, player in enumerate(self.opposing_players):
                player_label = QLabel(f"• {player}")
                opposing_layout.addWidget(player_label)

            opposing_note = QLabel("These players may choose to counter-maneuver if they wish to oppose this maneuver.")
            opposing_note.setStyleSheet("font-style: italic; margin-top: 10px;")
            opposing_layout.addWidget(opposing_note)

            self.content_layout.addWidget(opposing_group)
        else:
            no_opposition_label = QLabel("No opposing armies at this location. Maneuver will automatically succeed.")
            no_opposition_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
            self.content_layout.addWidget(no_opposition_label)

    def _show_counter_decision(self):
        """Show counter-maneuver decision for opposing players."""
        self.step_label.setText("Step 2: 🤔 Counter-Maneuver Decision")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            "<b>Opposing players</b> must decide whether to counter-maneuver.<br>"
            "If any player chooses to counter-maneuver, both armies will roll dice simultaneously.<br>"
            "If no one counter-maneuvers, the maneuver automatically succeeds."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #fdf8e8;")
        self.content_layout.addWidget(instructions)

        # Decision buttons
        decision_layout = QHBoxLayout()

        counter_btn = QPushButton("🛡️ Counter-Maneuver")
        counter_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold; padding: 10px;")
        counter_btn.clicked.connect(self._choose_counter_maneuver)
        decision_layout.addWidget(counter_btn)

        allow_btn = QPushButton("✅ Allow Maneuver")
        allow_btn.setStyleSheet("background-color: #51cf66; color: white; font-weight: bold; padding: 10px;")
        allow_btn.clicked.connect(self._choose_allow_maneuver)
        decision_layout.addWidget(allow_btn)

        decision_widget = QWidget()
        decision_widget.setLayout(decision_layout)
        self.content_layout.addWidget(decision_widget)

    def _show_simultaneous_rolls(self):
        """Show simultaneous dice rolling for both armies."""
        self.step_label.setText("Step 3: 🎲 Simultaneous Maneuver Rolls")
        self.results_display.show()

        # Instructions
        instructions = QLabel(
            "Both armies roll dice simultaneously. Enter each die face result.<br>"
            "Count maneuver results, SAIs, and applicable species abilities."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f8ff;")
        self.content_layout.addWidget(instructions)

        # Two-column layout for both armies
        armies_layout = QHBoxLayout()

        # Maneuvering army
        maneuvering_group = QGroupBox(f"Maneuvering Army - {self.maneuvering_player}")
        maneuvering_layout = QVBoxLayout(maneuvering_group)

        self.maneuvering_roll_widgets = []
        army_units = self.maneuvering_army.get("units", [])

        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_health = unit.get("health", 1)

            unit_widget = ManeuverDieRollInputWidget(unit_name, unit_health)
            self.maneuvering_roll_widgets.append(unit_widget)
            maneuvering_layout.addWidget(unit_widget)

        armies_layout.addWidget(maneuvering_group)

        # Counter-maneuvering army (simplified - in reality would be multiple armies)
        if self.opposing_armies:
            counter_group = QGroupBox("Counter-Maneuvering Army")
            counter_layout = QVBoxLayout(counter_group)

            self.counter_roll_widgets = []
            # Use first opposing army for simplicity
            counter_army = self.opposing_armies[0] if self.opposing_armies else {"units": []}
            counter_units = counter_army.get("units", [])

            for unit in counter_units:
                unit_name = unit.get("name", "Unknown Unit")
                unit_health = unit.get("health", 1)

                unit_widget = ManeuverDieRollInputWidget(unit_name, unit_health)
                self.counter_roll_widgets.append(unit_widget)
                counter_layout.addWidget(unit_widget)

            armies_layout.addWidget(counter_group)

        armies_widget = QWidget()
        armies_widget.setLayout(armies_layout)
        self.content_layout.addWidget(armies_widget)

        # Species ability reminder
        terrain_elements = self._get_terrain_elements()
        if "earth" in terrain_elements:
            reminder = QLabel(
                "💡 Remember: At earth terrain, Dwarves (Mountain Master) and Goblins (Swamp Master) "
                "can count melee results as maneuver results!"
            )
            reminder.setStyleSheet("background-color: #fffbf0; padding: 10px; border: 1px solid #ffd43b;")
            reminder.setWordWrap(True)
            self.content_layout.addWidget(reminder)

    def _show_choose_direction(self):
        """Show terrain direction choice after successful maneuver."""
        self.step_label.setText("Step 4: 🎯 Choose Direction")
        self.results_display.show()

        # Show maneuver results
        results_text = "MANEUVER RESULTS:\n"
        results_text += f"Maneuvering Army: {self.final_maneuvering_total} maneuver\n"
        if self.will_be_opposed:
            results_text += f"Counter-Maneuver Army: {self.final_counter_total} maneuver\n"
            results_text += f"\nResult: {self.final_maneuvering_total} ≥ {self.final_counter_total} = SUCCESS!"
        else:
            results_text += "\nResult: No opposition = AUTOMATIC SUCCESS!"

        self.results_display.setText(results_text)

        # Direction choice
        direction_group = QGroupBox("Choose Terrain Direction")
        direction_layout = QVBoxLayout(direction_group)

        current_face = self.current_terrain_face

        direction_buttons_layout = QHBoxLayout()

        # UP button
        up_face = min(current_face + 1, 8)
        up_button = QPushButton(f"Turn UP\n(Face {current_face} → {up_face})")
        up_button.setStyleSheet("background-color: #339af0; color: white; font-weight: bold; padding: 15px;")
        up_button.clicked.connect(lambda: self._choose_direction("UP"))
        if current_face >= 8:
            up_button.setEnabled(False)
            up_button.setText("Turn UP\n(Already at Max)")
        direction_buttons_layout.addWidget(up_button)

        # DOWN button
        down_face = max(current_face - 1, 1)
        down_button = QPushButton(f"Turn DOWN\n(Face {current_face} → {down_face})")
        down_button.setStyleSheet("background-color: #ff8787; color: white; font-weight: bold; padding: 15px;")
        down_button.clicked.connect(lambda: self._choose_direction("DOWN"))
        if current_face <= 1:
            down_button.setEnabled(False)
            down_button.setText("Turn DOWN\n(Already at Min)")
        direction_buttons_layout.addWidget(down_button)

        direction_layout.addLayout(direction_buttons_layout)
        self.content_layout.addWidget(direction_group)

    def _choose_counter_maneuver(self):
        """Handle decision to counter-maneuver."""
        self.will_be_opposed = True
        self.current_step = "simultaneous_rolls"
        self._update_step_display()

    def _choose_allow_maneuver(self):
        """Handle decision to allow maneuver."""
        self.will_be_opposed = False
        # Skip to direction choice since maneuver automatically succeeds
        self.final_maneuvering_total = 1  # Automatic success
        self.final_counter_total = 0
        self.current_step = "choose_direction"
        self._update_step_display()

    def _choose_direction(self, direction: str):
        """Handle terrain direction choice."""
        self.chosen_direction = direction
        self._complete_maneuver()

    def _collect_maneuvering_results(self) -> bool:
        """Collect maneuvering army roll results."""
        if not hasattr(self, "maneuvering_roll_widgets"):
            return False

        self.maneuvering_results = {}
        army_units = self.maneuvering_army.get("units", [])

        for i, widget in enumerate(self.maneuvering_roll_widgets):
            if i < len(army_units):
                unit_name = army_units[i].get("name", f"Unit {i + 1}")
                face_results = widget.get_face_results()
                self.maneuvering_results[unit_name] = face_results

        return True

    def _collect_counter_results(self) -> bool:
        """Collect counter-maneuvering army roll results."""
        if not self.will_be_opposed or not hasattr(self, "counter_roll_widgets"):
            return True  # No counter-maneuver

        self.counter_results = {}
        if self.opposing_armies:
            counter_army = self.opposing_armies[0]
            counter_units = counter_army.get("units", [])

            for i, widget in enumerate(self.counter_roll_widgets):
                if i < len(counter_units):
                    unit_name = counter_units[i].get("name", f"Counter Unit {i + 1}")
                    face_results = widget.get_face_results()
                    self.counter_results[unit_name] = face_results

        return True

    def _calculate_maneuver_results(self):
        """Calculate final maneuver results with species abilities."""
        terrain_elements = self._get_terrain_elements()

        # Process maneuvering army results
        maneuvering_army_units = self.maneuvering_army.get("units", [])
        maneuvering_result = self.sai_processor.process_combat_roll(
            self.maneuvering_results,
            "maneuver",
            maneuvering_army_units,
            is_attacker=True,
            terrain_elements=terrain_elements,
        )
        self.final_maneuvering_total = maneuvering_result.final_maneuver

        # Process counter-maneuvering army results
        if self.will_be_opposed and self.opposing_armies:
            counter_army_units = self.opposing_armies[0].get("units", [])
            counter_result = self.sai_processor.process_combat_roll(
                self.counter_results,
                "maneuver",
                counter_army_units,
                is_attacker=False,
                terrain_elements=terrain_elements,
            )
            self.final_counter_total = counter_result.final_maneuver
        else:
            self.final_counter_total = 0

    def _complete_maneuver(self):
        """Complete the maneuver and emit results."""
        success = self.final_maneuvering_total >= self.final_counter_total

        # Calculate new terrain face
        old_face = self.current_terrain_face
        if success and self.chosen_direction:
            if self.chosen_direction == "UP":
                new_face = min(old_face + 1, 8)
            else:  # DOWN
                new_face = max(old_face - 1, 1)
        else:
            new_face = old_face  # Failed maneuver

        maneuver_result = {
            "success": success,
            "maneuvering_player": self.maneuvering_player,
            "location": self.location,
            "direction": self.chosen_direction,
            "old_face": old_face,
            "new_face": new_face,
            "maneuvering_total": self.final_maneuvering_total,
            "counter_total": self.final_counter_total,
            "was_opposed": self.will_be_opposed,
            "maneuvering_results": self.maneuvering_results,
            "counter_results": self.counter_results,
            "army": self.maneuvering_army,
            "timestamp": "now",
        }

        self.maneuver_completed.emit(maneuver_result)
        self.accept()

    def _get_terrain_elements(self) -> List[str]:
        """Get terrain elements for the maneuver location."""
        # Same logic as melee combat dialog
        terrain_mappings = {
            "Highland": ["fire", "earth"],
            "Flatland": ["air", "earth"],
            "Coastland": ["air", "water"],
            "Swampland": ["water", "earth"],
            "Wasteland": ["air", "fire"],
            "Feyland": ["water", "fire"],
            "Deadland": ["death"],
        }

        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in self.location.lower():
                return elements

        return []

    def _update_buttons(self):
        """Update button states based on current step."""
        if self.current_step == "announce_maneuver":
            self.back_button.setEnabled(False)
            if self.opposing_players:
                self.next_button.setText("Proceed ▶")
            else:
                self.next_button.setText("Auto-Success ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "counter_decision":
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(False)  # Decision buttons handle navigation
        elif self.current_step == "simultaneous_rolls":
            self.back_button.setEnabled(True)
            self.next_button.setText("Calculate Results ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "choose_direction":
            self.back_button.setEnabled(True)
            self.next_button.setEnabled(False)  # Direction buttons handle completion

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "counter_decision":
            self.current_step = "announce_maneuver"
        elif self.current_step == "simultaneous_rolls":
            self.current_step = "counter_decision"
        elif self.current_step == "choose_direction":
            if self.will_be_opposed:
                self.current_step = "simultaneous_rolls"
            else:
                self.current_step = "counter_decision"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "announce_maneuver":
            if self.opposing_players:
                self.current_step = "counter_decision"
            else:
                # No opposition, auto-succeed
                self.will_be_opposed = False
                self.final_maneuvering_total = 1
                self.final_counter_total = 0
                self.current_step = "choose_direction"

        elif self.current_step == "simultaneous_rolls":
            # Collect results and calculate
            if self._collect_maneuvering_results() and self._collect_counter_results():
                self._calculate_maneuver_results()
                self.current_step = "choose_direction"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self, "Input Required", "Please enter die face results for all units before proceeding."
                )
                return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.maneuver_cancelled.emit()
        self.reject()
