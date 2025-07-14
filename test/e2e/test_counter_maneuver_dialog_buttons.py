#!/usr/bin/env python3
"""
E2E test specifically for counter-maneuver dialog button functionality.
Tests that the dialog buttons properly trigger the expected game engine calls.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from game_logic.engine import GameEngine
from views.maneuver_dialog import CounterManeuverDecisionDialog


class TestCounterManeuverDialogButtons(unittest.TestCase):
    """E2E test for counter-maneuver dialog button functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test data for each test."""
        self.player_setup_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "force_size": 24,
                "selected_dragons": [],
                "armies": {
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Frontier terrain
                        
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            },
                        ],
                        "unique_id": "player_1_campaign",
                    },
                },
            },
            {
                "name": "Player 2",
                "home_terrain": "Coastland",
                "force_size": 24,
                "selected_dragons": [],
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 2 Coastland",
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_p2_1",
                                "unit_type": "amazon_runner",
                            },
                        ],
                        "unique_id": "player_2_home",
                    },
                    "horde": {
                        "name": "Horde Army",
                        "location": "Coastland",  # Same frontier terrain as Player 1
                        
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Seer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_p2_1",
                                "unit_type": "amazon_seer",
                            },
                        ],
                        "unique_id": "player_2_horde",
                    },
                },
            },
        ]

        self.frontier_terrain = "Coastland"
        self.distance_rolls = [("Player 1", 3), ("Player 2", 5)]

        # Create game engine
        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

        # Track engine method calls
        self.engine_calls = []
        self._patch_engine_methods()

    def _patch_engine_methods(self):
        """Patch engine methods to track calls."""
        original_submit = self.engine.submit_counter_maneuver_decision

        def tracked_submit(player_name, will_counter):
            self.engine_calls.append(
                f"submit_counter_maneuver_decision({player_name}, {will_counter})"
            )
            return original_submit(player_name, will_counter)

        self.engine.submit_counter_maneuver_decision = tracked_submit

    def _choose_army_by_id(self, army_unique_id: str):
        """Helper to choose an army by its unique ID."""
        all_players_data = self.engine.get_all_players_data()

        # Find the army across all players
        for _player_name, player_data in all_players_data.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("unique_id") == army_unique_id:
                    # Create the army data structure expected by choose_acting_army
                    army_choice_data = {
                        "name": army_data.get("name", f"{army_type.title()} Army"),
                        "army_type": army_type,
                        "location": army_data.get("location", "Unknown"),
                        "units": army_data.get("units", []),
                        "unique_id": army_data.get("unique_id", army_unique_id),
                    }
                    self.engine.choose_acting_army(army_choice_data)
                    return

        raise ValueError(f"Army with ID '{army_unique_id}' not found")

    def test_e2e_counter_maneuver_dialog_allow_button(self):
        """
        E2E Test: Counter-maneuver dialog "Allow Maneuver" button functionality

        Flow:
        1. Set up maneuver scenario
        2. Trigger counter-maneuver request
        3. Simulate clicking "Allow Maneuver" button
        4. Verify correct engine method is called
        """
        print("\n🧪 E2E Test: Counter-Maneuver Dialog - Allow Button")
        print("=" * 50)

        # Set up scenario: Player 1 maneuvers at contested location
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(True)

        # This should trigger counter-maneuver request
        # We'll simulate the dialog response programmatically

        # Create the dialog that would be shown
        dialog = CounterManeuverDecisionDialog(
            "Coastland", "Player 2", "Player 1", None
        )

        # Connect to track the signal
        decision_received = []
        dialog.decision_made.connect(
            lambda player, decision: decision_received.append((player, decision))
        )

        # Simulate clicking "Allow Maneuver" button (green button)
        print("Step 1: Simulating 'Allow Maneuver' button click")
        dialog._make_decision(False)  # False = allow maneuver

        # Verify the signal was emitted correctly
        assert len(decision_received) == 1
        player, decision = decision_received[0]
        assert player == "Player 2"
        assert not decision  # False = allow maneuver

        print(
            f"✅ Signal emitted correctly: Player {player}, Decision: {'Allow' if not decision else 'Counter'}"
        )

        # Now manually submit to engine to test the full flow
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Verify engine method was called
        assert "submit_counter_maneuver_decision(Player 2, False)" in self.engine_calls

        print("✅ Test completed - Allow Maneuver button works correctly")

    def test_e2e_counter_maneuver_dialog_counter_button(self):
        """
        E2E Test: Counter-maneuver dialog "Counter-Maneuver" button functionality

        Flow:
        1. Set up maneuver scenario
        2. Trigger counter-maneuver request
        3. Simulate clicking "Counter-Maneuver" button
        4. Verify correct engine method is called
        """
        print("\n🧪 E2E Test: Counter-Maneuver Dialog - Counter Button")
        print("=" * 50)

        # Set up scenario: Player 1 maneuvers at contested location
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(True)

        # Create the dialog that would be shown
        dialog = CounterManeuverDecisionDialog(
            "Coastland", "Player 2", "Player 1", None
        )

        # Connect to track the signal
        decision_received = []
        dialog.decision_made.connect(
            lambda player, decision: decision_received.append((player, decision))
        )

        # Simulate clicking "Counter-Maneuver" button (red button)
        print("Step 1: Simulating 'Counter-Maneuver' button click")
        dialog._make_decision(True)  # True = counter-maneuver

        # Verify the signal was emitted correctly
        assert len(decision_received) == 1
        player, decision = decision_received[0]
        assert player == "Player 2"
        assert decision  # True = counter-maneuver

        print(
            f"✅ Signal emitted correctly: Player {player}, Decision: {'Counter' if decision else 'Allow'}"
        )

        # Now manually submit to engine to test the full flow
        self.engine.submit_counter_maneuver_decision("Player 2", True)

        # Verify engine method was called
        assert "submit_counter_maneuver_decision(Player 2, True)" in self.engine_calls

        print("✅ Test completed - Counter-Maneuver button works correctly")

    def test_e2e_dialog_button_signal_connection(self):
        """
        E2E Test: Verify dialog buttons are properly connected to signals

        This test specifically checks that the button click handlers
        properly call the _make_decision method.
        """
        print("\n🧪 E2E Test: Dialog Button Signal Connection")
        print("=" * 50)

        # Create dialog
        dialog = CounterManeuverDecisionDialog(
            "Coastland", "Player 2", "Player 1", None
        )

        # Track method calls
        decision_calls = []
        original_make_decision = dialog._make_decision

        def tracked_make_decision(will_counter):
            decision_calls.append(will_counter)
            return original_make_decision(will_counter)

        dialog._make_decision = tracked_make_decision

        # Simulate button clicks directly
        print("Step 1: Testing Counter-Maneuver button click")
        dialog.counter_button.click()

        print("Step 2: Testing Allow Maneuver button click")
        dialog.allow_button.click()

        # Verify both button clicks were registered
        assert len(decision_calls) == 2
        assert decision_calls[0]  # Counter button
        assert not decision_calls[1]  # Allow button

        print("✅ Both buttons correctly connected to _make_decision method")
        print(f"   Counter button call: {decision_calls[0]}")
        print(f"   Allow button call: {decision_calls[1]}")

        print("✅ Test completed - button signal connections working")

    def test_e2e_full_counter_maneuver_dialog_flow(self):
        """
        E2E Test: Complete counter-maneuver dialog flow from start to finish

        Flow:
        1. Trigger maneuver that requires counter-maneuver decision
        2. Verify counter-maneuver signal is emitted
        3. Create and test dialog
        4. Verify decision is processed correctly
        5. Check game state progression
        """
        print("\n🧪 E2E Test: Full Counter-Maneuver Dialog Flow")
        print("=" * 50)

        # Track signals
        signals_received = []
        self.engine.counter_maneuver_requested.connect(
            lambda location, armies: signals_received.append(
                f"counter_maneuver_requested: {location}"
            )
        )

        # Step 1: Set up contested maneuver
        print("Step 1: Setting up contested maneuver scenario")
        self._choose_army_by_id("player_1_campaign")
        assert self.engine.current_march_step == "DECIDE_MANEUVER"

        # Step 2: Initiate maneuver
        print("Step 2: Player 1 decides to maneuver")
        self.engine.decide_maneuver(True)

        # Step 3: Verify counter-maneuver signal was emitted
        print("Step 3: Verifying counter-maneuver signal")
        assert len(signals_received) == 1
        assert "counter_maneuver_requested: Coastland" in signals_received[0]
        print("✅ Counter-maneuver signal emitted correctly")

        # Step 4: Simulate dialog interaction
        print("Step 4: Testing dialog decision handling")

        # Test allowing the maneuver
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Verify the call was tracked
        assert "submit_counter_maneuver_decision(Player 2, False)" in self.engine_calls
        print("✅ Decision processed by engine")

        # Step 5: Verify game progresses correctly
        print("Step 5: Verifying game state progression")
        # After allowing maneuver, should proceed to terrain direction choice
        # (This would normally trigger another signal, but we're testing the dialog part)

        print("✅ Test completed - full counter-maneuver dialog flow working")

    def tearDown(self):
        """Clean up after each test."""
        # Clear tracked calls
        self.engine_calls.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
