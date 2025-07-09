"""
Example integration showing how to use the MagicActionDialog in the main gameplay view.

This file demonstrates how to integrate magic actions with detailed die face input,
spell selection, and Amazon Terrain Harmony support.
"""

from typing import Any, Dict, List

from views.magic_action_dialog import MagicActionDialog


class MagicIntegrationExample:
    """
    Example class showing how to integrate the magic action dialog
    into the main gameplay view's action handling.
    """

    def __init__(self, game_engine, main_view):
        self.game_engine = game_engine
        self.main_view = main_view

    def handle_magic_action_selected(self):
        """
        Replace or enhance the existing magic action handling in MainGameplayView.

        This shows how to use the magic action dialog instead of simple action dialog.
        """
        try:
            # Get the current acting army
            acting_army = self.game_engine.get_current_acting_army()
            if not acting_army:
                print("No acting army selected")
                return

            # Get current player and location info
            current_player = self.game_engine.get_current_player_name()
            location = acting_army.get("location", "Unknown")

            # Check if army has any units capable of magic
            if not self._has_magic_capable_units(acting_army):
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self.main_view, "No Magic Units", "No units in this army are capable of performing magic actions."
                )
                return

            # Create and show magic action dialog
            dialog = MagicActionDialog(
                caster_name=current_player,
                caster_army=acting_army,
                location=location,
                parent=self.main_view,
            )

            # Connect signals
            dialog.magic_completed.connect(self._handle_magic_completed)
            dialog.magic_cancelled.connect(self._handle_magic_cancelled)

            # Show dialog
            dialog.exec()

        except Exception as e:
            print(f"Error showing magic action dialog: {e}")
            # Fallback to simple action
            self.main_view.magic_action_selected_signal.emit()

    def _has_magic_capable_units(self, army: Dict[str, Any]) -> bool:
        """
        Check if army has units capable of performing magic actions.

        In Dragon Dice, all units can potentially generate magic results,
        but some are more effective than others.
        """
        army_units = army.get("units", [])
        return len(army_units) > 0  # All units can attempt magic

    def _handle_magic_completed(self, magic_result: Dict[str, Any]):
        """Handle completed magic action from dialog."""
        print(f"Magic action completed: {magic_result}")

        # Extract result details
        caster = magic_result.get("caster", "Unknown")
        location = magic_result.get("location", "Unknown")
        magic_points_by_element = magic_result.get("magic_points_by_element", {})
        amazon_flexible_magic = magic_result.get("amazon_flexible_magic", {})
        cast_spells = magic_result.get("cast_spells", [])

        # Calculate total magic generated
        total_magic_generated = sum(magic_points_by_element.values())
        total_amazon_magic = sum(amazon_flexible_magic.values())

        # Create detailed result text
        result_text = f"{caster} performed magic action at {location}"

        if total_magic_generated > 0:
            result_text += f" - {total_magic_generated} magic points generated"

            # Show magic points by element
            magic_details = []
            for element, points in magic_points_by_element.items():
                if points > 0:
                    icon = {"AIR": "💨", "DEATH": "💀", "EARTH": "🌍", "FIRE": "🔥", "WATER": "🌊"}.get(element, "✨")
                    magic_details.append(f"{icon} {element}: {points}")

            if magic_details:
                result_text += f" ({', '.join(magic_details)})"

        if total_amazon_magic > 0:
            result_text += f" + {total_amazon_magic} flexible Amazon magic"

        # Show spells cast
        if cast_spells:
            result_text += f"\n🔮 Spells Cast ({len(cast_spells)}):"
            spell_effects = []

            for spell_name, cost, element in cast_spells:
                element_icon = {
                    "AIR": "💨",
                    "DEATH": "💀",
                    "EARTH": "🌍",
                    "FIRE": "🔥",
                    "WATER": "🌊",
                    "ELEMENTAL": "✨",
                }.get(element, "⭐")
                spell_effects.append(f"  • {spell_name} ({element_icon} {element}, Cost: {cost})")

            result_text += "\n" + "\n".join(spell_effects)

            # Check for notable spell effects
            spell_notes = self._analyze_spell_effects(cast_spells)
            if spell_notes:
                result_text += "\n" + "\n".join(spell_notes)
        else:
            result_text += "\n🔮 No spells cast"

        # Check for Amazon Terrain Harmony usage
        if amazon_flexible_magic and self._has_amazon_units(magic_result.get("magic_results", {})):
            result_text += "\n⚖️ Amazon Terrain Harmony: Magic matched terrain elements"

        # Apply spell effects to game state
        if cast_spells:
            success = self.game_engine.apply_spell_effects(magic_result)
            if not success:
                print("Failed to apply spell effects")

        # Emit signal with detailed results
        self.main_view.magic_action_completed_signal.emit(result_text)

        # Continue to next phase of turn
        self.game_engine.march_step_change_requested.emit("SECOND_MARCH")
        self.game_engine.game_state_updated.emit()

    def _handle_magic_cancelled(self):
        """Handle cancelled magic action from dialog."""
        print("Magic action cancelled")

        # Player cancelled magic action, return to action selection
        self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
        self.game_engine.game_state_updated.emit()

    def _has_amazon_units(self, magic_results: Dict[str, List[str]]) -> bool:
        """Check if any units in the magic results are Amazons."""
        # This would check the actual unit species data
        # For now, use a simple heuristic
        return any("amazon" in unit_name.lower() for unit_name in magic_results.keys())

    def _analyze_spell_effects(self, cast_spells: List[tuple]) -> List[str]:
        """Analyze cast spells and provide relevant notes."""
        notes = []

        # Check for offensive spells
        offensive_spells = [
            "Hailstorm",
            "Lightning Strike",
            "Finger of Death",
            "Firebolt",
            "Fearful Flames",
            "Firestorm",
            "Ash Storm",
        ]

        # Check for defensive spells
        defensive_spells = ["Stone Skin", "Watery Double", "Flashfire", "Fiery Weapon"]

        # Check for terrain manipulation spells
        terrain_spells = ["Flash Flood", "Transmute Rock to Mud", "Wall of Thorns", "Tidal Wave", "Fields of Ice"]

        offensive_count = sum(1 for spell_name, _, _ in cast_spells if spell_name in offensive_spells)
        defensive_count = sum(1 for spell_name, _, _ in cast_spells if spell_name in defensive_spells)
        terrain_count = sum(1 for spell_name, _, _ in cast_spells if spell_name in terrain_spells)

        if offensive_count > 0:
            notes.append(f"⚔️ {offensive_count} offensive spell{'s' if offensive_count > 1 else ''} cast")

        if defensive_count > 0:
            notes.append(f"🛡️ {defensive_count} defensive spell{'s' if defensive_count > 1 else ''} cast")

        if terrain_count > 0:
            notes.append(f"🌍 {terrain_count} terrain manipulation spell{'s' if terrain_count > 1 else ''} cast")

        # Check for specific notable spells
        for spell_name, cost, element in cast_spells:
            if spell_name == "Summon Dragon":
                notes.append(f"🐉 Dragon summoned using {element} magic!")
            elif spell_name == "Summon White Dragon":
                notes.append("🐉 White Dragon summoned with mixed elements!")
            elif spell_name == "Resurrect Dead":
                notes.append("💀 Units returned from the dead!")
            elif spell_name == "Lightning Strike":
                notes.append("⚡ Targeted elimination spell used!")

        return notes


# Usage example for integrating into MainGameplayView:
"""
To integrate this into your main gameplay view, you would:

1. Import the MagicActionDialog and MagicIntegrationExample
2. Replace the existing magic action handling with the enhanced version
3. Update the action selection flow to use the magic dialog

Example changes to MainGameplayView:

```python
from views.magic_action_dialog import MagicActionDialog
from views.magic_integration_example import MagicIntegrationExample

class MainGameplayView(QWidget):
    def __init__(self, game_engine):
        # ... existing initialization ...
        self.magic_integration = MagicIntegrationExample(game_engine, self)
        
        # Add new signal for magic completion
        self.magic_action_completed_signal = Signal(str)
    
    def _handle_action_selected(self, action_type: str):
        # Enhance existing method to handle magic actions
        if action_type == "MAGIC":
            self.magic_integration.handle_magic_action_selected()
        elif action_type == "MELEE":
            # Use enhanced melee dialog
            # ... existing melee handling ...
        elif action_type == "MISSILE":
            # Use enhanced missile dialog
            # ... existing missile handling ...
        # ... handle other action types ...
```

This integration provides:
- Individual die face input for precise magic tracking
- Element-specific magic point calculation
- Amazon Terrain Harmony support for flexible element assignment
- Comprehensive spell database integration
- Spell selection based on available magic points and army composition
- Detailed spell effect tracking and reporting
- Proper game state integration with spell effects
"""
