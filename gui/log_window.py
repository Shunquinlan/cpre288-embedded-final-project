"""Separate window for viewing logs"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTextEdit, 
                               QPushButton, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor
from utils import COLORS


class LogWindow(QMainWindow):
    """Floating window to display logs separately from main GUI"""
    
    # Signal emitted when window is closed
    window_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the log window UI"""
        self.setWindowTitle("CyBot Logs")
        self.setGeometry(200, 200, 800, 600)
        
        # Apply dark theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
            QTextEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_green']};
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }}
            QPushButton {{
                background-color: {COLORS['button_primary']};
                color: {COLORS['text_green']};
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: #2a3f1a;
            }}
            QLabel {{
                color: {COLORS['text_green']};
                font-weight: bold;
                font-size: 11pt;
            }}
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("System Logs")
        title.setStyleSheet(f"color: {COLORS['text_green']}; font-size: 14pt;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("● Disconnected")
        self.status_label.setStyleSheet(f"color: {COLORS['text_red']}; font-size: 10pt;")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.log_text)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_btn)
        
        # Auto-scroll toggle
        self.autoscroll_btn = QPushButton("Auto-scroll: ON")
        self.autoscroll_btn.setCheckable(True)
        self.autoscroll_btn.setChecked(True)
        self.autoscroll_btn.clicked.connect(self.toggle_autoscroll)
        button_layout.addWidget(self.autoscroll_btn)
        
        button_layout.addStretch()
        
        # Close button
        self.close_btn = QPushButton("✖ Close Window")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # State
        self.autoscroll_enabled = True
        
    @Slot(str, bool)
    def append_log(self, message, connected=False):
        """Append a log message to the window
        
        Args:
            message: The log message to display
            connected: Whether CyBot is currently connected
        """
        self.log_text.append(message)
        
        # Auto-scroll to bottom if enabled
        if self.autoscroll_enabled:
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)
    
    @Slot()
    def clear_logs(self):
        """Clear all logs from the window"""
        self.log_text.clear()
        self.log_text.append("=== Logs cleared ===")
    
    @Slot()
    def toggle_autoscroll(self):
        """Toggle auto-scrolling of logs"""
        self.autoscroll_enabled = self.autoscroll_btn.isChecked()
        if self.autoscroll_enabled:
            self.autoscroll_btn.setText("Auto-scroll: ON")
            self.autoscroll_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['button_primary']};
                    color: {COLORS['text_green']};
                    border: 2px solid {COLORS['border']};
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
            """)
        else:
            self.autoscroll_btn.setText("Auto-scroll: OFF")
            self.autoscroll_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #555555;
                    color: {COLORS['text_green']};
                    border: 2px solid #666666;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
            """)
    
    @Slot(bool)
    def update_connection_status(self, connected):
        """Update the connection status indicator
        
        Args:
            connected: Whether CyBot is currently connected
        """
        if connected:
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet(f"color: {COLORS['text_green']}; font-size: 10pt;")
        else:
            self.status_label.setText("● Disconnected")
            self.status_label.setStyleSheet(f"color: {COLORS['text_red']}; font-size: 10pt;")
    
    def closeEvent(self, event):
        """Override close event to emit signal"""
        self.window_closed.emit()
        super().closeEvent(event)
