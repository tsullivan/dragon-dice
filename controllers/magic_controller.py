"""
Magic Action Controller for Dragon Dice.

This controller coordinates magic actions including magic point calculation,
spell selection, and spell casting through the proper domain layers.
"""

from typing import Any, Dict

from PySide6.QtCore import QObject, Signal, Slot

from utils.field_access import strict_get, strict_get_optional


class MagicController(QObject):
    """
    Controller for magic actions, coordinating between UI and game logic layers.
    """

    magic_points_calculated = Signal(dict)  # magic_points_by_element
    available_spells_updated = Signal(list)  # available_spells
    spell_cast_completed = Signal(dict)  # spell_results
    magic_action_completed = Signal(dict)  # action_results

    def __init__(self, game_engine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.magic_resolver = game_engine.action_resolver.spell_resolver  # Access through action resolver

    @Slot(str, str, dict, str)
    def handle_magic_roll_submission(self, player_name: str, army_identifier: str, magic_results: dict, location: str):
        """Handle submission of magic roll results."""
        print(f"[MagicController] Processing magic roll for {player_name} at {location}")

        # Calculate magic points using the magic resolver
        magic_points = self.game_engine.magic_resolver.calculate_magic_points(
            player_name, army_identifier, magic_results, location
        )

        print(f"[MagicController] Magic points calculated: {magic_points}")
        self.magic_points_calculated.emit(magic_points)

        # Get available spells
        army_data = self.game_engine.game_state_manager.get_army_data(player_name, army_identifier)
        army_units = strict_get(army_data, "units")
        army_species = list({strict_get(unit, "species") for unit in army_units})

        available_spells = self.game_engine.magic_resolver.get_spell_availability(magic_points, army_species, location)

        print(f"[MagicController] Available spells: {len(available_spells)}")
        self.available_spells_updated.emit(available_spells)

    @Slot(str, list)
    def handle_spell_casting_request(self, player_name: str, spell_requests: list):
        """Handle request to cast spells."""
        print(f"[MagicController] Processing spell casting for {player_name}")

        results = {"spells_cast": [], "total_spells": len(spell_requests), "success": True, "errors": []}

        for spell_request in spell_requests:
            spell_name = strict_get(spell_request, "name")
            element_used = strict_get(spell_request, "element")
            target_data = strict_get(spell_request, "target")
            casting_count = strict_get_optional(spell_request, "count", 1)

            # Use spell resolver to cast spell
            cast_result = self.magic_resolver.cast_spell(
                spell_name, player_name, target_data, element_used, casting_count
            )

            if cast_result.get("success"):
                results["spells_cast"].append(
                    {
                        "name": spell_name,
                        "element": element_used,
                        "count": casting_count,
                        "results": cast_result.get("results", {}),
                    }
                )
                print(f"[MagicController] Successfully cast {spell_name}")
            else:
                error_msg = cast_result.get("error", "Unknown error")
                results["errors"].append(f"Failed to cast {spell_name}: {error_msg}")
                results["success"] = False
                print(f"[MagicController] Failed to cast {spell_name}: {error_msg}")

        self.spell_cast_completed.emit(results)

    @Slot(str, str, str)
    def handle_magic_action_completion(self, player_name: str, magic_roll_str: str, spell_casting_data_str: str = ""):
        """Handle completion of entire magic action."""
        print(f"[MagicController] Completing magic action for {player_name}")

        # Parse spell casting data if provided
        spell_casting_data = None
        if spell_casting_data_str:
            try:
                import json

                spell_casting_data = json.loads(spell_casting_data_str)
            except Exception as e:
                print(f"[MagicController] Error parsing spell data: {e}")

        # Use action resolver to process complete magic action
        self.game_engine.action_resolver.resolve_magic_action(player_name, magic_roll_str, spell_casting_data)

        action_results = {
            "player": player_name,
            "magic_roll": magic_roll_str,
            "spells_cast": bool(spell_casting_data),
            "completed": True,
        }

        self.magic_action_completed.emit(action_results)
        print(f"[MagicController] Magic action completed for {player_name}")

    @Slot(str, str, str, str, int, result=dict)
    def validate_spell_casting(
        self, spell_name: str, element_used: str, player_name: str, location: str, available_magic: int
    ) -> dict:
        """Validate that a spell can be cast."""
        # Get player's army species
        army_data = self.game_engine.game_state_manager.get_active_army_data(player_name)
        army_units = strict_get(army_data, "units")
        army_species = list({strict_get(unit, "species") for unit in army_units})

        # Create magic points dict for validation
        magic_points = {element_used.upper(): available_magic}

        # Use magic resolver for validation
        validation_result = self.game_engine.magic_resolver.validate_spell_casting(
            spell_name, element_used, magic_points, army_species, location
        )

        return validation_result

    def get_magic_point_calculation_details(
        self, player_name: str, army_identifier: str, location: str
    ) -> Dict[str, Any]:
        """Get detailed breakdown of magic point calculation."""
        army_data = self.game_engine.game_state_manager.get_army_data(player_name, army_identifier)
        army_units = strict_get(army_data, "units")

        details = {
            "player": player_name,
            "army": army_identifier,
            "location": location,
            "units": [],
            "terrain_elements": [],
            "eighth_face_controlled": False,
            "special_rules": [],
        }

        # Get terrain elements
        from models.terrain_model import get_terrain_elements

        details["terrain_elements"] = get_terrain_elements(location)

        # Check eighth face control
        try:
            controller = self.game_engine.game_state_manager.get_terrain_controller(location)
            details["eighth_face_controlled"] = controller == player_name
        except Exception:
            details["eighth_face_controlled"] = False

        # Get unit details
        for unit in army_units:
            from models.species_model import get_species_elements

            unit_species = strict_get(unit, "species")
            unit_elements = get_species_elements(unit_species)

            # Special case for Amazons
            if unit_species == "Amazons" and details["terrain_elements"]:
                unit_elements = [elem.upper() for elem in details["terrain_elements"]]
                details["special_rules"].append("Amazon Terrain Harmony: Using terrain elements")

            unit_detail = {
                "name": strict_get(unit, "name"),
                "species": unit_species,
                "health": strict_get(unit, "health"),
                "max_health": strict_get(unit, "max_health"),
                "elements": unit_elements,
            }
            details["units"].append(unit_detail)

        # Check for reserves special rules
        if location.lower() in ["reserve area", "reserves"]:
            amazon_count = len([u for u in army_units if strict_get(u, "species") == "Amazons"])
            if amazon_count > 0:
                details["special_rules"].append(f"Amazon Ivory Magic: {amazon_count} points available")

        return details
