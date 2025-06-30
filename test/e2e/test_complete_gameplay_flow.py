#!/usr/bin/env python3
"""
Complete E2E tests for Dragon Dice application.
Tests the full user journey from startup through actual gameplay.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from main_window import MainWindow
from models.app_data_model import AppDataModel


class TestCompleteGameplayFlow:
    """End-to-end tests for complete Dragon Dice gameplay flow."""
    
    @pytest.fixture(autouse=True)
    def setup_application(self, qtbot):
        """Set up the application for testing."""
        self.qtbot = qtbot
        self.main_window = MainWindow()
        self.qtbot.addWidget(self.main_window)
        self.main_window.show()
        
        # Wait for the application to be ready
        self.qtbot.waitForWindowShown(self.main_window)
        QTest.qWait(500)  # Additional wait for initialization
        
        yield
        
        # Cleanup
        self.main_window.close()
    
    def test_complete_two_player_game_flow(self, qtbot):
        """Test a complete two-player game from start to action selection."""
        print("\n🎮 Starting Complete Two-Player Game Flow Test")
        print("=" * 60)
        
        # Phase 1: Welcome Screen
        print("📍 Phase 1: Welcome Screen Setup")
        self._test_welcome_screen_setup()
        
        # Phase 2: Player Setup 
        print("📍 Phase 2: Player Setup")
        self._test_player_setup_flow()
        
        # Phase 3: Frontier Selection
        print("📍 Phase 3: Frontier Selection")
        self._test_frontier_selection()
        
        # Phase 4: Distance Rolls
        print("📍 Phase 4: Distance Rolls")
        self._test_distance_rolls()
        
        # Phase 5: Main Gameplay - Action Selection
        print("📍 Phase 5: Main Gameplay - Action Selection")
        self._test_main_gameplay_action_selection()
        
        print("✅ Complete game flow test passed!")
    
    def _test_welcome_screen_setup(self):
        """Test the welcome screen configuration."""
        # Find and configure player count
        player_count_combo = self._find_widget(QComboBox, "player count")
        if player_count_combo:
            # Select 2 players
            player_count_combo.setCurrentText("2")
            QTest.qWait(100)
        
        # Find and configure force size
        force_size_combo = self._find_widget(QComboBox, "force size")
        if force_size_combo:
            # Select 24 points
            force_size_combo.setCurrentText("24")
            QTest.qWait(100)
        
        # Click proceed button
        proceed_button = self._find_button_with_text("Proceed to Player Setup")
        if proceed_button:
            print("✓ Clicking 'Proceed to Player Setup'")
            self.qtbot.mouseClick(proceed_button, Qt.LeftButton)
            QTest.qWait(1000)  # Wait for transition
        else:
            raise AssertionError("Could not find 'Proceed to Player Setup' button")
    
    def _test_player_setup_flow(self):
        """Test player setup for both players."""
        # Setup Player 1
        print("  Setting up Player 1...")
        self._setup_single_player("Player 1", "SWAMPLAND", "COASTLAND", "Red Dragon")
        
        # Click Next Player
        next_button = self._find_button_with_text("Next Player")
        if next_button:
            print("✓ Proceeding to Player 2")
            self.qtbot.mouseClick(next_button, Qt.LeftButton)
            QTest.qWait(1000)
        
        # Setup Player 2  
        print("  Setting up Player 2...")
        self._setup_single_player("Player 2", "HIGHLAND", "DEADLAND", "Black Dragon")
        
        # Click final setup button
        final_button = self._find_button_containing_text("Finalize Setup")
        if final_button:
            print("✓ Finalizing player setup")
            self.qtbot.mouseClick(final_button, Qt.LeftButton)
            QTest.qWait(1000)
    
    def _setup_single_player(self, player_name, home_terrain, frontier_proposal, dragon_type):
        """Set up a single player's configuration."""
        # Set player name
        name_input = self._find_widget(QLineEdit, "player name")
        if name_input:
            name_input.clear()
            name_input.setText(player_name)
            QTest.qWait(100)
        
        # Select home terrain
        home_terrain_combo = self._find_combo_with_option(home_terrain)
        if home_terrain_combo:
            home_terrain_combo.setCurrentText(home_terrain)
            QTest.qWait(100)
        
        # Select frontier proposal
        frontier_combo = self._find_combo_with_option(frontier_proposal)
        if frontier_combo and frontier_combo != home_terrain_combo:
            frontier_combo.setCurrentText(frontier_proposal)
            QTest.qWait(100)
        
        # Select dragon
        dragon_combo = self._find_combo_with_option(dragon_type)
        if dragon_combo:
            dragon_combo.setCurrentText(dragon_type)
            QTest.qWait(100)
        
        # Add some units to armies (simplified for testing)
        self._add_basic_army_units()
    
    def _add_basic_army_units(self):
        """Add basic units to armies to meet minimum requirements."""
        # Look for "Manage Units" buttons and add minimal units
        manage_buttons = self._find_all_buttons_with_text("Manage Units")
        
        for i, button in enumerate(manage_buttons[:3]):  # Home, Campaign, Horde
            print(f"  Adding units to army {i+1}")
            self.qtbot.mouseClick(button, Qt.LeftButton)
            QTest.qWait(500)
            
            # In unit selection dialog, add minimum units
            self._add_units_in_dialog()
            
            # Close dialog
            done_button = self._find_button_with_text("Done")
            if done_button:
                self.qtbot.mouseClick(done_button, Qt.LeftButton)
                QTest.qWait(300)
    
    def _add_units_in_dialog(self):
        """Add units in the unit selection dialog."""
        # Find unit selection buttons (simplified - add first available units)
        unit_buttons = self._find_all_buttons_containing_text("Add")
        
        # Add a few units to meet minimum requirements
        for i, button in enumerate(unit_buttons[:3]):  # Add first 3 available units
            if button.isEnabled():
                self.qtbot.mouseClick(button, Qt.LeftButton)
                QTest.qWait(200)
    
    def _test_frontier_selection(self):
        """Test frontier selection phase."""
        print("  Selecting frontier terrain...")
        
        # Find terrain option buttons
        terrain_buttons = self._find_all_buttons_containing_text("Select")
        
        if terrain_buttons:
            # Select first available terrain
            self.qtbot.mouseClick(terrain_buttons[0], Qt.LeftButton)
            QTest.qWait(500)
        
        # Submit frontier selection
        submit_button = self._find_button_with_text("Submit")
        if submit_button:
            print("✓ Submitting frontier selection")
            self.qtbot.mouseClick(submit_button, Qt.LeftButton)
            QTest.qWait(1000)
    
    def _test_distance_rolls(self):
        """Test distance rolls phase."""
        print("  Rolling distance dice...")
        
        # Find roll buttons and click them
        roll_buttons = self._find_all_buttons_with_text("Roll")
        
        for button in roll_buttons:
            self.qtbot.mouseClick(button, Qt.LeftButton)
            QTest.qWait(300)
        
        # Submit distance rolls
        submit_button = self._find_button_with_text("Submit Distance Rolls")
        if submit_button:
            print("✓ Submitting distance rolls")
            self.qtbot.mouseClick(submit_button, Qt.LeftButton)
            QTest.qWait(2000)  # Wait for game engine initialization
    
    def _test_main_gameplay_action_selection(self):
        """Test the main gameplay action selection - the problematic area."""
        print("  Testing main gameplay action selection...")
        
        # Wait for game to initialize
        QTest.qWait(2000)
        
        # This is where the original bug occurred - test action button responsiveness
        action_buttons = self._find_action_buttons()
        
        if not action_buttons:
            raise AssertionError("No action buttons found in main gameplay")
        
        print(f"  Found {len(action_buttons)} action buttons")
        
        # Test each action button for responsiveness
        for i, button in enumerate(action_buttons):
            button_text = button.text()
            print(f"  Testing button: {button_text}")
            
            # Verify button is enabled and visible
            assert button.isEnabled(), f"Button '{button_text}' is not enabled"
            assert button.isVisible(), f"Button '{button_text}' is not visible"
            
            # Test that clicking doesn't cause infinite loop
            if "Skip" in button_text:  # Test the Skip Action button specifically
                print(f"  Clicking {button_text} button...")
                self.qtbot.mouseClick(button, Qt.LeftButton)
                QTest.qWait(500)
                
                # Verify the application is still responsive
                assert self.main_window.isVisible(), "Main window became unresponsive"
                break  # Only test one action to avoid changing game state too much
        
        print("✓ Action buttons are responsive!")
    
    def _find_action_buttons(self):
        """Find the main gameplay action buttons (Melee, Missile, Magic, Skip)."""
        action_button_texts = ["Melee", "Missile", "Magic", "Skip Action"]
        buttons = []
        
        for text in action_button_texts:
            button = self._find_button_containing_text(text)
            if button:
                buttons.append(button)
        
        return buttons
    
    # Helper methods for finding UI elements
    def _find_widget(self, widget_type, description=""):
        """Find a widget of specific type."""
        widgets = self.main_window.findChildren(widget_type)
        if widgets:
            return widgets[0]  # Return first match
        return None
    
    def _find_button_with_text(self, text):
        """Find a button with specific text."""
        buttons = self.main_window.findChildren(QPushButton)
        for button in buttons:
            if button.text() == text:
                return button
        return None
    
    def _find_button_containing_text(self, text):
        """Find a button containing specific text."""
        buttons = self.main_window.findChildren(QPushButton)
        for button in buttons:
            if text.lower() in button.text().lower():
                return button
        return None
    
    def _find_all_buttons_with_text(self, text):
        """Find all buttons with specific text."""
        buttons = self.main_window.findChildren(QPushButton)
        return [btn for btn in buttons if text in btn.text()]
    
    def _find_all_buttons_containing_text(self, text):
        """Find all buttons containing specific text."""
        buttons = self.main_window.findChildren(QPushButton)
        return [btn for btn in buttons if text.lower() in btn.text().lower()]
    
    def _find_combo_with_option(self, option_text):
        """Find a combo box that contains a specific option."""
        combos = self.main_window.findChildren(QComboBox)
        for combo in combos:
            for i in range(combo.count()):
                if option_text in combo.itemText(i):
                    return combo
        return None


class TestGameplayInteractions:
    """Test specific gameplay interactions and scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup_game_state(self, qtbot):
        """Set up a game in progress for interaction testing."""
        self.qtbot = qtbot
        
        # Create a game engine with initialized state
        from game_logic.engine import GameEngine
        self.game_engine = GameEngine()
        
        # Mock initialized game state
        sample_players = [
            {
                "name": "Test Player 1",
                "home_terrain": "SWAMPLAND",
                "armies": {
                    "home": {"name": "HOME", "units": [{"name": "Soldier", "max_health": 1}]},
                    "campaign": {"name": "CAMPAIGN", "units": [{"name": "Warrior", "max_health": 2}]},
                    "horde": {"name": "HORDE", "units": [{"name": "Runner", "max_health": 1}]}
                }
            },
            {
                "name": "Test Player 2", 
                "home_terrain": "HIGHLAND",
                "armies": {
                    "home": {"name": "HOME", "units": [{"name": "Fighter", "max_health": 1}]},
                    "campaign": {"name": "CAMPAIGN", "units": [{"name": "Guard", "max_health": 2}]},
                    "horde": {"name": "HORDE", "units": [{"name": "Scout", "max_health": 1}]}
                }
            }
        ]
        
        distance_rolls = [("Test Player 1", 3), ("__frontier__", 4), ("Test Player 2", 5)]
        self.game_engine.initialize_game(sample_players, "COASTLAND", "Test Player 1", distance_rolls)
        
        # Create main gameplay view
        from views.main_gameplay_view import MainGameplayView
        self.gameplay_view = MainGameplayView(self.game_engine)
        self.qtbot.addWidget(self.gameplay_view)
        self.gameplay_view.show()
        self.qtbot.waitForWindowShown(self.gameplay_view)
        
        yield
        
        self.gameplay_view.close()
    
    def test_action_button_responsiveness(self, qtbot):
        """Test that action buttons respond correctly without infinite loops."""
        print("\n🎯 Testing Action Button Responsiveness")
        
        # Simulate reaching the action selection phase
        self._simulate_reach_action_phase()
        
        # Test each action button
        action_tests = [
            ("Skip Action", self._test_skip_action),
            ("Melee", self._test_melee_action),
            ("Missile", self._test_missile_action),
            ("Magic", self._test_magic_action)
        ]
        
        for action_name, test_func in action_tests:
            print(f"  Testing {action_name} button...")
            try:
                test_func()
                print(f"  ✓ {action_name} button works correctly")
            except Exception as e:
                print(f"  ❌ {action_name} button failed: {e}")
                raise
    
    def test_infinite_loop_prevention(self, qtbot):
        """Test that the infinite loop issue is resolved."""
        print("\n🔄 Testing Infinite Loop Prevention")
        
        # Monitor for rapid repeated actions that would indicate a loop
        action_count = 0
        start_time = time.time()
        
        def count_actions():
            nonlocal action_count
            action_count += 1
        
        # Connect to action signals to monitor
        if hasattr(self.gameplay_view, 'action_decision_widget'):
            self.gameplay_view.action_decision_widget.action_decision_made.connect(count_actions)
        
        # Simulate the problematic scenario
        self._simulate_reach_action_phase()
        
        # Wait and check if actions are being triggered rapidly (indicating a loop)
        QTest.qWait(3000)  # Wait 3 seconds
        elapsed_time = time.time() - start_time
        
        # If more than 5 actions in 3 seconds, likely an infinite loop
        if action_count > 5:
            raise AssertionError(f"Detected potential infinite loop: {action_count} actions in {elapsed_time:.1f} seconds")
        
        print(f"  ✓ No infinite loop detected ({action_count} actions in {elapsed_time:.1f} seconds)")
    
    def _simulate_reach_action_phase(self):
        """Simulate reaching the action selection phase."""
        # Force the game engine to the correct state
        self.game_engine._current_phase = "FIRST_MARCH"
        self.game_engine._current_march_step = "SELECT_ACTION"
        
        # Trigger UI update
        self.gameplay_view.update_ui()
        QTest.qWait(500)
    
    def _test_skip_action(self):
        """Test the Skip Action button."""
        skip_button = self._find_button_in_view("Skip")
        if skip_button:
            assert skip_button.isEnabled(), "Skip button is not enabled"
            self.qtbot.mouseClick(skip_button, Qt.LeftButton)
            QTest.qWait(300)
        else:
            raise AssertionError("Skip Action button not found")
    
    def _test_melee_action(self):
        """Test the Melee action button.""" 
        melee_button = self._find_button_in_view("Melee")
        if melee_button:
            assert melee_button.isEnabled(), "Melee button is not enabled"
            # Don't actually click to avoid changing game state
        else:
            raise AssertionError("Melee button not found")
    
    def _test_missile_action(self):
        """Test the Missile action button."""
        missile_button = self._find_button_in_view("Missile")
        if missile_button:
            assert missile_button.isEnabled(), "Missile button is not enabled"
        else:
            raise AssertionError("Missile button not found")
    
    def _test_magic_action(self):
        """Test the Magic action button."""
        magic_button = self._find_button_in_view("Magic")
        if magic_button:
            assert magic_button.isEnabled(), "Magic button is not enabled"
        else:
            raise AssertionError("Magic button not found")
    
    def _find_button_in_view(self, text):
        """Find a button containing text in the gameplay view."""
        buttons = self.gameplay_view.findChildren(QPushButton)
        for button in buttons:
            if text.lower() in button.text().lower():
                return button
        return None


class TestErrorRecovery:
    """Test error recovery and robustness."""
    
    def test_terrain_data_error_recovery(self, qtbot):
        """Test that terrain data errors are handled gracefully."""
        print("\n🛡️ Testing Terrain Data Error Recovery")
        
        from components.action_decision_widget import ActionDecisionWidget
        
        widget = ActionDecisionWidget()
        qtbot.addWidget(widget)
        
        # Test with malformed terrain data
        malformed_army_data = {
            "name": "Test Army",
            "army_type": "campaign",
            "location": "INVALID_TERRAIN",
            "units": []
        }
        
        malformed_terrain_data = {
            "INVALID_TERRAIN": None  # This should not crash the widget
        }
        
        try:
            widget.set_acting_army(malformed_army_data, malformed_terrain_data)
            print("  ✓ Widget handled malformed data gracefully")
        except Exception as e:
            raise AssertionError(f"Widget failed to handle malformed data: {e}")
    
    def test_app_closure_after_fixes(self, qtbot):
        """Test that the application can be closed normally after fixes."""
        print("\n🚪 Testing Application Closure")
        
        main_window = MainWindow()
        qtbot.addWidget(main_window)
        main_window.show()
        qtbot.waitForWindowShown(main_window)
        
        # Simulate some activity
        QTest.qWait(1000)
        
        # Close the application
        main_window.close()
        QTest.qWait(500)
        
        # Verify it closed properly
        assert not main_window.isVisible(), "Main window did not close properly"
        print("  ✓ Application closes normally")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])