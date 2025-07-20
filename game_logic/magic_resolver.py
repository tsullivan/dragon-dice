"""
Magic Resolution System for Dragon Dice.

This module handles the calculation of magic points, terrain magic interactions,
and magic result processing according to Dragon Dice rules.
"""

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get


class MagicResolver(QObject):
    """
    Resolves magic actions including point calculation, terrain interactions,
    and eighth face effects according to Dragon Dice rules.
    """

    magic_points_calculated = Signal(dict)  # Emits magic points by element
    terrain_magic_applied = Signal(str, dict)  # location, magic_effects

    def __init__(self, game_state_manager, sai_processor, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager
        self.sai_processor = sai_processor

    def calculate_magic_points(
        self,
        caster_player: str,
        army_identifier: str,
        magic_results: Dict[str, List[str]],
        location: str,
    ) -> Dict[str, int]:
        """
        Calculate available magic points by element for spell casting.

        Args:
            caster_player: Player casting magic
            army_identifier: Specific army casting magic
            magic_results: Raw die face results by unit name
            location: Location where magic is being cast

        Returns:
            Dictionary mapping element names to available magic points
        """
        # Get army data
        army_data = self.game_state_manager.get_army_data(caster_player, army_identifier)
        army_units = strict_get(army_data, "units")

        # Get terrain elements for Amazon Terrain Harmony
        terrain_elements = self._get_terrain_elements(location)

        # Check if army controls terrain eighth face (doubles all ID results)
        terrain_eighth_face_controlled = self._check_terrain_eighth_face_control(location, caster_player)

        # Process magic roll with SAI effects
        processed_results = self._process_magic_roll_with_sai(
            magic_results, army_units, terrain_elements, terrain_eighth_face_controlled
        )

        # Initialize magic points by element
        magic_points_by_element = {"AIR": 0, "DEATH": 0, "EARTH": 0, "FIRE": 0, "WATER": 0}

        # Calculate magic points by unit and element
        for unit_name, face_results in processed_results.items():
            # Find unit data
            unit_data = next((u for u in army_units if strict_get(u, "name") == unit_name), None)
            if not unit_data:
                continue

            unit_species = strict_get(unit_data, "species")
            unit_elements = self._get_unit_elements(unit_species, terrain_elements)
            unit_health = strict_get(unit_data, "health")

            # Count magic results
            magic_count, id_count = self._count_magic_results(face_results)

            # ID faces generate magic equal to unit health
            id_magic_count = id_count * unit_health

            # Apply terrain eighth face doubling to ID results only
            if terrain_eighth_face_controlled:
                id_magic_count *= 2

            # Total magic for this unit
            total_magic = magic_count + id_magic_count

            # Distribute magic points among unit elements
            if unit_elements and total_magic > 0:
                points_per_element = total_magic // len(unit_elements)
                remainder = total_magic % len(unit_elements)

                for i, element in enumerate(unit_elements):
                    element_key = element.upper()
                    points = points_per_element + (1 if i < remainder else 0)
                    magic_points_by_element[element_key] += points

        # Handle special cases (Amazon Ivory magic)
        self._apply_special_magic_rules(magic_points_by_element, caster_player, location, army_units)

        self.magic_points_calculated.emit(magic_points_by_element)
        return magic_points_by_element

    def _process_magic_roll_with_sai(
        self,
        magic_results: Dict[str, List[str]],
        army_units: List[Dict[str, Any]],
        terrain_elements: List[str],
        terrain_eighth_face_controlled: bool,
    ) -> Dict[str, List[str]]:
        """Process magic roll results with SAI effects."""
        # Make a copy of the results to avoid modifying the original
        processed_results = {unit: faces.copy() for unit, faces in magic_results.items()}

        # Apply SAI processing if available
        if self.sai_processor:
            self.sai_processor.process_combat_roll(
                processed_results,
                "magic",
                army_units,
                is_attacker=True,
                terrain_elements=terrain_elements,
                terrain_eighth_face_controlled=terrain_eighth_face_controlled,
            )

        return processed_results

    def _count_magic_results(self, face_results: List[str]) -> tuple[int, int]:
        """Count magic and ID results from face results."""
        magic_count = 0
        id_count = 0

        for face in face_results:
            face_lower = face.lower().strip()
            if face_lower in ["mg", "magic"]:
                magic_count += 1
            elif face_lower == "id":
                id_count += 1

        return magic_count, id_count

    def _get_unit_elements(self, species: str, terrain_elements: List[str]) -> List[str]:
        """Get elements for a unit species, handling special cases like Amazons."""
        # Import here to avoid circular dependency
        from models.species_model import get_species_elements

        species_elements = get_species_elements(species)

        # Special case for Amazons - use terrain elements (Terrain Harmony)
        if species == "Amazons" and terrain_elements:
            return [elem.upper() for elem in terrain_elements]

        return species_elements

    def _check_terrain_eighth_face_control(self, location: str, caster_player: str) -> bool:
        """Check if the caster's army controls the terrain's eighth face."""
        try:
            # Query the game state for terrain control
            terrain_controller = self.game_state_manager.get_terrain_controller(location)
            return terrain_controller == caster_player
        except Exception:
            # Fallback to simplified check if game state query fails
            return "eighth" in location.lower() or "controlled" in location.lower()

    def _get_terrain_elements(self, location: str) -> List[str]:
        """Get terrain elements for the magic location."""
        # Import here to avoid circular dependency
        from models.terrain_model import get_terrain_elements

        try:
            return get_terrain_elements(location)
        except Exception:
            # Fallback to hardcoded mapping if model lookup fails
            terrain_mappings = {
                "Highland": ["fire", "earth"],
                "Flatland": ["air", "earth"],
                "Coastland": ["air", "water"],
                "Frozenwaste": ["air", "death"],
                "Badlands": ["death", "earth"],
                "Swampland": ["death", "water"],
                "Volcano": ["fire", "death"],
                "Temple": ["fire", "water"],
            }

            # Extract base terrain name
            base_terrain = location.split("(")[0].strip() if "(" in location else location.strip()
            return terrain_mappings.get(base_terrain, [])

    def _apply_special_magic_rules(
        self,
        magic_points: Dict[str, int],
        caster_player: str,
        location: str,
        army_units: List[Dict[str, Any]],
    ) -> None:
        """Apply special magic generation rules (e.g., Amazon Ivory magic)."""
        # Check if army is in Reserve Area
        is_in_reserves = location.lower() in ["reserve area", "reserves"]

        if is_in_reserves:
            # Amazon Ivory magic generation
            amazon_units = [unit for unit in army_units if strict_get(unit, "species") == "Amazons"]
            if amazon_units:
                # Generate Ivory magic based on Amazon units in reserves
                ivory_magic = len(amazon_units)
                magic_points["IVORY"] = ivory_magic

    def get_spell_availability(
        self,
        magic_points_by_element: Dict[str, int],
        army_species: List[str],
        location: str,
    ) -> List[Dict[str, Any]]:
        """
        Get spells that can be cast with available magic points.

        Args:
            magic_points_by_element: Available magic by element
            army_species: Species in the casting army
            location: Location where magic is being cast

        Returns:
            List of available spells with casting information
        """
        # Import here to avoid circular dependency
        from models.spell_model import get_available_spells

        # Check if army is in Reserve Area
        is_in_reserves = location.lower() in ["reserve area", "reserves"]

        # Get available spells using the model function
        available_spells = get_available_spells(
            magic_points_by_element=magic_points_by_element,
            army_species=army_species,
            from_reserves=is_in_reserves,
        )

        # Convert SpellModel objects to dictionaries for UI consumption
        spell_data = []
        for spell in available_spells:
            spell_info = {
                "name": spell.name,
                "cost": spell.cost,
                "element": spell.element,
                "species": spell.species,
                "effect": spell.effect,
                "reserves": spell.reserves,
                "cantrip": spell.cantrip,
            }
            spell_data.append(spell_info)

        return spell_data

    def validate_spell_casting(
        self,
        spell_name: str,
        element_used: str,
        magic_points: Dict[str, int],
        army_species: List[str],
        location: str,
    ) -> Dict[str, Any]:
        """
        Validate that a spell can be cast with given parameters.

        Returns:
            Dictionary with 'valid' boolean and 'error' message if invalid
        """
        # Import here to avoid circular dependency
        from models.spell_model import ALL_SPELLS

        spell_key = spell_name.upper().replace(" ", "_")
        spell = ALL_SPELLS.get(spell_key)

        if not spell:
            return {"valid": False, "error": f"Unknown spell: {spell_name}"}

        # Check species restrictions
        if spell.species != "Any" and spell.species not in army_species:
            return {"valid": False, "error": f"{spell_name} not available to army species"}

        # Check reserve restrictions
        is_in_reserves = location.lower() in ["reserve area", "reserves"]
        if is_in_reserves and not spell.reserves:
            return {"valid": False, "error": f"{spell_name} cannot be cast from reserves"}
        if not is_in_reserves and spell.reserves:
            return {"valid": False, "error": f"{spell_name} can only be cast from reserves"}

        # Check magic point requirements
        if spell.element == "ELEMENTAL":
            total_magic = sum(magic_points.values())
            if spell.cost > total_magic:
                return {
                    "valid": False,
                    "error": f"Insufficient magic for {spell_name} (need {spell.cost}, have {total_magic})",
                }
        else:
            element_magic = magic_points.get(spell.element, 0)
            if spell.cost > element_magic:
                return {
                    "valid": False,
                    "error": f"Insufficient {spell.element} magic for {spell_name} (need {spell.cost}, have {element_magic})",
                }

        return {"valid": True}
