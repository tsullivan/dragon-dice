"""
Special Action Icon (SAI) processor for Dragon Dice combat.

This module handles the complex SAI calculations and interactions during combat,
including cantrips, combat modifications, and other special effects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


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
class RollModifier:
    """Represents a modifier to be applied during die roll resolution."""

    modifier_type: str  # "subtract", "divide", "multiply", "add", "counts_as"
    value: int
    source: str  # What created this modifier (SAI name, spell, etc.)
    target_result_type: str  # "melee", "missile", "magic", "save", "maneuver"
    description: str = ""


@dataclass
class RerollEffect:
    """Represents a re-roll effect to be applied."""

    unit_name: str
    source: str  # SAI name that caused the re-roll
    description: str
    force_reroll: bool = False  # True if mandatory, False if optional


@dataclass
class DelayedEffect:
    """Represents an SAI effect that is delayed until a later step."""

    effect_type: str  # Type of delayed effect
    source: str  # SAI that created the effect
    target: str  # What it targets
    value: Any  # Effect parameters
    description: str


@dataclass
class TargetingRequest:
    """Represents a request to target units for an SAI effect."""

    sai_name: str
    source_unit: str  # Unit using the SAI
    target_type: str  # "unit", "health_worth", "army", "specific_unit"
    target_count: int  # Number to target (X value or specific count)
    target_army: str  # Which army to target ("defending", "attacking", "any")
    targeting_criteria: str  # Additional criteria ("rolled_id", "none", etc.)
    effect_description: str
    must_target_fullest_extent: bool = True  # Follow fullest extent rule


@dataclass
class TargetingResult:
    """Result of a targeting operation."""

    success: bool
    targeted_units: List[Dict[str, Any]] = field(default_factory=list)
    total_health_targeted: int = 0
    targeting_notes: List[str] = field(default_factory=list)
    effect_applied: bool = False


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

    # New resolution tracking
    modifiers: List[RollModifier] = field(default_factory=list)
    reroll_effects: List[RerollEffect] = field(default_factory=list)
    delayed_effects: List[DelayedEffect] = field(default_factory=list)
    resolution_log: List[str] = field(default_factory=list)  # Step-by-step log
    targeting_requests: List[TargetingRequest] = field(default_factory=list)  # Targeting requests for UI
    targeting_results: List[TargetingResult] = field(default_factory=list)  # Applied targeting results


class SAIProcessor:
    """
    Processes Special Action Icons (SAIs) and their effects during combat.

    This class handles the complex interactions between different SAI types
    and their effects on combat results, including cantrips, combat bonuses,
    and special abilities.
    """

    # Comprehensive SAI registry from special_action_icons.md
    SAI_REGISTRY = {
        "attune": {
            "applies": ["magic"],
            "description": "During a magic action, Attune generates X magic results of any element. Attune may also change the normal (non-ID, non-SAI) magic results of one unit in the marching army to the same element as the Attune magic results.",
        },
        "bash": {
            "applies": ["dragon_attack", "save"],
            "description": "During a save roll against a melee attack, target one unit from the attacking army. The targeted unit takes damage equal to the melee results it generated. The targeted unit must make a save roll against this damage. Bash also generates save results equal to the targeted unit's melee results. During other save rolls, Bash generates X save results. During a dragon attack choose an attacking dragon that has inflicted damage. That dragon takes damage equal to the amount of damage it inflicted. Bash also generates save results equal to the damage the chosen dragon did.",
        },
        "belly": {"applies": ["any"], "description": "During any roll, the unit loses its automatic save results."},
        "breath": {
            "applies": ["melee"],
            "description": "During a melee attack, target X health-worth of units in the defending army. The targets are killed.",
        },
        "bullseye": {
            "applies": ["dragon_attack", "missile"],
            "description": "During a missile attack, target X health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well. During a dragon attack, Bullseye generates X missile results.",
        },
        "cantrip": {
            "applies": ["magic", "non_maneuver"],
            "description": "During a magic action or Magic Negation (Frostwings - page 23) roll, Cantrip generates X magic results. During other non-maneuver rolls, Cantrip generates X magic results that only allow you to cast spells marked as 'Cantrip' from the spell list.",
        },
        "charge": {
            "applies": ["melee"],
            "description": "During a melee attack, the attacking army counts all Maneuver results as if they were Melee results. Instead of making a regular save roll or a counter-attack, the defending army makes a combination save and melee roll. The attacking army takes damage equal to these melee results. Only save results generated by spells may reduce this damage. Charge has no effect during a counter-attack.",
        },
        "charm": {
            "applies": ["melee"],
            "description": "During a melee attack, target up to X health-worth of units in the defending army; those units don't roll to save during this march. Instead, the owner rolls these units and adds their results to the attacking army's results. Those units may take damage from the melee attack as normal.",
        },
        "choke": {
            "applies": ["melee"],
            "description": "During a melee attack, this effect is delayed until after the target army rolls for saves. Target up to X healthworth of units in the that army that rolled an ID icon. The targets are killed. None of their results are counted towards the army's save results.",
        },
        "cloak": {
            "applies": ["dragon_attack", "individual", "magic", "save"],
            "description": "During a save roll or dragon attack, add X non-magical save results to the army containing this unit until the beginning of your next turn. During a magic action, Cloak generates X magic results. During a roll for an individual-targeting effect, Cloak generates X magic, maneuver, melee, missile, or save results.",
        },
        "coil": {
            "applies": ["dragon_attack", "melee"],
            "description": "During a melee attack, target one unit in the defending army. The target takes X damage and makes a combination roll, counting save and melee results. Any melee results that the target generates inflict damage on the Coiling unit with no save possible. During a dragon attack, Coil generates X melee results.",
        },
        "confuse": {
            "applies": ["melee", "missile"],
            "description": "During a melee or missile attack, this effect is delayed until after the target army rolls for saves. Target up to X health-worth of units in the that army. Re-roll the targeted units, ignoring all previous results.",
        },
        "convert": {
            "applies": ["melee"],
            "description": "During a melee attack, target up to X health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. The attacking player may return up to the amount of heath-worth killed this way from their DUA to the attacking army.",
        },
        "counter": {
            "applies": ["dragon_attack", "melee", "save"],
            "description": "During a save roll against a melee attack, Counter generates X save results and inflicts X damage upon the attacking army. Only save results generated by spells may reduce this damage. During any other save roll, Counter generates X save results. During a melee attack, Counter generates X melee results. During a dragon attack, Counter generates X save and X melee results.",
        },
        "create_fireminions": {
            "applies": ["any_non_individual"],
            "description": "During any army roll, Create Fireminions generates X magic, maneuver, melee, missile or save results.",
        },
        "crush": {
            "applies": ["dragon_attack", "missile"],
            "description": "During a missile attack, target up to X healthworth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed. Each unit killed must make a save roll. Those that do not generate a save result on this second roll are buried. During a dragon attack, Crush generates X missile results.",
        },
        "decapitate": {
            "applies": ["melee", "dragon_attack"],
            "description": "During a melee attack, this effect is delayed until after the target army rolls for saves. Target one unit that rolled an ID icon. The target is killed. None of their results are counted towards the army's save results. During a dragon attack, kill one dragon that rolled Jaws. If no dragon rolled Jaws, Decapitate generates three melee results.",
        },
        "elevate": {
            "applies": ["dragon_attack", "maneuver", "missile", "save"],
            "description": "During a maneuver roll, Elevate generates X maneuver results. During a missile attack, double one unit's missile results. During a save roll against a melee attack, double one unit's save results. During a dragon attack, double one unit's missile or save results.",
        },
        "fly": {"applies": ["any"], "description": "During any roll, Fly generates X maneuver or X save results."},
        "regenerate": {
            "applies": ["non_maneuver"],
            "description": "During any non-maneuver roll, choose one: Regenerate generates X save results, OR, you may return up to X health-worth of units from your DUA to the army containing this unit.",
        },
        "rend": {
            "applies": ["dragon_attack", "maneuver", "melee"],
            "description": "During a melee or dragon attack, Rend generates X melee results. Roll this unit again and apply the new result as well. During a maneuver roll, Rend generates X maneuver results.",
        },
        "trample": {
            "applies": ["any"],
            "description": "During any roll, Trample generates X maneuver and X melee results.",
        },
        "vanish": {
            "applies": ["save"],
            "description": "During a save roll, Vanish generates X save results. The unit may then move to any terrain or its Reserve Area. If the unit moves, the save results still apply to the army that the Vanishing unit left.",
        },
        # More SAIs can be added incrementally as needed
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

        # Targeting state
        self._targeting_restrictions = {}  # Track what's already been targeted
        self._pending_targeting_requests = []  # Requests waiting for UI resolution

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

    # New 10-step resolution engine methods
    def _count_raw_results(self, result: CombatRollResult, roll_results: Dict[str, List[str]]):
        """Step 1: Count the raw die face results."""
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

        # Initialize final results with raw results
        result.final_melee = result.raw_melee
        result.final_missile = result.raw_missile
        result.final_magic = result.raw_magic
        result.final_save = result.raw_save
        result.final_maneuver = result.raw_maneuver

    def _apply_delayed_effects(
        self,
        result: CombatRollResult,
        delayed_effects: List[DelayedEffect],
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
    ):
        """Step 2: Apply delayed SAI effects from attacker's roll."""
        for effect in delayed_effects:
            result.special_notes.append(f"Delayed effect applied: {effect.description}")
            # Implementation would depend on specific delayed effect types
            # This is a placeholder for the framework

    def _process_reroll_effects(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        combat_type: str,
    ):
        """Step 3: Process re-roll effects like Bullseye."""
        # Identify units with re-roll SAIs
        for unit_name, face_results in roll_results.items():
            for face_result in face_results:
                if face_result and "bullseye" in face_result.lower():
                    # Bullseye allows re-rolling the unit
                    reroll = RerollEffect(
                        unit_name=unit_name,
                        source="Bullseye",
                        description=f"{unit_name} may re-roll due to Bullseye",
                        force_reroll=False,
                    )
                    result.reroll_effects.append(reroll)

        # Note: Actual re-rolling would happen in the UI/game engine
        # This method identifies what can be re-rolled

    def _identify_and_apply_sai_effects(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        is_attacker: bool,
        terrain_elements: List[str],
    ):
        """Step 4: Identify and apply SAI effects."""
        # Process SAI faces to generate modifiers
        for unit_name, face_results in roll_results.items():
            # Collect all SAI faces (including specific SAI names)
            sai_faces = [face for face in face_results if self._is_sai_face(face)]

            if sai_faces:
                unit_data = self._find_unit_data(unit_name, army_units)
                if unit_data:
                    self._generate_sai_modifiers(result, unit_data, sai_faces, combat_type, is_attacker)

    def _is_sai_face(self, face_result: str) -> bool:
        """Check if a face result is an SAI face."""
        face_name = face_result.lower().strip()
        return (
            face_name == "sai"  # Generic SAI
            or face_name in self.SAI_REGISTRY  # Specific SAI
        )

    def _determine_die_type(self, unit_data: Dict[str, Any]) -> str:
        """Determine the die type from unit data."""
        # Check unit type to determine die type
        unit_type = unit_data.get("unit_type", "").lower()
        size = unit_data.get("size", "").lower()

        # Check for specific die types based on unit classification
        if "monster" in unit_type:
            return "monster"
        elif "artifact" in unit_type:
            return "artifact"
        elif "medallion" in unit_type:
            return "medallion"
        elif "relic" in unit_type:
            return "relic"
        elif "champion" in unit_type:
            return "champion"
        elif "large" in size and ("equipment" in unit_type or "dragonkin" in unit_type):
            if "equipment" in unit_type:
                return "large_equipment"
            else:
                return "large_dragonkin"
        else:
            # Default to six-sided for regular units
            return "six_sided"

    def _calculate_x_value_for_sai(self, die_type: str, icons_rolled: int) -> int:
        """Calculate X-value for SAI based on die type and icons rolled."""
        if die_type == "six_sided":
            # For 6-sided dice, X = number of icons on the face
            # For now, assume 1 icon per face (will be improved with actual face data)
            return icons_rolled  # Each SAI face counts as 1 icon
        elif die_type in ["large_equipment", "large_dragonkin"]:
            return 3  # Fixed value per rules
        elif die_type in ["monster", "artifact", "medallion", "relic", "champion"]:
            return 4  # Fixed value per rules
        else:
            # Default fallback
            return icons_rolled

    def _generate_sai_modifiers(
        self,
        result: CombatRollResult,
        unit_data: Dict[str, Any],
        sai_faces_rolled: List[str],
        combat_type: str,
        is_attacker: bool,
    ):
        """Generate modifiers from SAI effects using the comprehensive SAI registry."""
        unit_name = unit_data.get("name", "Unknown")

        # Process each SAI face rolled
        for sai_face in sai_faces_rolled:
            sai_name = sai_face.lower().strip()

            # Skip generic "sai" faces - they need specific SAI identification
            if sai_name == "sai":
                continue

            # Look up SAI in registry
            if sai_name in self.SAI_REGISTRY:
                sai_info = self.SAI_REGISTRY[sai_name]
                self._apply_specific_sai_effect(result, unit_data, sai_name, sai_info, 1, combat_type, is_attacker)
            else:
                # Unknown SAI - log for debugging
                result.special_notes.append(f"Unknown SAI: {sai_name} on {unit_name}")

    def _apply_specific_sai_effect(
        self,
        result: CombatRollResult,
        unit_data: Dict[str, Any],
        sai_name: str,
        sai_info: Dict[str, Any],
        icons_rolled: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply a specific SAI effect based on the rules registry."""
        unit_name = unit_data.get("name", "Unknown")

        # Check if this SAI applies to the current roll type
        applies_to = sai_info.get("applies", [])
        current_roll_type = self._normalize_roll_type(combat_type, is_attacker)

        if not ("any" in applies_to or current_roll_type in applies_to):
            return  # SAI doesn't apply to this roll type

        # Calculate X-value based on die type and face data
        # For now, assume 6-sided dice unless unit data indicates otherwise
        die_type = self._determine_die_type(unit_data)
        x_value = self._calculate_x_value_for_sai(die_type, icons_rolled)

        # Apply specific SAI effects
        if sai_name == "cantrip":
            self._apply_cantrip_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "bash":
            self._apply_bash_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "bullseye":
            self._apply_bullseye_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "counter":
            self._apply_counter_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "fly":
            self._apply_fly_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "regenerate":
            self._apply_regenerate_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "rend":
            self._apply_rend_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "trample":
            self._apply_trample_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "vanish":
            self._apply_vanish_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "attune":
            self._apply_attune_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "belly":
            self._apply_belly_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "breath":
            self._apply_breath_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "charge":
            self._apply_charge_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "charm":
            self._apply_charm_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "choke":
            self._apply_choke_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "cloak":
            self._apply_cloak_effect(result, unit_name, x_value, combat_type, is_attacker)
        elif sai_name == "elevate":
            self._apply_elevate_effect(result, unit_name, x_value, combat_type, is_attacker)
        # Add more specific SAI implementations here
        else:
            # Generic SAI handling - log that it needs implementation
            result.special_notes.append(f"{unit_name} {sai_name.title()}: Effect needs implementation (X={x_value})")

    def _normalize_roll_type(self, combat_type: str, is_attacker: bool) -> str:
        """Normalize roll type to match SAI applies conditions."""
        if combat_type == "save":
            return "save"
        elif combat_type == "magic":
            return "magic"
        elif combat_type == "maneuver":
            return "maneuver"
        elif combat_type == "melee":
            return "melee"
        elif combat_type == "missile":
            return "missile"
        else:
            return "other"

    def _apply_cantrip_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Cantrip SAI effect."""
        if combat_type == "magic":
            # Generate X magic results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Cantrip",
                target_result_type="magic",
                description=f"{unit_name} Cantrip: +{x_value} magic results",
            )
            result.modifiers.append(modifier)
        elif combat_type in ["melee", "missile", "save"] and not is_attacker:
            # Generate X magic results for cantrip spells only during non-maneuver rolls
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Cantrip",
                target_result_type="magic",
                description=f"{unit_name} Cantrip: +{x_value} magic (cantrip spells only)",
            )
            result.modifiers.append(modifier)
            result.sai_results.append(
                SAIResult(
                    sai_type="cantrip",
                    effect_description=f"{unit_name} Cantrip: +{x_value} magic (cantrip spells only)",
                    magic_bonus=x_value,
                    special_effects=["cantrip_magic"],
                )
            )

    def _apply_bash_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Bash SAI effect."""
        if combat_type == "save" and not is_attacker:
            # Generate X save results (simplified - full effect involves targeting)
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Bash",
                target_result_type="save",
                description=f"{unit_name} Bash: +{x_value} save results",
            )
            result.modifiers.append(modifier)

    def _apply_bullseye_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Bullseye SAI effect."""
        if combat_type == "missile" and is_attacker:
            # Note that this unit can re-roll (targeting implementation needed)
            reroll = RerollEffect(
                unit_name=unit_name,
                source="Bullseye",
                description=f"{unit_name} may re-roll due to Bullseye (targets {x_value} health-worth)",
                force_reroll=False,
            )
            result.reroll_effects.append(reroll)
            result.special_notes.append(f"{unit_name} Bullseye: Targets {x_value} health-worth, then re-rolls")
        elif combat_type == "dragon_attack":
            # Generate X missile results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Bullseye",
                target_result_type="missile",
                description=f"{unit_name} Bullseye: +{x_value} missile results",
            )
            result.modifiers.append(modifier)

    def _apply_counter_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Counter SAI effect."""
        if combat_type == "save" and not is_attacker:
            # Generate X save results and inflict X damage
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Counter",
                target_result_type="save",
                description=f"{unit_name} Counter: +{x_value} save results and {x_value} damage to attacker",
            )
            result.modifiers.append(modifier)
            result.special_notes.append(f"{unit_name} Counter: Inflicts {x_value} damage on attacking army")
        elif combat_type == "melee" and is_attacker:
            # Generate X melee results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Counter",
                target_result_type="melee",
                description=f"{unit_name} Counter: +{x_value} melee results",
            )
            result.modifiers.append(modifier)

    def _apply_fly_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Fly SAI effect."""
        # Fly generates X maneuver or X save results during any roll
        # For now, generate maneuver during maneuver rolls, save during save rolls
        if combat_type == "maneuver":
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Fly",
                target_result_type="maneuver",
                description=f"{unit_name} Fly: +{x_value} maneuver results",
            )
            result.modifiers.append(modifier)
        elif combat_type == "save":
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Fly",
                target_result_type="save",
                description=f"{unit_name} Fly: +{x_value} save results",
            )
            result.modifiers.append(modifier)
        else:
            # For other roll types, offer choice (simplified - actual implementation would need UI)
            result.special_notes.append(f"{unit_name} Fly: Can generate {x_value} maneuver OR {x_value} save results")

    def _apply_regenerate_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Regenerate SAI effect."""
        if combat_type != "maneuver":  # Non-maneuver roll
            # Choice: Generate X save results OR return X health-worth from DUA
            # For now, generate save results (actual implementation would need UI choice)
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Regenerate",
                target_result_type="save",
                description=f"{unit_name} Regenerate: +{x_value} save results",
            )
            result.modifiers.append(modifier)
            result.special_notes.append(
                f"{unit_name} Regenerate: Alternative - return {x_value} health-worth from DUA to army"
            )

    def _apply_rend_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Rend SAI effect."""
        if combat_type in ["melee", "dragon_attack"]:
            # Generate X melee results and re-roll
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Rend",
                target_result_type="melee",
                description=f"{unit_name} Rend: +{x_value} melee results",
            )
            result.modifiers.append(modifier)
            reroll = RerollEffect(
                unit_name=unit_name,
                source="Rend",
                description=f"{unit_name} may re-roll due to Rend",
                force_reroll=False,
            )
            result.reroll_effects.append(reroll)
        elif combat_type == "maneuver":
            # Generate X maneuver results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Rend",
                target_result_type="maneuver",
                description=f"{unit_name} Rend: +{x_value} maneuver results",
            )
            result.modifiers.append(modifier)

    def _apply_trample_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Trample SAI effect."""
        # Trample generates X maneuver and X melee results during any roll
        maneuver_modifier = RollModifier(
            modifier_type="add",
            value=x_value,
            source=f"{unit_name} Trample",
            target_result_type="maneuver",
            description=f"{unit_name} Trample: +{x_value} maneuver results",
        )
        result.modifiers.append(maneuver_modifier)

        melee_modifier = RollModifier(
            modifier_type="add",
            value=x_value,
            source=f"{unit_name} Trample",
            target_result_type="melee",
            description=f"{unit_name} Trample: +{x_value} melee results",
        )
        result.modifiers.append(melee_modifier)

    def _apply_vanish_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Vanish SAI effect."""
        if combat_type == "save":
            # Generate X save results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Vanish",
                target_result_type="save",
                description=f"{unit_name} Vanish: +{x_value} save results",
            )
            result.modifiers.append(modifier)
            # Note that unit may move (movement implementation needed)
            result.special_notes.append(f"{unit_name} may move to any terrain or Reserve Area after Vanish")

    def _apply_attune_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Attune SAI effect."""
        if combat_type == "magic" and is_attacker:
            # Generate X magic results of any element
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Attune",
                target_result_type="magic",
                description=f"{unit_name} Attune: +{x_value} magic results of any element",
            )
            result.modifiers.append(modifier)
            result.special_notes.append(
                f"{unit_name} Attune: May change normal magic results of one unit to same element"
            )

    def _apply_belly_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Belly SAI effect."""
        # Belly removes automatic save results
        result.special_notes.append(f"{unit_name} Belly: Unit loses automatic save results")

    def _apply_breath_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Breath SAI effect."""
        if combat_type == "melee" and is_attacker:
            # Create targeting request for X health-worth of units
            targeting_request = self.create_targeting_request("breath", unit_name, x_value, combat_type, is_attacker)
            if targeting_request:
                result.targeting_requests.append(targeting_request)
                result.special_notes.append(
                    f"{unit_name} Breath: Targets {x_value} health-worth of defending units (killed outright)"
                )

    def _apply_charge_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Charge SAI effect."""
        if combat_type == "melee" and is_attacker:
            # Maneuver results count as melee, defending army makes combination roll
            result.special_notes.append(
                f"{unit_name} Charge: All maneuver results count as melee; defender makes combination save+melee roll"
            )

    def _apply_charm_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Charm SAI effect."""
        if combat_type == "melee" and is_attacker:
            # Create targeting request for units that don't save
            targeting_request = self.create_targeting_request("charm", unit_name, x_value, combat_type, is_attacker)
            if targeting_request:
                result.targeting_requests.append(targeting_request)
                result.special_notes.append(
                    f"{unit_name} Charm: Target {x_value} health-worth don't save; their results added to attacker"
                )

    def _apply_choke_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Choke SAI effect."""
        if combat_type == "melee" and is_attacker:
            # Create targeting request for units that rolled ID (delayed effect)
            targeting_request = self.create_targeting_request("choke", unit_name, x_value, combat_type, is_attacker)
            if targeting_request:
                result.targeting_requests.append(targeting_request)

            # Also create delayed effect
            delayed_effect = DelayedEffect(
                effect_type="target_id_units",
                source="Choke",
                target=f"{x_value} health-worth that rolled ID",
                value=x_value,
                description=f"{unit_name} Choke: Target {x_value} health-worth that rolled ID (killed, no save results counted)",
            )
            result.delayed_effects.append(delayed_effect)

    def _apply_cloak_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Cloak SAI effect."""
        if combat_type in ["save", "dragon_attack"]:
            # Add X non-magical save results until next turn
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Cloak",
                target_result_type="save",
                description=f"{unit_name} Cloak: +{x_value} non-magical save results (until next turn)",
            )
            result.modifiers.append(modifier)
        elif combat_type == "magic" and is_attacker:
            # Generate X magic results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Cloak",
                target_result_type="magic",
                description=f"{unit_name} Cloak: +{x_value} magic results",
            )
            result.modifiers.append(modifier)

    def _apply_elevate_effect(
        self,
        result: CombatRollResult,
        unit_name: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ):
        """Apply Elevate SAI effect."""
        if combat_type == "maneuver":
            # Generate X maneuver results
            modifier = RollModifier(
                modifier_type="add",
                value=x_value,
                source=f"{unit_name} Elevate",
                target_result_type="maneuver",
                description=f"{unit_name} Elevate: +{x_value} maneuver results",
            )
            result.modifiers.append(modifier)
        elif combat_type == "missile" and is_attacker:
            # Double one unit's missile results
            result.special_notes.append(f"{unit_name} Elevate: Double one unit's missile results")
        elif combat_type == "save" and not is_attacker:
            # Double one unit's save results against melee
            result.special_notes.append(f"{unit_name} Elevate: Double one unit's save results")
        elif combat_type == "dragon_attack":
            # Double one unit's missile or save results
            result.special_notes.append(f"{unit_name} Elevate: Double one unit's missile or save results")

    def _count_non_sai_results(self, result: CombatRollResult) -> Dict[str, int]:
        """Step 5: Count all non-SAI generated action results."""
        return {
            "melee": result.raw_melee,
            "missile": result.raw_missile,
            "magic": result.raw_magic,
            "save": result.raw_save,
            "maneuver": result.raw_maneuver,
        }

    def _apply_subtract_modifiers(self, result: CombatRollResult, subtotal: Dict[str, int]) -> Dict[str, int]:
        """Step 6: Apply modifiers that subtract (minimum 0)."""
        for modifier in result.modifiers:
            if modifier.modifier_type == "subtract":
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = max(0, current_value - modifier.value)
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  Subtract: {modifier.description} ({current_value} -> {new_value})")
        return subtotal

    def _apply_divide_modifiers(self, result: CombatRollResult, subtotal: Dict[str, int]) -> Dict[str, int]:
        """Step 7: Apply modifiers that divide (round down)."""
        for modifier in result.modifiers:
            if modifier.modifier_type == "divide":
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = current_value // modifier.value
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  Divide: {modifier.description} ({current_value} -> {new_value})")
        return subtotal

    def _add_sai_generated_results(self, result: CombatRollResult, subtotal: Dict[str, int]) -> Dict[str, int]:
        """Step 8: Add SAI generated action results."""
        for modifier in result.modifiers:
            if modifier.modifier_type == "add" and "SAI" in modifier.source:
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = current_value + modifier.value
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  SAI Add: {modifier.description} ({current_value} -> {new_value})")
        return subtotal

    def _apply_multiply_modifiers(self, result: CombatRollResult, subtotal: Dict[str, int]) -> Dict[str, int]:
        """Step 9: Apply modifiers that multiply."""
        for modifier in result.modifiers:
            if modifier.modifier_type == "multiply":
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = current_value * modifier.value
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  Multiply: {modifier.description} ({current_value} -> {new_value})")
        return subtotal

    def _apply_add_modifiers_and_counts_as(
        self,
        result: CombatRollResult,
        subtotal: Dict[str, int],
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        terrain_elements: List[str],
    ):
        """Step 10: Apply add modifiers and counts-as results for final total."""
        # Apply non-SAI add modifiers
        for modifier in result.modifiers:
            if modifier.modifier_type == "add" and "SAI" not in modifier.source:
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = current_value + modifier.value
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  Add: {modifier.description} ({current_value} -> {new_value})")

        # Apply counts-as modifiers
        for modifier in result.modifiers:
            if modifier.modifier_type == "counts_as":
                current_value = subtotal.get(modifier.target_result_type, 0)
                new_value = current_value + modifier.value
                subtotal[modifier.target_result_type] = new_value
                result.resolution_log.append(f"  Counts-as: {modifier.description} ({current_value} -> {new_value})")

        # Update final results
        result.final_melee = subtotal.get("melee", 0)
        result.final_missile = subtotal.get("missile", 0)
        result.final_magic = subtotal.get("magic", 0)
        result.final_save = subtotal.get("save", 0)
        result.final_maneuver = subtotal.get("maneuver", 0)

    def _process_roll_with_10_step_resolution(
        self,
        roll_results: Dict[str, List[str]],
        combat_type: str,
        army_units: List[Dict[str, Any]],
        is_attacker: bool,
        terrain_elements: Optional[List[str]],
        terrain_eighth_face_controlled: bool,
        player_name: Optional[str],
        opponent_name: Optional[str],
        delayed_effects_from_attacker: Optional[List[DelayedEffect]],
    ) -> CombatRollResult:
        """
        Implement the 10-step die roll resolution process from the rules.
        """
        result = CombatRollResult()
        if terrain_elements is None:
            terrain_elements = []
        if delayed_effects_from_attacker is None:
            delayed_effects_from_attacker = []

        # STEP 1: Roll the dice (already done - we have roll_results)
        result.resolution_log.append("Step 1: Dice rolled")
        self._count_raw_results(result, roll_results)

        # STEP 2: Apply delayed SAI effects from attacker (if this is a save roll)
        result.resolution_log.append("Step 2: Applying delayed effects from attacker")
        if combat_type == "save" and delayed_effects_from_attacker:
            self._apply_delayed_effects(result, delayed_effects_from_attacker, roll_results, army_units)

        # STEP 3: Handle re-roll effects
        result.resolution_log.append("Step 3: Processing re-roll effects")
        self._process_reroll_effects(result, roll_results, army_units, combat_type)

        # STEP 4: Identify and apply SAI effects
        result.resolution_log.append("Step 4: Processing SAI effects")
        self._identify_and_apply_sai_effects(
            result, roll_results, combat_type, army_units, is_attacker, terrain_elements
        )

        # STEP 5: Count non-SAI generated action results
        result.resolution_log.append("Step 5: Counting non-SAI action results")
        subtotal = self._count_non_sai_results(result)

        # STEP 6: Apply subtract modifiers
        result.resolution_log.append("Step 6: Applying subtract modifiers")
        subtotal = self._apply_subtract_modifiers(result, subtotal)

        # STEP 7: Apply divide modifiers
        result.resolution_log.append("Step 7: Applying divide modifiers")
        subtotal = self._apply_divide_modifiers(result, subtotal)

        # STEP 8: Add SAI generated action results
        result.resolution_log.append("Step 8: Adding SAI generated results")
        subtotal = self._add_sai_generated_results(result, subtotal)

        # STEP 9: Apply multiply modifiers
        result.resolution_log.append("Step 9: Applying multiply modifiers")
        subtotal = self._apply_multiply_modifiers(result, subtotal)

        # STEP 10: Apply add modifiers and counts-as results
        result.resolution_log.append("Step 10: Applying add modifiers and counts-as results")
        self._apply_add_modifiers_and_counts_as(result, subtotal, roll_results, army_units, terrain_elements)

        # Process ID faces and species abilities (these add counts-as modifiers)
        self._process_id_faces_for_resolution(
            result, roll_results, army_units, combat_type, terrain_eighth_face_controlled
        )
        self._process_species_abilities_for_resolution(
            result, roll_results, army_units, combat_type, is_attacker, terrain_elements, player_name, opponent_name
        )

        result.resolution_log.append("Resolution complete")
        return result

    def _process_id_faces_for_resolution(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        combat_type: str,
        terrain_eighth_face_controlled: bool,
    ):
        """Process ID face bonuses using the resolution engine."""
        for unit_name, face_results in roll_results.items():
            id_count = sum(1 for face in face_results if face.lower().strip() == "id")

            if id_count > 0:
                unit_data = self._find_unit_data(unit_name, army_units)
                if unit_data:
                    health = unit_data.get("health", 1)
                    id_bonus = id_count * health

                    # Apply terrain eighth face doubling
                    if terrain_eighth_face_controlled:
                        id_bonus *= 2
                        eighth_face_note = " (doubled by terrain eighth face)"
                    else:
                        eighth_face_note = ""

                    # Create counts-as modifier for ID results
                    target_type = combat_type if combat_type in ["melee", "missile", "magic", "maneuver"] else "save"
                    modifier = RollModifier(
                        modifier_type="counts_as",
                        value=id_bonus,
                        source=f"{unit_name} ID",
                        target_result_type=target_type,
                        description=f"{unit_name} ID: +{id_bonus} {target_type}{eighth_face_note}",
                    )
                    result.modifiers.append(modifier)

    def _process_species_abilities_for_resolution(
        self,
        result: CombatRollResult,
        roll_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        combat_type: str,
        is_attacker: bool,
        terrain_elements: List[str],
        player_name: Optional[str],
        opponent_name: Optional[str],
    ):
        """Process species abilities using counts-as modifiers."""
        for unit_name, face_results in roll_results.items():
            unit_data = self._find_unit_data(unit_name, army_units)
            if not unit_data:
                continue

            species = unit_data.get("species", "")

            # Dwarven Might: saves count as melee at fire terrain during counter-attack
            if species == "Dwarves" and combat_type == "melee" and not is_attacker and "fire" in terrain_elements:
                save_count = sum(1 for face in face_results if face.lower().strip() in ["s", "save"])
                if save_count > 0:
                    modifier = RollModifier(
                        modifier_type="counts_as",
                        value=save_count,
                        source="Dwarven Might",
                        target_result_type="melee",
                        description=f"{unit_name} Dwarven Might: {save_count} saves count as melee",
                    )
                    result.modifiers.append(modifier)

            # Coastal Dodge: maneuver counts as save at water terrain
            if (
                species == "Coral Elves"
                and combat_type in ["save", "melee", "missile"]
                and not is_attacker
                and "water" in terrain_elements
            ):
                maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])
                if maneuver_count > 0:
                    modifier = RollModifier(
                        modifier_type="counts_as",
                        value=maneuver_count,
                        source="Coastal Dodge",
                        target_result_type="save",
                        description=f"{unit_name} Coastal Dodge: {maneuver_count} maneuver count as save",
                    )
                    result.modifiers.append(modifier)

            # Add other species abilities as counts-as modifiers
            self._add_other_species_counts_as_modifiers(
                result, unit_data, face_results, combat_type, is_attacker, terrain_elements
            )

    def _add_other_species_counts_as_modifiers(
        self,
        result: CombatRollResult,
        unit_data: Dict[str, Any],
        face_results: List[str],
        combat_type: str,
        is_attacker: bool,
        terrain_elements: List[str],
    ):
        """Add remaining species abilities as counts-as modifiers."""
        unit_name = unit_data.get("name", "Unknown")
        species = unit_data.get("species", "")

        # Mountain Master: melee counts as maneuver at earth terrain
        if species == "Dwarves" and combat_type == "maneuver" and "earth" in terrain_elements:
            melee_count = sum(1 for face in face_results if face.lower().strip() in ["m", "melee"])
            if melee_count > 0:
                modifier = RollModifier(
                    modifier_type="counts_as",
                    value=melee_count,
                    source="Mountain Master",
                    target_result_type="maneuver",
                    description=f"{unit_name} Mountain Master: {melee_count} melee count as maneuver",
                )
                result.modifiers.append(modifier)

        # Stampede: maneuver counts as melee during counter-attack at earth+air
        if (
            species == "Feral"
            and combat_type == "melee"
            and not is_attacker
            and "earth" in terrain_elements
            and "air" in terrain_elements
        ):
            maneuver_count = sum(1 for face in face_results if face.lower().strip() in ["ma", "maneuver"])
            if maneuver_count > 0:
                modifier = RollModifier(
                    modifier_type="counts_as",
                    value=maneuver_count,
                    source="Stampede",
                    target_result_type="melee",
                    description=f"{unit_name} Stampede: {maneuver_count} maneuver count as melee",
                )
                result.modifiers.append(modifier)

        # Flaming Shields: saves count as melee during attack at fire terrain
        if species == "Firewalkers" and combat_type == "melee" and is_attacker and "fire" in terrain_elements:
            save_count = sum(1 for face in face_results if face.lower().strip() in ["s", "save"])
            if save_count > 0:
                modifier = RollModifier(
                    modifier_type="counts_as",
                    value=save_count,
                    source="Flaming Shields",
                    target_result_type="melee",
                    description=f"{unit_name} Flaming Shields: {save_count} saves count as melee",
                )
                result.modifiers.append(modifier)

    # Targeting system methods
    def create_targeting_request(
        self,
        sai_name: str,
        source_unit: str,
        x_value: int,
        combat_type: str,
        is_attacker: bool,
    ) -> Optional[TargetingRequest]:
        """Create a targeting request for SAIs that require unit selection."""
        sai_info = self.SAI_REGISTRY.get(sai_name.lower())
        if not sai_info:
            return None

        # Determine target type and army based on SAI rules
        target_army = "defending" if is_attacker else "attacking"
        target_type = "unit"  # Default
        targeting_criteria = "none"
        must_target_fullest_extent = True

        # Specific targeting rules per SAI
        if sai_name == "breath":
            target_type = "health_worth"
            targeting_criteria = "none"
        elif sai_name == "bullseye":
            target_type = "health_worth"
            targeting_criteria = "save_roll_required"
        elif sai_name == "charm":
            target_type = "health_worth"
            targeting_criteria = "no_save_roll"
        elif sai_name == "choke":
            target_type = "health_worth"
            targeting_criteria = "rolled_id"
        elif sai_name == "coil":
            target_type = "specific_unit"
            target_army = "defending" if is_attacker else "attacking"
            x_value = 1  # Always targets one unit
        elif sai_name == "bash":
            target_type = "specific_unit"
            target_army = "attacking" if not is_attacker else "defending"  # Targets attacker from defender
            x_value = 1  # Always targets one unit

        return TargetingRequest(
            sai_name=sai_name,
            source_unit=source_unit,
            target_type=target_type,
            target_count=x_value,
            target_army=target_army,
            targeting_criteria=targeting_criteria,
            effect_description=str(sai_info.get("description", "")),
            must_target_fullest_extent=must_target_fullest_extent,
        )

    def apply_targeting_restrictions(
        self,
        targeting_request: TargetingRequest,
        available_units: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Apply targeting restrictions based on SAI rules and fullest extent rule."""
        sai_name = targeting_request.sai_name.lower()

        # Check if this army/unit has already been targeted by multiply/divide SAIs
        restricted_units = []
        for unit in available_units:
            unit_id = unit.get("unique_id", unit.get("name", ""))

            # Check multiply/divide restrictions
            if self._is_restricted_by_multiply_divide(unit_id, targeting_request):
                continue

            # Apply specific targeting criteria
            if targeting_request.targeting_criteria == "rolled_id":
                # Only target units that rolled an ID icon
                if not self._unit_rolled_id(unit):
                    continue
            elif targeting_request.targeting_criteria == "save_roll_required":
                # Units that need to make save rolls
                pass  # No additional filtering needed
            elif targeting_request.targeting_criteria == "no_save_roll":
                # Units that won't make save rolls
                pass  # Implementation depends on game state

            restricted_units.append(unit)

        return restricted_units

    def _is_restricted_by_multiply_divide(self, unit_id: str, targeting_request: TargetingRequest) -> bool:
        """Check if unit is restricted due to multiply/divide SAI rules."""
        # Check targeting restrictions registry
        sai_name = targeting_request.sai_name.lower()

        # SAIs that multiply or divide cannot target same army/unit multiple times
        multiply_divide_sais = ["elevate", "frost_breath", "galeforce"]

        if sai_name in multiply_divide_sais:
            # Check if this unit has already been targeted by a multiply/divide SAI
            return unit_id in self._targeting_restrictions.get("multiply_divide_targeted", set())

        return False

    def _unit_rolled_id(self, unit: Dict[str, Any]) -> bool:
        """Check if a unit rolled an ID icon (for SAIs like Choke)."""
        # This would need to be tracked during the actual dice rolling
        # For now, return False as a placeholder
        # In actual implementation, this info would come from roll results
        rolled_id = unit.get("rolled_id", False)
        return bool(rolled_id)

    def find_targetable_units(
        self,
        targeting_request: TargetingRequest,
        all_armies: Dict[str, List[Dict[str, Any]]],
        current_terrain: str,
    ) -> List[Dict[str, Any]]:
        """Find all units that can be targeted by this SAI effect."""
        targetable_units = []

        # Determine which armies to search
        target_army_type = targeting_request.target_army

        for army_id, army_units in all_armies.items():
            # Filter by army type (attacking/defending/any)
            if target_army_type == "defending" and "defending" not in army_id.lower():
                continue
            elif target_army_type == "attacking" and "attacking" not in army_id.lower():
                continue
            elif target_army_type == "any":
                pass  # All armies are valid

            # Filter units at current terrain
            for unit in army_units:
                unit_location = unit.get("location", "")
                if unit_location == current_terrain:
                    targetable_units.append(unit)

        # Apply targeting restrictions
        restricted_units = self.apply_targeting_restrictions(targeting_request, targetable_units)

        return restricted_units

    def select_targets_fullest_extent(
        self,
        targeting_request: TargetingRequest,
        available_units: List[Dict[str, Any]],
    ) -> TargetingResult:
        """Select targets following the fullest extent possible rule."""
        result = TargetingResult(success=False)

        if not available_units:
            result.targeting_notes.append("No valid targets available")
            return result

        target_count = targeting_request.target_count
        target_type = targeting_request.target_type

        if target_type == "specific_unit":
            # Target a specific number of individual units
            selected_units = available_units[:target_count]
            result.targeted_units = selected_units
            result.total_health_targeted = sum(unit.get("health", 1) for unit in selected_units)
            result.success = len(selected_units) > 0

        elif target_type == "health_worth":
            # Target up to X health-worth of units
            selected_units = []
            health_targeted = 0

            # Sort by health to optimize targeting (smallest first for fullest extent)
            sorted_units = sorted(available_units, key=lambda u: u.get("health", 1))

            for unit in sorted_units:
                unit_health = unit.get("health", 1)
                if health_targeted + unit_health <= target_count:
                    selected_units.append(unit)
                    health_targeted += unit_health

                    # Check if we've reached the target
                    if health_targeted == target_count:
                        break

            # If we can't reach exact target, apply fullest extent rule
            if health_targeted < target_count and targeting_request.must_target_fullest_extent:
                # Try to target larger units if they would fit
                remaining_capacity = target_count - health_targeted
                larger_units = [
                    u for u in available_units if u not in selected_units and u.get("health", 1) <= remaining_capacity
                ]

                if larger_units:
                    # Add the largest unit that fits
                    largest_unit = max(larger_units, key=lambda u: u.get("health", 1))
                    selected_units.append(largest_unit)
                    health_targeted += largest_unit.get("health", 1)

            result.targeted_units = selected_units
            result.total_health_targeted = health_targeted
            result.success = len(selected_units) > 0

            if health_targeted < target_count:
                result.targeting_notes.append(
                    f"Could only target {health_targeted}/{target_count} health-worth (fullest extent applied)"
                )
            else:
                result.targeting_notes.append(f"Successfully targeted {health_targeted} health-worth")

        elif target_type == "army":
            # Target entire armies
            result.targeting_notes.append("Army targeting not yet implemented")

        return result

    def process_targeting_request(
        self,
        targeting_request: TargetingRequest,
        all_armies: Dict[str, List[Dict[str, Any]]],
        current_terrain: str,
    ) -> TargetingResult:
        """Process a complete targeting request and return the result."""
        # Find all targetable units
        targetable_units = self.find_targetable_units(targeting_request, all_armies, current_terrain)

        # Select targets using fullest extent rule
        targeting_result = self.select_targets_fullest_extent(targeting_request, targetable_units)

        # Record targeting restrictions for multiply/divide SAIs
        if targeting_result.success:
            self._record_targeting_restriction(targeting_request, targeting_result)

        return targeting_result

    def _record_targeting_restriction(
        self,
        targeting_request: TargetingRequest,
        targeting_result: TargetingResult,
    ):
        """Record targeting restrictions to prevent multiple multiply/divide effects."""
        sai_name = targeting_request.sai_name.lower()
        multiply_divide_sais = ["elevate", "frost_breath", "galeforce"]

        if sai_name in multiply_divide_sais:
            # Initialize restrictions if needed
            if "multiply_divide_targeted" not in self._targeting_restrictions:
                self._targeting_restrictions["multiply_divide_targeted"] = set()

            # Record all targeted units
            for unit in targeting_result.targeted_units:
                unit_id = unit.get("unique_id", unit.get("name", ""))
                self._targeting_restrictions["multiply_divide_targeted"].add(unit_id)

    def clear_targeting_restrictions(self):
        """Clear all targeting restrictions (call at start of new turn)."""
        self._targeting_restrictions.clear()
        self._pending_targeting_requests.clear()

    def get_pending_targeting_requests(self) -> List[TargetingRequest]:
        """Get all pending targeting requests that need UI resolution."""
        return self._pending_targeting_requests.copy()

    def add_pending_targeting_request(self, request: TargetingRequest):
        """Add a targeting request to the pending list."""
        self._pending_targeting_requests.append(request)

    def remove_pending_targeting_request(self, request: TargetingRequest):
        """Remove a targeting request from the pending list."""
        if request in self._pending_targeting_requests:
            self._pending_targeting_requests.remove(request)
