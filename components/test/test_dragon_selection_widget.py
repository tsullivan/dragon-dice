#!/usr/bin/env python3
"""
Tests for DragonSelectionWidget functionality
"""
import pytest
from PySide6.QtWidgets import QApplication

from components.dragon_selection_widget import DragonSelectionWidget
import utils.constants as constants


class TestDragonSelectionWidget:
    """Test the DragonSelectionWidget functionality."""

    def test_default_initialization(self, qtbot):
        """Test that widget initializes with correct defaults."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Check default values
        value = widget.value()
        assert value["dragon_type"] == constants.AVAILABLE_DRAGON_TYPES[0]
        assert value["die_type"] == "Drake"

    def test_dragon_type_selection(self, qtbot):
        """Test that dragon type can be changed."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Set to Blue Dragon
        widget.setValue({"dragon_type": "Blue Dragon", "die_type": "Dragon"})

        value = widget.value()
        assert value["dragon_type"] == "Blue Dragon"
        assert value["die_type"] == "Drake"

    def test_wyrm_selection(self, qtbot):
        """Test that wyrm can be selected."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Set to Gold Wyrm
        widget.setValue({"dragon_type": "Gold Dragon", "die_type": "Wyrm"})

        value = widget.value()
        assert value["dragon_type"] == "Gold Dragon"
        assert value["die_type"] == "Wyrm"

    def test_display_text(self, qtbot):
        """Test that display text is formatted correctly."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Test default
        assert "Red Dragon (Drake)" in widget.get_display_text()

        # Test after change
        widget.setValue({"dragon_type": "Black Dragon", "die_type": "Wyrm"})
        assert "Black Dragon (Wyrm)" in widget.get_display_text()

    def test_clear_functionality(self, qtbot):
        """Test that clear resets to defaults."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Change values
        widget.setValue({"dragon_type": "Ivory Dragon", "die_type": "Wyrm"})

        # Clear and check defaults
        widget.clear()
        value = widget.value()
        assert value["dragon_type"] == constants.AVAILABLE_DRAGON_TYPES[0]
        assert value["die_type"] == "Drake"

    def test_signal_emission(self, qtbot):
        """Test that valueChanged signal is emitted properly."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Connect to signal
        signal_received = []
        widget.valueChanged.connect(lambda x: signal_received.append(x))

        # Change value and verify signal
        new_value = {"dragon_type": "Green Dragon", "die_type": "Wyrm"}
        widget.setValue(new_value)

        assert len(signal_received) > 0
        assert signal_received[-1] == new_value


def test_dragon_constants():
    """Test that dragon constants are properly defined."""
    # Test dragon types exist
    assert len(constants.AVAILABLE_DRAGON_TYPES) > 0
    assert "Red Dragon" in constants.AVAILABLE_DRAGON_TYPES
    assert "Blue Dragon" in constants.AVAILABLE_DRAGON_TYPES

    # Test die types exist
    assert len(constants.AVAILABLE_DRAGON_DIE_TYPES) == 2
    assert "Drake" in constants.AVAILABLE_DRAGON_DIE_TYPES
    assert "Wyrm" in constants.AVAILABLE_DRAGON_DIE_TYPES

    # Test specific values
    assert constants.DRAGON_DATA["DIE_TYPES"]["DRAKE"]["display_name"] == "Drake"
    assert constants.DRAGON_DATA["DIE_TYPES"]["WYRM"]["display_name"] == "Wyrm"


if __name__ == "__main__":
    # Simple test runner
    app = QApplication([])

    print("Testing DragonSelectionWidget...")

    # Test basic functionality
    widget = DragonSelectionWidget(1)
    print(f"✓ Default value: {widget.value()}")

    # Test setting values
    widget.setValue({"dragon_type": "Blue Dragon", "die_type": "Wyrm"})
    print(f"✓ Set value: {widget.value()}")
    print(f"✓ Display text: {widget.get_display_text()}")

    # Test constants
    test_dragon_constants()
    print("✓ Constants defined correctly")

    print("\n🎉 All manual tests passed!")
