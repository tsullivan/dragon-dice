"""
Spell Effect Resolution Engine for Dragon Dice.

This module handles the execution of spell effects, including damage, modifiers,
movement, summoning, and other spell mechanics according to Dragon Dice rules.
"""

from typing import Any, Dict
from enum import Enum

from PySide6.QtCore import QObject, Signal

from models.spell_model import SpellModel, ALL_SPELLS
from utils.field_access import strict_get, strict_get_optional


class SpellTargetType(Enum):
    """Types of targets a spell can affect."""

    ARMY = "army"
    UNIT = "unit"
    TERRAIN = "terrain"
    DUA = "dua"
    BUA = "bua"
    SUMMONING_POOL = "summoning_pool"


class SpellEffectType(Enum):
    """Categories of spell effects for processing."""

    DAMAGE = "damage"
    MODIFIER = "modifier"
    MOVEMENT = "movement"
    SUMMONING = "summoning"
    RESURRECTION = "resurrection"
    PROMOTION = "promotion"
    TERRAIN_MANIPULATION = "terrain_manipulation"
    SPECIAL = "special"


class SpellResolver(QObject):
    """
    Handles the resolution of spell effects in Dragon Dice.

    This class processes spell casting, validates targets, applies effects,
    and manages spell durations according to official Dragon Dice rules.
    """

    spell_cast_completed = Signal(dict)  # Emits spell resolution results
    spell_effect_applied = Signal(str, dict)  # spell_name, effect_data
    spell_targeting_required = Signal(str, dict)  # spell_name, targeting_requirements

    def __init__(self, game_state_manager, effect_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.effect_manager = effect_manager

        # Spell effect type mappings
        self._effect_type_map = self._build_effect_type_map()

    def _build_effect_type_map(self) -> Dict[str, SpellEffectType]:
        """Build mapping of spell names to their primary effect types."""
        effect_map = {}

        # Damage spells
        damage_spells = ["HAILSTORM", "LIGHTNING_STRIKE", "FINGER_OF_DEATH", "FEARFUL_FLAMES", "FIREBOLT", "FIRESTORM"]
        for spell in damage_spells:
            effect_map[spell] = SpellEffectType.DAMAGE

        # Modifier spells (add/subtract results)
        modifier_spells = [
            "PALSY",
            "STONE_SKIN",
            "WIND_WALK",
            "WATERY_DOUBLE",
            "ASH_STORM",
            "BLIZZARD",
            "DECAY",
            "EVIL_EYE",
            "MAGIC_DRAIN",
            "HIGHER_GROUND",
            "DELUGE",
            "DANCING_LIGHTS",
            "WALL_OF_FOG",
            "TRANSMUTE_ROCK_TO_MUD",
        ]
        for spell in modifier_spells:
            effect_map[spell] = SpellEffectType.MODIFIER

        # Movement spells
        movement_spells = ["PATH", "RALLY", "SCENT_OF_FEAR", "MIRAGE"]
        for spell in movement_spells:
            effect_map[spell] = SpellEffectType.MOVEMENT

        # Summoning spells
        summoning_spells = ["SUMMON_DRAGON", "SUMMON_WHITE_DRAGON", "SUMMON_DRAGONKIN"]
        for spell in summoning_spells:
            effect_map[spell] = SpellEffectType.SUMMONING

        # Resurrection spells
        resurrection_spells = ["RESURRECT_DEAD", "EXHUME"]
        for spell in resurrection_spells:
            effect_map[spell] = SpellEffectType.RESURRECTION

        # Promotion spells
        promotion_spells = ["EVOLVE_DRAGONKIN", "RISE_OF_THE_ELDARIM"]
        for spell in promotion_spells:
            effect_map[spell] = SpellEffectType.PROMOTION

        # Terrain manipulation
        terrain_spells = ["FLASH_FLOOD", "TIDAL_WAVE"]
        for spell in terrain_spells:
            effect_map[spell] = SpellEffectType.TERRAIN_MANIPULATION

        # Special effects
        special_spells = [
            "WILDING",
            "BERSERKER_RAGE",
            "FLASHFIRE",
            "ACCELERATED_GROWTH",
            "WALL_OF_THORNS",
            "MIRE",
            "NECROMANTIC_WAVE",
            "OPEN_GRAVE",
            "SOILED_GROUND",
            "ESFAHS_GIFT",
            "RESTLESS_DEAD",
            "SWAMP_FEVER",
            "FIELDS_OF_ICE",
            "FIERY_WEAPON",
        ]
        for spell in special_spells:
            effect_map[spell] = SpellEffectType.SPECIAL

        return effect_map

    def cast_spell(
        self,
        spell_name: str,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Cast a spell and resolve its effects.

        Args:
            spell_name: Name of the spell to cast
            caster_player: Player casting the spell
            target_data: Dictionary containing target information
            magic_element_used: Element of magic used to cast the spell
            casting_count: Number of times spell is being cast (for cumulative effects)

        Returns:
            Dictionary containing spell resolution results
        """
        spell_key = spell_name.upper().replace(" ", "_")
        spell = strict_get(ALL_SPELLS, spell_key)

        if not spell:
            return {"success": False, "error": f"Unknown spell: {spell_name}"}

        # Validate casting requirements
        validation_result = self._validate_spell_casting(spell, caster_player, target_data, magic_element_used)
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Determine effect type and resolve
        effect_type = strict_get(self._effect_type_map, spell_key)

        try:
            resolution_result = self._resolve_spell_effect(
                spell, effect_type, caster_player, target_data, magic_element_used, casting_count
            )

            # Apply duration-based effects to effect manager
            if resolution_result.get("has_duration"):
                self._apply_duration_effect(spell, caster_player, resolution_result)

            self.spell_cast_completed.emit(
                {
                    "spell_name": spell.name,
                    "caster": caster_player,
                    "success": True,
                    "effect_type": effect_type.value,
                    "results": resolution_result,
                }
            )

            return {"success": True, "results": resolution_result}

        except Exception as e:
            error_msg = f"Failed to resolve {spell.name}: {str(e)}"
            return {"success": False, "error": error_msg}

    def _validate_spell_casting(
        self, spell: SpellModel, caster_player: str, target_data: Dict[str, Any], magic_element_used: str
    ) -> Dict[str, Any]:
        """Validate that a spell can be cast with given parameters."""

        # Validate element compatibility
        if spell.element == "ELEMENTAL":
            # Elemental spells can use any element
            pass
        elif spell.element != magic_element_used.upper():
            return {"valid": False, "error": f"{spell.name} requires {spell.element} magic, got {magic_element_used}"}

        # Validate target exists and is valid
        target_type = strict_get(target_data, "type")
        if not target_type:
            return {"valid": False, "error": "Missing target type"}

        # Additional validation based on spell requirements would go here
        # (checking if target armies exist, units are valid, etc.)

        return {"valid": True}

    def _resolve_spell_effect(
        self,
        spell: SpellModel,
        effect_type: SpellEffectType,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int,
    ) -> Dict[str, Any]:
        """Resolve the specific effect of a spell based on its type."""

        spell_key = spell.name.upper().replace(" ", "_")

        if effect_type == SpellEffectType.DAMAGE:
            return self._resolve_damage_effect(spell, caster_player, target_data, casting_count)
        elif effect_type == SpellEffectType.MODIFIER:
            return self._resolve_modifier_effect(spell, caster_player, target_data, casting_count)
        elif effect_type == SpellEffectType.MOVEMENT:
            return self._resolve_movement_effect(spell, caster_player, target_data, casting_count)
        elif effect_type == SpellEffectType.SUMMONING:
            return self._resolve_summoning_effect(spell, caster_player, target_data, magic_element_used, casting_count)
        elif effect_type == SpellEffectType.RESURRECTION:
            return self._resolve_resurrection_effect(
                spell, caster_player, target_data, magic_element_used, casting_count
            )
        elif effect_type == SpellEffectType.PROMOTION:
            return self._resolve_promotion_effect(spell, caster_player, target_data, magic_element_used, casting_count)
        elif effect_type == SpellEffectType.TERRAIN_MANIPULATION:
            return self._resolve_terrain_effect(spell, caster_player, target_data, casting_count)
        else:  # SpellEffectType.SPECIAL
            return self._resolve_special_effect(spell, caster_player, target_data, magic_element_used, casting_count)

    def _resolve_damage_effect(
        self, spell: SpellModel, caster_player: str, target_data: Dict[str, Any], casting_count: int
    ) -> Dict[str, Any]:
        """Resolve damage-dealing spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        base_damage = 1  # Default damage
        save_allowed = True

        # Spell-specific damage rules
        if spell_key == "HAILSTORM":
            base_damage = 1 * casting_count
        elif spell_key == "LIGHTNING_STRIKE":
            base_damage = 1  # Always kills if save fails
            # Lightning Strike has special rule: max one per magic action per unit
        elif spell_key == "FINGER_OF_DEATH":
            base_damage = 1 * casting_count
            save_allowed = False  # "no save possible"
        elif spell_key == "FIREBOLT":
            base_damage = 1 * casting_count
        elif spell_key == "FIRESTORM":
            base_damage = 2 * casting_count
        elif spell_key == "FEARFUL_FLAMES":
            base_damage = 1 * casting_count
            # Special: if save succeeds, second save or flee to reserves

        return {
            "effect_type": "damage",
            "damage_amount": base_damage,
            "save_allowed": save_allowed,
            "target_data": target_data,
            "special_rules": self._get_damage_special_rules(spell_key),
        }

    def _resolve_modifier_effect(
        self, spell: SpellModel, caster_player: str, target_data: Dict[str, Any], casting_count: int
    ) -> Dict[str, Any]:
        """Resolve result modifier spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        modifier_data = self._get_modifier_values(spell_key, casting_count)

        return {
            "effect_type": "modifier",
            "modifier_type": modifier_data["type"],  # "add" or "subtract"
            "result_types": modifier_data["result_types"],  # ["melee", "save", etc.]
            "amount": modifier_data["amount"],
            "target_data": target_data,
            "has_duration": True,
            "duration": "until_next_turn",
        }

    def _resolve_movement_effect(
        self, spell: SpellModel, caster_player: str, target_data: Dict[str, Any], casting_count: int
    ) -> Dict[str, Any]:
        """Resolve unit movement spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        if spell_key == "PATH":
            return {
                "effect_type": "move_unit",
                "source_terrain": strict_get(target_data, "source_terrain"),
                "destination_terrain": strict_get(target_data, "destination_terrain"),
                "unit_data": strict_get(target_data, "unit"),
            }
        elif spell_key == "RALLY":
            return {
                "effect_type": "move_multiple_units",
                "max_units": 3,
                "unit_restriction": "Amazons",
                "destination_requirement": "terrain_with_amazons",
            }
        elif spell_key == "SCENT_OF_FEAR":
            return {
                "effect_type": "force_to_reserves",
                "max_health_worth": 3 * casting_count,
                "target_data": target_data,
            }
        elif spell_key == "MIRAGE":
            return {
                "effect_type": "save_or_move_to_reserves",
                "max_health_worth": 5 * casting_count,
                "target_data": target_data,
            }

        return {"effect_type": "movement", "target_data": target_data}

    def _resolve_summoning_effect(
        self,
        spell: SpellModel,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int,
    ) -> Dict[str, Any]:
        """Resolve summoning spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        if spell_key == "SUMMON_DRAGON":
            return {
                "effect_type": "summon_dragon",
                "dragon_element": magic_element_used,
                "target_terrain": strict_get(target_data, "terrain"),
                "allow_ivory": True,
            }
        elif spell_key == "SUMMON_WHITE_DRAGON":
            return {
                "effect_type": "summon_white_dragon",
                "target_terrain": strict_get(target_data, "terrain"),
                "cost_elements": strict_get_optional(target_data, "elements_used", []),
            }
        elif spell_key == "SUMMON_DRAGONKIN":
            return {
                "effect_type": "summon_dragonkin",
                "element_required": magic_element_used,
                "health_worth": 1 * casting_count,
                "target_army": strict_get(target_data, "army"),
            }

        return {"effect_type": "summoning", "target_data": target_data}

    def _resolve_resurrection_effect(
        self,
        spell: SpellModel,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int,
    ) -> Dict[str, Any]:
        """Resolve resurrection spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        if spell_key == "RESURRECT_DEAD":
            return {
                "effect_type": "resurrect_from_dua",
                "element_required": magic_element_used,
                "health_worth": 1 * casting_count,
                "target_army": strict_get(target_data, "army"),
            }
        elif spell_key == "EXHUME":
            return {
                "effect_type": "force_burial_and_resurrect",
                "max_target_health": 3 * casting_count,
                "target_dua": strict_get(target_data, "opponent_dua"),
                "resurrect_to_army": strict_get(target_data, "army"),
            }

        return {"effect_type": "resurrection", "target_data": target_data}

    def _resolve_promotion_effect(
        self,
        spell: SpellModel,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int,
    ) -> Dict[str, Any]:
        """Resolve promotion spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        promotion_amount = 1 * casting_count

        if spell_key == "EVOLVE_DRAGONKIN":
            return {
                "effect_type": "promote_dragonkin",
                "element_required": magic_element_used,
                "promotion_amount": promotion_amount,
                "target_unit": strict_get(target_data, "unit"),
            }
        elif spell_key == "RISE_OF_THE_ELDARIM":
            return {
                "effect_type": "promote_eldarim",
                "element_required": magic_element_used,
                "promotion_amount": promotion_amount,
                "target_unit": strict_get(target_data, "unit"),
            }

        return {"effect_type": "promotion", "target_data": target_data}

    def _resolve_terrain_effect(
        self, spell: SpellModel, caster_player: str, target_data: Dict[str, Any], casting_count: int
    ) -> Dict[str, Any]:
        """Resolve terrain manipulation spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        if spell_key == "FLASH_FLOOD":
            return {
                "effect_type": "reduce_terrain",
                "steps": 1,
                "counter_requirement": 6,  # maneuver results needed to prevent
                "max_per_turn": 1,  # terrain reduction limit
                "target_terrain": strict_get(target_data, "terrain"),
            }
        elif spell_key == "TIDAL_WAVE":
            return {
                "effect_type": "damage_and_reduce_terrain",
                "damage_amount": 4 * casting_count,
                "special_save_type": "combination_save_maneuver",
                "reduce_counter_requirement": 4,
                "max_per_turn": 1,
                "target_terrain": strict_get(target_data, "terrain"),
            }

        return {"effect_type": "terrain_manipulation", "target_data": target_data}

    def _resolve_special_effect(
        self,
        spell: SpellModel,
        caster_player: str,
        target_data: Dict[str, Any],
        magic_element_used: str,
        casting_count: int,
    ) -> Dict[str, Any]:
        """Resolve special/complex spell effects."""
        spell_key = spell.name.upper().replace(" ", "_")

        # Each special spell needs individual handling
        if spell_key == "OPEN_GRAVE":
            return {
                "effect_type": "redirect_death_to_reserves",
                "target_army": strict_get(target_data, "army"),
                "has_duration": True,
                "duration": "until_next_turn",
                "conditions": "save_roll_death_only",
            }
        elif spell_key == "SOILED_GROUND":
            return {
                "effect_type": "death_burial_check",
                "target_terrain": strict_get(target_data, "terrain"),
                "has_duration": True,
                "duration": "until_next_turn",
            }
        # Add more special cases as needed

        return {
            "effect_type": "special",
            "spell_name": spell.name,
            "target_data": target_data,
            "requires_manual_resolution": True,
        }

    def _get_modifier_values(self, spell_key: str, casting_count: int) -> Dict[str, Any]:
        """Get modifier values for result-modifying spells."""
        modifier_map = {
            "PALSY": {"type": "subtract", "result_types": ["all_non_maneuver"], "amount": 1},
            "STONE_SKIN": {"type": "add", "result_types": ["save"], "amount": 1},
            "WIND_WALK": {"type": "add", "result_types": ["maneuver"], "amount": 4},
            "WATERY_DOUBLE": {"type": "add", "result_types": ["save"], "amount": 1},
            "ASH_STORM": {"type": "subtract", "result_types": ["all"], "amount": 1},
            "BLIZZARD": {"type": "subtract", "result_types": ["melee"], "amount": 3},
            "DECAY": {"type": "subtract", "result_types": ["melee"], "amount": 2},
            "EVIL_EYE": {"type": "subtract", "result_types": ["save"], "amount": 2},
            "MAGIC_DRAIN": {"type": "subtract", "result_types": ["magic"], "amount": 2},
            "HIGHER_GROUND": {"type": "subtract", "result_types": ["melee"], "amount": 5},
            "DELUGE": {"type": "subtract", "result_types": ["maneuver", "missile"], "amount": 3},
            "DANCING_LIGHTS": {"type": "subtract", "result_types": ["melee"], "amount": 6},
            "WALL_OF_FOG": {"type": "subtract", "result_types": ["missile"], "amount": 6},
            "TRANSMUTE_ROCK_TO_MUD": {"type": "subtract", "result_types": ["maneuver"], "amount": 6},
        }

        base_modifier = modifier_map.get(spell_key, {"type": "add", "result_types": ["all"], "amount": 1})

        # Apply casting count multiplier for cumulative spells
        cumulative_spells = ["WIND_WALK", "PALSY"]  # Spells that stack with multiple castings
        if spell_key in cumulative_spells:
            base_modifier["amount"] *= casting_count

        return base_modifier

    def _get_damage_special_rules(self, spell_key: str) -> Dict[str, Any]:
        """Get special rules for damage spells."""
        special_rules = {}

        if spell_key == "LIGHTNING_STRIKE":
            special_rules["max_per_target"] = 1  # One Lightning Strike per unit per magic action
        elif spell_key == "FEARFUL_FLAMES":
            special_rules["second_save_or_flee"] = True

        return special_rules

    def _apply_duration_effect(self, spell: SpellModel, caster_player: str, resolution_result: Dict[str, Any]) -> None:
        """Apply duration-based spell effects to the effect manager."""
        effect_data = {
            "spell_name": spell.name,
            "caster": caster_player,
            "effect_type": strict_get(resolution_result, "effect_type"),
            "modifier_data": resolution_result,
            "duration": strict_get(resolution_result, "duration"),
        }

        # Add to effect manager for duration tracking
        self.effect_manager.add_spell_effect(caster_player, effect_data)

    def get_spell_requirements(self, spell_name: str) -> Dict[str, Any]:
        """Get targeting and casting requirements for a spell."""
        spell_key = spell_name.upper().replace(" ", "_")
        spell = strict_get(ALL_SPELLS, spell_key)

        if not spell:
            return {"error": f"Unknown spell: {spell_name}"}

        # Determine target requirements based on spell effect
        target_requirements = self._analyze_spell_targeting(spell)

        return {
            "spell_name": spell.name,
            "cost": spell.cost,
            "element": spell.element,
            "species_restriction": spell.species,
            "can_cast_from_reserves": spell.reserves,
            "is_cantrip": spell.cantrip,
            "target_requirements": target_requirements,
        }

    def _analyze_spell_targeting(self, spell: SpellModel) -> Dict[str, Any]:
        """Analyze spell effect text to determine targeting requirements."""
        effect_lower = spell.effect.lower()

        requirements = {"target_types": [], "restrictions": [], "selection_method": "single"}

        # Analyze effect text for targeting patterns
        if "target any opposing army" in effect_lower:
            requirements["target_types"].append("opposing_army")
        elif "target any army" in effect_lower:
            requirements["target_types"].append("any_army")
        elif "target any opposing unit" in effect_lower:
            requirements["target_types"].append("opposing_unit")
        elif "target any terrain" in effect_lower:
            requirements["target_types"].append("terrain")
        elif "target your dua" in effect_lower:
            requirements["target_types"].append("own_dua")

        # Check for health-worth limitations
        if "health-worth" in effect_lower:
            requirements["health_worth_selection"] = True

        # Check for multiple target selection
        if "up to" in effect_lower:
            requirements["selection_method"] = "multiple_up_to_limit"

        return requirements
