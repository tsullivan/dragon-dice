"""
Core Engine for Dragon Dice - Pure Business Logic

This module contains the core game rules, validation logic, and business rule
implementations without any UI coordination or signal emission concerns.
"""

from typing import Any, Dict, List, Optional

from models.unit_model import UnitModel
from utils.field_access import strict_get, strict_get_optional, strict_get_with_fallback


class CoreEngine:
    """
    Pure game rules engine for Dragon Dice.

    Contains business logic, rule validation, and data transformation
    without any UI coordination or Qt signal dependencies.
    """

    def __init__(self, managers: Dict[str, Any]):
        """Initialize with pre-configured managers."""
        self.game_state_manager = managers["game_state_manager"]
        self.bua_manager = managers["bua_manager"]
        self.dua_manager = managers["dua_manager"]
        self.reserves_manager = managers["reserves_manager"]
        self.summoning_pool_manager = managers["summoning_pool_manager"]
        self.effect_manager = managers["effect_manager"]
        self.turn_manager = managers["turn_manager"]
        self.action_resolver = managers["action_resolver"]
        self.promotion_manager = managers["promotion_manager"]
        self.eighth_face_manager = managers["eighth_face_manager"]
        self.dragon_attack_manager = managers["dragon_attack_manager"]
        self.minor_terrain_manager = managers["minor_terrain_manager"]
        self.species_ability_manager = managers["species_ability_manager"]
        self.spell_resolver = managers.get("spell_resolver")

    # =============================================================================
    # RULE ENFORCEMENT & VALIDATION
    # =============================================================================

    def check_death_magic_immunity(self, target_unit: UnitModel, magic_element: str) -> bool:
        """Check if a unit has death magic immunity against specific element."""
        if not hasattr(target_unit, "species") or not hasattr(target_unit.species, "abilities"):
            return False

        abilities = target_unit.species.abilities
        for ability in abilities:
            if (
                hasattr(ability, "name")
                and ability.name == "Death Magic Immunity"
                and hasattr(ability, "elements")
                and magic_element.upper() in [e.upper() for e in ability.elements]
            ):
                return True
        return False

    def extract_terrain_type_from_location(self, location: str) -> str:
        """Extract the base terrain type from a location string."""
        if not location or not isinstance(location, str):
            return ""

        # Handle formatted locations like "Forest (Face 3)"
        if "(" in location:
            location = location.split("(")[0].strip()

        # Common terrain type extractions
        terrain_mappings = {
            "forest": "Forest",
            "swampland": "Swampland",
            "frozen wastes": "Frozen Wastes",
            "highlands": "Highlands",
            "coastland": "Coastland",
            "badlands": "Badlands",
            "city": "City",
            "tower": "Tower",
            "temple": "Temple",
            "standing stones": "Standing Stones",
            "vortex": "Vortex",
        }

        location_lower = location.lower()
        for key, value in terrain_mappings.items():
            if key in location_lower:
                return value

        return location

    def is_terrain_eighth_face_controlled(self, terrain_location: str, player_name: str) -> bool:
        """Check if player controls the eighth face at given terrain."""
        terrain_controller = self.game_state_manager.get_terrain_controller(terrain_location)
        return terrain_controller == player_name

    def _get_terrain_face_description(self, terrain_type: str, face_number: int) -> str:
        """Get description for terrain face based on type and number."""
        # This would be replaced with actual terrain face data lookup
        face_descriptions = {
            "Forest": {
                8: "Eighth Face - Natural Growth",
                7: "Seventh Face - Ancient Grove",
                6: "Sixth Face - Dense Canopy",
            },
            "City": {
                8: "Eighth Face - Recruitment",
                7: "Seventh Face - Fortifications",
                6: "Sixth Face - Trade Routes",
            },
        }

        return face_descriptions.get(terrain_type, {}).get(face_number, f"Face {face_number}")

    def _get_default_species(self, player_name: str) -> List[str]:
        """Get default species available to a player."""
        # This would typically come from player setup data
        return ["Human", "Dwarf", "Elf"]  # Placeholder

    # =============================================================================
    # BUSINESS LOGIC CALCULATIONS
    # =============================================================================

    def find_promotion_opportunities(self, player_name: str, trigger: str) -> Dict[str, Any]:
        """Find all promotion opportunities for a player based on trigger."""
        if not self.promotion_manager:
            return {"opportunities": [], "trigger": trigger, "player": player_name}

        opportunities = self.promotion_manager.find_promotion_opportunities(player_name, trigger)

        return {
            "opportunities": [self._promotion_option_to_dict(opp) for opp in opportunities],
            "trigger": trigger,
            "player": player_name,
            "total_opportunities": len(opportunities),
        }

    def _promotion_option_to_dict(self, promotion_option: Any) -> Dict[str, Any]:
        """Convert promotion option object to dictionary."""
        return {
            "unit_id": strict_get_with_fallback(promotion_option, "unit_id", "id", "unknown"),
            "unit_name": strict_get_optional(promotion_option, "unit_name", "Unknown Unit"),
            "current_health": strict_get_optional(promotion_option, "current_health", 1),
            "promotion_target": strict_get_optional(promotion_option, "promotion_target", "unknown"),
            "promotion_cost": strict_get_optional(promotion_option, "promotion_cost", 1),
            "can_promote": strict_get_optional(promotion_option, "can_promote", False),
        }

    def execute_single_promotion(self, player_name: str, unit_id: str, target_health: int) -> Dict[str, Any]:
        """Execute a single unit promotion."""
        if not self.promotion_manager:
            return {"success": False, "error": "Promotion manager not available"}

        result = self.promotion_manager.execute_promotion(player_name, unit_id, target_health)

        return {
            "success": result.get("success", False),
            "unit_id": unit_id,
            "target_health": target_health,
            "player": player_name,
            "details": result,
        }

    def execute_mass_promotion(self, player_name: str, promotions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple promotions simultaneously."""
        results = []
        successful_promotions = 0

        for promotion_data in promotions:
            unit_id = strict_get(promotion_data, "unit_id")
            target_health = strict_get(promotion_data, "target_health")

            result = self.execute_single_promotion(player_name, unit_id, target_health)
            results.append(result)

            if result.get("success"):
                successful_promotions += 1

        return {
            "total_attempted": len(promotions),
            "successful_promotions": successful_promotions,
            "results": results,
            "player": player_name,
        }

    def check_promotion_after_dragon_kill(self, player_name: str, dragon_health: int) -> Dict[str, Any]:
        """Check for promotion opportunities after killing a dragon."""
        trigger = f"dragon_kill_{dragon_health}"
        return self.find_promotion_opportunities(player_name, trigger)

    # =============================================================================
    # DATA ACCESS & TRANSFORMATION
    # =============================================================================

    def get_all_player_summary_data(self) -> Dict[str, Any]:
        """Get comprehensive summary data for all players."""
        player_summaries = {}

        for player_name in self.turn_manager.get_all_players():
            player_summaries[player_name] = {
                "armies": self.get_player_armies_summary(player_name),
                "reserves": self.get_player_reserve_units(player_name),
                "dua": self.get_player_dua_units(player_name),
                "bua": self.get_player_bua_units(player_name),
                "active_effects": self.effect_manager.get_active_effects_for_player(player_name),
                "promotion_opportunities": self.find_promotion_opportunities(player_name, "general"),
            }

        return player_summaries

    def get_relevant_terrains_info(self, player_names: List[str]) -> Dict[str, Any]:
        """Get terrain information relevant to given players."""
        terrains_info = {}
        all_terrain_data = self.game_state_manager.get_all_terrain_data()

        for terrain_name, terrain_data in all_terrain_data.items():
            armies = strict_get_optional(terrain_data, "armies", {})

            # Include terrain if any of the specified players have armies there
            relevant = False
            for player_name in player_names:
                if player_name in armies and armies[player_name]:
                    relevant = True
                    break

            if relevant:
                terrains_info[terrain_name] = terrain_data

        return terrains_info

    def get_all_players_data(self) -> Dict[str, Any]:
        """Get all player data from game state manager."""
        return self.game_state_manager.get_all_players_data()

    def get_all_terrain_data(self) -> Dict[str, Any]:
        """Get all terrain data from game state manager."""
        return self.game_state_manager.get_all_terrain_data()

    def get_available_units_for_damage(self, player_name: str, army_identifier: str) -> List[Dict[str, Any]]:
        """Get units available for damage allocation."""
        army_units = self.game_state_manager.get_army_units(player_name, army_identifier)

        available_units = []
        for unit in army_units:
            unit_health = strict_get(unit, "health")
            if unit_health > 0:  # Only living units can take damage
                available_units.append(
                    {
                        "name": strict_get(unit, "name"),
                        "health": unit_health,
                        "max_health": strict_get_optional(unit, "max_health", unit_health),
                        "unit_id": strict_get_with_fallback(unit, "id", "name", unit),
                    }
                )

        return available_units

    def get_player_armies_summary(self, player_name: str) -> Dict[str, Any]:
        """Get summary of all armies for a player."""
        return self.game_state_manager.get_player_armies_summary(player_name)

    def get_units_as_dua_objects(self, units_data: List[Dict[str, Any]]) -> List[Any]:
        """Convert unit dictionaries to DUA unit objects."""
        dua_units = []
        for unit_data in units_data:
            dua_unit = self.dict_to_dua_unit(unit_data)
            if dua_unit:
                dua_units.append(dua_unit)
        return dua_units

    def get_units_as_reserve_objects(self, units_data: List[Dict[str, Any]]) -> List[Any]:
        """Convert unit dictionaries to reserve unit objects."""
        reserve_units = []
        for unit_data in units_data:
            reserve_unit = self.dict_to_reserve_unit(unit_data)
            if reserve_unit:
                reserve_units.append(reserve_unit)
        return reserve_units

    def dict_to_dua_unit(self, unit_dict: Dict[str, Any]) -> Optional[Any]:
        """Convert dictionary to DUA unit object."""
        try:
            from models.game_state.dua_manager import DUAUnit

            return DUAUnit(
                name=strict_get(unit_dict, "name"),
                species=strict_get(unit_dict, "species", "Unknown"),
                health=strict_get(unit_dict, "health"),
                elements=strict_get_optional(unit_dict, "elements", []),
                original_owner=strict_get_optional(unit_dict, "original_owner", "Unknown"),
            )
        except Exception as e:
            print(f"CoreEngine: Failed to convert dict to DUA unit: {e}")
            return None

    def dict_to_reserve_unit(self, unit_dict: Dict[str, Any]) -> Optional[Any]:
        """Convert dictionary to reserve unit object."""
        try:
            from models.game_state.reserves_manager import ReserveUnit

            return ReserveUnit(
                name=strict_get(unit_dict, "name"),
                species=strict_get(unit_dict, "species", "Unknown"),
                health=strict_get(unit_dict, "health"),
                elements=strict_get_optional(unit_dict, "elements", []),
            )
        except Exception as e:
            print(f"CoreEngine: Failed to convert dict to reserve unit: {e}")
            return None

    def dua_unit_to_dict(self, dua_unit: Any) -> Dict[str, Any]:
        """Convert DUA unit object to dictionary."""
        return {
            "name": strict_get(dua_unit, "name"),
            "species": strict_get(dua_unit, "species"),
            "health": strict_get(dua_unit, "health"),
            "elements": strict_get_optional(dua_unit, "elements", []),
            "original_owner": strict_get_optional(dua_unit, "original_owner", "Unknown"),
        }

    def reserve_unit_to_dict(self, reserve_unit: Any) -> Dict[str, Any]:
        """Convert reserve unit object to dictionary."""
        return {
            "name": strict_get(reserve_unit, "name"),
            "species": strict_get(reserve_unit, "species"),
            "health": strict_get(reserve_unit, "health"),
            "elements": strict_get_optional(reserve_unit, "elements", []),
        }

    # =============================================================================
    # PURE GAME RULE PROCESSING
    # =============================================================================

    def process_spell_effects(self, spell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process spell effects using pure business logic."""
        if not self.spell_resolver:
            return {"success": False, "error": "Spell resolver not available"}

        spell_name = strict_get(spell_data, "spell_name")
        caster = strict_get(spell_data, "caster")
        target_data = strict_get(spell_data, "target_data")
        element_used = strict_get(spell_data, "element_used")
        casting_count = strict_get_optional(spell_data, "casting_count", 1)

        return self.spell_resolver.cast_spell(spell_name, caster, target_data, element_used, casting_count)

    def _process_single_spell(self, spell_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual spell result."""
        effect_type = strict_get_optional(spell_result, "effect_type", "unknown")

        if effect_type == "summon_dragon":
            return self._process_dragon_summon_spell(spell_result)
        if effect_type == "summon_dragonkin":
            return self._process_dragonkin_summon_spell(spell_result)
        return {"processed": True, "effect_type": effect_type, "details": spell_result}

    def _process_dragon_summon_spell(self, spell_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process dragon summoning spell effects."""
        dragon_element = strict_get_optional(spell_result, "dragon_element", "FIRE")
        target_terrain = strict_get_optional(spell_result, "target_terrain", "")

        if not target_terrain:
            return {"success": False, "error": "No target terrain specified for dragon summon"}

        # Apply dragon summoning logic through summoning pool manager
        summon_result = self.summoning_pool_manager.summon_dragon(dragon_element, target_terrain)

        return {
            "processed": True,
            "effect_type": "dragon_summoned",
            "dragon_element": dragon_element,
            "target_terrain": target_terrain,
            "summon_result": summon_result,
        }

    def _process_dragonkin_summon_spell(self, spell_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process dragonkin summoning spell effects."""
        element_required = strict_get_optional(spell_result, "element_required", "FIRE")
        health_worth = strict_get_optional(spell_result, "health_worth", 1)
        target_army = strict_get_optional(spell_result, "target_army", "")

        if not target_army:
            return {"success": False, "error": "No target army specified for dragonkin summon"}

        # Apply dragonkin summoning logic
        summon_result = self.summoning_pool_manager.summon_dragonkin(element_required, health_worth, target_army)

        return {
            "processed": True,
            "effect_type": "dragonkin_summoned",
            "element": element_required,
            "health_worth": health_worth,
            "target_army": target_army,
            "summon_result": summon_result,
        }

    def add_promotion_trigger_to_spell_effect(self, spell_effect: Dict[str, Any], trigger: str) -> Dict[str, Any]:
        """Add promotion trigger information to spell effect."""
        enhanced_effect = spell_effect.copy()
        enhanced_effect["promotion_trigger"] = trigger
        enhanced_effect["check_for_promotions"] = True
        return enhanced_effect

    # =============================================================================
    # STATE MANAGEMENT (without UI signals)
    # =============================================================================

    def add_unit_to_dua(self, player_name: str, unit_data: Dict[str, Any]) -> bool:
        """Add unit to dead units area."""
        dua_unit = self.dict_to_dua_unit(unit_data)
        if dua_unit:
            self.dua_manager.add_unit_to_dua(dua_unit)
            return True
        return False

    def add_unit_to_reserves(self, player_name: str, unit_data: Dict[str, Any]) -> bool:
        """Add unit to reserves."""
        reserve_unit = self.dict_to_reserve_unit(unit_data)
        if reserve_unit:
            self.reserves_manager.add_unit_to_reserves(player_name, reserve_unit)
            return True
        return False

    def bury_unit_in_bua(self, player_name: str, unit_data: Dict[str, Any]) -> bool:
        """Bury unit in buried units area."""
        self.bua_manager.bury_unit(player_name, unit_data)
        return True

    def get_player_dua_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get DUA units for player as dictionaries."""
        dua_units = self.dua_manager.get_dua_units_for_player(player_name)
        return [self.dua_unit_to_dict(unit) for unit in dua_units]

    def get_player_reserve_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get reserve units for player as dictionaries."""
        reserve_units = self.reserves_manager.get_player_reserves(player_name)
        return [self.reserve_unit_to_dict(unit) for unit in reserve_units]

    def get_player_bua_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get BUA units for player."""
        return self.bua_manager.get_buried_units_for_player(player_name)

    # =============================================================================
    # AUTO ALLOCATION LOGIC
    # =============================================================================

    def auto_allocate_damage(self, player_name: str, army_identifier: str, total_damage: int) -> Dict[str, Any]:
        """Automatically allocate damage to units using business rules."""
        available_units = self.get_available_units_for_damage(player_name, army_identifier)

        if not available_units:
            return {"success": False, "error": "No units available for damage allocation"}

        allocation_plan = []
        remaining_damage = total_damage

        # Allocation strategy: spread damage evenly, prioritize lower health units
        available_units.sort(key=lambda u: u["health"])

        while remaining_damage > 0 and available_units:
            for unit in available_units[:]:  # Copy list to allow modification
                if remaining_damage <= 0:
                    break

                damage_to_apply = min(1, remaining_damage, unit["health"])
                unit["health"] -= damage_to_apply
                remaining_damage -= damage_to_apply

                allocation_plan.append(
                    {"unit_id": unit["unit_id"], "damage_applied": damage_to_apply, "remaining_health": unit["health"]}
                )

                if unit["health"] <= 0:
                    available_units.remove(unit)

        return {
            "success": True,
            "total_damage": total_damage,
            "damage_allocated": total_damage - remaining_damage,
            "damage_remaining": remaining_damage,
            "allocation_plan": allocation_plan,
        }

    def allocate_damage_to_units(
        self, player_name: str, army_identifier: str, allocations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply specific damage allocations to units."""
        results = []
        total_applied = 0

        for allocation in allocations:
            unit_name = strict_get(allocation, "unit_name")
            new_health = strict_get(allocation, "new_health")

            # Apply the damage through game state manager
            apply_result = self.game_state_manager.apply_damage_to_units(
                player_name,
                army_identifier,
                1,  # Applying 1 damage at a time for control
            )

            results.append(
                {"unit_name": unit_name, "new_health": new_health, "applied": apply_result.get("success", False)}
            )

            if apply_result.get("success", False):
                total_applied += 1

        return {
            "success": len(results) > 0,
            "total_allocations": len(allocations),
            "successful_applications": total_applied,
            "results": results,
        }
