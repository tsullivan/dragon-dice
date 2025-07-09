"""
Integration example for Species Abilities Phase in Dragon Dice.

This example demonstrates:
1. How to use the SpeciesAbilitiesPhaseDialog
2. Integration with DUA and Reserves managers
3. Swamp Stalkers' Mutate ability workflow
4. Save roll resolution and recruitment mechanics
5. Turn sequence integration
"""

import sys
from typing import Any, Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit

from game_logic.dua_manager import DUAManager
from game_logic.reserves_manager import ReservesManager
from models.unit_model import UnitModel
from views.species_abilities_phase_dialog import SpeciesAbilitiesPhaseDialog
from views.mutate_save_roll_dialog import MutateSaveRollDialog


class SpeciesAbilityIntegrationExample(QMainWindow):
    """Example integration of Species Abilities Phase mechanics."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice - Species Abilities Phase Integration Example")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize game components
        self.dua_manager = DUAManager()
        self.reserves_manager = ReservesManager()

        # Sample game state
        self.current_player = "Player 1"
        self.opponent_players = ["Player 2", "Player 3"]
        self.game_points = 24
        self.game_turn = 4

        # Setup sample data
        self._setup_sample_data()

        # Setup UI
        self._setup_ui()

    def _setup_sample_data(self):
        """Setup sample game data for demonstration."""
        # Sample player armies with Swamp Stalkers
        self.sample_player_armies = [
            {
                "name": "Swamp Army Alpha",
                "location": "Water/Death Swamp",
                "units": [
                    {
                        "name": "Swamp Stalker Hunter",
                        "species": "Swamp Stalkers",
                        "health": 2,
                        "elements": ["water", "death"],
                    },
                    {
                        "name": "Swamp Stalker Scout",
                        "species": "Swamp Stalkers",
                        "health": 1,
                        "elements": ["water", "death"],
                    },
                    {
                        "name": "Frostwing Ally",
                        "species": "Frostwings",
                        "health": 2,
                        "elements": ["air", "death"],
                    },
                ],
                "terrain_elements": ["water", "death"],
            },
            {
                "name": "Swamp Army Beta",
                "location": "Earth/Water Valley",
                "units": [
                    {
                        "name": "Swamp Stalker Champion",
                        "species": "Swamp Stalkers",
                        "health": 3,
                        "elements": ["water", "death"],
                    },
                    {
                        "name": "Coral Elf Mystic",
                        "species": "Coral Elves",
                        "health": 2,
                        "elements": ["air", "water"],
                    },
                ],
                "terrain_elements": ["earth", "water"],
            },
        ]

        # Sample opponent reserves
        self.sample_opponent_reserves = {
            "Player 2": [
                {
                    "name": "Amazon Warrior",
                    "species": "Amazons",
                    "health": 2,
                    "elements": ["any"],
                },
                {
                    "name": "Amazon Scout",
                    "species": "Amazons",
                    "health": 1,
                    "elements": ["any"],
                },
                {
                    "name": "Dwarf Champion",
                    "species": "Dwarves",
                    "health": 3,
                    "elements": ["fire", "earth"],
                },
            ],
            "Player 3": [
                {
                    "name": "Firewalker Flyer",
                    "species": "Firewalkers",
                    "health": 2,
                    "elements": ["air", "fire"],
                },
                {
                    "name": "Goblin Raider",
                    "species": "Goblins",
                    "health": 1,
                    "elements": ["fire", "earth"],
                },
            ],
        }

        # Add dead Swamp Stalkers to DUA
        dead_swamp_stalkers = [
            UnitModel(
                name="Dead Swamp Stalker Alpha",
                species="Swamp Stalkers",
                health=2,
                elements=["water", "death"],
                owner=self.current_player,
            ),
            UnitModel(
                name="Dead Swamp Stalker Beta",
                species="Swamp Stalkers",
                health=1,
                elements=["water", "death"],
                owner=self.current_player,
            ),
            UnitModel(
                name="Dead Swamp Stalker Gamma",
                species="Swamp Stalkers",
                health=1,
                elements=["water", "death"],
                owner=self.current_player,
            ),
        ]

        for unit in dead_swamp_stalkers:
            self.dua_manager.add_unit_to_dua(unit)

        # Add opponent reserves to reserves manager
        for opponent, reserve_units in self.sample_opponent_reserves.items():
            for unit_data in reserve_units:
                unit = UnitModel(
                    name=unit_data["name"],
                    species=unit_data["species"],
                    health=unit_data["health"],
                    elements=unit_data["elements"],
                    owner=opponent,
                )
                self.reserves_manager.add_unit_to_reserves(unit, opponent, "previous_terrain", "retreat")

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Game state display
        self.game_state_display = QTextEdit()
        self.game_state_display.setMaximumHeight(200)
        self.game_state_display.setReadOnly(True)
        layout.addWidget(self.game_state_display)

        # Species Abilities Phase button
        self.species_abilities_button = QPushButton("🧬 Start Species Abilities Phase")
        self.species_abilities_button.clicked.connect(self._start_species_abilities_phase)
        layout.addWidget(self.species_abilities_button)

        # Direct Mutate demo button
        self.mutate_demo_button = QPushButton("🎯 Direct Mutate Demo")
        self.mutate_demo_button.clicked.connect(self._direct_mutate_demo)
        layout.addWidget(self.mutate_demo_button)

        # Show game state button
        self.show_state_button = QPushButton("📊 Show Game State")
        self.show_state_button.clicked.connect(self._show_game_state)
        layout.addWidget(self.show_state_button)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        # Initialize display
        self._show_game_state()

    def _start_species_abilities_phase(self):
        """Start the Species Abilities Phase."""
        self._log("=== Starting Species Abilities Phase ===")

        # Create and show species abilities phase dialog
        dialog = SpeciesAbilitiesPhaseDialog(
            player_name=self.current_player,
            player_armies=self.sample_player_armies,
            opponent_reserves=self.sample_opponent_reserves,
            dua_manager=self.dua_manager,
            reserves_manager=self.reserves_manager,
            game_points=self.game_points,
            parent=self,
        )

        dialog.abilities_completed.connect(self._on_abilities_completed)
        dialog.abilities_skipped.connect(self._on_abilities_skipped)

        dialog.exec()

    def _on_abilities_completed(self, results: Dict[str, Any]):
        """Handle completed species abilities phase."""
        self._log("=== Species Abilities Phase Completed ===")
        self._log(f"Player: {results['player_name']}")
        self._log(f"Phase: {results['phase_type']}")
        self._log(f"Available abilities: {results['available_abilities']}")
        self._log(f"Used abilities: {results['abilities_count']}")

        # Process each used ability
        for ability_data in results.get("used_abilities", []):
            ability_type = ability_data.get("ability_type", "unknown")
            
            if ability_type == "mutate":
                self._process_mutate_ability(ability_data)

    def _on_abilities_skipped(self):
        """Handle skipped species abilities phase."""
        self._log("=== Species Abilities Phase Skipped ===")

    def _process_mutate_ability(self, mutate_data: Dict[str, Any]):
        """Process a Mutate ability use."""
        self._log("\n--- Processing Mutate Ability ---")
        self._log(f"Swamp Stalker Player: {mutate_data['swamp_stalker_player']}")
        self._log(f"Targets: {len(mutate_data['targets'])}")
        self._log(f"Max targets: {mutate_data['max_targets']}")
        self._log(f"S-value: {mutate_data['s_value']}")

        # Show mutate save roll dialog
        save_roll_dialog = MutateSaveRollDialog(mutate_data, parent=self)
        save_roll_dialog.mutate_resolved.connect(self._on_mutate_resolved)
        save_roll_dialog.exec()

    def _on_mutate_resolved(self, resolution_results: Dict[str, Any]):
        """Handle resolved Mutate ability."""
        self._log("\n--- Mutate Resolved ---")
        self._log(f"Success: {resolution_results['success']}")
        self._log(f"Units killed: {resolution_results['units_killed_count']}")
        self._log(f"Units saved: {resolution_results['units_saved_count']}")
        self._log(f"Total health killed: {resolution_results['total_health_killed']}")

        # Process killed units
        for killed_unit in resolution_results.get("killed_units", []):
            unit_data = killed_unit["unit_data"]
            opponent_name = killed_unit["opponent_name"]
            self._log(f"  Killed: {unit_data['name']} ({opponent_name})")

            # Remove from opponent's reserves
            self.reserves_manager.remove_unit_from_reserves(
                opponent_name, unit_data["name"], "killed_by_mutate"
            )

        # Process saved units
        for saved_unit in resolution_results.get("saved_units", []):
            unit_data = saved_unit["unit_data"]
            opponent_name = saved_unit["opponent_name"]
            self._log(f"  Saved: {unit_data['name']} ({opponent_name})")

        # Show recruitment opportunity
        if resolution_results["total_health_killed"] > 0:
            recruiting_army = resolution_results["recruiting_army"]
            self._log(f"\n{resolution_results['swamp_stalker_player']} can recruit/promote {resolution_results['total_health_killed']} health-worth of Swamp Stalkers")
            self._log(f"Recruiting army: {recruiting_army['name']} at {recruiting_army['location']}")

    def _direct_mutate_demo(self):
        """Demonstrate direct Mutate ability usage."""
        self._log("=== Direct Mutate Demo ===")

        # Create sample mutate data
        sample_targets = [
            {
                "unit_data": self.sample_opponent_reserves["Player 2"][0],
                "opponent_name": "Player 2",
            },
            {
                "unit_data": self.sample_opponent_reserves["Player 3"][0],
                "opponent_name": "Player 3",
            },
        ]

        mutate_data = {
            "ability_type": "mutate",
            "swamp_stalker_player": self.current_player,
            "targets": sample_targets,
            "recruiting_army": self.sample_player_armies[0],
            "dead_swamp_stalkers_count": 3,
            "max_targets": 1,  # Based on s-value for 24 points
            "s_value": 1,
            "game_points": self.game_points,
        }

        # Show save roll dialog
        save_roll_dialog = MutateSaveRollDialog(mutate_data, parent=self)
        save_roll_dialog.mutate_resolved.connect(self._on_mutate_resolved)
        save_roll_dialog.exec()

    def _show_game_state(self):
        """Show current game state."""
        game_state = []
        game_state.append(f"=== Game State - Turn {self.game_turn} ===")
        game_state.append(f"Current Player: {self.current_player}")
        game_state.append(f"Game Points: {self.game_points}")
        game_state.append("")

        # Show player armies
        game_state.append("Player Armies:")
        for army in self.sample_player_armies:
            swamp_stalkers = [u for u in army["units"] if u["species"] == "Swamp Stalkers"]
            game_state.append(f"  {army['name']} at {army['location']}")
            game_state.append(f"    Swamp Stalkers: {len(swamp_stalkers)}")
            game_state.append(f"    Total units: {len(army['units'])}")

        game_state.append("")

        # Show DUA state
        player_dua = self.dua_manager.get_player_dua(self.current_player)
        dead_swamp_stalkers = [u for u in player_dua if u.species == "Swamp Stalkers"]
        game_state.append("DUA (Dead Units Area):")
        game_state.append(f"  Dead Swamp Stalkers: {len(dead_swamp_stalkers)}")
        game_state.append(f"  Total dead units: {len(player_dua)}")

        game_state.append("")

        # Show opponent reserves
        game_state.append("Opponent Reserves:")
        for opponent, reserve_units in self.sample_opponent_reserves.items():
            game_state.append(f"  {opponent}: {len(reserve_units)} units")
            for unit in reserve_units:
                game_state.append(f"    - {unit['name']} ({unit['species']}, Health: {unit['health']})")

        self.game_state_display.setPlainText("\n".join(game_state))

    def _log(self, message: str):
        """Log a message to the results display."""
        current_text = self.results_display.toPlainText()
        self.results_display.setPlainText(current_text + message + "\n")
        
        # Auto-scroll to bottom
        scrollbar = self.results_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Also print to console
        print(message)


def main():
    """Run the species ability integration example."""
    app = QApplication(sys.argv)
    window = SpeciesAbilityIntegrationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
