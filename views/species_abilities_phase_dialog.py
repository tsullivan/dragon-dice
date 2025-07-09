"""
Species Abilities Phase Dialog for Dragon Dice.

This dialog manages the Species Abilities Phase, which occurs during the marching player's turn
after Dragon Attacks but before any marching. Each species has unique abilities that can be
used during this phase.

Currently supported species abilities:
- Swamp Stalkers: Mutate (target units in opponent's Reserves Area)
- Eldarim: Dragonkin Handlers (move/promote Dragonkin units)
- Feral: Feralization (recruit/promote Feral units)
- Frostwings: Winter's Fortitude (move units from BUA to DUA)
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from game_logic.dua_manager import DUAManager
from game_logic.reserves_manager import ReservesManager


class MutateAbilityWidget(QWidget):
    """Widget for managing Swamp Stalkers' Mutate ability."""

    mutate_requested = Signal(dict)  # Emits mutate attempt data

    def __init__(
        self,
        swamp_stalker_player: str,
        swamp_stalker_armies: List[Dict[str, Any]],
        opponent_reserves: Dict[str, List[Dict[str, Any]]],  # opponent_name -> reserve_units
        dead_swamp_stalkers_count: int,
        game_points: int = 24,
        parent=None,
    ):
        super().__init__(parent)
        self.swamp_stalker_player = swamp_stalker_player
        self.swamp_stalker_armies = swamp_stalker_armies
        self.opponent_reserves = opponent_reserves
        self.dead_swamp_stalkers_count = dead_swamp_stalkers_count
        self.game_points = game_points

        # Calculate s-value scaling
        self.s_value = max(1, game_points // 24)
        self.max_targets = min(dead_swamp_stalkers_count, self.s_value)

        # Selection state
        self.selected_targets: List[Dict[str, Any]] = []
        self.selected_recruiting_army: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the Mutate ability UI."""
        main_layout = QVBoxLayout(self)

        # Header
        header_info = QLabel(
            f"<b>Swamp Stalkers Mutate Ability</b><br>"
            f"Target units in opponent's Reserves Area. Units that fail save rolls are killed.<br>"
            f"You can then recruit/promote Swamp Stalkers equal to the health-worth killed.<br>"
            f"<b>Dead Swamp Stalkers in DUA:</b> {self.dead_swamp_stalkers_count}<br>"
            f"<b>Maximum targets:</b> {self.max_targets} (s-value: {self.s_value})"
        )
        header_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_info.setWordWrap(True)
        header_info.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 10px; background-color: #f0f8e8; border: 1px solid #8bc34a;"
        )
        main_layout.addWidget(header_info)

        # Check if mutate is possible
        total_opponent_reserves = sum(len(units) for units in self.opponent_reserves.values())
        if total_opponent_reserves == 0:
            no_targets_label = QLabel("❌ No opponent units in Reserves Area. Mutate cannot be used.")
            no_targets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_targets_label.setStyleSheet("color: #d32f2f; font-size: 16px; margin: 20px;")
            main_layout.addWidget(no_targets_label)
            return

        if self.max_targets == 0:
            no_dead_label = QLabel("❌ No dead Swamp Stalkers in DUA. Mutate cannot be used.")
            no_dead_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_dead_label.setStyleSheet("color: #d32f2f; font-size: 16px; margin: 20px;")
            main_layout.addWidget(no_dead_label)
            return

        # Target selection
        target_group = QGroupBox("Select Target Units in Opponent's Reserves")
        target_layout = QVBoxLayout(target_group)

        # Show opponents and their reserve units
        self.target_checkboxes: List[QCheckBox] = []
        for opponent_name, reserve_units in self.opponent_reserves.items():
            if not reserve_units:
                continue

            opponent_label = QLabel(f"<b>{opponent_name}'s Reserves:</b>")
            target_layout.addWidget(opponent_label)

            for unit in reserve_units:
                unit_name = unit.get("name", "Unknown Unit")
                unit_species = unit.get("species", "Unknown")
                unit_health = unit.get("health", 1)

                checkbox = QCheckBox(f"{unit_name} - {unit_species} (Health: {unit_health})")
                checkbox.setProperty("unit_data", unit)
                checkbox.setProperty("opponent_name", opponent_name)
                checkbox.stateChanged.connect(self._on_target_selected)
                self.target_checkboxes.append(checkbox)
                target_layout.addWidget(checkbox)

        main_layout.addWidget(target_group)

        # Recruiting army selection
        army_group = QGroupBox("Select Army for Recruitment/Promotion")
        army_layout = QVBoxLayout(army_group)

        army_info = QLabel(
            "Choose which army containing Swamp Stalkers will receive the recruited/promoted units:"
        )
        army_info.setWordWrap(True)
        army_layout.addWidget(army_info)

        self.army_list = QListWidget()
        self.army_list.setMaximumHeight(150)
        for army in self.swamp_stalker_armies:
            army_name = army.get("name", "Unknown Army")
            army_location = army.get("location", "Unknown Location")
            swamp_stalker_count = len([u for u in army.get("units", []) if u.get("species") == "Swamp Stalkers"])

            item_text = f"{army_name} at {army_location} ({swamp_stalker_count} Swamp Stalkers)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, army)
            self.army_list.addItem(item)

        self.army_list.currentItemChanged.connect(self._on_army_selected)
        army_layout.addWidget(self.army_list)

        main_layout.addWidget(army_group)

        # Selection status
        self.status_label = QLabel("Select up to {} target units and a recruiting army".format(self.max_targets))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; margin: 10px; padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self._clear_selection)
        button_layout.addWidget(self.clear_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.mutate_button = QPushButton("🧬 Attempt Mutate")
        self.mutate_button.clicked.connect(self._attempt_mutate)
        self.mutate_button.setEnabled(False)
        button_layout.addWidget(self.mutate_button)

        main_layout.addLayout(button_layout)

    def _on_target_selected(self, state: int):
        """Handle target unit selection."""
        sender = self.sender()
        is_checked = state == Qt.CheckState.Checked.value

        if is_checked:
            # Check if we've reached the limit
            if len(self.selected_targets) >= self.max_targets:
                # Uncheck this box
                sender.setChecked(False)
                return

            # Add to selected targets
            unit_data = sender.property("unit_data")
            opponent_name = sender.property("opponent_name")
            self.selected_targets.append({
                "unit_data": unit_data,
                "opponent_name": opponent_name,
                "checkbox": sender,
            })
        else:
            # Remove from selected targets
            self.selected_targets = [
                target for target in self.selected_targets if target["checkbox"] != sender
            ]

        self._update_status()

    def _on_army_selected(self):
        """Handle recruiting army selection."""
        current_item = self.army_list.currentItem()
        if current_item:
            army_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_recruiting_army = army_data
        else:
            self.selected_recruiting_army = None

        self._update_status()

    def _update_status(self):
        """Update the status display and button states."""
        targets_selected = len(self.selected_targets)
        army_selected = self.selected_recruiting_army is not None

        # Update status text
        status_parts = []
        if targets_selected > 0:
            status_parts.append(f"Targets: {targets_selected}/{self.max_targets}")
        if army_selected:
            army_name = self.selected_recruiting_army.get("name", "Unknown")
            status_parts.append(f"Army: {army_name}")

        if status_parts:
            self.status_label.setText(" | ".join(status_parts))
        else:
            self.status_label.setText("Select up to {} target units and a recruiting army".format(self.max_targets))

        # Update button states
        can_mutate = targets_selected > 0 and army_selected
        self.mutate_button.setEnabled(can_mutate)

        # Update status styling
        if can_mutate:
            self.status_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 5px; background-color: #e8f5e8; color: #2e7d32;"
            )
        else:
            self.status_label.setStyleSheet(
                "font-weight: bold; margin: 10px; padding: 5px; background-color: #f0f0f0; color: #666;"
            )

    def _clear_selection(self):
        """Clear all selections."""
        for checkbox in self.target_checkboxes:
            checkbox.setChecked(False)
        self.selected_targets.clear()
        self.army_list.clearSelection()
        self.selected_recruiting_army = None
        self._update_status()

    def _attempt_mutate(self):
        """Attempt the Mutate ability."""
        if not self.selected_targets or not self.selected_recruiting_army:
            return

        mutate_data = {
            "ability_type": "mutate",
            "swamp_stalker_player": self.swamp_stalker_player,
            "targets": self.selected_targets,
            "recruiting_army": self.selected_recruiting_army,
            "dead_swamp_stalkers_count": self.dead_swamp_stalkers_count,
            "max_targets": self.max_targets,
            "s_value": self.s_value,
            "game_points": self.game_points,
        }

        self.mutate_requested.emit(mutate_data)


class SpeciesAbilitiesPhaseDialog(QDialog):
    """
    Dialog for managing the Species Abilities Phase.
    
    This phase occurs during the marching player's turn after Dragon Attacks
    but before any marching. Each species has unique abilities that can be used.
    """

    abilities_completed = Signal(dict)  # Emits phase results
    abilities_skipped = Signal()

    def __init__(
        self,
        player_name: str,
        player_armies: List[Dict[str, Any]],
        opponent_reserves: Dict[str, List[Dict[str, Any]]],
        dua_manager: DUAManager,
        reserves_manager: ReservesManager,
        game_points: int = 24,
        parent=None,
    ):
        super().__init__(parent)
        self.player_name = player_name
        self.player_armies = player_armies
        self.opponent_reserves = opponent_reserves
        self.dua_manager = dua_manager
        self.reserves_manager = reserves_manager
        self.game_points = game_points

        # Phase state
        self.available_abilities: List[str] = []
        self.used_abilities: List[Dict[str, Any]] = []

        self.setWindowTitle(f"🧬 Species Abilities Phase - {player_name}")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self._analyze_available_abilities()
        self._setup_ui()

    def _analyze_available_abilities(self):
        """Analyze which species abilities are available."""
        self.available_abilities = []

        # Check for Swamp Stalkers' Mutate ability
        if self._can_use_mutate():
            self.available_abilities.append("mutate")

        # Check for other species abilities (placeholder for future implementation)
        # if self._can_use_feralization():
        #     self.available_abilities.append("feralization")
        # if self._can_use_dragonkin_handlers():
        #     self.available_abilities.append("dragonkin_handlers")
        # if self._can_use_winters_fortitude():
        #     self.available_abilities.append("winters_fortitude")

    def _can_use_mutate(self) -> bool:
        """Check if Swamp Stalkers' Mutate ability can be used."""
        # Must have at least one army containing a Swamp Stalker at a terrain
        has_swamp_stalker_army = any(
            any(unit.get("species") == "Swamp Stalkers" for unit in army.get("units", []))
            for army in self.player_armies
        )
        if not has_swamp_stalker_army:
            return False

        # Must have at least one Swamp Stalker unit in DUA (or Deadlands minor terrain)
        player_dua = self.dua_manager.get_player_dua(self.player_name)
        dead_swamp_stalkers = [unit for unit in player_dua if unit.species == "Swamp Stalkers"]
        if not dead_swamp_stalkers:
            return False

        # An opposing player must have at least one unit in their Reserves Area
        total_opponent_reserves = sum(len(units) for units in self.opponent_reserves.values())
        if total_opponent_reserves == 0:
            return False

        return True

    def _setup_ui(self):
        """Setup the species abilities phase UI."""
        main_layout = QVBoxLayout(self)

        # Phase header
        phase_header = QLabel(
            f"<b>Species Abilities Phase - {self.player_name}</b><br>"
            f"Use your species' unique abilities before marching.<br>"
            f"This phase occurs after Dragon Attacks but before any marching actions."
        )
        phase_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_header.setWordWrap(True)
        phase_header.setStyleSheet(
            "font-size: 14px; margin: 10px; padding: 15px; background-color: #e8f5e8; border: 1px solid #4caf50;"
        )
        main_layout.addWidget(phase_header)

        if not self.available_abilities:
            # No abilities available
            no_abilities_label = QLabel(
                "No species abilities are available during this phase.\n"
                "Click 'Skip Phase' to proceed to First March."
            )
            no_abilities_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_abilities_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
            main_layout.addWidget(no_abilities_label)
        else:
            # Available abilities
            abilities_group = QGroupBox("Available Species Abilities")
            abilities_layout = QVBoxLayout(abilities_group)

            # Tab widget for different abilities
            self.abilities_tabs = QTabWidget()

            # Mutate ability tab
            if "mutate" in self.available_abilities:
                mutate_tab = self._create_mutate_tab()
                self.abilities_tabs.addTab(mutate_tab, "🧬 Swamp Stalkers: Mutate")

            # Add other ability tabs here in the future
            # if "feralization" in self.available_abilities:
            #     feral_tab = self._create_feralization_tab()
            #     self.abilities_tabs.addTab(feral_tab, "🐺 Feral: Feralization")

            abilities_layout.addWidget(self.abilities_tabs)
            main_layout.addWidget(abilities_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.skip_button = QPushButton("⏭️ Skip Phase")
        self.skip_button.clicked.connect(self._skip_phase)
        button_layout.addWidget(self.skip_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.complete_button = QPushButton("✅ Complete Phase")
        self.complete_button.clicked.connect(self._complete_phase)
        button_layout.addWidget(self.complete_button)

        main_layout.addLayout(button_layout)

    def _create_mutate_tab(self) -> QWidget:
        """Create the Mutate ability tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Get Swamp Stalker armies
        swamp_stalker_armies = [
            army for army in self.player_armies
            if any(unit.get("species") == "Swamp Stalkers" for unit in army.get("units", []))
        ]

        # Get dead Swamp Stalkers count
        player_dua = self.dua_manager.get_player_dua(self.player_name)
        dead_swamp_stalkers_count = len([unit for unit in player_dua if unit.species == "Swamp Stalkers"])

        # Create mutate widget
        self.mutate_widget = MutateAbilityWidget(
            swamp_stalker_player=self.player_name,
            swamp_stalker_armies=swamp_stalker_armies,
            opponent_reserves=self.opponent_reserves,
            dead_swamp_stalkers_count=dead_swamp_stalkers_count,
            game_points=self.game_points,
        )
        self.mutate_widget.mutate_requested.connect(self._on_mutate_requested)

        layout.addWidget(self.mutate_widget)

        return tab

    def _on_mutate_requested(self, mutate_data: Dict[str, Any]):
        """Handle Mutate ability request."""
        # Process the mutate attempt
        self.used_abilities.append(mutate_data)

        # Update UI to show the ability was used
        self.mutate_widget.setEnabled(False)
        
        # Add a status message
        status_msg = QLabel(
            f"🧬 Mutate ability used! Targeting {len(mutate_data['targets'])} units. "
            f"Proceed to resolve save rolls."
        )
        status_msg.setStyleSheet("color: #2e7d32; font-weight: bold; margin: 10px;")
        status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to the mutate tab
        mutate_tab = self.abilities_tabs.widget(0)
        mutate_tab.layout().addWidget(status_msg)

    def _skip_phase(self):
        """Skip the Species Abilities Phase."""
        self.abilities_skipped.emit()
        self.accept()

    def _complete_phase(self):
        """Complete the Species Abilities Phase."""
        phase_results = {
            "success": True,
            "player_name": self.player_name,
            "phase_type": "species_abilities",
            "available_abilities": self.available_abilities,
            "used_abilities": self.used_abilities,
            "abilities_count": len(self.used_abilities),
            "timestamp": "now",
        }

        self.abilities_completed.emit(phase_results)
        self.accept()