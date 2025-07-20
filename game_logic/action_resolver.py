from typing import Optional, List, Dict, Any

from PySide6.QtCore import QObject, Signal

from .effect_manager import EffectManager
from .spell_resolver import SpellResolver
from utils.field_access import strict_get, strict_get_with_fallback, strict_get_optional
from models.spell_model import get_available_spells

# Forward declaration for type hinting if GameStateManager and EffectManager are in different files
# and create circular dependencies. Or import them directly if no circular dependency.
from .game_state_manager import GameStateManager


class ActionResolver(QObject):
    """Resolves game actions like melee, missile, magic, and maneuvers."""

    action_resolved = Signal(dict)  # Emits a dictionary with action results/outcomes
    # Example: {"type": "melee", "damage_done": 5, "effects_triggered": [...]}
    next_action_step_determined = Signal(str)  # Emits the next action_step constant

    def __init__(
        self,
        game_state_manager: GameStateManager,
        effect_manager: EffectManager,
        minor_terrain_manager=None,
        spell_resolver: Optional[SpellResolver] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.effect_manager = effect_manager
        self.minor_terrain_manager = minor_terrain_manager
        self.spell_resolver = spell_resolver

        # Store context for determining target armies
        self._current_combat_location = None
        self._current_attacking_army = None
        self._current_defending_army = None

    def set_combat_context(
        self,
        location: str,
        attacking_army_id: str,
        defending_army_id: str,
    ):
        """Set the context for combat to determine specific armies being involved."""
        if not location:
            raise ValueError("Combat location is required (empty string provided)")
        if not attacking_army_id:
            raise ValueError("Attacking army ID is required (empty string provided)")
        if not defending_army_id:
            raise ValueError("Defending army ID is required (empty string provided)")

        self._current_combat_location = location
        self._current_attacking_army = attacking_army_id
        self._current_defending_army = defending_army_id

    def determine_defending_army_identifier(self, defending_player_name: str, combat_location: str) -> str:
        """
        Determine the specific army identifier for the defending player.
        Returns a specific army identifier instead of the placeholder.
        """
        # If we have explicit defending army context, use it
        if self._current_defending_army:
            return self._current_defending_army

        # If we have a combat location, find armies at that location
        if combat_location or self._current_combat_location:
            location = combat_location or self._current_combat_location
            armies_at_location = self.game_state_manager.get_all_armies_at_location(
                defending_player_name, location or ""
            )

            if len(armies_at_location) == 1:
                # Only one army at location, that's the target
                army_data = armies_at_location[0]
                army_type = strict_get(army_data, "army_type", "Army")
                return strict_get_optional(army_data, "unique_id", f"{defending_player_name}_{army_type}")  # type: ignore[no-any-return]
            if len(armies_at_location) > 1:
                # Multiple armies - prioritize by type (home > campaign > horde)
                priority_order = ["home", "campaign", "horde"]
                for army_type in priority_order:
                    for army_data in armies_at_location:
                        if army_data["army_type"] == army_type:
                            return strict_get_optional(army_data, "unique_id", f"{defending_player_name}_{army_type}")  # type: ignore[no-any-return]

        # Fallback to active army
        active_army_type = self.game_state_manager.get_active_army_type(defending_player_name)
        if active_army_type:
            return self.game_state_manager.generate_army_identifier(defending_player_name, active_army_type)

        # Final fallback to home army
        return self.game_state_manager.generate_army_identifier(defending_player_name, "home")

    def determine_attacking_army_identifier(self, attacking_player_name: str, combat_location: str) -> str:
        """
        Determine the specific army identifier for the attacking player.
        """
        # If we have explicit attacking army context, use it
        if self._current_attacking_army:
            return self._current_attacking_army

        # Use same logic as defending army determination
        return self.determine_defending_army_identifier(attacking_player_name, combat_location)

    # This method might be too generic; specific methods per action type are better.
    def resolve_melee_attack(
        self,
        attacking_player_name: str,
        defending_player_name: str,
        attacker_roll_results_str: str,
    ):
        """Resolves a complete melee attack sequence, including saves and counter-attacks."""
        print(f"ActionResolver: Resolving melee attack between {attacking_player_name} and {defending_player_name}.")
        print(f"ActionResolver: Attacker roll results: {attacker_roll_results_str}")

        # Step 1: Parse attacker's dice results
        parsed_attacker_dice = self.parse_dice_string(attacker_roll_results_str, "MELEE")
        if not parsed_attacker_dice:
            print("ActionResolver: No valid dice results to process.")
            self.action_resolved.emit({"type": "melee", "outcome": "no_results"})
            return

        # Step 2: Process attacker's roll
        attacker_outcome = self.process_attacker_melee_roll(attacking_player_name, parsed_attacker_dice)

        # Step 3: Check if there are hits to defend against
        if attacker_outcome.get("hits", 0) <= 0:
            print("ActionResolver: No hits from attacker, ending melee action.")
            self.action_resolved.emit(
                {
                    "type": "melee",
                    "outcome": "no_hits",
                    "attacker_hits": 0,
                    "damage_dealt": 0,
                }
            )
            self.next_action_step_determined.emit("")  # End action
            return

        # Step 4: Emit signal for defender to roll saves
        print(f"ActionResolver: Attacker scored {attacker_outcome['hits']} hits. Awaiting defender's save roll.")
        # Store the attacker outcome for when defender responds
        self._pending_attacker_outcome = attacker_outcome
        self._pending_defending_player = defending_player_name

        # Emit action resolved with intermediate results
        self.action_resolved.emit(
            {
                "type": "melee_attacker_complete",
                "attacker": attacking_player_name,
                "defender": defending_player_name,
                "hits": attacker_outcome["hits"],
                "sais_for_defender": attacker_outcome.get("sais_for_defender", []),
            }
        )

    def process_attacker_melee_roll(self, attacking_player_name: str, parsed_dice_results: list) -> dict:
        """
        Processes the attacker's melee roll.
        Queries game state for attacker's units, abilities, and active effects.
        Calculates hits, damage, and any SAIs that affect the defender.
        Returns a dictionary with results, e.g., {"hits": N, "sais_for_defender": [...]}
        """
        print(f"ActionResolver: Processing attacker melee roll for {attacking_player_name} with {parsed_dice_results}")

        attacking_units = self.game_state_manager.get_active_army_units(attacking_player_name)
        if not attacking_units:
            print(
                f"ActionResolver: No active units found for attacker {attacking_player_name}. Aborting melee roll processing."
            )
            # self.next_action_step_determined.emit("SELECT_ACTION") # Or some error state
            return {"hits": 0, "sais_for_defender": []}  # Early exit

        print(f"ActionResolver: Attacking units: {[strict_get(unit, 'name', 'Unit') for unit in attacking_units]}")

        calculated_results = {
            "hits": 0,
            "sais_for_defender": [],
            "original_icons": parsed_dice_results,
        }

        # --- Stage 1: Initial Icon Tally & ID Conversion ---
        # Create a mutable copy of parsed_dice_results to track used ID icons
        remaining_icons = [icon.copy() for icon in parsed_dice_results]

        id_icons_to_convert = 0
        for icon_data in remaining_icons:  # Iterate over the copy
            if strict_get(icon_data, "type", "IconData") == "ID":
                id_icons_to_convert += strict_get(icon_data, "count", "IconData")
            elif strict_get(icon_data, "type", "IconData") == "Melee":
                calculated_results["hits"] += strict_get(icon_data, "count", "IconData")
            # TODO: Handle SAIs that modify attacker's roll (e.g., Doubler) here or in a dedicated step

        # Convert ID icons based on unit abilities
        converted_id_hits = 0
        units_that_used_id = set()  # To ensure a unit's ID is used only once per roll
        for _ in range(id_icons_to_convert):
            for unit in attacking_units:
                unit_id = strict_get_with_fallback(unit, "id", "name", "Unit")
                if unit_id not in units_that_used_id:
                    # For now, use a default ID ability since we don't have die_faces data
                    # This would normally come from unit definitions from the unit roster

                    # Default ID conversion (placeholder logic until die_faces are implemented)
                    default_id_melee = 1  # Most units convert 1 ID to 1 melee
                    converted_id_hits += default_id_melee
                    units_that_used_id.add(unit_id)
                    print(
                        f"ActionResolver: Unit {strict_get(unit, 'name', 'Unit')} used ID for {default_id_melee} melee."
                    )
                    break  # Move to the next ID icon to be converted
        calculated_results["hits"] += converted_id_hits

        # --- Stage 2: Apply SAIs that modify results (e.g., Doubler) ---
        # TODO: 4. Apply SAIs from parsed_dice_results that modify the attacker's roll (e.g., Doubler). (This was TODO #3 before ID conversion)
        # Example:
        for icon_data in remaining_icons:
            if (
                strict_get(icon_data, "type", "IconData") == "SAI"
                and strict_get(icon_data, "name", "IconData") == "Doubler"
            ):
                print(f"ActionResolver: Applying Doubler. Current hits: {calculated_results['hits']}")
                calculated_results["hits"] *= 2  # Assuming one Doubler for now
                # TODO: Handle multiple doublers/triplers (usually best one applies)
                break  # Typically only one such SAI is effective

        # --- Stage 3: Apply Modifiers from Active Effects ---
        # Get relevant active effects from self.effect_manager for the attacker/attacking army.
        # For now, assume target_army_identifier can be derived or is not strictly needed for attacker's own buffs/debuffs.
        active_mods = self.effect_manager.get_active_modifiers(attacking_player_name, None, "MELEE")
        calculated_results["hits"] += active_mods.get("melee_bonus", 0)
        if active_mods.get("halve_results"):
            calculated_results["hits"] = calculated_results["hits"] // 2  # Integer division

        # TODO: 5. Apply modifiers from active effects. (Partially done above, may need more complex logic)
        # TODO: 6. Calculate total melee hits/damage. (This is partially done, needs to incorporate SAIs/modifiers)

        # --- Stage 4: Identify SAIs affecting defender's save roll ---
        for icon_data in remaining_icons:
            if icon_data.get("type") == "SAI" and icon_data.get("name") == "Bullseye":
                calculated_results["sais_for_defender"].append("Bullseye")
                print("ActionResolver: Bullseye identified for defender's save.")
        # TODO: 7. Identify SAIs that will affect the defender's save roll.

        # After processing, determine the next step
        self.next_action_step_determined.emit("AWAITING_DEFENDER_SAVES")
        return calculated_results

    def process_defender_save_roll(
        self, defending_player_name: str, parsed_save_dice: list, attacker_outcome: dict
    ) -> dict:
        """
        Processes the defender's save roll.
        Queries game state for defender's units, abilities, and active effects.
        Applies attacker's SAIs (e.g., Bullseye).
        Calculates successful saves and final damage.
        Returns a dictionary with results, e.g., {"damage_taken": N, "counter_attack_possible": False}
        """
        print(
            f"ActionResolver: Processing defender save roll for {defending_player_name} with {parsed_save_dice}. Attacker outcome: {attacker_outcome}"
        )

        defending_units = self.game_state_manager.get_active_army_units(defending_player_name)
        if not defending_units:
            print(f"ActionResolver: No active units found for defender {defending_player_name}.")
            # If no defending units, all hits from attacker likely apply directly.
            # This needs careful consideration based on rules (e.g., if army was wiped out by a previous effect).
            final_damage = attacker_outcome.get("hits", 0)
            # TODO: Instruct GameStateManager to record this damage if applicable (e.g. vs terrain if no units)
            self.next_action_step_determined.emit("")  # End of action, advance phase
            return {
                "damage_taken": final_damage,
                "saves_made": 0,
                "counter_attack_possible": False,
            }

        print(f"ActionResolver: Defending units: {[strict_get(unit, 'name', 'Unit') for unit in defending_units]}")

        successful_saves = 0
        sais_from_attacker = attacker_outcome.get("sais_for_defender", [])
        attacker_hits = attacker_outcome.get("hits", 0)

        # Apply SAIs from attacker that affect saves
        bullseye_active = "Bullseye" in sais_from_attacker
        if bullseye_active:
            print("ActionResolver: Attacker Bullseye is active, preventing ID conversion to saves.")

        # Handle other save-affecting SAIs from attacker
        piercing_active = "PIERCING" in sais_from_attacker  # Placeholder SAI
        if piercing_active:
            print("ActionResolver: Attacker Piercing SAI reduces defender's saves.")

        # Convert ID icons to save results based on defending unit abilities
        converted_id_saves = 0
        units_that_used_id = set()  # To ensure a unit's ID is used only once per roll
        id_icons_to_convert = sum(
            strict_get(item, "count", "SaveDice")
            for item in parsed_save_dice
            if strict_get(item, "type", "SaveDice") == "ID"
        )

        for _ in range(id_icons_to_convert):
            # If Bullseye is active, ID icons might not convert to saves (rule dependent)
            if bullseye_active:
                print("ActionResolver: Bullseye prevents ID conversion to saves.")
                break  # Skip ID conversion if Bullseye active (simplified rule)

            for unit in defending_units:
                unit_id = strict_get_with_fallback(unit, "id", "name", "Unit")
                if unit_id not in units_that_used_id:
                    # Default ID conversion (placeholder logic until die_faces are implemented)
                    default_id_saves = 1  # Most units convert 1 ID to 1 save
                    converted_id_saves += default_id_saves
                    units_that_used_id.add(unit_id)
                    print(
                        f"ActionResolver: Unit {strict_get(unit, 'name', 'Unit')} used ID for {default_id_saves} save."
                    )
                    break  # Move to the next ID icon to be converted
        successful_saves += converted_id_saves

        # Apply SAIs from save dice that generate additional saves
        for icon_data in parsed_save_dice:
            if strict_get(icon_data, "type", "IconData") == "SAI":
                sai_type = strict_get(icon_data, "sai_type", "IconData")
                count = strict_get_optional(icon_data, "count", 1)
                # Handle save-generating SAIs
                if sai_type == "SHIELD":  # Placeholder SAI name
                    successful_saves += count
                    print(f"ActionResolver: SAI Shield generated {count} additional saves")
                # Add other save-generating SAIs here

        # Apply active effects for defender (already done above with effect_manager)
        # For now, assume target_army_identifier can be derived or is not strictly needed for defender's own buffs/debuffs.
        active_mods = self.effect_manager.get_active_modifiers(defending_player_name, None, "SAVE")
        successful_saves += active_mods.get("save_bonus", 0)
        if active_mods.get("halve_results"):  # Effects can halve saves too
            successful_saves = successful_saves // 2
        if active_mods.get("double_results"):  # Effects can double saves
            successful_saves = successful_saves * 2

        # Placeholder for direct save icons
        for item in parsed_save_dice:
            if strict_get(item, "type", "SaveDice") == "Save":
                successful_saves += strict_get(item, "count", "SaveDice")

        # Apply minor terrain effects to save results
        if self.minor_terrain_manager:
            defending_army_location = self.game_state_manager.get_army_location(defending_player_name)
            if defending_army_location:
                save_results = {"save_results": successful_saves, "id_results": converted_id_saves}
                modified_results = self.apply_minor_terrain_effects(
                    defending_player_name, defending_army_location, save_results, "SAVE"
                )
                successful_saves = modified_results.get("save_results", successful_saves)
                # Also apply ID doubling effect if present
                if "id_results" in modified_results and modified_results["id_results"] != converted_id_saves:
                    id_bonus = modified_results["id_results"] - converted_id_saves
                    successful_saves += id_bonus

        # --- Calculate final damage ---
        final_damage = max(0, attacker_hits - successful_saves)
        print(
            f"ActionResolver: Attacker Hits: {attacker_hits}, Successful Saves: {successful_saves}, Final Damage: {final_damage}"
        )

        # --- Apply Damage ---
        # Apply damage to the defending army using specific army identifier
        if final_damage > 0:
            if self._current_combat_location is None:
                raise ValueError("Current combat location cannot be None")
            defending_army_id = self.determine_defending_army_identifier(
                defending_player_name, self._current_combat_location
            )  # type: ignore[arg-type]
            self.game_state_manager.apply_damage_to_units(defending_player_name, defending_army_id, final_damage)
            print(f"ActionResolver: Applied {final_damage} damage to {defending_player_name}'s army")

        # Determine if a counter-attack is possible
        # Rules: Counter-attack possible if defender has surviving melee units and rolled melee icons
        counter_attack_possible = False
        if final_damage < attacker_hits:  # Some damage was saved
            # Check if defender has melee icons in their save roll
            defender_melee_icons = sum(item.get("count", 0) for item in parsed_save_dice if item.get("type") == "Melee")
            # Check if defender still has units capable of counter-attacking
            surviving_units = [unit for unit in defending_units if unit.get("health", 0) > 0]

            if defender_melee_icons > 0 and surviving_units:
                counter_attack_possible = True
                print(
                    f"ActionResolver: Counter-attack possible! {defender_melee_icons} melee icons, {len(surviving_units)} surviving units"
                )

        if counter_attack_possible:
            self.next_action_step_determined.emit("AWAITING_MELEE_COUNTER_ATTACK_ROLL")  # Placeholder constant
        else:
            self.next_action_step_determined.emit("")  # Empty string signifies end of this action, advance phase/march
        return {
            "damage_taken": final_damage,
            "saves_made": successful_saves,
            "counter_attack_possible": counter_attack_possible,
        }

    def parse_dice_string(self, dice_string: str, roll_type: str) -> list:
        """
        Robust parser for dice result strings like '3 melee, 1 sai:bullseye, 2 id'.

        Supported formats:
        - Numbers + icon names: "3 melee", "2 missile", "1 magic"
        - SAIs with types: "1 sai:bullseye", "2 sai:doubler"
        - Short forms: "3m", "2mi", "1s:bullseye"
        - Multiple results: "3 melee, 1 sai:bullseye, 2 id"

        Returns: List of dicts with 'type', 'count', and optional 'sai_type' keys
        """
        import re

        print(f"ActionResolver: Parsing '{dice_string}' for roll type '{roll_type}'")

        parsed_list: List[Dict[str, Any]] = []
        if not dice_string or not isinstance(dice_string, str):
            return parsed_list

        # Icon name mappings (full names and abbreviations)
        icon_mappings = {
            # Full names
            "melee": "Melee",
            "missile": "Missile",
            "magic": "Magic",
            "save": "Save",
            "id": "ID",
            "sai": "SAI",
            "maneuver": "Maneuver",
            # Common abbreviations
            "m": "Melee",
            "mel": "Melee",
            "mi": "Missile",
            "mis": "Missile",
            "mag": "Magic",
            "sv": "Save",
            "s": "SAI",  # When not followed by 'ai'
            "man": "Maneuver",
            # Dragon-specific icons
            "claw": "Claw",
            "bite": "Jaws",
            "tail": "Tail",
            "breath": "Firebreath",
        }

        # Valid SAI types
        valid_sais = {
            "bullseye": "Bullseye",
            "doubler": "Doubler",
            "tripler": "Tripler",
            "recruit": "Recruit",
            "magic_bolt": "Magic Bolt",
        }

        # Split on commas and process each part
        parts = [part.strip() for part in dice_string.lower().split(",")]

        for part in parts:
            if not part:
                continue

            try:
                # Pattern: number + space + icon_name (optionally with :sai_type)
                # Examples: "3 melee", "1 sai:bullseye", "2m", "1s:doubler"
                match = re.match(r"^(\d+)\s*([a-z_]+)(?::([a-z_]+))?$", part)

                if match:
                    count = int(match.group(1))
                    icon_name = match.group(2)
                    sai_type = match.group(3)

                    # Map icon name to constant
                    icon_type = icon_mappings.get(icon_name)
                    if not icon_type:
                        print(f"ActionResolver: Warning - Unknown icon type '{icon_name}' in '{part}'")
                        continue

                    result_dict = {"type": icon_type, "count": count}

                    # Handle SAI-specific processing
                    if icon_type == "SAI" and sai_type:
                        sai_constant = valid_sais.get(sai_type)
                        if sai_constant:
                            result_dict["sai_type"] = sai_constant
                        else:
                            print(f"ActionResolver: Warning - Unknown SAI type '{sai_type}' in '{part}'")
                            continue

                    parsed_list.append(result_dict)

                else:
                    # Try pattern without number (assumes count of 1)
                    # Examples: "melee", "sai:bullseye", "id"
                    sai_match = re.match(r"^([a-z_]+)(?::([a-z_]+))?$", part)
                    if sai_match:
                        icon_name = sai_match.group(1)
                        sai_type = sai_match.group(2)

                        icon_type = icon_mappings.get(icon_name)
                        if not icon_type:
                            print(f"ActionResolver: Warning - Unknown icon type '{icon_name}' in '{part}'")
                            continue

                        result_dict = {"type": icon_type, "count": 1}

                        if icon_type == "SAI" and sai_type:
                            sai_constant = valid_sais.get(sai_type)
                            if sai_constant:
                                result_dict["sai_type"] = sai_constant
                            else:
                                print(f"ActionResolver: Warning - Unknown SAI type '{sai_type}' in '{part}'")
                                continue

                        parsed_list.append(result_dict)
                    else:
                        print(f"ActionResolver: Warning - Could not parse dice part '{part}'")

            except (ValueError, AttributeError) as e:
                print(f"ActionResolver: Error parsing dice part '{part}': {e}")
                continue

        print(f"ActionResolver: Parsed dice string into {len(parsed_list)} results: {parsed_list}")
        return parsed_list

    def resolve_defender_save_response(self, defending_player_name: str, save_roll_results_str: str):
        """Processes the defender's save roll response and completes the melee attack."""
        if not hasattr(self, "_pending_attacker_outcome"):
            print("ActionResolver: No pending attacker outcome to resolve against.")
            return

        print(f"ActionResolver: Processing defender save response: {save_roll_results_str}")

        # Parse defender's save dice
        parsed_save_dice = self.parse_dice_string(save_roll_results_str, "SAVE")

        # Process the save roll against the pending attacker outcome
        save_outcome = self.process_defender_save_roll(
            defending_player_name, parsed_save_dice, self._pending_attacker_outcome
        )

        # Emit final action resolution
        self.action_resolved.emit(
            {
                "type": "melee_complete",
                "attacker_hits": self._pending_attacker_outcome.get("hits", 0),
                "defender_saves": save_outcome.get("saves_made", 0),
                "damage_dealt": save_outcome.get("damage_taken", 0),
                "counter_attack_possible": save_outcome.get("counter_attack_possible", False),
            }
        )

        # Clean up pending state
        delattr(self, "_pending_attacker_outcome")
        delattr(self, "_pending_defending_player")

    def resolve_attacker_melee(self, dice_results_str: str, attacking_player_name: str | None = None) -> dict:
        """
        Resolve attacker melee dice results and return outcome.

        Args:
            dice_results_str: String representation of dice results
            attacking_player_name: Name of attacking player (for minor terrain effects)

        Returns:
            Dict with 'hits', 'damage', and other result information
        """
        parsed_dice = self.parse_dice_string(dice_results_str, "MELEE")

        hits = 0
        damage = 0
        effects = []
        id_results = 0

        for die_result in parsed_dice:
            if die_result.get("type") == "Melee":
                hits += die_result.get("count", 0)
                damage += die_result.get("count", 0)  # Each melee hit does 1 damage
            elif die_result.get("type") == "ID":
                id_results += die_result.get("count", 0)
            elif die_result.get("type") == "SAI":
                effects.append(
                    {
                        "type": "sai",
                        "sai_type": strict_get_optional(die_result, "sai_type", "unknown"),
                        "count": die_result.get("count", 1),
                    }
                )

        # Apply terrain control and minor terrain effects to melee results
        if attacking_player_name:
            attacking_army_location = self.game_state_manager.get_army_location(attacking_player_name)
            if attacking_army_location:
                # Check for terrain control ID doubling
                terrain_controller = self.game_state_manager.get_terrain_controller(attacking_army_location)
                if terrain_controller == attacking_player_name and id_results > 0:
                    original_id = id_results
                    id_results = id_results * 2
                    hits += id_results - original_id  # Add doubled ID results to melee hits
                    effects.append(
                        {
                            "type": "terrain_control",
                            "description": f"Terrain control: Doubled ID results ({original_id} -> {id_results})",
                        }
                    )

                # Apply minor terrain effects
                if self.minor_terrain_manager:
                    melee_results = {"melee_results": hits, "id_results": id_results}
                    modified_results = self.apply_minor_terrain_effects(
                        attacking_player_name, attacking_army_location, melee_results, "MELEE"
                    )
                    hits = modified_results.get("melee_results", hits)
                    # Also apply ID doubling effect if present
                    if "id_results" in modified_results and modified_results["id_results"] != id_results:
                        id_bonus = modified_results["id_results"] - id_results
                        hits += id_bonus  # Add doubled ID results to melee hits

                    # Add applied effects to return data
                    if "minor_terrain_effects" in modified_results:
                        effects.extend(
                            [
                                {"type": "minor_terrain", "description": effect}
                                for effect in modified_results["minor_terrain_effects"]
                            ]
                        )

        return {
            "hits": hits,
            "damage": hits,  # Update damage to reflect modified hits
            "effects": effects,
            "raw_results": parsed_dice,
        }

    def resolve_magic(self, dice_results_str: str) -> dict:
        """
        Resolve magic dice results and return outcome.

        Args:
            dice_results_str: String representation of dice results

        Returns:
            Dict with magic effects and result information
        """
        parsed_dice = self.parse_dice_string(dice_results_str, "MAGIC")

        magic_icons = 0
        effects = []

        for die_result in parsed_dice:
            if die_result.get("type") == "Magic":
                magic_icons += die_result.get("count", 0)
            elif die_result.get("type") == "SAI":
                effects.append(
                    {
                        "type": "sai",
                        "sai_type": strict_get_optional(die_result, "sai_type", "unknown"),
                        "count": die_result.get("count", 1),
                    }
                )

        return {
            "magic_results": magic_icons,
            "effects_applied": magic_icons > 0,
            "effects": effects,
            "raw_results": parsed_dice,
        }

    def resolve_attacker_missile(self, dice_results_str: str, attacking_player_name: str | None = None) -> dict:
        """
        Resolve attacker missile dice results and return outcome.

        Args:
            dice_results_str: String representation of dice results
            attacking_player_name: Name of attacking player (for minor terrain effects)

        Returns:
            Dict with 'hits', 'damage', and other result information
        """
        parsed_dice = self.parse_dice_string(dice_results_str, "MISSILE")

        hits = 0
        damage = 0
        effects = []
        id_results = 0

        for die_result in parsed_dice:
            if die_result.get("type") == "Missile":
                hits += die_result.get("count", 0)
                damage += die_result.get("count", 0)  # Each missile hit does 1 damage
            elif die_result.get("type") == "ID":
                id_results += die_result.get("count", 0)
            elif die_result.get("type") == "SAI":
                effects.append(
                    {
                        "type": "sai",
                        "sai_type": strict_get_optional(die_result, "sai_type", "unknown"),
                        "count": die_result.get("count", 1),
                    }
                )

        # Apply terrain control and minor terrain effects to missile results
        if attacking_player_name:
            attacking_army_location = self.game_state_manager.get_army_location(attacking_player_name)
            if attacking_army_location:
                # Check for terrain control ID doubling
                terrain_controller = self.game_state_manager.get_terrain_controller(attacking_army_location)
                if terrain_controller == attacking_player_name and id_results > 0:
                    original_id = id_results
                    id_results = id_results * 2
                    hits += id_results - original_id  # Add doubled ID results to missile hits
                    effects.append(
                        {
                            "type": "terrain_control",
                            "description": f"Terrain control: Doubled ID results ({original_id} -> {id_results})",
                        }
                    )

                # Apply minor terrain effects
                if self.minor_terrain_manager:
                    missile_results = {"missile_results": hits, "id_results": id_results}
                    modified_results = self.apply_minor_terrain_effects(
                        attacking_player_name, attacking_army_location, missile_results, "MISSILE"
                    )
                    hits = modified_results.get("missile_results", hits)
                    # Also apply ID doubling effect if present
                    if "id_results" in modified_results and modified_results["id_results"] != id_results:
                        id_bonus = modified_results["id_results"] - id_results
                        hits += id_bonus  # Add doubled ID results to missile hits

                    # Add applied effects to return data
                    if "minor_terrain_effects" in modified_results:
                        effects.extend(
                            [
                                {"type": "minor_terrain", "description": effect}
                                for effect in modified_results["minor_terrain_effects"]
                            ]
                        )

        return {
            "hits": hits,
            "damage": hits,  # Update damage to reflect modified hits
            "effects": effects,
            "raw_results": parsed_dice,
        }

    def resolve_missile_attack(
        self,
        attacking_player_name: str,
        defending_player_name: str,
        missile_roll_results_str: str,
    ):
        """Resolves a missile attack (no saves allowed, direct damage)."""
        print(f"ActionResolver: Resolving missile attack from {attacking_player_name} to {defending_player_name}")

        # Parse missile dice results
        parsed_missile_dice = self.parse_dice_string(missile_roll_results_str, "MISSILE")

        # Calculate missile hits (similar to melee but no save phase)
        missile_hits = 0
        for icon_data in parsed_missile_dice:
            if icon_data.get("type") == "Missile":
                missile_hits += icon_data.get("count", 0)

        # Apply missile damage directly (no saves)
        if missile_hits > 0:
            if self._current_combat_location is None:
                raise ValueError("Current combat location cannot be None")
            defending_army_id = self.determine_defending_army_identifier(
                defending_player_name, self._current_combat_location
            )  # type: ignore[arg-type]
            self.game_state_manager.apply_damage_to_units(defending_player_name, defending_army_id, missile_hits)

        self.action_resolved.emit(
            {
                "type": "missile_complete",
                "attacker": attacking_player_name,
                "defender": defending_player_name,
                "hits": missile_hits,
                "damage_dealt": missile_hits,
            }
        )

        self.next_action_step_determined.emit("")  # End action

    def resolve_magic_action(
        self, casting_player_name: str, magic_roll_results_str: str, spell_casting_data: Optional[Dict[str, Any]] = None
    ):
        """Resolves a magic action (effects, SAIs, and spell casting)."""
        print(f"ActionResolver: Resolving magic action for {casting_player_name}")

        # Parse magic dice results
        parsed_magic_dice = self.parse_dice_string(magic_roll_results_str, "MAGIC")

        # Count available magic results by element
        magic_results_by_element = self._count_magic_results_by_element(casting_player_name, parsed_magic_dice)
        print(f"ActionResolver: Magic results by element: {magic_results_by_element}")

        magic_effects = []
        spells_cast = []

        # Handle spell casting if spell data provided
        if spell_casting_data and self.spell_resolver:
            spell_results = self._process_spell_casting(
                casting_player_name, spell_casting_data, magic_results_by_element
            )
            spells_cast = spell_results.get("spells_cast", [])
            magic_effects.extend(spell_results.get("effects", []))

        # Process non-spell magic effects
        for icon_data in parsed_magic_dice:
            if icon_data.get("type") == "Magic":
                # Non-spell magic icons might generate other effects
                count = icon_data.get("count", 1)
                if not spell_casting_data:  # Only add if no spells were cast
                    magic_effects.append(f"Unallocated magic results x{count}")
            elif icon_data.get("type") == "SAI":
                # SAIs from magic might have special effects
                sai_type = strict_get_optional(icon_data, "sai_type", "unknown")
                magic_effects.append(f"Magic SAI: {sai_type}")

        self.action_resolved.emit(
            {
                "type": "magic_complete",
                "caster": casting_player_name,
                "magic_results_by_element": magic_results_by_element,
                "spells_cast": spells_cast,
                "effects": magic_effects,
            }
        )

        self.next_action_step_determined.emit("")  # End action

    def resolve_maneuver_action(self, maneuvering_player_name: str, maneuver_roll_results_str: str):
        """Resolves a maneuver action (movement and positioning)."""
        print(f"ActionResolver: Resolving maneuver action for {maneuvering_player_name}")

        # Parse maneuver dice results
        parsed_maneuver_dice = self.parse_dice_string(maneuver_roll_results_str, "MANEUVER")

        maneuver_successes = 0
        maneuver_effects = []
        id_results = 0

        for icon_data in parsed_maneuver_dice:
            if icon_data.get("type") == "Maneuver":
                maneuver_successes += icon_data.get("count", 0)
            elif icon_data.get("type") == "ID":
                id_results += icon_data.get("count", 0)
            elif icon_data.get("type") == "SAI":
                # SAIs from maneuver might have special movement effects
                sai_type = strict_get_optional(icon_data, "sai_type", "unknown")
                maneuver_effects.append(f"Maneuver SAI: {sai_type}")
                # Handle specific maneuver SAIs
                if sai_type == "TELEPORT":  # Placeholder SAI
                    maneuver_effects.append("Teleport effect activated")

        # Apply terrain control and minor terrain effects to maneuver results
        maneuvering_army_location = self.game_state_manager.get_army_location(maneuvering_player_name)
        if maneuvering_army_location:
            # Check for terrain control ID doubling
            terrain_controller = self.game_state_manager.get_terrain_controller(maneuvering_army_location)
            if terrain_controller == maneuvering_player_name and id_results > 0:
                original_id = id_results
                id_results = id_results * 2
                maneuver_successes += id_results - original_id  # Add doubled ID results to maneuver successes
                maneuver_effects.append(f"Terrain control: Doubled ID results ({original_id} -> {id_results})")

            # Apply minor terrain effects
            if self.minor_terrain_manager:
                maneuver_results = {"maneuver_results": maneuver_successes, "id_results": id_results}
                modified_results = self.apply_minor_terrain_effects(
                    maneuvering_player_name, maneuvering_army_location, maneuver_results, "MANEUVER"
                )
                maneuver_successes = modified_results.get("maneuver_results", maneuver_successes)
                # Also apply ID doubling effect if present
                if "id_results" in modified_results and modified_results["id_results"] != id_results:
                    id_bonus = modified_results["id_results"] - id_results
                    maneuver_successes += id_bonus  # Add doubled ID results to maneuver successes

                # Add applied effects to return data
                if "minor_terrain_effects" in modified_results:
                    maneuver_effects.extend(modified_results["minor_terrain_effects"])

        # Apply maneuver results
        print(f"ActionResolver: Maneuver successes: {maneuver_successes}")
        if maneuver_successes > 0:
            # TODO: Apply actual movement logic based on maneuver successes
            print(f"ActionResolver: {maneuvering_player_name} can perform {maneuver_successes} movement actions")

        self.action_resolved.emit(
            {
                "type": "maneuver_complete",
                "player": maneuvering_player_name,
                "successes": maneuver_successes,
                "effects": maneuver_effects,
            }
        )

        self.next_action_step_determined.emit("")  # End action

    def resolve_counter_attack(
        self,
        counter_attacking_player_name: str,
        counter_attack_roll_results_str: str,
        original_attacker_name: str,
    ):
        """Resolves a counter-attack following a successful save."""
        print(
            f"ActionResolver: Resolving counter-attack from {counter_attacking_player_name} against {original_attacker_name}"
        )

        # Parse counter-attack dice (similar to melee attack)
        parsed_counter_dice = self.parse_dice_string(counter_attack_roll_results_str, "MELEE")

        # Process counter-attack (simplified - no saves for counter-attacks)
        counter_hits = 0
        for icon_data in parsed_counter_dice:
            if icon_data.get("type") == "Melee":
                counter_hits += icon_data.get("count", 0)

        # Apply counter-attack damage directly
        if counter_hits > 0:
            if self._current_combat_location is None:
                raise ValueError("Current combat location cannot be None")
            # Counter-attack targets the original attacker's army
            original_attacker_army_id = self.determine_attacking_army_identifier(
                original_attacker_name, self._current_combat_location
            )  # type: ignore[arg-type]
            self.game_state_manager.apply_damage_to_units(
                original_attacker_name, original_attacker_army_id, counter_hits
            )
            print(f"ActionResolver: Counter-attack dealt {counter_hits} damage to {original_attacker_name}")

        self.action_resolved.emit(
            {
                "type": "counter_attack_complete",
                "counter_attacker": counter_attacking_player_name,
                "original_attacker": original_attacker_name,
                "hits": counter_hits,
                "damage_dealt": counter_hits,
            }
        )

        self.next_action_step_determined.emit("")  # End action sequence

    def apply_minor_terrain_effects(
        self, player_name: str, army_location: str, roll_results: dict, roll_type: str
    ) -> dict:
        """Apply minor terrain effects to army roll results."""
        if not self.minor_terrain_manager or not army_location:
            return roll_results

        # Get minor terrain effects for this player at this location
        effects = self.minor_terrain_manager.get_minor_terrain_effects(army_location, player_name)

        modified_results = roll_results.copy()
        applied_effects = []

        for effect in effects:
            face_name = strict_get_optional(effect, "face_name", "")
            effect_type = strict_get_optional(effect, "effect_type", "")
            minor_terrain_name = strict_get_optional(effect, "minor_terrain_name", "")

            # Apply enhancement effects
            if effect_type == "enhancement":
                if face_name == "Double Saves" and roll_type in ["SAVE", "DEFENSIVE"]:
                    # Double ID results for saves
                    if "id_results" in modified_results:
                        original_id = modified_results["id_results"]
                        modified_results["id_results"] = original_id * 2
                        applied_effects.append(
                            f"{minor_terrain_name}: Doubled save ID results ({original_id} -> {modified_results['id_results']})"
                        )

                elif face_name == "Double Maneuvers" and roll_type in ["MANEUVER", "MOVEMENT"]:
                    # Double ID results for maneuvers
                    if "id_results" in modified_results:
                        original_id = modified_results["id_results"]
                        modified_results["id_results"] = original_id * 2
                        applied_effects.append(
                            f"{minor_terrain_name}: Doubled maneuver ID results ({original_id} -> {modified_results['id_results']})"
                        )

            # Apply negative effects (halving)
            elif effect_type == "negative":
                if face_name == "Flood" and roll_type in ["MANEUVER", "MOVEMENT"]:
                    # Halve maneuver results
                    if "maneuver_results" in modified_results:
                        original_maneuver = modified_results["maneuver_results"]
                        modified_results["maneuver_results"] = max(0, original_maneuver // 2)
                        applied_effects.append(
                            f"{minor_terrain_name}: Halved maneuver results ({original_maneuver} -> {modified_results['maneuver_results']})"
                        )

                elif face_name == "Flanked" and roll_type in ["SAVE", "DEFENSIVE"]:
                    # Halve save results
                    if "save_results" in modified_results:
                        original_save = modified_results["save_results"]
                        modified_results["save_results"] = max(0, original_save // 2)
                        applied_effects.append(
                            f"{minor_terrain_name}: Halved save results ({original_save} -> {modified_results['save_results']})"
                        )

                elif face_name == "Landslide" and roll_type in ["MISSILE", "RANGED"]:
                    # Halve missile results
                    if "missile_results" in modified_results:
                        original_missile = modified_results["missile_results"]
                        modified_results["missile_results"] = max(0, original_missile // 2)
                        applied_effects.append(
                            f"{minor_terrain_name}: Halved missile results ({original_missile} -> {modified_results['missile_results']})"
                        )

                elif face_name == "Revolt" and roll_type in ["MELEE", "COMBAT"]:
                    # Halve melee results
                    if "melee_results" in modified_results:
                        original_melee = modified_results["melee_results"]
                        modified_results["melee_results"] = max(0, original_melee // 2)
                        applied_effects.append(
                            f"{minor_terrain_name}: Halved melee results ({original_melee} -> {modified_results['melee_results']})"
                        )

        if applied_effects:
            modified_results["minor_terrain_effects"] = applied_effects
            print(f"ActionResolver: Applied minor terrain effects to {player_name}: {applied_effects}")

        return modified_results

    def get_available_minor_terrain_actions(self, player_name: str, army_location: str) -> list:
        """Get available actions from minor terrains controlled by player at location."""
        if not self.minor_terrain_manager or not army_location:
            return []

        effects = self.minor_terrain_manager.get_minor_terrain_effects(army_location, player_name)
        available_actions = []

        for effect in effects:
            face_name = strict_get_optional(effect, "face_name", "")
            effect_type = strict_get_optional(effect, "effect_type", "")
            minor_terrain_name = strict_get_optional(effect, "minor_terrain_name", "")

            if effect_type == "action":
                action_data = {
                    "action_type": face_name.lower(),  # "magic", "melee", "missile"
                    "source": f"Minor Terrain: {minor_terrain_name}",
                    "description": strict_get_optional(effect, "face_description", ""),
                    "allows_terrain_action": True,
                }
                available_actions.append(action_data)

            elif effect_type == "choice" and face_name == "ID":
                # ID face allows choosing any action
                for action_type in ["magic", "melee", "missile"]:
                    action_data = {
                        "action_type": action_type,
                        "source": f"Minor Terrain ID: {minor_terrain_name}",
                        "description": f"Choose {action_type} action from minor terrain ID face",
                        "allows_terrain_action": True,
                        "requires_choice": True,
                    }
                    available_actions.append(action_data)

        return available_actions

    def _count_magic_results_by_element(
        self, player_name: str, parsed_magic_dice: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Count magic results by element from parsed dice and player's units."""
        if not parsed_magic_dice:
            return {}

        # Get total magic result count
        total_magic_count = sum(
            icon_data.get("count", 0) for icon_data in parsed_magic_dice if icon_data.get("type") == "Magic"
        )

        if total_magic_count == 0:
            return {}

        # Get player's active army units
        active_units = self.game_state_manager.get_active_army_units(player_name)
        if not active_units:
            return {}

        # Count available elements from units
        element_counts = {}
        for unit in active_units:
            # Get unit species elements
            if hasattr(unit, "species"):
                species = unit.species
                if hasattr(species, "elements"):
                    unit_elements = species.elements
                else:
                    unit_elements = []
            else:
                # Handle dict format
                species_data = unit.get("species", {})
                unit_elements = species_data.get("elements", [])

            for element in unit_elements:
                element_name = element.lower()
                if element_name not in element_counts:
                    element_counts[element_name] = 0
                element_counts[element_name] += total_magic_count  # Each unit contributes all its magic

        return element_counts

    def _process_spell_casting(
        self, casting_player: str, spell_casting_data: Dict[str, Any], available_magic: Dict[str, int]
    ) -> Dict[str, Any]:
        """Process spell casting with available magic results."""
        if not self.spell_resolver:
            return {"spells_cast": [], "effects": ["Spell resolver not available"]}

        spells_to_cast = spell_casting_data.get("spells", [])
        spells_cast = []
        effects = []
        remaining_magic = available_magic.copy()

        for spell_request in spells_to_cast:
            spell_name = spell_request.get("name")
            target_data = spell_request.get("target", {})
            element_used = spell_request.get("element")
            casting_count = spell_request.get("count", 1)

            if not spell_name or not element_used:
                effects.append(f"Invalid spell request: missing name or element")
                continue

            # Check if enough magic results available
            element_lower = element_used.lower()
            if remaining_magic.get(element_lower, 0) < casting_count:
                effects.append(
                    f"Insufficient {element_used} magic for {spell_name} (need {casting_count}, have {remaining_magic.get(element_lower, 0)})"
                )
                continue

            # Validate spell availability
            available_spells = get_available_spells(
                magic_points_by_element=remaining_magic,
                army_species=self._get_player_species(casting_player),
                from_reserves=self._is_player_in_reserves(casting_player),
            )

            spell_available = any(
                spell.name.upper().replace(" ", "_") == spell_name.upper().replace(" ", "_")
                for spell in available_spells
            )
            if not spell_available:
                effects.append(f"Spell {spell_name} not available to cast")
                continue

            # Cast the spell
            spell_result = self.spell_resolver.cast_spell(
                spell_name, casting_player, target_data, element_used, casting_count
            )

            if spell_result.get("success"):
                # Deduct magic results
                remaining_magic[element_lower] -= casting_count
                spells_cast.append(
                    {
                        "name": spell_name,
                        "element": element_used,
                        "count": casting_count,
                        "target": target_data,
                        "results": spell_result.get("results", {}),
                    }
                )
                effects.append(f"Cast {spell_name} using {casting_count} {element_used} magic")
            else:
                effects.append(f"Failed to cast {spell_name}: {spell_result.get('error')}")

        return {"spells_cast": spells_cast, "effects": effects, "remaining_magic": remaining_magic}

    def _get_player_elements(self, player_name: str) -> List[str]:
        """Get all elements available to a player from their active units."""
        active_units = self.game_state_manager.get_active_army_units(player_name)
        elements = set()

        for unit in active_units:
            if hasattr(unit, "species"):
                species = unit.species
                if hasattr(species, "elements"):
                    unit_elements = species.elements
                else:
                    unit_elements = []
            else:
                species_data = unit.get("species", {})
                unit_elements = species_data.get("elements", [])

            elements.update(unit_elements)

        return list(elements)

    def _get_player_species(self, player_name: str) -> List[str]:
        """Get all species available to a player from their active units."""
        active_units = self.game_state_manager.get_active_army_units(player_name)
        species = set()

        for unit in active_units:
            if hasattr(unit, "species"):
                unit_species = unit.species
                if hasattr(unit_species, "name"):
                    species.add(unit_species.name)
                else:
                    # Handle dict format
                    species_name = strict_get(unit_species, "name")
                    species.add(species_name)
            else:
                # Handle dict format
                species_data = unit.get("species", {})
                species_name = strict_get(species_data, "name")
                species.add(species_name)

        return list(species)

    def _is_player_in_reserves(self, player_name: str) -> bool:
        """Check if player's active army is in reserves."""
        army_location = self.game_state_manager.get_army_location(player_name)
        return army_location == "reserves" if army_location else False
