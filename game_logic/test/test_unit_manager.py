"""
Unit tests for unit management logic.

Tests the extracted business logic for managing, sorting, and organizing
Dragon Dice units independently of UI components.
"""

import unittest
from unittest.mock import MagicMock, Mock

from game_logic.unit_manager import (
    SortCriteria,
    UnitCollectionManager,
    UnitInstanceConfig,
    UnitInstanceManager,
    UnitOrganizer,
    UnitSorter,
)


class TestSortCriteria(unittest.TestCase):
    """Test the SortCriteria dataclass."""

    def test_default_creation(self):
        """Test creating SortCriteria with defaults."""
        criteria = SortCriteria()

        assert criteria.primary_key == "max_health"
        assert criteria.secondary_key == "unit_class_type"
        assert criteria.tertiary_key == "display_name"
        assert not criteria.reverse_primary
        assert not criteria.reverse_secondary
        assert not criteria.reverse_tertiary

    def test_custom_creation(self):
        """Test creating SortCriteria with custom values."""
        criteria = SortCriteria(primary_key="display_name", reverse_primary=True, reverse_secondary=True)

        assert criteria.primary_key == "display_name"
        assert criteria.reverse_primary
        assert criteria.reverse_secondary
        assert not criteria.reverse_tertiary


class TestUnitInstanceConfig(unittest.TestCase):
    """Test the UnitInstanceConfig dataclass."""

    def test_generate_instance_id_default(self):
        """Test generating instance ID with default pattern."""
        config = UnitInstanceConfig(army_name="Home Guard", unit_type_id="goblin_thug", instance_count=2)

        instance_id = config.generate_instance_id()
        assert instance_id == "home_guard_goblin_thug_3"

    def test_generate_instance_id_custom_pattern(self):
        """Test generating instance ID with custom pattern."""
        config = UnitInstanceConfig(
            army_name="Campaign Army",
            unit_type_id="orc_warrior",
            instance_count=0,
            naming_pattern="{unit_type}_{army}_{count:02d}",
        )

        instance_id = config.generate_instance_id()
        assert instance_id == "orc_warrior_campaign_army_01"


class TestUnitSorter(unittest.TestCase):
    """Test the UnitSorter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_units = [
            {"display_name": "Thug", "max_health": 1, "unit_class_type": "Heavy Melee"},
            {"display_name": "Archer", "max_health": 2, "unit_class_type": "Missile"},
            {"display_name": "Wizard", "max_health": 1, "unit_class_type": "Magic"},
            {
                "display_name": "Cutthroat",
                "max_health": 2,
                "unit_class_type": "Heavy Melee",
            },
            {
                "display_name": "Berserker",
                "max_health": 3,
                "unit_class_type": "Heavy Melee",
            },
        ]

    def test_sort_units_default(self):
        """Test sorting with default configuration."""
        sorted_units = UnitSorter.sort_units(self.test_units)

        # Should sort by health (1,1,2,2,3), then class type (Heavy Melee before Magic), then name
        expected_order = ["Thug", "Wizard", "Cutthroat", "Archer", "Berserker"]
        actual_order = [unit["display_name"] for unit in sorted_units]

        assert actual_order == expected_order

    def test_sort_units_alphabetical(self):
        """Test sorting alphabetically."""
        sorted_units = UnitSorter.sort_units(self.test_units, "alphabetical")

        expected_order = ["Archer", "Berserker", "Cutthroat", "Thug", "Wizard"]
        actual_order = [unit["display_name"] for unit in sorted_units]

        assert actual_order == expected_order

    def test_sort_units_by_cost(self):
        """Test sorting by cost (health points)."""
        sorted_units = UnitSorter.sort_units(self.test_units, "by_cost")

        # Should sort by health, then name
        expected_costs = [1, 1, 2, 2, 3]
        actual_costs = [unit["max_health"] for unit in sorted_units]

        assert actual_costs == expected_costs

    def test_sort_units_by_power_desc(self):
        """Test sorting by power descending."""
        sorted_units = UnitSorter.sort_units(self.test_units, "by_power_desc")

        # Should sort by health descending
        expected_costs = [3, 2, 2, 1, 1]
        actual_costs = [unit["max_health"] for unit in sorted_units]

        assert actual_costs == expected_costs

    def test_sort_units_by_criteria(self):
        """Test sorting with custom criteria."""
        criteria = SortCriteria(
            primary_key="unit_class_type",
            secondary_key="max_health",
            tertiary_key="display_name",
        )

        sorted_units = UnitSorter.sort_units_by_criteria(self.test_units, criteria)

        # Should group by class type first
        class_types = [unit["unit_class_type"] for unit in sorted_units]
        assert class_types.index("Heavy Melee") < class_types.index("Magic")
        assert class_types.index("Heavy Melee") < class_types.index("Missile")

    def test_sort_units_custom(self):
        """Test sorting with custom key function."""
        # Sort by name length descending
        sorted_units = UnitSorter.sort_units_custom(self.test_units, lambda unit: -len(unit["display_name"]))

        expected_order = ["Cutthroat", "Berserker", "Archer", "Wizard", "Thug"]
        actual_order = [unit["display_name"] for unit in sorted_units]

        assert actual_order == expected_order

    def test_sort_units_empty_list(self):
        """Test sorting empty list."""
        sorted_units = UnitSorter.sort_units([])
        assert sorted_units == []


class TestUnitOrganizer(unittest.TestCase):
    """Test the UnitOrganizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_units = [
            {
                "unit_type_id": "goblin_thug",
                "display_name": "Thug",
                "unit_class_type": "Heavy Melee",
                "max_health": 1,
            },
            {
                "unit_type_id": "goblin_archer",
                "display_name": "Archer",
                "unit_class_type": "Missile",
                "max_health": 2,
            },
            {
                "unit_type_id": "feral_lynx",
                "display_name": "Lynx",
                "unit_class_type": "Heavy Melee",
                "max_health": 1,
            },
            {
                "unit_type_id": "orc_wizard",
                "display_name": "Wizard",
                "unit_class_type": "Magic",
                "max_health": 3,
            },
            {
                "unit_type_id": "goblin_berserker",
                "display_name": "Berserker",
                "unit_class_type": "Heavy Melee",
                "max_health": 4,
            },
        ]

    def test_group_by_species(self):
        """Test grouping units by species."""
        # Create a mock roster that doesn't interfere with the species extraction
        mock_roster = Mock()
        groups = UnitOrganizer.group_by_species(self.test_units, mock_roster)

        assert "Goblin" in groups
        assert "Feral" in groups
        assert "Orc" in groups

        # Check that goblin units are grouped together
        goblin_units = groups["Goblin"]
        goblin_names = [unit["display_name"] for unit in goblin_units]
        assert "Thug" in goblin_names
        assert "Archer" in goblin_names
        assert "Berserker" in goblin_names

        # Check single unit groups
        assert len(groups["Feral"]) == 1
        assert len(groups["Orc"]) == 1

    def test_group_by_species_no_roster(self):
        """Test grouping by species without roster."""
        groups = UnitOrganizer.group_by_species(self.test_units, None)

        assert groups == {"All Units": self.test_units}

    def test_group_by_class_type(self):
        """Test grouping units by class type."""
        groups = UnitOrganizer.group_by_class_type(self.test_units)

        assert "Heavy Melee" in groups
        assert "Missile" in groups
        assert "Magic" in groups

        # Check Heavy Melee group has 3 units
        heavy_melee_units = groups["Heavy Melee"]
        assert len(heavy_melee_units) == 3

        # Check single unit groups
        assert len(groups["Missile"]) == 1
        assert len(groups["Magic"]) == 1

    def test_group_by_cost_range_default(self):
        """Test grouping by default cost ranges."""
        groups = UnitOrganizer.group_by_cost_range(self.test_units)

        assert "1 pt" in groups
        assert "2 pt" in groups
        assert "3 pt" in groups
        assert "4-6 pts" in groups

        # Check 1 pt group has 2 units
        one_pt_units = groups["1 pt"]
        assert len(one_pt_units) == 2

        # Check 4 pt unit is in 4-6 pts range
        four_pt_units = groups["4-6 pts"]
        assert len(four_pt_units) == 1
        assert four_pt_units[0]["display_name"] == "Berserker"

    def test_group_by_cost_range_custom(self):
        """Test grouping by custom cost ranges."""
        custom_ranges = [(1, 2), (3, 5)]
        groups = UnitOrganizer.group_by_cost_range(self.test_units, custom_ranges)

        assert "1-2 pts" in groups
        assert "3-5 pts" in groups

        # Check 1-2 pts group has 3 units (1, 1, 2 health)
        low_cost_units = groups["1-2 pts"]
        assert len(low_cost_units) == 3

        # Check 3-5 pts group has 2 units (3, 4 health)
        high_cost_units = groups["3-5 pts"]
        assert len(high_cost_units) == 2

    def test_filter_units_string(self):
        """Test filtering units by string criteria."""
        filters = {"unit_class_type": "Heavy"}

        filtered_units = UnitOrganizer.filter_units(self.test_units, filters)

        # Should find 3 Heavy Melee units
        assert len(filtered_units) == 3
        for unit in filtered_units:
            assert "Heavy" in unit["unit_class_type"]

    def test_filter_units_numeric(self):
        """Test filtering units by numeric criteria."""
        filters = {"max_health": 1}

        filtered_units = UnitOrganizer.filter_units(self.test_units, filters)

        # Should find 2 units with 1 health
        assert len(filtered_units) == 2
        for unit in filtered_units:
            assert unit["max_health"] == 1

    def test_filter_units_list(self):
        """Test filtering units by list criteria."""
        filters = {"max_health": [1, 3]}

        filtered_units = UnitOrganizer.filter_units(self.test_units, filters)

        # Should find 3 units (2 with health 1, 1 with health 3)
        assert len(filtered_units) == 3
        for unit in filtered_units:
            assert unit["max_health"] in [1, 3]

    def test_filter_units_function(self):
        """Test filtering units by function criteria."""
        filters = {"max_health": lambda x: x > 2}

        filtered_units = UnitOrganizer.filter_units(self.test_units, filters)

        # Should find 2 units with health > 2
        assert len(filtered_units) == 2
        for unit in filtered_units:
            assert unit["max_health"] > 2

    def test_filter_units_multiple_criteria(self):
        """Test filtering units by multiple criteria."""
        filters = {"unit_class_type": "Heavy", "max_health": 1}

        filtered_units = UnitOrganizer.filter_units(self.test_units, filters)

        # Should find 2 Heavy Melee units with 1 health
        assert len(filtered_units) == 2
        for unit in filtered_units:
            assert "Heavy" in unit["unit_class_type"]
            assert unit["max_health"] == 1


class TestUnitInstanceManager(unittest.TestCase):
    """Test the UnitInstanceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock unit roster
        self.mock_roster = Mock()
        self.mock_unit = Mock()
        self.mock_unit.unit_type = "goblin_thug"
        self.mock_unit.unit_id = "home_goblin_thug_1"

        self.mock_roster.create_unit_instance.return_value = self.mock_unit

        self.manager = UnitInstanceManager(self.mock_roster)

    def test_create_unit_instance(self):
        """Test creating a unit instance."""
        config = UnitInstanceConfig(army_name="Home Guard", unit_type_id="goblin_thug", instance_count=0)

        unit = self.manager.create_unit_instance(config)

        assert unit is not None
        self.mock_roster.create_unit_instance.assert_called_once_with("goblin_thug", "home_guard_goblin_thug_1")

    def test_create_unit_instance_with_existing_units(self):
        """Test creating unit instance with existing units count."""
        existing_units = [Mock(unit_type="goblin_thug"), Mock(unit_type="goblin_thug")]

        config = UnitInstanceConfig(army_name="Home Guard", unit_type_id="goblin_thug")

        self.manager.create_unit_instance(config, existing_units)

        # Should create instance with count 3 (2 existing + 1)
        self.mock_roster.create_unit_instance.assert_called_once_with("goblin_thug", "home_guard_goblin_thug_3")

    def test_create_unit_instance_no_roster(self):
        """Test creating unit instance without roster."""
        manager = UnitInstanceManager(None)
        config = UnitInstanceConfig("Home", "goblin_thug")

        unit = manager.create_unit_instance(config)

        assert unit is None

    def test_get_instance_count(self):
        """Test getting instance count."""
        config = UnitInstanceConfig("Home Guard", "goblin_thug")

        # Create an instance
        self.manager.create_unit_instance(config)

        count = self.manager.get_instance_count("Home Guard", "goblin_thug")
        assert count == 1

    def test_reset_instance_counts_specific_army(self):
        """Test resetting instance counts for specific army."""
        config1 = UnitInstanceConfig("Home Guard", "goblin_thug")
        config2 = UnitInstanceConfig("Campaign Army", "orc_warrior")

        self.manager.create_unit_instance(config1)
        self.manager.create_unit_instance(config2)

        # Reset only Home Guard counts
        self.manager.reset_instance_counts("Home Guard")

        assert self.manager.get_instance_count("Home Guard", "goblin_thug") == 0
        assert self.manager.get_instance_count("Campaign Army", "orc_warrior") == 1

    def test_reset_instance_counts_all(self):
        """Test resetting all instance counts."""
        config1 = UnitInstanceConfig("Home Guard", "goblin_thug")
        config2 = UnitInstanceConfig("Campaign Army", "orc_warrior")

        self.manager.create_unit_instance(config1)
        self.manager.create_unit_instance(config2)

        # Reset all counts
        self.manager.reset_instance_counts()

        assert self.manager.get_instance_count("Home Guard", "goblin_thug") == 0
        assert self.manager.get_instance_count("Campaign Army", "orc_warrior") == 0

    def test_bulk_create_instances(self):
        """Test creating multiple instances in bulk."""
        configs = [
            UnitInstanceConfig("Home", "goblin_thug"),
            UnitInstanceConfig("Home", "goblin_archer"),
            UnitInstanceConfig("Campaign", "orc_warrior"),
        ]

        instances = self.manager.bulk_create_instances(configs)

        assert len(instances) == 3
        assert self.mock_roster.create_unit_instance.call_count == 3


class TestUnitCollectionManager(unittest.TestCase):
    """Test the UnitCollectionManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_roster = Mock()
        self.manager = UnitCollectionManager(self.mock_roster)

        self.test_units = [
            {
                "unit_type_id": "goblin_thug",
                "display_name": "Thug",
                "unit_class_type": "Heavy Melee",
                "max_health": 1,
            },
            {
                "unit_type_id": "goblin_archer",
                "display_name": "Archer",
                "unit_class_type": "Missile",
                "max_health": 2,
            },
            {
                "unit_type_id": "feral_lynx",
                "display_name": "Lynx",
                "unit_class_type": "Heavy Melee",
                "max_health": 1,
            },
            {
                "unit_type_id": "orc_wizard",
                "display_name": "Wizard",
                "unit_class_type": "Magic",
                "max_health": 3,
            },
        ]

    def test_organize_units_for_display_species(self):
        """Test organizing units by species for display."""
        groups = self.manager.organize_units_for_display(self.test_units, "species")

        assert "Goblin" in groups
        assert "Feral" in groups
        assert "Orc" in groups

        # Units within groups should be sorted
        goblin_units = groups["Goblin"]
        assert len(goblin_units) == 2

    def test_organize_units_for_display_class(self):
        """Test organizing units by class for display."""
        groups = self.manager.organize_units_for_display(self.test_units, "class")

        assert "Heavy Melee" in groups
        assert "Missile" in groups
        assert "Magic" in groups

    def test_organize_units_for_display_cost(self):
        """Test organizing units by cost for display."""
        groups = self.manager.organize_units_for_display(self.test_units, "cost")

        assert "1 pt" in groups
        assert "2 pt" in groups
        assert "3 pt" in groups

    def test_search_units(self):
        """Test searching units by term."""
        # Search for "arch" should find "Archer"
        results = self.manager.search_units(self.test_units, "arch")

        assert len(results) == 1
        assert results[0]["display_name"] == "Archer"

    def test_search_units_multiple_fields(self):
        """Test searching units across multiple fields."""
        # Search for "Heavy" should find units with Heavy Melee class
        results = self.manager.search_units(self.test_units, "Heavy")

        assert len(results) == 2
        for unit in results:
            assert unit["unit_class_type"] == "Heavy Melee"

    def test_search_units_empty_term(self):
        """Test searching with empty term returns all units."""
        results = self.manager.search_units(self.test_units, "")

        assert len(results) == len(self.test_units)

    def test_search_units_no_matches(self):
        """Test searching with term that matches nothing."""
        results = self.manager.search_units(self.test_units, "nonexistent")

        assert len(results) == 0

    def test_get_unit_statistics(self):
        """Test generating unit collection statistics."""
        stats = self.manager.get_unit_statistics(self.test_units)

        assert stats["total_units"] == 4
        assert stats["total_cost"] == 7  # 1+2+1+3
        assert stats["average_cost"] == 1.8  # 7/4 rounded
        assert stats["min_cost"] == 1
        assert stats["max_cost"] == 3
        assert stats["unique_classes"] == 3

        # Check class distribution
        assert stats["class_distribution"]["Heavy Melee"] == 2
        assert stats["class_distribution"]["Missile"] == 1
        assert stats["class_distribution"]["Magic"] == 1

    def test_get_unit_statistics_empty(self):
        """Test statistics for empty unit collection."""
        stats = self.manager.get_unit_statistics([])

        assert stats == {"total_units": 0}


if __name__ == "__main__":
    unittest.main()
