"""
Example integration showing how to use the EnhancedManeuverDialog in the main gameplay view.

This file demonstrates how to replace the existing maneuver handling with the new
detailed die face input system that properly tracks species abilities.
"""

from typing import Any, Dict, List

from views.enhanced_maneuver_dialog import EnhancedManeuverDialog


class ManeuverIntegrationExample:
    """
    Example class showing how to integrate the enhanced maneuver dialog
    into the main gameplay view's maneuver handling.
    """

    def __init__(self, game_engine, main_view):
        self.game_engine = game_engine
        self.main_view = main_view

    def handle_maneuver_decision(self, wants_to_maneuver: bool):
        """
        Replace the existing _handle_maneuver_decision method in MainGameplayView.

        This shows how to use the enhanced maneuver dialog instead of the simple one.
        """
        if wants_to_maneuver:
            self._show_enhanced_maneuver_dialog()
        else:
            # Player chose not to maneuver, proceed to action decision
            self.main_view.maneuver_decision_signal.emit(False)
            self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
            self.game_engine._current_march_step = "DECIDE_ACTION"
            self.game_engine.game_state_updated.emit()

    def _show_enhanced_maneuver_dialog(self):
        """Show the enhanced maneuver dialog with detailed die face input."""
        try:
            # Get the current acting army
            acting_army = self.game_engine.get_current_acting_army()
            if not acting_army:
                print("No acting army selected")
                return

            # Get current player and location info
            current_player = self.game_engine.get_current_player_name()
            location = acting_army.get("location", "Unknown")

            # Get current terrain face
            all_terrain_data = self.game_engine.get_all_terrain_data()
            current_terrain_face = all_terrain_data.get(location, {}).get("current_face", 1)

            # Find opposing players at the same location
            opposing_players = []
            opposing_armies = []
            all_players_data = self.game_engine.get_all_players_data()

            for player_name, player_data in all_players_data.items():
                if player_name != current_player:
                    for army_name, army_data in player_data.get("armies", {}).items():
                        if army_data.get("location") == location:
                            opposing_players.append(player_name)
                            opposing_armies.append(army_data)

            # Create and show enhanced maneuver dialog
            dialog = EnhancedManeuverDialog(
                maneuvering_player=current_player,
                maneuvering_army=acting_army,
                location=location,
                current_terrain_face=current_terrain_face,
                opposing_players=opposing_players,
                opposing_armies=opposing_armies,
                parent=self.main_view,
            )

            # Connect signals
            dialog.maneuver_completed.connect(self._handle_enhanced_maneuver_completed)
            dialog.maneuver_cancelled.connect(self._handle_enhanced_maneuver_cancelled)

            # Show dialog
            dialog.exec()

        except Exception as e:
            print(f"Error showing enhanced maneuver dialog: {e}")
            # Fallback to simple decision
            self.main_view.maneuver_decision_signal.emit(True)

    def _handle_enhanced_maneuver_completed(self, maneuver_result: Dict[str, Any]):
        """Handle completed maneuver from enhanced dialog."""
        print(f"Enhanced maneuver completed: {maneuver_result}")

        # Apply maneuver results to game state
        if maneuver_result.get("success"):
            success = self.game_engine.apply_maneuver_results(maneuver_result)
            if success:
                # Extract result details
                army_name = maneuver_result.get("army", {}).get("name", "Unknown Army")
                location = maneuver_result.get("location", "Unknown")
                direction = maneuver_result.get("direction", "UP")
                old_face = maneuver_result.get("old_face", "?")
                new_face = maneuver_result.get("new_face", "?")
                maneuvering_total = maneuver_result.get("maneuvering_total", 0)
                counter_total = maneuver_result.get("counter_total", 0)

                # Create detailed result text
                result_text = f"{army_name} maneuvered at {location} - turned terrain {direction} from face {old_face} to {new_face}"

                if maneuver_result.get("was_opposed"):
                    result_text += f" (Maneuver: {maneuvering_total} vs Counter: {counter_total})"
                else:
                    result_text += " (Unopposed)"

                # Check for species abilities used
                maneuvering_results = maneuver_result.get("maneuvering_results", {})
                counter_results = maneuver_result.get("counter_results", {})

                species_notes = []
                if self._check_for_species_ability_usage(maneuvering_results, location, "Dwarves", "Mountain Master"):
                    species_notes.append("⛰️ Dwarven Mountain Master activated!")
                if self._check_for_species_ability_usage(maneuvering_results, location, "Goblins", "Swamp Master"):
                    species_notes.append("🏔️ Goblin Swamp Master activated!")
                if self._check_for_species_ability_usage(counter_results, location, "Dwarves", "Mountain Master"):
                    species_notes.append("⛰️ Counter-maneuvering Dwarven Mountain Master activated!")
                if self._check_for_species_ability_usage(counter_results, location, "Goblins", "Swamp Master"):
                    species_notes.append("🏔️ Counter-maneuvering Goblin Swamp Master activated!")

                if species_notes:
                    result_text += "\n" + "\n".join(species_notes)

                # Emit signal with detailed results
                self.main_view.maneuver_input_submitted_signal.emit(result_text)

                # Check for eighth face capture
                if new_face == 8:
                    print(f"🏆 {army_name} captured {location}!")
                    # Additional logic for terrain capture could go here

            else:
                print("Failed to apply enhanced maneuver results")
        else:
            # Maneuver failed
            army_name = maneuver_result.get("army", {}).get("name", "Unknown Army")
            location = maneuver_result.get("location", "Unknown")
            maneuvering_total = maneuver_result.get("maneuvering_total", 0)
            counter_total = maneuver_result.get("counter_total", 0)

            result_text = f"{army_name} failed to maneuver at {location} (Maneuver: {maneuvering_total} vs Counter: {counter_total})"
            self.main_view.maneuver_input_submitted_signal.emit(result_text)

        # Continue to next phase of turn
        self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
        self.game_engine._current_march_step = "DECIDE_ACTION"
        self.game_engine.game_state_updated.emit()

    def _handle_enhanced_maneuver_cancelled(self):
        """Handle cancelled maneuver from enhanced dialog."""
        print("Enhanced maneuver cancelled")

        # Player cancelled maneuver, proceed to action decision
        self.main_view.maneuver_decision_signal.emit(False)
        self.game_engine.march_step_change_requested.emit("DECIDE_ACTION")
        self.game_engine._current_march_step = "DECIDE_ACTION"
        self.game_engine.game_state_updated.emit()

    def _check_for_species_ability_usage(
        self, roll_results: Dict[str, List[str]], location: str, species: str, ability_name: str
    ) -> bool:
        """Check if a species ability was likely used based on die results."""
        # This is a simplified check - in a full implementation,
        # the SAI processor would track this information

        # Check if location has earth element (required for Mountain Master and Swamp Master)
        terrain_mappings = {
            "Highland": ["fire", "earth"],
            "Flatland": ["air", "earth"],
            "Swampland": ["water", "earth"],
        }

        location_elements = []
        for terrain_type, elements in terrain_mappings.items():
            if terrain_type.lower() in location.lower():
                location_elements = elements
                break

        if "earth" not in location_elements:
            return False

        # Check if any unit had melee results (which would convert to maneuver for these abilities)
        for unit_name, face_results in roll_results.items():
            if species.lower() in unit_name.lower():  # Simplified species check
                melee_count = sum(1 for face in face_results if face.lower().strip() in ["m", "melee"])
                if melee_count > 0:
                    return True

        return False


# Usage example for integrating into MainGameplayView:
"""
To integrate this into your main gameplay view, you would:

1. Import the EnhancedManeuverDialog and ManeuverIntegrationExample
2. Replace the existing _handle_maneuver_decision method with the enhanced version
3. Update the _show_maneuver_dialog method to use the enhanced dialog

Example changes to MainGameplayView:

```python
from views.enhanced_maneuver_dialog import EnhancedManeuverDialog
from views.maneuver_integration_example import ManeuverIntegrationExample

class MainGameplayView(QWidget):
    def __init__(self, game_engine):
        # ... existing initialization ...
        self.maneuver_integration = ManeuverIntegrationExample(game_engine, self)
    
    def _handle_maneuver_decision(self, wants_to_maneuver: bool):
        # Replace existing method with enhanced version
        self.maneuver_integration.handle_maneuver_decision(wants_to_maneuver)
    
    # Remove or comment out the old _show_maneuver_dialog method
    # def _show_maneuver_dialog(self):
    #     # Old implementation using simple ManeuverDialog
```

This integration provides:
- Individual die face input for proper SAI tracking
- Mountain Master and Swamp Master species ability detection
- Detailed maneuver result reporting
- Proper terrain face changes
- Enhanced user experience with step-by-step flow
"""
