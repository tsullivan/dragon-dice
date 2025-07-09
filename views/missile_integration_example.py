"""
Example integration showing how to use the MissileCombatDialog in the main gameplay view.

This file demonstrates how to integrate missile actions with detailed die face input
and proper handling of Coral Elf species abilities.
"""

from typing import Any, Dict, List

from views.missile_combat_dialog import MissileCombatDialog


class MissileIntegrationExample:
    """
    Example class showing how to integrate the missile combat dialog
    into the main gameplay view's action handling.
    """

    def __init__(self, game_engine, main_view):
        self.game_engine = game_engine
        self.main_view = main_view

    def handle_missile_action_selected(self):
        """
        Replace or enhance the existing missile action handling in MainGameplayView.

        This shows how to use the missile combat dialog instead of simple action dialog.
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

            # Find available targets for missile attack
            available_targets = self._get_missile_targets(current_player, location)

            if not available_targets:
                from components.error_dialog import ErrorDialog

                ErrorDialog.show_warning(
                    self.main_view,
                    "No Valid Targets",
                    "No valid targets found for missile attack.\n"
                    "Missile attacks cannot target armies at other Home Terrains or in Reserve Areas.",
                )
                return

            # Create and show missile combat dialog
            dialog = MissileCombatDialog(
                attacker_name=current_player,
                attacker_army=acting_army,
                available_targets=available_targets,
                location=location,
                parent=self.main_view,
            )

            # Connect signals
            dialog.combat_completed.connect(self._handle_missile_completed)
            dialog.combat_cancelled.connect(self._handle_missile_cancelled)

            # Show dialog
            dialog.exec()

        except Exception as e:
            print(f"Error showing missile combat dialog: {e}")
            # Fallback to simple action
            self.main_view.missile_action_selected_signal.emit()

    def _get_missile_targets(self, current_player: str, attacker_location: str) -> List[Dict[str, Any]]:
        """
        Get available targets for missile attack based on Dragon Dice rules.

        Missile targeting rules:
        - Can target any opponent's army
        - Cannot target armies at other Home Terrains if attacking from Home Terrain
        - Cannot target armies in opponent's Reserve Area
        """
        available_targets = []
        all_players_data = self.game_engine.get_all_players_data()
        all_terrain_data = self.game_engine.get_all_terrain_data()

        # Determine if attacker is at a Home Terrain
        attacker_at_home = self._is_home_terrain(attacker_location, current_player)

        for player_name, player_data in all_players_data.items():
            if player_name == current_player:
                continue  # Skip current player

            for army_name, army_data in player_data.get("armies", {}).items():
                army_location = army_data.get("location", "")

                # Skip armies in Reserve Area
                if army_location.lower() == "reserve" or "reserve" in army_location.lower():
                    continue

                # Skip armies at other Home Terrains if attacker is at Home Terrain
                if attacker_at_home and self._is_home_terrain(army_location, player_name):
                    continue

                # Valid target
                target_info = {"player_name": player_name, "army_data": army_data, "location": army_location}
                available_targets.append(target_info)

        return available_targets

    def _is_home_terrain(self, location: str, player_name: str) -> bool:
        """Check if a location is a Home Terrain for the given player."""
        # This would check game state to determine home terrains
        # For now, use a simple heuristic
        return "home" in location.lower() or player_name.lower() in location.lower()

    def _handle_missile_completed(self, missile_result: Dict[str, Any]):
        """Handle completed missile combat from dialog."""
        print(f"Missile combat completed: {missile_result}")

        # Extract result details
        attacker = missile_result.get("attacker", "Unknown")
        defender = missile_result.get("defender", "Unknown")
        target_army = missile_result.get("target_army", {})
        target_location = missile_result.get("target_location", "Unknown")
        final_damage = missile_result.get("final_damage", 0)
        defensive_volley_used = missile_result.get("defensive_volley_used", False)
        defensive_volley_damage = missile_result.get("defensive_volley_damage", 0)

        # Create detailed result text
        result_text = (
            f"{attacker} fired missile attack at {defender}'s {target_army.get('name', 'army')} at {target_location}"
        )

        if final_damage > 0:
            result_text += f" - {final_damage} damage dealt"
        else:
            result_text += " - no damage dealt"

        # Check for Coral Elf abilities used
        attacker_results = missile_result.get("attacker_results", {})
        defender_results = missile_result.get("defender_results", {})

        ability_notes = []
        if self._check_for_coastal_dodge_usage(defender_results, target_location):
            ability_notes.append("🌊 Coastal Dodge activated! (Maneuver counted as saves)")

        if self._check_for_intangibility_usage(defender_results, target_location):
            ability_notes.append("👻 Intangibility activated! (Scalder maneuver counted as saves vs missile)")

        if defensive_volley_used:
            result_text += f"\n🏹 Defensive Volley counter-attack: {defensive_volley_damage} damage to attacker"
            ability_notes.append("💨 Defensive Volley activated! (Coral Elves counter-attacked)")

        if self._check_for_coral_elf_missile_save_usage(defender_results):
            ability_notes.append("🏹 Coral Elf ability: Missile results counted as saves")

        if ability_notes:
            result_text += "\n" + "\n".join(ability_notes)

        # Apply results to game state
        if final_damage > 0:
            # Apply damage to target army
            success = self.game_engine.apply_missile_damage(missile_result)
            if not success:
                print("Failed to apply missile damage")

        if defensive_volley_damage > 0:
            # Apply counter-damage to attacker
            counter_damage_result = {
                "target_army": missile_result.get("attacker_army", {}),
                "damage": defensive_volley_damage,
                "damage_type": "defensive_volley",
            }
            success = self.game_engine.apply_missile_damage(counter_damage_result)
            if not success:
                print("Failed to apply defensive volley damage")

        # Emit signal with detailed results
        self.main_view.missile_action_completed_signal.emit(result_text)

        # Continue to next phase of turn
        self.game_engine.march_step_change_requested.emit("SECOND_MARCH")
        self.game_engine.game_state_updated.emit()

    def _handle_missile_cancelled(self):
        """Handle cancelled missile combat from dialog."""
        print("Missile combat cancelled")

        # Player cancelled missile action, return to action selection
        self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
        self.game_engine.game_state_updated.emit()

    def _check_for_coastal_dodge_usage(self, defender_results: Dict[str, List[str]], target_location: str) -> bool:
        """Check if Coastal Dodge was likely used based on die results."""
        # Check if location has water element (required for Coastal Dodge)
        terrain_mappings = {
            "Coastland": ["air", "water"],
            "Swampland": ["water", "earth"],
            "Feyland": ["water", "fire"],
        }

        location_elements = []
        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in target_location.lower():
                location_elements = elements
                break

        if "water" not in location_elements:
            return False

        # Check if any Coral Elf unit had maneuver results (which would convert to saves)
        for unit_name, face_results in defender_results.items():
            if "coral" in unit_name.lower():  # Simplified species check
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])
                if maneuver_count > 0:
                    return True

        return False

    def _check_for_coral_elf_missile_save_usage(self, defender_results: Dict[str, List[str]]) -> bool:
        """Check if Coral Elf missile→save ability was used."""
        # Check if any Coral Elf unit had missile results during saves
        for unit_name, face_results in defender_results.items():
            if "coral" in unit_name.lower():  # Simplified species check
                missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])
                if missile_count > 0:
                    return True

        return False

    def _check_for_intangibility_usage(self, defender_results: Dict[str, List[str]], target_location: str) -> bool:
        """Check if Scalder Intangibility was likely used based on die results."""
        # Check if location has water element (required for Intangibility)
        terrain_mappings = {
            "Coastland": ["air", "water"],
            "Swampland": ["water", "earth"],
            "Feyland": ["water", "fire"],
        }

        location_elements = []
        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in target_location.lower():
                location_elements = elements
                break

        if "water" not in location_elements:
            return False

        # Check if any Scalder unit had maneuver results (which would convert to saves vs missile)
        for unit_name, face_results in defender_results.items():
            if "scalder" in unit_name.lower():  # Simplified species check
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])
                if maneuver_count > 0:
                    return True

        return False


# Usage example for integrating into MainGameplayView:
"""
To integrate this into your main gameplay view, you would:

1. Import the MissileCombatDialog and MissileIntegrationExample
2. Replace the existing missile action handling with the enhanced version
3. Update the action selection flow to use the missile dialog

Example changes to MainGameplayView:

```python
from views.missile_combat_dialog import MissileCombatDialog
from views.missile_integration_example import MissileIntegrationExample

class MainGameplayView(QWidget):
    def __init__(self, game_engine):
        # ... existing initialization ...
        self.missile_integration = MissileIntegrationExample(game_engine, self)
        
        # Add new signal for missile completion
        self.missile_action_completed_signal = Signal(str)
    
    def _handle_action_selected(self, action_type: str):
        # Enhance existing method to handle missile actions
        if action_type == "MISSILE":
            self.missile_integration.handle_missile_action_selected()
        elif action_type == "MELEE":
            # Use enhanced melee dialog
            # ... existing melee handling ...
        # ... handle other action types ...
```

This integration provides:
- Target selection with proper missile targeting rules
- Individual die face input for precise SAI tracking
- Coastal Dodge ability detection and conversion
- Defensive Volley counter-attack handling
- Comprehensive result reporting with ability usage
- Proper game state integration
"""
