"""
Dragon Combat Resolution System for Dragon Dice.

This module handles dragon attack mechanics including targeting determination,
damage calculation, breath effects, and combat resolution according to Dragon Dice rules.
"""

from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get, strict_get_optional, strict_get_with_fallback


class DragonCombatResolver(QObject):
    """
    Resolves dragon combat mechanics including targeting, attacks,
    and breath effects according to Dragon Dice rules.
    """

    dragon_targeting_determined = Signal(dict)  # targeting_results
    dragon_attacks_resolved = Signal(list)  # attack_results
    breath_effects_processed = Signal(list)  # breath_effects

    def __init__(self, game_state_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager

    def determine_dragon_targeting(
        self,
        dragons_present: List[Dict[str, Any]],
        marching_player: str,
        marching_army: Dict[str, Any],
        terrain_name: str,
    ) -> Dict[str, Any]:
        """
        Determine dragon targets according to Dragon Dice targeting priority rules.

        Priority order:
        1. Dragons attack other dragons first (if any)
        2. Dragons attack armies if no other dragons present
        3. Consider special targeting rules

        Returns:
            Dictionary mapping dragon IDs to target information
        """
        targeting_results = {}

        # Get all armies at terrain (including the marching army)
        armies_at_terrain = self._get_armies_at_terrain(terrain_name)
        other_dragons = [d for d in dragons_present]  # All dragons can potentially target each other

        for dragon in dragons_present:
            dragon_id = strict_get_with_fallback(dragon, "dragon_id", "id", dragon)
            dragon_name = strict_get(dragon, "name")
            dragon_owner = strict_get(dragon, "owner")

            # Dragon targeting priority logic
            target_info = self._determine_single_dragon_target(
                dragon, other_dragons, armies_at_terrain, marching_player, marching_army
            )

            targeting_results[dragon_id] = {
                "dragon_name": dragon_name,
                "dragon_owner": dragon_owner,
                "target_type": target_info["target_type"],  # "dragon", "army", or "none"
                "target_description": target_info["description"],
                "target_data": target_info.get("target_data", {}),
                "reason": target_info["reason"],
            }

        self.dragon_targeting_determined.emit(targeting_results)
        return targeting_results

    def _determine_single_dragon_target(
        self,
        dragon: Dict[str, Any],
        available_dragons: List[Dict[str, Any]],
        armies_at_terrain: List[Dict[str, Any]],
        marching_player: str,
        marching_army: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Determine target for a single dragon."""
        dragon_owner = strict_get(dragon, "owner")
        dragon_name = strict_get(dragon, "name")

        # Priority 1: Target other dragons (excluding self)
        enemy_dragons = [
            d
            for d in available_dragons
            if strict_get(d, "owner") != dragon_owner and strict_get(d, "name") != dragon_name
        ]

        if enemy_dragons:
            # Target the first enemy dragon (can be enhanced with more sophisticated targeting)
            target_dragon = enemy_dragons[0]
            return {
                "target_type": "dragon",
                "description": f"Dragon: {strict_get(target_dragon, 'name')} ({strict_get(target_dragon, 'owner')})",
                "target_data": target_dragon,
                "reason": "Dragons target other dragons first",
            }

        # Priority 2: Target enemy armies
        enemy_armies = [army for army in armies_at_terrain if strict_get(army, "owner") != dragon_owner]

        if enemy_armies:
            # Prefer the marching army if it's an enemy
            if strict_get(marching_army, "owner", marching_player) != dragon_owner:
                return {
                    "target_type": "army",
                    "description": f"{marching_player}'s army ({strict_get(marching_army, 'name')})",
                    "target_data": marching_army,
                    "reason": "Targeting marching army",
                }
            else:
                # Target first enemy army
                target_army = enemy_armies[0]
                return {
                    "target_type": "army",
                    "description": f"{strict_get(target_army, 'owner')}'s army ({strict_get(target_army, 'name')})",
                    "target_data": target_army,
                    "reason": "No other dragons available",
                }

        # No valid targets
        return {"target_type": "none", "description": "No valid targets", "reason": "Dragon has no enemies at terrain"}

    def resolve_dragon_attacks(
        self, targeting_results: Dict[str, Any], dragons_present: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Resolve dragon attacks by simulating die rolls and calculating results.

        Returns:
            List of attack result dictionaries
        """
        attack_results = []

        for dragon in dragons_present:
            dragon_id = strict_get_with_fallback(dragon, "dragon_id", "id", dragon)
            dragon_name = strict_get(dragon, "name")

            # Get targeting info for this dragon
            target_info = targeting_results.get(dragon_id, {})
            target_type = strict_get_optional(target_info, "target_type", "none")

            if target_type == "none":
                continue

            # Roll dragon die and calculate results
            roll_result = self._roll_dragon_die(dragon)
            damage_result = self._calculate_dragon_damage(roll_result, target_type, dragon)

            attack_result = {
                "dragon_id": dragon_id,
                "dragon_name": dragon_name,
                "target_type": target_type,
                "target_data": target_info.get("target_data", {}),
                "die_result": roll_result["face"],
                "damage_dealt": damage_result["damage"],
                "special_effects": damage_result["effects"],
                "wings_rolled": roll_result["face"] in ["Wing_Left", "Wing_Right"],
                "treasure_rolled": roll_result["face"] == "Treasure",
                "breath_effects": damage_result.get("breath_effects", []),
            }

            attack_results.append(attack_result)

        self.dragon_attacks_resolved.emit(attack_results)
        return attack_results

    def _roll_dragon_die(self, dragon: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate rolling a dragon die."""
        import random

        # Standard dragon faces
        dragon_faces = [
            "Jaws",
            "Dragon_Breath",
            "Claw_Front_Left",
            "Claw_Front_Right",
            "Wing_Left",
            "Wing_Right",
            "Belly_Front",
            "Belly_Back",
            "Treasure",
        ]

        # Special cases for different dragon types
        dragon_name = strict_get(dragon, "name")

        # Weighted probabilities (can be enhanced for different dragon types)
        face = random.choice(dragon_faces)

        return {"face": face, "dragon_name": dragon_name}

    def _calculate_dragon_damage(
        self, roll_result: Dict[str, Any], target_type: str, dragon: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate damage and effects from dragon die roll."""
        face = strict_get(roll_result, "face")
        dragon_name = strict_get(dragon, "name")
        is_white_dragon = "White" in dragon_name

        # Base damage values for each face
        damage_values = {
            "Jaws": 12,
            "Dragon_Breath": 5 if target_type == "army" else 0,  # Breath only affects armies directly
            "Claw_Front_Left": 6,
            "Claw_Front_Right": 6,
            "Wing_Left": 5,
            "Wing_Right": 5,
            "Belly_Front": 0,  # Vulnerable, no damage
            "Belly_Back": 0,  # Vulnerable, no damage
            "Treasure": 0,  # Beneficial effect
        }

        base_damage = damage_values.get(face, 0)
        effects = []
        breath_effects = []

        # Calculate effects based on face
        if face == "Jaws":
            effects.append(f"Jaws: {base_damage} points of damage")

        elif face == "Dragon_Breath":
            if target_type == "army":
                effects.append("Breath: Kills 5 units + elemental effect")
                breath_effects.append(
                    {
                        "name": "Dragon Breath",
                        "effect": "Kill 5 units immediately, survivors roll burial saves",
                        "units_killed": 5,
                        "element_effect": self._get_dragon_breath_element(dragon),
                    }
                )
            else:
                effects.append("Breath: No effect on dragon targets")

        elif "Claw" in face:
            effects.append(f"Claw: {base_damage} points of damage")

        elif "Wing" in face:
            effects.append(f"Wing: {base_damage} points of damage + dragon flies away")

        elif "Belly" in face:
            effects.append("Belly: Dragon vulnerable (no automatic saves)")

        elif face == "Treasure":
            if target_type == "army":
                effects.append("Treasure: Target army may promote one unit")
            else:
                effects.append("Treasure: No effect")

        # White dragons take double damage when vulnerable
        if is_white_dragon and "Belly" in face:
            effects.append("White Dragon vulnerability: Takes double damage this round")

        return {
            "damage": base_damage,
            "effects": effects,
            "breath_effects": breath_effects,
            "vulnerable": "Belly" in face,
            "flies_away": "Wing" in face,
        }

    def _get_dragon_breath_element(self, dragon: Dict[str, Any]) -> str:
        """Get the elemental effect of dragon breath."""
        dragon_elements = strict_get_optional(dragon, "elements", [])
        if dragon_elements:
            return dragon_elements[0].upper()  # Use first element
        return "FIRE"  # Default to fire

    def process_breath_effects(
        self, attack_results: List[Dict[str, Any]], target_player: str, target_army_id: str
    ) -> List[Dict[str, Any]]:
        """
        Process dragon breath effects on target army.

        Returns:
            List of processed breath effects with results
        """
        processed_effects = []

        for attack in attack_results:
            breath_effects = strict_get_optional(attack, "breath_effects", [])

            for effect in breath_effects:
                if strict_get(effect, "name") == "Dragon Breath":
                    # Process breath weapon effect
                    units_to_kill = strict_get(effect, "units_killed")
                    element_effect = strict_get(effect, "element_effect")

                    # Get target army units
                    army_data = self.game_state_manager.get_army_data(target_player, target_army_id)
                    army_units = strict_get(army_data, "units")
                    alive_units = [u for u in army_units if strict_get(u, "health") > 0]

                    # Select units to be affected (weakest first for breath)
                    affected_units = sorted(alive_units, key=lambda u: strict_get(u, "health"))[:units_to_kill]

                    processed_effect = {
                        "type": "dragon_breath",
                        "dragon_name": strict_get(attack, "dragon_name"),
                        "element": element_effect,
                        "units_affected": len(affected_units),
                        "units_killed": [],
                        "burial_saves_needed": [],
                    }

                    # Apply breath effect to units
                    for unit in affected_units:
                        unit_id = strict_get_optional(unit, "id", strict_get(unit, "name"))
                        unit_name = strict_get(unit, "name")

                        # Kill unit immediately
                        kill_success = self.game_state_manager.kill_unit(target_player, target_army_id, unit_id)

                        if kill_success:
                            processed_effect["units_killed"].append(
                                {"name": unit_name, "id": unit_id, "species": strict_get(unit, "species")}
                            )

                            # Add to burial saves (survivors may get saves)
                            processed_effect["burial_saves_needed"].append(
                                {
                                    "name": unit_name,
                                    "id": unit_id,
                                    "species": strict_get(unit, "species"),
                                    "element": element_effect,
                                }
                            )

                    processed_effects.append(processed_effect)

        self.breath_effects_processed.emit(processed_effects)
        return processed_effects

    def calculate_dragon_deaths(
        self, attack_results: List[Dict[str, Any]], army_response_damage: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate which dragons are killed based on attack results and army response.

        Args:
            attack_results: Results from dragon attacks
            army_response_damage: Damage dealt by army response {dragon_id: damage}

        Returns:
            Dictionary with dragon death information
        """
        dragon_deaths = {"dragons_killed": [], "total_killed": 0, "kill_details": []}

        for attack in attack_results:
            dragon_id = strict_get(attack, "dragon_id")
            dragon_name = strict_get(attack, "dragon_name")

            # Check if dragon is vulnerable (belly faces)
            is_vulnerable = any("Belly" in effect for effect in strict_get_optional(attack, "special_effects", []))

            # Calculate total damage to dragon
            response_damage = army_response_damage.get(dragon_id, 0)

            # Dragons need 5 damage to die (10 for White Dragons, but vulnerably counts as double damage)
            is_white_dragon = "White" in dragon_name
            death_threshold = 10 if is_white_dragon else 5

            # Apply vulnerability modifier
            effective_damage = response_damage * 2 if is_vulnerable else response_damage

            if effective_damage >= death_threshold:
                dragon_deaths["dragons_killed"].append(
                    {
                        "dragon_id": dragon_id,
                        "dragon_name": dragon_name,
                        "damage_taken": response_damage,
                        "effective_damage": effective_damage,
                        "was_vulnerable": is_vulnerable,
                        "death_threshold": death_threshold,
                    }
                )

                dragon_deaths["kill_details"].append(
                    f"{dragon_name} killed by {effective_damage} damage ({'vulnerable' if is_vulnerable else 'normal'})"
                )

        dragon_deaths["total_killed"] = len(dragon_deaths["dragons_killed"])
        return dragon_deaths

    def calculate_army_response_options(
        self, marching_army: Dict[str, Any], attacking_dragons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate army response options against dragon attacks.

        Returns:
            Dictionary with response options and mechanics
        """
        army_units = strict_get(marching_army, "units")
        alive_units = [u for u in army_units if strict_get(u, "health") > 0]

        response_options = {
            "can_respond": len(alive_units) > 0,
            "total_units": len(alive_units),
            "response_types": ["combination_roll"],  # melee + missile + save
            "targeting_options": [],
            "damage_potential": {},
        }

        # Calculate potential damage against each dragon
        for dragon in attacking_dragons:
            dragon_id = strict_get_with_fallback(dragon, "dragon_id", "id", dragon)
            dragon_name = strict_get(dragon, "name")

            # Estimate damage potential (simplified calculation)
            unit_count = len(alive_units)
            estimated_melee_results = max(1, unit_count // 3)  # Rough estimate
            estimated_missile_results = max(1, unit_count // 4)  # Rough estimate

            max_damage = max(estimated_melee_results, estimated_missile_results)  # Can't combine

            response_options["targeting_options"].append(
                {
                    "dragon_id": dragon_id,
                    "dragon_name": dragon_name,
                    "estimated_max_damage": max_damage,
                    "can_kill": max_damage >= 5,  # Standard dragon death threshold
                }
            )

            response_options["damage_potential"][dragon_id] = max_damage

        return response_options

    def _get_armies_at_terrain(self, terrain_name: str) -> List[Dict[str, Any]]:
        """Get all armies currently at the specified terrain."""
        armies = []

        # Get all players
        all_players = self.game_state_manager.get_all_player_names()

        for player in all_players:
            player_armies = self.game_state_manager.get_all_armies_at_location(player, terrain_name)
            for army in player_armies:
                army_with_owner = dict(army)
                army_with_owner["owner"] = player
                armies.append(army_with_owner)

        return armies

    def get_promotion_opportunities(self, dragons_killed: int, army_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate promotion opportunities from killing dragons.

        Args:
            dragons_killed: Number of dragons killed by the army
            army_data: Army that killed the dragons

        Returns:
            Dictionary with promotion information
        """
        if dragons_killed <= 0:
            return {"has_promotions": False, "eligible_units": []}

        army_units = strict_get(army_data, "units")
        alive_units = [u for u in army_units if strict_get(u, "health") > 0]

        # Get promotable units (those not at max health for their species)
        promotable_units = []
        for unit in alive_units:
            current_health = strict_get(unit, "health")
            max_health = strict_get(unit, "max_health")

            # Check if unit can be promoted (simplified - would need species promotion rules)
            if current_health < max_health:
                promotable_units.append(
                    {
                        "name": strict_get(unit, "name"),
                        "id": strict_get_optional(unit, "id", strict_get(unit, "name")),
                        "species": strict_get(unit, "species"),
                        "current_health": current_health,
                        "max_health": max_health,
                        "can_promote": True,  # Simplified check
                    }
                )

        return {
            "has_promotions": dragons_killed > 0,
            "dragons_killed": dragons_killed,
            "promotion_points": dragons_killed,  # One promotion per dragon killed
            "eligible_units": promotable_units,
            "max_promotions": min(dragons_killed, len(promotable_units)),
        }
