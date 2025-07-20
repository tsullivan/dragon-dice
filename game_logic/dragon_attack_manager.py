"""
Dragon Attack Manager for Dragon Dice.

This module handles the Dragon Attack Phase mechanics, including targeting,
resolution, breath effects, and integration with the game state.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get_optional


class DragonTargetType(Enum):
    """Types of targets a dragon can attack."""

    DRAGON = "dragon"
    ARMY = "army"
    NONE = "none"


@dataclass
class DragonAttackTarget:
    """Represents a target for dragon attack."""

    target_type: DragonTargetType
    target_data: Dict[str, Any]  # Dragon data or army data
    reason: str  # Why this target was selected


@dataclass
class DragonAttackResult:
    """Result of a single dragon's attack."""

    dragon_id: str
    dragon_owner: str
    target: DragonAttackTarget
    die_result: str  # The face that was rolled
    damage_dealt: int
    special_effects: List[str]  # List of effects applied
    treasure_rolled: bool
    wings_rolled: bool
    breath_effects: List[Dict[str, Any]]  # Breath effect details
    success: bool
    message: str


@dataclass
class DragonPhaseResult:
    """Result of entire Dragon Attack Phase."""

    terrain_attacks: List[Dict[str, Any]]  # Attack results per terrain
    dragons_killed: List[str]  # Dragon IDs that were killed
    armies_affected: List[str]  # Army IDs that were affected
    promotions_earned: List[Dict[str, Any]]  # Promotion opportunities
    total_damage: int
    phase_completed: bool
    message: str


class DragonAttackManager(QObject):
    """Manages Dragon Attack Phase according to Dragon Dice rules."""

    # Signals for UI integration
    dragon_attack_started = Signal(dict)  # terrain_data
    dragon_targeting_determined = Signal(dict)  # targeting_info
    dragon_roll_requested = Signal(str, str)  # dragon_id, owner_name
    army_response_requested = Signal(str, str, list)  # terrain, army_id, attacking_dragons
    dragon_attack_completed = Signal(dict)  # attack_result
    phase_completed = Signal(dict)  # phase_result

    def __init__(self, parent=None):
        super().__init__(parent)

        # Dragon targeting matrix (rules from CSV provided)
        self.targeting_matrix = self._create_targeting_matrix()

        # Dragon breath effects by element
        self.breath_effects = self._create_breath_effects()

    def _create_targeting_matrix(self) -> Dict[str, Dict[str, str]]:
        """Create the dragon targeting matrix from the rules."""
        return {
            "Elemental": {
                "Elemental": "Will attack unless same element",
                "Hybrid": "Will attack",
                "Ivory": "Will not attack",
                "Ivory Hybrid": "Will attack unless the element matches",
                "White": "Will attack",
                "Army": "Will attack if no valid dragon target",
            },
            "Hybrid": {
                "Elemental": "Will attack",
                "Hybrid": "Will attack unless matching both elements",
                "Ivory": "Will not attack",
                "Ivory Hybrid": "Will attack unless matching one element",
                "White": "Will attack",
                "Army": "Will attack if no valid dragon target",
            },
            "Ivory": {
                "Elemental": "Will not attack",
                "Hybrid": "Will not attack",
                "Ivory": "Will not attack",
                "Ivory Hybrid": "Will not attack",
                "White": "Will not attack",
                "Army": "Will attack",
            },
            "Ivory Hybrid": {
                "Elemental": "Will not attack",
                "Hybrid": "Will not attack",
                "Ivory": "Will not attack",
                "Ivory Hybrid": "Will not attack",
                "White": "Will not attack",
                "Army": "Will attack",
            },
            "White": {
                "Elemental": "Will attack",
                "Hybrid": "Will attack",
                "Ivory": "Will not attack",
                "Ivory Hybrid": "Will attack",
                "White": "Will not attack",
                "Army": "Will attack if no valid dragon target",
            },
        }

    def _create_breath_effects(self) -> Dict[str, Dict[str, Any]]:
        """Create dragon breath effects by element type."""
        return {
            "Air": {
                "name": "Lightning Bolt",
                "effect": "The army's melee results are halved until the beginning of its next turn. Results are rounded down",
                "duration": "next_turn",
                "modifier_type": "halve_melee",
            },
            "Death": {
                "name": "Dragon Plague",
                "effect": "The army ignores all of its ID results until the beginning of its next turn",
                "duration": "next_turn",
                "modifier_type": "ignore_id",
            },
            "Earth": {
                "name": "Petrify",
                "effect": "The army's maneuver results are halved until the beginning of its next turn. Results are rounded down",
                "duration": "next_turn",
                "modifier_type": "halve_maneuver",
            },
            "Fire": {
                "name": "Dragon Fire",
                "effect": "Roll the units killed by this dragon's breath attack. Those that do not generate a save result are buried",
                "duration": "immediate",
                "modifier_type": "burial_save",
            },
            "Ivory": {
                "name": "Life Drain",
                "effect": "No additional effect",
                "duration": "none",
                "modifier_type": "none",
            },
            "Water": {
                "name": "Poisonous Cloud",
                "effect": "The army's missile results are halved until the beginning of its next turn. Results are rounded down",
                "duration": "next_turn",
                "modifier_type": "halve_missile",
            },
            "White": {
                "name": "Terrain Empathy",
                "effect": "An additional five health-worth of units in the army are killed, bringing the total health killed to ten. The army suffers the elemental breath effects of both elements of the terrain.",
                "duration": "immediate",
                "modifier_type": "terrain_empathy",
            },
        }

    def execute_dragon_attack_phase(
        self, marching_player: str, game_state_manager, dua_manager, summoning_pool_manager
    ) -> DragonPhaseResult:
        """Execute the complete Dragon Attack Phase."""

        print(f"DragonAttackManager: Executing Dragon Attack Phase for {marching_player}")

        # Step 1: Find all terrains where marching player has armies
        terrains_with_armies = self._find_terrains_with_marching_armies(marching_player, game_state_manager)

        if not terrains_with_armies:
            print("DragonAttackManager: No terrains with marching player armies found")
            return DragonPhaseResult(
                terrain_attacks=[],
                dragons_killed=[],
                armies_affected=[],
                promotions_earned=[],
                total_damage=0,
                phase_completed=True,
                message="No terrains with marching player armies - Dragon Attack Phase skipped",
            )

        # Step 2: For each terrain, check for dragons and execute attacks
        terrain_attacks = []
        all_dragons_killed = []
        all_armies_affected = []
        all_promotions = []
        total_damage = 0

        for terrain_name in terrains_with_armies:
            terrain_result = self._execute_terrain_dragon_attacks(
                terrain_name, marching_player, game_state_manager, summoning_pool_manager
            )

            if terrain_result:
                terrain_attacks.append(terrain_result)
                all_dragons_killed.extend(terrain_result.get("dragons_killed", []))
                all_armies_affected.extend(terrain_result.get("armies_affected", []))
                all_promotions.extend(terrain_result.get("promotions_earned", []))
                total_damage += terrain_result.get("damage_dealt", 0)

        # Create final result
        phase_result = DragonPhaseResult(
            terrain_attacks=terrain_attacks,
            dragons_killed=all_dragons_killed,
            armies_affected=all_armies_affected,
            promotions_earned=all_promotions,
            total_damage=total_damage,
            phase_completed=True,
            message=f"Dragon Attack Phase completed - {len(terrain_attacks)} terrain(s) had dragon attacks",
        )

        # Emit completion signal
        self.phase_completed.emit({"result": phase_result, "marching_player": marching_player})

        return phase_result

    def _find_terrains_with_marching_armies(self, marching_player: str, game_state_manager) -> List[str]:
        """Find all terrains where the marching player has armies."""
        terrains_with_armies = []

        # Get all terrains in the game
        all_terrains = game_state_manager.get_all_terrain_names()

        for terrain_name in all_terrains:
            armies_at_terrain = game_state_manager.get_armies_at_terrain(terrain_name)

            # Check if marching player has any army at this terrain
            for army_data in armies_at_terrain:
                if army_data.get("owner") == marching_player:
                    terrains_with_armies.append(terrain_name)
                    break

        return terrains_with_armies

    def _execute_terrain_dragon_attacks(
        self, terrain_name: str, marching_player: str, game_state_manager, summoning_pool_manager
    ) -> Optional[Dict[str, Any]]:
        """Execute dragon attacks at a specific terrain."""

        print(f"DragonAttackManager: Checking for dragons at terrain {terrain_name}")

        # Get all dragons at this terrain
        dragons_at_terrain = summoning_pool_manager.get_dragons_at_terrain(terrain_name)

        if not dragons_at_terrain:
            print(f"DragonAttackManager: No dragons at terrain {terrain_name}")
            return None

        print(f"DragonAttackManager: Found {len(dragons_at_terrain)} dragon(s) at {terrain_name}")

        # Get marching player's army at this terrain
        marching_army = self._get_marching_army_at_terrain(terrain_name, marching_player, game_state_manager)

        if not marching_army:
            print(f"DragonAttackManager: No marching army found at {terrain_name}")
            return None

        # Execute attacks for each dragon
        attack_results = []
        dragons_killed = []
        damage_dealt = 0

        for dragon_data in dragons_at_terrain:
            # Determine target for this dragon
            target = self._determine_dragon_target(dragon_data, dragons_at_terrain, marching_army, terrain_name)

            if target.target_type != DragonTargetType.NONE:
                # Execute the attack
                attack_result = self._execute_single_dragon_attack(dragon_data, target, game_state_manager)
                attack_results.append(attack_result)
                damage_dealt += attack_result.damage_dealt

                # Track killed dragons
                if not attack_result.success and target.target_type == DragonTargetType.DRAGON:
                    dragons_killed.append(target.target_data.get("dragon_id"))

        # Return terrain attack result
        return {
            "terrain_name": terrain_name,
            "attack_results": attack_results,
            "dragons_killed": dragons_killed,
            "armies_affected": [marching_army.get("army_id")],
            "damage_dealt": damage_dealt,
            "promotions_earned": [],  # Will be calculated later based on dragon kills
        }

    def _get_marching_army_at_terrain(
        self, terrain_name: str, marching_player: str, game_state_manager
    ) -> Optional[Dict[str, Any]]:
        """Get the marching player's army at the specified terrain."""
        armies_at_terrain = game_state_manager.get_armies_at_terrain(terrain_name)

        for army_data in armies_at_terrain:
            if army_data.get("owner") == marching_player:
                return army_data

        return None

    def _determine_dragon_target(
        self,
        attacking_dragon: Dict[str, Any],
        all_dragons: List[Dict[str, Any]],
        marching_army: Dict[str, Any],
        terrain_name: str,
    ) -> DragonAttackTarget:
        """Determine what a dragon will attack based on targeting rules."""

        dragon_type = self._get_dragon_type(attacking_dragon)
        print(f"DragonAttackManager: Determining target for {dragon_type} dragon")

        # Check for valid dragon targets first
        for potential_target in all_dragons:
            if potential_target == attacking_dragon:
                continue  # Don't attack self

            target_type = self._get_dragon_type(potential_target)
            targeting_rule = strict_get_optional(self.targeting_matrix[dragon_type], target_type, "Will not attack")

            if self._will_attack_dragon(attacking_dragon, potential_target, targeting_rule):
                return DragonAttackTarget(
                    target_type=DragonTargetType.DRAGON,
                    target_data=potential_target,
                    reason=f"{dragon_type} dragon attacks {target_type} dragon: {targeting_rule}",
                )

        # No valid dragon targets, attack the army
        army_targeting_rule = self.targeting_matrix[dragon_type]["Army"]
        if "Will attack" in army_targeting_rule:
            return DragonAttackTarget(
                target_type=DragonTargetType.ARMY,
                target_data=marching_army,
                reason=f"{dragon_type} dragon attacks army: {army_targeting_rule}",
            )

        # Dragon doesn't attack anything
        return DragonAttackTarget(
            target_type=DragonTargetType.NONE, target_data={}, reason=f"{dragon_type} dragon does not attack"
        )

    def _get_dragon_type(self, dragon_data: Dict[str, Any]) -> str:
        """Determine the dragon type for targeting rules."""
        elements = dragon_data.get("elements", [])

        if not elements:
            return "Ivory"
        if len(elements) == 1:
            if elements[0] == "white":
                return "White"
            if elements[0] == "ivory":
                return "Ivory"
            return "Elemental"
        if len(elements) == 2:
            if "ivory" in elements:
                return "Ivory Hybrid"
            return "Hybrid"
        return "White"  # All elements

    def _will_attack_dragon(self, attacker: Dict[str, Any], target: Dict[str, Any], targeting_rule: str) -> bool:
        """Determine if one dragon will attack another based on the targeting rule."""

        if "Will not attack" in targeting_rule:
            return False
        if "Will attack" in targeting_rule and "unless" not in targeting_rule:
            return True
        if "unless same element" in targeting_rule:
            return not self._dragons_share_element(attacker, target)
        if "unless matching both elements" in targeting_rule:
            return not self._dragons_match_all_elements(attacker, target)
        if "unless the element matches" in targeting_rule or "unless matching one element" in targeting_rule:
            return not self._dragons_share_element(attacker, target)

        return False

    def _dragons_share_element(self, dragon1: Dict[str, Any], dragon2: Dict[str, Any]) -> bool:
        """Check if two dragons share at least one element."""
        elements1 = set(dragon1.get("elements", []))
        elements2 = set(dragon2.get("elements", []))
        return bool(elements1.intersection(elements2))

    def _dragons_match_all_elements(self, dragon1: Dict[str, Any], dragon2: Dict[str, Any]) -> bool:
        """Check if two dragons have exactly the same elements."""
        elements1 = set(dragon1.get("elements", []))
        elements2 = set(dragon2.get("elements", []))
        return elements1 == elements2

    def _execute_single_dragon_attack(
        self, dragon_data: Dict[str, Any], target: DragonAttackTarget, game_state_manager
    ) -> DragonAttackResult:
        """Execute a single dragon's attack following the 7-step process."""

        dragon_id = strict_get_optional(dragon_data, "dragon_id", "unknown")
        dragon_owner = strict_get_optional(dragon_data, "owner", "unknown")

        print(f"DragonAttackManager: Executing attack by dragon {dragon_id} on {target.target_type.value}")

        # Step 1: Roll the dragon (simulated for now)
        die_result = self._simulate_dragon_roll(dragon_data)

        # Initialize result
        result = DragonAttackResult(
            dragon_id=dragon_id,
            dragon_owner=dragon_owner,
            target=target,
            die_result=die_result,
            damage_dealt=0,
            special_effects=[],
            treasure_rolled=False,
            wings_rolled=False,
            breath_effects=[],
            success=True,
            message="",
        )

        # Step 2: Process the rolled face
        self._process_dragon_die_result(result, die_result, dragon_data)

        # Steps 3-7 will be implemented as the system develops
        result.message = f"Dragon {dragon_id} rolled {die_result} against {target.target_type.value}"

        return result

    def _simulate_dragon_roll(self, dragon_data: Dict[str, Any]) -> str:
        """Simulate a dragon die roll (placeholder for actual rolling)."""
        # For now, return a random dragon face
        import random

        dragon_faces = [
            "Jaws",
            "Dragon_Breath",
            "Claw_Front_Left",
            "Claw_Front_Right",
            "Wing_Left",
            "Wing_Right",
            "Belly_Front",
            "Belly_Rear",
            "Claw_Rear_Left",
            "Claw_Rear_Right",
            "Tail_Front",
            "Treasure",
        ]
        return random.choice(dragon_faces)

    def _process_dragon_die_result(self, result: DragonAttackResult, die_result: str, dragon_data: Dict[str, Any]):
        """Process the result of a dragon die roll."""

        if die_result == "Jaws":
            result.damage_dealt = 12
            result.special_effects.append("Jaws: 12 points of damage")

        elif die_result == "Dragon_Breath":
            if result.target.target_type == DragonTargetType.DRAGON:
                # Against dragon: 5 damage (10 for White Dragon) + re-roll
                base_damage = 10 if self._is_white_dragon(dragon_data) else 5
                result.damage_dealt = base_damage
                result.special_effects.append(f"Breath vs Dragon: {base_damage} damage + re-roll")
            else:
                # Against army: 5 health-worth killed + breath effect
                result.damage_dealt = 5
                breath_effect = self._get_breath_effect(dragon_data)
                result.breath_effects.append(breath_effect)
                result.special_effects.append(f"Breath vs Army: 5 units killed + {breath_effect['name']}")

        elif "Claw" in die_result:
            result.damage_dealt = 6
            result.special_effects.append("Claw: 6 points of damage")

        elif "Wing" in die_result:
            result.damage_dealt = 5
            result.wings_rolled = True
            result.special_effects.append("Wing: 5 points of damage + dragon flies away")

        elif "Belly" in die_result:
            result.damage_dealt = 0
            result.special_effects.append("Belly: Dragon vulnerable (no automatic saves)")

        elif "Tail" in die_result:
            result.damage_dealt = 3
            result.special_effects.append("Tail: 3 points of damage + re-roll dragon")

        elif die_result == "Treasure":
            result.damage_dealt = 0
            result.treasure_rolled = True
            result.special_effects.append("Treasure: Target army may promote one unit")

    def _is_white_dragon(self, dragon_data: Dict[str, Any]) -> bool:
        """Check if a dragon is a White Dragon."""
        elements = dragon_data.get("elements", [])
        return "white" in elements or len(elements) >= 5

    def _get_breath_effect(self, dragon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the breath effect for a dragon based on its elements."""
        elements = dragon_data.get("elements", [])

        if not elements:
            return self.breath_effects["Ivory"]
        if "white" in elements or len(elements) >= 5:
            return self.breath_effects["White"]
        # Use the first element for breath effect
        primary_element = elements[0].title()
        return strict_get_optional(self.breath_effects, primary_element, self.breath_effects["Ivory"])
