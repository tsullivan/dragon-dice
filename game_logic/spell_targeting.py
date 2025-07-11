"""
Spell Targeting System for Dragon Dice.

This module handles spell targeting logic including:
- Army targeting
- Unit targeting
- Terrain targeting
- DUA (Dead Units Area) targeting
- BUA (Buried Units Area) targeting
- Summoning Pool restrictions (spells cannot target the Summoning Pool)
"""

from enum import Enum
from typing import Any, Dict, List, Tuple

from models.spell_model import SpellModel


class TargetType(Enum):
    """Types of spell targets."""

    ARMY = "army"
    UNIT = "unit"
    TERRAIN = "terrain"
    DUA = "dua"
    BUA = "bua"
    SUMMONING_POOL = "summoning_pool"  # NOT VALID - spells cannot target this


class SpellTargetingManager:
    """Manages spell targeting logic and validation."""

    def __init__(self, dua_manager, bua_manager, summoning_pool_manager):
        self.dua_manager = dua_manager
        self.bua_manager = bua_manager
        self.summoning_pool_manager = summoning_pool_manager

    def get_valid_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all valid targets for a spell."""
        valid_targets: Dict[str, List[Dict[str, Any]]] = {
            "armies": [],
            "units": [],
            "terrains": [],
            "dua_units": [],
            "bua_units": [],
        }

        # Parse spell effect to determine target types
        target_types = self._parse_spell_target_types(spell)

        for target_type in target_types:
            if target_type == TargetType.ARMY:
                valid_targets["armies"] = self._get_valid_army_targets(spell, caster_player, game_state)
            elif target_type == TargetType.UNIT:
                valid_targets["units"] = self._get_valid_unit_targets(spell, caster_player, game_state)
            elif target_type == TargetType.TERRAIN:
                valid_targets["terrains"] = self._get_valid_terrain_targets(spell, caster_player, game_state)
            elif target_type == TargetType.DUA:
                valid_targets["dua_units"] = self._get_valid_dua_targets(spell, caster_player, game_state)
            elif target_type == TargetType.BUA:
                valid_targets["bua_units"] = self._get_valid_bua_targets(spell, caster_player, game_state)
            elif target_type == TargetType.SUMMONING_POOL:
                # Dragon summoning spells use summoning pool as source, not target
                valid_targets["summoning_pool_sources"] = self._get_valid_summoning_pool_sources(
                    spell, caster_player, game_state
                )

        return valid_targets

    def _parse_spell_target_types(self, spell: SpellModel) -> List[TargetType]:
        """Parse spell effect text to determine what types of targets are valid."""
        target_types = []
        effect_lower = spell.effect.lower()

        # Check for army targeting
        if "army" in effect_lower or "casting army" in effect_lower:
            target_types.append(TargetType.ARMY)

        # Check for unit targeting
        if "unit" in effect_lower or "target one" in effect_lower or "target any" in effect_lower:
            target_types.append(TargetType.UNIT)

        # Check for terrain targeting
        if "terrain" in effect_lower:
            target_types.append(TargetType.TERRAIN)

        # Check for DUA targeting
        if "dua" in effect_lower or "dead units area" in effect_lower or "resurrect" in effect_lower:
            target_types.append(TargetType.DUA)

        # Check for BUA targeting
        if "bua" in effect_lower or "buried units area" in effect_lower or "buried" in effect_lower:
            target_types.append(TargetType.BUA)

        # Check for dragon summoning spells (use summoning pool as source)
        if "summon" in effect_lower and ("dragon" in effect_lower or "dragonkin" in effect_lower):
            target_types.append(TargetType.SUMMONING_POOL)
        elif "summoning pool" in effect_lower:
            # Other summoning pool references (like Esfah's Gift)
            target_types.append(TargetType.SUMMONING_POOL)

        return target_types

    def _get_valid_army_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid army targets for a spell."""
        valid_armies = []

        # Get all armies from game state
        all_players_data = game_state.get("all_players_data", {})

        for player_name, player_data in all_players_data.items():
            armies = player_data.get("armies", {})

            for army_id, army_data in armies.items():
                army_info = {
                    "player": player_name,
                    "army_id": army_id,
                    "army_data": army_data,
                    "location": army_data.get("location", "Unknown"),
                    "units": army_data.get("units", []),
                    "is_own_army": player_name == caster_player,
                }

                # Apply spell-specific targeting rules
                if self._is_valid_army_target(spell, army_info, caster_player):
                    valid_armies.append(army_info)

        return valid_armies

    def _get_valid_unit_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid unit targets for a spell."""
        valid_units = []

        # Get all units from all armies
        all_players_data = game_state.get("all_players_data", {})

        for player_name, player_data in all_players_data.items():
            armies = player_data.get("armies", {})

            for army_id, army_data in armies.items():
                units = army_data.get("units", [])

                for unit in units:
                    unit_info = {
                        "player": player_name,
                        "army_id": army_id,
                        "unit_data": unit,
                        "location": army_data.get("location", "Unknown"),
                        "is_own_unit": player_name == caster_player,
                    }

                    # Apply spell-specific targeting rules
                    if self._is_valid_unit_target(spell, unit_info, caster_player):
                        valid_units.append(unit_info)

        return valid_units

    def _get_valid_terrain_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid terrain targets for a spell."""
        valid_terrains = []

        terrain_data = game_state.get("terrain_data", {})

        for terrain_id, terrain_info in terrain_data.items():
            terrain_target = {
                "terrain_id": terrain_id,
                "terrain_data": terrain_info,
                "name": terrain_info.get("name", "Unknown Terrain"),
                "elements": terrain_info.get("elements", []),
                "controller": terrain_info.get("controller"),
            }

            # Apply spell-specific targeting rules
            if self._is_valid_terrain_target(spell, terrain_target, caster_player):
                valid_terrains.append(terrain_target)

        return valid_terrains

    def _get_valid_dua_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid DUA targets for a spell."""
        valid_dua_units = []

        # Get units from caster's DUA
        dua_units = self.dua_manager.get_player_dua(caster_player)

        for unit in dua_units:
            unit_info = {
                "player": caster_player,
                "unit_data": unit.to_dict(),
                "location": "DUA",
                "is_own_unit": True,
            }

            # Apply spell-specific targeting rules
            if self._is_valid_dua_target(spell, unit_info, caster_player):
                valid_dua_units.append(unit_info)

        return valid_dua_units

    def _get_valid_bua_targets(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid BUA targets for a spell."""
        valid_bua_units = []

        # Get units from caster's BUA
        bua_units = self.bua_manager.get_player_bua(caster_player)

        for unit in bua_units:
            unit_info = {
                "player": caster_player,
                "unit_data": unit.to_dict(),
                "location": "BUA",
                "is_own_unit": True,
            }

            # Apply spell-specific targeting rules
            if self._is_valid_bua_target(spell, unit_info, caster_player):
                valid_bua_units.append(unit_info)

        return valid_bua_units

    def _is_valid_army_target(self, spell: SpellModel, army_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if an army is a valid target for a spell."""
        # Basic targeting rules
        effect_lower = spell.effect.lower()

        # Check for "your" vs "any" targeting
        if "your" in effect_lower and not army_info["is_own_army"]:
            return False

        # Check for element matching if required
        if spell.element != "ANY" and spell.element != "ELEMENTAL":
            # Check if army has units with matching elements
            army_elements = set()
            for unit in army_info["units"]:
                army_elements.update(unit.get("elements", []))

            if spell.element not in army_elements:
                return False

        return True

    def _is_valid_unit_target(self, spell: SpellModel, unit_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if a unit is a valid target for a spell."""
        effect_lower = spell.effect.lower()
        unit_data = unit_info["unit_data"]

        # Check for "your" vs "any" targeting
        if "your" in effect_lower and not unit_info["is_own_unit"]:
            return False

        # Check for species restrictions
        if spell.species != "Any" and unit_data.get("species") != spell.species:
            return False

        # Check for element matching if required
        if spell.element != "ANY" and spell.element != "ELEMENTAL":
            unit_elements = unit_data.get("elements", [])
            if spell.element not in unit_elements:
                return False

        return True

    def _is_valid_terrain_target(self, spell: SpellModel, terrain_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if a terrain is a valid target for a spell."""
        # Most spells can target any terrain
        return True

    def _is_valid_dua_target(self, spell: SpellModel, unit_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if a DUA unit is a valid target for a spell."""
        effect_lower = spell.effect.lower()
        unit_data = unit_info["unit_data"]

        # Only certain spells can target DUA
        if "dua" not in effect_lower and "resurrect" not in effect_lower:
            return False

        # Check for element matching if required
        if spell.element != "ANY" and spell.element != "ELEMENTAL":
            unit_elements = unit_data.get("elements", [])
            if spell.element not in unit_elements:
                return False

        return True

    def _is_valid_bua_target(self, spell: SpellModel, unit_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if a BUA unit is a valid target for a spell."""
        effect_lower = spell.effect.lower()
        unit_data = unit_info["unit_data"]

        # Only certain spells can target BUA
        if "bua" not in effect_lower and "buried" not in effect_lower:
            return False

        # Check for element matching if required
        if spell.element != "ANY" and spell.element != "ELEMENTAL":
            unit_elements = unit_data.get("elements", [])
            if spell.element not in unit_elements:
                return False

        return True

    def validate_spell_target(
        self, spell: SpellModel, target_type: str, target_data: Dict[str, Any], caster_player: str
    ) -> Tuple[bool, str]:
        """Validate a specific spell target."""
        if target_type == "summoning_pool":
            return False, "Spells cannot target the Summoning Pool"

        # Validate based on target type
        if target_type == "army":
            if self._is_valid_army_target(spell, target_data, caster_player):
                return True, "Valid army target"
            return False, "Invalid army target"

        if target_type == "unit":
            if self._is_valid_unit_target(spell, target_data, caster_player):
                return True, "Valid unit target"
            return False, "Invalid unit target"

        if target_type == "terrain":
            if self._is_valid_terrain_target(spell, target_data, caster_player):
                return True, "Valid terrain target"
            return False, "Invalid terrain target"

        if target_type == "dua":
            if self._is_valid_dua_target(spell, target_data, caster_player):
                return True, "Valid DUA target"
            return False, "Invalid DUA target"

        if target_type == "bua":
            if self._is_valid_bua_target(spell, target_data, caster_player):
                return True, "Valid BUA target"
            return False, "Invalid BUA target"

        return False, f"Unknown target type: {target_type}"

    def get_target_description(self, target_type: str, target_data: Dict[str, Any]) -> str:
        """Get a human-readable description of a target."""
        if target_type == "army":
            player = target_data.get("player", "Unknown")
            location = target_data.get("location", "Unknown")
            return f"{player}'s army at {location}"

        if target_type == "unit":
            unit_data = target_data.get("unit_data", {})
            player = target_data.get("player", "Unknown")
            location = target_data.get("location", "Unknown")
            unit_name = unit_data.get("name", "Unknown Unit")
            species = unit_data.get("species", "Unknown")
            return f"{unit_name} ({species}) - {player}'s unit at {location}"

        if target_type == "terrain":
            name = target_data.get("name", "Unknown Terrain")
            controller = target_data.get("controller", "Neutral")
            return f"{name} (controlled by {controller})"

        if target_type == "dua":
            unit_data = target_data.get("unit_data", {})
            player = target_data.get("player", "Unknown")
            unit_name = unit_data.get("name", "Unknown Unit")
            species = unit_data.get("species", "Unknown")
            return f"{unit_name} ({species}) - {player}'s DUA"

        if target_type == "bua":
            unit_data = target_data.get("unit_data", {})
            player = target_data.get("player", "Unknown")
            unit_name = unit_data.get("name", "Unknown Unit")
            species = unit_data.get("species", "Unknown")
            return f"{unit_name} ({species}) - {player}'s BUA"

        return "Unknown target"

    def _get_valid_summoning_pool_sources(
        self, spell: SpellModel, caster_player: str, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get valid dragons/units from summoning pool for summoning spells."""
        valid_sources: List[Dict[str, Any]] = []

        if not self.summoning_pool_manager:
            return valid_sources

        # Get caster's summoning pool
        player_pool = self.summoning_pool_manager.get_player_pool(caster_player)

        for dragon in player_pool:
            dragon_info = {
                "dragon_data": dragon.to_dict(),
                "player": caster_player,
                "location": "Summoning Pool",
                "dragon_type": dragon.dragon_type,
                "elements": dragon.elements,
                "name": dragon.name,
            }

            # Apply spell-specific rules
            if self._is_valid_summoning_source(spell, dragon_info, caster_player):
                valid_sources.append(dragon_info)

        return valid_sources

    def _is_valid_summoning_source(self, spell: SpellModel, dragon_info: Dict[str, Any], caster_player: str) -> bool:
        """Check if a dragon is a valid source for a summoning spell."""
        effect_lower = spell.effect.lower()
        dragon_info.get("dragon_data", {})

        if spell.name == "Summon White Dragon":
            # Only White Dragons can be summoned with this spell
            return dragon_info.get("dragon_type") == "WHITE"

        if spell.name == "Summon Dragon":
            # Regular dragons can be summoned (not White Dragons)
            return dragon_info.get("dragon_type") != "WHITE"

        if spell.name == "Summon Dragonkin":
            # Only dragonkin units
            return "dragonkin" in dragon_info.get("name", "").lower()

        # Default: allow all dragons for summoning spells
        return "summon" in effect_lower
