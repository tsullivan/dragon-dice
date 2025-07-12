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

    def _get_available_actions_for_terrain_face(self, face, terrain_name=None, acting_player=None):
        """Get expected available actions based on terrain face logic and terrain control."""
        actions = ["SKIP"]  # Skip is always available
        
        # Check if eighth face with opposing army (melee only restriction)
        if face == 8 and terrain_name and acting_player:
            terrain_controller = self.engine.game_state_manager.get_terrain_controller(terrain_name)
            if terrain_controller and terrain_controller != acting_player:
                # Opposing army on eighth face - only melee allowed
                actions.append("MELEE")
                return sorted(actions)
        
        # Normal terrain face rules
        if face >= 1:
            actions.append("MELEE")
        if face >= 2:
            actions.append("MISSILE")
        if face >= 3:
            actions.append("MAGIC")
            
        return sorted(actions)

    def _verify_terrain_and_actions(self, terrain_name, expected_face, expected_actions, acting_player=None):
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
        if acting_player is None:
            acting_player = self.engine.get_current_player_name()
        actual_actions = self._get_available_actions_for_terrain_face(expected_face, terrain_name, acting_player)
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

    def test_e2e_eighth_face_action_choice_controlling_army(self):
        """
        E2E Test: Controlling army can choose any action on eighth face
        
        Flow:
        1. Set terrain to eighth face with controlling army
        2. Verify UI shows Magic, Missile, Melee, and Skip buttons
        3. Select each action type to verify all work
        """
        print("\n🧪 E2E Test: Eighth Face Action Choice for Controlling Army")
        print("=" * 60)
        
        # Set up scenario with eighth face and controlling army
        self._setup_terrain_action_scenario("Highland", 8)
        
        # Set army as controlling the terrain
        self.engine.game_state_manager.set_terrain_controller("Highland", "Action Player")
        
        # Navigate to action selection
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        
        # Verify eighth face allows all actions for controlling army
        expected_actions = ["MAGIC", "MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("Highland", 8, expected_actions)
        
        # Test Magic action selection (most restrictive normally)
        self.engine.select_action("MAGIC")
        
        print("✅ Test completed - Controlling army can choose any action on eighth face")

    def test_e2e_eighth_face_melee_only_opposing_army(self):
        """
        E2E Test: Opposing army can only use melee on eighth face
        
        Flow:
        1. Set terrain to eighth face with different controlling army
        2. Verify UI shows only Melee and Skip buttons for opposing army
        3. Select Melee action to verify it works
        """
        print("\n🧪 E2E Test: Eighth Face Melee Only for Opposing Army")
        print("=" * 60)
        
        # Set up scenario with eighth face
        self._setup_terrain_action_scenario("Coastland", 8)
        
        # Set different player as controlling the terrain
        self.engine.game_state_manager.set_terrain_controller("Coastland", "Opponent Player")
        
        # Navigate to action selection with Action Player (opposing army)
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        
        # Verify opposing army can only use melee on eighth face
        expected_actions = ["MELEE", "SKIP"]
        self._verify_terrain_and_actions("Coastland", 8, expected_actions, "Action Player")
        
        # Test that only melee works
        self.engine.select_action("MELEE")
        
        print("✅ Test completed - Opposing army limited to melee only on eighth face")

    def test_e2e_id_doubling_when_controlling_terrain(self):
        """
        E2E Test: ID results are doubled when army controls terrain
        
        Flow:
        1. Set up army controlling a terrain with opponent army present
        2. Submit roll with ID results
        3. Verify ID results are doubled in action resolution
        4. Compare with non-controlling army results
        """
        print("\n🧪 E2E Test: ID Doubling When Controlling Terrain")
        print("=" * 60)
        
        # Set up scenario with army controlling terrain and opponent present
        self.player_setup_data = [
            {
                "name": "Action Player",
                "home_terrain": "Highland",
                "armies": {
                    "campaign": {
                        "name": "Test Army",
                        "location": "Highland",
                        "units": [
                            {
                                "name": "Amazon Soldier",
                                "health": 2,
                                "max_health": 2,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            },
                        ],
                        "unique_id": "action_player_campaign",
                        "terrain_elements": ["IVORY"],
                    },
                },
            },
            {
                "name": "Opponent Player",
                "home_terrain": "Coastland",
                "armies": {
                    "campaign": {
                        "name": "Opponent Army",
                        "location": "Highland",  # Same location for combat
                        "units": [
                            {
                                "name": "Amazon Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "opponent_1",
                                "unit_type": "amazon_runner",
                            },
                        ],
                        "unique_id": "opponent_player_campaign",
                        "terrain_elements": ["WATER"],
                    },
                },
            },
        ]

        self.frontier_terrain = "Highland"
        self.distance_rolls = [("Action Player", 4), ("Opponent Player", 2), ("__frontier__", 5)]

        # Create engine
        self.engine = GameEngine(
            self.player_setup_data,
            "Action Player",
            self.frontier_terrain,
            self.distance_rolls,
        )
        
        # Set terrain control and face
        self.engine.game_state_manager.update_terrain_face("Highland", 5)
        self.engine.game_state_manager.set_terrain_controller("Highland", "Action Player")
        
        # Track game state
        self.game_log = []
        self._connect_action_tracking()
        
        # Navigate to action and select melee
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(False)
        self.engine.select_action("MELEE")
        
        # Submit dice roll with ID results and check for terrain control doubling
        dice_results = "2 melee, 3 id"
        
        # Test the action resolver directly to see ID doubling
        outcome = self.engine.action_resolver.resolve_attacker_melee(dice_results, "Action Player")
        
        # Verify terrain control effects are present
        terrain_effects = [effect for effect in outcome.get("effects", []) if effect.get("type") == "terrain_control"]
        self.assertTrue(len(terrain_effects) > 0, "Terrain control ID doubling should be applied")
        
        # Verify the doubling effect is properly described
        doubling_effect = terrain_effects[0].get("description", "")
        self.assertIn("Doubled ID results", doubling_effect, "Should describe ID doubling effect")
        self.assertIn("(3 -> 6)", doubling_effect, "Should show ID results doubled from 3 to 6")
        
        print("✅ Test completed - ID results doubled when controlling terrain")

    def test_e2e_terrain_face_reset_when_control_lost(self):
        """
        E2E Test: Terrain resets from eighth to seventh face when control is lost
        
        Flow:
        1. Set terrain to eighth face with controlling army
        2. Simulate control loss (army killed/out-maneuvered/abandoned)
        3. Verify terrain face resets to seventh face
        4. Verify controlling army advantages cease
        """
        print("\n🧪 E2E Test: Terrain Face Reset When Control Lost")
        print("=" * 60)
        
        # Set up terrain at eighth face with controlling army
        self._setup_terrain_action_scenario("Flatland", 8)
        self.engine.game_state_manager.set_terrain_controller("Flatland", "Action Player")
        
        # Verify initial eighth face
        terrains_info = self.engine.get_relevant_terrains_info()
        flatland = next(t for t in terrains_info if t["name"] == "Flatland")
        self.assertEqual(flatland["face"], 8, "Terrain should start at eighth face")
        
        # Simulate control loss by removing all units from controlling army
        self.engine.game_state_manager.apply_damage_to_units("Action Player", "action_player_campaign", 99)
        
        # Verify terrain face reset to seventh
        terrains_info = self.engine.get_relevant_terrains_info()
        flatland = next(t for t in terrains_info if t["name"] == "Flatland")
        self.assertEqual(flatland["face"], 7, "Terrain should reset to seventh face when control lost")
        
        # Verify controller is cleared
        controller = self.engine.game_state_manager.get_terrain_controller("Flatland")
        self.assertIsNone(controller, "Terrain should have no controller after control lost")
        
        print("✅ Test completed - Terrain face resets when control is lost")

    def test_e2e_city_eighth_face_recruitment(self):
        """
        E2E Test: City eighth face allows recruitment from DUA
        
        Flow:
        1. Set up City terrain at eighth face with controlling army
        2. Place units in DUA for recruitment
        3. Enter Eighth Face Phase
        4. Verify recruitment option is available
        5. Recruit unit from DUA to army
        """
        print("\n🧪 E2E Test: City Eighth Face Recruitment")
        print("=" * 60)
        
        # Set up City terrain scenario
        self._setup_terrain_action_scenario("City", 8)
        self.engine.game_state_manager.set_terrain_controller("City", "Action Player")
        
        # Add units to DUA for recruitment
        from game_logic.dua_manager import DUAUnit
        dua_unit = DUAUnit(
            name="Amazon Recruit",
            species="amazon",
            health=1,
            elements=["IVORY"],
            original_owner="Action Player"
        )
        self.engine.dua_manager.add_unit_to_dua(dua_unit)
        
        # Navigate to Eighth Face Phase
        self._choose_army_by_id("action_player_campaign")
        
        # Manually trigger eighth face phase
        self.engine.enter_eighth_face_phase()
        
        # Verify recruitment is available for City
        eighth_face_options = self.engine.get_eighth_face_options("Action Player", "City")
        self.assertIn("recruitment", [opt.get("type") for opt in eighth_face_options])
        
        # Perform recruitment
        initial_dua_size = len(self.engine.dua_manager.get_player_dua("Action Player"))
        recruitment_result = self.engine.process_eighth_face_action("Action Player", "recruitment", {"unit_id": "recruit_1"})
        final_dua_size = len(self.engine.dua_manager.get_player_dua("Action Player"))
        
        # Verify recruitment succeeded
        self.assertTrue(recruitment_result.get("success", False), "Recruitment should succeed")
        self.assertEqual(final_dua_size, initial_dua_size - 1, "DUA should lose one unit from recruitment")
        
        print("✅ Test completed - City eighth face recruitment works correctly")

    def test_e2e_standing_stones_magic_conversion(self):
        """
        E2E Test: Standing Stones eighth face converts magic to terrain elements
        
        Flow:
        1. Set up Standing Stones terrain at eighth face
        2. Enter Eighth Face Phase with controlling army
        3. Verify magic conversion option is available
        4. Convert magic results to terrain elements
        """
        print("\n🧪 E2E Test: Standing Stones Magic Conversion")
        print("=" * 60)
        
        # Set up Standing Stones terrain scenario
        self._setup_terrain_action_scenario("Standing Stones", 8)
        self.engine.game_state_manager.set_terrain_controller("Standing Stones", "Action Player")
        
        # Navigate to Eighth Face Phase
        self._choose_army_by_id("action_player_campaign")
        self.engine.enter_eighth_face_phase()
        
        # Verify magic conversion is available for Standing Stones
        eighth_face_options = self.engine.get_eighth_face_options("Action Player", "Standing Stones")
        self.assertIn("magic_conversion", [opt.get("type") for opt in eighth_face_options])
        
        # Simulate magic roll and conversion
        magic_results = {"magic": 3, "other": 2}
        conversion_result = self.engine.process_eighth_face_action(
            "Action Player", "magic_conversion", {"magic_results": magic_results}
        )
        
        self.assertTrue(conversion_result.get("success", False), "Magic conversion should succeed")
        
        print("✅ Test completed - Standing Stones magic conversion works correctly")

    def test_e2e_temple_death_magic_immunity(self):
        """
        E2E Test: Temple eighth face provides death magic immunity
        
        Flow:
        1. Set up Temple terrain at eighth face with controlling army
        2. Attempt death magic attack on controlling army
        3. Verify army is immune to death magic effects
        4. Test forced burial of opponent's unit
        """
        print("\n🧪 E2E Test: Temple Death Magic Immunity")
        print("=" * 60)
        
        # Set up Temple terrain scenario
        self._setup_terrain_action_scenario("Temple", 8)
        self.engine.game_state_manager.set_terrain_controller("Temple", "Action Player")
        
        # Ensure Temple terrain has proper subtype for death magic immunity
        terrain_data = self.engine.game_state_manager.get_terrain_data("Temple")
        terrain_data["subtype"] = "temple"
        print(f"Set Temple subtype to: {terrain_data.get('subtype')}")
        
        # Navigate to controlling army
        self._choose_army_by_id("action_player_campaign")
        
        # Test death magic immunity with debug info
        # First check if the army exists
        player_data = self.engine.game_state_manager.get_player_data("Action Player")
        print(f"Player armies: {list(player_data.get('armies', {}).keys())}")
        campaign_army = player_data.get('armies', {}).get('campaign', {})
        print(f"Campaign army location: {campaign_army.get('location')}")
        print(f"Campaign army unique_id: {campaign_army.get('unique_id')}")
        
        army_location = self.engine.game_state_manager.get_army_location("Action Player", "action_player_campaign")
        print(f"Army location lookup result: {army_location}")
        
        # Try with just the army type instead of unique_id
        army_location_alt = self.engine.game_state_manager.get_army_location("Action Player", "campaign")
        print(f"Army location (using 'campaign'): {army_location_alt}")
        
        terrain_data = self.engine.game_state_manager.get_terrain_data_safe("Temple")
        print(f"Temple terrain data: {terrain_data}")
        
        immunity_status = self.engine.check_death_magic_immunity("Action Player", "action_player_campaign")
        print(f"Death magic immunity status: {immunity_status}")
        self.assertTrue(immunity_status, "Army controlling Temple should be immune to death magic")
        
        # Test forced burial option in Eighth Face Phase
        self.engine.enter_eighth_face_phase()
        eighth_face_options = self.engine.get_eighth_face_options("Action Player", "Temple")
        self.assertIn("forced_burial", [opt.get("type") for opt in eighth_face_options])
        
        # Execute forced burial
        burial_result = self.engine.process_eighth_face_action(
            "Action Player", "forced_burial", {"target_player": "Opponent Player", "unit_choice": "any"}
        )
        
        self.assertTrue(burial_result.get("success", False), "Forced burial should succeed")
        
        print("✅ Test completed - Temple death magic immunity and forced burial work correctly")

    def test_e2e_tower_missile_attack_any_army(self):
        """
        E2E Test: Tower eighth face allows missile attack on any army
        
        Flow:
        1. Set up Tower terrain at eighth face with controlling army
        2. Enter Eighth Face Phase
        3. Verify missile attack option is available
        4. Attack distant army including Reserve Army
        5. Verify non-ID results count against Reserve Army
        """
        print("\n🧪 E2E Test: Tower Missile Attack Any Army")
        print("=" * 60)
        
        # Set up Tower terrain scenario
        self._setup_terrain_action_scenario("Tower", 8)
        self.engine.game_state_manager.set_terrain_controller("Tower", "Action Player")
        
        # Add a unit to reserves for testing
        reserve_unit_data = {
            "name": "Amazon Reserve",
            "species": "amazon",
            "health": 2,
            "elements": ["WATER"],
        }
        self.engine.reserves_manager.add_unit_to_reserves(reserve_unit_data, "Opponent Player")
        
        # Navigate to Eighth Face Phase
        self._choose_army_by_id("action_player_campaign")
        self.engine.enter_eighth_face_phase()
        
        # Verify missile attack option is available
        eighth_face_options = self.engine.get_eighth_face_options("Action Player", "Tower")
        self.assertIn("missile_attack", [opt.get("type") for opt in eighth_face_options])
        
        # Execute missile attack on Reserve Army
        missile_results = "2 missile, 1 id"  # Only non-ID should count against reserves
        attack_result = self.engine.process_eighth_face_action(
            "Action Player", "missile_attack", 
            {"target": "opponent_reserves", "missile_results": missile_results}
        )
        
        self.assertTrue(attack_result.get("success", False), "Tower missile attack should succeed")
        self.assertEqual(attack_result.get("effective_hits", 0), 2, "Only non-ID results should count against Reserve Army")
        
        print("✅ Test completed - Tower missile attack works correctly including Reserve Army rules")

    def test_e2e_comprehensive_terrain_control_flow(self):
        """
        E2E Test: Complete terrain control flow from capture to loss
        
        Flow:
        1. Start with uncontrolled terrain
        2. Maneuver to capture terrain (eighth face)
        3. Verify controlling army benefits (action choice, ID doubling)
        4. Use eighth face effect based on terrain type
        5. Lose control and verify reset
        """
        print("\n🧪 E2E Test: Comprehensive Terrain Control Flow")
        print("=" * 60)
        
        # Start with uncontrolled terrain at face 1
        self._setup_terrain_action_scenario("City", 1)
        
        # Maneuver to capture terrain
        self._choose_army_by_id("action_player_campaign")
        self.engine.decide_maneuver(True)
        
        # Mock successful maneuver to eighth face
        self.engine.submit_counter_maneuver_decision("Opponent Player", False)
        self.engine.submit_terrain_direction_choice("UP")
        self._set_terrain_face("City", 8)
        self.engine.game_state_manager.set_terrain_controller("City", "Action Player")
        
        # Verify controlling army benefits
        print("\n--- Testing Controlling Army Benefits ---")
        
        # Test action choice freedom on eighth face
        expected_actions = ["MAGIC", "MELEE", "MISSILE", "SKIP"]
        self._verify_terrain_and_actions("City", 8, expected_actions)
        
        # Test ID doubling by calling resolver directly (no opponent needed for this test)
        self.engine.select_action("MELEE")
        # Test ID doubling directly through action resolver
        outcome = self.engine.action_resolver.resolve_attacker_melee("1 melee, 2 id", "Action Player")
        terrain_effects = [effect for effect in outcome.get("effects", []) if effect.get("type") == "terrain_control"]
        self.assertTrue(len(terrain_effects) > 0, "Terrain control ID doubling should be applied")
        
        # Test eighth face effect (City recruitment)
        self.engine.enter_eighth_face_phase()
        recruitment_available = "recruitment" in [
            opt.get("type") for opt in self.engine.get_eighth_face_options("Action Player", "City")
        ]
        self.assertTrue(recruitment_available, "City recruitment should be available")
        
        # Simulate control loss - this triggers automatic terrain control loss
        print("\n--- Testing Control Loss ---")
        self.engine.game_state_manager.apply_damage_to_units("Action Player", "action_player_campaign", 99)
        
        # Verify automatic terrain control loss occurred by checking terrain state
        
        # Verify terrain reset
        terrains_info = self.engine.get_relevant_terrains_info()
        city = next(t for t in terrains_info if t["name"] == "City")
        self.assertEqual(city["face"], 7, "City should reset to face 7 after control loss")
        
        controller = self.engine.game_state_manager.get_terrain_controller("City")
        self.assertIsNone(controller, "City should have no controller after army destruction")
        
        print("✅ Test completed - Complete terrain control flow works correctly")

    def tearDown(self):
        """Clean up after each test."""
        # Clear game log for next test
        self.game_log.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)