"""
Integration example for Reserves Phase in Dragon Dice.

This example demonstrates:
1. How to use the ReservesPhaseDialog
2. Integration with ReservesManager
3. Amazon Ivory magic generation
4. Firewalker Air Flight movement
5. Reserve spell casting
"""

import sys
from typing import Any, Dict

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from game_logic.reserves_manager import ReservesManager
from views.magic_action_dialog import MagicActionDialog
from views.reserves_phase_dialog import ReservesPhaseDialog


class ReservesIntegrationExample(QMainWindow):
    """Example integration of Reserves Phase mechanics."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice - Reserves Phase Integration Example")
        self.setGeometry(100, 100, 800, 600)

        # Initialize game components
        self.reserves_manager = ReservesManager()

        # Sample game state
        self.current_player = "Player 1"
        self.game_turn = 3
        self.reserves_manager.set_current_turn(self.game_turn)

        # Setup sample data
        self._setup_sample_data()

        # Setup UI
        self._setup_ui()

    def _setup_sample_data(self):
        """Setup sample game data for demonstration."""
        # Sample units in Reserve Area
        self.sample_reserve_units = [
            {
                "name": "Amazon Warrior",
                "species": "Amazons",
                "health": 2,
                "elements": ["any"],  # Amazons adapt to terrain
            },
            {
                "name": "Amazon Scout",
                "species": "Amazons",
                "health": 1,
                "elements": ["any"],
            },
            {
                "name": "Firewalker Champion",
                "species": "Firewalkers",
                "health": 3,
                "elements": ["air", "fire"],
            },
            {
                "name": "Coral Elf Mystic",
                "species": "Coral Elves",
                "health": 2,
                "elements": ["air", "water"],
            },
        ]

        # Add units to reserves manager
        for unit in self.sample_reserve_units:
            self.reserves_manager.add_unit_to_reserves(unit, self.current_player, "previous_terrain", "retreat")

        # Sample terrain armies
        self.sample_terrain_armies = {
            "Air/Fire Mountain": {
                "units": [
                    {
                        "name": "Firewalker Flyer",
                        "species": "Firewalkers",
                        "health": 2,
                        "elements": ["air", "fire"],
                    },
                    {
                        "name": "Dwarf Warrior",
                        "species": "Dwarves",
                        "health": 2,
                        "elements": ["fire", "earth"],
                    },
                ],
                "terrain_elements": ["air", "fire", "earth"],
            },
            "Water/Earth Valley": {
                "units": [
                    {
                        "name": "Swamp Stalker",
                        "species": "Swamp Stalkers",
                        "health": 1,
                        "elements": ["death", "water"],
                    },
                ],
                "terrain_elements": ["water", "earth"],
            },
            "Air/Death Wasteland": {
                "units": [
                    {
                        "name": "Firewalker Hunter",
                        "species": "Firewalkers",
                        "health": 1,
                        "elements": ["air", "fire"],
                    },
                    {
                        "name": "Frostwing Sentinel",
                        "species": "Frostwings",
                        "health": 2,
                        "elements": ["air", "death"],
                    },
                ],
                "terrain_elements": ["air", "death"],
            },
        }

        # Available terrains for reinforcement
        self.available_terrains = list(self.sample_terrain_armies.keys()) + [
            "Fire/Earth Volcano",
            "Water/Air Coast",
            "Death/Earth Swamp",
        ]

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Reserves Phase button
        self.reserves_phase_button = QPushButton("🏰 Start Reserves Phase")
        self.reserves_phase_button.clicked.connect(self._start_reserves_phase)
        layout.addWidget(self.reserves_phase_button)

        # Magic Action from Reserves button
        self.magic_from_reserves_button = QPushButton("✨ Magic Action from Reserves")
        self.magic_from_reserves_button.clicked.connect(self._magic_action_from_reserves)
        layout.addWidget(self.magic_from_reserves_button)

        # Amazon Ivory Magic button
        self.amazon_ivory_button = QPushButton("💎 Amazon Ivory Magic Demo")
        self.amazon_ivory_button.clicked.connect(self._amazon_ivory_magic_demo)
        layout.addWidget(self.amazon_ivory_button)

        # Firewalker Air Flight button
        self.air_flight_button = QPushButton("🌪️ Firewalker Air Flight Demo")
        self.air_flight_button.clicked.connect(self._air_flight_demo)
        layout.addWidget(self.air_flight_button)

        # Reserve spell demo button
        self.reserve_spell_button = QPushButton("📚 Reserve Spell Demo")
        self.reserve_spell_button.clicked.connect(self._reserve_spell_demo)
        layout.addWidget(self.reserve_spell_button)

        # Status display
        self.status_button = QPushButton("📊 Show Reserves Status")
        self.status_button.clicked.connect(self._show_reserves_status)
        layout.addWidget(self.status_button)

    def _start_reserves_phase(self):
        """Start the Reserves Phase."""
        print("\\n=== Starting Reserves Phase ===")

        # Get current reserves
        current_reserves = self.reserves_manager.get_player_reserves(self.current_player)
        reserve_units_data = [unit.to_dict() for unit in current_reserves]

        # Create and show reserves phase dialog
        dialog = ReservesPhaseDialog(
            player_name=self.current_player,
            reserves_units=reserve_units_data,
            terrain_armies=self.sample_terrain_armies,
            available_terrains=self.available_terrains,
            parent=self,
        )

        dialog.phase_completed.connect(self._on_reserves_phase_completed)
        dialog.phase_cancelled.connect(self._on_reserves_phase_cancelled)

        dialog.exec()

    def _on_reserves_phase_completed(self, results: Dict[str, Any]):
        """Handle completed reserves phase."""
        print("\\n=== Reserves Phase Results ===")
        print(f"Player: {results['player_name']}")
        print(f"Phase: {results['phase_type']}")

        # Process reinforcement step
        reinforce_step = results.get("reinforce_step", {})
        reinforcement_plan = reinforce_step.get("reinforcement_plan", {})
        units_reinforced = reinforce_step.get("units_reinforced", 0)

        print("\\nReinforce Step:")
        print(f"  Units reinforced: {units_reinforced}")
        for terrain, unit_names in reinforcement_plan.items():
            print(f"  {terrain}: {', '.join(unit_names)}")

        # Process retreat step
        retreat_step = results.get("retreat_step", {})
        retreat_plan = retreat_step.get("retreat_plan", {})
        air_flight_plan = retreat_step.get("air_flight_plan", {})
        units_retreated = retreat_step.get("units_retreated", 0)
        firewalkers_moved = retreat_step.get("firewalkers_moved", 0)

        print("\\nRetreat Step:")
        print(f"  Units retreated: {units_retreated}")
        print(f"  Firewalkers moved via Air Flight: {firewalkers_moved}")

        # Apply changes to reserves manager
        if reinforcement_plan:
            reinforcement_results = self.reserves_manager.process_reinforcement(self.current_player, reinforcement_plan)
            print(f"\\nReinforcement processing: {reinforcement_results}")

        if retreat_plan:
            retreat_results = self.reserves_manager.process_retreat(
                self.current_player, retreat_plan, self.sample_terrain_armies
            )
            print(f"\\nRetreat processing: {retreat_results}")

    def _on_reserves_phase_cancelled(self):
        """Handle cancelled reserves phase."""
        print("\\n=== Reserves Phase Cancelled ===")

    def _magic_action_from_reserves(self):
        """Demonstrate magic action from Reserve Area."""
        print("\\n=== Magic Action from Reserves ===")

        # Create sample army in reserves with Amazons
        reserve_army = {
            "name": "Reserve Army",
            "units": [
                {
                    "name": "Amazon Priestess",
                    "species": "Amazons",
                    "health": 2,
                    "elements": ["any"],  # Will generate Ivory magic
                },
                {
                    "name": "Amazon Archer",
                    "species": "Amazons",
                    "health": 1,
                    "elements": ["any"],
                },
            ],
        }

        # Create magic action dialog for reserves
        dialog = MagicActionDialog(
            caster_name=self.current_player,
            caster_army=reserve_army,
            location="Reserve Area",
            parent=self,
        )

        dialog.magic_completed.connect(self._on_magic_completed)
        dialog.magic_cancelled.connect(self._on_magic_cancelled)

        dialog.exec()

    def _amazon_ivory_magic_demo(self):
        """Demonstrate Amazon Ivory magic generation."""
        print("\\n=== Amazon Ivory Magic Demo ===")

        # Get Amazon units in reserves
        amazon_units = self.reserves_manager.get_reserve_units_by_species(self.current_player, "Amazons")
        ivory_potential = self.reserves_manager.get_amazon_ivory_magic_generation(self.current_player)

        print(f"Amazon units in reserves: {len(amazon_units)}")
        print(f"Ivory magic potential: {ivory_potential}")

        # Show available reserve spells
        reserve_spells = self.reserves_manager.get_available_reserve_spells(self.current_player)
        elemental_spells = [spell for spell in reserve_spells if spell["element"] == "ELEMENTAL"]

        print("\\nElemental spells available with Ivory magic:")
        for spell in elemental_spells:
            print(f"  - {spell['name']} (Cost: {spell['cost']})")

    def _air_flight_demo(self):
        """Demonstrate Firewalker Air Flight."""
        print("\\n=== Firewalker Air Flight Demo ===")

        # Find air terrains with Firewalkers
        air_terrains = []
        for terrain, army_data in self.sample_terrain_armies.items():
            terrain_elements = army_data.get("terrain_elements", [])
            if isinstance(terrain_elements, list) and "air" in terrain_elements:
                firewalker_units = [unit for unit in army_data.get("units", []) if unit.get("species") == "Firewalkers"]
                if firewalker_units:
                    air_terrains.append((terrain, firewalker_units))

        print(f"Air terrains with Firewalkers: {len(air_terrains)}")
        for terrain, units in air_terrains:
            print(f"  {terrain}: {len(units)} Firewalker units")
            for unit in units:
                print(f"    - {unit['name']} (Health: {unit['health']})")

    def _reserve_spell_demo(self):
        """Demonstrate reserve spell casting."""
        print("\\n=== Reserve Spell Demo ===")

        # Show all available reserve spells
        reserve_spells = self.reserves_manager.get_available_reserve_spells(self.current_player)

        print(f"Available reserve spells: {len(reserve_spells)}")
        for spell in reserve_spells:
            print(f"  - {spell['name']} ({spell['element']}, Cost: {spell['cost']})")
            print(f"    Species: {spell['species']}")
            print(f"    Effect: {spell['effect'][:100]}...")
            print()

    def _show_reserves_status(self):
        """Show current reserves status."""
        print("\\n=== Reserves Status ===")

        # Get reserves statistics
        stats = self.reserves_manager.get_reserves_statistics(self.current_player)

        print(f"Player: {self.current_player}")
        print(f"Total units in reserves: {stats['total_units']}")
        print(f"Total health in reserves: {stats['total_health']}")
        print(f"Amazon Ivory magic potential: {stats['amazon_ivory_magic_potential']}")

        print("\\nSpecies breakdown:")
        for species, count in stats["species_breakdown"].items():
            print(f"  {species}: {count}")

        print("\\nElement breakdown:")
        for element, count in stats["element_breakdown"].items():
            print(f"  {element}: {count}")

    def _on_magic_completed(self, results: Dict[str, Any]):
        """Handle completed magic action."""
        print("\\n=== Magic Action Completed ===")
        print(f"Caster: {results['caster_name']}")
        print(f"Location: {results['caster_location']}")
        print(f"Spells cast: {len(results.get('spells_cast', []))}")

        for spell in results.get("spells_cast", []):
            print(f"  - {spell['name']} using {spell['element']} magic")

    def _on_magic_cancelled(self):
        """Handle cancelled magic action."""
        print("\\n=== Magic Action Cancelled ===")


def main():
    """Run the reserves integration example."""
    app = QApplication(sys.argv)
    window = ReservesIntegrationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
