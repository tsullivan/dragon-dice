from PySide6.QtCore import QObject, Signal
import uuid
from typing import Optional, Dict, Any

class EffectManager(QObject):
    """Manages active effects in the game, their durations, and application."""
    effects_changed = Signal() # Emitted when effects are added or removed

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.active_effects = [] # List of effect dictionaries

    def _generate_unique_effect_id(self):
        return str(uuid.uuid4())

    def add_effect(self, description: str, source: str, target_type: str, target_identifier: str,
                   duration_type: str, duration_value: int,
                   caster_player_name: str, affected_player_name: Optional[str] = None):
        """Adds a new active effect."""
        effect = {
            "id": self._generate_unique_effect_id(),
            "description": description, "source": source, "target_type": target_type,
            "target_identifier": target_identifier, "duration_type": duration_type,
            "duration_value": duration_value, "caster_player_name": caster_player_name,
            "affected_player_name": affected_player_name or caster_player_name
        }
        self.active_effects.append(effect)
        print(f"EffectManager: Effect added - {description} on {target_identifier}")
        self.effects_changed.emit()

    def process_effect_expirations(self, current_player_name: str):
        """Processes effects that might expire at the start of a player's turn or round."""
        # TODO: Implement logic to check and remove expired effects based on duration_type and current_player_name
        # Remember to emit self.effects_changed if any effects are removed.
        pass

    def get_displayable_effects(self) -> list[str]:
        """Returns a list of strings representing active effects for UI display."""
        # TODO: Implement formatting for display
        return [f"Effect: {effect['description']} on {effect['target_identifier']}" for effect in self.active_effects]

    def get_active_modifiers(self, target_player_name: str, target_army_identifier: Optional[str], action_type: str) -> Dict[str, Any]:
        """
        Queries for active modifiers affecting a target for a specific action type.
        Returns a dictionary of modifiers, e.g., {"melee_bonus": 1, "halve_results": True}.
        """
        modifiers = {"melee_bonus": 0, "missile_bonus": 0, "magic_bonus": 0, "save_bonus": 0, "halve_results": False, "double_results": False}
        # TODO: Implement more sophisticated effect checking based on target_type, target_identifier, and effect properties.
        # This is a simplified example.
        for effect in self.active_effects:
            # Check if the effect applies to the current player/army and action
            if effect.get("affected_player_name") == target_player_name: # Basic check
                if "melee results -3" in effect.get("description", "").lower() and action_type == "MELEE":
                    modifiers["melee_bonus"] -= 3
                elif "all results halved" in effect.get("description", "").lower(): # General halving
                    modifiers["halve_results"] = True
                elif "melee results halved" in effect.get("description", "").lower() and action_type == "MELEE":
                    modifiers["halve_results"] = True
                # Add more specific effect checks here

        print(f"EffectManager: Modifiers for {target_player_name} ({action_type}): {modifiers}")
        return modifiers
