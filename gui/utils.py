"""Shared utilities and constants for CyBot GUI"""

import time

# Military theme colors
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#2d3d1f',
    'border': '#4a5c23',
    'text_green': '#00ff00',
    'text_cyan': '#00ffff',
    'text_yellow': '#ffff00',
    'text_red': '#ff0000',
    'button_primary': '#3a4f2a',
    'button_hover': '#4a5c23',
}


def get_base_stylesheet():
    """Returns the base stylesheet for the application (matches legacy gui_client look)."""
    # Full consolidated stylesheet adapted from the legacy gui_client for a consistent military theme
    return """
QMainWindow {
    background-color: #1a1a1a;
    color: #00ff00;
}

QPushButton {
    background-color: #3a4f2a;
    color: #00ff00;
    border: 2px solid #4a5c23;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
    font-family: 'Courier New', monospace;
    qproperty-minimumSize: 80px 30px;
}
QPushButton:hover {
    background-color: #4a5c23;
    color: #ffffff;
    border-color: #5a6c33;
}
QPushButton:pressed {
    background-color: #2a3f1a;
    border-color: #4a5c23;
}
QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border-color: #333333;
}

QLineEdit {
    padding: 8px;
    border: 2px solid #4a5c23;
    border-radius: 4px;
    font-size: 11px;
    background-color: #2d3d1f;
    color: #00ff00;
    font-family: 'Courier New', monospace;
}
QLineEdit:focus {
    border-color: #00ff00;
    background-color: #3a4f2a;
}

QTextEdit, QPlainTextEdit {
    background-color: #0a0a0a;
    color: #00ff00;
    font-family: 'Courier New', 'Monaco', monospace;
    font-size: 10px;
    border: 2px solid #4a5c23;
    border-radius: 4px;
    padding: 8px;
}

QLabel {
    color: #00ff00;
    font-family: 'Courier New', monospace;
}

QFrame {
    border: 1px solid #4a5c23;
    background-color: #2d3d1f;
}

QSplitter::handle {
    background-color: #4a5c23;
}
QSplitter::handle:hover {
    background-color: #5a6c33;
}

QTabWidget::pane {
    border: 2px solid #4a5c23;
    background-color: #2d3d1f;
}
QTabBar::tab {
    background-color: #3a4f2a;
    color: #00ff00;
    padding: 8px 16px;
    margin: 2px;
    border: 1px solid #4a5c23;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #4a5c23;
    color: #ffffff;
}
QTabBar::tab:hover {
    background-color: #556b3d;
}

QListWidget {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #4a5c23;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    padding: 5px;
}
QListWidget::item:selected {
    background-color: #4a5c23;
    color: #ffffff;
}

"""


def format_log_message(message, connected=False):
    """Format a log message with timestamp and status indicator"""
    timestamp = time.strftime("[%H:%M:%S]")
    status_indicator = "●" if connected else "○"
    return f"{timestamp} {status_indicator} {message}"
