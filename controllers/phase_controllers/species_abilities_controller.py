"""
Species Abilities Controller for Dragon Dice

Handles the Species Abilities phase where players can activate race-specific abilities:
- Undead necromancy and unit raising
- Dragonkin breath weapons and dragon summoning
- Elemental magic bonuses and terrain manipulation
- Feral pack abilities and natural terrain bonuses
- Special racial abilities and synergies
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get_optional


class SpeciesAbilitiesController(QObject):
    """
    Controller for Species Abilities phase interaction patterns.

    Manages race-specific ability activation, resource requirements,
    and ability resolution coordination.
    """

    # =============================================================================
    # SIGNALS
    # =============================================================================

    # Phase completion signals
    species_phase_completed = Signal()

    # Ability availability signals
    abilities_available = Signal(str, list)  # player_name, available_abilities
    ability_requirements_check = Signal(str, str, dict)  # player_name, ability_id, requirements

    # Ability activation signals
    ability_activated = Signal(str, str, dict)  # player_name, ability_id, activation_data
    ability_targeting_required = Signal(str, str, list)  # player_name, ability_id, valid_targets
    ability_resource_cost = Signal(str, dict)  # player_name, resource_cost

    # Necromancy-specific signals
    necromancy_available = Signal(str, list)  # player_name, raiseable_units
    unit_raised = Signal(str, dict)  # player_name, raised_unit_data

    # Dragon-specific signals
    dragon_summoning_available = Signal(str, list)  # player_name, summonable_dragons
    breath_weapon_available = Signal(str, list)  # player_name, breath_targets

    # Elemental-specific signals
    elemental_magic_bonus = Signal(str, str, int)  # player_name, magic_type, bonus_amount
    terrain_manipulation_available = Signal(str, list)  # player_name, manipulatable_terrains

    # Error and status signals
    species_error = Signal(str, str)  # error_type, error_message
    species_status_update = Signal(str)  # status_message

    def __init__(self, game_orchestrator, parent=None):
        super().__init__(parent)
        self.game_orchestrator = game_orchestrator
        self.core_engine = game_orchestrator.core_engine

        # Current species abilities state
        self.current_player = ""
        self.player_races = []  # Races the player has armies of
        self.abilities_context = {}  # Store ability state and targeting info
        self.abilities_used = []  # Track activated abilities this phase

        # Connect to game orchestrator signals
        self._setup_signal_connections()

    def _setup_signal_connections(self):
        """Set up signal connections with game orchestrator."""
        # Connect to orchestrator phase signals
        self.game_orchestrator.current_phase_changed.connect(self._handle_phase_change)
        self.game_orchestrator.current_player_changed.connect(self._handle_player_change)

        # Note: TurnFlowController will handle phase completion coordination
        # Individual controllers should not directly advance phases

    # =============================================================================
    # PHASE COORDINATION
    # =============================================================================

    @Slot(str)
    def _handle_phase_change(self, phase_display: str):
        """Handle phase changes from game orchestrator."""
        phase = self.game_orchestrator.get_current_phase()

        if phase == "SPECIES_ABILITIES":
            self._enter_species_abilities_phase()
        elif self.current_player:
            # Exiting species abilities phase
            self._exit_species_abilities_phase()

    @Slot(str)
    def _handle_player_change(self, player_name: str):
        """Handle player changes from game orchestrator."""
        self.current_player = player_name

    def _enter_species_abilities_phase(self):
        """Enter the species abilities phase."""
        self.current_player = self.game_orchestrator.get_current_player_name()
        self.abilities_context.clear()
        self.abilities_used.clear()

        print(f"SpeciesAbilitiesController: Entering species abilities phase for {self.current_player}")

        # Analyze player's races and available abilities
        self._analyze_species_abilities()

    def _exit_species_abilities_phase(self):
        """Exit species abilities phase."""
        print("SpeciesAbilitiesController: Exiting species abilities phase")

        self.current_player = ""
        self.player_races.clear()
        self.abilities_context.clear()
        self.abilities_used.clear()

    # =============================================================================
    # SPECIES ANALYSIS AND ABILITY DISCOVERY
    # =============================================================================

    def _analyze_species_abilities(self):
        """Analyze player's armies and identify available species abilities."""
        # Get all player armies to determine races
        player_armies = self.core_engine.get_player_armies_summary(self.current_player)

        # Extract unique races
        self.player_races = self._extract_player_races(player_armies)

        if not self.player_races:
            # No armies, skip phase
            self.species_status_update.emit("No armies for species abilities")
            self.species_phase_completed.emit()
            return

        # Get available abilities for each race
        available_abilities = self._get_available_abilities_by_race()

        if not available_abilities:
            # No abilities available, skip phase
            self.species_status_update.emit("No species abilities available")
            self.species_phase_completed.emit()
            return

        # Store abilities context
        self.abilities_context = {
            "player_races": self.player_races,
            "available_abilities": available_abilities,
            "resource_costs": self._calculate_ability_costs(available_abilities),
        }

        # Present abilities to player
        self.abilities_available.emit(self.current_player, available_abilities)

    def _extract_player_races(self, armies: List[Dict[str, Any]]) -> List[str]:
        """Extract unique races from player's armies."""
        races = set()

        for army_data in armies:
            army_race = strict_get_optional(army_data, "race", "")
            if army_race:
                races.add(army_race)

        return list(races)

    def _get_available_abilities_by_race(self) -> List[Dict[str, Any]]:
        """Get available species abilities for player's races."""
        available_abilities = []

        for race in self.player_races:
            race_abilities = self._get_race_specific_abilities(race)
            available_abilities.extend(race_abilities)

        return available_abilities

    def _get_race_specific_abilities(self, race: str) -> List[Dict[str, Any]]:
        """Get abilities specific to a race."""
        abilities = []

        if race.lower() == "undead":
            abilities.extend(self._get_undead_abilities())
        elif race.lower() == "dragonkin":
            abilities.extend(self._get_dragonkin_abilities())
        elif race.lower() in ["firewalker", "frostlander", "swampstalker", "amazon"]:
            abilities.extend(self._get_elemental_abilities(race))
        elif race.lower() == "feral":
            abilities.extend(self._get_feral_abilities())

        return abilities

    def _get_undead_abilities(self) -> List[Dict[str, Any]]:
        """Get Undead species abilities."""
        abilities = []

        # Necromancy - raise units from DUA
        if self._can_perform_necromancy():
            abilities.append(
                {
                    "id": "necromancy",
                    "name": "Necromancy",
                    "race": "undead",
                    "type": "raise_units",
                    "description": "Raise fallen units from DUA",
                    "resource_cost": {"death_magic": 1},
                    "requires_targeting": True,
                }
            )

        # Death Magic Enhancement
        if self._has_death_magic_units():
            abilities.append(
                {
                    "id": "death_magic_enhancement",
                    "name": "Death Magic Enhancement",
                    "race": "undead",
                    "type": "magic_bonus",
                    "description": "Enhance death magic abilities",
                    "resource_cost": {},
                    "requires_targeting": False,
                }
            )

        return abilities

    def _get_dragonkin_abilities(self) -> List[Dict[str, Any]]:
        """Get Dragonkin species abilities."""
        abilities = []

        # Breath Weapon
        if self._can_use_breath_weapon():
            abilities.append(
                {
                    "id": "breath_weapon",
                    "name": "Breath Weapon",
                    "race": "dragonkin",
                    "type": "area_attack",
                    "description": "Use draconic breath attack",
                    "resource_cost": {"dragon_essence": 1},
                    "requires_targeting": True,
                }
            )

        # Dragon Summoning
        if self._can_summon_dragons():
            abilities.append(
                {
                    "id": "dragon_summoning",
                    "name": "Dragon Summoning",
                    "race": "dragonkin",
                    "type": "summon",
                    "description": "Summon dragons to battlefield",
                    "resource_cost": {"dragon_essence": 2},
                    "requires_targeting": True,
                }
            )

        return abilities

    def _get_elemental_abilities(self, race: str) -> List[Dict[str, Any]]:
        """Get Elemental race abilities."""
        abilities = []

        # Magic affinity bonus
        magic_type = self._get_elemental_magic_type(race)
        if magic_type:
            abilities.append(
                {
                    "id": f"{race.lower()}_magic_affinity",
                    "name": f"{race} Magic Affinity",
                    "race": race.lower(),
                    "type": "magic_bonus",
                    "description": f"Gain bonus to {magic_type} magic",
                    "resource_cost": {},
                    "requires_targeting": False,
                }
            )

        # Terrain manipulation
        if self._can_manipulate_terrain(race):
            abilities.append(
                {
                    "id": f"{race.lower()}_terrain_control",
                    "name": f"{race} Terrain Control",
                    "race": race.lower(),
                    "type": "terrain_manipulation",
                    "description": f"Manipulate terrain using {race} abilities",
                    "resource_cost": {"elemental_power": 1},
                    "requires_targeting": True,
                }
            )

        return abilities

    def _get_feral_abilities(self) -> List[Dict[str, Any]]:
        """Get Feral species abilities."""
        abilities = []

        # Pack Hunt
        if self._can_pack_hunt():
            abilities.append(
                {
                    "id": "pack_hunt",
                    "name": "Pack Hunt",
                    "race": "feral",
                    "type": "coordinate_attack",
                    "description": "Coordinate pack hunting attack",
                    "resource_cost": {"pack_unity": 1},
                    "requires_targeting": True,
                }
            )

        # Natural Terrain Bonus
        abilities.append(
            {
                "id": "natural_terrain_affinity",
                "name": "Natural Terrain Affinity",
                "race": "feral",
                "type": "terrain_bonus",
                "description": "Gain bonuses in natural terrains",
                "resource_cost": {},
                "requires_targeting": False,
            }
        )

        return abilities

    # =============================================================================
    # ABILITY REQUIREMENT CHECKS
    # =============================================================================

    def _can_perform_necromancy(self) -> bool:
        """Check if player can perform necromancy."""
        # Check if there are units in DUA that can be raised
        dua_units = self.core_engine.get_player_dua_units(self.current_player)
        undead_units = [unit for unit in dua_units if strict_get_optional(unit, "race", "") == "undead"]

        return len(undead_units) > 0

    def _has_death_magic_units(self) -> bool:
        """Check if player has units capable of death magic."""
        armies = self.core_engine.get_player_armies_summary(self.current_player)

        for army in armies:
            units: List[Dict[str, Any]] = strict_get_optional(army, "units", [])
            for unit in units:
                if "death" in strict_get_optional(unit, "magic_types", []):
                    return True

        return False

    def _can_use_breath_weapon(self) -> bool:
        """Check if player can use dragonkin breath weapon."""
        # Check for dragonkin units with breath capability
        armies = self.core_engine.get_player_armies_summary(self.current_player)

        for army in armies:
            units: List[Dict[str, Any]] = strict_get_optional(army, "units", [])
            for unit in units:
                if strict_get_optional(unit, "race", "") == "dragonkin" and strict_get_optional(
                    unit, "has_breath_weapon", False
                ):
                    return True

        return False

    def _can_summon_dragons(self) -> bool:
        """Check if player can summon dragons."""
        # Check summoning pool for available dragons
        if hasattr(self.game_orchestrator, "summoning_pool_manager"):
            available_dragons = self.game_orchestrator.summoning_pool_manager.get_available_dragons()
            return len(available_dragons) > 0

        return False

    def _get_elemental_magic_type(self, race: str) -> Optional[str]:
        """Get elemental magic type for a race."""
        magic_mapping = {"firewalker": "fire", "frostlander": "water", "swampstalker": "earth", "amazon": "air"}
        return magic_mapping.get(race.lower())

    def _can_manipulate_terrain(self, race: str) -> bool:
        """Check if race can manipulate terrain."""
        # Check for appropriate terrains and elemental power
        terrain_data = self.core_engine.get_all_terrain_data()

        # Each elemental race can manipulate their preferred terrain types
        preferred_terrains = {
            "firewalker": ["volcano", "wasteland"],
            "frostlander": ["frozen_wasteland", "highlands"],
            "swampstalker": ["swampland", "forest"],
            "amazon": ["plains", "highlands"],
        }

        race_terrains = preferred_terrains.get(race.lower(), [])

        for _terrain_name, terrain_info in terrain_data.items():
            terrain_type = strict_get_optional(terrain_info, "terrain_type", "")
            if terrain_type.lower() in race_terrains:
                return True

        return False

    def _can_pack_hunt(self) -> bool:
        """Check if feral units can perform pack hunt."""
        armies = self.core_engine.get_player_armies_summary(self.current_player)

        # Need multiple feral units in same location for pack hunt
        feral_locations: Dict[str, int] = {}
        for army in armies:
            location = strict_get_optional(army, "location", "")
            units: List[Dict[str, Any]] = strict_get_optional(army, "units", [])

            feral_count = sum(1 for unit in units if strict_get_optional(unit, "race", "") == "feral")

            if feral_count > 0:
                feral_locations[location] = feral_locations.get(location, 0) + feral_count

        # Pack hunt requires 2+ feral units at same location
        return any(count >= 2 for count in feral_locations.values())

    def _calculate_ability_costs(self, abilities: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Calculate resource costs for abilities."""
        costs = {}

        for ability in abilities:
            ability_id = strict_get_optional(ability, "id", "")
            resource_cost: Dict[str, Any] = strict_get_optional(ability, "resource_cost", {})
            costs[ability_id] = resource_cost

        return costs

    # =============================================================================
    # ABILITY ACTIVATION
    # =============================================================================

    @Slot(str, str)
    def activate_ability(self, player_name: str, ability_id: str):
        """Handle ability activation from UI."""
        if player_name != self.current_player:
            self.species_error.emit("invalid_player", f"Not {player_name}'s turn")
            return

        # Find ability data
        ability_data = self._find_ability_by_id(ability_id)
        if not ability_data:
            self.species_error.emit("invalid_ability", f"Unknown ability: {ability_id}")
            return

        print(f"SpeciesAbilitiesController: {player_name} activating {ability_id}")

        # Check if ability requires targeting
        requires_targeting = strict_get_optional(ability_data, "requires_targeting", False)

        if requires_targeting:
            self._request_ability_targeting(ability_id, ability_data)
        else:
            self._execute_ability(ability_id, ability_data, {})

    def _find_ability_by_id(self, ability_id: str) -> Optional[Dict[str, Any]]:
        """Find ability data by ID."""
        available_abilities = self.abilities_context.get("available_abilities", [])

        for ability in available_abilities:
            if strict_get_optional(ability, "id", "") == ability_id:
                return dict(ability)  # Type cast to Dict[str, Any]

        return None

    def _request_ability_targeting(self, ability_id: str, ability_data: Dict[str, Any]):
        """Request targeting information for ability."""
        ability_type = strict_get_optional(ability_data, "type", "")

        if ability_type == "raise_units":
            targets = self._get_necromancy_targets()
        elif ability_type == "area_attack":
            targets = self._get_breath_weapon_targets()
        elif ability_type == "summon":
            targets = self._get_summoning_targets()
        elif ability_type == "terrain_manipulation":
            targets = self._get_terrain_manipulation_targets(ability_data)
        elif ability_type == "coordinate_attack":
            targets = self._get_pack_hunt_targets()
        else:
            targets = []

        if targets:
            self.ability_targeting_required.emit(self.current_player, ability_id, targets)
        else:
            self.species_error.emit("no_targets", f"No valid targets for {ability_id}")

    def _get_necromancy_targets(self) -> List[Dict[str, Any]]:
        """Get valid targets for necromancy ability."""
        dua_units = self.core_engine.get_player_dua_units(self.current_player)
        undead_units = []

        for unit in dua_units:
            if strict_get_optional(unit, "race", "") == "undead":
                undead_units.append(
                    {
                        "type": "unit",
                        "unit_id": strict_get_optional(unit, "unit_id", ""),
                        "name": strict_get_optional(unit, "name", ""),
                        "description": f"Raise {strict_get_optional(unit, 'name', 'unit')}",
                    }
                )

        return undead_units

    def _get_breath_weapon_targets(self) -> List[Dict[str, Any]]:
        """Get valid targets for breath weapon."""
        # Get locations where player has dragonkin and enemies present
        targets = []
        terrain_data = self.core_engine.get_all_terrain_data()

        for location, _terrain_info in terrain_data.items():
            if self._has_dragonkin_at_location(location) and self._has_enemies_at_location(location):
                targets.append(
                    {"type": "location", "location": location, "description": f"Breath attack at {location}"}
                )

        return targets

    def _get_summoning_targets(self) -> List[Dict[str, Any]]:
        """Get valid targets for dragon summoning."""
        targets = []

        # Can summon to any location where player has armies
        armies = self.core_engine.get_player_armies_summary(self.current_player)
        locations = {strict_get_optional(army, "location", "") for army in armies}

        for location in locations:
            if location and location != "reserves":
                targets.append(
                    {"type": "location", "location": location, "description": f"Summon dragon at {location}"}
                )

        return targets

    def _get_terrain_manipulation_targets(self, ability_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get valid targets for terrain manipulation."""
        targets = []
        race = strict_get_optional(ability_data, "race", "")

        # Get terrains this race can manipulate
        terrain_data = self.core_engine.get_all_terrain_data()

        for location, terrain_info in terrain_data.items():
            if self._can_race_manipulate_terrain(race, terrain_info):
                targets.append(
                    {
                        "type": "terrain",
                        "location": location,
                        "current_face": strict_get_optional(terrain_info, "current_face", 1),
                        "description": f"Manipulate terrain at {location}",
                    }
                )

        return targets

    def _get_pack_hunt_targets(self) -> List[Dict[str, Any]]:
        """Get valid targets for pack hunt."""
        targets = []

        # Get locations where player has multiple feral units
        armies = self.core_engine.get_player_armies_summary(self.current_player)

        for army in armies:
            location = strict_get_optional(army, "location", "")
            units: List[Dict[str, Any]] = strict_get_optional(army, "units", [])

            feral_count = sum(1 for unit in units if strict_get_optional(unit, "race", "") == "feral")

            if feral_count >= 2 and self._has_enemies_at_location(location):
                targets.append(
                    {
                        "type": "location",
                        "location": location,
                        "feral_count": feral_count,
                        "description": f"Pack hunt at {location} ({feral_count} feral units)",
                    }
                )

        return targets

    @Slot(str, str, dict)
    def execute_targeted_ability(self, player_name: str, ability_id: str, target_data: dict):
        """Execute ability with targeting information."""
        if player_name != self.current_player:
            self.species_error.emit("invalid_player", f"Not {player_name}'s turn")
            return

        ability_data = self._find_ability_by_id(ability_id)
        if not ability_data:
            self.species_error.emit("invalid_ability", f"Unknown ability: {ability_id}")
            return

        self._execute_ability(ability_id, ability_data, target_data)

    def _execute_ability(self, ability_id: str, ability_data: Dict[str, Any], target_data: Dict[str, Any]):
        """Execute the species ability."""
        ability_type = strict_get_optional(ability_data, "type", "")

        # Check and pay resource costs
        if not self._pay_ability_costs(ability_id, ability_data):
            return

        # Execute by type
        if ability_type == "raise_units":
            result = self._execute_necromancy(ability_data, target_data)
        elif ability_type == "area_attack":
            result = self._execute_breath_weapon(ability_data, target_data)
        elif ability_type == "summon":
            result = self._execute_dragon_summoning(ability_data, target_data)
        elif ability_type == "magic_bonus":
            result = self._execute_magic_enhancement(ability_data)
        elif ability_type == "terrain_manipulation":
            result = self._execute_terrain_manipulation(ability_data, target_data)
        elif ability_type == "coordinate_attack":
            result = self._execute_pack_hunt(ability_data, target_data)
        elif ability_type == "terrain_bonus":
            result = self._execute_terrain_bonus(ability_data)
        else:
            self.species_error.emit("unknown_ability_type", f"Unknown ability type: {ability_type}")
            return

        if result.get("success", False):
            self.abilities_used.append(
                {"ability_id": ability_id, "ability_data": ability_data, "target_data": target_data, "result": result}
            )

            self.ability_activated.emit(self.current_player, ability_id, result)
            self.species_status_update.emit(result.get("message", f"Activated {ability_id}"))

            # Check if more abilities can be used or complete phase
            self._check_additional_abilities()
        else:
            error_msg = result.get("error", f"Failed to execute {ability_id}")
            self.species_error.emit("execution_failed", error_msg)

    def _pay_ability_costs(self, ability_id: str, ability_data: Dict[str, Any]) -> bool:
        """Pay resource costs for ability activation."""
        resource_cost: Dict[str, Any] = strict_get_optional(ability_data, "resource_cost", {})

        if not resource_cost:
            return True  # No cost

        # Check if player has resources (would integrate with resource system)
        # For now, assume costs can be paid
        self.ability_resource_cost.emit(self.current_player, resource_cost)
        return True

    # =============================================================================
    # ABILITY EXECUTION METHODS
    # =============================================================================

    def _execute_necromancy(self, ability_data: Dict[str, Any], target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute necromancy ability."""
        unit_id = strict_get_optional(target_data, "unit_id", "")

        if hasattr(self.game_orchestrator, "dua_manager"):
            result = self.game_orchestrator.dua_manager.raise_unit_from_dua(self.current_player, unit_id)

            if result.get("success", False):
                raised_unit = result.get("unit_data", {})
                self.unit_raised.emit(self.current_player, raised_unit)

                return {
                    "success": True,
                    "message": f"Raised {strict_get_optional(raised_unit, 'name', 'unit')} from DUA",
                }
            return {"success": False, "error": result.get("error", "Necromancy failed")}

        return {"success": False, "error": "DUA manager not available"}

    def _execute_breath_weapon(self, ability_data: Dict[str, Any], target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute breath weapon ability."""
        location = strict_get_optional(target_data, "location", "")

        # Would integrate with combat system for breath weapon attacks
        return {
            "success": True,
            "message": f"Breath weapon attack at {location}",
            "damage_dealt": 3,  # Example damage
            "targets_hit": 2,  # Example targets
        }

    def _execute_dragon_summoning(self, ability_data: Dict[str, Any], target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dragon summoning ability."""
        location = strict_get_optional(target_data, "location", "")

        if hasattr(self.game_orchestrator, "summoning_pool_manager"):
            result = self.game_orchestrator.summoning_pool_manager.summon_dragon(self.current_player, location)
            return dict(result)  # Type cast to Dict[str, Any]

        return {"success": False, "error": "Summoning manager not available"}

    def _execute_magic_enhancement(self, ability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute magic enhancement ability."""
        race = strict_get_optional(ability_data, "race", "")

        if race == "undead":
            magic_type = "death"
            bonus = 2
        else:
            magic_type = self._get_elemental_magic_type(race) or "elemental"
            bonus = 1

        self.elemental_magic_bonus.emit(self.current_player, magic_type, bonus)

        return {
            "success": True,
            "message": f"Enhanced {magic_type} magic (+{bonus})",
            "magic_type": magic_type,
            "bonus": bonus,
        }

    def _execute_terrain_manipulation(
        self, ability_data: Dict[str, Any], target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute terrain manipulation ability."""
        location = strict_get_optional(target_data, "location", "")

        # Apply terrain manipulation effect
        return {
            "success": True,
            "message": f"Manipulated terrain at {location}",
            "location": location,
            "effect": "terrain_face_advanced",
        }

    def _execute_pack_hunt(self, ability_data: Dict[str, Any], target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pack hunt ability."""
        location = strict_get_optional(target_data, "location", "")
        feral_count = strict_get_optional(target_data, "feral_count", 0)

        return {
            "success": True,
            "message": f"Pack hunt at {location} with {feral_count} feral units",
            "location": location,
            "pack_size": feral_count,
            "attack_bonus": feral_count - 1,
        }

    def _execute_terrain_bonus(self, ability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute terrain bonus ability."""
        return {
            "success": True,
            "message": "Natural terrain affinity activated",
            "bonus_type": "terrain_affinity",
            "duration": "rest_of_turn",
        }

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _has_dragonkin_at_location(self, location: str) -> bool:
        """Check if player has dragonkin units at location."""
        armies = self.game_orchestrator.game_state_manager.get_all_armies_at_location(self.current_player, location)

        for army in armies:
            units: List[Dict[str, Any]] = strict_get_optional(army, "units", [])
            for unit in units:
                if strict_get_optional(unit, "race", "") == "dragonkin":
                    return True

        return False

    def _has_enemies_at_location(self, location: str) -> bool:
        """Check if there are enemy units at location."""
        all_armies = self.game_orchestrator.game_state_manager.get_all_armies_at_location_all_players(location)

        for army in all_armies:
            army_player = strict_get_optional(army, "player_name", "")
            if army_player != self.current_player:
                return True

        return False

    def _can_race_manipulate_terrain(self, race: str, terrain_info: Dict[str, Any]) -> bool:
        """Check if race can manipulate specific terrain."""
        terrain_type = strict_get_optional(terrain_info, "terrain_type", "")

        manipulation_rules = {
            "firewalker": ["volcano", "wasteland"],
            "frostlander": ["frozen_wasteland", "highlands"],
            "swampstalker": ["swampland", "forest"],
            "amazon": ["plains", "highlands"],
        }

        allowed_terrains = manipulation_rules.get(race, [])
        return terrain_type.lower() in allowed_terrains

    def _check_additional_abilities(self):
        """Check if player can activate additional abilities."""
        # Re-analyze available abilities after using one
        remaining_abilities = [
            ability
            for ability in self.abilities_context.get("available_abilities", [])
            if not any(used["ability_id"] == ability["id"] for used in self.abilities_used)
        ]

        if remaining_abilities:
            # Player might want to use more abilities
            self.abilities_available.emit(self.current_player, remaining_abilities)
        else:
            # No more abilities available, complete phase
            self._complete_species_phase()

    def _complete_species_phase(self):
        """Complete the species abilities phase."""
        abilities_count = len(self.abilities_used)

        if abilities_count == 0:
            self.species_status_update.emit("No species abilities used")
        else:
            self.species_status_update.emit(f"Used {abilities_count} species abilities")

        self.species_phase_completed.emit()

    # =============================================================================
    # PUBLIC INTERFACE
    # =============================================================================

    def get_current_species_state(self) -> Dict[str, Any]:
        """Get current species abilities phase state for UI display."""
        return {
            "player": self.current_player,
            "player_races": self.player_races.copy(),
            "abilities_context": self.abilities_context,
            "abilities_used": self.abilities_used.copy(),
            "can_use_more_abilities": len(self.abilities_context.get("available_abilities", []))
            > len(self.abilities_used),
        }

    def get_race_summary(self) -> Dict[str, Any]:
        """Get summary of player's racial composition."""
        race_counts: Dict[str, int] = {}
        armies = self.core_engine.get_player_armies_summary(self.current_player)

        for army in armies:
            race = strict_get_optional(army, "race", "unknown")
            unit_count = len(strict_get_optional(army, "units", []))
            race_counts[race] = race_counts.get(race, 0) + unit_count

        return {
            "races": self.player_races.copy(),
            "race_unit_counts": race_counts,
            "abilities_available": len(self.abilities_context.get("available_abilities", [])),
            "abilities_used": len(self.abilities_used),
        }

    @Slot()
    def skip_species_abilities_phase(self):
        """Skip the species abilities phase without using abilities."""
        print("SpeciesAbilitiesController: Skipping species abilities phase")
        self._complete_species_phase()
