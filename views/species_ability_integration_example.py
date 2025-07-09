"""
Integration example for DUA-dependent species abilities.

This file demonstrates how to integrate the species ability dialogs
with the combat systems and game engine.
"""

from typing import Any, Dict, List, Optional

from views.species_ability_dialogs import MagicNegationDialog, FoulStenchDialog, CursedBulletsDialog


class SpeciesAbilityIntegration:
    """
    Integration class for managing DUA-dependent species abilities
    during combat actions.
    """

    def __init__(self, game_engine, main_view, dua_manager):
        self.game_engine = game_engine
        self.main_view = main_view
        self.dua_manager = dua_manager

    def check_magic_negation_opportunity(self, magic_result: Dict[str, Any]) -> bool:
        """
        Check if any opponents can use Magic Negation against a magic action.

        Returns True if Magic Negation was used, False otherwise.
        """
        caster = magic_result.get("caster", "")
        location = magic_result.get("location", "")

        # Check all other players for Frostwings at the same location
        all_players = self.game_engine.get_all_players_data()

        for player_name, player_data in all_players.items():
            if player_name == caster:
                continue  # Skip the caster

            # Check if player has Frostwings at this location
            if self._player_has_frostwings_at_location(player_name, location):
                # Check DUA for dead Frostwings
                dead_frostwings_count = self.dua_manager.get_dua_species_count(player_name, "Frostwings")

                if dead_frostwings_count > 0:
                    # Offer Magic Negation opportunity
                    if self._offer_magic_negation(player_name, magic_result, dead_frostwings_count):
                        return True  # Magic was negated

        return False  # No negation occurred

    def _player_has_frostwings_at_location(self, player_name: str, location: str) -> bool:
        """Check if a player has Frostwings units at the specified location."""
        player_data = self.game_engine.get_player_data(player_name)
        if not player_data:
            return False

        for army_name, army_data in player_data.get("armies", {}).items():
            army_location = army_data.get("location", "")
            if army_location == location:
                # Check for Frostwings in this army
                army_units = army_data.get("units", [])
                for unit in army_units:
                    if unit.get("species") == "Frostwings":
                        return True

        return False

    def _offer_magic_negation(
        self, frostwing_player: str, magic_result: Dict[str, Any], dead_frostwings_count: int
    ) -> bool:
        """Offer Magic Negation opportunity to Frostwing player."""
        caster = magic_result.get("caster", "")
        location = magic_result.get("location", "")
        magic_results = magic_result.get("magic_results", {})

        # Get Frostwing army at location
        frostwing_army = self._get_player_army_at_location(frostwing_player, location)
        if not frostwing_army:
            return False

        # Create Magic Negation dialog
        dialog = MagicNegationDialog(
            frostwing_player=frostwing_player,
            frostwing_army=frostwing_army,
            opponent_player=caster,
            opponent_magic_results=magic_results,
            dead_frostwings_count=dead_frostwings_count,
            location=location,
            parent=self.main_view,
        )

        # Handle results
        negation_used = False

        def on_negation_completed(negation_result: Dict[str, Any]):
            nonlocal negation_used
            negation_used = True
            self._apply_magic_negation(magic_result, negation_result)

        def on_negation_declined():
            nonlocal negation_used
            negation_used = False

        dialog.negation_completed.connect(on_negation_completed)
        dialog.negation_declined.connect(on_negation_declined)

        # Show dialog and wait for result
        dialog.exec()

        return negation_used

    def _apply_magic_negation(self, magic_result: Dict[str, Any], negation_result: Dict[str, Any]):
        """Apply Magic Negation effects to the magic result."""
        negation_amount = negation_result.get("magic_negation_amount", 0)

        if negation_amount > 0:
            # Reduce magic points by negation amount
            # This is simplified - real implementation would need more complex logic
            magic_points = magic_result.get("magic_points_by_element", {})

            # Distribute negation across elements proportionally
            total_magic = sum(magic_points.values())
            if total_magic > 0:
                reduction_ratio = min(1.0, negation_amount / total_magic)

                for element in magic_points:
                    original_points = magic_points[element]
                    reduced_points = int(original_points * (1 - reduction_ratio))
                    magic_points[element] = reduced_points

            # Update game state
            self.game_engine.apply_magic_negation(magic_result, negation_result)

            # Show result
            frostwing_player = negation_result.get("frostwing_player", "")
            result_text = f"❄️ {frostwing_player} used Magic Negation: {negation_amount} magic results negated!"
            self.main_view.combat_result_signal.emit(result_text)

    def check_foul_stench_opportunity(self, melee_result: Dict[str, Any]) -> List[str]:
        """
        Check if Foul Stench affects the opponent's counter-attack.

        Returns list of units that cannot counter-attack.
        """
        attacker = melee_result.get("attacker", "")
        defender = melee_result.get("defender", "")

        # Check if attacker has Goblins
        attacker_army = melee_result.get("attacker_army", {})
        has_goblins = any(unit.get("species") == "Goblins" for unit in attacker_army.get("units", []))

        if not has_goblins:
            return []

        # Check DUA for dead Goblins
        dead_goblins_count = self.dua_manager.get_dua_species_count(attacker, "Goblins")

        if dead_goblins_count == 0:
            return []

        # Apply Foul Stench
        return self._apply_foul_stench(defender, melee_result, dead_goblins_count)

    def _apply_foul_stench(
        self, opponent_player: str, melee_result: Dict[str, Any], dead_goblins_count: int
    ) -> List[str]:
        """Apply Foul Stench effect - opponent selects units that cannot counter-attack."""
        goblin_player = melee_result.get("attacker", "")
        opponent_army = melee_result.get("target_army", {})

        # Create Foul Stench dialog
        dialog = FoulStenchDialog(
            goblin_player=goblin_player,
            opponent_player=opponent_player,
            opponent_army=opponent_army,
            dead_goblins_count=dead_goblins_count,
            parent=self.main_view,
        )

        # Handle results
        affected_units = []

        def on_stench_completed(stench_result: Dict[str, Any]):
            nonlocal affected_units
            affected_units = stench_result.get("selected_units", [])

            # Update game state
            self.game_engine.apply_foul_stench(melee_result, stench_result)

            # Show result
            unit_names = ", ".join(affected_units)
            result_text = f"🤢 Foul Stench: {unit_names} cannot counter-attack (DUA: {dead_goblins_count} dead Goblins)"
            self.main_view.combat_result_signal.emit(result_text)

        dialog.stench_completed.connect(on_stench_completed)

        # Show dialog and wait for result
        dialog.exec()

        return affected_units

    def check_cursed_bullets_effect(self, missile_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if Cursed Bullets affect missile damage.

        Returns modified missile result with cursed bullet information.
        """
        attacker = missile_result.get("attacker", "")

        # Check if attacker has Lava Elves
        attacker_army = missile_result.get("attacker_army", {})
        has_lava_elves = any(unit.get("species") == "Lava Elves" for unit in attacker_army.get("units", []))

        if not has_lava_elves:
            return missile_result

        # Check DUA for dead Lava Elves
        dead_lava_elves_count = self.dua_manager.get_dua_species_count(attacker, "Lava Elves")

        if dead_lava_elves_count == 0:
            return missile_result

        # Apply Cursed Bullets effect
        return self._apply_cursed_bullets(missile_result, dead_lava_elves_count)

    def _apply_cursed_bullets(self, missile_result: Dict[str, Any], dead_lava_elves_count: int) -> Dict[str, Any]:
        """Apply Cursed Bullets effect to missile damage."""
        attacker_results = missile_result.get("attacker_results", {})

        # Count total missile results
        total_missiles = 0
        for unit_name, face_results in attacker_results.items():
            missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])
            total_missiles += missile_count

        # Determine cursed missiles (max 3 dead Lava Elves)
        cursed_missiles = min(dead_lava_elves_count, total_missiles, 3)

        if cursed_missiles > 0:
            # Add cursed bullets information to result
            missile_result["cursed_bullets"] = {
                "cursed_missile_count": cursed_missiles,
                "dead_lava_elves_count": dead_lava_elves_count,
                "total_missiles": total_missiles,
            }

            # Show Cursed Bullets information dialog
            self._show_cursed_bullets_info(missile_result, dead_lava_elves_count)

        return missile_result

    def _show_cursed_bullets_info(self, missile_result: Dict[str, Any], dead_lava_elves_count: int):
        """Show information about Cursed Bullets effect."""
        attacker = missile_result.get("attacker", "")
        attacker_results = missile_result.get("attacker_results", {})
        target_army = missile_result.get("target_army", {})

        # Create information dialog
        dialog = CursedBulletsDialog(
            lava_elf_player=attacker,
            missile_results=attacker_results,
            dead_lava_elves_count=dead_lava_elves_count,
            target_army=target_army,
            parent=self.main_view,
        )

        # Show dialog
        dialog.exec()

        # Update game state
        self.game_engine.apply_cursed_bullets(missile_result)

        # Show result
        cursed_count = missile_result.get("cursed_bullets", {}).get("cursed_missile_count", 0)
        result_text = f"💀 Cursed Bullets: {cursed_count} missile results can only be reduced by spell saves"
        self.main_view.combat_result_signal.emit(result_text)

    def _get_player_army_at_location(self, player_name: str, location: str) -> Optional[Dict[str, Any]]:
        """Get a player's army at a specific location."""
        player_data = self.game_engine.get_player_data(player_name)
        if not player_data:
            return None

        for army_name, army_data in player_data.get("armies", {}).items():
            army_location = army_data.get("location", "")
            if army_location == location:
                return army_data

        return None


# Usage example for integrating into combat systems:
"""
To integrate these species abilities into your combat dialogs:

1. **In MagicActionDialog**: Check for Magic Negation before completing
```python
class MagicActionDialog(QDialog):
    def __init__(self, ...):
        # ... existing initialization ...
        self.species_abilities = SpeciesAbilityIntegration(game_engine, main_view, dua_manager)
    
    def _complete_magic_action(self):
        magic_result = self._build_magic_result()
        
        # Check for Magic Negation
        if self.species_abilities.check_magic_negation_opportunity(magic_result):
            # Magic was negated, update results accordingly
            pass
        
        self.magic_completed.emit(magic_result)
        self.accept()
```

2. **In MeleeCombatDialog**: Check for Foul Stench before counter-attack
```python
class MeleeCombatDialog(QDialog):
    def _handle_counter_attack(self, melee_result):
        # Check for Foul Stench
        affected_units = self.species_abilities.check_foul_stench_opportunity(melee_result)
        
        if affected_units:
            # Remove affected units from counter-attack
            self._exclude_units_from_counter_attack(affected_units)
        
        # Proceed with counter-attack
        self._show_counter_attack_step()
```

3. **In MissileCombatDialog**: Apply Cursed Bullets to damage calculation
```python
class MissileCombatDialog(QDialog):
    def _calculate_final_damage(self):
        missile_result = self._build_missile_result()
        
        # Apply Cursed Bullets effect
        missile_result = self.species_abilities.check_cursed_bullets_effect(missile_result)
        
        # Use modified result for damage calculation
        self._apply_missile_damage(missile_result)
```

4. **Enhanced Bone Magic**: Already integrated in SAI processor
The Bone Magic ability is automatically handled by the SAI processor when a DUA manager is provided.

This integration provides:
- Interactive species ability dialogs with proper DUA dependency
- Automatic checking for ability opportunities during combat
- Visual feedback for players about ability effects
- Proper game state integration with DUA tracking
- Support for all four DUA-dependent abilities
"""
