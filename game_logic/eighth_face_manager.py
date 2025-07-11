"""
Eighth Face Phase Manager for Dragon Dice.

This module handles the Eighth Face phase of player turns, which occurs after
all marches are complete and involves terrain control evaluation and special
eighth face effects for controlled terrains.

Key responsibilities:
- Evaluate terrain control for all terrains
- Process eighth face effects for controlled terrains
- Check victory conditions during eighth face phase
- Handle terrain-specific eighth face mechanics (City, Dragon Lair, Grove, etc.)
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal


class EighthFaceManager(QObject):
    """Manages the Eighth Face phase mechanics and terrain control evaluation."""

    # Signals for UI communication
    eighth_face_phase_started = Signal(str)  # player_name
    terrain_control_evaluated = Signal(dict)  # terrain_control_results
    eighth_face_effect_triggered = Signal(str, str, dict)  # player_name, terrain_name, effect_data
    player_choice_required = Signal(str, str, list)  # player_name, choice_type, options
    victory_condition_met = Signal(str, dict)  # winning_player, victory_data
    eighth_face_phase_completed = Signal()

    def __init__(self, game_state_manager, dua_manager, bua_manager, summoning_pool_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.dua_manager = dua_manager
        self.bua_manager = bua_manager
        self.summoning_pool_manager = summoning_pool_manager

    def start_eighth_face_phase(self, player_name: str) -> Dict[str, Any]:
        """
        Start the Eighth Face phase for the specified player.

        Args:
            player_name: The player whose turn it is

        Returns:
            Dictionary containing phase results and next actions required
        """
        self.eighth_face_phase_started.emit(player_name)

        phase_result = {
            "player": player_name,
            "terrain_control": {},
            "eighth_face_effects": [],
            "victory_achieved": False,
            "choices_required": [],
        }

        # Step 1: Evaluate terrain control for all terrains
        terrain_control_results = self._evaluate_terrain_control()
        phase_result["terrain_control"] = terrain_control_results
        self.terrain_control_evaluated.emit(terrain_control_results)

        # Step 2: Check for victory conditions before processing eighth face effects
        victory_check = self._check_victory_conditions(terrain_control_results)
        if victory_check["victory_achieved"]:
            phase_result["victory_achieved"] = True
            phase_result["winning_player"] = victory_check["winning_player"]
            phase_result["victory_type"] = victory_check["victory_type"]
            self.victory_condition_met.emit(victory_check["winning_player"], victory_check)
            return phase_result

        # Step 3: Process eighth face effects for controlled terrains
        controlled_terrains = self._get_player_controlled_terrains(player_name, terrain_control_results)
        for terrain_id, terrain_data in controlled_terrains.items():
            effect_result = self._process_eighth_face_effect(player_name, terrain_id, terrain_data)
            if effect_result:
                phase_result["eighth_face_effects"].append(effect_result)

                # Check if player choice is required
                if effect_result.get("choice_required"):
                    phase_result["choices_required"].append(effect_result)

        # Step 4: Final victory check after eighth face effects
        final_victory_check = self._check_victory_conditions(self._evaluate_terrain_control())
        if final_victory_check["victory_achieved"]:
            phase_result["victory_achieved"] = True
            phase_result["winning_player"] = final_victory_check["winning_player"]
            phase_result["victory_type"] = final_victory_check["victory_type"]
            self.victory_condition_met.emit(final_victory_check["winning_player"], final_victory_check)

        self.eighth_face_phase_completed.emit()
        return phase_result

    def _evaluate_terrain_control(self) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate which player controls each terrain based on army presence.

        Returns:
            Dictionary mapping terrain_id to control information
        """
        terrain_control = {}
        game_state = self.game_state_manager.get_current_state()

        if "terrain_data" not in game_state:
            raise ValueError("Game state missing required terrain_data")

        terrain_data = game_state["terrain_data"]
        all_players_data = game_state.get("all_players_data", {})

        for terrain_id, terrain_info in terrain_data.items():
            control_result = self._determine_terrain_controller(terrain_id, terrain_info, all_players_data)
            terrain_control[terrain_id] = {
                "terrain_name": terrain_info.get("name", "Unknown"),
                "terrain_subtype": terrain_info.get("subtype", "Unknown"),
                "controller": control_result["controller"],
                "control_strength": control_result["control_strength"],
                "armies_present": control_result["armies_present"],
                "at_eighth_face": control_result["at_eighth_face"],
            }

        return terrain_control

    def _determine_terrain_controller(
        self, terrain_id: str, terrain_info: Dict[str, Any], all_players_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine which player controls a specific terrain.

        Args:
            terrain_id: The terrain identifier
            terrain_info: Terrain data from game state
            all_players_data: All player data from game state

        Returns:
            Dictionary with controller information
        """
        armies_at_terrain = []

        # Find all armies at this terrain
        for player_name, player_data in all_players_data.items():
            armies = player_data.get("armies", {})
            for army_id, army_data in armies.items():
                if army_data.get("location") == terrain_id:
                    army_strength = len(army_data.get("units", []))
                    armies_at_terrain.append(
                        {
                            "player": player_name,
                            "army_id": army_id,
                            "strength": army_strength,
                            "units": army_data.get("units", []),
                        }
                    )

        # Determine controller based on army presence
        if not armies_at_terrain:
            return {
                "controller": None,
                "control_strength": 0,
                "armies_present": [],
                "at_eighth_face": terrain_info.get("current_face", 1) == 8,
            }

        # Group by player and calculate total strength
        player_strengths = {}
        for army in armies_at_terrain:
            player = army["player"]
            if player not in player_strengths:
                player_strengths[player] = 0
            player_strengths[player] += army["strength"]

        at_eighth_face = terrain_info.get("current_face", 1) == 8

        # According to Dragon Dice rules, a terrain is only "controlled" when it's at eighth face
        if not at_eighth_face:
            controller = None
            max_strength = 0
        else:
            # Find the player with the highest strength at eighth face terrain
            max_strength = max(player_strengths.values()) if player_strengths else 0
            controllers = [player for player, strength in player_strengths.items() if strength == max_strength]

            # If there's a tie, no one controls the terrain
            if len(controllers) > 1:
                controller = None
            else:
                controller = controllers[0] if controllers else None

        return {
            "controller": controller,
            "control_strength": max_strength,
            "armies_present": armies_at_terrain,
            "at_eighth_face": at_eighth_face,
        }

    def _get_player_controlled_terrains(
        self, player_name: str, terrain_control: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all terrains controlled by the specified player that are at their eighth face.

        Args:
            player_name: The player to check
            terrain_control: Results from terrain control evaluation

        Returns:
            Dictionary of terrain_id -> terrain_data for controlled terrains at eighth face
        """
        controlled_terrains = {}

        for terrain_id, control_data in terrain_control.items():
            if control_data["controller"] == player_name and control_data["at_eighth_face"]:
                controlled_terrains[terrain_id] = control_data

        return controlled_terrains

    def _process_eighth_face_effect(
        self, player_name: str, terrain_id: str, terrain_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process the eighth face effect for a specific terrain controlled by the player.

        Args:
            player_name: The controlling player
            terrain_id: The terrain identifier
            terrain_data: Terrain control data

        Returns:
            Effect result dictionary if an effect was processed, None otherwise
        """
        terrain_subtype = terrain_data.get("terrain_subtype", "Unknown")
        terrain_name = terrain_data.get("terrain_name", "Unknown")

        effect_result = {
            "terrain_id": terrain_id,
            "terrain_name": terrain_name,
            "terrain_subtype": terrain_subtype,
            "player": player_name,
            "effect_type": terrain_subtype.lower(),
            "choice_required": False,
            "choices": [],
            "automatic_effect": False,
        }

        # Process effect based on terrain subtype
        if terrain_subtype == "City":
            effect_result.update(self._process_city_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Dragon Lair":
            effect_result.update(self._process_dragon_lair_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Grove":
            effect_result.update(self._process_grove_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Standing Stones":
            effect_result.update(self._process_standing_stones_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Temple":
            effect_result.update(self._process_temple_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Tower":
            effect_result.update(self._process_tower_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Vortex":
            effect_result.update(self._process_vortex_eighth_face(player_name, terrain_id))
        elif terrain_subtype == "Castle":
            effect_result.update(self._process_castle_eighth_face(player_name, terrain_id))
        else:
            # Unknown terrain subtype
            return None

        # Emit signal for UI handling
        self.eighth_face_effect_triggered.emit(player_name, terrain_name, effect_result)

        # Emit choice required signal if needed
        if effect_result.get("choice_required"):
            self.player_choice_required.emit(
                player_name, effect_result.get("choice_type", "unknown"), effect_result.get("choices", [])
            )

        return effect_result

    def _process_city_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process City eighth face effect: recruit 1-health unit or promote one unit."""
        return {
            "choice_required": True,
            "choice_type": "city_eighth_face",
            "choices": [
                {
                    "type": "recruit_unit",
                    "description": "Recruit a 1-health (small) unit",
                    "available_units": self._get_available_recruitment_units(player_name),
                },
                {
                    "type": "promote_unit",
                    "description": "Promote one unit in the controlling army",
                    "available_units": self._get_promotable_units_at_terrain(player_name, terrain_id),
                },
            ],
        }

    def _process_dragon_lair_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Dragon Lair eighth face effect: summon matching dragons."""
        terrain_elements = self._get_terrain_elements(terrain_id)
        available_dragons = self._get_summonable_dragons(player_name, terrain_elements)

        if not available_dragons:
            return {"automatic_effect": True, "description": "No dragons available to summon"}

        return {
            "choice_required": True,
            "choice_type": "dragon_lair_eighth_face",
            "choices": [
                {
                    "type": "summon_dragon",
                    "description": "Summon a dragon to any terrain",
                    "available_dragons": available_dragons,
                    "target_terrains": self._get_all_terrain_ids(),
                }
            ],
        }

    def _process_grove_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Grove eighth face effect: move units between BUA/DUA/Summoning Pool."""
        return {
            "choice_required": True,
            "choice_type": "grove_eighth_face",
            "choices": [
                {
                    "type": "move_bua_to_dua",
                    "description": "Move non-Dragonkin unit from any player's BUA to their DUA",
                    "available_moves": self._get_bua_to_dua_moves(),
                },
                {
                    "type": "move_bua_to_summoning",
                    "description": "Move Dragonkin unit or minor terrain from your BUA to your Summoning Pool",
                    "available_moves": self._get_bua_to_summoning_moves(player_name),
                },
                {
                    "type": "move_bua_to_army",
                    "description": "Move Item from your BUA to your army controlling this eighth face",
                    "available_moves": self._get_bua_to_army_moves(player_name, terrain_id),
                },
            ],
            "mandatory": True,
            "description": "This effect is not optional and must be performed if possible",
        }

    def _process_standing_stones_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Standing Stones eighth face effect: convert magic results to terrain colors."""
        return {
            "automatic_effect": True,
            "persistent_effect": True,
            "description": "All units in your controlling army may convert magic results to terrain colors",
            "effect_details": {
                "applies_to": "controlling_army",
                "duration": "until_terrain_face_changes",
                "available_colors": self._get_terrain_elements(terrain_id),
            },
        }

    def _process_temple_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Temple eighth face effect: death magic immunity + force opponent to bury DUA unit."""
        opposing_players = self._get_opposing_players(player_name)
        burial_targets = []

        for opponent in opposing_players:
            opponent_dua = self.dua_manager.get_player_dua(opponent)
            if opponent_dua:
                burial_targets.extend([{"player": opponent, "unit": unit.to_dict()} for unit in opponent_dua])

        result = {
            "automatic_effect": True,
            "persistent_effect": True,
            "description": "Death magic immunity for controlling army",
            "effect_details": {"death_magic_immunity": True, "applies_to": "controlling_army"},
        }

        if burial_targets:
            result.update(
                {
                    "choice_required": True,
                    "choice_type": "temple_eighth_face",
                    "choices": [
                        {
                            "type": "force_burial",
                            "description": "Force another player to bury one unit from their DUA",
                            "burial_targets": burial_targets,
                        }
                    ],
                }
            )

        return result

    def _process_tower_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Tower eighth face effect: missile attack any opponent army."""
        opponent_armies = self._get_all_opponent_armies(player_name)

        if not opponent_armies:
            return {"automatic_effect": True, "description": "No opponent armies available to attack"}

        return {
            "choice_required": True,
            "choice_type": "tower_eighth_face",
            "choices": [
                {
                    "type": "missile_attack",
                    "description": "Use missile action to attack any opponent's army",
                    "target_armies": opponent_armies,
                    "attack_type": "missile",
                    "special_rules": "If attacking Reserve Army, only count non-ID missile results",
                }
            ],
        }

    def _process_vortex_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Vortex eighth face effect: reroll one unit during army rolls."""
        return {
            "automatic_effect": True,
            "persistent_effect": True,
            "description": "May reroll one unit during non-maneuver army rolls at this terrain",
            "effect_details": {
                "reroll_ability": True,
                "applies_to": "terrain_rolls",
                "restrictions": "non-maneuver rolls only",
                "timing": "before resolving SAIs",
            },
        }

    def _process_castle_eighth_face(self, player_name: str, terrain_id: str) -> Dict[str, Any]:
        """Process Castle eighth face effect: choose terrain type."""
        return {
            "choice_required": True,
            "choice_type": "castle_eighth_face",
            "choices": [
                {
                    "type": "choose_terrain_type",
                    "description": "Choose terrain type for castle",
                    "available_types": ["City", "Standing Stones", "Temple", "Tower"],
                    "effect": "Castle becomes chosen terrain until face is moved",
                }
            ],
        }

    def _check_victory_conditions(self, terrain_control: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if any player has achieved victory conditions during the eighth face phase.

        Args:
            terrain_control: Current terrain control evaluation results

        Returns:
            Dictionary with victory check results
        """
        victory_result: Dict[str, Any] = {
            "victory_achieved": False,
            "winning_player": None,
            "victory_type": None,
            "details": {},
        }

        # Count terrain control by player
        player_terrain_counts: Dict[str, int] = {}
        total_terrains = len(terrain_control)

        for terrain_data in terrain_control.values():
            controller = terrain_data.get("controller")
            if controller:
                if controller not in player_terrain_counts:
                    player_terrain_counts[controller] = 0
                player_terrain_counts[controller] += 1

        # Check for majority control victory (more than half of all terrains)
        majority_threshold = total_terrains // 2 + 1

        for player, terrain_count in player_terrain_counts.items():
            if terrain_count >= majority_threshold:
                victory_result.update(
                    {
                        "victory_achieved": True,
                        "winning_player": player,
                        "victory_type": "terrain_control_majority",
                        "details": {
                            "controlled_terrains": terrain_count,
                            "total_terrains": total_terrains,
                            "majority_threshold": majority_threshold,
                        },
                    }
                )
                break

        return victory_result

    # Helper methods for terrain effect processing
    def _get_terrain_elements(self, terrain_id: str) -> List[str]:
        """Get the elements of a specific terrain."""
        game_state = self.game_state_manager.get_current_state()
        terrain_data = game_state.get("terrain_data", {})
        terrain_info = terrain_data.get(terrain_id, {})
        return terrain_info.get("elements", [])

    def _get_available_recruitment_units(self, player_name: str) -> List[Dict[str, Any]]:
        """Get units available for recruitment (1-health units)."""
        # This would integrate with the recruitment system
        # For now, return placeholder data
        return [
            {"name": "Small Warrior", "health": 1, "species": "Generic"},
            {"name": "Small Scout", "health": 1, "species": "Generic"},
        ]

    def _get_promotable_units_at_terrain(self, player_name: str, terrain_id: str) -> List[Dict[str, Any]]:
        """Get units that can be promoted at the specified terrain."""
        game_state = self.game_state_manager.get_current_state()
        all_players_data = game_state.get("all_players_data", {})
        player_data = all_players_data.get(player_name, {})
        armies = player_data.get("armies", {})

        promotable_units = []
        for army_id, army_data in armies.items():
            if army_data.get("location") == terrain_id:
                for unit in army_data.get("units", []):
                    if unit.get("health", 0) < unit.get("max_health", 1):
                        promotable_units.append({"army_id": army_id, "unit_data": unit})

        return promotable_units

    def _get_summonable_dragons(self, player_name: str, terrain_elements: List[str]) -> List[Dict[str, Any]]:
        """Get dragons that can be summoned based on terrain elements."""
        if not self.summoning_pool_manager:
            return []

        player_pool = self.summoning_pool_manager.get_player_pool(player_name)
        summonable = []

        for dragon in player_pool:
            dragon_elements = dragon.elements
            # Check if dragon has at least one matching element, or is Ivory
            # Exclude White Dragons (they cannot be summoned by Dragon Lair)
            if (
                any(elem in terrain_elements for elem in dragon_elements) or "IVORY" in dragon_elements
            ) and dragon.dragon_type != "WHITE":
                summonable.append(dragon.to_dict())

        return summonable

    def _get_all_terrain_ids(self) -> List[str]:
        """Get all terrain IDs in the game."""
        game_state = self.game_state_manager.get_current_state()
        terrain_data = game_state.get("terrain_data", {})
        return list(terrain_data.keys())

    def _get_bua_to_dua_moves(self) -> List[Dict[str, Any]]:
        """Get possible moves from any player's BUA to their DUA."""
        moves = []
        game_state = self.game_state_manager.get_current_state()
        all_players_data = game_state.get("all_players_data", {})

        for player_name in all_players_data:
            bua_units = self.bua_manager.get_player_bua(player_name)
            for unit in bua_units:
                # Only non-Dragonkin units
                if "dragonkin" not in unit.species.lower():
                    moves.append({"player": player_name, "unit": unit.to_dict(), "from": "BUA", "to": "DUA"})

        return moves

    def _get_bua_to_summoning_moves(self, player_name: str) -> List[Dict[str, Any]]:
        """Get possible moves from player's BUA to Summoning Pool."""
        moves = []
        bua_units = self.bua_manager.get_player_bua(player_name)

        for unit in bua_units:
            # Dragonkin units or minor terrain
            if "dragonkin" in unit.species.lower() or unit.unit_type == "terrain" and unit.terrain_type == "minor":
                moves.append({"player": player_name, "unit": unit.to_dict(), "from": "BUA", "to": "Summoning Pool"})

        return moves

    def _get_bua_to_army_moves(self, player_name: str, terrain_id: str) -> List[Dict[str, Any]]:
        """Get possible Item moves from player's BUA to controlling army."""
        moves = []
        bua_units = self.bua_manager.get_player_bua(player_name)

        for unit in bua_units:
            # Only Items
            if unit.unit_type == "item":
                moves.append(
                    {"player": player_name, "item": unit.to_dict(), "from": "BUA", "to": f"Army at {terrain_id}"}
                )

        return moves

    def _get_opposing_players(self, player_name: str) -> List[str]:
        """Get list of all opposing players."""
        game_state = self.game_state_manager.get_current_state()
        all_players_data = game_state.get("all_players_data", {})
        return [p for p in all_players_data if p != player_name]

    def _get_all_opponent_armies(self, player_name: str) -> List[Dict[str, Any]]:
        """Get all armies belonging to opposing players."""
        opponent_armies = []
        game_state = self.game_state_manager.get_current_state()
        all_players_data = game_state.get("all_players_data", {})

        for opponent in all_players_data:
            if opponent != player_name:
                armies = all_players_data[opponent].get("armies", {})
                for army_id, army_data in armies.items():
                    opponent_armies.append(
                        {
                            "player": opponent,
                            "army_id": army_id,
                            "army_data": army_data,
                            "location": army_data.get("location"),
                            "units": army_data.get("units", []),
                        }
                    )

        return opponent_armies

    def apply_player_choice(self, player_name: str, choice_type: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a player's choice for an eighth face effect.

        Args:
            player_name: The player making the choice
            choice_type: The type of choice being made
            choice_data: The specific choice and its parameters

        Returns:
            Result of applying the choice
        """
        if choice_type == "city_eighth_face":
            return self._apply_city_choice(player_name, choice_data)
        if choice_type == "dragon_lair_eighth_face":
            return self._apply_dragon_lair_choice(player_name, choice_data)
        if choice_type == "grove_eighth_face":
            return self._apply_grove_choice(player_name, choice_data)
        if choice_type == "temple_eighth_face":
            return self._apply_temple_choice(player_name, choice_data)
        if choice_type == "tower_eighth_face":
            return self._apply_tower_choice(player_name, choice_data)
        if choice_type == "castle_eighth_face":
            return self._apply_castle_choice(player_name, choice_data)
        return {"success": False, "error": f"Unknown choice type: {choice_type}"}

    def _apply_city_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for City eighth face effect."""
        # Implementation would depend on recruitment and promotion systems
        return {"success": True, "action": "city_choice_applied", "details": choice_data}

    def _apply_dragon_lair_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for Dragon Lair eighth face effect."""
        # Implementation would integrate with dragon summoning system
        return {"success": True, "action": "dragon_summoned", "details": choice_data}

    def _apply_grove_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for Grove eighth face effect."""
        # Implementation would integrate with BUA/DUA/Summoning Pool managers
        return {"success": True, "action": "grove_move_applied", "details": choice_data}

    def _apply_temple_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for Temple eighth face effect."""
        # Implementation would integrate with DUA manager for forced burial
        return {"success": True, "action": "forced_burial_applied", "details": choice_data}

    def _apply_tower_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for Tower eighth face effect."""
        # Implementation would integrate with combat system for missile attacks
        return {"success": True, "action": "missile_attack_executed", "details": choice_data}

    def _apply_castle_choice(self, player_name: str, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player's choice for Castle eighth face effect."""
        # Implementation would update terrain type in game state
        return {"success": True, "action": "castle_type_chosen", "details": choice_data}
