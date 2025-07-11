"""
Special Action Icon (SAI) processor for Dragon Dice combat.

This module handles the complex SAI calculations and interactions during combat,
including cantrips, combat modifications, and other special effects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SAIResult:
    """Result of processing a Special Action Icon."""

    sai_type: str
    effect_description: str
    melee_bonus: int = 0
    missile_bonus: int = 0
    magic_bonus: int = 0
    save_bonus: int = 0
    maneuver_bonus: int = 0
    special_effects: List[str] = field(default_factory=list)


@dataclass
class CombatRollResult:
    """Result of processing a combat roll with SAI effects."""

    raw_melee: int = 0
    raw_missile: int = 0
    raw_magic: int = 0
    raw_save: int = 0
    raw_maneuver: int = 0
    raw_id: int = 0
    raw_sai: int = 0

    # After SAI processing
    final_melee: int = 0
    final_missile: int = 0
    final_magic: int = 0
    final_save: int = 0
    final_maneuver: int = 0

    sai_results: List[SAIResult] = field(default_factory=list)
    special_notes: List[str] = field(default_factory=list)


class SAIProcessor:
    """
    Processes Special Action Icons (SAIs) and their effects during combat.

    This class handles the complex interactions between different SAI types
    and their effects on combat results, including cantrips, combat bonuses,
    and special abilities.
    """

    # Common SAI types and their effects
    SAI_TYPES = {
        "cantrip": "Generates magic results for casting cantrip spells",
        "melee_bonus": "Adds bonus melee results",
        "missile_bonus": "Adds bonus missile results",
        "save_bonus": "Adds bonus save results",
        "double_results": "Doubles certain result types",
        "reroll": "Allows rerolling of dice",
        "negate_damage": "Negates damage from specific sources",
        "element_conversion": "Converts magic results to specific elements",
        "recruitment": "Allows unit recruitment",
        "promotion": "Allows unit promotion",
    }

    def __init__(self, unit_roster=None, dua_manager=None):
        """
        Initialize SAI processor.

        Args:
            unit_roster: Unit roster for looking up unit-specific SAI effects
            dua_manager: DUA manager for species abilities that depend on dead units
        """
        self.unit_roster = unit_roster
        self.dua_manager = dua_manager

    def process_combat_roll(
        self,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        is_attacker: bool = True,
        terrain_elements: Optional[List[str]] = None,
        terrain_eighth_face_controlled: bool = False,
        player_name: Optional[str] = None,
        opponent_name: Optional[str] = None,
    ) -> CombatRollResult:
        """
        Process a complete combat roll including SAI effects.

        Args:
            roll_results: Dictionary of unit_name -> face_results
            combat_type: Type of combat ("melee", "missile", "magic")
            army_units: List of unit data for the army
            is_attacker: Whether this is the attacking army

        Returns:
            CombatRollResult with all calculations
        """
        result = CombatRollResult()

        # Count raw results
        for _unit_name, face_results in roll_results.items():
            for face_result in face_results:
                if face_result:
                    normalized = face_result.lower().strip()

                    if normalized in ["m", "melee"]:
                        result.raw_melee += 1
                    elif normalized in ["mi", "missile"]:
                        result.raw_missile += 1
                    elif normalized in ["mg", "magic"]:
                        result.raw_magic += 1
                    elif normalized in ["s", "save"]:
                        result.raw_save += 1
                    elif normalized in ["ma", "maneuver"]:
                        result.raw_maneuver += 1
                    elif normalized in ["id"]:
                        result.raw_id += 1
                    elif normalized in ["sai"]:
                        result.raw_sai += 1

        # Start with raw results
        result.final_melee = result.raw_melee
        result.final_missile = result.raw_missile
        result.final_magic = result.raw_magic
        result.final_save = result.raw_save
        result.final_maneuver = result.raw_maneuver

        # Process SAI effects
        if result.raw_sai > 0:
            self._process_sai_effects(result, roll_results, combat_type, army_units, is_attacker)

        # Add ID face bonuses (ID faces generate results equal to unit health)
        self._process_id_faces(result, roll_results, army_units, combat_type, terrain_eighth_face_controlled)

        # Process species abilities
        self._process_species_abilities(
            result, roll_results, army_units, combat_type, is_attacker, terrain_elements, player_name, opponent_name
        )

        return result

    def _process_sai_effects(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        is_attacker: bool,
    ):
        """Process all SAI effects for the roll."""

        # For this implementation, we'll handle common SAI effects
        # In a full implementation, this would look up specific SAI effects
        # from unit definitions and spell/ability databases

        for unit_name, face_results in roll_results.items():
            sai_count = sum(1 for face in face_results if face.lower().strip() == "sai")

            if sai_count > 0:
                # Find the unit data
                unit_data = self._find_unit_data(unit_name, army_units)
                if unit_data:
                    self._process_unit_sai_effects(result, unit_data, sai_count, combat_type, is_attacker)

    def _process_unit_sai_effects(
        self, result: CombatRollResult, unit_data: Dict[str, Any], sai_count: int, combat_type: str, is_attacker: bool
    ):
        """Process SAI effects for a specific unit."""

        # This is a simplified implementation
        # In reality, each unit would have specific SAI effects defined

        unit_name = unit_data.get("name", "Unknown")
        species = unit_data.get("species", "Unknown")

        # Generic SAI effects (simplified)
        if combat_type == "melee" and is_attacker:
            # Example: Some units get bonus melee from SAI
            if species in ["Dwarves", "Amazons"]:  # Examples
                bonus_melee = sai_count
                result.final_melee += bonus_melee
                result.sai_results.append(
                    SAIResult(
                        sai_type="melee_bonus",
                        effect_description=f"{unit_name} SAI: +{bonus_melee} melee",
                        melee_bonus=bonus_melee,
                    )
                )

        elif (
            combat_type == "melee"
            and not is_attacker
            and species
            in [  # noqa: C901
                "Coral Elves",
                "Treefolk",
            ]
        ):  # Examples
            # Example: Some units get bonus saves from SAI
            bonus_saves = sai_count
            result.final_save += bonus_saves
            result.sai_results.append(
                SAIResult(
                    sai_type="save_bonus",
                    effect_description=f"{unit_name} SAI: +{bonus_saves} save",
                    save_bonus=bonus_saves,
                )
            )

        # Cantrip effects
        if combat_type in ["melee", "missile"] and not is_attacker:
            # Cantrips can be used during save rolls
            magic_from_cantrip = sai_count
            result.final_magic += magic_from_cantrip
            result.sai_results.append(
                SAIResult(
                    sai_type="cantrip",
                    effect_description=f"{unit_name} Cantrip: +{magic_from_cantrip} magic (cantrip spells only)",
                    magic_bonus=magic_from_cantrip,
                    special_effects=["cantrip_magic"],
                )
            )

    def _process_id_faces(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        combat_type: str,
        terrain_eighth_face_controlled: bool = False,
    ):
        """Process ID face bonuses."""

        for unit_name, face_results in roll_results.items():
            id_count = sum(1 for face in face_results if face.lower().strip() == "id")

            if id_count > 0:
                # Find unit health for ID bonus calculation
                unit_data = self._find_unit_data(unit_name, army_units)
                if unit_data:
                    health = unit_data.get("health", 1)
                    id_bonus = id_count * health

                    # Apply terrain eighth face doubling to ID results
                    if terrain_eighth_face_controlled:
                        id_bonus *= 2
                        eighth_face_note = " (doubled by terrain eighth face)"
                    else:
                        eighth_face_note = ""

                    # ID faces generate results matching the roll type
                    if combat_type == "melee":
                        result.final_melee += id_bonus
                        result.special_notes.append(f"{unit_name} ID: +{id_bonus} melee{eighth_face_note}")
                    elif combat_type == "missile":
                        result.final_missile += id_bonus
                        result.special_notes.append(f"{unit_name} ID: +{id_bonus} missile{eighth_face_note}")
                    elif combat_type == "magic":
                        result.final_magic += id_bonus
                        result.special_notes.append(f"{unit_name} ID: +{id_bonus} magic{eighth_face_note}")
                    else:  # Save rolls
                        result.final_save += id_bonus
                        result.special_notes.append(f"{unit_name} ID: +{id_bonus} save{eighth_face_note}")

    def _process_species_abilities(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        combat_type: str,
        is_attacker: bool,
        terrain_elements: Optional[List[str]] = None,
        player_name: Optional[str] = None,
        opponent_name: Optional[str] = None,
    ):
        """Process species-specific abilities."""

        if terrain_elements is None:
            terrain_elements = []  # Would get from terrain data in full implementation

        # Process each unit's species abilities
        for unit_name, face_results in roll_results.items():
            unit_data = self._find_unit_data(unit_name, army_units)
            if not unit_data:
                continue

            species = unit_data.get("species", "")

            # Dwarven Might: Count save results as melee results when counter-attacking at fire terrain
            if (
                species == "Dwarves"
                and combat_type == "melee"
                and not is_attacker  # This is a counter-attack (defender)
                and "fire" in terrain_elements
            ):
                # Count save results for this unit
                save_count = sum(1 for face in face_results if face.lower().strip() in ["s", "save"])

                if save_count > 0:
                    # Convert saves to melee for counter-attack
                    result.final_melee += save_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="dwarven_might",
                            effect_description=f"{unit_name} Dwarven Might: +{save_count} melee (saves count as melee at fire terrain)",
                            melee_bonus=save_count,
                            special_effects=["dwarven_might_conversion"],
                        )
                    )

            # Mountain Master: Dwarves count melee results as maneuver results at earth terrain
            if species == "Dwarves" and combat_type == "maneuver" and "earth" in terrain_elements:
                # Count melee results for this unit
                melee_count = sum(1 for face in face_results if face.lower().strip() in ["m", "melee"])

                if melee_count > 0:
                    # Convert melee to maneuver
                    result.final_maneuver += melee_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="mountain_master",
                            effect_description=f"{unit_name} Mountain Master: +{melee_count} maneuver (melee count as maneuver at earth terrain)",
                            maneuver_bonus=melee_count,
                            special_effects=["mountain_master_conversion"],
                        )
                    )

            # Swamp Master: Goblins count melee results as maneuver results at earth terrain
            if species == "Goblins" and combat_type == "maneuver" and "earth" in terrain_elements:
                # Count melee results for this unit
                melee_count = sum(1 for face in face_results if face.lower().strip() in ["m", "melee"])

                if melee_count > 0:
                    # Convert melee to maneuver
                    result.final_maneuver += melee_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="swamp_master",
                            effect_description=f"{unit_name} Swamp Master: +{melee_count} maneuver (melee count as maneuver at earth terrain)",
                            maneuver_bonus=melee_count,
                            special_effects=["swamp_master_conversion"],
                        )
                    )

            # Stampede: Feral count maneuver results as melee results during counter-attacks at earth+air terrain
            if (
                species == "Feral"
                and combat_type == "melee"
                and not is_attacker  # This is a counter-attack (defender)
                and "earth" in terrain_elements
                and "air" in terrain_elements
            ):
                # Count maneuver results for this unit
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])

                if maneuver_count > 0:
                    # Convert maneuver to melee for counter-attack
                    result.final_melee += maneuver_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="stampede",
                            effect_description=f"{unit_name} Stampede: +{maneuver_count} melee (maneuver count as melee at earth+air terrain)",
                            melee_bonus=maneuver_count,
                            special_effects=["stampede_conversion"],
                        )
                    )

            # Flaming Shields: Firewalkers count save results as melee results at fire terrain (NOT during counter-attacks)
            if (
                species == "Firewalkers"
                and combat_type == "melee"
                and is_attacker  # NOT a counter-attack (original attacker only)
                and "fire" in terrain_elements
            ):
                # Count save results for this unit
                save_count = sum(1 for face in face_results if face.lower().strip() in ["s", "save"])

                if save_count > 0:
                    # Convert saves to melee for attack
                    result.final_melee += save_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="flaming_shields",
                            effect_description=f"{unit_name} Flaming Shields: +{save_count} melee (saves count as melee at fire terrain)",
                            melee_bonus=save_count,
                            special_effects=["flaming_shields_conversion"],
                        )
                    )

            # Coastal Dodge: Coral Elves count maneuver results as save results at water terrain
            if (
                species == "Coral Elves"
                and combat_type in ["save", "melee", "missile"]  # Works for saves against any action
                and not is_attacker  # Defending only
                and "water" in terrain_elements
            ):
                # Count maneuver results for this unit
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])

                if maneuver_count > 0:
                    # Convert maneuver to save
                    result.final_save += maneuver_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="coastal_dodge",
                            effect_description=f"{unit_name} Coastal Dodge: +{maneuver_count} save (maneuver count as save at water terrain)",
                            save_bonus=maneuver_count,
                            special_effects=["coastal_dodge_conversion"],
                        )
                    )

            # Defensive Volley: Coral Elves can counter-attack against missile attacks at air terrain
            # Note: This is handled separately in the missile combat dialog, but we track it here for completeness
            if (
                species == "Coral Elves"
                and combat_type == "missile"
                and not is_attacker  # Counter-attacking against missile
                and "air" in terrain_elements
            ):
                # This doesn't modify results here, but indicates the ability is available
                result.special_notes.append(
                    f"{unit_name} can use Defensive Volley (missile counter-attack at air terrain)"
                )

            # Coral Elves missile results count as saves during save rolls (existing ability from rules)
            if species == "Coral Elves" and combat_type == "save" and not is_attacker:
                missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])
                if missile_count > 0:
                    result.final_save += missile_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="coral_elf_missile_save",
                            effect_description=f"{unit_name} Coral Elf: +{missile_count} save (missile results count as saves)",
                            save_bonus=missile_count,
                            special_effects=["coral_elf_missile_conversion"],
                        )
                    )

            # Intangibility: Scalders count maneuver results as save results against missile damage at water terrain
            if (
                species == "Scalders"
                and combat_type == "missile"  # Specifically against missile attacks
                and not is_attacker  # Defending only
                and "water" in terrain_elements
            ):
                # Count maneuver results for this unit
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])

                if maneuver_count > 0:
                    # Convert maneuver to save specifically against missile damage
                    result.final_save += maneuver_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="intangibility",
                            effect_description=f"{unit_name} Intangibility: +{maneuver_count} save (maneuver count as save vs missile at water terrain)",
                            save_bonus=maneuver_count,
                            special_effects=["intangibility_conversion"],
                        )
                    )

            # Terrain Harmony: Amazons generate magic results matching terrain elements when rolling for magic
            if species == "Amazons" and combat_type == "magic" and is_attacker:  # When casting magic (not defending)
                # Amazon magic results can be any element present in the terrain
                # This is handled differently - we note that their magic is terrain-element flexible
                # The actual element assignment happens during spell casting
                amazon_magic_count = sum(1 for face in face_results if face.lower().strip() in ["mg", "magic"])

                if amazon_magic_count > 0:
                    result.special_notes.append(
                        f"{unit_name} Terrain Harmony: {amazon_magic_count} magic can match any terrain element "
                        + f"({', '.join(terrain_elements)})"
                    )

            # Add other species abilities here as needed
            # Examples from the game:

            # Coral Elves: Missile results count as saves during save rolls
            if species == "Coral Elves" and combat_type == "save" and not is_attacker:
                missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])
                if missile_count > 0:
                    result.final_save += missile_count
                    result.sai_results.append(
                        SAIResult(
                            sai_type="coral_elf_ability",
                            effect_description=f"{unit_name} Coral Elf: +{missile_count} save (missile results count as saves)",
                            save_bonus=missile_count,
                            special_effects=["coral_elf_conversion"],
                        )
                    )

            # Amazons: ID results doubled when at eighth face
            # This would be handled elsewhere when terrain is at eighth face

            # DUA-DEPENDENT SPECIES ABILITIES
            # These abilities require access to the DUA manager

            # Bone Magic (Undead): Additional magic results based on DUA count
            if species == "Undead" and combat_type == "magic" and is_attacker and self.dua_manager and player_name:
                # Count non-ID magic results for this unit
                non_id_magic_count = sum(1 for face in face_results if face.lower().strip() in ["mg", "magic"])

                if non_id_magic_count > 0:
                    # Get dead Undead count from DUA (max 4)
                    dead_undead_count = self._get_dua_species_count(player_name, "Undead", max_count=4)

                    if dead_undead_count > 0:
                        # Add bonus magic results equal to DUA count
                        bonus_magic = min(dead_undead_count, non_id_magic_count)  # Can't exceed non-ID magic rolled
                        result.final_magic += bonus_magic
                        result.sai_results.append(
                            SAIResult(
                                sai_type="bone_magic",
                                effect_description=f"{unit_name} Bone Magic: +{bonus_magic} magic (DUA: {dead_undead_count} dead Undead)",
                                magic_bonus=bonus_magic,
                                special_effects=["bone_magic_dua_bonus"],
                            )
                        )

            # Add placeholder notes for other DUA-dependent abilities
            # These will be handled by specialized dialogs since they require opponent interaction

            # Magic Negation (Frostwings) - opponent must be notified when they take magic action
            if species == "Frostwings" and self.dua_manager and player_name:
                dead_frostwings_count = self._get_dua_species_count(player_name, "Frostwings", max_count=5)
                if dead_frostwings_count > 0:
                    result.special_notes.append(
                        f"{unit_name} can use Magic Negation (DUA: {dead_frostwings_count} dead Frostwings available)"
                    )

            # Foul Stench (Goblins) - affects opponent's counter-attack in melee
            if species == "Goblins" and combat_type == "melee" and is_attacker and self.dua_manager and player_name:
                dead_goblins_count = self._get_dua_species_count(player_name, "Goblins", max_count=3)
                if dead_goblins_count > 0:
                    result.special_notes.append(
                        f"{unit_name} Foul Stench: {dead_goblins_count} opponent units cannot counter-attack (DUA effect)"
                    )

            # Cursed Bullets (Lava Elves) - special missile damage rules
            if (
                species == "Lava Elves"
                and combat_type == "missile"
                and is_attacker
                and self.dua_manager
                and player_name
            ):
                dead_lava_elves_count = self._get_dua_species_count(player_name, "Lava Elves", max_count=3)
                missile_count = sum(1 for face in face_results if face.lower().strip() in ["mi", "missile"])

                if dead_lava_elves_count > 0 and missile_count > 0:
                    cursed_missile_count = min(dead_lava_elves_count, missile_count)
                    result.special_notes.append(
                        f"{unit_name} Cursed Bullets: {cursed_missile_count} missile results bypass normal saves (DUA: {dead_lava_elves_count} dead Lava Elves)"
                    )

    def _find_unit_data(self, unit_name: str, army_units: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find unit data by name."""
        for unit in army_units:
            if unit.get("name") == unit_name:
                return unit
        return None

    def _get_dua_species_count(self, player_name: str, species: str, max_count: Optional[int] = None) -> int:
        """Get the count of dead units of a specific species in a player's DUA."""
        if not self.dua_manager or not player_name:
            return 0

        dead_units = self.dua_manager.get_units_by_species(player_name, species)
        count = len(dead_units)

        if max_count is not None:
            count = min(count, max_count)

        return count

    def calculate_cantrip_magic(self, roll_results: Dict[str, List[str]], army_units: List[Dict[str, Any]]) -> int:
        """
        Calculate magic points available from cantrip SAIs.

        Args:
            roll_results: Dictionary of unit_name -> face_results
            army_units: List of unit data

        Returns:
            Total magic points available for cantrip spells
        """
        cantrip_magic = 0

        for unit_name, face_results in roll_results.items():
            sai_count = sum(1 for face in face_results if face.lower().strip() == "sai")

            if sai_count > 0:
                # Check if this unit has cantrip ability
                unit_data = self._find_unit_data(unit_name, army_units)
                if unit_data and self._unit_has_cantrip(unit_data):
                    cantrip_magic += sai_count

        return cantrip_magic

    def _unit_has_cantrip(self, unit_data: Dict[str, Any]) -> bool:
        """Check if a unit has cantrip ability."""
        # This would check unit definitions for cantrip SAI
        # For now, assume all units can potentially have cantrip
        return True

    def get_available_cantrip_spells(self, elements: List[str], species: str) -> List[Dict[str, Any]]:
        """
        Get list of cantrip spells available to cast.

        Args:
            elements: List of elements the army can use
            species: Species of the casting army

        Returns:
            List of available cantrip spells
        """
        # This would integrate with the spell system
        # For now, return a simplified list
        cantrip_spells = [
            {"name": "Hailstorm", "cost": 2, "element": "air", "description": "Inflict 1 damage"},
            {"name": "Stone Skin", "cost": 2, "element": "earth", "description": "Add 1 save result"},
            {"name": "Palsy", "cost": 2, "element": "death", "description": "Subtract 1 result"},
            {
                "name": "Ash Storm",
                "cost": 2,
                "element": "fire",
                "description": "Subtract 1 result from all rolls at terrain",
            },
            {"name": "Watery Double", "cost": 2, "element": "water", "description": "Add 1 save result"},
        ]

        # Filter by available elements
        available_spells = []
        for spell in cantrip_spells:
            if spell["element"] in elements or not elements:  # No element restriction if empty
                available_spells.append(spell)

        return available_spells

    def format_combat_summary(self, result: CombatRollResult, combat_type: str) -> str:
        """Format combat result into a readable summary."""
        lines = []

        # Raw results
        lines.append("Raw Die Results:")
        if result.raw_melee > 0:
            lines.append(f"  Melee: {result.raw_melee}")
        if result.raw_missile > 0:
            lines.append(f"  Missile: {result.raw_missile}")
        if result.raw_magic > 0:
            lines.append(f"  Magic: {result.raw_magic}")
        if result.raw_save > 0:
            lines.append(f"  Save: {result.raw_save}")
        if result.raw_maneuver > 0:
            lines.append(f"  Maneuver: {result.raw_maneuver}")
        if result.raw_id > 0:
            lines.append(f"  ID: {result.raw_id}")
        if result.raw_sai > 0:
            lines.append(f"  SAI: {result.raw_sai}")

        # SAI effects
        if result.sai_results:
            lines.append("\nSAI Effects:")
            for sai_result in result.sai_results:
                lines.append(f"  {sai_result.effect_description}")

        # ID bonuses
        if result.special_notes:
            lines.append("\nID Bonuses:")
            for note in result.special_notes:
                lines.append(f"  {note}")

        # Final results
        lines.append(f"\nFinal {combat_type.title()} Results:")
        if combat_type == "melee":
            lines.append(f"  Total Melee: {result.final_melee}")
        elif combat_type == "missile":
            lines.append(f"  Total Missile: {result.final_missile}")
        elif combat_type == "magic":
            lines.append(f"  Total Magic: {result.final_magic}")
        elif combat_type == "maneuver":
            lines.append(f"  Total Maneuver: {result.final_maneuver}")
        else:  # Save roll
            lines.append(f"  Total Saves: {result.final_save}")

        return "\n".join(lines)
