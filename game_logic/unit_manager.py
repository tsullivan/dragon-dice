"""
Unit management logic for Dragon Dice units.

This module contains pure Python business logic for sorting, organizing,
and managing unit instances, extracted from UI components for better
testability and reusability.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from collections import defaultdict
import utils.constants as constants


@dataclass
class SortCriteria:
    """Defines criteria for sorting units."""

    primary_key: str = "max_health"
    secondary_key: str = "unit_class_type"
    tertiary_key: str = "display_name"
    reverse_primary: bool = False
    reverse_secondary: bool = False
    reverse_tertiary: bool = False


@dataclass
class UnitInstanceConfig:
    """Configuration for creating unit instances."""

    army_name: str
    unit_type_id: str
    instance_count: int = 0
    naming_pattern: str = "{army}_{unit_type}_{count}"

    def generate_instance_id(self) -> str:
        """Generate a unique instance ID."""
        safe_army_name = self.army_name.lower().replace(" ", "_")
        return self.naming_pattern.format(
            army=safe_army_name,
            unit_type=self.unit_type_id,
            count=self.instance_count + 1,
        )


class UnitSorter:
    """
    Handles sorting of unit collections by various criteria.

    Provides flexible sorting with multiple sort keys and customizable
    ordering for different display contexts.
    """

    # Predefined sort configurations
    SORT_CONFIGS = {
        "display_default": SortCriteria(
            primary_key="max_health",
            secondary_key="unit_class_type",
            tertiary_key="display_name",
        ),
        "alphabetical": SortCriteria(
            primary_key="display_name",
            secondary_key="max_health",
            tertiary_key="unit_class_type",
        ),
        "by_cost": SortCriteria(
            primary_key="max_health",
            secondary_key="display_name",
            tertiary_key="unit_class_type",
        ),
        "by_class": SortCriteria(
            primary_key="unit_class_type",
            secondary_key="max_health",
            tertiary_key="display_name",
        ),
        "by_power_desc": SortCriteria(
            primary_key="max_health",
            secondary_key="unit_class_type",
            tertiary_key="display_name",
            reverse_primary=True,
        ),
    }

    @staticmethod
    def sort_units(
        units: List[Dict[str, Any]], sort_config: str = "display_default"
    ) -> List[Dict[str, Any]]:
        """
        Sort units according to specified configuration.

        Args:
            units: List of unit dictionaries to sort
            sort_config: Name of predefined sort configuration

        Returns:
            Sorted list of unit dictionaries
        """
        if not units:
            return []

        criteria = UnitSorter.SORT_CONFIGS.get(
            sort_config, UnitSorter.SORT_CONFIGS["display_default"]
        )
        return UnitSorter.sort_units_by_criteria(units, criteria)

    @staticmethod
    def sort_units_by_criteria(
        units: List[Dict[str, Any]], criteria: SortCriteria
    ) -> List[Dict[str, Any]]:
        """
        Sort units by specific criteria.

        Args:
            units: List of unit dictionaries to sort
            criteria: SortCriteria object defining sort behavior

        Returns:
            Sorted list of unit dictionaries
        """

        def get_sort_key(unit):
            primary = unit.get(criteria.primary_key, "")
            secondary = unit.get(criteria.secondary_key, "")
            tertiary = unit.get(criteria.tertiary_key, "")

            # Handle numeric vs string sorting
            if isinstance(primary, (int, float)) and criteria.reverse_primary:
                primary = -primary
            if isinstance(secondary, (int, float)) and criteria.reverse_secondary:
                secondary = -secondary
            if isinstance(tertiary, (int, float)) and criteria.reverse_tertiary:
                tertiary = -tertiary

            return (primary, secondary, tertiary)

        sorted_units = sorted(units, key=get_sort_key)

        # Apply reverse flags for string-based sorting
        if criteria.reverse_primary and not isinstance(
            units[0].get(criteria.primary_key, ""), (int, float)
        ):
            sorted_units.reverse()

        return sorted_units

    @staticmethod
    def sort_units_custom(
        units: List[Dict[str, Any]], key_func: Callable
    ) -> List[Dict[str, Any]]:
        """
        Sort units using a custom key function.

        Args:
            units: List of unit dictionaries to sort
            key_func: Function that takes a unit dict and returns sort key

        Returns:
            Sorted list of unit dictionaries
        """
        return sorted(units, key=key_func)


class UnitOrganizer:
    """
    Organizes units by various grouping criteria.

    Handles grouping units by species, class type, cost, and other
    categorization methods for display and management purposes.
    """

    @staticmethod
    def group_by_species(
        units: List[Dict[str, Any]], unit_roster=None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group units by their species.

        Args:
            units: List of unit dictionaries
            unit_roster: Optional unit roster for species lookup

        Returns:
            Dictionary mapping species names to unit lists
        """
        if not unit_roster:
            # Fallback grouping without roster
            return {"All Units": units}

        species_groups = defaultdict(list)

        for unit in units:
            unit_type_id = unit.get("unit_type_id", unit.get("id", ""))
            if unit_type_id:
                # Try to determine species from unit type ID
                species = UnitOrganizer._extract_species_from_id(unit_type_id)
                species_groups[species].append(unit)
            else:
                species_groups["Unknown"].append(unit)

        return dict(species_groups)

    @staticmethod
    def group_by_class_type(
        units: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group units by their class type.

        Args:
            units: List of unit dictionaries

        Returns:
            Dictionary mapping class types to unit lists
        """
        class_groups = defaultdict(list)

        for unit in units:
            class_type = unit.get("unit_class_type", "Unknown")
            class_groups[class_type].append(unit)

        return dict(class_groups)

    @staticmethod
    def group_by_cost_range(
        units: List[Dict[str, Any]], ranges: List[Tuple[int, int]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group units by cost ranges.

        Args:
            units: List of unit dictionaries
            ranges: List of (min, max) cost ranges. Defaults to standard ranges.

        Returns:
            Dictionary mapping cost range names to unit lists
        """
        if ranges is None:
            ranges = [(1, 1), (2, 2), (3, 3), (4, 6), (7, 10)]

        cost_groups = defaultdict(list)

        for unit in units:
            cost = unit.get("max_health", 0)
            range_name = UnitOrganizer._get_cost_range_name(cost, ranges)
            cost_groups[range_name].append(unit)

        return dict(cost_groups)

    @staticmethod
    def filter_units(
        units: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter units based on criteria.

        Args:
            units: List of unit dictionaries
            filters: Dictionary of field_name -> filter_value pairs

        Returns:
            Filtered list of unit dictionaries
        """
        filtered_units = units.copy()

        for field, value in filters.items():
            if value is None:
                continue

            if isinstance(value, str):
                # String matching (case-insensitive partial match)
                filtered_units = [
                    unit
                    for unit in filtered_units
                    if value.lower() in str(unit.get(field, "")).lower()
                ]
            elif isinstance(value, (int, float)):
                # Exact numeric match
                filtered_units = [
                    unit for unit in filtered_units if unit.get(field) == value
                ]
            elif isinstance(value, (list, tuple)):
                # Match any value in list
                filtered_units = [
                    unit for unit in filtered_units if unit.get(field) in value
                ]
            elif callable(value):
                # Custom filter function
                filtered_units = [
                    unit for unit in filtered_units if value(unit.get(field))
                ]

        return filtered_units

    @staticmethod
    def _extract_species_from_id(unit_type_id: str) -> str:
        """Extract species name from unit type ID."""
        # Common patterns: "goblin_thug", "feral_lynx_folk", etc.
        if "_" in unit_type_id:
            return unit_type_id.split("_")[0].title()
        return "Unknown"

    @staticmethod
    def _get_cost_range_name(cost: int, ranges: List[Tuple[int, int]]) -> str:
        """Get descriptive name for cost range."""
        for min_cost, max_cost in ranges:
            if min_cost <= cost <= max_cost:
                if min_cost == max_cost:
                    return f"{min_cost} pt"
                else:
                    return f"{min_cost}-{max_cost} pts"
        return f"{cost} pts"


class UnitInstanceManager:
    """
    Manages creation and tracking of unit instances.

    Handles the creation of unique unit instances from unit types,
    including ID generation and instance counting.
    """

    def __init__(self, unit_roster=None):
        """
        Initialize instance manager.

        Args:
            unit_roster: Optional unit roster for creating instances
        """
        self.unit_roster = unit_roster
        self.instance_counts = defaultdict(int)  # Track instances per army/unit type

    def create_unit_instance(
        self, config: UnitInstanceConfig, existing_units: List[Any] = None
    ) -> Optional[Any]:
        """
        Create a new unit instance.

        Args:
            config: UnitInstanceConfig specifying creation parameters
            existing_units: Optional list of existing units to check for duplicates

        Returns:
            New unit instance or None if creation failed
        """
        if not self.unit_roster:
            return None

        # Update instance count based on existing units
        if existing_units:
            current_count = sum(
                1
                for unit in existing_units
                if getattr(unit, "unit_type", unit.get("unit_type", ""))
                == config.unit_type_id
            )
            config.instance_count = current_count

        # Generate unique instance ID
        instance_id = config.generate_instance_id()

        # Create the unit instance
        new_unit = self.unit_roster.create_unit_instance(
            config.unit_type_id, instance_id
        )

        if new_unit:
            # Track the creation
            key = f"{config.army_name}_{config.unit_type_id}"
            self.instance_counts[key] += 1

        return new_unit

    def get_instance_count(self, army_name: str, unit_type_id: str) -> int:
        """
        Get current instance count for army/unit type combination.

        Args:
            army_name: Name of the army
            unit_type_id: ID of the unit type

        Returns:
            Current instance count
        """
        key = f"{army_name}_{unit_type_id}"
        return self.instance_counts[key]

    def reset_instance_counts(self, army_name: str = None):
        """
        Reset instance counts.

        Args:
            army_name: If specified, only reset counts for this army
        """
        if army_name:
            keys_to_reset = [
                key
                for key in self.instance_counts.keys()
                if key.startswith(f"{army_name}_")
            ]
            for key in keys_to_reset:
                self.instance_counts[key] = 0
        else:
            self.instance_counts.clear()

    def bulk_create_instances(self, configs: List[UnitInstanceConfig]) -> List[Any]:
        """
        Create multiple unit instances.

        Args:
            configs: List of UnitInstanceConfig objects

        Returns:
            List of created unit instances
        """
        instances = []

        for config in configs:
            instance = self.create_unit_instance(config)
            if instance:
                instances.append(instance)

        return instances


class UnitCollectionManager:
    """
    High-level manager for unit collections combining sorting, organizing, and instance management.

    Provides a unified interface for complex unit management operations.
    """

    def __init__(self, unit_roster=None):
        """
        Initialize collection manager.

        Args:
            unit_roster: Optional unit roster for unit operations
        """
        self.unit_roster = unit_roster
        self.sorter = UnitSorter()
        self.organizer = UnitOrganizer()
        self.instance_manager = UnitInstanceManager(unit_roster)

    def organize_units_for_display(
        self, units: List[Dict[str, Any]], organization: str = "species"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize units for display purposes.

        Args:
            units: List of unit dictionaries
            organization: Organization method ("species", "class", "cost")

        Returns:
            Dictionary of organized unit groups
        """
        if organization == "species":
            groups = self.organizer.group_by_species(units, self.unit_roster)
        elif organization == "class":
            groups = self.organizer.group_by_class_type(units)
        elif organization == "cost":
            groups = self.organizer.group_by_cost_range(units)
        else:
            groups = {"All Units": units}

        # Sort units within each group
        for group_name, group_units in groups.items():
            groups[group_name] = self.sorter.sort_units(group_units)

        return groups

    def search_units(
        self,
        units: List[Dict[str, Any]],
        search_term: str,
        search_fields: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search units by term across specified fields.

        Args:
            units: List of unit dictionaries
            search_term: Search term to match
            search_fields: List of fields to search in. Defaults to name and class.

        Returns:
            List of matching units
        """
        if not search_term:
            return units

        if search_fields is None:
            search_fields = ["display_name", "unit_class_type"]

        search_term = search_term.lower()
        matching_units = []

        for unit in units:
            for field in search_fields:
                field_value = str(unit.get(field, "")).lower()
                if search_term in field_value:
                    matching_units.append(unit)
                    break  # Avoid duplicates

        return matching_units

    def get_unit_statistics(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics for a unit collection.

        Args:
            units: List of unit dictionaries

        Returns:
            Dictionary with collection statistics
        """
        if not units:
            return {"total_units": 0}

        costs = [unit.get("max_health", 0) for unit in units]
        class_counts = defaultdict(int)

        for unit in units:
            class_type = unit.get("unit_class_type", "Unknown")
            class_counts[class_type] += 1

        return {
            "total_units": len(units),
            "total_cost": sum(costs),
            "average_cost": round(sum(costs) / len(costs), 1),
            "min_cost": min(costs),
            "max_cost": max(costs),
            "class_distribution": dict(class_counts),
            "unique_classes": len(class_counts),
        }
