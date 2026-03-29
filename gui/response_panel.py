"""Response and Scan Results panel with logging helpers"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
import time
from utils import COLORS


class ResponsePanel(QWidget):
    # Signal emitted whenever a log message is added
    log_signal = Signal(str, bool)  # (message, connected)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("COMMUNICATION LOG & SCAN REPORTS")
        title.setFont(QFont("Courier New", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_green']};")
        layout.addWidget(title)

        self.response_text = QPlainTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setMinimumHeight(200)
        layout.addWidget(self.response_text)

        self.scan_results_text = QPlainTextEdit()
        self.scan_results_text.setReadOnly(True)
        self.scan_results_text.setMinimumHeight(200)
        layout.addWidget(self.scan_results_text)

    def _timestamp(self):
        return time.strftime("[%H:%M:%S]")

    def log(self, message, connected=False):
        timestamp = self._timestamp()
        status = "●" if connected else "○"
        line_count = self.response_text.document().blockCount()
        formatted = f"{timestamp} {status} #{line_count:03d} {message}"
        self.response_text.appendPlainText(formatted)
        scrollbar = self.response_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Emit signal for external log window
        self.log_signal.emit(formatted, connected)

    def scan_log(self, message):
        timestamp = self._timestamp()
        line_count = self.scan_results_text.document().blockCount()
        formatted = f"{timestamp} #{line_count:03d} {message}"
        self.scan_results_text.appendPlainText(formatted)
        scrollbar = self.scan_results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
