"""
Army validation logic for Dragon Dice game rules.

This module contains pure Python business logic for validating army compositions
according to official Dragon Dice rules, extracted from UI components for
better testability and reusability.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import constants


@dataclass
class ValidationResult:
    """Result of army validation with errors and summary data."""

    is_valid: bool
    errors: List[str]
    total_force_points: int
    total_magic_points: int
    army_point_totals: Dict[str, int]


@dataclass
class ArmyComposition:
    """Represents an army's composition for validation."""

    army_type: str
    units: List[Any]  # Unit objects or dicts

    def get_total_points(self) -> int:
        """Calculate total points for this army."""
        return sum(
            getattr(unit, "max_health", unit.get("max_health", 0))
            for unit in self.units
        )

    def get_unit_count(self) -> int:
        """Get the number of units in this army."""
        return len(self.units)


class DragonDiceArmyValidator:
    """
    Validates army compositions according to official Dragon Dice rules.

    Official Rules (Dragon Dice v4.01d):
    1. Each army must have at least 1 unit
    2. No army can exceed 50% of total force points (rounded down)
    3. Magic units cannot exceed 50% of total force points (rounded down)
    4. Total army points must equal selected force size
    """

    def __init__(self, unit_roster=None):
        """
        Initialize validator.

        Args:
            unit_roster: Optional unit roster for looking up unit definitions
        """
        self.unit_roster = unit_roster

    def validate_army_composition(
        self, armies: List[ArmyComposition], force_size: int, num_players: int = 2
    ) -> ValidationResult:
        """
        Validate complete army composition according to Dragon Dice rules.

        Args:
            armies: List of ArmyComposition objects to validate
            force_size: Total force size in points
            num_players: Number of players (affects horde army requirements)

        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        total_force_points = 0
        total_magic_points = 0
        army_point_totals = {}

        # Calculate limits
        max_points_per_army = force_size // 2  # 50% rounded down
        max_magic_points = force_size // 2  # 50% rounded down

        for army in armies:
            # Skip horde army validation for single player games
            if army.army_type.lower() == "horde" and num_players <= 1:
                continue

            # Rule 1: Each army must have at least 1 unit
            if army.get_unit_count() == 0:
                errors.append(f"{army.army_type} Army must have at least 1 unit")

            # Calculate army points
            army_points = army.get_total_points()
            army_point_totals[army.army_type] = army_points

            # Rule 2: No army can exceed 50% of total force points
            if army_points > max_points_per_army:
                errors.append(
                    f"{army.army_type} Army ({army_points} pts) exceeds maximum "
                    f"{max_points_per_army} pts (50% of {force_size} pts)"
                )

            # Count magic unit points for Rule 3
            magic_points_in_army = self._count_magic_unit_points(army.units)
            total_magic_points += magic_points_in_army
            total_force_points += army_points

        # Rule 3: Magic units cannot exceed 50% of total force points
        if total_magic_points > max_magic_points:
            errors.append(
                f"Magic units ({total_magic_points} pts) exceed maximum "
                f"{max_magic_points} pts (50% of {force_size} pts)"
            )

        # Rule 4: Total army points must equal selected force size
        if total_force_points != force_size:
            errors.append(
                f"Total army points ({total_force_points} pts) must equal "
                f"selected force size ({force_size} pts)"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            total_force_points=total_force_points,
            total_magic_points=total_magic_points,
            army_point_totals=army_point_totals,
        )

    def _count_magic_unit_points(self, units: List[Any]) -> int:
        """Count total points from magic units."""
        magic_points = 0

        for unit in units:
            # Try to get unit definition to check class type
            unit_type = getattr(unit, "unit_type", unit.get("unit_type", ""))
            unit_def = None

            if self.unit_roster and unit_type:
                unit_def = self.unit_roster.get_unit_definition(unit_type)

            # Check if unit is magic class
            if unit_def and unit_def.get("unit_class_type") == "Magic":
                unit_points = getattr(unit, "max_health", unit.get("max_health", 0))
                magic_points += unit_points

        return magic_points

    def validate_single_army(
        self, army: ArmyComposition, max_points: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate a single army against point limits.

        Args:
            army: ArmyComposition to validate
            max_points: Maximum points allowed for this army

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check minimum unit requirement
        if army.get_unit_count() == 0:
            errors.append(f"{army.army_type} Army must have at least 1 unit")

        # Check point limit
        army_points = army.get_total_points()
        if army_points > max_points:
            errors.append(
                f"{army.army_type} Army ({army_points} pts) exceeds maximum {max_points} pts"
            )

        return len(errors) == 0, errors

    def get_force_size_limits(self, force_size: int) -> Dict[str, int]:
        """
        Get various limits based on force size.

        Args:
            force_size: Total force size in points

        Returns:
            Dictionary with limit values
        """
        return {
            "max_points_per_army": force_size // 2,
            "max_magic_points": force_size // 2,
            "total_force_size": force_size,
        }

    def create_validation_summary(self, result: ValidationResult) -> str:
        """
        Create a human-readable summary of validation results.

        Args:
            result: ValidationResult to summarize

        Returns:
            Formatted string summary
        """
        if result.is_valid:
            return "✅ Army composition is valid"

        error_summary = "❌ Army composition validation failed:\n"
        error_summary += "• " + "\n• ".join(result.errors)
        return error_summary


class ArmyCompositionBuilder:
    """Helper class for building ArmyComposition objects from various sources."""

    @staticmethod
    def from_army_widgets(army_widgets: Dict[str, Any]) -> List[ArmyComposition]:
        """
        Build army compositions from UI army widgets.

        Args:
            army_widgets: Dictionary of army type -> army widget

        Returns:
            List of ArmyComposition objects
        """
        armies = []

        for army_type, widget in army_widgets.items():
            if hasattr(widget, "current_units"):
                units = widget.current_units
            else:
                units = []

            armies.append(ArmyComposition(army_type=army_type, units=units))

        return armies

    @staticmethod
    def from_player_data(player_data: Dict[str, Any]) -> List[ArmyComposition]:
        """
        Build army compositions from player setup data.

        Args:
            player_data: Player data dictionary with armies

        Returns:
            List of ArmyComposition objects
        """
        armies = []

        armies_data = player_data.get("armies", {})
        for army_key, army_details in armies_data.items():
            units = army_details.get("units", [])
            armies.append(ArmyComposition(army_type=army_key.title(), units=units))

        return armies
