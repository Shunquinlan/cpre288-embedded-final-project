#!/usr/bin/env python3
"""Launcher for CyBot modular GUI.

Run this from the `gui` folder:
    python run_gui.py

This creates the QApplication and shows the `CyBotMainWindow` defined in
`main_window.py`.
"""
import sys
import os

# Ensure local package imports resolve when running from this folder
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication

try:
    from main_window import CyBotMainWindow
except Exception as e:
    print("Failed to import main_window:", e)
    raise


def main():
    app = QApplication(sys.argv)
    win = CyBotMainWindow()
    win.show()

    # Force non-native menu bars in some environments (optional)
    try:
        menubar = win.menuBar()
        if hasattr(menubar, "setNativeMenuBar"):
            menubar.setNativeMenuBar(False)
    except Exception:
        pass

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
