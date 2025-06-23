#!/usr/bin/env python3
"""
Demo script showing the new dragon/wyrm selection functionality
"""
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt

from views.player_setup_view import PlayerSetupView
from components.dragon_selection_widget import DragonSelectionWidget
import constants


class DragonSelectionDemo(QWidget):
    """Demo widget showing dragon selection functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon Dice - Dragon/Wyrm Selection Demo")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Dragon Dice: Dragon vs Wyrm Selection")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Players can now specify both the dragon type (Red, Blue, etc.) "
            "and whether it's a Dragon die or a Wyrm die for each dragon they bring to the game."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("margin: 10px; padding: 10px;")
        layout.addWidget(desc)
        
        # Example dragon widgets
        example_label = QLabel("Example Dragon Selections:")
        example_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(example_label)
        
        # Dragon 1 - Default
        self.dragon1 = DragonSelectionWidget(dragon_number=1)
        layout.addWidget(self.dragon1)
        
        # Dragon 2 - Set to Wyrm
        self.dragon2 = DragonSelectionWidget(dragon_number=2)
        self.dragon2.setValue({
            "dragon_type": "Blue Dragon",
            "die_type": "Wyrm"
        })
        layout.addWidget(self.dragon2)
        
        # Status display
        self.status_label = QLabel()
        self.status_label.setStyleSheet("margin: 20px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Button to show current selections
        show_button = QPushButton("Show Current Selections")
        show_button.clicked.connect(self.show_selections)
        layout.addWidget(show_button)
        
        # Connect signals to update status
        self.dragon1.valueChanged.connect(self.update_status)
        self.dragon2.valueChanged.connect(self.update_status)
        
        # Initial status update
        self.update_status()
    
    def update_status(self):
        """Update the status display with current selections."""
        dragon1_data = self.dragon1.value()
        dragon2_data = self.dragon2.value()
        
        status_text = f"""Current Dragon Selections:
        
Dragon 1: {dragon1_data['dragon_type']} ({dragon1_data['die_type']})
Dragon 2: {dragon2_data['dragon_type']} ({dragon2_data['die_type']})

Data format: {{"dragon_type": "...", "die_type": "..."}}"""
        
        self.status_label.setText(status_text)
    
    def show_selections(self):
        """Show current selections in a message."""
        dragons = [self.dragon1.value(), self.dragon2.value()]
        print("\nCurrent Dragon Selections:")
        for i, dragon in enumerate(dragons, 1):
            print(f"  Dragon {i}: {dragon}")
        print(f"\nThis data would be saved to player_data['selected_dragons']")


def main():
    app = QApplication(sys.argv)
    
    print("Dragon Dice - Dragon/Wyrm Selection Demo")
    print("=" * 50)
    print("\nNew Features:")
    print("• Players can select dragon type (Red, Blue, Green, etc.)")
    print("• Players can specify if each dragon is a Dragon die or Wyrm die")
    print("• Data is stored as {'dragon_type': '...', 'die_type': '...'}")
    print("• Backward compatibility with old string-only format")
    print("\nConstants added:")
    print(f"• DRAGON_DIE_TYPE_DRAGON = '{constants.DRAGON_DIE_TYPE_DRAGON}'")
    print(f"• DRAGON_DIE_TYPE_WYRM = '{constants.DRAGON_DIE_TYPE_WYRM}'")
    print(f"• AVAILABLE_DRAGON_DIE_TYPES = {constants.AVAILABLE_DRAGON_DIE_TYPES}")
    
    # Show the demo widget
    demo = DragonSelectionDemo()
    demo.show()
    
    print(f"\nDemo window opened. Try changing the dragon selections!")
    print("The status will update automatically as you make changes.")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())