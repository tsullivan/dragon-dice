from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QWidget
from typing import Optional


class HelpPanelWidget(QGroupBox):
    """
    A reusable widget for displaying help text.
    It consists of a QGroupBox with a QTextEdit inside.
    """

    def __init__(self, title: str = "Help", parent: Optional[QWidget] = None):
        super().__init__(title, parent)

        layout = QVBoxLayout(self)

        self.help_text_edit = QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setMaximumWidth(
            400
        )  # Prevent excessive horizontal stretching
        self.help_text_edit.setMaximumHeight(
            300
        )  # Limit vertical size to reasonable height
        # Apply common stylesheet for list formatting
        self.help_text_edit.setStyleSheet(
            "ul { margin-left: 0px; padding-left: 5px; list-style-position: inside; } li { margin-bottom: 3px; }"
        )

        layout.addWidget(self.help_text_edit)
        self.setLayout(layout)

    def set_help_text(self, html_content: str):
        """Sets the HTML content of the help text display."""
        self.help_text_edit.setHtml(html_content)
