"""Scan / sensor control panel with radar visualization"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QPushButton, QLabel, QFrame, QSizePolicy, QCheckBox)
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient
import numpy as np
import math

# Color scheme for UI elements
COLORS = {
    'bg_dark': '#1a1a1a',
    'text_green': '#00ff00',
    'text_cyan': '#00ffff',
    'text_yellow': '#ffff00',
    'border_green': '#00ff00',
}


class RadarWidget(QWidget):
    """Custom widget to display radar-like scan visualization with PING and IR data"""
    
    def __init__(self):
        super().__init__()
        self.angles = []
        self.ping_distances = []
        self.ir_distances = []
        self.object_angles = []  # List of angles where objects were detected
        self.taped_object_angles = []  # List of angles where objects with tape were detected
        self.max_distance = 200  # cm
        
        # Toggle flags for display
        self.show_ping = True
        self.show_ir = True
        self.show_objects = True
        self.show_taped_objects = True
        self.show_object_lines = True  # Toggle for object pointer lines
        
        # Mouse hover tracking
        self.setMouseTracking(True)
        self.hover_point_index = -1
        self.hover_info = ""
        
        self.setMinimumSize(350, 350)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; border: 2px solid {COLORS['text_green']}; border-radius: 10px;")
        
    def update_scan_data(self, angles, ping_distances, ir_distances=None, object_angles=None, taped_object_angles=None):
        """Update the radar display with new scan data (both PING and IR)"""
        self.angles = angles.copy() if angles else []
        self.ping_distances = ping_distances.copy() if ping_distances else []
        self.ir_distances = ir_distances.copy() if ir_distances else []
        self.object_angles = object_angles.copy() if object_angles else []
        self.taped_object_angles = taped_object_angles.copy() if taped_object_angles else []
        
        # Debug logging
        if object_angles or taped_object_angles:
            print(f"[DEBUG] RadarWidget.update_scan_data: object_angles={object_angles}, taped_object_angles={taped_object_angles}")
            print(f"[DEBUG] RadarWidget now has: {len(self.angles)} scan angles, {len(self.object_angles)} object angles, {len(self.taped_object_angles)} taped")
        
        self.update()  # Trigger repaint
    
    def toggle_ping(self, state):
        """Toggle PING data visibility"""
        self.show_ping = state
        self.update()
    
    def toggle_ir(self, state):
        """Toggle IR data visibility"""
        self.show_ir = state
        self.update()
    
    def toggle_objects(self, state):
        """Toggle object markers visibility"""
        self.show_objects = state
        self.update()
    
    def toggle_taped_objects(self, state):
        """Toggle taped object markers visibility"""
        self.show_taped_objects = state
        self.update()
    
    def toggle_object_lines(self, state):
        """Toggle object pointer lines visibility"""
        self.show_object_lines = state
        self.update()
        
    def clear_scan(self):
        """Clear all scan data"""
        self.angles = []
        self.ping_distances = []
        self.ir_distances = []
        self.object_angles = []
        self.taped_object_angles = []
        self.hover_point_index = -1
        self.hover_info = ""
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event to draw radar display with PING and IR data"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20
        
        # Draw background gradient
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor(30, 30, 30))
        gradient.setColorAt(1, QColor(10, 10, 10))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), 
                          int(radius * 2), int(radius * 2))
        
        # Draw range circles
        painter.setPen(QPen(QColor(0, 100, 0), 1, Qt.DotLine))
        for i in range(1, 5):
            r = radius * i / 4
            painter.drawEllipse(int(center_x - r), int(center_y - r), int(r * 2), int(r * 2))
            
        # Draw angle lines (every 30 degrees)
        painter.setPen(QPen(QColor(0, 100, 0), 1))
        for angle_deg in range(0, 181, 30):
            angle_rad = math.radians(angle_deg)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y - radius * math.sin(angle_rad)
            painter.drawLine(int(center_x), int(center_y), int(x), int(y))
            
        # Draw center line (90 degrees - forward)
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        angle_rad = math.radians(90)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)
        painter.drawLine(int(center_x), int(center_y), int(x), int(y))
        
        # Draw distance labels
        painter.setPen(QColor(0, 255, 0))
        painter.setFont(QFont("Courier New", 8))
        for i in range(1, 5):
            dist = self.max_distance * i / 4
            r = radius * i / 4
            painter.drawText(int(center_x + 5), int(center_y - r + 5), f"{int(dist)}cm")
            
        # Draw angle labels
        labels = ["180°", "150°", "120°", "90°", "60°", "30°", "0°"]
        angles_deg = [180, 150, 120, 90, 60, 30, 0]
        for label, angle_deg in zip(labels, angles_deg):
            angle_rad = math.radians(angle_deg)
            x = center_x + (radius + 15) * math.cos(angle_rad)
            y = center_y - (radius + 15) * math.sin(angle_rad)
            painter.drawText(int(x - 15), int(y + 5), label)
        
        # Draw PING data (BLUE line and points)
        if self.angles and self.ping_distances and self.show_ping:
            # Draw connecting line for PING
            if len(self.angles) > 1:
                painter.setPen(QPen(QColor(0, 100, 255), 2, Qt.SolidLine))
                for i in range(len(self.angles) - 1):
                    angle1 = self.angles[i]
                    angle2 = self.angles[i + 1]
                    dist1 = self.ping_distances[i]
                    dist2 = self.ping_distances[i + 1]
                    
                    x1 = center_x + (dist1 / self.max_distance) * radius * math.cos(angle1)
                    y1 = center_y - (dist1 / self.max_distance) * radius * math.sin(angle1)
                    x2 = center_x + (dist2 / self.max_distance) * radius * math.cos(angle2)
                    y2 = center_y - (dist2 / self.max_distance) * radius * math.sin(angle2)
                    
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
            # Draw PING points
            for i, (angle, distance) in enumerate(zip(self.angles, self.ping_distances)):
                x = center_x + (distance / self.max_distance) * radius * math.cos(angle)
                y = center_y - (distance / self.max_distance) * radius * math.sin(angle)
                
                # Check if this angle is part of a detected object
                angle_deg = math.degrees(angle)
                is_object = any(abs(angle_deg - obj_angle) < 2 for obj_angle in self.object_angles)
                is_taped_object = any(abs(angle_deg - taped_angle) < 2 for taped_angle in self.taped_object_angles)
                
                # Check if this point is being hovered over
                is_hovered = (i == self.hover_point_index)
                
                # Determine if we should draw this point and what color
                should_draw = False
                color = None
                size = 8  # default size
                
                # Decision tree based on point type and toggle states
                if is_taped_object:
                    # This is a taped object
                    if self.show_taped_objects:
                        # TAPE toggle is ON - show as PURPLE
                        should_draw = True
                        color = QColor(200, 0, 255)
                        size = 12
                    elif self.show_objects:
                        # TAPE toggle OFF, but OBJ toggle ON - show as YELLOW
                        should_draw = True
                        color = QColor(255, 255, 0)
                        size = 10
                    elif self.show_ping:
                        # Both TAPE and OBJ toggles OFF, but PING ON - show as BLUE
                        should_draw = True
                        color = QColor(0, 150, 255)
                        size = 8
                elif is_object:
                    # This is a regular object (not taped)
                    if self.show_objects:
                        # OBJ toggle is ON - show as YELLOW
                        should_draw = True
                        color = QColor(255, 255, 0)
                        size = 10
                    elif self.show_ping:
                        # OBJ toggle OFF, but PING ON - show as BLUE
                        should_draw = True
                        color = QColor(0, 150, 255)
                        size = 8
                else:
                    # This is a normal point (not an object)
                    if self.show_ping:
                        # PING toggle is ON - show as BLUE
                        should_draw = True
                        color = QColor(0, 150, 255)
                        size = 8
                
                # Draw the point if we should
                if should_draw and color:
                    painter.setPen(QPen(color, 3 if size > 8 else 2))
                    painter.setBrush(QBrush(color))
                    half_size = size // 2
                    painter.drawEllipse(int(x - half_size), int(y - half_size), size, size)
                
                # Draw white highlight ring if this point is hovered (regardless of toggle state)
                if is_hovered and should_draw:
                    painter.setPen(QPen(QColor(255, 255, 255), 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(int(x - 10), int(y - 10), 20, 20)
        
        # Draw IR data (RED line and points)
        if self.angles and self.ir_distances and self.show_ir:
            # Draw connecting line for IR
            if len(self.angles) > 1:
                painter.setPen(QPen(QColor(255, 50, 50), 2, Qt.SolidLine))
                for i in range(len(self.angles) - 1):
                    angle1 = self.angles[i]
                    angle2 = self.angles[i + 1]
                    dist1 = self.ir_distances[i]
                    dist2 = self.ir_distances[i + 1]
                    
                    x1 = center_x + (dist1 / self.max_distance) * radius * math.cos(angle1)
                    y1 = center_y - (dist1 / self.max_distance) * radius * math.sin(angle1)
                    x2 = center_x + (dist2 / self.max_distance) * radius * math.cos(angle2)
                    y2 = center_y - (dist2 / self.max_distance) * radius * math.sin(angle2)
                    
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
            # Draw IR points
            for angle, distance in zip(self.angles, self.ir_distances):
                x = center_x + (distance / self.max_distance) * radius * math.cos(angle)
                y = center_y - (distance / self.max_distance) * radius * math.sin(angle)
                
                painter.setPen(QPen(QColor(255, 80, 80), 2))
                painter.setBrush(QBrush(QColor(255, 80, 80)))
                painter.drawEllipse(int(x - 3), int(y - 3), 6, 6)
        
        # Draw object pointer lines (dashed purple lines from robot to objects)
        if self.show_object_lines and (self.object_angles or self.taped_object_angles):
            # Combine all object angles
            all_object_angles = set(self.object_angles + self.taped_object_angles)
            
            # Debug logging
            if all_object_angles:
                print(f"[DEBUG] Drawing lines for {len(all_object_angles)} objects: {sorted(all_object_angles)}")
                print(f"[DEBUG] Scan has {len(self.angles)} angles, {len(self.ping_distances)} distances")
            
            # Draw dashed lines to each object
            for obj_angle_deg in all_object_angles:
                # Convert angle to radians
                obj_angle_rad = math.radians(obj_angle_deg)
                
                # Find the distance at this angle (from PING data)
                obj_distance = None
                matched_angle = None
                for i, angle in enumerate(self.angles):
                    angle_deg = math.degrees(angle)
                    if abs(angle_deg - obj_angle_deg) < 2:  # Within 2 degrees
                        obj_distance = self.ping_distances[i]
                        matched_angle = angle_deg
                        break
                
                if obj_distance:
                    print(f"[DEBUG] Drawing line to object at {obj_angle_deg}° (matched scan angle {matched_angle:.1f}°, dist={obj_distance:.1f}cm)")
                    
                    # Calculate end point of line
                    end_x = center_x + (obj_distance / self.max_distance) * radius * math.cos(obj_angle_rad)
                    end_y = center_y - (obj_distance / self.max_distance) * radius * math.sin(obj_angle_rad)
                    
                    # Determine line color based on object type
                    if obj_angle_deg in self.taped_object_angles:
                        # Taped object - brighter purple
                        line_color = QColor(200, 0, 255)
                        line_width = 3
                    else:
                        # Regular object - medium purple
                        line_color = QColor(150, 0, 200)
                        line_width = 2
                    
                    # Draw dashed line from robot to object
                    painter.setPen(QPen(line_color, line_width, Qt.DashLine))
                    painter.drawLine(int(center_x), int(center_y), int(end_x), int(end_y))
                else:
                    print(f"[DEBUG] Could not find distance for object at {obj_angle_deg}° in scan data")
                
        # Draw center point (robot position)
        painter.setPen(QPen(QColor(255, 255, 0), 2))
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.drawEllipse(int(center_x - 5), int(center_y - 5), 10, 10)
        
        # Draw legend
        painter.setFont(QFont("Courier New", 8, QFont.Bold))
        legend_y = 20
        
        # PING legend
        painter.setPen(QColor(0, 150, 255))
        painter.setBrush(QBrush(QColor(0, 150, 255)))
        painter.drawEllipse(10, legend_y, 8, 8)
        painter.drawText(25, legend_y + 8, "PING")
        
        # IR legend
        legend_y += 15
        painter.setPen(QColor(255, 80, 80))
        painter.setBrush(QBrush(QColor(255, 80, 80)))
        painter.drawEllipse(10, legend_y, 8, 8)
        painter.drawText(25, legend_y + 8, "IR")
        
        # Object legend
        legend_y += 15
        painter.setPen(QColor(255, 255, 0))
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.drawEllipse(10, legend_y, 8, 8)
        painter.drawText(25, legend_y + 8, "OBJECT")
        
        # Taped Object legend
        legend_y += 15
        painter.setPen(QColor(200, 0, 255))
        painter.setBrush(QBrush(QColor(200, 0, 255)))
        painter.drawEllipse(10, legend_y, 8, 8)
        painter.drawText(25, legend_y + 8, "TAPE")
        
        # Object Lines legend
        legend_y += 15
        painter.setPen(QPen(QColor(180, 0, 220), 2, Qt.DashLine))
        painter.drawLine(10, legend_y + 4, 18, legend_y + 4)
        painter.setPen(QColor(180, 0, 220))
        painter.drawText(25, legend_y + 8, "LINES")
        
        # Points count
        legend_y += 20
        painter.setPen(QColor(0, 255, 255))
        status_text = f"Points: {len(self.angles)}"
        painter.drawText(10, legend_y, status_text)
        
        # Draw hover info with background box
        if self.hover_info:
            info_height = 25
            info_width = len(self.hover_info) * 7  # Approximate width based on text length
            info_x = (width - info_width) / 2
            info_y = height - info_height - 10
            
            # Draw semi-transparent background box
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(30, 30, 30, 200)))
            painter.drawRoundedRect(int(info_x - 10), int(info_y - 5), 
                                   int(info_width + 20), int(info_height), 5, 5)
            
            # Draw border
            painter.setPen(QPen(QColor(0, 255, 255), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(int(info_x - 10), int(info_y - 5), 
                                   int(info_width + 20), int(info_height), 5, 5)
            
            # Draw text
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Courier New", 9, QFont.Bold))
            painter.drawText(int(info_x), int(info_y + 12), self.hover_info)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events to detect hover over data points"""
        if not self.angles or not self.ping_distances:
            self.hover_point_index = -1
            self.hover_info = ""
            self.update()
            return
        
        # Get widget dimensions and radar parameters
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20
        
        # Get mouse position
        mouse_x = event.position().x()
        mouse_y = event.position().y()
        
        # Check if mouse is near any data point
        hover_threshold = 10  # pixels
        closest_index = -1
        closest_distance = float('inf')
        
        for i, (angle, ping_dist) in enumerate(zip(self.angles, self.ping_distances)):
            # Calculate point position on radar
            x = center_x + (ping_dist / self.max_distance) * radius * math.cos(angle)
            y = center_y - (ping_dist / self.max_distance) * radius * math.sin(angle)
            
            # Calculate distance from mouse to point
            dx = mouse_x - x
            dy = mouse_y - y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < hover_threshold and dist < closest_distance:
                closest_distance = dist
                closest_index = i
        
        # Update hover information
        if closest_index != -1:
            angle_deg = math.degrees(self.angles[closest_index])
            ping_val = self.ping_distances[closest_index]
            ir_val = self.ir_distances[closest_index] if closest_index < len(self.ir_distances) else ping_val
            
            # Check if this is an object or taped object
            is_object = any(abs(angle_deg - obj_angle) < 2 for obj_angle in self.object_angles)
            is_taped = any(abs(angle_deg - taped_angle) < 2 for taped_angle in self.taped_object_angles)
            
            obj_type = ""
            if is_taped:
                obj_type = " [TAPED]"
            elif is_object:
                obj_type = " [OBJECT]"
            
            self.hover_info = f"Angle: {angle_deg:.1f}° | PING: {ping_val:.2f}cm | IR: {ir_val:.2f}cm{obj_type}"
            self.hover_point_index = closest_index
        else:
            self.hover_info = ""
            self.hover_point_index = -1
        
        self.update()  # Trigger repaint to show hover info
        super().mouseMoveEvent(event)
        

class ScanPanel(QWidget):
    """Widget for scan controls and radar visualization"""

    # Signals
    scan_requested = Signal(str)  # emits single-char command
    scan_data_ready = Signal(list, list)  # angles (rad), distances (cm)
    raw_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._connection_manager = None
        self._logger = None
        self._scan_logger = None
        self._scanning = False
        self._scan_timer = None
        self._current_scan_type = None  # Track which scan is running ('b', 'o', 'k', etc.)
        
        # Live scan data collection - separate for PING and IR
        self.live_scan_angles = []
        self.live_scan_ping_distances = []
        self.live_scan_ir_distances = []
        self.detected_object_angles = []  # Track angles where objects are detected
        self.taped_object_angles = []  # Track angles where objects with tape are detected
        self.radar_widget = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("◈ RECONNAISSANCE & SENSOR CONTROL SYSTEM ◈")
        title.setFont(QFont("Courier New", 11, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_green']}; margin: 8px; background-color: {COLORS['bg_dark']}; padding: 8px; border: 2px solid {COLORS['text_green']}; border-radius: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Create horizontal layout for buttons and radar
        main_layout = QHBoxLayout()
        
        # Left side: Control buttons
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame { 
                background-color: #2a2a2a; 
                border: 2px solid #00ff00; 
                border-radius: 10px; 
                padding: 15px; 
            }
        """)
        control_frame.setMaximumWidth(350)
        
        btn_layout = QVBoxLayout(control_frame)
        
        # Subtitle for controls
        control_title = QLabel("SCAN OPERATIONS")
        control_title.setFont(QFont("Courier New", 9, QFont.Bold))
        control_title.setStyleSheet(f"color: {COLORS['text_green']}; margin-bottom: 5px;")
        control_title.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(control_title)
        
        # Keyboard shortcuts info
        keyboard_info = QLabel("Press Q/E/F Keys")
        keyboard_info.setFont(QFont("Courier New", 8, QFont.Bold))
        keyboard_info.setStyleSheet(f"color: {COLORS['text_cyan']}; margin-bottom: 10px;")
        keyboard_info.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(keyboard_info)
        
        # Button definitions matching scan.h functions with keyboard shortcuts
        btn_map = [
            ("POINT SCAN", 'p', "Scan at specific\nangle (90°)"),
            ("BASIC SCAN (Q)", 'b', "Simple 0-180°\nIR distance scan\nPress Q key"),
            ("OBJECT DETECT (E)", 'o', "Advanced object\ndetection + tape\nPress E key"),
            ("TAPE DETECT (F)", 'k', "Check for tape\nat 90° angle\nPress F key"),
        ]

        button_style = """
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3a5a3a, stop:1 #2a4a2a);
                color: #00ff00; 
                border: 2px solid #00ff00; 
                padding: 12px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 11px; 
                font-family: 'Courier New', monospace;
                text-align: left;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4a7a4a, stop:1 #3a6a3a);
                border: 2px solid #00ffff;
                color: #00ffff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a4a2a, stop:1 #1a3a1a);
            }
        """

        for text, cmd, tooltip in btn_map:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda _, x=cmd: self._handle_scan_request(x))
            btn.setStyleSheet(button_style)
            btn.setMinimumHeight(50)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton("🗑️ CLEAR RADAR")
        clear_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4a2a2a; 
                color: #ff4444; 
                border: 2px solid #ff4444; 
                padding: 10px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 10px; 
                font-family: 'Courier New', monospace;
            }
            QPushButton:hover { 
                background-color: #6a3a3a; 
                border: 2px solid #ff6666;
            }
        """)
        clear_btn.clicked.connect(self.clear_live_scan)
        btn_layout.addWidget(clear_btn)

        main_layout.addWidget(control_frame)
        
        # Right side: Radar display
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
        
        # Radar title
        radar_title = QLabel("🎯 RADAR DISPLAY")
        radar_title.setFont(QFont("Courier New", 9, QFont.Bold))
        radar_title.setStyleSheet(f"color: {COLORS['text_green']}; margin-bottom: 5px;")
        radar_title.setAlignment(Qt.AlignCenter)
        radar_layout.addWidget(radar_title)
        
        # Radar widget
        self.radar_widget = RadarWidget()
        radar_layout.addWidget(self.radar_widget)
        
        # Toggle controls for radar layers
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setSpacing(8)
        
        # Toggle label
        toggle_label = QLabel("Display:")
        toggle_label.setFont(QFont("Courier New", 8, QFont.Bold))
        toggle_label.setStyleSheet(f"color: {COLORS['text_green']}; border: none;")
        toggle_layout.addWidget(toggle_label)
        
        # Create toggle buttons
        self.ping_checkbox = QCheckBox("PING")
        self.ping_checkbox.setChecked(True)
        self.ping_checkbox.setStyleSheet("""
            QCheckBox {
                color: #0096ff;
                font-family: 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #0096ff;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #0096ff;
            }
        """)
        self.ping_checkbox.stateChanged.connect(lambda state: self.radar_widget.toggle_ping(state == 2))
        toggle_layout.addWidget(self.ping_checkbox)
        
        self.ir_checkbox = QCheckBox("IR")
        self.ir_checkbox.setChecked(True)
        self.ir_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ff5050;
                font-family: 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #ff5050;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #ff5050;
            }
        """)
        self.ir_checkbox.stateChanged.connect(lambda state: self.radar_widget.toggle_ir(state == 2))
        toggle_layout.addWidget(self.ir_checkbox)
        
        self.object_checkbox = QCheckBox("OBJ")
        self.object_checkbox.setChecked(True)
        self.object_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffff00;
                font-family: 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #ffff00;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #ffff00;
            }
        """)
        self.object_checkbox.stateChanged.connect(lambda state: self.radar_widget.toggle_objects(state == 2))
        toggle_layout.addWidget(self.object_checkbox)
        
        self.tape_checkbox = QCheckBox("TAPE")
        self.tape_checkbox.setChecked(True)
        self.tape_checkbox.setStyleSheet("""
            QCheckBox {
                color: #c800ff;
                font-family: 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #c800ff;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #c800ff;
            }
        """)
        self.tape_checkbox.stateChanged.connect(lambda state: self.radar_widget.toggle_taped_objects(state == 2))
        toggle_layout.addWidget(self.tape_checkbox)
        
        self.lines_checkbox = QCheckBox("LINES")
        self.lines_checkbox.setChecked(True)
        self.lines_checkbox.setStyleSheet("""
            QCheckBox {
                color: #b400dc;
                font-family: 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #b400dc;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #b400dc;
            }
        """)
        self.lines_checkbox.stateChanged.connect(lambda state: self.radar_widget.toggle_object_lines(state == 2))
        toggle_layout.addWidget(self.lines_checkbox)
        
        toggle_layout.addStretch()
        radar_layout.addWidget(toggle_frame)
        
        # Radar info label
        self.radar_info = QLabel("Awaiting scan data...")
        self.radar_info.setFont(QFont("Courier New", 8))
        self.radar_info.setStyleSheet(f"color: {COLORS['text_green']}; padding: 5px;")
        self.radar_info.setAlignment(Qt.AlignCenter)
        radar_layout.addWidget(self.radar_info)
        
        main_layout.addWidget(radar_frame, 1)  # Give radar more space
        
        layout.addLayout(main_layout)

    def _handle_scan_request(self, cmd):
        """Handle scan button press"""
        self.scan_requested.emit(cmd)
        # Start the scan collection
        self.start_scan(cmd)

    def set_connection_manager(self, cm):
        """Attach a ConnectionManager to receive messages."""
        if self._connection_manager:
            try:
                self._connection_manager.message_received.disconnect(self._on_message)
            except Exception:
                pass
        self._connection_manager = cm
        if cm:
            cm.message_received.connect(self._on_message)

    def set_loggers(self, logger_callable, scan_logger_callable):
        """Provide logging callables."""
        self._logger = logger_callable
        self._scan_logger = scan_logger_callable

    def start_scan(self, cmd):
        """Initiate a scan: send command and collect incoming messages."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("✗ ERROR: No connection established for scan")
            return

    def start_scan(self, cmd):
        """Initiate a scan: send command and collect incoming messages."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("✗ ERROR: No connection established for scan")
            return

        # Determine timeout based on command (extract base command for multi-char commands)
        base_cmd = cmd[0] if cmd else cmd  # Extract first character for commands like 'k90'
        timeout_map = {
            'o': 15,  # Object detect
            'p': 3,   # Point scan
            'b': 12,  # Basic scan
            'k': 15,  # Tape detect (longer timeout for multiple objects)
        }
        timeout = timeout_map.get(base_cmd, 5)

        # Reset live buffers (but preserve scan data for tape detect)
        # Tape detect (cmd 'k') keeps both scan data AND object angles from previous object detect
        # It only updates which objects have tape
        if base_cmd != 'k':
            # For non-tape-detect commands, clear everything
            self.live_scan_angles = []
            self.live_scan_ping_distances = []
            self.live_scan_ir_distances = []
            self.detected_object_angles = []
            self.taped_object_angles = []
        else:
            # For tape detect, keep scan data and object angles, only reset tape flags
            # This preserves the background scan from object detect
            self.taped_object_angles = []
            print("[DEBUG] Tape detect: Preserving scan data and object angles from previous scan")
        
        self._scanning = True
        self._current_scan_type = base_cmd  # Track which scan command is running (base command)
        
        # Clear radar display
        if self.radar_widget:
            self.radar_widget.clear_scan()
        
        # Update radar info
        self.radar_info.setText(f"Scanning... ({cmd.upper()} command)")

        # Start timer to end scan
        if self._scan_timer:
            try:
                self._scan_timer.stop()
            except Exception:
                pass
        self._scan_timer = QTimer()
        self._scan_timer.setSingleShot(True)
        self._scan_timer.timeout.connect(self._finish_scan)
        self._scan_timer.start(timeout * 1000)

        # Send command
        self._connection_manager.send_command(cmd, wait_for_response=False)
        if self._scan_logger:
            self._scan_logger(f"╔══ {cmd.upper()} SCAN INITIATED (timeout={timeout}s) ══╗")

    def _finish_scan(self):
        """Complete the scan and update display"""
        self._scanning = False
        
        # Update radar info
        point_count = len(self.live_scan_angles)
        if point_count > 0:
            self.radar_info.setText(f"✓ Scan complete: {point_count} points detected")
        else:
            self.radar_info.setText("⚠ Scan complete: No data received")
        
        # Emit final collected data (PING distances)
        try:
            self.scan_data_ready.emit(self.live_scan_angles.copy(), self.live_scan_ping_distances.copy())
        except Exception:
            pass
            
        if self._scan_logger:
            self._scan_logger(f"✓ SCAN COMPLETE: {point_count} points collected")

    def _on_message(self, message):
        """Handle incoming messages from ConnectionManager."""
        try:
            self.raw_message.emit(message)
        except Exception:
            pass

        if not self._scanning:
            return

        try:
            self.parse_and_log_scan_data(message, collect_for_plot=True, 
                                        logger=self._logger, scan_logger=self._scan_logger)
        except Exception:
            if self._logger:
                self._logger(f"✗ parse error for message: {message}")

    def parse_and_log_scan_data(self, response, collect_for_plot=False, logger=None, scan_logger=None):
        """Parse sensor response strings and optionally collect plot data with tape detection."""
        try:
            # Handle basic scan start
            if "BASIC_SCAN_START" in response:
                if scan_logger:
                    scan_logger(f"📡 {response}")
                return
            
            # Handle exit scan start - CLEAR RADAR for quick scans during auto exit
            if "EXIT_SCAN_START" in response:
                # Clear previous scan data for fresh quick scan display
                self.live_scan_angles = []
                self.live_scan_ping_distances = []
                self.live_scan_ir_distances = []
                
                # Set scan type to 'q' for quick scan
                self._current_scan_type = 'q'
                
                # Immediately clear the radar display
                if self.radar_widget:
                    self.radar_widget.clear_scan()
                    self.radar_info.setText("🚪 Quick scan starting (46°-134°)...")
                
                if scan_logger:
                    scan_logger(f"🚪 {response} - Quick scan (46°-134°)")
                return
            
            # Handle exit scan completion
            if "EXIT_SCAN_COMPLETE" in response:
                # Reset scan type after quick scan completes
                self._current_scan_type = None
                
                if scan_logger:
                    scan_logger(f"✅ {response} - Quick scan finished")
                return
            
            # Handle basic scan data cleaning
            if "CLEANING_SCAN_DATA" in response:
                if scan_logger:
                    scan_logger(f"🧹 {response} - Removing noise and smoothing...")
                return
            
            # Handle basic scan completion
            if "BASIC_SCAN_COMPLETE" in response:
                if scan_logger:
                    scan_logger(f"✅ {response}")
                return
            
            # Clear detected objects when a new object detection scan starts
            if "OBJECT_DETECT_START" in response:
                self.detected_object_angles = []
                self.taped_object_angles = []
                if scan_logger:
                    scan_logger(f"🎯 {response}")
                return
            
            # Clear tape angles when tape detect starts (but keep object angles)
            if "TAPE_DETECT_START" in response:
                self.taped_object_angles = []
                if scan_logger:
                    scan_logger(f"🎗️ {response}")
                return
            
            # Log scan completion
            if "OBJECT_DETECT_COMPLETE" in response:
                if scan_logger:
                    scan_logger(f"✅ {response}")
                return
            
            if "PING=" in response and "IR=" in response:
                parts = response.split()
                direction = parts[0].replace(":", "")
                ping_val = None
                ir_val = None
                angle_deg = None
                has_tape = 0

                if direction.startswith("ANGLE="):
                    try:
                        angle_deg = float(direction.split("=")[1])
                    except ValueError:
                        angle_deg = None
                elif direction == "LEFT":
                    angle_deg = 100.0
                elif direction in ("FORWARD", "CENTER"):
                    angle_deg = 90.0
                elif direction == "RIGHT":
                    angle_deg = 80.0

                for part in parts:
                    if part.startswith("PING="):
                        try:
                            ping_val = float(part.split("=")[1])
                        except ValueError:
                            ping_val = None
                    elif part.startswith("IR="):
                        try:
                            ir_val = float(part.split("=")[1])
                        except ValueError:
                            ir_val = None
                    elif part.startswith("TAPE="):
                        try:
                            has_tape = int(part.split("=")[1])
                        except ValueError:
                            has_tape = 0

                if ping_val is not None and ir_val is not None:
                    distance = ping_val
                    if collect_for_plot and angle_deg is not None:
                        # For tape detect ('k'), add the scan point to show the object dot on radar
                        # For other scans, add normal scan points
                        if self._current_scan_type == 'k':
                            # Tape detect: add this single point to show object on radar
                            print(f"[DEBUG] Tape detect: Adding scan point at {angle_deg}° for radar display")
                            # Don't add to main scan arrays, but ensure object is marked
                        else:
                            # Normal scan modes: add scan points for background
                            self.live_scan_angles.append(np.radians(angle_deg))
                            self.live_scan_ping_distances.append(distance)
                            self.live_scan_ir_distances.append(ir_val)
                        
                        # Mark objects during object detection ('o') or tape detection ('k') scans
                        # Do NOT mark objects during basic scans ('b')
                        if self._current_scan_type in ['o', 'k']:
                            # If PING distance is different from IR, OR if explicit TAPE marker, this is a detected object
                            is_object_by_distance = abs(ping_val - ir_val) > 5.0  # 5cm threshold
                            
                            # Also treat as object if we have TAPE data (tape detect command)
                            if is_object_by_distance or has_tape or self._current_scan_type == 'k':
                                if angle_deg not in self.detected_object_angles:
                                    self.detected_object_angles.append(angle_deg)
                                    print(f"[DEBUG] Adding object at {angle_deg}° (from PING/IR data)")
                                
                                # If object has tape, also add to taped_object_angles
                                if has_tape:
                                    if angle_deg not in self.taped_object_angles:
                                        self.taped_object_angles.append(angle_deg)
                                        print(f"[DEBUG] Marking object at {angle_deg}° as TAPED")
                        
                        # Update radar display in real-time with both PING and IR data
                        if self.radar_widget:
                            # For tape detection, we want to preserve existing scan background
                            # but add the new object marker
                            if self._current_scan_type == 'k':
                                # Update radar with preserved background data plus new object markers
                                self.radar_widget.update_scan_data(self.live_scan_angles, 
                                                                  self.live_scan_ping_distances,
                                                                  self.live_scan_ir_distances,
                                                                  self.detected_object_angles,
                                                                  self.taped_object_angles)
                            else:
                                # Normal scan update
                                self.radar_widget.update_scan_data(self.live_scan_angles, 
                                                                  self.live_scan_ping_distances,
                                                                  self.live_scan_ir_distances,
                                                                  self.detected_object_angles,
                                                                  self.taped_object_angles)
                            
                            objects_count = len(self.detected_object_angles)
                            taped_count = len(self.taped_object_angles)
                            if self._current_scan_type == 'k':
                                self.radar_info.setText(f"📡 Tape Check: {len(self.live_scan_angles)} points | Objects: {objects_count} | Taped: {taped_count}")
                            elif self._current_scan_type == 'q':
                                self.radar_info.setText(f"🚪 Quick Scan: {len(self.live_scan_angles)} points (46°-134°)")
                            else:
                                self.radar_info.setText(f"📡 Collecting: {len(self.live_scan_angles)} points | Objects: {objects_count} | Taped: {taped_count}")
                        
                        if scan_logger:
                            # Only show object markers if we're in object/tape detection mode
                            obj_marker = ""
                            tape_marker = ""
                            if self._current_scan_type in ['o', 'k']:
                                is_obj = abs(ping_val - ir_val) > 5.0 or has_tape
                                obj_marker = " 🎯" if is_obj else ""
                                tape_marker = " 🎗️" if has_tape else ""
                            scan_logger(f"📍 PLOT DATA: angle={angle_deg:.1f}° PING={ping_val:.1f}cm IR={ir_val:.1f}cm{obj_marker}{tape_marker}")
                        
                        # Only emit scan data updates for non-tape-detect scans
                        if self._current_scan_type != 'k':
                            try:
                                self.scan_data_ready.emit(self.live_scan_angles.copy(), 
                                                         self.live_scan_ping_distances.copy())
                            except Exception:
                                pass

                    ping_status = "CLEAR" if ping_val > 30 else "OBSTACLE" if ping_val > 10 else "BLOCKED"
                    ir_status = "CLEAR" if ir_val > 40 else "OBJECT" if ir_val > 15 else "CLOSE"
                    angle_info = f" @{angle_deg:3.0f}°" if angle_deg is not None else ""
                    msg = f"📊 {direction:>8}{angle_info}: PING={ping_val:5.1f}cm [{ping_status:>8}] | IR={ir_val:5.1f}cm [{ir_status:>6}]"
                    if scan_logger:
                        scan_logger(msg)
                    return
            
            # Check for object detection messages
            elif "OBJECT_" in response or "OBJ_" in response:
                # Parse object detection: OBJECT_0: ANGLE=90 WIDTH=10deg ...
                if scan_logger:
                    scan_logger(f"🎯 {response}")
                
                # Extract angle from object detection
                try:
                    if "Angle=" in response:  # Match C code format: "Angle=97 deg"
                        angle_str = response.split("Angle=")[1].split()[0]
                        obj_angle = float(angle_str)
                        
                        # Check if this object has tape
                        has_tape = "Tape=YES" in response
                        
                        print(f"[DEBUG] Parsed object: angle={obj_angle}°, has_tape={has_tape}")
                        
                        if obj_angle not in self.detected_object_angles:
                            self.detected_object_angles.append(obj_angle)
                            print(f"[DEBUG] Added to detected_object_angles: {self.detected_object_angles}")
                        
                        # If object has tape, add to taped_object_angles
                        if has_tape and obj_angle not in self.taped_object_angles:
                            self.taped_object_angles.append(obj_angle)
                            print(f"[DEBUG] Added to taped_object_angles: {self.taped_object_angles}")
                        
                        # Update radar with object markers
                        if self.radar_widget:
                            print(f"[DEBUG] Updating radar widget with {len(self.detected_object_angles)} objects, {len(self.taped_object_angles)} taped")
                            self.radar_widget.update_scan_data(
                                self.live_scan_angles,
                                self.live_scan_ping_distances,
                                self.live_scan_ir_distances,
                                self.detected_object_angles,
                                self.taped_object_angles
                            )
                            # Update info display
                            objects_count = len(self.detected_object_angles)
                            taped_count = len(self.taped_object_angles)
                            self.radar_info.setText(f"📡 Objects: {objects_count} | Taped: {taped_count}")
                except Exception as e:
                    if logger:
                        logger(f"Error parsing OBJ message: {e}")
                    print(f"[DEBUG] Exception parsing OBJ message: {e}")
                return
            
            elif "OBJECTS_DETECTED:" in response or "DETECTED_OBJECTS:" in response:
                if scan_logger:
                    scan_logger(f"🎯 {response}")
                return
            
            # Check for tape detection results
            elif "TAPE_RESULT:" in response:
                # Parse: TAPE_RESULT: ANGLE=90 PING=45.2 IR=42.1 STATUS=TAPE_DETECTED
                if scan_logger:
                    if "TAPE_DETECTED" in response:
                        scan_logger(f"🎗️ {response} ✓")
                    else:
                        scan_logger(f"🎗️ {response} ✗")
                return
            
            elif "TAPE_DETECT_START" in response or "TAPE_DETECT_COMPLETE" in response:
                if scan_logger:
                    scan_logger(f"🎗️ {response}")
                return

            # Fallback generic log
            if scan_logger:
                scan_logger(f"📡 {response}")
        except Exception as e:
            if scan_logger:
                scan_logger(f"📡 {response}")
            if logger:
                logger(f"✗ parse error: {e}")

    def clear_live_scan(self):
        """Clear live scan buffers and radar display."""
        self.live_scan_angles = []
        self.live_scan_ping_distances = []
        self.live_scan_ir_distances = []
        self.detected_object_angles = []
        self.taped_object_angles = []
        if self.radar_widget:
            self.radar_widget.clear_scan()
            self.radar_info.setText("Radar cleared - awaiting new scan data...")
        if self._scan_logger:
            self._scan_logger("Radar display cleared")

    def basic_scan(self, ir_data_func, num_points=91):
        """Scan from 0 to 180 degrees."""
        data = np.zeros(num_points)
        for i in range(num_points):
            angle = i * 2
            ir_val = ir_data_func(angle)
            data[i] = ir_val / 100.0
        return data

    def clean_scan_data(self, data):
        """Smooth scan data to remove spikes/noise."""
        cleaned = data.copy()
        for k in range(1, len(data) - 1):
            if k <= 2:
                cleaned[k - 1] = cleaned[k + 1]
            elif (abs(cleaned[k] - cleaned[k + 1]) > 0.10 and
                  abs(cleaned[k] - cleaned[k - 1]) > 0.10 and
                  abs(cleaned[k + 1] - cleaned[k - 1]) < 0.10):
                cleaned[k] = (cleaned[k + 1] + cleaned[k - 1]) / 2.0
        return cleaned

    def point_scan(self, angle, ir_data_func, ping_data_func):
        """Get IR and ping values at a specific angle."""
        ir_val = ir_data_func(angle)
        ir_dist = ir_val / 100.0
        ping_val = ping_data_func(angle)
        return ir_dist, ping_val

    def getLinWidth(self, degrees, dist):
        """Calculate linear width from angle and distance."""
        return 2 * dist * np.sin(np.pi * degrees / 360)

    def is_taped(self, ir_val, ping_dist, convert_ir_taped, convert_ir_normal):
        """Detect if object has tape based on IR and ping values."""
        taped_dist = convert_ir_taped(ir_val)
        norm_dist = convert_ir_normal(ir_val)
        ping_to_tape = abs(ping_dist - taped_dist)
        ping_to_norm = abs(ping_dist - norm_dist)
        return int((ping_to_norm - ping_to_tape) > 0)

    def detect_Obj(self, data, ir_data_func, ping_data_func):
        """Detect objects from scan data."""
        objects = []
        i = 0
        while i < len(data):
            if data[i] < 1.0:
                rEdge = i * 2
                redgeDist = data[i]
                while i < len(data) and abs(redgeDist - data[i]) < 0.18:
                    i += 1
                lEdge = (i - 1) * 2
                angle = (lEdge + rEdge) / 2
                width = lEdge - rEdge
                if width > 0:
                    irVal, distance = self.point_scan(angle, ir_data_func, ping_data_func)
                    irVal, distance = self.point_scan(angle, ir_data_func, ping_data_func)
                    obj = {
                        'angle': angle,
                        'width': width,
                        'irVal': irVal,
                        'distance': distance
                    }
                    objects.append(obj)
            i += 1
        return objects