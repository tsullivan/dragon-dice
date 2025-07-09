"""
Integration example for Summoning Pool and BUA (Buried Units Area) in Dragon Dice.

This example demonstrates:
1. Summoning Pool management for dragons
2. BUA management for buried units
3. Integration with Reserves Phase for burial
4. Spell targeting with DUA and BUA
5. Dragon return-to-pool mechanics when killed
"""

import sys
from typing import Any, Dict, List

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout

from game_logic.summoning_pool_manager import SummoningPoolManager
from game_logic.bua_manager import BUAManager
from game_logic.dua_manager import DUAManager
from game_logic.spell_targeting import SpellTargetingManager
from models.dragon_model import DragonModel
from models.unit_model import UnitModel
from models.spell_model import ALL_SPELLS


class SummoningPoolBUAIntegrationExample(QMainWindow):
    """Example integration of Summoning Pool and BUA mechanics."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice - Summoning Pool & BUA Integration Example")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize managers
        self.summoning_pool_manager = SummoningPoolManager()
        self.bua_manager = BUAManager()
        self.dua_manager = DUAManager()
        self.spell_targeting_manager = SpellTargetingManager(
            self.dua_manager, self.bua_manager, self.summoning_pool_manager
        )

        # Sample players
        self.players = ["Player 1", "Player 2", "Player 3"]
        self.current_player = "Player 1"

        # Setup sample data
        self._setup_sample_data()

        # Setup UI
        self._setup_ui()

    def _setup_sample_data(self):
        """Setup sample game data for demonstration."""
        # Create sample dragons for summoning pools
        sample_dragons = {
            "Player 1": [
                DragonModel("Flame Drake", "DRAKE", "FIRE_ELEMENTAL", ["FIRE"], "Player 1"),
                DragonModel("Storm Wyrm", "WYRM", "AIR_ELEMENTAL", ["AIR"], "Player 1"),
                DragonModel("Hybrid Beast", "DRAKE", "FIRE_AIR_HYBRID", ["FIRE", "AIR"], "Player 1"),
            ],
            "Player 2": [
                DragonModel("Earth Wyrm", "WYRM", "EARTH_ELEMENTAL", ["EARTH"], "Player 2"),
                DragonModel("Death Drake", "DRAKE", "DEATH_ELEMENTAL", ["DEATH"], "Player 2"),
                DragonModel("Ivory Dragon", "WYRM", "IVORY", ["IVORY"], "Player 2"),
            ],
            "Player 3": [
                DragonModel("Water Drake", "DRAKE", "WATER_ELEMENTAL", ["WATER"], "Player 3"),
                DragonModel("White Dragon", "WYRM", "WHITE", ["WHITE"], "Player 3"),
            ],
        }

        # Initialize summoning pools
        for player, dragons in sample_dragons.items():
            self.summoning_pool_manager.initialize_player_pool(player, dragons)

        # Initialize BUAs
        for player in self.players:
            self.bua_manager.initialize_player_bua(player)

        # Add some sample dead units to DUA
        sample_dua_units = [
            UnitModel("Dead Amazon Warrior", "Amazons", 2, ["any"], "Player 1"),
            UnitModel("Dead Firewalker Scout", "Firewalkers", 1, ["air", "fire"], "Player 1"),
            UnitModel("Dead Swamp Stalker", "Swamp Stalkers", 1, ["water", "death"], "Player 1"),
            UnitModel("Dead Dwarf Champion", "Dwarves", 3, ["fire", "earth"], "Player 2"),
            UnitModel("Dead Coral Elf", "Coral Elves", 2, ["air", "water"], "Player 2"),
        ]

        for unit in sample_dua_units:
            self.dua_manager.add_unit_to_dua(unit)

        # Bury some units in BUA
        buried_units = [
            UnitModel("Buried Goblin", "Goblins", 1, ["fire", "earth"], "Player 1"),
            UnitModel("Buried Frostwing", "Frostwings", 2, ["air", "death"], "Player 2"),
        ]

        for unit in buried_units:
            self.bua_manager.bury_unit(unit.owner, unit)

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Left panel - Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_widget.setMaximumWidth(300)

        # Summoning Pool controls
        controls_layout.addWidget(self._create_summoning_pool_controls())

        # BUA controls
        controls_layout.addWidget(self._create_bua_controls())

        # Dragon mechanics controls
        controls_layout.addWidget(self._create_dragon_mechanics_controls())

        # Spell targeting controls
        controls_layout.addWidget(self._create_spell_targeting_controls())

        layout.addWidget(controls_widget)

        # Right panel - Display
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        layout.addWidget(self.display_area)

        # Initialize display
        self._show_all_status()

    def _create_summoning_pool_controls(self):
        """Create summoning pool control buttons."""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)

        # Header
        header = QPushButton("🐉 Summoning Pool")
        header.setStyleSheet("font-weight: bold; background-color: #e3f2fd;")
        header.setEnabled(False)
        layout.addWidget(header)

        # Show pools button
        show_pools_button = QPushButton("Show All Pools")
        show_pools_button.clicked.connect(self._show_summoning_pools)
        layout.addWidget(show_pools_button)

        # Summon dragon button
        summon_button = QPushButton("Summon Dragon")
        summon_button.clicked.connect(self._demo_dragon_summoning)
        layout.addWidget(summon_button)

        # Kill dragon button
        kill_button = QPushButton("Kill Dragon (Return to Pool)")
        kill_button.clicked.connect(self._demo_dragon_death)
        layout.addWidget(kill_button)

        return group_widget

    def _create_bua_controls(self):
        """Create BUA control buttons."""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)

        # Header
        header = QPushButton("⚰️ BUA (Buried Units Area)")
        header.setStyleSheet("font-weight: bold; background-color: #f3e5f5;")
        header.setEnabled(False)
        layout.addWidget(header)

        # Show BUA button
        show_bua_button = QPushButton("Show All BUAs")
        show_bua_button.clicked.connect(self._show_buas)
        layout.addWidget(show_bua_button)

        # Bury units button
        bury_button = QPushButton("Bury Units from DUA")
        bury_button.clicked.connect(self._demo_burial)
        layout.addWidget(bury_button)

        # Show DUA button
        show_dua_button = QPushButton("Show DUA")
        show_dua_button.clicked.connect(self._show_dua)
        layout.addWidget(show_dua_button)

        return group_widget

    def _create_dragon_mechanics_controls(self):
        """Create dragon mechanics control buttons."""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)

        # Header
        header = QPushButton("🔥 Dragon Mechanics")
        header.setStyleSheet("font-weight: bold; background-color: #fff3e0;")
        header.setEnabled(False)
        layout.addWidget(header)

        # Dragon types button
        dragon_types_button = QPushButton("Show Dragon Types")
        dragon_types_button.clicked.connect(self._show_dragon_types)
        layout.addWidget(dragon_types_button)

        # Dragon abilities button
        abilities_button = QPushButton("Show Dragon Abilities")
        abilities_button.clicked.connect(self._show_dragon_abilities)
        layout.addWidget(abilities_button)

        return group_widget

    def _create_spell_targeting_controls(self):
        """Create spell targeting control buttons."""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)

        # Header
        header = QPushButton("✨ Spell Targeting")
        header.setStyleSheet("font-weight: bold; background-color: #e8f5e8;")
        header.setEnabled(False)
        layout.addWidget(header)

        # Show spell targets button
        spell_targets_button = QPushButton("Show Spell Targets")
        spell_targets_button.clicked.connect(self._show_spell_targets)
        layout.addWidget(spell_targets_button)

        # Demo DUA spell button
        dua_spell_button = QPushButton("Demo DUA Spell")
        dua_spell_button.clicked.connect(self._demo_dua_spell)
        layout.addWidget(dua_spell_button)

        # Demo BUA spell button
        bua_spell_button = QPushButton("Demo BUA Spell")
        bua_spell_button.clicked.connect(self._demo_bua_spell)
        layout.addWidget(bua_spell_button)

        return group_widget

    def _show_all_status(self):
        """Show comprehensive status of all systems."""
        status = []
        status.append("=== Dragon Dice: Summoning Pool & BUA Integration ===")
        status.append("")

        # Summoning Pool Status
        status.append("🐉 SUMMONING POOLS:")
        for player in self.players:
            pool_stats = self.summoning_pool_manager.get_pool_statistics(player)
            status.append(f"  {player}: {pool_stats['total_dragons']} dragons")
            for dragon_type, count in pool_stats['dragon_types'].items():
                status.append(f"    - {dragon_type}: {count}")
        status.append("")

        # BUA Status
        status.append("⚰️ BUA (BURIED UNITS AREA):")
        for player in self.players:
            bua_stats = self.bua_manager.get_bua_statistics(player)
            status.append(f"  {player}: {bua_stats['total_units']} buried units")
            for species, count in bua_stats['species_breakdown'].items():
                status.append(f"    - {species}: {count}")
        status.append("")

        # DUA Status
        status.append("💀 DUA (DEAD UNITS AREA):")
        for player in self.players:
            dua_units = self.dua_manager.get_player_dua(player)
            status.append(f"  {player}: {len(dua_units)} dead units")
            for unit in dua_units:
                status.append(f"    - {unit.name} ({unit.species})")
        status.append("")

        # Current Player
        status.append(f"📍 Current Player: {self.current_player}")
        status.append("")

        self.display_area.setPlainText("\\n".join(status))

    def _show_summoning_pools(self):
        """Show detailed summoning pool information."""
        output = []
        output.append("=== SUMMONING POOLS ===")
        output.append("")

        for player in self.players:
            dragons = self.summoning_pool_manager.get_player_pool(player)
            output.append(f"🐉 {player}'s Summoning Pool:")
            
            if not dragons:
                output.append("  (No dragons in pool)")
            else:
                for dragon in dragons:
                    output.append(f"  - {dragon.get_display_name()}")
                    output.append(f"    Health: {dragon.health}/{dragon.max_health}")
                    output.append(f"    Elements: {', '.join(dragon.elements)}")
                    output.append(f"    Can summon from terrain: {dragon.can_be_summoned_from_terrain()}")
                    output.append(f"    Force value: {dragon.get_force_value()}")
            output.append("")

        self.display_area.setPlainText("\\n".join(output))

    def _show_buas(self):
        """Show detailed BUA information."""
        output = []
        output.append("=== BUA (BURIED UNITS AREA) ===")
        output.append("")

        for player in self.players:
            bua_units = self.bua_manager.get_player_bua(player)
            output.append(f"⚰️ {player}'s BUA:")
            
            if not bua_units:
                output.append("  (No buried units)")
            else:
                for unit in bua_units:
                    output.append(f"  - {unit.name} ({unit.species})")
                    output.append(f"    Health: {unit.health}")
                    output.append(f"    Elements: {', '.join(unit.elements)}")
            output.append("")

        output.append("📝 NOTE: Spells can target units in the BUA, but they cannot target the Summoning Pool.")
        self.display_area.setPlainText("\\n".join(output))

    def _show_dua(self):
        """Show detailed DUA information."""
        output = []
        output.append("=== DUA (DEAD UNITS AREA) ===")
        output.append("")

        for player in self.players:
            dua_units = self.dua_manager.get_player_dua(player)
            output.append(f"💀 {player}'s DUA:")
            
            if not dua_units:
                output.append("  (No dead units)")
            else:
                for unit in dua_units:
                    output.append(f"  - {unit.name} ({unit.species})")
                    output.append(f"    Health: {unit.health}")
                    output.append(f"    Elements: {', '.join(unit.elements)}")
            output.append("")

        output.append("📝 NOTE: During Reserves Phase Retreat Step, dead units can be buried from DUA to BUA.")
        self.display_area.setPlainText("\\n".join(output))

    def _demo_dragon_summoning(self):
        """Demonstrate dragon summoning from pool."""
        output = []
        output.append("=== DRAGON SUMMONING DEMO ===")
        output.append("")

        player = self.current_player
        dragons = self.summoning_pool_manager.get_player_pool(player)
        
        if not dragons:
            output.append(f"❌ {player} has no dragons in summoning pool")
        else:
            # Summon the first dragon
            dragon = dragons[0]
            summoned_dragon = self.summoning_pool_manager.remove_dragon_from_pool(player, dragon.get_id())
            
            if summoned_dragon:
                output.append(f"✅ {player} summoned {summoned_dragon.get_display_name()}")
                output.append(f"Dragon moved from Summoning Pool to Air/Fire Mountain")
                output.append(f"Remaining dragons in pool: {len(self.summoning_pool_manager.get_player_pool(player))}")
            else:
                output.append(f"❌ Failed to summon dragon")
        
        output.append("")
        output.append("📝 NOTE: In the actual game, dragons are summoned using magic or special effects.")
        
        self.display_area.setPlainText("\\n".join(output))

    def _demo_dragon_death(self):
        """Demonstrate dragon death and return to pool."""
        output = []
        output.append("=== DRAGON DEATH DEMO ===")
        output.append("")

        player = self.current_player
        
        # Create a sample dragon that was "killed"
        killed_dragon = DragonModel("Killed Fire Drake", "DRAKE", "FIRE_ELEMENTAL", ["FIRE"], player)
        killed_dragon.health = 0  # Dead
        
        # Return to summoning pool
        killed_dragon.reset_health()  # Dragons return to pool at full health
        self.summoning_pool_manager.add_dragon_to_pool(player, killed_dragon)
        
        output.append(f"💀 {killed_dragon.get_display_name()} was killed in combat")
        output.append(f"✅ Dragon returned to {player}'s Summoning Pool at full health")
        output.append(f"Dragons in pool: {len(self.summoning_pool_manager.get_player_pool(player))}")
        output.append("")
        output.append("📝 NOTE: When dragons are killed, they return to their owner's Summoning Pool.")
        
        self.display_area.setPlainText("\\n".join(output))

    def _demo_burial(self):
        """Demonstrate burying units from DUA to BUA."""
        output = []
        output.append("=== BURIAL DEMO ===")
        output.append("")

        player = self.current_player
        dua_units = self.dua_manager.get_player_dua(player)
        
        if not dua_units:
            output.append(f"❌ {player} has no dead units in DUA")
        else:
            # Bury the first unit
            unit_to_bury = dua_units[0]
            removed_unit = self.dua_manager.remove_unit_from_dua(player, unit_to_bury.get_id())
            
            if removed_unit:
                self.bua_manager.bury_unit(player, removed_unit)
                output.append(f"⚰️ Buried {removed_unit.name} ({removed_unit.species})")
                output.append(f"Moved from {player}'s DUA to BUA")
                output.append(f"Remaining in DUA: {len(self.dua_manager.get_player_dua(player))}")
                output.append(f"Total in BUA: {len(self.bua_manager.get_player_bua(player))}")
            else:
                output.append(f"❌ Failed to bury unit")
        
        output.append("")
        output.append("📝 NOTE: Burial occurs during the Retreat Step of the Reserves Phase.")
        
        self.display_area.setPlainText("\\n".join(output))

    def _show_dragon_types(self):
        """Show information about dragon types."""
        output = []
        output.append("=== DRAGON TYPES ===")
        output.append("")

        # Show examples of different dragon types
        dragon_examples = [
            ("Elemental", "Standard dragons with one element"),
            ("Hybrid", "Dragons with two elements - both breath effects apply"),
            ("Ivory", "Can be summoned with any element, only from Summoning Pool"),
            ("Ivory Hybrid", "One element + ivory, special summoning rules"),
            ("White", "10 health, doubled damage and treasure, counts as 2 dragons"),
        ]

        for dragon_type, description in dragon_examples:
            output.append(f"🐉 {dragon_type} Dragons:")
            output.append(f"   {description}")
            output.append("")

        output.append("📝 NOTE: Different dragon types have different summoning and combat rules.")
        self.display_area.setPlainText("\\n".join(output))

    def _show_dragon_abilities(self):
        """Show dragon abilities and mechanics."""
        output = []
        output.append("=== DRAGON ABILITIES ===")
        output.append("")

        output.append("🔥 Dragon Combat:")
        output.append("  - Claw attacks deal damage to enemy units")
        output.append("  - Breath attacks apply elemental effects")
        output.append("  - Treasure results allow unit promotion")
        output.append("  - White Dragons have doubled damage and treasure")
        output.append("")

        output.append("🌟 Dragon Summoning:")
        output.append("  - Dragons start in the Summoning Pool")
        output.append("  - Can be summoned using magic or special effects")
        output.append("  - Most dragons can be summoned from terrain or pool")
        output.append("  - Ivory Dragons can only be summoned from pool")
        output.append("  - When killed, dragons return to Summoning Pool")
        output.append("")

        output.append("⚡ Special Rules:")
        output.append("  - Hybrid Dragons apply both elemental effects")
        output.append("  - White Dragons count as 2 dragons for force limits")
        output.append("  - Dragons can be affected by spells matching their elements")
        output.append("")

        self.display_area.setPlainText("\\n".join(output))

    def _show_spell_targets(self):
        """Show spell targeting capabilities."""
        output = []
        output.append("=== SPELL TARGETING ===")
        output.append("")

        output.append("✨ Valid Spell Targets:")
        output.append("  ✅ Armies (at terrains or in reserves)")
        output.append("  ✅ Individual Units (in armies)")
        output.append("  ✅ Terrains (for summoning, etc.)")
        output.append("  ✅ DUA (Dead Units Area) - for resurrection spells")
        output.append("  ✅ BUA (Buried Units Area) - for special effects")
        output.append("  ❌ Summoning Pool - CANNOT be targeted by spells")
        output.append("")

        output.append("🎯 Targeting Examples:")
        output.append("  - 'Resurrect Dead' targets units in your DUA")
        output.append("  - 'Summon Dragon' targets terrains")
        output.append("  - 'Promote Unit' targets units in armies")
        output.append("  - BUA-targeting spells can affect buried units")
        output.append("")

        output.append("📝 NOTE: Spells follow specific targeting rules based on their effects.")
        self.display_area.setPlainText("\\n".join(output))

    def _demo_dua_spell(self):
        """Demonstrate DUA-targeting spell."""
        output = []
        output.append("=== DUA SPELL DEMO ===")
        output.append("")

        # Find a DUA-targeting spell
        resurrect_spell = ALL_SPELLS.get("RESURRECT_DEAD")
        if not resurrect_spell:
            output.append("❌ Resurrect Dead spell not found")
            self.display_area.setPlainText("\\n".join(output))
            return

        output.append(f"🪄 Casting: {resurrect_spell.name}")
        output.append(f"Effect: {resurrect_spell.effect}")
        output.append("")

        # Get valid DUA targets
        game_state = {"all_players_data": {}}  # Simplified for demo
        valid_targets = self.spell_targeting_manager.get_valid_targets(
            resurrect_spell, self.current_player, game_state
        )

        dua_targets = valid_targets.get("dua_units", [])
        output.append(f"Valid DUA targets for {self.current_player}:")
        
        if not dua_targets:
            output.append("  (No valid DUA targets)")
        else:
            for target in dua_targets:
                description = self.spell_targeting_manager.get_target_description("dua", target)
                output.append(f"  - {description}")

        output.append("")
        output.append("📝 NOTE: DUA spells typically require element matching.")
        self.display_area.setPlainText("\\n".join(output))

    def _demo_bua_spell(self):
        """Demonstrate BUA-targeting spell."""
        output = []
        output.append("=== BUA SPELL DEMO ===")
        output.append("")

        output.append("🪄 Hypothetical BUA Spell:")
        output.append("Effect: Target units in your BUA that match the element of magic used")
        output.append("")

        # Show BUA targets
        bua_units = self.bua_manager.get_player_bua(self.current_player)
        output.append(f"Available BUA targets for {self.current_player}:")
        
        if not bua_units:
            output.append("  (No units in BUA)")
        else:
            for unit in bua_units:
                output.append(f"  - {unit.name} ({unit.species})")
                output.append(f"    Elements: {', '.join(unit.elements)}")

        output.append("")
        output.append("📝 NOTE: BUA spells are rare but can affect buried units.")
        output.append("📝 NOTE: Spells CANNOT target the Summoning Pool.")
        self.display_area.setPlainText("\\n".join(output))


def main():
    """Run the summoning pool and BUA integration example."""
    app = QApplication(sys.argv)
    window = SummoningPoolBUAIntegrationExample()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()