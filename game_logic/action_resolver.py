from PySide6.QtCore import QObject, Signal
from typing import Optional
import constants  # For ICON_MELEE etc.

# Forward declaration for type hinting if GameStateManager and EffectManager are in different files
# and create circular dependencies. Or import them directly if no circular dependency.
from .game_state_manager import GameStateManager
from .effect_manager import EffectManager


class ActionResolver(QObject):
    """Resolves game actions like melee, missile, magic, and maneuvers."""

    action_resolved = Signal(dict)  # Emits a dictionary with action results/outcomes
    # Example: {"type": "melee", "damage_done": 5, "effects_triggered": [...]}
    next_action_step_determined = Signal(str)  # Emits the next action_step constant

    def __init__(
        self,
        game_state_manager: GameStateManager,
        effect_manager: EffectManager,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.effect_manager = effect_manager

    # This method might be too generic; specific methods per action type are better.
    def resolve_melee_attack(
        self, attacker_army, defender_army, attacker_roll_results_str
    ):
        """Resolves a melee attack sequence, including saves and counter-attacks."""
        # TODO: Implement melee resolution logic
        # This will involve parsing dice, applying SAIs, calculating damage, handling saves,
        # checking for counter-attacks, and potentially interacting with an EffectManager.
        print(
            f"ActionResolver: Resolving melee attack. Attacker results: {attacker_roll_results_str}"
        )
        # self.action_resolved.emit(...)
        pass

    def process_attacker_melee_roll(
        self, attacking_player_name: str, parsed_dice_results: list
    ) -> dict:
        """
        Processes the attacker's melee roll.
        Queries game state for attacker's units, abilities, and active effects.
        Calculates hits, damage, and any SAIs that affect the defender.
        Returns a dictionary with results, e.g., {"hits": N, "sais_for_defender": [...]}
        """
        print(
            f"ActionResolver: Processing attacker melee roll for {attacking_player_name} with {parsed_dice_results}"
        )

        attacking_units = self.game_state_manager.get_active_army_units(
            attacking_player_name
        )
        if not attacking_units:
            print(
                f"ActionResolver: No active units found for attacker {attacking_player_name}. Aborting melee roll processing."
            )
            # self.next_action_step_determined.emit(constants.ACTION_STEP_SELECT_ACTION) # Or some error state
            return {"hits": 0, "sais_for_defender": []}  # Early exit

        print(
            f"ActionResolver: Attacking units: {[unit.get('name') for unit in attacking_units]}"
        )

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
            if icon_data.get("type") == constants.ICON_ID:
                id_icons_to_convert += icon_data.get("count", 0)
            elif icon_data.get("type") == constants.ICON_MELEE:
                calculated_results["hits"] += icon_data.get("count", 0)
            # TODO: Handle SAIs that modify attacker's roll (e.g., Doubler) here or in a dedicated step

        # Convert ID icons based on unit abilities (simplified: 1 ID per unit, first available)
        converted_id_hits = 0
        units_that_used_id = set()  # To ensure a unit's ID is used only once per roll
        for _ in range(id_icons_to_convert):
            for unit in attacking_units:
                if unit["id"] not in units_that_used_id:
                    id_ability = unit.get("abilities", {}).get("id_results", {})
                    if (
                        constants.ICON_MELEE in id_ability
                    ):  # Check if unit's ID produces melee
                        converted_id_hits += id_ability[constants.ICON_MELEE]
                        units_that_used_id.add(unit["id"])
                        print(
                            f"ActionResolver: Unit {unit['name']} used ID for {id_ability[constants.ICON_MELEE]} melee."
                        )
                        break  # Move to the next ID icon to be converted
        calculated_results["hits"] += converted_id_hits

        # --- Stage 2: Apply SAIs that modify results (e.g., Doubler) ---
        # TODO: 4. Apply SAIs from parsed_dice_results that modify the attacker's roll (e.g., Doubler). (This was TODO #3 before ID conversion)
        # Example:
        for icon_data in remaining_icons:
            if (
                icon_data.get("type") == constants.ICON_SAI
                and icon_data.get("name") == constants.SAI_DOUBLER
            ):
                print(
                    f"ActionResolver: Applying {constants.SAI_DOUBLER}. Current hits: {calculated_results['hits']}"
                )
                calculated_results["hits"] *= 2  # Assuming one Doubler for now
                # TODO: Handle multiple doublers/triplers (usually best one applies)
                break  # Typically only one such SAI is effective

        # --- Stage 3: Apply Modifiers from Active Effects ---
        # Get relevant active effects from self.effect_manager for the attacker/attacking army.
        # For now, assume target_army_identifier can be derived or is not strictly needed for attacker's own buffs/debuffs.
        active_mods = self.effect_manager.get_active_modifiers(
            attacking_player_name, None, "MELEE"
        )
        calculated_results["hits"] += active_mods.get("melee_bonus", 0)
        if active_mods.get("halve_results"):
            calculated_results["hits"] = (
                calculated_results["hits"] // 2
            )  # Integer division

        # TODO: 5. Apply modifiers from active effects. (Partially done above, may need more complex logic)
        # TODO: 6. Calculate total melee hits/damage. (This is partially done, needs to incorporate SAIs/modifiers)

        # --- Stage 4: Identify SAIs affecting defender's save roll ---
        for icon_data in remaining_icons:
            if (
                icon_data.get("type") == constants.ICON_SAI
                and icon_data.get("name") == constants.SAI_BULLSEYE
            ):
                calculated_results["sais_for_defender"].append(constants.SAI_BULLSEYE)
                print(
                    f"ActionResolver: {constants.SAI_BULLSEYE} identified for defender's save."
                )
        # TODO: 7. Identify SAIs that will affect the defender's save roll.

        # After processing, determine the next step
        self.next_action_step_determined.emit(
            constants.ACTION_STEP_AWAITING_DEFENDER_SAVES
        )
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

        defending_units = self.game_state_manager.get_active_army_units(
            defending_player_name
        )
        if not defending_units:
            print(
                f"ActionResolver: No active units found for defender {defending_player_name}."
            )
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

        print(
            f"ActionResolver: Defending units: {[unit.get('name') for unit in defending_units]}"
        )

        successful_saves = 0
        sais_from_attacker = attacker_outcome.get("sais_for_defender", [])
        attacker_hits = attacker_outcome.get("hits", 0)

        # TODO: 1. Apply SAIs from attacker that affect saves (e.g., Bullseye negates ID saves).
        # Example: If Bullseye is present, ID icons rolled by the defender might be ignored.
        bullseye_active = constants.SAI_BULLSEYE in sais_from_attacker
        if bullseye_active:
            print(
                "ActionResolver: Attacker Bullseye is active, affecting defender saves."
            )

        # TODO: 2. Convert ID icons in parsed_save_dice to actual save results based on defending_units abilities.
        converted_id_saves = 0
        units_that_used_id = set()  # To ensure a unit's ID is used only once per roll
        id_icons_to_convert = sum(
            item.get("count", 0)
            for item in parsed_save_dice
            if item.get("type") == constants.ICON_ID
        )

        for _ in range(id_icons_to_convert):
            # If Bullseye is active, ID icons might not convert to saves (rule dependent)
            if bullseye_active:
                print("ActionResolver: Bullseye prevents ID conversion to saves.")
                break  # Skip ID conversion if Bullseye active (simplified rule)

            for unit in defending_units:
                if unit["id"] not in units_that_used_id:
                    id_ability = unit.get("abilities", {}).get("id_results", {})
                    if (
                        constants.ICON_SAVE in id_ability
                    ):  # Check if unit's ID produces saves
                        converted_id_saves += id_ability[constants.ICON_SAVE]
                        units_that_used_id.add(unit["id"])
                        print(
                            f"ActionResolver: Unit {unit['name']} used ID for {id_ability[constants.ICON_SAVE]} save."
                        )
                        break  # Move to the next ID icon to be converted
        successful_saves += converted_id_saves

        # TODO: 3. Apply SAIs from parsed_save_dice that generate saves or modify save results.
        # Example: SAI_SHIELD might add saves.

        # TODO: 4. Get relevant active effects from self.effect_manager for the defender/defending army and apply them.
        # For now, assume target_army_identifier can be derived or is not strictly needed for defender's own buffs/debuffs.
        active_mods = self.effect_manager.get_active_modifiers(
            defending_player_name, None, "SAVE"
        )
        successful_saves += active_mods.get("save_bonus", 0)
        if active_mods.get("halve_results"):  # Effects can halve saves too
            successful_saves = successful_saves // 2
        if active_mods.get("double_results"):  # Effects can double saves
            successful_saves = successful_saves * 2

        # Placeholder for direct save icons
        for item in parsed_save_dice:
            if item.get("type") == constants.ICON_SAVE:
                successful_saves += item.get("count", 0)

        # --- Calculate final damage ---
        final_damage = max(0, attacker_hits - successful_saves)
        print(
            f"ActionResolver: Attacker Hits: {attacker_hits}, Successful Saves: {successful_saves}, Final Damage: {final_damage}"
        )

        # --- Apply Damage ---
        # TODO: Determine the specific army identifier being attacked.
        self.game_state_manager.apply_damage_to_units(
            defending_player_name, constants.PLACEHOLDER_DEFENDING_ARMY_ID, final_damage
        )

        # TODO: 6. Determine if a counter-attack is possible (Rulebook pg. 12).
        counter_attack_possible = False  # Placeholder

        if counter_attack_possible:
            self.next_action_step_determined.emit(
                constants.ACTION_STEP_AWAITING_MELEE_COUNTER_ATTACK_ROLL
            )  # Placeholder constant
        else:
            self.next_action_step_determined.emit(
                ""
            )  # Empty string signifies end of this action, advance phase/march
        return {
            "damage_taken": final_damage,
            "saves_made": successful_saves,
            "counter_attack_possible": counter_attack_possible,
        }

    def parse_dice_string(self, dice_string: str, roll_type: str) -> list:
        """
        Helper to parse a string like '3 melee, 1 sai:bullseye, 2 id' into a structured list.
        Returns an empty list if parsing fails or input is invalid.
        """
        # Very basic placeholder parser. This needs to be robust.
        # Example: "2m, 1s:doubler, 3id"
        # TODO: Implement robust parsing (regex, string splitting, error handling, validation of icon names)
        print(
            f"ActionResolver: Attempting to parse '{dice_string}' for roll type '{roll_type}'"
        )
        parsed_list = []
        if not dice_string or not isinstance(dice_string, str):
            return parsed_list  # Return empty for invalid input
        parts = dice_string.lower().split(",")
        for part in parts:
            part = part.strip()
            # This is highly simplified and needs proper logic for numbers, icon names, and SAI names.
            if "melee" in part or "m" in part:  # Example
                parsed_list.append(
                    {
                        "type": constants.ICON_MELEE,
                        "count": (
                            int(part.split(" ")[0])
                            if part.split(" ")[0].isdigit()
                            else 1
                        ),
                    }
                )
        return parsed_list

    # TODO: Add methods for resolving missile attacks, magic actions, maneuvers, etc.
    # def _resolve_dice_roll(self, army_units: list, rolled_icons: list, roll_type: str, ...) -> dict: ...
