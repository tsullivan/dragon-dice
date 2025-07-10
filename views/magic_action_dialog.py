"""
Magic Action Dialog for Dragon Dice - handles magic roll input and spell casting.

This dialog provides:
1. Individual die face input for magic rolls
2. Spell selection based on available magic points and elements
3. Amazon Terrain Harmony support
4. Element-specific magic point allocation
5. Spell casting with proper targeting
"""

from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from game_logic.sai_processor import SAIProcessor
from models.spell_model import ALL_SPELLS, SpellModel


class MagicDieRollInputWidget(QWidget):
    """Widget for inputting individual die face results for magic rolls."""

    def __init__(self, unit_name: str, unit_species: str, unit_health: int, parent=None):
        super().__init__(parent)
        self.unit_name = unit_name
        self.unit_species = unit_species
        self.unit_health = unit_health
        self.face_inputs: List[QLineEdit] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the die roll input UI."""
        layout = QVBoxLayout(self)

        # Unit header
        header_label = QLabel(f"{self.unit_name} ({self.unit_species}, Health: {self.unit_health})")
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


class SpellSelectionWidget(QWidget):
    """Widget for selecting and casting spells."""

    def __init__(self, caster_location: str = "", caster_army: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.caster_location = caster_location
        self.caster_army = caster_army or {}
        self.selected_spells: List[Tuple[SpellModel, int, str]] = []  # (spell, cost, element_used)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the spell selection UI."""
        layout = QVBoxLayout(self)

        # Available spells list
        self.spells_list = QListWidget()
        self.spells_list.setMaximumHeight(200)
        layout.addWidget(QLabel("Available Spells:"))
        layout.addWidget(self.spells_list)

        # Spell details
        self.spell_details = QTextEdit()
        self.spell_details.setMaximumHeight(100)
        self.spell_details.setReadOnly(True)
        layout.addWidget(QLabel("Spell Details:"))
        layout.addWidget(self.spell_details)

        # Element selection for casting
        element_layout = QHBoxLayout()
        element_layout.addWidget(QLabel("Cast using element:"))
        self.element_combo = QComboBox()
        element_layout.addWidget(self.element_combo)
        layout.addLayout(element_layout)

        # Add/Remove spell buttons
        button_layout = QHBoxLayout()
        self.add_spell_button = QPushButton("Add Spell to Cast")
        self.add_spell_button.clicked.connect(self._add_spell)
        button_layout.addWidget(self.add_spell_button)

        self.remove_spell_button = QPushButton("Remove Selected")
        self.remove_spell_button.clicked.connect(self._remove_spell)
        button_layout.addWidget(self.remove_spell_button)

        layout.addLayout(button_layout)

        # Selected spells for casting
        self.selected_spells_list = QListWidget()
        self.selected_spells_list.setMaximumHeight(150)
        layout.addWidget(QLabel("Spells to Cast:"))
        layout.addWidget(self.selected_spells_list)

        # Connect signals
        self.spells_list.itemClicked.connect(self._on_spell_selected)
        self.selected_spells_list.itemClicked.connect(self._on_selected_spell_clicked)

    def update_available_spells(
        self, magic_points_by_element: Dict[str, int], army_species: List[str], terrain_elements: List[str]
    ):
        """Update the list of available spells based on magic points and army composition."""
        self.spells_list.clear()
        self.magic_points_by_element = magic_points_by_element
        self.army_species = army_species
        self.terrain_elements = terrain_elements

        # Get available spells
        available_spells = self._get_castable_spells(magic_points_by_element, army_species)

        # Sort spells by element, then cost, then name
        available_spells.sort(key=lambda s: (s.element, s.cost, s.name))

        # Add spells to list
        for spell in available_spells:
            if spell.reserves:
                continue  # Skip reserve spells for now

            # Format spell display
            element_icon = self._get_element_icon(spell.element)
            species_text = f" ({spell.species})" if spell.species != "Any" else ""
            cantrip_text = " [Cantrip]" if spell.cantrip else ""

            display_text = f"{element_icon} {spell.name}{species_text}{cantrip_text} - Cost: {spell.cost}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, spell)
            self.spells_list.addItem(item)

    def _get_castable_spells(
        self, magic_points_by_element: Dict[str, int], army_species: List[str]
    ) -> List[SpellModel]:
        """Get spells that can be cast with available magic points."""
        available_spells = []

        # Check if army is in Reserve Area
        is_in_reserves = self.caster_location.lower() == "reserve area" or self.caster_location.lower() == "reserves"

        # Check for Amazon Ivory magic generation
        army_units = self.caster_army.get("units", [])
        amazon_units = [unit for unit in army_units if unit.get("species") == "Amazons"]
        has_ivory_magic = is_in_reserves and amazon_units and magic_points_by_element.get("IVORY", 0) > 0

        for spell in ALL_SPELLS.values():
            # Reserve spell restrictions
            if is_in_reserves and not spell.reserves:
                continue  # In reserves, can only cast reserve spells
            if not is_in_reserves and spell.reserves:
                continue  # Not in reserves, cannot cast reserve spells

            # Check species restrictions
            if spell.species != "Any" and spell.species not in army_species:
                continue

            # Check if we have enough magic points
            if spell.element == "ELEMENTAL":
                # Elemental spells can use any element
                total_magic = sum(magic_points_by_element.values())

                # Special case: Ivory magic can only cast Elemental spells
                if has_ivory_magic and "IVORY" in magic_points_by_element:
                    ivory_magic = magic_points_by_element["IVORY"]
                    if spell.cost <= ivory_magic:
                        available_spells.append(spell)
                        continue

                if spell.cost <= total_magic:
                    available_spells.append(spell)
            else:
                # Element-specific spells
                element_magic = magic_points_by_element.get(spell.element, 0)
                if spell.cost <= element_magic:
                    available_spells.append(spell)

        return available_spells

    def _on_spell_selected(self, item: QListWidgetItem):
        """Handle spell selection from the list."""
        spell = item.data(Qt.ItemDataRole.UserRole)
        if spell:
            self.spell_details.setText(f"<b>{spell.name}</b> ({spell.element})<br><br>{spell.effect}")

            # Update element combo based on spell
            self.element_combo.clear()

            if spell.element == "ELEMENTAL":
                # Can use any element
                # Check for Ivory magic priority (can only cast Elemental spells)
                ivory_magic = self.magic_points_by_element.get("IVORY", 0)
                if ivory_magic >= spell.cost:
                    self.element_combo.addItem(f"IVORY ({ivory_magic} available) - Elemental Only", "IVORY")

                for element, points in self.magic_points_by_element.items():
                    if element != "IVORY" and points >= spell.cost:
                        self.element_combo.addItem(f"{element} ({points} available)", element)
            else:
                # Must use specific element
                points = self.magic_points_by_element.get(spell.element, 0)
                if points >= spell.cost:
                    self.element_combo.addItem(f"{spell.element} ({points} available)", spell.element)

    def _add_spell(self):
        """Add selected spell to the casting list."""
        current_item = self.spells_list.currentItem()
        if not current_item:
            return

        spell = current_item.data(Qt.ItemDataRole.UserRole)
        element_data = self.element_combo.currentData()

        if spell and element_data:
            # Check if we still have enough magic points
            current_cost = sum(cost for _, cost, elem in self.selected_spells if elem == element_data)
            available_points = self.magic_points_by_element.get(element_data, 0)

            if current_cost + spell.cost <= available_points:
                self.selected_spells.append((spell, spell.cost, element_data))
                self._update_selected_spells_display()

                # Update magic points display to reflect remaining points
                self.magic_points_by_element[element_data] -= spell.cost
            else:
                # Not enough magic points - show error
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self,
                    "Insufficient Magic Points",
                    f"Not enough {element_data} magic points to cast {spell.name}.\n"
                    f"Required: {spell.cost}, Available: {available_points - current_cost}",
                )

    def _update_selected_spells_display(self):
        """Update the display of selected spells."""
        self.selected_spells_list.clear()

        total_cost_by_element: Dict[str, int] = {}
        for spell, cost, element in self.selected_spells:
            display_text = f"{spell.name} - Cost: {cost} ({element})"
            self.selected_spells_list.addItem(display_text)

            total_cost_by_element[element] = total_cost_by_element.get(element, 0) + cost

        # Add summary and remaining points
        if total_cost_by_element:
            summary_text = "Total Cost: " + ", ".join(f"{elem}: {cost}" for elem, cost in total_cost_by_element.items())
            self.selected_spells_list.addItem(summary_text)

            # Show remaining magic points
            remaining_text = "Remaining: " + ", ".join(
                f"{elem}: {self.magic_points_by_element.get(elem, 0)}"
                for elem in ["AIR", "DEATH", "EARTH", "FIRE", "WATER"]
                if self.magic_points_by_element.get(elem, 0) > 0
            )
            if remaining_text != "Remaining: ":
                self.selected_spells_list.addItem(remaining_text)

    def _get_element_icon(self, element: str) -> str:
        """Get icon for element."""
        icons = {"AIR": "💨", "DEATH": "💀", "EARTH": "🌍", "FIRE": "🔥", "WATER": "🌊", "ELEMENTAL": "✨"}
        return icons.get(element, "⭐")

    def get_selected_spells(self) -> List[Tuple[SpellModel, int, str]]:
        """Get the list of selected spells."""
        return self.selected_spells

    def _remove_spell(self):
        """Remove selected spell from the casting list."""
        current_row = self.selected_spells_list.currentRow()
        if current_row >= 0 and current_row < len(self.selected_spells):
            # Get the spell being removed
            spell, cost, element = self.selected_spells[current_row]

            # Restore magic points
            self.magic_points_by_element[element] += cost

            # Remove from list
            self.selected_spells.pop(current_row)
            self._update_selected_spells_display()

    def _on_selected_spell_clicked(self, item):
        """Handle click on selected spell item."""
        # Just ensure the item is selected for removal
        pass

    def clear_selections(self):
        """Clear all spell selections."""
        # Restore all magic points
        for spell, cost, element in self.selected_spells:
            self.magic_points_by_element[element] += cost

        self.selected_spells = []
        self.selected_spells_list.clear()


class MagicActionDialog(QDialog):
    """
    Dialog for handling magic actions with spell casting.

    This dialog captures individual die face results and provides
    spell selection and casting interface.
    """

    magic_completed = Signal(dict)  # Emits magic action results
    magic_cancelled = Signal()
    magic_negation_check = Signal(dict)  # Emits request for magic negation check

    def __init__(self, caster_name: str, caster_army: Dict[str, Any], location: str, parent=None):
        super().__init__(parent)
        self.caster_name = caster_name
        self.caster_army = caster_army
        self.location = location

        # Magic state
        self.current_step = "magic_roll"  # magic_roll, spell_selection, cast_spells
        self.magic_results: Dict[str, List[str]] = {}  # unit_name -> face_results
        self.magic_points_by_element: Dict[str, int] = {}
        self.amazon_flexible_magic: Dict[str, int] = {}  # Amazon magic that can be any terrain element
        self.cast_spells: List[Tuple[SpellModel, int, str]] = []

        self.sai_processor = SAIProcessor()

        self.setWindowTitle(f"✨ Magic Action at {location}")
        self.setModal(True)
        self.setMinimumSize(900, 700)

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

        # Magic info
        magic_info = QLabel(f"✨ {self.caster_name} performs magic action at {self.location}")
        magic_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        magic_info.setStyleSheet("font-size: 14px; margin: 10px; padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(magic_info)

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

        if self.current_step == "magic_roll":
            self._show_magic_roll()
        elif self.current_step == "spell_selection":
            self._show_spell_selection()
        elif self.current_step == "cast_spells":
            self._show_cast_spells()

        self._update_buttons()

    def _show_magic_roll(self):
        """Show magic roll input."""
        self.step_label.setText("Step 1: ✨ Magic Roll")
        self.results_display.hide()

        # Instructions
        instructions = QLabel(
            f"<b>{self.caster_name}</b>: Roll all units in your army and enter each die face result below.<br>"
            f"Magic results will be used to cast spells."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f2ff;")
        self.content_layout.addWidget(instructions)

        # Check for Amazon Terrain Harmony and Ivory magic generation
        terrain_elements = self._get_terrain_elements()
        army_units = self.caster_army.get("units", [])
        amazon_units = [unit for unit in army_units if unit.get("species") == "Amazons"]

        # Check if army is in Reserve Area (Amazon Ivory magic generation)
        is_in_reserves = self.location.lower() == "reserve area" or self.location.lower() == "reserves"

        # Show terrain eighth face effect notice
        if self._check_terrain_eighth_face_control():
            eighth_face_note = QLabel("🎯 <b>Terrain Eighth Face Controlled:</b> All ID results are doubled!")
            eighth_face_note.setWordWrap(True)
            eighth_face_note.setStyleSheet(
                "background-color: #f0f8ff; padding: 10px; border: 1px solid #1890ff; margin: 10px;"
            )
            self.content_layout.addWidget(eighth_face_note)

        if amazon_units and is_in_reserves:
            # Amazon Ivory magic generation in Reserve Area
            ivory_note = QLabel(
                "💎 <b>Amazon Ivory Magic:</b> Amazon units in Reserve Area generate Ivory magic, "
                "which can only be used to cast Elemental spells."
            )
            ivory_note.setWordWrap(True)
            ivory_note.setStyleSheet(
                "background-color: #f6ffed; padding: 10px; border: 1px solid #52c41a; margin: 10px;"
            )
            self.content_layout.addWidget(ivory_note)
        elif amazon_units and terrain_elements:
            # Regular Amazon Terrain Harmony
            harmony_note = QLabel(
                f"⚖️ <b>Terrain Harmony:</b> Amazon magic results can match any terrain element: "
                f"{', '.join(terrain_elements)}"
            )
            harmony_note.setWordWrap(True)
            harmony_note.setStyleSheet(
                "background-color: #fffbe6; padding: 10px; border: 1px solid #fadb14; margin: 10px;"
            )
            self.content_layout.addWidget(harmony_note)

        # Army units
        self.magic_roll_widgets = []
        for unit in army_units:
            unit_name = unit.get("name", "Unknown Unit")
            unit_species = unit.get("species", "Unknown")
            unit_health = unit.get("health", 1)

            unit_widget = MagicDieRollInputWidget(unit_name, unit_species, unit_health)
            self.magic_roll_widgets.append(unit_widget)
            self.content_layout.addWidget(unit_widget)

        # Helpful note
        note = QLabel("💡 Tip: Magic results (Mg) and SAI faces can generate magic points for spell casting")
        note.setStyleSheet("font-style: italic; color: #666; margin: 10px;")
        note.setWordWrap(True)
        self.content_layout.addWidget(note)

    def _show_spell_selection(self):
        """Show spell selection interface."""
        self.step_label.setText("Step 2: 📚 Spell Selection")
        self.results_display.show()

        # Show magic roll results
        self._update_magic_results_display()

        # Instructions
        instructions = QLabel(
            "<b>Select Spells:</b> Choose spells to cast with your available magic points.<br>"
            "Element-specific spells require magic of that element. Elemental spells can use any element."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f2ff;")
        self.content_layout.addWidget(instructions)

        # Spell selection widget
        self.spell_selection_widget = SpellSelectionWidget(caster_location=self.location, caster_army=self.caster_army)
        army_species = list(set(unit.get("species", "") for unit in self.caster_army.get("units", [])))
        terrain_elements = self._get_terrain_elements()

        self.spell_selection_widget.update_available_spells(
            self.magic_points_by_element, army_species, terrain_elements
        )

        self.content_layout.addWidget(self.spell_selection_widget)

    def _show_cast_spells(self):
        """Show spell casting results."""
        self.step_label.setText("Step 3: 🎯 Cast Spells")
        self.results_display.show()

        # Get selected spells
        self.cast_spells = self.spell_selection_widget.get_selected_spells()

        # Show final results
        self._update_final_results_display()

        # Spell effects summary
        if self.cast_spells:
            effects_label = QLabel("<b>Spell Effects:</b>")
            effects_label.setStyleSheet("font-size: 14px; margin: 10px;")
            self.content_layout.addWidget(effects_label)

            for spell, cost, element in self.cast_spells:
                effect_text = f"<b>{spell.name}</b> ({element}, Cost: {cost})<br>{spell.effect}"
                effect_label = QLabel(effect_text)
                effect_label.setWordWrap(True)
                effect_label.setStyleSheet(
                    "margin: 5px; padding: 10px; background-color: #f8f8f8; border-left: 3px solid #1890ff;"
                )
                self.content_layout.addWidget(effect_label)
        else:
            no_spells_label = QLabel("No spells selected for casting.")
            no_spells_label.setStyleSheet("margin: 10px; font-style: italic; color: #666;")
            self.content_layout.addWidget(no_spells_label)

    def _collect_magic_results(self) -> bool:
        """Collect magic roll results from input widgets."""
        if not hasattr(self, "magic_roll_widgets"):
            return False

        self.magic_results = {}
        army_units = self.caster_army.get("units", [])

        for i, widget in enumerate(self.magic_roll_widgets):
            if i < len(army_units):
                unit_name = army_units[i].get("name", f"Unit {i + 1}")
                face_results = widget.get_face_results()
                self.magic_results[unit_name] = face_results

        return True

    def _calculate_magic_points(self):
        """Calculate available magic points by element."""
        terrain_elements = self._get_terrain_elements()
        army_units = self.caster_army.get("units", [])

        # Check if army controls terrain eighth face (doubles all ID results)
        terrain_eighth_face_controlled = self._check_terrain_eighth_face_control()

        # Process magic roll with SAI effects
        magic_result = self.sai_processor.process_combat_roll(
            self.magic_results,
            "magic",
            army_units,
            is_attacker=True,
            terrain_elements=terrain_elements,
            terrain_eighth_face_controlled=terrain_eighth_face_controlled,
        )

        # Initialize magic points
        self.magic_points_by_element = {"AIR": 0, "DEATH": 0, "EARTH": 0, "FIRE": 0, "WATER": 0}

        # Check if in Reserve Area for Ivory magic
        is_in_reserves = self.location.lower() == "reserve area" or self.location.lower() == "reserves"
        if is_in_reserves:
            self.magic_points_by_element["IVORY"] = 0

        # Calculate magic points by unit and element
        for unit_name, face_results in self.magic_results.items():
            # Find unit data
            unit_data = next((u for u in army_units if u.get("name") == unit_name), None)
            if not unit_data:
                continue

            unit_species = unit_data.get("species", "")
            unit_elements = self._get_unit_elements(unit_species)
            unit_health = unit_data.get("health", 1)

            # Count magic results (non-ID)
            non_id_magic_count = sum(1 for face in face_results if face.lower().strip() in ["mg", "magic"])
            id_count = sum(1 for face in face_results if face.lower().strip() == "id")

            # ID faces generate magic equal to unit health
            id_magic_count = id_count * unit_health

            # Apply terrain eighth face doubling to ID results only
            if terrain_eighth_face_controlled:
                id_magic_count *= 2

            # Total magic from this unit
            total_magic_count = non_id_magic_count + id_magic_count

            if total_magic_count > 0:
                if unit_species == "Amazons":
                    if is_in_reserves:
                        # Amazon Ivory magic generation in Reserve Area
                        self.magic_points_by_element["IVORY"] = (
                            self.magic_points_by_element.get("IVORY", 0) + total_magic_count
                        )
                    else:
                        # Amazon Terrain Harmony - magic can be any terrain element
                        self.amazon_flexible_magic[unit_name] = total_magic_count
                else:
                    # Regular unit - magic matches unit elements
                    if unit_elements:
                        # Distribute magic evenly among unit elements
                        magic_per_element = total_magic_count // len(unit_elements)
                        remainder = total_magic_count % len(unit_elements)

                        for i, element in enumerate(unit_elements):
                            points = magic_per_element
                            if i < remainder:
                                points += 1
                            self.magic_points_by_element[element] = (
                                self.magic_points_by_element.get(element, 0) + points
                            )

        # Handle Amazon flexible magic - will be assigned during spell selection
        total_amazon_magic = sum(self.amazon_flexible_magic.values())
        if total_amazon_magic > 0:
            # For now, distribute evenly among terrain elements
            if terrain_elements:
                magic_per_element = total_amazon_magic // len(terrain_elements)
                remainder = total_amazon_magic % len(terrain_elements)

                for i, element in enumerate(terrain_elements):
                    element_key = element.upper()
                    if element_key in self.magic_points_by_element:
                        points = magic_per_element
                        if i < remainder:
                            points += 1
                        self.magic_points_by_element[element_key] += points

    def _get_unit_elements(self, species: str) -> List[str]:
        """Get elements for a unit species."""
        species_elements = {
            "Amazons": [],  # Special case - uses terrain elements
            "Coral Elves": ["AIR", "WATER"],
            "Dwarves": ["FIRE", "EARTH"],
            "Eldarim": ["AIR", "DEATH", "EARTH", "FIRE", "WATER"],  # Varies by specific unit
            "Feral": ["AIR", "EARTH"],
            "Firewalkers": ["AIR", "FIRE"],
            "Frostwings": ["DEATH", "AIR"],
            "Goblins": ["DEATH", "EARTH"],
            "Lava Elves": ["DEATH", "FIRE"],
            "Scalders": ["WATER", "FIRE"],
            "Swamp Stalkers": ["DEATH", "WATER"],
            "Treefolk": ["WATER", "EARTH"],
            "Undead": ["DEATH"],
        }
        return species_elements.get(species, [])

    def _check_terrain_eighth_face_control(self) -> bool:
        """Check if the caster's army controls the terrain's eighth face."""
        # This would check the actual terrain state in the game
        # For now, this is a simplified check - in a full implementation,
        # this would query the game engine for terrain control status

        # Check if location indicates eighth face control
        # This is a placeholder - real implementation would check game state
        if "eighth" in self.location.lower() or "controlled" in self.location.lower():
            return True

        # In a full implementation, this would check:
        # return self.game_engine.is_terrain_eighth_face_controlled(self.location, self.caster_name)
        return False

    def _get_terrain_elements(self) -> List[str]:
        """Get terrain elements for the magic location."""
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

    def _update_magic_results_display(self):
        """Update magic results display."""
        # Calculate magic points
        self._calculate_magic_points()

        # Format results
        results_text = "MAGIC ROLL RESULTS:\n"

        # Show terrain eighth face effect if active
        if self._check_terrain_eighth_face_control():
            results_text += "🎯 Terrain Eighth Face Controlled: ID results doubled!\n\n"

        # Show magic points by element
        for element, points in self.magic_points_by_element.items():
            if points > 0:
                icon = {"AIR": "💨", "DEATH": "💀", "EARTH": "🌍", "FIRE": "🔥", "WATER": "🌊"}.get(element, "✨")
                results_text += f"{icon} {element}: {points} points\n"

        # Show Amazon flexible magic
        if self.amazon_flexible_magic:
            total_amazon = sum(self.amazon_flexible_magic.values())
            results_text += f"⚖️ Amazon Terrain Harmony: {total_amazon} flexible points\n"

        self.results_display.setText(results_text)

    def _update_final_results_display(self):
        """Update final results display."""
        results_text = "MAGIC ACTION RESULTS:\n\n"

        # Magic points summary
        total_generated = sum(self.magic_points_by_element.values())
        results_text += f"Total Magic Generated: {total_generated} points\n"

        # Spells cast
        if self.cast_spells:
            results_text += f"\nSpells Cast ({len(self.cast_spells)}):\n"
            total_cost = 0
            for spell, cost, element in self.cast_spells:
                results_text += f"  • {spell.name} ({element}, Cost: {cost})\n"
                total_cost += cost
            results_text += f"\nTotal Magic Used: {total_cost} points"
        else:
            results_text += "\nNo spells cast."

        self.results_display.setText(results_text)

    def _complete_magic_action(self):
        """Complete the magic action and emit results."""
        magic_result = {
            "success": True,
            "action_type": "magic",
            "caster": self.caster_name,
            "location": self.location,
            "magic_results": self.magic_results,
            "magic_points_by_element": self.magic_points_by_element,
            "amazon_flexible_magic": self.amazon_flexible_magic,
            "cast_spells": [self._create_spell_data(spell, cost, element) for spell, cost, element in self.cast_spells],
            "timestamp": "now",
        }

        # Check for Magic Negation opportunity before completing
        self._check_magic_negation_opportunity(magic_result)

        self.magic_completed.emit(magic_result)
        self.accept()

    def _create_spell_data(self, spell: SpellModel, cost: int, element: str) -> Dict[str, Any]:
        """Create detailed spell data including targeting information."""
        spell_data = {
            "name": spell.name,
            "cost": cost,
            "element_used": element,
            "caster": self.caster_name,
            "effect": spell.effect,
        }

        # Add targeting information for dragon summoning spells
        if spell.name in ["Summon Dragon", "Summon White Dragon", "Summon Dragonkin"]:
            # For now, use the current location as target terrain
            # In a full implementation, this would show a terrain selection dialog
            spell_data["target_terrain"] = self.location

        return spell_data

    def _check_magic_negation_opportunity(self, magic_result: Dict[str, Any]):
        """Check if opponents can use Magic Negation against this magic action."""
        # Emit signal for game engine to check for Frostwings Magic Negation
        negation_check = {
            "magic_result": magic_result,
            "caster": self.caster_name,
            "location": self.location,
            "check_type": "magic_negation",
        }

        self.magic_negation_check.emit(negation_check)

    def _update_buttons(self):
        """Update button states based on current step."""
        if self.current_step == "magic_roll":
            self.back_button.setEnabled(False)
            self.next_button.setText("Roll Magic ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "spell_selection":
            self.back_button.setEnabled(True)
            self.next_button.setText("Cast Spells ▶")
            self.next_button.setEnabled(True)
        elif self.current_step == "cast_spells":
            self.back_button.setEnabled(True)
            self.next_button.setText("Complete Magic ▶")
            self.next_button.setEnabled(True)

    def _on_back(self):
        """Handle back button."""
        if self.current_step == "spell_selection":
            self.current_step = "magic_roll"
        elif self.current_step == "cast_spells":
            self.current_step = "spell_selection"

        self._update_step_display()

    def _on_next(self):
        """Handle next button."""
        if self.current_step == "magic_roll":
            if self._collect_magic_results():
                self._calculate_magic_points()
                self.current_step = "spell_selection"
            else:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(self, "Input Required", "Please enter die face results for all units.")
                return

        elif self.current_step == "spell_selection":
            self.current_step = "cast_spells"

        elif self.current_step == "cast_spells":
            self._complete_magic_action()
            return

        self._update_step_display()

    def _on_cancel(self):
        """Handle cancel button."""
        self.magic_cancelled.emit()
        self.reject()
