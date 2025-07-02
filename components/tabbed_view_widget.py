from typing import Optional

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from components.help_panel_widget import HelpPanelWidget


class TabbedViewWidget(QWidget):
    """
    A reusable tabbed widget that provides a standardized interface for views
    with "Game" and "Help" tabs. This component allows views to easily add
    their main content to the Game tab and help content to the Help tab.

    This widget maintains the existing HelpPanelWidget functionality while
    providing a clean tabbed interface that can be used across all views.

    INTEGRATION GUIDE:
    ==================

    Basic Usage:
    -----------
    1. Create a TabbedViewWidget instance: self.tabbed_widget = TabbedViewWidget()
    2. Build your game content and add it: self.tabbed_widget.add_game_content(widget)
    3. Set help text: self.tabbed_widget.set_help_text(help_html)
    4. Add to your main layout: main_layout.addWidget(self.tabbed_widget)

    Refactoring Existing Views:
    --------------------------
    To refactor existing views (like WelcomeView, MainGameplayView, etc.):
    1. Replace the existing side-by-side layout with TabbedViewWidget
    2. Move main content from the left side to Game tab using add_game_content()
    3. Replace direct HelpPanelWidget usage with set_help_text()
    4. Preserve all existing functionality and signals

    Example:
    --------
    # OLD: main_layout.addWidget(help_panel, 1)
    # NEW: self.tabbed_widget.set_help_text(help_content)

    # OLD: main_layout.addWidget(main_content)
    # NEW: self.tabbed_widget.add_game_content(main_content)

    See tabbed_view_example.py for complete integration examples.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the tabbed interface with Game and Help tabs."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create the tab widget
        self.tab_widget = QTabWidget()

        # Create Game tab (empty widget to be populated by child views)
        self.game_tab = QWidget()
        self.game_layout = QVBoxLayout(self.game_tab)
        self.game_layout.setContentsMargins(5, 5, 5, 5)

        # Create Help tab with HelpPanelWidget
        self.help_tab = QWidget()
        help_tab_layout = QVBoxLayout(self.help_tab)
        help_tab_layout.setContentsMargins(5, 5, 5, 5)

        # Use the existing HelpPanelWidget for consistency
        self.help_panel = HelpPanelWidget("Help")
        help_tab_layout.addWidget(self.help_panel)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.game_tab, "Game")
        self.tab_widget.addTab(self.help_tab, "Help")

        # Set Game tab as default
        self.tab_widget.setCurrentIndex(0)

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def add_game_content(self, widget: QWidget):
        """
        Add a widget to the Game tab content area.

        Args:
            widget: The widget to add to the Game tab
        """
        self.game_layout.addWidget(widget)

    def add_game_layout(self, layout):
        """
        Add a layout to the Game tab content area.

        Args:
            layout: The layout to add to the Game tab
        """
        self.game_layout.addLayout(layout)

    def set_help_text(self, html_content: str):
        """
        Set the help text content for the Help tab.
        This preserves the existing HelpPanelWidget API.

        Args:
            html_content: HTML formatted help text to display
        """
        self.help_panel.set_help_text(html_content)

    def get_game_tab(self) -> QWidget:
        """
        Get the Game tab widget for direct manipulation if needed.

        Returns:
            The Game tab widget
        """
        return self.game_tab

    def get_game_layout(self) -> QVBoxLayout:
        """
        Get the Game tab layout for direct manipulation if needed.

        Returns:
            The Game tab's QVBoxLayout
        """
        return self.game_layout

    def get_help_panel(self) -> HelpPanelWidget:
        """
        Get the help panel widget for direct manipulation if needed.

        Returns:
            The HelpPanelWidget instance
        """
        return self.help_panel

    def set_current_tab(self, tab_name: str):
        """
        Set the currently active tab by name.

        Args:
            tab_name: Either "Game" or "Help"
        """
        if tab_name.lower() == "game":
            self.tab_widget.setCurrentIndex(0)
        elif tab_name.lower() == "help":
            self.tab_widget.setCurrentIndex(1)

    def get_current_tab_name(self) -> str:
        """
        Get the name of the currently active tab.

        Returns:
            Either "Game" or "Help"
        """
        current_index = self.tab_widget.currentIndex()
        return "Game" if current_index == 0 else "Help"
