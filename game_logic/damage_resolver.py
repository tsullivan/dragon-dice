"""
Damage Resolution System for Dragon Dice.

This module handles damage allocation, unit health calculations,
and damage distribution algorithms according to Dragon Dice rules.
"""

from typing import Any, Dict, List, Tuple

from PySide6.QtCore import QObject, Signal

from utils.field_access import strict_get, strict_get_optional


class DamageAllocation:
    """Represents a damage allocation decision for a unit."""

    def __init__(self, unit_name: str, unit_id: str, damage_taken: int, max_health: int):
        self.unit_name = unit_name
        self.unit_id = unit_id
        self.damage_taken = damage_taken
        self.max_health = max_health
        self.current_health = max(0, max_health - damage_taken)
        self.is_killed = self.current_health == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_name": self.unit_name,
            "unit_id": self.unit_id,
            "damage_taken": self.damage_taken,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "is_killed": self.is_killed,
        }


class DamageResolver(QObject):
    """
    Resolves damage allocation and unit health management
    according to Dragon Dice rules.
    """

    damage_allocated = Signal(dict)  # Emits damage allocation results
    unit_killed = Signal(str, dict)  # unit_name, unit_data

    def __init__(self, game_state_manager, parent=None):
        super().__init__(parent)
        self.game_state_manager = game_state_manager

    def calculate_damage_allocation(
        self, target_units: List[Dict[str, Any]], total_damage: int, allocation_strategy: str = "player_choice"
    ) -> List[DamageAllocation]:
        """
        Calculate how damage should be allocated across units.

        Args:
            target_units: List of unit dictionaries with name, id, health, max_health
            total_damage: Total damage to allocate
            allocation_strategy: How to allocate damage ("player_choice", "weakest_first", "strongest_first")

        Returns:
            List of DamageAllocation objects
        """
        if total_damage <= 0:
            return []

        allocations = []

        if allocation_strategy == "weakest_first":
            allocations = self._allocate_weakest_first(target_units, total_damage)
        elif allocation_strategy == "strongest_first":
            allocations = self._allocate_strongest_first(target_units, total_damage)
        else:
            # Default to equal distribution for player choice guidance
            allocations = self._allocate_equal_distribution(target_units, total_damage)

        return allocations

    def _allocate_weakest_first(self, units: List[Dict[str, Any]], total_damage: int) -> List[DamageAllocation]:
        """Allocate damage to weakest units first."""
        allocations = []
        remaining_damage = total_damage

        # Sort units by current health (weakest first)
        sorted_units = sorted(units, key=lambda u: strict_get(u, "health"))

        for unit in sorted_units:
            if remaining_damage <= 0:
                break

            unit_name = strict_get(unit, "name")
            unit_id = strict_get_optional(unit, "id", unit_name)
            max_health = strict_get(unit, "max_health")
            current_health = strict_get(unit, "health")

            # Allocate minimum of remaining damage or what's needed to kill unit
            damage_to_allocate = min(remaining_damage, current_health)
            remaining_damage -= damage_to_allocate

            allocation = DamageAllocation(unit_name, unit_id, damage_to_allocate, max_health)
            allocations.append(allocation)

        return allocations

    def _allocate_strongest_first(self, units: List[Dict[str, Any]], total_damage: int) -> List[DamageAllocation]:
        """Allocate damage to strongest units first."""
        allocations = []
        remaining_damage = total_damage

        # Sort units by current health (strongest first)
        sorted_units = sorted(units, key=lambda u: strict_get(u, "health"), reverse=True)

        for unit in sorted_units:
            if remaining_damage <= 0:
                break

            unit_name = strict_get(unit, "name")
            unit_id = strict_get_optional(unit, "id", unit_name)
            max_health = strict_get(unit, "max_health")
            current_health = strict_get(unit, "health")

            # Allocate minimum of remaining damage or current health
            damage_to_allocate = min(remaining_damage, current_health)
            remaining_damage -= damage_to_allocate

            allocation = DamageAllocation(unit_name, unit_id, damage_to_allocate, max_health)
            allocations.append(allocation)

        return allocations

    def _allocate_equal_distribution(self, units: List[Dict[str, Any]], total_damage: int) -> List[DamageAllocation]:
        """Distribute damage equally across units."""
        allocations = []

        if not units:
            return allocations

        # Calculate base damage per unit
        damage_per_unit = total_damage // len(units)
        remainder = total_damage % len(units)

        for i, unit in enumerate(units):
            unit_name = strict_get(unit, "name")
            unit_id = strict_get_optional(unit, "id", unit_name)
            max_health = strict_get(unit, "max_health")
            current_health = strict_get(unit, "health")

            # Add remainder to first few units
            damage_to_allocate = damage_per_unit + (1 if i < remainder else 0)

            # Don't exceed current health
            damage_to_allocate = min(damage_to_allocate, current_health)

            allocation = DamageAllocation(unit_name, unit_id, damage_to_allocate, max_health)
            allocations.append(allocation)

        return allocations

    def apply_damage_allocation(
        self, player_name: str, army_identifier: str, allocations: List[DamageAllocation]
    ) -> Dict[str, Any]:
        """
        Apply damage allocation to units in the game state.

        Returns:
            Dictionary with results including killed units and total damage applied
        """
        results = {"total_damage_applied": 0, "units_killed": [], "units_damaged": [], "allocation_details": []}

        for allocation in allocations:
            if allocation.damage_taken <= 0:
                continue

            # Apply damage to unit in game state
            success = self.game_state_manager.apply_damage_to_specific_unit(
                player_name, army_identifier, allocation.unit_id, allocation.damage_taken
            )

            if success:
                results["total_damage_applied"] += allocation.damage_taken
                results["allocation_details"].append(allocation.to_dict())

                if allocation.is_killed:
                    results["units_killed"].append(
                        {"name": allocation.unit_name, "id": allocation.unit_id, "max_health": allocation.max_health}
                    )
                    self.unit_killed.emit(allocation.unit_name, allocation.to_dict())
                else:
                    results["units_damaged"].append(
                        {
                            "name": allocation.unit_name,
                            "id": allocation.unit_id,
                            "damage_taken": allocation.damage_taken,
                            "health_remaining": allocation.current_health,
                        }
                    )

        self.damage_allocated.emit(results)
        return results

    def calculate_optimal_allocation(
        self, units: List[Dict[str, Any]], total_damage: int
    ) -> Tuple[List[DamageAllocation], Dict[str, int]]:
        """
        Calculate multiple allocation strategies and return the most efficient.

        Returns:
            Tuple of (optimal_allocation, strategy_comparison)
        """
        strategies = {
            "weakest_first": self._allocate_weakest_first(units, total_damage),
            "strongest_first": self._allocate_strongest_first(units, total_damage),
            "equal_distribution": self._allocate_equal_distribution(units, total_damage),
        }

        strategy_comparison = {}

        for strategy_name, allocation in strategies.items():
            killed_count = sum(1 for a in allocation if a.is_killed)
            total_health_removed = sum(a.damage_taken for a in allocation)

            strategy_comparison[strategy_name] = {
                "units_killed": killed_count,
                "total_damage_applied": total_health_removed,
                "efficiency_score": killed_count * 10 + total_health_removed,  # Favor killing units
            }

        # Choose strategy with highest efficiency score
        best_strategy = max(strategy_comparison.keys(), key=lambda s: strategy_comparison[s]["efficiency_score"])

        return strategies[best_strategy], strategy_comparison

    def validate_damage_allocation(self, allocations: List[DamageAllocation], expected_total: int) -> Dict[str, Any]:
        """
        Validate that damage allocation is legal and complete.

        Returns:
            Validation result with errors if any
        """
        validation = {"valid": True, "errors": [], "warnings": [], "total_allocated": 0}

        total_allocated = sum(a.damage_taken for a in allocations)
        validation["total_allocated"] = total_allocated

        if total_allocated != expected_total:
            validation["valid"] = False
            validation["errors"].append(
                f"Total damage allocated ({total_allocated}) does not match expected ({expected_total})"
            )

        for allocation in allocations:
            # Check for over-damage
            if allocation.damage_taken > allocation.max_health:
                validation["valid"] = False
                validation["errors"].append(
                    f"Unit {allocation.unit_name} allocated more damage ({allocation.damage_taken}) than max health ({allocation.max_health})"
                )

            # Check for negative damage
            if allocation.damage_taken < 0:
                validation["valid"] = False
                validation["errors"].append(
                    f"Unit {allocation.unit_name} has negative damage allocation ({allocation.damage_taken})"
                )

        return validation
