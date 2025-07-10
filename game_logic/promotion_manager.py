"""
Promotion Manager for Dragon Dice.

This module handles unit promotions, including validation, exchange mechanics,
and promotion chain management according to Dragon Dice rules.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal
from models.unit_model import UnitModel


@dataclass
class PromotionOption:
    """Represents a single promotion option for a unit."""

    source_unit: Dict[str, Any]  # Unit being promoted (in army)
    target_unit: Dict[str, Any]  # Unit from DUA/pool to promote to
    health_increase: int  # Amount of health increase
    source_location: str  # Where target unit comes from ("DUA" or "SUMMONING_POOL")

    def __post_init__(self):
        """Validate promotion option data."""
        if self.health_increase <= 0:
            raise ValueError("Health increase must be positive")


@dataclass
class PromotionResult:
    """Result of a promotion operation."""

    success: bool
    promoted_units: List[Dict[str, Any]]  # Units that were promoted
    exchanged_from_dua: List[Dict[str, Any]]  # Units taken from DUA
    exchanged_from_pool: List[Dict[str, Any]]  # Units taken from Summoning Pool
    message: str
    errors: List[str]


class PromotionManager(QObject):
    """Manages unit promotions according to Dragon Dice rules."""

    promotion_completed = Signal(dict)  # Emitted when promotions are completed

    def __init__(self, dua_manager=None, summoning_pool_manager=None, parent=None):
        super().__init__(parent)
        self.dua_manager = dua_manager
        self.summoning_pool_manager = summoning_pool_manager

    def find_promotion_options(self, army_units: List[Dict[str, Any]], player_name: str) -> List[PromotionOption]:
        """Find all possible promotion options for units in an army."""
        promotion_options = []

        for unit_dict in army_units:
            unit_options = self._find_unit_promotion_options(unit_dict, player_name)
            promotion_options.extend(unit_options)

        return promotion_options

    def _find_unit_promotion_options(self, unit_dict: Dict[str, Any], player_name: str) -> List[PromotionOption]:
        """Find promotion options for a specific unit."""
        options = []
        current_health = unit_dict.get("max_health", unit_dict.get("health", 1))
        species_name = unit_dict.get("species", {}).get("name", "")

        if not species_name:
            return options

        # Look for units with +1 health in DUA
        dua_candidates = self._find_promotion_candidates_in_dua(player_name, species_name, current_health + 1)

        for candidate in dua_candidates:
            options.append(
                PromotionOption(source_unit=unit_dict, target_unit=candidate, health_increase=1, source_location="DUA")
            )

        # For Dragonkin, also check Summoning Pool
        if self._is_dragonkin(unit_dict):
            pool_candidates = self._find_promotion_candidates_in_pool(player_name, species_name, current_health + 1)

            for candidate in pool_candidates:
                options.append(
                    PromotionOption(
                        source_unit=unit_dict,
                        target_unit=candidate,
                        health_increase=1,
                        source_location="SUMMONING_POOL",
                    )
                )

        return options

    def _find_promotion_candidates_in_dua(
        self, player_name: str, species_name: str, target_health: int
    ) -> List[Dict[str, Any]]:
        """Find promotion candidates in the DUA."""
        if not self.dua_manager:
            return []

        dua_units = self.dua_manager.get_player_dua(player_name)
        candidates = []

        for dua_unit in dua_units:
            unit_data = dua_unit.unit_data
            unit_species = unit_data.get("species", {}).get("name", "")
            unit_health = unit_data.get("max_health", unit_data.get("health", 1))

            if unit_species == species_name and unit_health == target_health:
                candidates.append(unit_data)

        return candidates

    def _find_promotion_candidates_in_pool(
        self, player_name: str, species_name: str, target_health: int
    ) -> List[Dict[str, Any]]:
        """Find promotion candidates in the Summoning Pool (for Dragonkin)."""
        if not self.summoning_pool_manager:
            return []

        # For now, return empty list as dragonkin promotion from summoning pool
        # is a complex mechanic that needs more detailed implementation
        return []

    def _is_dragonkin(self, unit_dict: Dict[str, Any]) -> bool:
        """Check if a unit is a Dragonkin."""
        species_name = unit_dict.get("species", {}).get("name", "")
        return "dragonkin" in species_name.lower()

    def validate_promotion(self, promotion_option: PromotionOption, player_name: str) -> Tuple[bool, str]:
        """Validate if a promotion option is valid."""
        try:
            source_unit = promotion_option.source_unit
            target_unit = promotion_option.target_unit

            # Check species match
            source_species = source_unit.get("species", {}).get("name", "")
            target_species = target_unit.get("species", {}).get("name", "")

            if source_species != target_species:
                return False, f"Species mismatch: {source_species} != {target_species}"

            # Check health progression
            source_health = source_unit.get("max_health", source_unit.get("health", 1))
            target_health = target_unit.get("max_health", target_unit.get("health", 1))

            if target_health != source_health + promotion_option.health_increase:
                return False, f"Invalid health progression: {source_health} -> {target_health}"

            # Check availability in DUA/Pool
            if promotion_option.source_location == "DUA":
                if not self._is_unit_available_in_dua(target_unit, player_name):
                    return False, "Target unit not available in DUA"
            elif promotion_option.source_location == "SUMMONING_POOL":
                if not self._is_unit_available_in_pool(target_unit, player_name):
                    return False, "Target unit not available in Summoning Pool"

            return True, "Valid promotion"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _is_unit_available_in_dua(self, unit_dict: Dict[str, Any], player_name: str) -> bool:
        """Check if a specific unit is available in the DUA."""
        if not self.dua_manager:
            return False

        dua_units = self.dua_manager.get_player_dua(player_name)
        unit_id = unit_dict.get("unit_id", "")

        for dua_unit in dua_units:
            if dua_unit.unit_data.get("unit_id") == unit_id:
                return dua_unit.state == "DEAD"  # Only dead units can be used for promotion

        return False

    def _is_unit_available_in_pool(self, unit_dict: Dict[str, Any], player_name: str) -> bool:
        """Check if a specific unit is available in the Summoning Pool."""
        if not self.summoning_pool_manager:
            return False

        # For now, return False as dragonkin promotion is complex
        return False

    def execute_promotion(self, promotion_option: PromotionOption, player_name: str) -> PromotionResult:
        """Execute a single promotion."""
        # Validate first
        is_valid, validation_msg = self.validate_promotion(promotion_option, player_name)
        if not is_valid:
            return PromotionResult(
                success=False,
                promoted_units=[],
                exchanged_from_dua=[],
                exchanged_from_pool=[],
                message=f"Promotion failed: {validation_msg}",
                errors=[validation_msg],
            )

        try:
            # Perform the exchange
            if promotion_option.source_location == "DUA":
                return self._execute_dua_promotion(promotion_option, player_name)
            elif promotion_option.source_location == "SUMMONING_POOL":
                return self._execute_pool_promotion(promotion_option, player_name)
            else:
                return PromotionResult(
                    success=False,
                    promoted_units=[],
                    exchanged_from_dua=[],
                    exchanged_from_pool=[],
                    message="Unknown promotion source",
                    errors=["Unknown promotion source location"],
                )

        except Exception as e:
            return PromotionResult(
                success=False,
                promoted_units=[],
                exchanged_from_dua=[],
                exchanged_from_pool=[],
                message=f"Promotion execution failed: {str(e)}",
                errors=[str(e)],
            )

    def _execute_dua_promotion(self, promotion_option: PromotionOption, player_name: str) -> PromotionResult:
        """Execute promotion using a unit from the DUA."""
        source_unit = promotion_option.source_unit
        target_unit = promotion_option.target_unit

        # This is a placeholder - the actual implementation would need to:
        # 1. Remove the target unit from DUA
        # 2. Replace the source unit in the army with promoted stats
        # 3. Add the source unit to DUA

        # For now, return a success result with the promoted unit info
        promoted_unit = source_unit.copy()
        promoted_unit["health"] = target_unit.get("max_health", target_unit.get("health", 1))
        promoted_unit["max_health"] = target_unit.get("max_health", target_unit.get("health", 1))
        promoted_unit["promotion_source"] = "DUA"

        return PromotionResult(
            success=True,
            promoted_units=[promoted_unit],
            exchanged_from_dua=[target_unit],
            exchanged_from_pool=[],
            message=f"Successfully promoted {source_unit.get('name', 'unit')} using DUA unit",
            errors=[],
        )

    def _execute_pool_promotion(self, promotion_option: PromotionOption, player_name: str) -> PromotionResult:
        """Execute promotion using a unit from the Summoning Pool."""
        # Placeholder for Summoning Pool promotion
        return PromotionResult(
            success=False,
            promoted_units=[],
            exchanged_from_dua=[],
            exchanged_from_pool=[],
            message="Summoning Pool promotion not yet implemented",
            errors=["Summoning Pool promotion not implemented"],
        )

    def execute_mass_promotion(
        self, army_units: List[Dict[str, Any]], player_name: str, promotion_type: str = "as_many_as_possible"
    ) -> PromotionResult:
        """Execute mass promotion for an entire army (e.g., after killing a dragon)."""
        all_promoted = []
        all_from_dua = []
        all_from_pool = []
        all_errors = []

        if promotion_type == "as_many_as_possible":
            promotion_options = self.find_promotion_options(army_units, player_name)

            for option in promotion_options:
                result = self.execute_promotion(option, player_name)
                if result.success:
                    all_promoted.extend(result.promoted_units)
                    all_from_dua.extend(result.exchanged_from_dua)
                    all_from_pool.extend(result.exchanged_from_pool)
                else:
                    all_errors.extend(result.errors)

        success = len(all_promoted) > 0
        message = f"Mass promotion completed: {len(all_promoted)} units promoted"
        if all_errors:
            message += f", {len(all_errors)} errors occurred"

        return PromotionResult(
            success=success,
            promoted_units=all_promoted,
            exchanged_from_dua=all_from_dua,
            exchanged_from_pool=all_from_pool,
            message=message,
            errors=all_errors,
        )

    def calculate_health_worth_promotion(
        self, available_health_worth: int, army_units: List[Dict[str, Any]], player_name: str
    ) -> List[PromotionOption]:
        """Calculate optimal promotion distribution for a given health-worth amount."""
        # This would implement the complex logic for distributing health-worth
        # across multiple promotions, allowing players to choose how to spend
        # promotion points (e.g., promote 2 units by 1 health each, or 1 unit by 2 health)

        # For now, return simple single-health promotions up to the available amount
        promotion_options = self.find_promotion_options(army_units, player_name)
        return promotion_options[:available_health_worth]

    def get_promotion_summary(self, promotion_result: PromotionResult) -> str:
        """Get a human-readable summary of promotion results."""
        if not promotion_result.success:
            return f"Promotion failed: {promotion_result.message}"

        summary_parts = []

        if promotion_result.promoted_units:
            unit_names = [unit.get("name", "Unit") for unit in promotion_result.promoted_units]
            summary_parts.append(f"Promoted: {', '.join(unit_names)}")

        if promotion_result.exchanged_from_dua:
            dua_count = len(promotion_result.exchanged_from_dua)
            summary_parts.append(f"Used {dua_count} unit(s) from DUA")

        if promotion_result.exchanged_from_pool:
            pool_count = len(promotion_result.exchanged_from_pool)
            summary_parts.append(f"Used {pool_count} unit(s) from Summoning Pool")

        return "; ".join(summary_parts) if summary_parts else "No promotions occurred"
