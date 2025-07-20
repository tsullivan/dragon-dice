"""
Dragon Combat Controller for Dragon Dice.

This controller coordinates dragon combat actions including targeting determination,
attack resolution, and combat management through the proper domain layers.
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get, strict_get_optional


class DragonCombatController(QObject):
    """
    Controller for dragon combat actions, coordinating between UI and game logic layers.
    """

    dragon_attack_initiated = Signal(dict)  # attack_setup_data
    dragon_targeting_completed = Signal(dict)  # targeting_results
    dragon_attacks_resolved = Signal(list)  # attack_results
    army_response_required = Signal(dict)  # response_options
    dragon_combat_completed = Signal(dict)  # combat_results

    def __init__(self, game_engine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.dragon_combat_resolver = None  # Will be set from game engine

    def set_dragon_combat_resolver(self, resolver):
        """Set the dragon combat resolver instance."""
        self.dragon_combat_resolver = resolver

    @Slot(str, str, list, dict)
    def handle_dragon_attack_initiation(
        self, marching_player: str, terrain_name: str, dragons_present: list, marching_army: dict
    ):
        """Handle the initiation of a dragon attack phase."""
        print(f"[DragonCombatController] Initiating dragon attack at {terrain_name}")
        print(f"[DragonCombatController] Dragons present: {len(dragons_present)}")

        if not dragons_present:
            # No dragons, skip phase
            self.dragon_combat_completed.emit(
                {
                    "skipped": True,
                    "reason": "No dragons present",
                    "terrain": terrain_name,
                    "marching_player": marching_player,
                }
            )
            return

        # Set up attack data
        attack_setup = {
            "marching_player": marching_player,
            "terrain_name": terrain_name,
            "dragons_present": dragons_present,
            "marching_army": marching_army,
            "total_dragons": len(dragons_present),
        }

        self.dragon_attack_initiated.emit(attack_setup)

        # Start targeting determination
        self._determine_dragon_targeting(dragons_present, marching_player, marching_army, terrain_name)

    def _determine_dragon_targeting(
        self,
        dragons_present: List[Dict[str, Any]],
        marching_player: str,
        marching_army: Dict[str, Any],
        terrain_name: str,
    ):
        """Determine dragon targeting using the combat resolver."""
        print("[DragonCombatController] Determining dragon targeting")

        if not self.dragon_combat_resolver:
            print("[DragonCombatController] ERROR: Dragon combat resolver not set")
            return

        targeting_results = self.dragon_combat_resolver.determine_dragon_targeting(
            dragons_present, marching_player, marching_army, terrain_name
        )

        print(f"[DragonCombatController] Targeting determined for {len(targeting_results)} dragons")
        self.dragon_targeting_completed.emit(targeting_results)

    @Slot(dict, list)
    def handle_dragon_attack_resolution(self, targeting_results: dict, dragons_present: list):
        """Handle the resolution of dragon attacks."""
        print("[DragonCombatController] Resolving dragon attacks")

        if not self.dragon_combat_resolver:
            print("[DragonCombatController] ERROR: Dragon combat resolver not set")
            return

        attack_results = self.dragon_combat_resolver.resolve_dragon_attacks(targeting_results, dragons_present)

        print(f"[DragonCombatController] Resolved {len(attack_results)} dragon attacks")
        self.dragon_attacks_resolved.emit(attack_results)

        # Check if army response is needed
        army_under_attack = any(strict_get(attack, "target_type") == "army" for attack in attack_results)

        if army_under_attack:
            self._request_army_response(attack_results, targeting_results)

    def _request_army_response(self, attack_results: List[Dict[str, Any]], targeting_results: Dict[str, Any]):
        """Request army response to dragon attacks."""
        print("[DragonCombatController] Army under attack, requesting response")

        # Get the attacked army from targeting results
        attacked_army = None
        attacking_dragons = []

        for attack in attack_results:
            if strict_get(attack, "target_type") == "army":
                attacked_army = strict_get(attack, "target_data")
                attacking_dragons.append(attack)

        if not attacked_army or not attacking_dragons:
            print("[DragonCombatController] No valid army attack found")
            return

        # Calculate response options
        response_options = self.dragon_combat_resolver.calculate_army_response_options(attacked_army, attacking_dragons)

        response_data = {
            "army_data": attacked_army,
            "attacking_dragons": attacking_dragons,
            "response_options": response_options,
            "total_damage_incoming": sum(
                strict_get_optional(attack, "damage_dealt", 0) for attack in attacking_dragons
            ),
        }

        self.army_response_required.emit(response_data)

    @Slot(dict, list)
    def handle_army_response_submission(self, army_response_results: dict, attack_results: list):
        """Handle submission of army response results."""
        print("[DragonCombatController] Processing army response")

        # Extract damage dealt to dragons from army response
        dragon_damage = strict_get_optional(army_response_results, "dragon_damage", {})

        # Calculate dragon deaths
        dragon_deaths = self.dragon_combat_resolver.calculate_dragon_deaths(attack_results, dragon_damage)

        print(f"[DragonCombatController] {dragon_deaths['total_killed']} dragons killed")

        self._complete_dragon_combat(attack_results, army_response_results, dragon_deaths)

    @Slot(list)
    def handle_no_army_response(self, attack_results: list):
        """Handle case where no army response is needed."""
        print("[DragonCombatController] No army response needed, completing combat")

        # No army response, so no dragons killed by army
        dragon_deaths = {"dragons_killed": [], "total_killed": 0, "kill_details": []}

        self._complete_dragon_combat(attack_results, {}, dragon_deaths)

    def _complete_dragon_combat(
        self, attack_results: List[Dict[str, Any]], army_response_results: Dict[str, Any], dragon_deaths: Dict[str, Any]
    ):
        """Complete the dragon combat phase."""
        print("[DragonCombatController] Completing dragon combat")

        # Calculate total damage dealt to army
        total_army_damage = sum(
            strict_get_optional(attack, "damage_dealt", 0)
            for attack in attack_results
            if strict_get(attack, "target_type") == "army"
        )

        # Process breath effects if any
        breath_effects = []
        for attack in attack_results:
            breath_effects.extend(strict_get_optional(attack, "breath_effects", []))

        # Check for promotions (if dragons were killed)
        dragons_killed = dragon_deaths["total_killed"]
        promotion_data = {}
        if dragons_killed > 0:
            # Get the army that killed dragons (simplified - would need proper army tracking)
            for attack in attack_results:
                if strict_get(attack, "target_type") == "army":
                    army_data = strict_get(attack, "target_data")
                    promotion_data = self.dragon_combat_resolver.get_promotion_opportunities(dragons_killed, army_data)
                    break

        # Compile final results
        combat_results = {
            "completed": True,
            "attack_results": attack_results,
            "army_response": army_response_results,
            "dragon_deaths": dragon_deaths,
            "total_army_damage": total_army_damage,
            "breath_effects": breath_effects,
            "promotions_available": promotion_data.get("has_promotions", False),
            "promotion_data": promotion_data,
            "wings_flown": [attack for attack in attack_results if strict_get_optional(attack, "wings_rolled", False)],
            "treasure_effects": [
                attack for attack in attack_results if strict_get_optional(attack, "treasure_rolled", False)
            ],
        }

        # Apply results to game state through game engine
        self._apply_combat_results_to_game_state(combat_results)

        self.dragon_combat_completed.emit(combat_results)

    def _apply_combat_results_to_game_state(self, combat_results: Dict[str, Any]):
        """Apply dragon combat results to the game state."""
        print("[DragonCombatController] Applying combat results to game state")

        # Apply army damage
        total_damage = strict_get(combat_results, "total_army_damage")
        if total_damage > 0:
            # This would need to be coordinated with damage allocation system
            print(f"[DragonCombatController] Army took {total_damage} damage")

        # Remove killed dragons
        dragon_deaths = strict_get(combat_results, "dragon_deaths")
        for dragon_death in dragon_deaths.get("dragons_killed", []):
            dragon_id = strict_get(dragon_death, "dragon_id")
            print(f"[DragonCombatController] Removing killed dragon: {dragon_id}")
            # Would call game state manager to remove dragon

        # Process wings (dragons fly away)
        wings_flown = strict_get(combat_results, "wings_flown")
        for wing_attack in wings_flown:
            dragon_name = strict_get(wing_attack, "dragon_name")
            print(f"[DragonCombatController] Dragon {dragon_name} flew away")
            # Would call game state manager to return dragon to summoning pool

        # Process treasure effects
        treasure_effects = strict_get(combat_results, "treasure_effects")
        for _treasure_attack in treasure_effects:
            print("[DragonCombatController] Treasure effect available for army")
            # Would trigger promotion opportunities

    @Slot(str, list, str)
    def handle_breath_effects_processing(self, target_player: str, attack_results: list, target_army_id: str):
        """Handle processing of dragon breath effects."""
        print(f"[DragonCombatController] Processing breath effects for {target_player}")

        if not self.dragon_combat_resolver:
            print("[DragonCombatController] ERROR: Dragon combat resolver not set")
            return

        processed_effects = self.dragon_combat_resolver.process_breath_effects(
            attack_results, target_player, target_army_id
        )

        print(f"[DragonCombatController] Processed {len(processed_effects)} breath effects")

        # Breath effects are applied immediately, so we continue with combat resolution
        # This would typically be called between attack resolution and army response

    @Slot(str, str, list, dict, result=dict)
    def get_dragon_combat_preview(
        self, marching_player: str, terrain_name: str, dragons_present: list, marching_army: dict
    ) -> dict:
        """Get a preview of dragon combat without executing it."""
        if not dragons_present:
            return {"has_dragons": False, "combat_preview": None}

        preview = {
            "has_dragons": True,
            "dragon_count": len(dragons_present),
            "terrain": terrain_name,
            "marching_player": marching_player,
            "potential_threats": [],
            "army_at_risk": False,
        }

        # Analyze potential threats
        for dragon in dragons_present:
            dragon_owner = strict_get(dragon, "owner")
            dragon_name = strict_get(dragon, "name")

            threat_level = "low"
            if dragon_owner != marching_player:
                threat_level = "high"
                preview["army_at_risk"] = True

            preview["potential_threats"].append(
                {
                    "dragon_name": dragon_name,
                    "owner": dragon_owner,
                    "threat_level": threat_level,
                    "elements": strict_get_optional(dragon, "elements", []),
                }
            )

        return preview
