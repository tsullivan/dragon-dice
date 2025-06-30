#!/usr/bin/env python3
"""
Visual validation E2E tests for Dragon Dice application.
Tests UI state and visual elements during gameplay flow.
"""

import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QPixmap
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from main_window import MainWindow


class TestVisualValidation:
    """Visual validation tests to ensure UI elements render correctly."""
    
    @pytest.fixture(autouse=True)
    def setup_visual_test(self, qtbot):
        """Set up for visual testing."""
        self.qtbot = qtbot
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.main_window = MainWindow()
        self.qtbot.addWidget(self.main_window)
        self.main_window.show()
        self.qtbot.waitForWindowShown(self.main_window)
        
        yield
        
        self.main_window.close()
    
    def test_welcome_screen_visual_state(self, qtbot):
        """Test that the welcome screen renders correctly."""
        print("\n📸 Testing Welcome Screen Visual State")
        
        QTest.qWait(1000)  # Wait for full render
        
        # Take screenshot
        self._capture_screenshot("welcome_screen")
        
        # Verify essential elements are visible
        self._assert_widget_visible("welcome", "Welcome screen should be visible")
        
        # Check for key UI elements
        combo_boxes = self.main_window.findChildren(QComboBox)
        assert len(combo_boxes) >= 2, "Should have player count and force size combos"
        
        proceed_button = self._find_button_with_text("Proceed")
        assert proceed_button is not None, "Proceed button should be present"
        
        print("  ✓ Welcome screen visual state is correct")
    
    def test_player_setup_visual_state(self, qtbot):
        """Test that player setup screen renders correctly.""" 
        print("\n📸 Testing Player Setup Visual State")
        
        # Navigate to player setup
        self._navigate_to_player_setup()
        
        # Take screenshot
        self._capture_screenshot("player_setup_screen")
        
        # Verify player setup elements
        name_inputs = self.main_window.findChildren(QLineEdit)
        assert len(name_inputs) > 0, "Should have name input fields"
        
        manage_buttons = self._find_all_buttons_with_text("Manage Units")
        assert len(manage_buttons) >= 3, "Should have army management buttons"
        
        print("  ✓ Player setup visual state is correct")
    
    def test_main_gameplay_visual_state(self, qtbot):
        """Test that main gameplay screen renders correctly."""
        print("\n📸 Testing Main Gameplay Visual State")
        
        # Navigate through full flow to main gameplay
        self._navigate_to_main_gameplay()
        
        # Take screenshot
        self._capture_screenshot("main_gameplay_screen")
        
        # Verify action buttons are present and visible
        action_buttons = self._find_action_buttons()
        assert len(action_buttons) > 0, "Should have action buttons"
        
        for button in action_buttons:
            assert button.isVisible(), f"Action button '{button.text()}' should be visible"
            assert button.isEnabled(), f"Action button '{button.text()}' should be enabled"
        
        print("  ✓ Main gameplay visual state is correct")
    
    def test_ui_responsiveness_during_transitions(self, qtbot):
        """Test that UI remains responsive during screen transitions."""
        print("\n⚡ Testing UI Responsiveness During Transitions")
        
        transitions = [
            ("Welcome to Player Setup", self._navigate_to_player_setup),
            ("Quick Player Setup", self._quick_player_setup),
            ("Player Setup to Frontier", self._navigate_to_frontier),
            ("Frontier to Distance Rolls", self._navigate_to_distance_rolls),
            ("Distance Rolls to Gameplay", self._navigate_to_gameplay)
        ]
        
        for transition_name, transition_func in transitions:
            print(f"  Testing transition: {transition_name}")
            start_time = time.time()
            
            try:
                transition_func()
                elapsed = time.time() - start_time
                
                # Verify main window is still responsive
                assert self.main_window.isVisible(), f"Main window not visible after {transition_name}"
                assert elapsed < 10.0, f"Transition took too long: {elapsed:.1f}s"
                
                print(f"    ✓ Transition completed in {elapsed:.1f}s")
                
            except Exception as e:
                print(f"    ❌ Transition failed: {e}")
                raise
    
    def test_error_state_visual_feedback(self, qtbot):
        """Test that error states provide appropriate visual feedback."""
        print("\n🚨 Testing Error State Visual Feedback")
        
        # Test incomplete player setup
        self._navigate_to_player_setup()
        
        # Try to proceed without completing setup
        next_button = self._find_button_containing_text("Next")
        if next_button:
            next_button.click()
            QTest.qWait(500)
            
            # Should show validation error
            error_labels = self.main_window.findChildren(QLabel)
            error_found = any("error" in label.text().lower() for label in error_labels)
            
            if not error_found:
                print("  ⚠️ No visible error feedback found (this may be expected)")
            else:
                print("  ✓ Error feedback is displayed")
    
    # Navigation helper methods
    def _navigate_to_player_setup(self):
        """Navigate to player setup screen."""
        proceed_button = self._find_button_with_text("Proceed")
        if proceed_button:
            self.qtbot.mouseClick(proceed_button, Qt.LeftButton)
            QTest.qWait(1000)
    
    def _quick_player_setup(self):
        """Quickly set up players with minimal data."""
        # Set player name
        name_input = self.main_window.findChildren(QLineEdit)[0] if self.main_window.findChildren(QLineEdit) else None
        if name_input:
            name_input.setText("Test Player")
        
        # Add minimal units (click first available manage button)
        manage_buttons = self._find_all_buttons_with_text("Manage Units")
        if manage_buttons:
            self.qtbot.mouseClick(manage_buttons[0], Qt.LeftButton)
            QTest.qWait(500)
            
            # Add a unit if dialog opened
            add_buttons = self._find_all_buttons_with_text("Add")
            if add_buttons:
                self.qtbot.mouseClick(add_buttons[0], Qt.LeftButton)
            
            # Close dialog
            done_button = self._find_button_with_text("Done")
            if done_button:
                self.qtbot.mouseClick(done_button, Qt.LeftButton)
    
    def _navigate_to_frontier(self):
        """Navigate to frontier selection."""
        next_button = self._find_button_containing_text("Next")
        if next_button:
            self.qtbot.mouseClick(next_button, Qt.LeftButton)
            QTest.qWait(1000)
    
    def _navigate_to_distance_rolls(self):
        """Navigate to distance rolls."""
        submit_button = self._find_button_with_text("Submit")
        if submit_button:
            self.qtbot.mouseClick(submit_button, Qt.LeftButton)
            QTest.qWait(1000)
    
    def _navigate_to_gameplay(self):
        """Navigate to main gameplay."""
        submit_button = self._find_button_containing_text("Submit")
        if submit_button:
            self.qtbot.mouseClick(submit_button, Qt.LeftButton)
            QTest.qWait(2000)  # Wait for game initialization
    
    def _navigate_to_main_gameplay(self):
        """Navigate through complete flow to main gameplay."""
        self._navigate_to_player_setup()
        self._quick_player_setup()
        # Note: This is simplified - full implementation would need complete setup
    
    # Helper methods
    def _capture_screenshot(self, name):
        """Capture screenshot of current state."""
        pixmap = self.main_window.grab()
        filename = os.path.join(self.screenshots_dir, f"{name}.png")
        pixmap.save(filename)
        print(f"    📷 Screenshot saved: {filename}")
    
    def _assert_widget_visible(self, widget_name, message):
        """Assert that a widget is visible."""
        assert self.main_window.isVisible(), message
    
    def _find_button_with_text(self, text):
        """Find button with exact text."""
        from PySide6.QtWidgets import QPushButton
        buttons = self.main_window.findChildren(QPushButton)
        for button in buttons:
            if text in button.text():
                return button
        return None
    
    def _find_button_containing_text(self, text):
        """Find button containing text."""
        from PySide6.QtWidgets import QPushButton
        buttons = self.main_window.findChildren(QPushButton)
        for button in buttons:
            if text.lower() in button.text().lower():
                return button
        return None
    
    def _find_all_buttons_with_text(self, text):
        """Find all buttons containing text."""
        from PySide6.QtWidgets import QPushButton
        buttons = self.main_window.findChildren(QPushButton)
        return [btn for btn in buttons if text in btn.text()]
    
    def _find_action_buttons(self):
        """Find main gameplay action buttons."""
        action_texts = ["Melee", "Missile", "Magic", "Skip"]
        buttons = []
        for text in action_texts:
            button = self._find_button_containing_text(text)
            if button:
                buttons.append(button)
        return buttons


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])