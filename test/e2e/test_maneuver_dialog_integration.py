#!/usr/bin/env python3
"""
E2E test for ManeuverDialog integration with GameEngine.
Tests the full maneuver dialog flow including counter-maneuver requests.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from game_logic.engine import GameEngine
from views.maneuver_dialog import ManeuverDialog


class TestManeuverDialogIntegration(unittest.TestCase):
    """E2E test for ManeuverDialog integration with GameEngine."""

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
                "armies": {
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Frontier terrain
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
                "armies": {
                    "horde": {
                        "name": "Horde Army",
                        "location": "Coastland",  # Same frontier terrain
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

        # Track signals and method calls
        self.signals_received = []
        self.engine_calls = []
        self._setup_tracking()

    def _setup_tracking(self):
        """Set up signal and method call tracking."""
        # Track signals
        self.engine.counter_maneuver_requested.connect(
            lambda location, armies: self.signals_received.append(
                f"counter_maneuver_requested: {location}, armies: {len(armies)}"
            )
        )

        # Track engine method calls
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

        for _player_name, player_data in all_players_data.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("unique_id") == army_unique_id:
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

    def test_e2e_maneuver_dialog_counter_maneuver_signal_flow(self):
        """
        E2E Test: ManeuverDialog properly handles counter-maneuver signals

        This test verifies that the ManeuverDialog correctly receives and processes
        counter-maneuver request signals from the GameEngine.
        """
        print("\n🧪 E2E Test: ManeuverDialog Counter-Maneuver Signal Flow")
        print("=" * 50)

        # Step 1: Set up maneuver scenario
        print("Step 1: Setting up contested maneuver")
        self._choose_army_by_id("player_1_campaign")

        # Get the current acting army
        acting_army = self.engine.get_current_acting_army()
        assert acting_army is not None

        # Get all players data and terrain data
        all_players_data = self.engine.get_all_players_data()
        terrain_data = self.engine.get_all_terrain_data()

        # Step 2: Create ManeuverDialog (this should trigger the maneuver process)
        print("Step 2: Creating ManeuverDialog")

        # Mock the dialog exec to avoid hanging
        with patch(
            "views.maneuver_dialog.CounterManeuverDecisionDialog.exec"
        ) as mock_exec:
            # Set up the mock to return accepted
            mock_exec.return_value = 1  # QDialog.Accepted

            # Track dialog creation
            dialogs_created = []
            original_init = ManeuverDialog.__init__

            def track_dialog_init(self, *args, **kwargs):
                dialogs_created.append(self)
                return original_init(self, *args, **kwargs)

            with patch.object(ManeuverDialog, "__init__", track_dialog_init):
                ManeuverDialog(
                    "Player 1",
                    acting_army,
                    all_players_data,
                    terrain_data,
                    self.engine,
                    None,
                )

        # Step 3: Verify signal flow
        print("Step 3: Verifying signal was emitted")
        assert len(self.signals_received) > 0
        assert any("counter_maneuver_requested" in signal for signal in self.signals_received)

        print(f"✅ Signals received: {self.signals_received}")

        # Step 4: Verify opposing armies were detected
        print("Step 4: Verifying opposing armies detection")
        counter_signal = [
            s for s in self.signals_received if "counter_maneuver_requested" in s
        ][0]
        assert "armies: 1" in counter_signal  # Should find Player 2's horde army

        print("✅ Test completed - ManeuverDialog signal flow working")

    def test_e2e_maneuver_dialog_handles_no_opposition(self):
        """
        E2E Test: ManeuverDialog handles scenarios with no opposing armies

        This test verifies automatic maneuver success when no opposition exists.
        """
        print("\n🧪 E2E Test: ManeuverDialog No Opposition Scenario")
        print("=" * 50)

        # Create scenario with no opposition
        isolated_setup = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",
                        "units": [
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_1",
                                "unit_type": "amazon_soldier",
                            },
                        ],
                        "unique_id": "player_1_home",
                    },
                },
            },
        ]

        isolated_engine = GameEngine(
            isolated_setup,
            "Player 1",
            "Coastland",  # Different frontier
            [("Player 1", 3)],
        )

        # Track signals for isolated engine
        isolated_signals = []
        isolated_engine.counter_maneuver_requested.connect(
            lambda location, armies: isolated_signals.append(
                f"counter_maneuver_requested: {location}"
            )
        )
        isolated_engine.terrain_direction_choice_requested.connect(
            lambda location, face: isolated_signals.append(
                f"terrain_direction_requested: {location}"
            )
        )

        # Choose army and test
        all_players_data = isolated_engine.get_all_players_data()
        for _player_name, player_data in all_players_data.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("unique_id") == "player_1_home":
                    army_choice_data = {
                        "name": army_data.get("name"),
                        "army_type": army_type,
                        "location": army_data.get("location"),
                        "units": army_data.get("units", []),
                        "unique_id": army_data.get("unique_id"),
                    }
                    isolated_engine.choose_acting_army(army_choice_data)
                    break

        acting_army = isolated_engine.get_current_acting_army()
        terrain_data = isolated_engine.get_all_terrain_data()

        # Create ManeuverDialog for isolated scenario
        print("Step 1: Creating ManeuverDialog for isolated scenario")
        with patch(
            "views.maneuver_dialog.TerrainDirectionDialog.exec"
        ) as mock_terrain_exec:
            mock_terrain_exec.return_value = 1  # QDialog.Accepted

            ManeuverDialog(
                "Player 1",
                acting_army,
                all_players_data,
                terrain_data,
                isolated_engine,
                None,
            )

        # Should NOT have counter-maneuver request (no opposition)
        counter_signals = [
            s for s in isolated_signals if "counter_maneuver_requested" in s
        ]
        assert len(counter_signals) == 0

        # Should have terrain direction request (automatic success)
        terrain_signals = [
            s for s in isolated_signals if "terrain_direction_requested" in s
        ]
        assert len(terrain_signals) == 1

        print("✅ Test completed - no opposition scenario handled correctly")

    def tearDown(self):
        """Clean up after each test."""
        self.signals_received.clear()
        self.engine_calls.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
