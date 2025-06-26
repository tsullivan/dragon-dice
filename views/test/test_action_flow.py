#!/usr/bin/env python3
"""
Test script to demonstrate the improved action flow with ActionDialog.
This simulates the flow from your logs but now with complete action dialog integration.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from views.action_dialog import ActionDialog


class ActionFlowDemo(QWidget):
    """Demo widget to test the action dialog flow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice Action Flow Demo")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Dragon Dice Action Dialog Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This demonstrates the complete action flow that resolves the\n'AWAITING_ATTACKER_MELEE_ROLL' issue by providing a comprehensive\ndialog similar to the maneuver dialog."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Test buttons
        melee_btn = QPushButton("🗡️ Test Melee Action")
        melee_btn.clicked.connect(lambda: self.test_action_dialog("MELEE"))
        layout.addWidget(melee_btn)

        missile_btn = QPushButton("🏹 Test Missile Action")
        missile_btn.clicked.connect(lambda: self.test_action_dialog("MISSILE"))
        layout.addWidget(missile_btn)

        magic_btn = QPushButton("✨ Test Magic Action")
        magic_btn.clicked.connect(lambda: self.test_action_dialog("MAGIC"))
        layout.addWidget(magic_btn)

        # Results
        self.result_label = QLabel("Click a button to test the action dialog flow.")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(
            "margin: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;"
        )
        layout.addWidget(self.result_label)

    def test_action_dialog(self, action_type: str):
        """Test the action dialog with sample data."""
        # Sample data similar to what would be passed from the game engine
        sample_acting_army = {
            "name": "Campaign Army",
            "location": "Coastland (Blue, Green)",
            "units": [
                {"name": "Amazon War Driver", "health": 3},
                {"name": "Amazon Javelineer", "health": 2},
            ],
        }

        sample_player_data = {"Player 1": {"armies": {"campaign": sample_acting_army}}}

        sample_terrain_data = {
            "Coastland (Blue, Green)": {
                "name": "Coastland (Blue, Green)",
                "type": "Frontier",
                "face": 3,
            }
        }

        # Create and show the action dialog
        dialog = ActionDialog(
            action_type=action_type,
            current_player_name="Player 1",
            acting_army=sample_acting_army,
            all_players_data=sample_player_data,
            terrain_data=sample_terrain_data,
            parent=self,
        )

        # Connect signals to show results
        dialog.action_completed.connect(self.on_action_completed)
        dialog.action_cancelled.connect(self.on_action_cancelled)

        dialog.exec()

    def on_action_completed(self, result: dict):
        """Handle completed action."""
        action_type = result.get("action_type", "Unknown")
        attacker_results = result.get("attacker_results", "N/A")
        defender_results = result.get("defender_results", "N/A")

        self.result_label.setText(
            f"✅ {action_type} Action Completed!\n\n"
            f"Attacker rolled: {attacker_results}\n"
            f"Defender rolled: {defender_results}\n\n"
            f"The action flow completed successfully, resolving the\n"
            f"'AWAITING_ATTACKER_MELEE_ROLL' blocking issue."
        )

    def on_action_cancelled(self):
        """Handle cancelled action."""
        self.result_label.setText(
            "❌ Action was cancelled. The player can return to action selection."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = ActionFlowDemo()
    demo.show()

    print("Action Dialog Demo Started")
    print("This demonstrates the solution to the AWAITING_ATTACKER_MELEE_ROLL issue.")
    print("The new ActionDialog provides a complete flow similar to ManeuverDialog.")

    sys.exit(app.exec())
