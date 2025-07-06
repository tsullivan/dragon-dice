#!/usr/bin/env python3
"""
Tests for DragonSelectionWidget functionality
"""

import pytest
from PySide6.QtWidgets import QApplication

import constants
from components.dragon_selection_widget import DragonSelectionWidget
from models.dragon_model import (
    DRAGON_FORM_DATA,
    DRAGON_TYPE_DATA,
    get_available_dragon_forms,
    get_available_dragon_types,
)


class TestDragonSelectionWidget:
    """Test the DragonSelectionWidget functionality."""

    def test_default_initialization(self, qtbot):
        """Test that widget initializes with correct defaults."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Check default values
        value = widget.value()
        assert value["dragon_type"] == list(DRAGON_TYPE_DATA.keys())[0]  # Should be first dragon type
        assert value["dragon_form"] == get_available_dragon_forms()[0]  # Should be "Drake"

    def test_dragon_type_selection(self, qtbot):
        """Test that dragon type can be changed."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Set to FIRE_ELEMENTAL dragon type with Wyrm form
        widget.setValue({"dragon_type": "FIRE_ELEMENTAL", "dragon_form": "Wyrm"})

        value = widget.value()
        assert value["dragon_type"] == "FIRE_ELEMENTAL"
        assert value["dragon_form"] == "Wyrm"

    def test_wyrm_selection(self, qtbot):
        """Test that wyrm can be selected."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Set to AIR_ELEMENTAL dragon type with Wyrm form
        widget.setValue({"dragon_type": "AIR_ELEMENTAL", "dragon_form": "Wyrm"})

        value = widget.value()
        assert value["dragon_type"] == "AIR_ELEMENTAL"
        assert value["dragon_form"] == "Wyrm"

    def test_display_text(self, qtbot):
        """Test that display text is formatted correctly."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Test default
        assert "Drake" in widget.get_display_text()

        # Test after change
        widget.setValue({"dragon_type": "FIRE_ELEMENTAL", "dragon_form": "Wyrm"})
        assert "Wyrm" in widget.get_display_text()
        assert "Fire Elemental" in widget.get_display_text()

    def test_clear_functionality(self, qtbot):
        """Test that clear resets to defaults."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Change values
        widget.setValue({"dragon_type": "FIRE_ELEMENTAL", "dragon_form": "Wyrm"})

        # Clear and check defaults
        widget.clear()
        value = widget.value()
        assert value["dragon_type"] == list(DRAGON_TYPE_DATA.keys())[0]
        assert value["dragon_form"] == get_available_dragon_forms()[0]

    def test_signal_emission(self, qtbot):
        """Test that valueChanged signal is emitted properly."""
        widget = DragonSelectionWidget(dragon_number=1)
        qtbot.addWidget(widget)

        # Connect to signal
        signal_received = []
        widget.valueChanged.connect(lambda x: signal_received.append(x))

        # Change value and verify signal
        new_value = {"dragon_type": "WATER_ELEMENTAL", "dragon_form": "Wyrm"}
        widget.setValue(new_value)

        assert len(signal_received) > 0
        assert signal_received[-1] == new_value


def test_dragon_constants():
    """Test that dragon constants are properly defined."""
    # Test dragon forms exist
    assert len(get_available_dragon_forms()) == 2
    assert "Drake" in get_available_dragon_forms()
    assert "Wyrm" in get_available_dragon_forms()

    # Test dragon types exist
    assert len(get_available_dragon_types()) == 28  # All dragon types
    assert "FIRE_ELEMENTAL" in get_available_dragon_types()
    assert "WATER_AIR_HYBRID" in get_available_dragon_types()
    assert "WHITE" in get_available_dragon_types()

    # Test specific values
    assert DRAGON_FORM_DATA["DRAKE"].display_name == "Drake"
    assert DRAGON_FORM_DATA["WYRM"].display_name == "Wyrm"


if __name__ == "__main__":
    # Simple test runner
    app = QApplication([])

    print("Testing DragonSelectionWidget...")

    # Test basic functionality
    widget = DragonSelectionWidget(1)
    print(f"✓ Default value: {widget.value()}")

    # Test setting values
    widget.setValue({"dragon_type": "FIRE_ELEMENTAL", "dragon_form": "Wyrm"})
    print(f"✓ Set value: {widget.value()}")
    print(f"✓ Display text: {widget.get_display_text()}")

    # Test constants
    test_dragon_constants()
    print("✓ Constants defined correctly")

    print("\n🎉 All manual tests passed!")
