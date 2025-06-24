from PySide6.QtCore import QObject, Signal
import uuid
from typing import Optional, Dict, Any, List
import constants


class EffectManager(QObject):
    """Manages active effects in the game, their durations, and application."""

    effects_changed = Signal()  # Emitted when effects are added or removed

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.active_effects = []  # List of effect dictionaries
    
    def remove_effect_by_id(self, effect_id: str) -> bool:
        """Remove a specific effect by its ID. Returns True if found and removed."""
        for effect in self.active_effects:
            if effect.get("id") == effect_id:
                self.active_effects.remove(effect)
                print(f"EffectManager: Removed effect: {effect.get('description', 'Unknown')}")
                self.effects_changed.emit()
                return True
        return False
    
    def clear_all_effects(self):
        """Remove all active effects."""
        if self.active_effects:
            print(f"EffectManager: Clearing {len(self.active_effects)} active effects")
            self.active_effects.clear()
            self.effects_changed.emit()
    
    def get_effects_by_player(self, player_name: str) -> List[Dict[str, Any]]:
        """Get all effects affecting a specific player."""
        return [
            effect for effect in self.active_effects
            if effect.get("affected_player_name") == player_name
        ]
    
    def get_effects_by_caster(self, caster_name: str) -> List[Dict[str, Any]]:
        """Get all effects cast by a specific player."""
        return [
            effect for effect in self.active_effects
            if effect.get("caster_player_name") == caster_name
        ]

    def _generate_unique_effect_id(self):
        return str(uuid.uuid4())

    def add_effect(
        self,
        description: str,
        source: str,
        target_type: str,
        target_identifier: str,
        duration_type: str,
        duration_value: int,
        caster_player_name: str,
        affected_player_name: Optional[str] = None,
    ):
        """Adds a new active effect."""
        effect = {
            "id": self._generate_unique_effect_id(),
            "description": description,
            "source": source,
            "target_type": target_type,
            "target_identifier": target_identifier,
            "duration_type": duration_type,
            "duration_value": duration_value,
            "caster_player_name": caster_player_name,
            "affected_player_name": affected_player_name or caster_player_name,
        }
        self.active_effects.append(effect)
        print(f"EffectManager: Effect added - {description} on {target_identifier} (duration: {duration_type})")
        self.effects_changed.emit()
        return effect["id"]  # Return effect ID for potential removal

    def process_effect_expirations(self, current_player_name: str, current_phase: str = None):
        """Processes effects that might expire at the start of a player's turn or round."""
        effects_to_remove = []
        
        for effect in self.active_effects:
            should_expire = False
            duration_type = effect.get("duration_type", "")
            caster_name = effect.get("caster_player_name", "")
            affected_name = effect.get("affected_player_name", "")
            
            # Check expiration conditions based on duration type
            if duration_type == constants.EFFECT_DURATION_NEXT_TURN_CASTER:
                # Expires at the start of the caster's next turn
                if current_player_name == caster_name:
                    should_expire = True
                    print(f"EffectManager: Effect '{effect['description']}' expires (caster's turn)")
            
            elif duration_type == constants.EFFECT_DURATION_NEXT_TURN_TARGET:
                # Expires at the start of the target's next turn
                if current_player_name == affected_name:
                    should_expire = True
                    print(f"EffectManager: Effect '{effect['description']}' expires (target's turn)")
            
            elif duration_type == "END_OF_TURN":
                # Expires at the end of the current turn (processed at start of next turn)
                should_expire = True
                print(f"EffectManager: Effect '{effect['description']}' expires (end of turn)")
            
            elif duration_type == "PERMANENT":
                # Never expires
                should_expire = False
            
            elif duration_type == "COUNTER_BASED":
                # Decrement counter and check if expired
                duration_value = effect.get("duration_value", 0)
                if duration_value <= 1:
                    should_expire = True
                    print(f"EffectManager: Effect '{effect['description']}' expires (counter reached 0)")
                else:
                    effect["duration_value"] = duration_value - 1
                    print(f"EffectManager: Effect '{effect['description']}' duration decreased to {duration_value - 1}")
            
            if should_expire:
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            self.active_effects.remove(effect)
            print(f"EffectManager: Removed expired effect: {effect['description']}")
        
        if effects_to_remove:
            self.effects_changed.emit()

    def get_displayable_effects(self) -> List[str]:
        """Returns a list of strings representing active effects for UI display."""
        if not self.active_effects:
            return ["No active effects"]
        
        display_effects = []
        for effect in self.active_effects:
            description = effect.get("description", "Unknown Effect")
            target = effect.get("target_identifier", "Unknown Target")
            caster = effect.get("caster_player_name", "Unknown")
            duration_type = effect.get("duration_type", "")
            duration_value = effect.get("duration_value", 0)
            
            # Format duration display
            duration_display = ""
            if duration_type == constants.EFFECT_DURATION_NEXT_TURN_CASTER:
                duration_display = f"(until {caster}'s turn)"
            elif duration_type == constants.EFFECT_DURATION_NEXT_TURN_TARGET:
                affected = effect.get("affected_player_name", "target")
                duration_display = f"(until {affected}'s turn)"
            elif duration_type == "COUNTER_BASED":
                duration_display = f"({duration_value} turns left)"
            elif duration_type == "PERMANENT":
                duration_display = "(permanent)"
            elif duration_type == "END_OF_TURN":
                duration_display = "(end of turn)"
            
            # Create formatted effect string
            effect_text = f"🔮 {description} on {target}"
            if duration_display:
                effect_text += f" {duration_display}"
            if caster:
                effect_text += f" [by {caster}]"
            
            display_effects.append(effect_text)
        
        return display_effects

    def get_active_modifiers(
        self,
        target_player_name: str,
        target_army_identifier: Optional[str],
        action_type: str,
    ) -> Dict[str, Any]:
        """
        Queries for active modifiers affecting a target for a specific action type.
        Returns a dictionary of modifiers, e.g., {"melee_bonus": 1, "halve_results": True}.
        """
        modifiers = {
            "melee_bonus": 0,
            "missile_bonus": 0,
            "magic_bonus": 0,
            "save_bonus": 0,
            "halve_results": False,
            "double_results": False,
            "prevent_maneuver": False,
            "terrain_bonus": 0,
        }
        
        applicable_effects = []
        
        for effect in self.active_effects:
            effect_applies = False
            target_type = effect.get("target_type", "")
            target_id = effect.get("target_identifier", "")
            affected_player = effect.get("affected_player_name", "")
            
            # Check if effect applies to the target
            if target_type == constants.EFFECT_TARGET_ARMY:
                # Effect targets a specific army
                if affected_player == target_player_name:
                    if target_army_identifier is None or target_id == target_army_identifier:
                        effect_applies = True
            elif target_type == constants.EFFECT_TARGET_TERRAIN:
                # Effect targets terrain (affects all units on that terrain)
                effect_applies = True  # Simplified - would need terrain location checking
            elif target_type == "PLAYER":
                # Effect targets the entire player
                if affected_player == target_player_name:
                    effect_applies = True
            
            if effect_applies:
                applicable_effects.append(effect)
                self._apply_effect_modifiers(effect, action_type, modifiers)
        
        if applicable_effects:
            effect_names = [e.get("description", "Unknown") for e in applicable_effects]
            print(f"EffectManager: Applied effects {effect_names} to {target_player_name} ({action_type})")
            print(f"EffectManager: Final modifiers: {modifiers}")
        
        return modifiers
    
    def _apply_effect_modifiers(self, effect: Dict[str, Any], action_type: str, modifiers: Dict[str, Any]):
        """Apply a single effect's modifiers to the modifiers dictionary."""
        description = effect.get("description", "").lower()
        
        # Parse effect description for modifiers
        if "melee" in description and action_type == "MELEE":
            if "-3" in description or "minus 3" in description:
                modifiers["melee_bonus"] -= 3
            elif "-2" in description or "minus 2" in description:
                modifiers["melee_bonus"] -= 2
            elif "-1" in description or "minus 1" in description:
                modifiers["melee_bonus"] -= 1
            elif "+3" in description or "plus 3" in description:
                modifiers["melee_bonus"] += 3
            elif "+2" in description or "plus 2" in description:
                modifiers["melee_bonus"] += 2
            elif "+1" in description or "plus 1" in description:
                modifiers["melee_bonus"] += 1
            
            if "halved" in description or "half" in description:
                modifiers["halve_results"] = True
            elif "doubled" in description or "double" in description:
                modifiers["double_results"] = True
        
        elif "missile" in description and action_type == "MISSILE":
            if "-2" in description:
                modifiers["missile_bonus"] -= 2
            elif "+2" in description:
                modifiers["missile_bonus"] += 2
        
        elif "magic" in description and action_type == "MAGIC":
            if "-1" in description:
                modifiers["magic_bonus"] -= 1
            elif "+1" in description:
                modifiers["magic_bonus"] += 1
        
        elif "save" in description and action_type == "SAVE":
            if "-1" in description:
                modifiers["save_bonus"] -= 1
            elif "+1" in description:
                modifiers["save_bonus"] += 1
            elif "halved" in description:
                modifiers["halve_results"] = True
        
        # Global effects
        if "all results halved" in description:
            modifiers["halve_results"] = True
        elif "all results doubled" in description:
            modifiers["double_results"] = True
        
        if "cannot maneuver" in description or "no maneuver" in description:
            modifiers["prevent_maneuver"] = True
