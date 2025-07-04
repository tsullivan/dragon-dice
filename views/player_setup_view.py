# views/player_setup_view.py
import random
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import utils.constants as constants
from components.army_setup_widget import ArmySetupWidget
from components.carousel import CarouselInputWidget
from components.dragon_selection_widget import DragonSelectionWidget
from components.player_identity_widget import PlayerIdentityWidget
from components.tabbed_view_widget import TabbedViewWidget
from components.terrain_selection_widget import (
    TerrainSelectionWidget,
)
from config.resource_manager import ResourceManager
from models.army_model import format_army_type_display, get_all_army_types
from models.help_text_model import HelpTextModel
from models.unit_roster_model import UnitRosterModel


class PlayerSetupView(QWidget):
    """
    The Player Setup Screen view.
    Allows input for player name, home terrain, army names, and points.
    """

    # Emits (player_index, player_data_dict)
    player_data_finalized = Signal(int, dict)
    back_signal = Signal(int)  # Emit the current player index

    def __init__(
        self,
        num_players: int,
        terrain_display_options: list,  # List of tuples (name, colors)
        required_dragons: int,  # No change, good comment
        force_size: int,  # Total force size in points for army validation
        app_data_model,  # AppDataModel instance
        initial_player_data: Optional[dict] = None,
        parent=None,
        current_player_index: int = 0,
    ):
        super().__init__(parent)
        self.num_players = num_players
        self.initial_player_data = initial_player_data
        self.terrain_display_options = terrain_display_options
        if self.terrain_display_options and isinstance(self.terrain_display_options[0], tuple):
            self.all_terrain_options = [name for name, _ in self.terrain_display_options]
        else:
            self.all_terrain_options = self.terrain_display_options

        self.required_dragons = required_dragons  # No change, good comment
        self.force_size = force_size  # Store total force size for army validation
        # Official rules: max 50% per army (rounded down)
        self.max_points_per_army = force_size // 2
        self.app_data_model = app_data_model
        self.resource_manager = ResourceManager()
        self.unit_roster = UnitRosterModel(app_data_model)
        self.help_model = HelpTextModel()
        self.current_player_index = current_player_index

        self.preselected_names = self.resource_manager.load_names()

        self.player_data: Dict = {}  # To store data for the current player
        self.army_units_data: Dict[str, List[Dict]] = {}  # {army_type: list of unit dicts}
        self.army_detailed_units_labels: Dict[str, QTextEdit] = {}  # {army_type: QLabel for detailed unit list}
        self.dragon_selection_carousels: List[CarouselInputWidget] = []
        self.setWindowTitle(f"Player {self.current_player_index + 1} Setup")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title and Global Randomize Button
        title_layout = QHBoxLayout()
        self.title_label = QLabel(f"Player {self.current_player_index + 1} Setup")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(title_layout)

        # Tabbed Interface (Game and Help)
        self.tabbed_widget = TabbedViewWidget()

        # Game Tab Content (Player Setup Form)
        game_content_layout = QVBoxLayout()

        # Remove the outer fieldset and create individual ones for each section

        # Instantiate PlayerIdentityWidget to get its components
        self.player_identity_widget = PlayerIdentityWidget(self.current_player_index + 1)

        # Player Name Section with fieldset
        player_name_group = QGroupBox("Player Name")
        player_name_layout = QHBoxLayout(player_name_group)
        player_name_layout.addWidget(self.player_identity_widget.player_name_input)

        # Small inline dice button
        self.global_randomize_button = QPushButton(constants.UI_ICONS["RANDOMIZE"])
        self.global_randomize_button.setToolTip("Randomize player name")
        self.global_randomize_button.clicked.connect(self._set_random_player_name)
        self.global_randomize_button.setFixedSize(30, 30)  # Small square button
        self.global_randomize_button.setStyleSheet("font-size: 12px;")  # Smaller emoji
        player_name_layout.addWidget(self.global_randomize_button)

        game_content_layout.addWidget(player_name_group)

        # Terrain Selection Section with fieldset
        terrain_selection_group = QGroupBox("Terrain Selection")
        terrain_selection_layout = QVBoxLayout(terrain_selection_group)
        self.terrain_selection_widget = TerrainSelectionWidget(self.all_terrain_options)
        terrain_selection_layout.addWidget(self.terrain_selection_widget)
        game_content_layout.addWidget(terrain_selection_group)

        # Dragon Selection Section (already has its own fieldset)
        dragon_selection_group = QGroupBox(f"Select Your {self.required_dragons} Dragon(s)")
        dragon_selection_layout = QHBoxLayout(dragon_selection_group)
        dragon_selection_layout.setSpacing(10)

        self.dragon_selection_widgets = []
        for i in range(self.required_dragons):
            dragon_widget = DragonSelectionWidget(dragon_number=i + 1)
            self.dragon_selection_widgets.append(dragon_widget)
            dragon_widget.valueChanged.connect(self._validate_and_update_button_state)
            dragon_selection_layout.addWidget(dragon_widget)

        game_content_layout.addWidget(dragon_selection_group)

        # Army Setups - each army in its own fieldset
        self.army_setup_widgets: Dict[str, ArmySetupWidget] = {}
        self.army_detailed_units_labels = {}
        self.army_group_boxes = {}  # Track the QGroupBox widgets for visibility control

        for army_type in get_all_army_types():
            # Create fieldset for each army
            army_group = QGroupBox(f"{format_army_type_display(army_type)} Army")
            army_layout = QVBoxLayout(army_group)
            self.army_group_boxes[army_type] = army_group  # Store reference for visibility control

            # Army setup widget (manage units button and summary)
            army_widget = ArmySetupWidget(army_type, self.unit_roster)
            self.army_setup_widgets[army_type] = army_widget
            army_layout.addWidget(army_widget)

            # Scrollable detailed units text area
            detailed_units_text = QTextEdit(constants.NO_UNITS_SELECTED_TEXT)
            detailed_units_text.setReadOnly(True)
            detailed_units_text.setMaximumHeight(80)  # Limit height to allow scrolling
            detailed_units_text.setMinimumHeight(60)  # Minimum height for visibility
            detailed_units_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #f9f9f9;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px;
                }
            """
            )
            self.army_detailed_units_labels[army_type] = detailed_units_text
            army_layout.addWidget(detailed_units_text)

            # Connect army widget signals
            army_widget.units_updated_signal.connect(self._handle_units_updated_from_widget)

            game_content_layout.addWidget(army_group)

        # Add game content to tabbed widget
        self.tabbed_widget.add_game_layout(game_content_layout)

        # Set help content for Help tab
        self._set_player_setup_help_text()

        main_layout.addWidget(self.tabbed_widget)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)  # Add status_label below middle_section
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Navigation Buttons
        navigation_layout = QHBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton("Back")
        self.back_button.setMaximumWidth(120)  # Limit button width
        self.back_button.clicked.connect(lambda: self.back_signal.emit(self.current_player_index))
        navigation_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next Player")
        self.next_button.setMaximumWidth(200)  # Limit button width
        self.next_button.clicked.connect(self._handle_next_action)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

        # Connect signals for live validation
        self.player_identity_widget.name_changed.connect(self._validate_and_update_button_state)
        self.terrain_selection_widget.home_terrain_changed.connect(self._validate_and_update_button_state)
        self.terrain_selection_widget.frontier_proposal_changed.connect(self._validate_and_update_button_state)
        # Signal connections are now done individually in the army setup loop above

        self._set_player_setup_help_text()
        self.update_for_player(self.current_player_index, self.initial_player_data)

    def _set_random_player_name(self):
        # Combine Player and Army names for more variety
        all_names = []
        if self.preselected_names.get("Player"):
            all_names.extend(self.preselected_names["Player"])
        if self.preselected_names.get("Army"):
            all_names.extend(self.preselected_names["Army"])

        if all_names:
            self.player_identity_widget.set_name(random.choice(all_names))

    def _set_random_army_name_for_input(self, line_edit_widget: QLineEdit):
        pass

    def _randomize_all_names(self):
        self._set_random_player_name()

    def _handle_next_action(self):
        if not self._validate_inputs():
            return

        player_name = self.player_identity_widget.get_name()
        home_terrain_val = self.terrain_selection_widget.get_home_terrain()
        frontier_proposal_val = self.terrain_selection_widget.get_frontier_proposal()

        player_data = {
            "player_index": self.current_player_index,
            "name": player_name,
            "home_terrain": home_terrain_val,
            "frontier_terrain_proposal": frontier_proposal_val,
            "selected_dragons": [widget.value() for widget in self.dragon_selection_widgets],
            "armies": {},
        }
        for army_type in get_all_army_types():
            army_key = army_type.lower()
            if army_key == "horde" and self.num_players <= 1:
                continue
            current_army_widget = self.army_setup_widgets[army_type]
            army_units_data = current_army_widget.get_current_units_as_dicts()
            player_data["armies"][army_key] = {  # type: ignore
                "name": army_type,
                "units": army_units_data,
            }
        self.player_data_finalized.emit(self.current_player_index, player_data)
        # self.current_player_index += 1 # MainWindow now handles index increment via AppDataModel
        # if self.current_player_index < self.num_players:
        #     self.update_for_player(self.current_player_index)

    def _set_status_message(self, message, color_name="black"):
        self.status_label.setText(message)
        palette = self.status_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color_name))
        self.status_label.setPalette(palette)

    def _validate_inputs(self) -> bool:
        validation_errors = []

        # Check player name
        player_name = self.player_identity_widget.get_name()
        if not player_name:
            validation_errors.append("Player Name cannot be empty")

        # Official Dragon Dice army assembly validation
        # Rule 1: Each army must have at least 1 unit
        # Rule 2: No army can exceed 50% of total force points (rounded down)
        # Rule 3: Magic units cannot exceed 50% of total force points (rounded down)
        # Rule 4: Total army points must equal selected force size

        total_force_points = 0
        total_magic_points = 0
        # 50% of total force size (rounded down)
        max_magic_points = self.force_size // 2

        for army_type in get_all_army_types():
            # Skip horde army for single player games
            if army_type.lower() == "horde" and self.num_players <= 1:
                continue

            army_widget = self.army_setup_widgets[army_type]
            current_units = army_widget.current_units

            # Rule 1: Minimum 1 unit per army
            if len(current_units) == 0:
                validation_errors.append(f"{army_type} Army must have at least 1 unit")

            # Rule 2: Army cannot exceed 50% of total force points
            army_points = sum(unit.max_health for unit in current_units)
            if army_points > self.max_points_per_army:
                validation_errors.append(
                    f"{army_type} Army ({army_points} pts) exceeds maximum {self.max_points_per_army} pts (50% of {self.force_size} pts)"
                )

            # Count magic unit points for Rule 3
            for unit in current_units:
                unit_def = self.unit_roster.get_unit_definition(unit.unit_type)
                if unit_def and unit_def.get("unit_class_type") == "Magic":
                    total_magic_points += unit.max_health

            total_force_points += army_points

        # Rule 3: Magic units cannot exceed 50% of total force points
        if total_magic_points > max_magic_points:
            validation_errors.append(
                f"Magic units ({total_magic_points} pts) exceed maximum {max_magic_points} pts (50% of {self.force_size} pts)"
            )

        # Rule 4: Total force points must equal selected force size
        if total_force_points != self.force_size:
            validation_errors.append(
                f"Total army points ({total_force_points} pts) must equal selected force size ({self.force_size} pts)"
            )

        # Display validation results
        if validation_errors:
            # Create bulleted list of errors
            error_message = "• " + "\n• ".join(validation_errors)
            self._set_status_message(error_message, "red")
            return False

        # All validation passed - show helpful reminder
        if total_force_points == 0:
            self._set_status_message(
                f"Build armies totaling exactly {self.force_size} points.",
                "blue",
            )
        else:
            self._set_status_message("", "black")
        return True

    def _set_player_setup_help_text(self):
        player_num_for_display = self.current_player_index + 1
        self.tabbed_widget.set_help_text(
            self.help_model.get_player_setup_help(player_num_for_display, self.num_players, self.force_size)
        )

    def _validate_and_update_button_state(self):
        is_valid = self._validate_inputs()
        self.next_button.setEnabled(is_valid)

    @Slot(str, int)
    def _handle_army_points_changed(self, army_type: str, points: int):
        pass

    @Slot(str, list)
    def _handle_units_updated_from_widget(self, army_type_key: str, unit_dicts: list):
        self.army_units_data[army_type_key] = unit_dicts
        # Convert to uppercase to match ARMY_DATA keys used in army_detailed_units_labels
        army_type_upper = army_type_key.upper()
        self._update_specific_army_detailed_units_label(army_type_upper)
        self._validate_and_update_button_state()

    def _update_specific_army_summary_label(self, army_type: str):
        if army_type in self.army_setup_widgets:
            self.army_setup_widgets[army_type]._update_units_summary()

    def _update_specific_army_detailed_units_label(self, army_type: str):
        army_key = army_type.lower()
        units_in_army = self.army_units_data.get(army_key, [])
        if units_in_army:
            formatted_units = self._format_units_with_species_and_count(units_in_army)
            self.army_detailed_units_labels[army_type].setPlainText(formatted_units)
        else:
            self.army_detailed_units_labels[army_type].setPlainText(constants.NO_UNITS_SELECTED_TEXT)

    def _format_units_with_species_and_count(self, units_list: list) -> str:
        """Format units with species prefix and count aggregation."""
        if not units_list:
            return constants.NO_UNITS_SELECTED_TEXT

        # Count units by species + name combination
        unit_counts: Dict[str, int] = {}
        for unit in units_list:
            unit_type_id = unit.get("unit_type", "unknown")
            unit_name = unit.get("name", "Unknown Unit")

            # Extract species from unit_type_id (e.g., "amazon_war_driver" -> "Amazon")
            species = self._extract_species_from_unit_type_id(unit_type_id)

            # Get species with element icons
            species_with_icons = self._get_species_with_element_icons(species)
            species_unit_name = f"{species_with_icons} {unit_name}"

            unit_counts[species_unit_name] = unit_counts.get(species_unit_name, 0) + 1

        # Format as bulleted list with counts
        formatted_lines = []
        for species_unit_name, count in sorted(unit_counts.items()):
            if count > 1:
                formatted_lines.append(f"• {species_unit_name} (x{count})")
            else:
                formatted_lines.append(f"• {species_unit_name}")

        return "Selected:\n" + "\n".join(formatted_lines)

    def _extract_species_from_unit_type_id(self, unit_type_id: str) -> str:
        """Extract species name from unit type ID."""
        # Get species from unit roster if available
        if hasattr(self, "unit_roster") and self.unit_roster:
            unit_def = self.unit_roster.get_unit_definition(unit_type_id)
            if unit_def and "species" in unit_def:
                return str(unit_def["species"])

        # Fallback: parse from unit_type_id (e.g., "amazon_war_driver" -> "Amazon")
        if "_" in unit_type_id:
            species_part = unit_type_id.split("_")[0]
            return species_part.capitalize()

        return "Unknown"

    def _get_species_with_element_icons(self, species_name: str) -> str:
        """Get species name with element color icons prepended."""
        try:
            from models.species_model import ALL_SPECIES

            # Try direct lookup first
            species_key = species_name.upper().replace(" ", "_")
            species = ALL_SPECIES.get(species_key)

            # If not found, try matching by display name
            if not species:
                for species_obj in ALL_SPECIES.values():
                    if (
                        species_obj.name.lower() == species_name.lower()
                        or species_obj.display_name.lower() == species_name.lower()
                    ):
                        species = species_obj
                        break

            if species:
                element_icons = "".join(species.get_element_icons())
                return f"{element_icons} {species_name}"
        except:
            pass

        # Fallback to original species name
        return species_name

    def update_for_player(self, player_index, player_data_to_load: Optional[dict] = None):
        print(f"PlayerSetupView: update_for_player called for player {player_index + 1}")
        print(f"PlayerSetupView: player_data_to_load is None: {player_data_to_load is None}")

        self.current_player_index = player_index
        player_display_num = self.current_player_index + 1
        self.title_label.setText(f"Player {player_display_num} Setup")
        self.player_identity_widget.set_player_display_number(player_display_num)

        print(f"PlayerSetupView: Updated title to 'Player {player_display_num} Setup'")

        if player_data_to_load:
            self.player_identity_widget.set_name(player_data_to_load.get("name", ""))
            self.terrain_selection_widget.set_home_terrain(player_data_to_load.get("home_terrain"))
            self.terrain_selection_widget.set_frontier_proposal(player_data_to_load.get("frontier_terrain_proposal"))

            selected_dragons_data = player_data_to_load.get("selected_dragons", [])
            for i, widget in enumerate(self.dragon_selection_widgets):
                if i < len(selected_dragons_data):
                    dragon_data = selected_dragons_data[i]
                    # Handle both old format (string) and new format (dict)
                    if isinstance(dragon_data, dict):
                        widget.setValue(dragon_data)
                    else:
                        # Convert old string format to new dict format
                        widget.setValue(
                            {
                                "dragon_type": dragon_data,
                                "die_type": "Drake",
                            }
                        )
                else:
                    # Set default values
                    widget.clear()

            armies_data = player_data_to_load.get("armies", {})
            for army_key, details in armies_data.items():
                army_type_title_case = army_key.title()
                if army_type_title_case in self.army_setup_widgets:
                    army_widget = self.army_setup_widgets[army_type_title_case]

                    army_widget.load_units_from_dicts(details.get("units", []))

                    self.army_units_data[army_key] = army_widget.get_current_units_as_dicts()

                    army_widget._update_units_summary()
                    self._update_specific_army_detailed_units_label(army_type_title_case)

        else:
            self.player_identity_widget.clear_inputs()
            self.terrain_selection_widget.clear_selections()
            self.player_identity_widget.set_player_display_number(player_display_num)
            self.player_identity_widget.set_default_name(player_display_num)

            for widget in self.dragon_selection_widgets:
                widget.clear()

            for army_type in get_all_army_types():
                army_widget = self.army_setup_widgets[army_type]
                army_widget.load_units_from_dicts([])  # Clear units
                army_widget._update_units_summary()
                self.army_units_data[army_widget.army_type_name.lower()] = []
                self._update_specific_army_detailed_units_label(
                    army_widget.army_type_name
                )  # Update after clearing the cache
        self._update_horde_visibility()

        self._validate_and_update_button_state()
        self._set_player_setup_help_text()
        self.player_identity_widget.player_name_input.setFocus()

        if self.current_player_index == self.num_players - 1:
            self.next_button.setText("Finalize Setup & Start Game")
        else:
            self.next_button.setText(f"Next Player ({self.current_player_index + 2}/{self.num_players})")

        # Ensure the widget is properly updated and visible
        self.update()
        self.repaint()
        print("PlayerSetupView: update_for_player completed successfully")

    def _update_horde_visibility(self):
        show_horde = self.num_players > 1
        # Hide/show the entire army group box (which contains the label, widget, and unit list)
        if "Horde" in self.army_group_boxes:
            self.army_group_boxes["Horde"].setVisible(show_horde)
