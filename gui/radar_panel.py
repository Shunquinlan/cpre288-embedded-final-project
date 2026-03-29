"""Radar display panel - shows only the radar visualization"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QCheckBox, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from utils import COLORS

# Import RadarWidget from scan_panel
try:
    from scan_panel import RadarWidget
except ImportError:
    RadarWidget = None


class RadarPanel(QWidget):
    """Panel that displays only the radar visualization with compass heading"""
    
    # Signal to request IMU calibration
    calibrate_imu_requested = Signal()
    # Signal to request setting north reference
    set_north_requested = Signal()
    # Signal to request compass refresh
    refresh_compass_requested = Signal()

    def __init__(self):
        super().__init__()
        self.radar_widget = None
        self.current_heading = None
        self.current_cardinal = "?"
        self.calibration_status = "0,0"
        self.initial_heading = None  # Store initial heading for reference
        self.init_ui()

    def init_ui(self):
        """Initialize the radar panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("◈ RADAR DISPLAY ◈")
        title.setFont(QFont("Courier New", 12, QFont.Bold))
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_green']};
                background-color: {COLORS['bg_dark']};
                padding: 10px;
                border: 2px solid {COLORS['text_green']};
                border-radius: 5px;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Compass display frame
        compass_frame = QFrame()
        compass_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #00ffff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        compass_layout = QHBoxLayout(compass_frame)
        compass_layout.setSpacing(15)
        
        compass_title = QLabel("◈ COMPASS ◈")
        compass_title.setFont(QFont("Courier New", 10, QFont.Bold))
        compass_title.setStyleSheet("color: #00ffff; border: none;")
        compass_layout.addWidget(compass_title)
        
        self.compass_display = QLabel("--- ° ? [Cal: 0,0]")
        self.compass_display.setFont(QFont("Courier New", 12, QFont.Bold))
        self.compass_display.setStyleSheet("""
            QLabel {
                color: #ffff00;
                background-color: #0a0a0a;
                padding: 8px 15px;
                border: 2px solid #ffff00;
                border-radius: 6px;
            }
        """)
        self.compass_display.setAlignment(Qt.AlignCenter)
        compass_layout.addWidget(self.compass_display)
        
        # Calibrate button
        self.calibrate_button = QPushButton("CALIBRATE IMU")
        self.calibrate_button.setFont(QFont("Courier New", 9, QFont.Bold))
        self.calibrate_button.setStyleSheet("""
            QPushButton {
                color: #00ffff;
                background-color: #0a0a0a;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 6px 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1a3a3a;
                border-color: #00ffff;
            }
            QPushButton:pressed {
                background-color: #00ffff;
                color: #000000;
            }
        """)
        self.calibrate_button.clicked.connect(self._on_calibrate_clicked)
        compass_layout.addWidget(self.calibrate_button)
        
        # Set North button
        self.set_north_button = QPushButton("SET NORTH")
        self.set_north_button.setFont(QFont("Courier New", 9, QFont.Bold))
        self.set_north_button.setStyleSheet("""
            QPushButton {
                color: #ffff00;
                background-color: #0a0a0a;
                border: 2px solid #ffff00;
                border-radius: 5px;
                padding: 6px 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a3a1a;
                border-color: #ffff00;
            }
            QPushButton:pressed {
                background-color: #ffff00;
                color: #000000;
            }
        """)
        self.set_north_button.clicked.connect(self._on_set_north_clicked)
        compass_layout.addWidget(self.set_north_button)
        
        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFont(QFont("Courier New", 12, QFont.Bold))
        self.refresh_button.setToolTip("Refresh compass reading")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                color: #00ff00;
                background-color: #0a0a0a;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 6px 10px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #1a3a1a;
                border-color: #00ff00;
            }
            QPushButton:pressed {
                background-color: #00ff00;
                color: #000000;
            }
        """)
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        compass_layout.addWidget(self.refresh_button)
        
        compass_layout.addStretch()
        layout.addWidget(compass_frame)

        # Radar container frame
        radar_frame = QFrame()
        radar_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        radar_layout = QVBoxLayout(radar_frame)

        # Toggle controls
        toggle_layout = QHBoxLayout()
        toggle_layout.setSpacing(15)
        toggle_layout.addStretch()

        # PING checkbox
        self.ping_checkbox = QCheckBox("PING")
        self.ping_checkbox.setChecked(True)
        self.ping_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_green']};
                font-family: 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['text_green']};
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['text_green']};
            }}
        """)
        self.ping_checkbox.stateChanged.connect(self._on_toggle_changed)
        toggle_layout.addWidget(self.ping_checkbox)

        # IR checkbox
        self.ir_checkbox = QCheckBox("IR")
        self.ir_checkbox.setChecked(True)
        self.ir_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: #ff6600;
                font-family: 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #ff6600;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: #ff6600;
            }}
        """)
        self.ir_checkbox.stateChanged.connect(self._on_toggle_changed)
        toggle_layout.addWidget(self.ir_checkbox)

        # OBJECT checkbox
        self.object_checkbox = QCheckBox("OBJ")
        self.object_checkbox.setChecked(True)
        self.object_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: #ffff00;
                font-family: 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #ffff00;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: #ffff00;
            }}
        """)
        self.object_checkbox.stateChanged.connect(self._on_toggle_changed)
        toggle_layout.addWidget(self.object_checkbox)

        # TAPE checkbox
        self.tape_checkbox = QCheckBox("TAPE")
        self.tape_checkbox.setChecked(True)
        self.tape_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: #ff00ff;
                font-family: 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #ff00ff;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: #ff00ff;
            }}
        """)
        self.tape_checkbox.stateChanged.connect(self._on_toggle_changed)
        toggle_layout.addWidget(self.tape_checkbox)

        # LINES checkbox
        self.lines_checkbox = QCheckBox("LINES")
        self.lines_checkbox.setChecked(True)
        self.lines_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: #b400dc;
                font-family: 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #b400dc;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: #b400dc;
            }}
        """)
        self.lines_checkbox.stateChanged.connect(self._on_toggle_changed)
        toggle_layout.addWidget(self.lines_checkbox)

        toggle_layout.addStretch()
        radar_layout.addLayout(toggle_layout)

        # Radar widget
        if RadarWidget:
            self.radar_widget = RadarWidget()
            self.radar_widget.setMinimumSize(400, 400)
            radar_layout.addWidget(self.radar_widget)
        else:
            error_label = QLabel("RadarWidget not available")
            error_label.setAlignment(Qt.AlignCenter)
            radar_layout.addWidget(error_label)

        # Radar info label
        self.radar_info = QLabel("Awaiting scan data...")
        self.radar_info.setFont(QFont("Courier New", 9))
        self.radar_info.setStyleSheet(f"color: {COLORS['text_green']}; padding: 8px;")
        self.radar_info.setAlignment(Qt.AlignCenter)
        radar_layout.addWidget(self.radar_info)

        layout.addWidget(radar_frame)

    def _on_toggle_changed(self):
        """Handle toggle checkbox state changes"""
        if self.radar_widget:
            # Update the radar widget's toggle states
            self.radar_widget.show_ping = self.ping_checkbox.isChecked()
            self.radar_widget.show_ir = self.ir_checkbox.isChecked()
            self.radar_widget.show_objects = self.object_checkbox.isChecked()
            self.radar_widget.show_taped_objects = self.tape_checkbox.isChecked()
            self.radar_widget.show_object_lines = self.lines_checkbox.isChecked()
            # Force a repaint
            self.radar_widget.update()

    def _on_calibrate_clicked(self):
        """Handle calibrate button click"""
        self.calibrate_imu_requested.emit()
    
    def _on_set_north_clicked(self):
        """Handle set north button click"""
        self.set_north_requested.emit()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click"""
        self.refresh_compass_requested.emit()
    
    def update_scan_data(self, angles, ping_distances, ir_distances=None):
        """Update radar display with new scan data"""
        if self.radar_widget:
            self.radar_widget.update_scan_data(angles, ping_distances, ir_distances)

    def clear_scan(self):
        """Clear the radar display"""
        if self.radar_widget:
            self.radar_widget.clear_scan()
            self.radar_info.setText("Radar cleared - awaiting new scan data...")

    def set_info_text(self, text):
        """Set the info label text"""
        if self.radar_info:
            self.radar_info.setText(text)
    
    def update_compass_heading(self, heading, cardinal, sys_cal, mag_cal):
        """Update compass display with new heading data
        
        Args:
            heading: Float heading in degrees (0-360)
            cardinal: String cardinal direction (N, NE, E, SE, S, SW, W, NW)
            sys_cal: System calibration status (0-3)
            mag_cal: Magnetometer calibration status (0-3)
        """
        # Store initial heading if this is the first reading
        if self.initial_heading is None and heading is not None:
            self.initial_heading = heading
        
        self.current_heading = heading
        self.current_cardinal = cardinal
        self.calibration_status = f"{sys_cal},{mag_cal}"
        
        # Calculate heading change from initial
        heading_change = ""
        if self.initial_heading is not None and heading is not None:
            delta = heading - self.initial_heading
            # Normalize to -180 to 180
            if delta > 180:
                delta -= 360
            elif delta < -180:
                delta += 360
            heading_change = f" (Δ{delta:+.1f}°)"
        
        # Update display
        heading_str = f"{heading:.1f}°" if heading is not None else "---°"
        cal_color = "#00ff00" if sys_cal >= 3 and mag_cal >= 3 else "#ffaa00" if sys_cal >= 2 else "#ff0000"
        
        self.compass_display.setText(f"{heading_str} {cardinal}{heading_change} [Cal: {sys_cal},{mag_cal}]")
        self.compass_display.setStyleSheet(f"""
            QLabel {{
                color: {cal_color};
                background-color: #0a0a0a;
                padding: 8px 15px;
                border: 2px solid {cal_color};
                border-radius: 6px;
            }}
        """)
    
    def clear_compass(self):
        """Clear compass display"""
        self.current_heading = None
        self.current_cardinal = "?"
        self.calibration_status = "0,0"
        self.initial_heading = None  # Reset initial heading
        self.compass_display.setText("--- ° ? [Cal: 0,0]")
        self.compass_display.setStyleSheet("""
            QLabel {
                color: #ffff00;
                background-color: #0a0a0a;
                padding: 8px 15px;
                border: 2px solid #ffff00;
                border-radius: 6px;
            }
        """)
