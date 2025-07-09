"""
Reserves Phase Dialog for Dragon Dice.

This dialog manages the final phase of each turn, consisting of:
1. Reinforce Step: Move units from Reserve Area to terrains
2. Retreat Step: Move units from terrains to Reserve Area

Special mechanics supported:
- Amazon Ivory magic generation in Reserves
- Firewalker Air Flight movement during Retreat Step
- Reserve spell casting restrictions
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ReserveUnitWidget(QWidget):
    """Widget for managing a single unit in the Reserve Area."""

    unit_selected = Signal(str, bool)  # unit_name, is_selected

    def __init__(self, unit_name: str, unit_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.unit_name = unit_name
        self.unit_data = unit_data
        self.is_selected = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the unit widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Selection checkbox
        self.selection_checkbox = QCheckBox()
        self.selection_checkbox.stateChanged.connect(self._on_selection_changed)
        layout.addWidget(self.selection_checkbox)

        # Unit info
        species = self.unit_data.get("species", "Unknown")
        health = self.unit_data.get("health", 1)
        elements = self.unit_data.get("elements", [])
        element_text = f" ({'/'.join(elements)})" if elements else ""

        unit_info_label = QLabel(f"{self.unit_name} - {species} (Health: {health}){element_text}")
        unit_info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(unit_info_label)

        # Spacer
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    def _on_selection_changed(self, state: int):
        """Handle selection state change."""
        self.is_selected = state == Qt.CheckState.Checked.value
        self.unit_selected.emit(self.unit_name, self.is_selected)

    def set_selected(self, selected: bool):
        """Set the selection state."""
        self.selection_checkbox.setChecked(selected)

    def get_unit_data(self) -> Dict[str, Any]:
        """Get the unit data."""
        return self.unit_data


class ReinforceStepWidget(QWidget):
    """Widget for the Reinforce Step of the Reserves Phase."""

    reinforcements_ready = Signal(dict)  # Emits reinforcement data

    def __init__(
        self, player_name: str, reserves_units: List[Dict[str, Any]], available_terrains: List[str], 
        existing_terrain_armies: Dict[str, Dict[str, Any]], parent=None
    ):
        super().__init__(parent)
        self.player_name = player_name
        self.reserves_units = reserves_units
        self.available_terrains = available_terrains
        self.existing_terrain_armies = existing_terrain_armies

        # Widget state
        self.unit_widgets: List[ReserveUnitWidget] = []
        self.selected_units: List[str] = []
        self.reinforcement_plan: Dict[str, List[str]] = {}  # terrain -> list of unit names
        self.new_army_names: Dict[str, str] = {}  # terrain -> new army name

        self._setup_ui()

    def _setup_ui(self):
        """Setup the reinforce step UI."""
        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(
            f"<b>Reinforce Step - {self.player_name}</b><br>"
            f"Move units from Reserve Area to terrains.<br>"
            f"<i>Units in Reserve Area: {len(self.reserves_units)}</i>"
        )
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #e8f5e8; border: 1px solid #4caf50;"
        )
        main_layout.addWidget(header_label)

        if not self.reserves_units:
            # No units in reserves
            no_units_label = QLabel("No units in Reserve Area. Skip to Retreat Step.")
            no_units_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_units_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
            main_layout.addWidget(no_units_label)
        else:
            # Units selection
            units_group = QGroupBox("Units in Reserve Area")
            units_layout = QVBoxLayout(units_group)

            # Scrollable unit list
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMaximumHeight(200)

            units_widget = QWidget()
            units_container_layout = QVBoxLayout(units_widget)

            for unit in self.reserves_units:
                unit_name = unit.get("name", "Unknown Unit")
                unit_widget = ReserveUnitWidget(unit_name, unit)
                unit_widget.unit_selected.connect(self._on_unit_selected)
                self.unit_widgets.append(unit_widget)
                units_container_layout.addWidget(unit_widget)

            scroll_area.setWidget(units_widget)
            units_layout.addWidget(scroll_area)

            main_layout.addWidget(units_group)

            # Deployment planning
            deployment_group = QGroupBox("Deployment Planning")
            deployment_layout = QVBoxLayout(deployment_group)

            # Terrain selection
            terrain_layout = QHBoxLayout()
            terrain_layout.addWidget(QLabel("Deploy to terrain:"))

            self.terrain_combo = QComboBox()
            self.terrain_combo.addItem("-- Select Terrain --")
            for terrain in self.available_terrains:
                self.terrain_combo.addItem(terrain)
            terrain_layout.addWidget(self.terrain_combo)

            self.add_deployment_button = QPushButton("Add to Deployment")
            self.add_deployment_button.clicked.connect(self._add_to_deployment)
            self.add_deployment_button.setEnabled(False)
            terrain_layout.addWidget(self.add_deployment_button)

            deployment_layout.addLayout(terrain_layout)

            # Deployment preview
            self.deployment_list = QListWidget()
            self.deployment_list.setMaximumHeight(100)
            deployment_layout.addWidget(QLabel("Deployment Plan:"))
            deployment_layout.addWidget(self.deployment_list)

            main_layout.addWidget(deployment_group)

            # Control buttons
            control_layout = QHBoxLayout()

            self.select_all_button = QPushButton("Select All")
            self.select_all_button.clicked.connect(self._select_all_units)
            control_layout.addWidget(self.select_all_button)

            self.clear_selection_button = QPushButton("Clear Selection")
            self.clear_selection_button.clicked.connect(self._clear_selection)
            control_layout.addWidget(self.clear_selection_button)

            control_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

            self.clear_plan_button = QPushButton("Clear Plan")
            self.clear_plan_button.clicked.connect(self._clear_deployment_plan)
            control_layout.addWidget(self.clear_plan_button)

            main_layout.addLayout(control_layout)

    def _on_unit_selected(self, unit_name: str, is_selected: bool):
        """Handle unit selection change."""
        if is_selected and unit_name not in self.selected_units:
            self.selected_units.append(unit_name)
        elif not is_selected and unit_name in self.selected_units:
            self.selected_units.remove(unit_name)

        # Update UI state
        self.add_deployment_button.setEnabled(len(self.selected_units) > 0 and self.terrain_combo.currentIndex() > 0)

    def _add_to_deployment(self):
        """Add selected units to deployment plan."""
        if not self.selected_units or self.terrain_combo.currentIndex() == 0:
            return

        terrain = self.terrain_combo.currentText()

        # Check if player has existing army at this terrain
        has_existing_army = terrain in self.existing_terrain_armies
        
        # If no existing army, need to create new army and get name
        if not has_existing_army and terrain not in self.new_army_names:
            army_name = self._get_new_army_name(terrain)
            if not army_name:
                return  # User cancelled
            self.new_army_names[terrain] = army_name

        # Add to deployment plan
        if terrain not in self.reinforcement_plan:
            self.reinforcement_plan[terrain] = []

        for unit_name in self.selected_units:
            if unit_name not in self.reinforcement_plan[terrain]:
                self.reinforcement_plan[terrain].append(unit_name)

        # Update deployment list
        self._update_deployment_list()

        # Clear selection
        self._clear_selection()

    def _get_new_army_name(self, terrain: str) -> str:
        """Get a name for a new army at a terrain."""
        dialog_title = "New Army Name"
        dialog_text = (
            f"You are sending units to {terrain} where you don't have an existing army.\n"
            f"A new army will be created. What would you like to name this army?\n\n"
            f"(Cannot be 'Home', 'Campaign', or 'Horde' as these are reserved names)"
        )
        
        while True:
            army_name, ok = QInputDialog.getText(
                self, dialog_title, dialog_text, text=f"{terrain} Army"
            )
            
            if not ok:
                return ""  # User cancelled
            
            army_name = army_name.strip()
            
            # Validate army name
            if not army_name:
                QMessageBox.warning(self, "Invalid Name", "Army name cannot be empty.")
                continue
            
            # Check for reserved names
            reserved_names = ["Home", "Campaign", "Horde"]
            if army_name in reserved_names:
                QMessageBox.warning(
                    self, "Invalid Name", 
                    f"'{army_name}' is a reserved army name. Please choose a different name."
                )
                continue
            
            # Check for duplicate names (if we're creating multiple new armies)
            if army_name in self.new_army_names.values():
                QMessageBox.warning(
                    self, "Invalid Name", 
                    f"You've already chosen '{army_name}' for another new army. Please choose a different name."
                )
                continue
            
            return army_name

    def _update_deployment_list(self):
        """Update the deployment plan display."""
        self.deployment_list.clear()

        for terrain, unit_names in self.reinforcement_plan.items():
            if unit_names:
                # Check if this terrain has existing army or needs new army
                has_existing_army = terrain in self.existing_terrain_armies
                new_army_name = self.new_army_names.get(terrain, "")
                
                if has_existing_army:
                    item_text = f"{terrain}: {', '.join(unit_names)} (joining existing army)"
                elif new_army_name:
                    item_text = f"{terrain}: {', '.join(unit_names)} (new army: '{new_army_name}')"
                else:
                    item_text = f"{terrain}: {', '.join(unit_names)}"
                    
                self.deployment_list.addItem(item_text)

    def _select_all_units(self):
        """Select all units in reserves."""
        for widget in self.unit_widgets:
            widget.set_selected(True)

    def _clear_selection(self):
        """Clear unit selection."""
        for widget in self.unit_widgets:
            widget.set_selected(False)
        self.selected_units.clear()

    def _clear_deployment_plan(self):
        """Clear the deployment plan."""
        self.reinforcement_plan.clear()
        self._update_deployment_list()

    def get_reinforcement_plan(self) -> Dict[str, List[str]]:
        """Get the current reinforcement plan."""
        return self.reinforcement_plan.copy()

    def has_reinforcements(self) -> bool:
        """Check if there are any reinforcements planned."""
        return bool(self.reinforcement_plan)


class RetreatStepWidget(QWidget):
    """Widget for the Retreat Step of the Reserves Phase."""

    retreat_ready = Signal(dict)  # Emits retreat data

    def __init__(self, player_name: str, terrain_armies: Dict[str, Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.terrain_armies = terrain_armies

        # Widget state
        self.retreat_plan: Dict[str, List[str]] = {}  # terrain -> list of unit names to retreat
        self.air_flight_plan: Dict[str, List[str]] = {}  # terrain -> list of Firewalker units for air flight
        self.burial_plan: List[str] = []  # List of unit names to bury from DUA to BUA

        self._setup_ui()

    def _setup_ui(self):
        """Setup the retreat step UI."""
        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(
            f"<b>Retreat Step - {self.player_name}</b><br>"
            f"Move units from terrains to Reserve Area.<br>"
            f"<i>Firewalker Air Flight movement is also available.</i>"
        )
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fff3e0; border: 1px solid #ff9800;"
        )
        main_layout.addWidget(header_label)

        # Tab widget for different retreat options
        self.tab_widget = QTabWidget()

        # Regular retreat tab
        retreat_tab = self._create_retreat_tab()
        self.tab_widget.addTab(retreat_tab, "🏃 Regular Retreat")

        # Air flight tab
        air_flight_tab = self._create_air_flight_tab()
        self.tab_widget.addTab(air_flight_tab, "🌪️ Firewalker Air Flight")

        # Burial tab (for moving units from DUA to BUA)
        burial_tab = self._create_burial_tab()
        self.tab_widget.addTab(burial_tab, "⚰️ Bury Dead Units")

        main_layout.addWidget(self.tab_widget)

    def _create_retreat_tab(self) -> QWidget:
        """Create the regular retreat tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        if not self.terrain_armies:
            no_armies_label = QLabel("No armies at terrains. Nothing to retreat.")
            no_armies_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_armies_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
            layout.addWidget(no_armies_label)
            return tab

        # Terrain armies
        for terrain, army_data in self.terrain_armies.items():
            terrain_group = QGroupBox(f"Army at {terrain}")
            terrain_layout = QVBoxLayout(terrain_group)

            units = army_data.get("units", [])
            if not units:
                continue

            # Unit selection for retreat
            for unit in units:
                unit_name = unit.get("name", "Unknown Unit")
                species = unit.get("species", "Unknown")
                health = unit.get("health", 1)

                unit_layout = QHBoxLayout()

                checkbox = QCheckBox(f"{unit_name} - {species} (Health: {health})")
                checkbox.stateChanged.connect(
                    lambda state, t=terrain, u=unit_name: self._on_retreat_unit_selected(t, u, state)
                )
                unit_layout.addWidget(checkbox)

                terrain_layout.addLayout(unit_layout)

            layout.addWidget(terrain_group)

        return tab

    def _create_air_flight_tab(self) -> QWidget:
        """Create the Firewalker Air Flight tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "Firewalker Air Flight allows Firewalker units to move from any air terrain "
            "to any other air terrain that already contains at least one Firewalker unit."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f8ff; border: 1px solid #2196f3;")
        layout.addWidget(instructions)

        # Find air terrains with Firewalkers
        air_terrains_with_firewalkers = []
        air_terrains_without_firewalkers = []

        for terrain, army_data in self.terrain_armies.items():
            terrain_elements = self._get_terrain_elements(terrain)
            if "air" in terrain_elements:  # Check if terrain contains air element
                units = army_data.get("units", [])
                has_firewalker = any(unit.get("species") == "Firewalkers" for unit in units)
                firewalker_units = [unit for unit in units if unit.get("species") == "Firewalkers"]

                if has_firewalker:
                    air_terrains_with_firewalkers.append((terrain, firewalker_units))
                else:
                    air_terrains_without_firewalkers.append((terrain, units))

        if not air_terrains_with_firewalkers:
            no_firewalkers_label = QLabel("No Firewalker units at air terrains for Air Flight.")
            no_firewalkers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_firewalkers_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
            layout.addWidget(no_firewalkers_label)
            return tab

        # Air flight planning
        for terrain, firewalker_units in air_terrains_with_firewalkers:
            terrain_group = QGroupBox(f"Firewalkers at {terrain}")
            terrain_layout = QVBoxLayout(terrain_group)

            for unit in firewalker_units:
                unit_name = unit.get("name", "Unknown Unit")
                health = unit.get("health", 1)

                unit_layout = QHBoxLayout()

                checkbox = QCheckBox(f"{unit_name} (Health: {health})")
                checkbox.stateChanged.connect(
                    lambda state, t=terrain, u=unit_name: self._on_air_flight_unit_selected(t, u, state)
                )
                unit_layout.addWidget(checkbox)

                # Destination selection
                dest_combo = QComboBox()
                dest_combo.addItem("-- Select Destination --")
                for dest_terrain, _ in air_terrains_with_firewalkers:
                    if dest_terrain != terrain:  # Can't move to same terrain
                        dest_combo.addItem(dest_terrain)
                dest_combo.currentTextChanged.connect(
                    lambda destination, t=terrain, u=unit_name: self._on_air_flight_destination_changed(t, u, destination)
                )
                unit_layout.addWidget(dest_combo)

                terrain_layout.addLayout(unit_layout)

            layout.addWidget(terrain_group)

        return tab

    def _create_burial_tab(self) -> QWidget:
        """Create the burial tab for moving units from DUA to BUA."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "During the Retreat Step, you may bury dead units from your DUA (Dead Units Area) "
            "to your BUA (Buried Units Area). Buried units can be targeted by spells but not by most other effects."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f5f5f5; border: 1px solid #666;")
        layout.addWidget(instructions)

        # Check if player has dead units in DUA
        # Note: This would need to be passed from the main dialog or retrieved from DUA manager
        # For now, we'll create a placeholder that shows the concept
        dua_placeholder = QLabel(
            "📋 Dead Units in DUA:\n"
            "• Select dead units below to bury them in your BUA\n"
            "• Buried units are removed from DUA and placed in BUA\n"
            "• This integration requires DUA Manager to be passed to this dialog"
        )
        dua_placeholder.setWordWrap(True)
        dua_placeholder.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #fff3e0; border: 1px solid #ff9800;"
        )
        layout.addWidget(dua_placeholder)

        # Placeholder for DUA units selection
        # This would be populated with actual DUA units when DUA manager is integrated
        placeholder_group = QGroupBox("Dead Units Available for Burial")
        placeholder_layout = QVBoxLayout(placeholder_group)
        
        placeholder_text = QLabel(
            "This section will show dead units from your DUA when integrated with DUA Manager.\n"
            "Each unit will have a checkbox to select it for burial."
        )
        placeholder_text.setWordWrap(True)
        placeholder_text.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        placeholder_layout.addWidget(placeholder_text)
        
        layout.addWidget(placeholder_group)

        # Burial controls
        burial_controls = QHBoxLayout()
        
        select_all_button = QPushButton("Select All for Burial")
        select_all_button.clicked.connect(self._select_all_for_burial)
        burial_controls.addWidget(select_all_button)
        
        clear_burial_button = QPushButton("Clear Burial Selection")
        clear_burial_button.clicked.connect(self._clear_burial_selection)
        burial_controls.addWidget(clear_burial_button)
        
        layout.addLayout(burial_controls)

        return tab

    def _select_all_for_burial(self):
        """Select all dead units for burial."""
        # Placeholder - would interact with DUA manager
        print("BurialTab: Select all units for burial (placeholder)")

    def _clear_burial_selection(self):
        """Clear burial selection."""
        self.burial_plan.clear()
        print("BurialTab: Cleared burial selection")

    def get_burial_plan(self) -> List[str]:
        """Get the current burial plan."""
        return self.burial_plan.copy()

    def has_burials(self) -> bool:
        """Check if there are any burials planned."""
        return bool(self.burial_plan)

    def _on_retreat_unit_selected(self, terrain: str, unit_name: str, state: int):
        """Handle unit selection for retreat."""
        is_selected = state == Qt.CheckState.Checked.value

        if terrain not in self.retreat_plan:
            self.retreat_plan[terrain] = []

        if is_selected and unit_name not in self.retreat_plan[terrain]:
            self.retreat_plan[terrain].append(unit_name)
        elif not is_selected and unit_name in self.retreat_plan[terrain]:
            self.retreat_plan[terrain].remove(unit_name)

        # Clean up empty entries
        if not self.retreat_plan[terrain]:
            del self.retreat_plan[terrain]

    def _on_air_flight_unit_selected(self, terrain: str, unit_name: str, state: int):
        """Handle Firewalker unit selection for air flight."""
        is_selected = state == Qt.CheckState.Checked.value

        if terrain not in self.air_flight_plan:
            self.air_flight_plan[terrain] = []

        if is_selected and unit_name not in self.air_flight_plan[terrain]:
            self.air_flight_plan[terrain].append(unit_name)
        elif not is_selected and unit_name in self.air_flight_plan[terrain]:
            self.air_flight_plan[terrain].remove(unit_name)

        # Clean up empty entries
        if not self.air_flight_plan[terrain]:
            del self.air_flight_plan[terrain]

    def _on_air_flight_destination_changed(self, terrain: str, unit_name: str, destination: str):
        """Handle destination change for air flight."""
        if destination == "-- Select Destination --":
            return
        
        # Store the destination choice for this specific unit
        # This would need more complex handling to store unit->destination mappings
        # For now, we'll keep it simple and just note that the destination was selected
        print(f"AirFlight: {unit_name} from {terrain} selected destination {destination}")

    def get_retreat_plan(self) -> Dict[str, List[str]]:
        """Get the current retreat plan."""
        return self.retreat_plan.copy()

    def get_air_flight_plan(self) -> Dict[str, List[str]]:
        """Get the current air flight plan."""
        return self.air_flight_plan.copy()

    def has_retreats(self) -> bool:
        """Check if there are any retreats planned."""
        return bool(self.retreat_plan) or bool(self.air_flight_plan) or bool(self.burial_plan)

    def _get_terrain_elements(self, terrain_name: str) -> List[str]:
        """Get the elements present in a terrain."""
        # This is a simplified implementation - in reality would check terrain data
        # For now, extract elements from terrain name
        elements = []
        terrain_lower = terrain_name.lower()

        if "air" in terrain_lower or "wind" in terrain_lower or "sky" in terrain_lower:
            elements.append("air")
        if "earth" in terrain_lower or "mountain" in terrain_lower or "stone" in terrain_lower:
            elements.append("earth")
        if "fire" in terrain_lower or "lava" in terrain_lower or "flame" in terrain_lower:
            elements.append("fire")
        if "water" in terrain_lower or "sea" in terrain_lower or "river" in terrain_lower:
            elements.append("water")
        if "death" in terrain_lower or "swamp" in terrain_lower or "shadow" in terrain_lower:
            elements.append("death")

        return elements


class ReservesPhaseDialog(QDialog):
    """
    Dialog for managing the Reserves Phase of Dragon Dice.

    Handles both Reinforce Step and Retreat Step with proper sequencing.
    """

    phase_completed = Signal(dict)  # Emits phase results
    phase_cancelled = Signal()

    def __init__(
        self,
        player_name: str,
        reserves_units: List[Dict[str, Any]],
        terrain_armies: Dict[str, Dict[str, Any]],
        available_terrains: List[str],
        parent=None,
    ):
        super().__init__(parent)
        self.player_name = player_name
        self.reserves_units = reserves_units
        self.terrain_armies = terrain_armies
        self.available_terrains = available_terrains

        # Phase state
        self.current_step = "reinforce"  # "reinforce" or "retreat"
        self.reinforcement_results = {}
        self.retreat_results = {}

        self.setWindowTitle(f"🏰 Reserves Phase - {player_name}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the reserves phase UI."""
        main_layout = QVBoxLayout(self)

        # Phase header
        phase_header = QLabel(
            f"<b>Reserves Phase - {self.player_name}</b><br>"
            f"Final phase of the turn. Complete both steps in order:<br>"
            f"1. <b>Reinforce Step</b>: Move units from Reserve Area to terrains<br>"
            f"2. <b>Retreat Step</b>: Move units from terrains to Reserve Area"
        )
        phase_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_header.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 15px; background-color: #f3e5f5; border: 1px solid #9c27b0;"
        )
        main_layout.addWidget(phase_header)

        # Step tabs
        self.step_tabs = QTabWidget()

        # Reinforce step
        self.reinforce_widget = ReinforceStepWidget(
            self.player_name, self.reserves_units, self.available_terrains, self.terrain_armies
        )
        self.step_tabs.addTab(self.reinforce_widget, "🔄 Reinforce Step")

        # Retreat step
        self.retreat_widget = RetreatStepWidget(self.player_name, self.terrain_armies)
        self.step_tabs.addTab(self.retreat_widget, "🏃 Retreat Step")

        # Initially enable only reinforce step
        self.step_tabs.setTabEnabled(1, False)  # Disable retreat step initially

        main_layout.addWidget(self.step_tabs)

        # Control buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("❌ Cancel Phase")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.back_button = QPushButton("⬅️ Back to Reinforce")
        self.back_button.clicked.connect(self._go_back_to_reinforce)
        self.back_button.setVisible(False)
        button_layout.addWidget(self.back_button)

        self.next_button = QPushButton("➡️ Continue to Retreat")
        self.next_button.clicked.connect(self._continue_to_retreat)
        button_layout.addWidget(self.next_button)

        self.complete_button = QPushButton("✅ Complete Phase")
        self.complete_button.clicked.connect(self._complete_phase)
        self.complete_button.setVisible(False)
        button_layout.addWidget(self.complete_button)

        main_layout.addLayout(button_layout)

    def _continue_to_retreat(self):
        """Continue to the retreat step."""
        # Store reinforce results
        self.reinforcement_results = {
            "reinforcement_plan": self.reinforce_widget.get_reinforcement_plan(),
            "new_army_names": self.reinforce_widget.new_army_names.copy(),
        }

        # Switch to retreat step
        self.current_step = "retreat"
        self.step_tabs.setCurrentIndex(1)
        self.step_tabs.setTabEnabled(1, True)
        self.step_tabs.setTabEnabled(0, False)  # Disable reinforce step

        # Update buttons
        self.next_button.setVisible(False)
        self.back_button.setVisible(True)
        self.complete_button.setVisible(True)

    def _go_back_to_reinforce(self):
        """Go back to the reinforce step."""
        self.current_step = "reinforce"
        self.step_tabs.setCurrentIndex(0)
        self.step_tabs.setTabEnabled(0, True)
        self.step_tabs.setTabEnabled(1, False)

        # Update buttons
        self.next_button.setVisible(True)
        self.back_button.setVisible(False)
        self.complete_button.setVisible(False)

    def _complete_phase(self):
        """Complete the reserves phase."""
        # Store retreat results
        self.retreat_results = {
            "retreat_plan": self.retreat_widget.get_retreat_plan(),
            "air_flight_plan": self.retreat_widget.get_air_flight_plan(),
            "burial_plan": self.retreat_widget.get_burial_plan(),
        }

        # Create comprehensive results
        phase_results = {
            "success": True,
            "player_name": self.player_name,
            "phase_type": "reserves",
            "reinforce_step": {
                "reinforcement_plan": self.reinforcement_results.get("reinforcement_plan", {}),
                "new_army_names": self.reinforcement_results.get("new_army_names", {}),
                "units_reinforced": sum(len(units) for units in self.reinforcement_results.get("reinforcement_plan", {}).values()),
            },
            "retreat_step": {
                "retreat_plan": self.retreat_results["retreat_plan"],
                "air_flight_plan": self.retreat_results["air_flight_plan"],
                "burial_plan": self.retreat_results["burial_plan"],
                "units_retreated": sum(len(units) for units in self.retreat_results["retreat_plan"].values()),
                "firewalkers_moved": sum(len(units) for units in self.retreat_results["air_flight_plan"].values()),
                "units_buried": len(self.retreat_results["burial_plan"]),
            },
            "timestamp": "now",
        }

        self.phase_completed.emit(phase_results)
        self.accept()

    def _on_cancel(self):
        """Cancel the reserves phase."""
        self.phase_cancelled.emit()
        self.reject()
