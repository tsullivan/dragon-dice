"""
Example integration showing how to use the DamageAllocationDialog with combat systems.

This file demonstrates how to integrate damage allocation with melee, missile,
and magic combat results, handling various damage types and special rules.
"""

from typing import Any, Dict, List, Tuple

from views.damage_allocation_dialog import DamageAllocationDialog, MultiArmyDamageDialog


class DamageIntegrationExample:
    """
    Example class showing how to integrate damage allocation dialogs
    with combat results from melee, missile, and magic systems.
    """

    def __init__(self, game_engine, main_view):
        self.game_engine = game_engine
        self.main_view = main_view

    def handle_melee_damage(self, melee_result: Dict[str, Any]):
        """Handle damage allocation from melee combat results."""
        final_damage = melee_result.get("final_damage", 0)

        if final_damage <= 0:
            print("No damage to allocate from melee combat")
            return

        # Get target army information
        target_army = melee_result.get("target_army", {})
        target_army_name = target_army.get("name", "Unknown Army")

        # Create damage allocation dialog
        dialog = DamageAllocationDialog(
            army_name=target_army_name,
            army_data=target_army,
            damage_amount=final_damage,
            damage_type="melee",
            damage_source="melee_combat",
            allow_saves=True,  # Melee damage allows saves
            parent=self.main_view,
        )

        # Connect signals
        dialog.damage_allocated.connect(self._handle_damage_allocated)
        dialog.damage_cancelled.connect(self._handle_damage_cancelled)

        # Show dialog
        dialog.exec()

    def handle_missile_damage(self, missile_result: Dict[str, Any]):
        """Handle damage allocation from missile combat results."""
        final_damage = missile_result.get("final_damage", 0)

        if final_damage <= 0:
            print("No damage to allocate from missile combat")
            return

        # Get target army information
        target_army = missile_result.get("target_army", {})
        target_army_name = target_army.get("name", "Unknown Army")

        # Create damage allocation dialog
        dialog = DamageAllocationDialog(
            army_name=target_army_name,
            army_data=target_army,
            damage_amount=final_damage,
            damage_type="missile",
            damage_source="missile_combat",
            allow_saves=True,  # Missile damage allows saves
            parent=self.main_view,
        )

        # Connect signals
        dialog.damage_allocated.connect(self._handle_damage_allocated)
        dialog.damage_cancelled.connect(self._handle_damage_cancelled)

        # Show dialog
        dialog.exec()

        # Handle defensive volley damage if present
        defensive_volley_damage = missile_result.get("defensive_volley_damage", 0)
        if defensive_volley_damage > 0:
            self._handle_defensive_volley_damage(missile_result, defensive_volley_damage)

    def handle_spell_damage(self, spell_result: Dict[str, Any], spell_name: str):
        """Handle damage allocation from spell effects."""
        # Different spells have different damage rules
        damage_rules = self._get_spell_damage_rules(spell_name)

        if damage_rules["damage_amount"] <= 0:
            print(f"No damage to allocate from spell {spell_name}")
            return

        # Check if spell affects multiple armies
        if damage_rules["multi_target"]:
            self._handle_multi_army_spell_damage(spell_result, damage_rules)
        else:
            self._handle_single_army_spell_damage(spell_result, damage_rules)

    def handle_dragon_attack_damage(self, dragon_result: Dict[str, Any]):
        """Handle damage allocation from dragon attacks."""
        damage_amount = dragon_result.get("damage", 0)

        if damage_amount <= 0:
            print("No damage to allocate from dragon attack")
            return

        # Dragon attacks typically affect multiple armies
        affected_armies = dragon_result.get("affected_armies", [])

        if len(affected_armies) > 1:
            # Multi-army damage
            dialog = MultiArmyDamageDialog(
                affected_armies=affected_armies,
                damage_amount=damage_amount,
                damage_type="dragon_attack",
                damage_source="dragon",
                allow_saves=True,
                parent=self.main_view,
            )

            dialog.all_damage_allocated.connect(self._handle_multi_army_damage_allocated)
            dialog.damage_cancelled.connect(self._handle_damage_cancelled)

            dialog.exec()
        else:
            # Single army damage
            army_name, army_data = affected_armies[0]
            dialog = DamageAllocationDialog(
                army_name=army_name,
                army_data=army_data,
                damage_amount=damage_amount,
                damage_type="dragon_attack",
                damage_source="dragon",
                allow_saves=True,
                parent=self.main_view,
            )

            dialog.damage_allocated.connect(self._handle_damage_allocated)
            dialog.damage_cancelled.connect(self._handle_damage_cancelled)

            dialog.exec()

    def _handle_defensive_volley_damage(self, missile_result: Dict[str, Any], damage: int):
        """Handle damage allocation from Coral Elf Defensive Volley."""
        # Defensive volley damage goes to the original attacker
        attacker_army = missile_result.get("attacker_army", {})
        attacker_army_name = attacker_army.get("name", "Unknown Army")

        dialog = DamageAllocationDialog(
            army_name=attacker_army_name,
            army_data=attacker_army,
            damage_amount=damage,
            damage_type="defensive_volley",
            damage_source="coral_elf_ability",
            allow_saves=True,
            parent=self.main_view,
        )

        dialog.damage_allocated.connect(self._handle_damage_allocated)
        dialog.damage_cancelled.connect(self._handle_damage_cancelled)

        dialog.exec()

    def _handle_single_army_spell_damage(self, spell_result: Dict[str, Any], damage_rules: Dict[str, Any]):
        """Handle damage allocation from single-target spells."""
        target_army = spell_result.get("target_army", {})
        target_army_name = target_army.get("name", "Unknown Army")

        dialog = DamageAllocationDialog(
            army_name=target_army_name,
            army_data=target_army,
            damage_amount=damage_rules["damage_amount"],
            damage_type=damage_rules["damage_type"],
            damage_source=f"spell_{damage_rules['spell_name']}",
            allow_saves=damage_rules["allow_saves"],
            parent=self.main_view,
        )

        dialog.damage_allocated.connect(self._handle_damage_allocated)
        dialog.damage_cancelled.connect(self._handle_damage_cancelled)

        dialog.exec()

    def _handle_multi_army_spell_damage(self, spell_result: Dict[str, Any], damage_rules: Dict[str, Any]):
        """Handle damage allocation from multi-target spells."""
        affected_armies = spell_result.get("affected_armies", [])

        dialog = MultiArmyDamageDialog(
            affected_armies=affected_armies,
            damage_amount=damage_rules["damage_amount"],
            damage_type=damage_rules["damage_type"],
            damage_source=f"spell_{damage_rules['spell_name']}",
            allow_saves=damage_rules["allow_saves"],
            parent=self.main_view,
        )

        dialog.all_damage_allocated.connect(self._handle_multi_army_damage_allocated)
        dialog.damage_cancelled.connect(self._handle_damage_cancelled)

        dialog.exec()

    def _get_spell_damage_rules(self, spell_name: str) -> Dict[str, Any]:
        """Get damage rules for specific spells."""
        spell_damage_rules = {
            # Direct damage spells
            "Hailstorm": {
                "damage_amount": 1,
                "damage_type": "spell_direct",
                "allow_saves": True,
                "multi_target": False,
                "spell_name": "Hailstorm",
            },
            "Lightning Strike": {
                "damage_amount": 1,
                "damage_type": "spell_direct",
                "allow_saves": True,  # Unit makes save roll, if no save result = killed
                "multi_target": False,
                "spell_name": "Lightning Strike",
            },
            "Finger of Death": {
                "damage_amount": 1,
                "damage_type": "spell_no_save",
                "allow_saves": False,  # "no save possible"
                "multi_target": False,
                "spell_name": "Finger of Death",
            },
            "Firebolt": {
                "damage_amount": 1,
                "damage_type": "spell_direct",
                "allow_saves": True,
                "multi_target": False,
                "spell_name": "Firebolt",
            },
            "Firestorm": {
                "damage_amount": 2,
                "damage_type": "spell_area",
                "allow_saves": True,
                "multi_target": True,  # Affects all armies at terrain
                "spell_name": "Firestorm",
            },
            # Add more spells as needed
        }

        return spell_damage_rules.get(
            spell_name,
            {
                "damage_amount": 0,
                "damage_type": "spell_direct",
                "allow_saves": True,
                "multi_target": False,
                "spell_name": spell_name,
            },
        )

    def _handle_damage_allocated(self, result: Dict[str, Any]):
        """Handle completed damage allocation for single army."""
        print(f"Damage allocated to {result['army_name']}")

        # Extract key information
        army_name = result["army_name"]
        killed_units = result["killed_units"]
        surviving_units = result["surviving_units"]
        damage_amount = result["damage_amount"]
        damage_type = result["damage_type"]

        # Apply damage to game state
        success = self.game_engine.apply_damage_allocation(result)
        if not success:
            print(f"Failed to apply damage allocation to {army_name}")
            return

        # Create result summary
        result_text = f"💥 {damage_amount} {damage_type} damage dealt to {army_name}"

        if killed_units:
            killed_names = [unit["unit_name"] for unit in killed_units]
            result_text += f"\\n💀 Units killed: {', '.join(killed_names)}"

        if surviving_units:
            # Show units with reduced health
            damaged_survivors = [unit for unit in surviving_units if unit["damage_taken"] > 0]
            if damaged_survivors:
                survivor_info = []
                for unit in damaged_survivors:
                    survivor_info.append(
                        f"{unit['unit_name']} ({unit['remaining_health']}/{unit['unit_data']['health']})"
                    )
                result_text += f"\\n🩹 Units damaged: {', '.join(survivor_info)}"

        # Check for army elimination
        if not surviving_units:
            result_text += f"\\n💀 {army_name} eliminated!"
            self.game_engine.handle_army_elimination(army_name)

        # Update game state display
        self.main_view.combat_result_signal.emit(result_text)
        self.game_engine.game_state_updated.emit()

        # Continue game flow
        self.game_engine.continue_after_damage_allocation()

    def _handle_multi_army_damage_allocated(self, results: List[Dict[str, Any]]):
        """Handle completed damage allocation for multiple armies."""
        print(f"Multi-army damage allocated to {len(results)} armies")

        # Apply all damage allocations
        for result in results:
            success = self.game_engine.apply_damage_allocation(result)
            if not success:
                print(f"Failed to apply damage allocation to {result['army_name']}")

        # Create summary
        total_killed = sum(len(result["killed_units"]) for result in results)
        affected_armies = [result["army_name"] for result in results]

        result_text = f"💥 Multi-army damage dealt to: {', '.join(affected_armies)}"
        if total_killed > 0:
            result_text += f"\\n💀 Total units killed: {total_killed}"

        # Check for army eliminations
        eliminated_armies = []
        for result in results:
            if not result["surviving_units"]:
                eliminated_armies.append(result["army_name"])
                self.game_engine.handle_army_elimination(result["army_name"])

        if eliminated_armies:
            result_text += f"\\n💀 Armies eliminated: {', '.join(eliminated_armies)}"

        # Update game state display
        self.main_view.combat_result_signal.emit(result_text)
        self.game_engine.game_state_updated.emit()

        # Continue game flow
        self.game_engine.continue_after_damage_allocation()

    def _handle_damage_cancelled(self):
        """Handle cancelled damage allocation."""
        print("Damage allocation cancelled")

        # Return to previous state or allow retry
        self.game_engine.handle_damage_allocation_cancelled()


# Usage example for integrating into combat systems:
"""
To integrate this damage allocation system into your combat dialogs:

1. **In MeleeCombatDialog**: After calculating final damage, call damage allocation
```python
def _complete_melee_combat(self):
    # ... existing melee calculation ...
    
    if final_damage > 0:
        # Show damage allocation dialog
        damage_integration = DamageIntegrationExample(self.game_engine, self.main_view)
        damage_integration.handle_melee_damage(melee_result)
    else:
        # No damage, continue normally
        self.combat_completed.emit(melee_result)
```

2. **In MissileCombatDialog**: Handle both primary and defensive volley damage
```python
def _complete_missile_combat(self):
    # ... existing missile calculation ...
    
    if final_damage > 0:
        damage_integration = DamageIntegrationExample(self.game_engine, self.main_view)
        damage_integration.handle_missile_damage(missile_result)
    else:
        self.combat_completed.emit(missile_result)
```

3. **In MagicActionDialog**: Handle spell damage based on spell effects
```python
def _complete_magic_action(self):
    # ... existing magic calculation ...
    
    damage_integration = DamageIntegrationExample(self.game_engine, self.main_view)
    
    for spell, cost, element in self.cast_spells:
        if self._spell_causes_damage(spell):
            damage_integration.handle_spell_damage(magic_result, spell.name)
```

4. **In MainGameplayView**: Handle dragon attacks and other area effects
```python
def handle_dragon_attack(self, dragon_result):
    damage_integration = DamageIntegrationExample(self.game_engine, self)
    damage_integration.handle_dragon_attack_damage(dragon_result)
```

This integration provides:
- Interactive damage allocation with visual feedback
- Support for different damage types (melee, missile, spell, dragon)
- Handling of special rules (no saves, area effects, etc.)
- Unit health tracking and DUA placement
- Comprehensive result reporting
- Proper game state integration
"""
