"""
Example demonstrating how to use TabbedViewWidget in a view.
This shows the recommended pattern for integrating the tabbed interface
into existing or new views.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QRadioButton, QButtonGroup, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal

from components.tabbed_view_widget import TabbedViewWidget
from models.help_text_model import HelpTextModel


class ExampleTabbedView(QWidget):
    """
    Example view showing how to use TabbedViewWidget.
    This demonstrates the recommended integration pattern.
    """
    
    # Signals for the view
    example_signal = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_model = HelpTextModel()
        self.setWindowTitle("Example Tabbed View")
        
        # Create the main layout
        main_layout = QVBoxLayout(self)
        
        # Create the tabbed widget
        self.tabbed_widget = TabbedViewWidget()
        
        # Build the game content
        self._build_game_content()
        
        # Set up help content
        self._setup_help_content()
        
        # Add the tabbed widget to the main layout
        main_layout.addWidget(self.tabbed_widget)
        self.setLayout(main_layout)
    
    def _build_game_content(self):
        """Build the main game content for the Game tab."""
        
        # Create a title
        title_label = QLabel("Example Game View")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        
        # Create some example controls
        controls_group = QGroupBox("Example Controls")
        controls_layout = QVBoxLayout()
        
        # Radio button group
        option_group = QGroupBox("Select Option:")
        option_layout = QHBoxLayout()
        self.option_button_group = QButtonGroup(self)
        
        options = ["Option A", "Option B", "Option C"]
        for i, option in enumerate(options):
            radio_button = QRadioButton(option)
            self.option_button_group.addButton(radio_button, i)
            option_layout.addWidget(radio_button)
            if i == 0:  # Default selection
                radio_button.setChecked(True)
        
        option_group.setLayout(option_layout)
        controls_layout.addWidget(option_group)
        
        # Action button
        action_button = QPushButton("Perform Action")
        action_button.clicked.connect(self._on_action_clicked)
        controls_layout.addWidget(action_button)
        
        controls_group.setLayout(controls_layout)
        
        # Add content to the Game tab
        self.tabbed_widget.add_game_content(title_label)
        self.tabbed_widget.add_game_content(controls_group)
        
        # Add a spacer to push content to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.tabbed_widget.get_game_layout().addSpacerItem(spacer)
    
    def _setup_help_content(self):
        """Set up the help content for the Help tab."""
        help_text = """
<b>Example Tabbed View Help</b>
<p>This is an example of how to use the TabbedViewWidget component.</p>
<p><b>Game Tab:</b> Contains the main functionality of the view.</p>
<p><b>Help Tab:</b> Contains this help information.</p>
<p><b>UI Elements:</b></p>
<ul>
    <li><b>Select Option:</b> Choose from the available options.</li>
    <li><b>Perform Action:</b> Click to execute the selected action.</li>
</ul>
<p><b>Usage Pattern:</b></p>
<ul>
    <li>Create a TabbedViewWidget instance</li>
    <li>Build your game content and add it using add_game_content() or add_game_layout()</li>
    <li>Set help text using set_help_text()</li>
    <li>Add the tabbed widget to your main layout</li>
</ul>
"""
        self.tabbed_widget.set_help_text(help_text)
    
    def _on_action_clicked(self):
        """Handle action button click."""
        selected_button = self.option_button_group.checkedButton()
        if selected_button:
            option_text = selected_button.text()
            self.example_signal.emit(f"Selected: {option_text}")
            print(f"Action performed with: {option_text}")


# Example of how existing views can be refactored
class RefactoredWelcomeViewExample(QWidget):
    """
    Example showing how the existing WelcomeView could be refactored 
    to use TabbedViewWidget while preserving all functionality.
    """
    
    proceed_signal = Signal()
    player_count_selected_signal = Signal(int)
    force_size_selected_signal = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_model = HelpTextModel()
        self.setWindowTitle("Welcome Screen - Tabbed")
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tabbed widget
        self.tabbed_widget = TabbedViewWidget()
        
        # Build the game content (same as original WelcomeView)
        self._build_welcome_content()
        
        # Set help content
        self._setup_welcome_help()
        
        main_layout.addWidget(self.tabbed_widget)
        self.setLayout(main_layout)
    
    def _build_welcome_content(self):
        """Build the welcome screen content - same as original but in Game tab."""
        # This would contain the exact same content as the original WelcomeView
        # but added to the tabbed widget instead of directly to the main layout
        
        # Welcome Title
        title_label = QLabel("Welcome to Dragon Dice Companion (PySide6)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        
        # Add title to Game tab
        self.tabbed_widget.add_game_content(title_label)
        
        # ... rest of the original content would be added here using
        # self.tabbed_widget.add_game_content() or self.tabbed_widget.add_game_layout()
        
        # Example: Proceed button
        proceed_button = QPushButton("Proceed to Player Setup")
        proceed_button.clicked.connect(self.proceed_signal.emit)
        self.tabbed_widget.add_game_content(proceed_button)
    
    def _setup_welcome_help(self):
        """Set up welcome help content."""
        self.tabbed_widget.set_help_text(self.help_model.get_welcome_help())


if __name__ == "__main__":
    """
    Simple test to demonstrate the component.
    Run this file directly to see the tabbed widget in action.
    """
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the example
    example = ExampleTabbedView()
    example.show()
    
    sys.exit(app.exec())