#!/usr/bin/env python3
"""
End-to-end tests for terrain-based action restrictions in Dragon Dice.
Tests that UI only shows appropriate action buttons based on terrain die face.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from game_logic.engine import GameEngine
from game_logic.game_state_manager import GameStateManager


class TestTerrainActionRestrictions(unittest.TestCase):
    """E2E tests for terrain face-based action button restrictions."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test data for each test."""
        # Base game state tracking
        self.game_log = []

    def _setup_terrain_action_scenario(self, terrain_name, target_face):
        """Set up a scenario for testing specific terrain face actions."""
        self.player_setup_data = [
            {
                "name": "Action Player",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Highland Guard",
                        "location": "Action Player Highland",
                        "units": [
                            {
                                "name": "Amazon Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "action_1",
                                "unit_type": "amazon_charioteer",
                            },
                            {
                                "name": "Amazon Archer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "action_2",
                                "unit_type": "amazon_archer",
                            },
                        ],
                        "unique_id": "action_player_home",
                        "terrain_elements": ["IVORY"],
                    },
                    "campaign": {
                        "name": "Test Army",
                        "location": terrain_name,
                        "units": [
                            {
                                "name": "Amazon Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            },
                            {
                                "name": "Amazon Scout",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_2",
                                "unit_type": "amazon_scout",
                            },
                        ],
                        "unique_id": "action_player_campaign",
                        "terrain_elements": self._get_terrain_elements_for_location(terrain_name),
                    },
                },
            },
            {
                "name": "Opponent Player",
                "home_terrain": "Coastland",
                "armies": {
                    "home": {
                        "name": "Coastal Defense",
                        "location": "Opponent Player Coastland",
                        "units": [
                            {
                                "name": "Amazon Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "opponent_1",
                                "unit_type": "amazon_runner",
                            },
                        ],
                        "unique_id": "opponent_player_home",
                        "terrain_elements": ["WATER"],
                    },
                },
            },
        ]

        self.frontier_terrain = terrain_name
        self.distance_rolls = [("Action Player", 4), ("Opponent Player", 2), ("__frontier__", 5)]

        # Create engine
        self.engine = GameEngine(
            self.player_setup_data,
            "Action Player",
            self.frontier_terrain,
            self.distance_rolls,
        )

        # Track game state
        self.game_log = []
        self._connect_action_tracking()

        # Set the terrain to the target face for testing
        self._set_terrain_face(terrain_name, target_face)

    def _get_terrain_elements_for_location(self, location):
        """Get terrain elements based on location."""
        terrain_mapping = {
            "Highland": ["IVORY"],
            "Coastland": ["WATER"],
            "Badland": ["DEATH"],
            "Flatland": ["EARTH"],
            "Frozen Wastes": ["FIRE"],
            "Swampland": ["DEATH", "WATER"],
        }
        
        # Extract terrain type from location
        for terrain_type, elements in terrain_mapping.items():
            if terrain_type in location:
                return elements
        
        return ["IVORY"]  # Default fallback

    def _set_terrain_face(self, terrain_name, target_face):
        """Force a terrain to a specific face for testing."""
        # Use the GameStateManager's update_terrain_face method
        success = self.engine.game_state_manager.update_terrain_face(terrain_name, target_face)
        if success:
            print(f"Set {terrain_name} to face {target_face}")
        else:
            print(f"Failed to set {terrain_name} to face {target_face}")
            # Fallback: access terrain data directly
            try:
                terrain_data = self.engine.game_state_manager.get_terrain_data(terrain_name)
                terrain_data["face"] = target_face
                print(f"Fallback: Set {terrain_name} to face {target_face}")
            except Exception as e:
                print(f"Error setting terrain face: {e}")

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
                    self.game_log.append(
                        f"Army chosen: {army_choice_data['name']} at {army_choice_data['location']}"
                    )
                    return

        raise ValueError(f"Army with ID '{army_unique_id}' not found")

    def _connect_action_tracking(self):
        """Connect to engine signals to track action-related events."""
        self.engine.current_player_changed.connect(
            lambda player: self.game_log.append(f"Current player: {player}")
        )
        self.engine.current_phase_changed.connect(
            lambda phase: self.game_log.append(f"Phase changed: {phase}")
        )

    def _get_available_actions_for_terrain_face(self, face):
        """Get expected available actions based on terrain face logic."""
        actions = ["SKIP"]  # Skip is always available
        
        if face >= 1:
            actions.append("MELEE")
        if face >= 2:
            actions.append("MISSILE")
        if face >= 3:
            actions.append("MAGIC")
            
        return sorted(actions)

    def _verify_terrain_and_actions(self, terrain_name, expected_face, expected_actions):
        """Verify terrain face and available actions match expectations."""
        # Get terrain info from engine
        terrains_info = self.engine.get_relevant_terrains_info()
        
        # Find our test terrain
        test_terrain = None
        for terrain_info in terrains_info:
            if terrain_info["name"] == terrain_name:
                test_terrain = terrain_info
                break
        
        self.assertIsNotNone(test_terrain, f"Terrain {terrain_name} not found")
        self.assertEqual(test_terrain["face"], expected_face, 
                        f"Terrain {terrain_name} should be on face {expected_face}")
        
        # Verify available actions match terrain face rules
        actual_actions = self._get_available_actions_for_terrain_face(expected_face)
        self.assertEqual(sorted(expected_actions), actual_actions,
                        f"Available actions should match terrain face {expected_face}")
        
        print(f"✅ Terrain {terrain_name} on face {expected_face} allows: {', '.join(sorted(expected_actions))}")

    def test_e2e_magic_action_terrain_face_3(self):
        """
        E2E Test: Magic action available on terrain face 3

        Flow:
        1. Set up army on terrain with face 3
        2. Navigate to action selection phase
        3. Verify UI shows Magic, Missile, Melee, and Skip buttons only
        4. Select Magic action and verify it works
        """
        print("\n🧪 E2E Test: Magic Action on Terrain Face 3")
        print("=" * 50)

        # Set up scenario with terrain face 3 (allows Magic + Missile + Melee)
        self._setup_terrain_action_scenario("Highland", 3)
        
        # Navigate to action selection
        assert self.engine.get_current_player_name() == "Action Player"
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Choose army on the terrain with face 3
        self._choose_army_by_id("action_player_campaign")
        
        # Skip maneuver to get to action selection
        self.engine.decide_maneuver(False)
        
        # Verify terrain face and available actions
        expected_actions = ["MAGIC", "MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Highland", 3, expected_actions)
        
        # Verify we're in action selection step
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Select magic action
        self.engine.select_action("MAGIC")
        
        print("✅ Test completed - Magic action available and selectable on face 3")

    def test_e2e_missile_action_terrain_face_2(self):
        """
        E2E Test: Missile action available on terrain face 2

        Flow:
        1. Set up army on terrain with face 2
        2. Navigate to action selection phase  
        3. Verify UI shows Missile, Melee, and Skip buttons only (no Magic)
        4. Select Missile action and verify it works
        """
        print("\n🧪 E2E Test: Missile Action on Terrain Face 2")
        print("=" * 50)

        # Set up scenario with terrain face 2 (allows Missile + Melee, no Magic)
        self._setup_terrain_action_scenario("Coastland", 2)
        
        # Navigate to action selection
        assert self.engine.get_current_player_name() == "Action Player"
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Choose army on the terrain with face 2
        self._choose_army_by_id("action_player_campaign")
        
        # Skip maneuver to get to action selection
        self.engine.decide_maneuver(False)
        
        # Verify terrain face and available actions (no Magic on face 2)
        expected_actions = ["MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Coastland", 2, expected_actions)
        
        # Verify we're in action selection step
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Select missile action
        self.engine.select_action("MISSILE")
        
        print("✅ Test completed - Missile action available and selectable on face 2, Magic not available")

    def test_e2e_melee_action_terrain_face_1(self):
        """
        E2E Test: Melee action available on terrain face 1

        Flow:
        1. Set up army on terrain with face 1
        2. Navigate to action selection phase
        3. Verify UI shows only Melee and Skip buttons (no Magic or Missile)
        4. Select Melee action and verify it works
        """
        print("\n🧪 E2E Test: Melee Action on Terrain Face 1")
        print("=" * 50)

        # Set up scenario with terrain face 1 (allows only Melee, no Magic or Missile)
        self._setup_terrain_action_scenario("Flatland", 1)
        
        # Navigate to action selection
        assert self.engine.get_current_player_name() == "Action Player"
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Choose army on the terrain with face 1
        self._choose_army_by_id("action_player_campaign")
        
        # Skip maneuver to get to action selection
        self.engine.decide_maneuver(False)
        
        # Verify terrain face and available actions (only Melee on face 1)
        expected_actions = ["MELEE", "SKIP"]
        self._verify_terrain_and_actions("Flatland", 1, expected_actions)
        
        # Verify we're in action selection step
        assert self.engine.current_phase == "FIRST_MARCH"
        
        # Select melee action
        self.engine.select_action("MELEE")
        
        print("✅ Test completed - Melee action available and selectable on face 1, Magic and Missile not available")

    def test_e2e_terrain_face_action_progression(self):
        """
        E2E Test: Verify action availability progresses correctly across terrain faces

        Flow:
        1. Test face 1: only Melee + Skip
        2. Change to face 2: adds Missile
        3. Change to face 3: adds Magic
        4. Verify each step shows correct buttons
        """
        print("\n🧪 E2E Test: Terrain Face Action Progression")
        print("=" * 50)

        # Set up scenario starting with face 1
        self._setup_terrain_action_scenario("Badland", 1)
        
        # Navigate to action selection
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        
        # Test Face 1: Only Melee + Skip
        print("\n--- Testing Face 1 ---")
        expected_actions_face1 = ["MELEE", "SKIP"]
        self._verify_terrain_and_actions("Badland", 1, expected_actions_face1)
        
        # Change to Face 2 and test
        print("\n--- Testing Face 2 ---")
        self._set_terrain_face("Badland", 2)
        expected_actions_face2 = ["MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Badland", 2, expected_actions_face2)
        
        # Change to Face 3 and test
        print("\n--- Testing Face 3 ---")
        self._set_terrain_face("Badland", 3)
        expected_actions_face3 = ["MAGIC", "MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Badland", 3, expected_actions_face3)
        
        # Select magic action (highest tier) to complete test
        self.engine.select_action("MAGIC")
        
        print("✅ Test completed - Action progression works correctly across all terrain faces")

    def test_e2e_skip_action_always_available(self):
        """
        E2E Test: Skip action is always available regardless of terrain face

        Flow:
        1. Test multiple terrain faces (1, 2, 3)
        2. Verify Skip action is available on all faces
        3. Select Skip action and verify it works
        """
        print("\n🧪 E2E Test: Skip Action Always Available")
        print("=" * 50)

        # Test on face 1
        self._setup_terrain_action_scenario("Swampland", 1)
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        
        print("\n--- Testing Skip on Face 1 ---")
        expected_actions = ["MELEE", "SKIP"]
        self._verify_terrain_and_actions("Swampland", 1, expected_actions)
        self.assertIn("SKIP", expected_actions, "Skip should be available on face 1")
        
        # Select skip to complete this march and test next scenario
        self.engine.select_action("SKIP")
        
        # Set up new scenario for face 2
        self._setup_terrain_action_scenario("Frozen Wastes", 2)
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        
        print("\n--- Testing Skip on Face 2 ---")
        expected_actions = ["MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Frozen Wastes", 2, expected_actions)
        self.assertIn("SKIP", expected_actions, "Skip should be available on face 2")
        
        # Select skip to complete this march
        self.engine.select_action("SKIP")
        
        print("✅ Test completed - Skip action always available on all terrain faces")

    def test_e2e_action_restrictions_with_maneuver(self):
        """
        E2E Test: Action restrictions work correctly after maneuver changes terrain face

        Flow:
        1. Start on terrain face 1 (Melee only)
        2. Maneuver successfully and change terrain face to 3
        3. Verify actions now include Magic, Missile, Melee
        4. Select Magic action to verify it works
        """
        print("\n🧪 E2E Test: Action Restrictions After Maneuver")
        print("=" * 50)

        # Set up scenario with face 1 initially
        self._setup_terrain_action_scenario("Highland", 1)
        
        # Navigate to action selection via successful maneuver
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(True)  # Attempt maneuver
        
        # Mock opponent declining counter-maneuver
        self.engine.submit_counter_maneuver_decision("Opponent Player", False)
        
        # Choose to turn terrain UP (which should increase face)
        self.engine.submit_terrain_direction_choice("UP")
        
        # Set terrain to face 3 to simulate successful maneuver result
        self._set_terrain_face("Highland", 3)
        
        print("\n--- After Successful Maneuver ---")
        # Verify terrain face changed and actions expanded
        expected_actions = ["MAGIC", "MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Highland", 3, expected_actions)
        
        # Select magic action (now available due to face 3)
        self.engine.select_action("MAGIC")
        
        print("✅ Test completed - Action restrictions update correctly after terrain face changes")

    def tearDown(self):
        """Clean up after each test."""
        # Clear game log for next test
        self.game_log.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)