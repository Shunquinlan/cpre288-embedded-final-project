"""Unbounded movement map visualization panel"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame, QPushButton)
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils import COLORS
import numpy as np


class MapWindow(QMainWindow):
    """Separate window for viewing the map independently"""
    
    # Signal emitted when window is closed
    window_closed = Signal()
    
    def __init__(self, parent_map_panel, parent=None):
        super().__init__(parent)
        self.parent_map_panel = parent_map_panel
        self.init_ui()
        
    def init_ui(self):
        """Initialize the map window UI"""
        self.setWindowTitle("CyBot Movement Map - External View")
        self.setGeometry(150, 150, 1400, 800)
        
        # Apply dark theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure (fullscreen)
        self.fig, self.ax = plt.subplots(figsize=(20, 12), facecolor='#1a1a1a')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("""
            FigureCanvas {
                background-color: #1a1a1a;
            }
        """)
        layout.addWidget(self.canvas)
        
        # Create overlay widget for controls (absolute positioning)
        overlay_widget = QWidget(central)
        overlay_widget.setAttribute(Qt.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay_widget)
        overlay_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header at top with title and close button
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 61, 31, 200);
                border: 2px solid #4a5c23;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("CYBOT MOVEMENT MAP - EXTERNAL VIEW")
        title.setFont(QFont("Courier New", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_green']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✖ Close Window")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #5c2323;
                color: {COLORS['text_green']};
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #6c2828;
                color: #ffffff;
            }}
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        overlay_layout.addWidget(header_frame)
        overlay_layout.addStretch()  # Push status bar to bottom
        
        # Status bar at bottom
        self.status_label = QLabel("Connected to main map panel - updates in real-time")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_green']};
                font-weight: bold;
                padding: 10px 15px;
                background-color: rgba(45, 61, 31, 200);
                border: 2px solid #4a5c23;
                border-radius: 8px;
                font-size: 11px;
            }}
        """)
        overlay_layout.addWidget(self.status_label)
        
        # Position overlay widget to fill parent
        overlay_widget.setGeometry(0, 0, central.width(), central.height())
        self.overlay_widget = overlay_widget  # Keep reference for resize
        
        # Initial draw
        self.update_map()
        
    def resizeEvent(self, event):
        """Handle resize to reposition overlay"""
        super().resizeEvent(event)
        if hasattr(self, 'overlay_widget'):
            central = self.centralWidget()
            if central:
                self.overlay_widget.setGeometry(0, 0, central.width(), central.height())

    def update_map(self):
        """Update this window's map with data from parent panel"""
        if not self.parent_map_panel:
            return
            
        self.ax.clear()
        
        # Get data from parent panel
        robot_x = self.parent_map_panel.robot_x
        robot_y = self.parent_map_panel.robot_y
        robot_angle = self.parent_map_panel.robot_angle
        movement_trail = self.parent_map_panel.movement_trail
        border_locations = self.parent_map_panel.border_locations
        bump_locations = self.parent_map_panel.bump_locations
        
        # Calculate view bounds
        if len(movement_trail) > 0:
            all_x = [pos[0] for pos in movement_trail]
            all_y = [pos[1] for pos in movement_trail]
            
            if len(border_locations) > 0:
                all_x.extend([pos[0] for pos in border_locations])
                all_y.extend([pos[1] for pos in border_locations])
            
            if len(bump_locations) > 0:
                all_x.extend([pos[0] for pos in bump_locations])
                all_y.extend([pos[1] for pos in bump_locations])
            
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            
            padding = max(2, (max_x - min_x) * 0.2, (max_y - min_y) * 0.2)
            min_x -= padding
            max_x += padding
            min_y -= padding
            max_y += padding
            
            if max_x - min_x < 5:
                center_x = (max_x + min_x) / 2
                min_x = center_x - 2.5
                max_x = center_x + 2.5
            if max_y - min_y < 5:
                center_y = (max_y + min_y) / 2
                min_y = center_y - 2.5
                max_y = center_y + 2.5
        else:
            min_x, max_x = -2.5, 2.5
            min_y, max_y = -2.5, 2.5
        
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)
        self.ax.set_aspect('equal')
        
        # Draw origin
        self.ax.plot(0, 0, 'w+', markersize=15, markeredgewidth=2, 
                    label='Origin (0,0)', alpha=0.5, zorder=1)
        
        # Draw axes
        self.ax.axhline(0, color='#4a5c23', linewidth=1.5, alpha=0.7, linestyle='--')
        self.ax.axvline(0, color='#4a5c23', linewidth=1.5, alpha=0.7, linestyle='--')
        self.ax.grid(True, color='#4a5c23', alpha=0.3, linestyle=':')
        
        # Draw trail
        if len(movement_trail) > 1:
            trail_x = [pos[0] for pos in movement_trail]
            trail_y = [pos[1] for pos in movement_trail]
            self.ax.plot(trail_x, trail_y, 'g-', linewidth=2, alpha=0.6, label='Movement Trail')
            
            step = max(1, len(movement_trail) // 20)
            for i in range(0, len(movement_trail) - 1, step):
                x, y = movement_trail[i]
                self.ax.plot(x, y, 'go', markersize=6, alpha=0.5)
                self.ax.text(x + 0.1, y + 0.1, str(i + 1), color='#00ff00', 
                           fontsize=7, weight='bold')
        
        # Draw robot - brown color
        angle_rad = np.radians(robot_angle)
        arrow_length = 0.5
        dx = arrow_length * np.cos(angle_rad)
        dy = arrow_length * np.sin(angle_rad)
        
        self.ax.plot(robot_x, robot_y, 'o', markersize=15, color='#8B4513',
                    label='Current Position', zorder=5)
        self.ax.arrow(robot_x, robot_y, dx, dy, 
                     head_width=0.3, head_length=0.2, fc='#8B4513', ec='#8B4513', 
                     linewidth=2, zorder=6)
        
        # Draw borders with X markers
        if len(border_locations) > 0:
            border_x = [loc[0] for loc in border_locations]
            border_y = [loc[1] for loc in border_locations]
            
            # Draw red X markers for each border detection
            self.ax.scatter(border_x, border_y, marker='x', s=200, linewidths=3,
                           color='red', label='Border Detected', alpha=0.9, zorder=4)
            
            # Draw connecting lines if multiple borders detected
            if len(border_locations) > 1:
                self.ax.plot(border_x, border_y, 'r--', linewidth=1.5, 
                           alpha=0.4, zorder=2)
        
        # Draw bumps with triangle markers
        if len(bump_locations) > 0:
            bump_x = [loc[0] for loc in bump_locations]
            bump_y = [loc[1] for loc in bump_locations]
            
            # Draw magenta triangle markers for each bump detection
            self.ax.scatter(bump_x, bump_y, marker='^', s=250, linewidths=2,
                           color='magenta', edgecolors='darkmagenta', label='Bump Detected', alpha=0.9, zorder=4)
            
            # Draw connecting lines if multiple bumps detected
            if len(bump_locations) > 1:
                self.ax.plot(bump_x, bump_y, 'm--', linewidth=1.5, 
                           alpha=0.4, zorder=2)
        
        # Labels and styling
        self.ax.set_title("CYBOT MOVEMENT MAPPING - EXTERNAL VIEW", 
                         color='#00ff00', fontsize=16, pad=20)
        self.ax.set_facecolor('#0a0a0a')
        self.ax.set_xlabel('X Coordinate', color='#00ff00', fontsize=12)
        self.ax.set_ylabel('Y Coordinate', color='#00ff00', fontsize=12)
        self.ax.tick_params(colors='#00ff00')
        self.ax.legend(loc='upper right', facecolor='#2d3d1f', edgecolor='#4a5c23', 
                      labelcolor='#00ff00', fontsize=10)
        
        # Update status
        total_dist = 0
        for i in range(1, len(movement_trail)):
            x1, y1 = movement_trail[i-1]
            x2, y2 = movement_trail[i]
            total_dist += np.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        self.status_label.setText(
            f"Position: ({robot_x:.1f}, {robot_y:.1f}) | "
            f"Angle: {robot_angle}° | "
            f"Trail: {len(movement_trail)} points | "
            f"Distance: {total_dist:.1f} units | "
            f"Borders: {len(border_locations)} | "
            f"Bumps: {len(bump_locations)}"
        )
        
        # Use tight layout to maximize map area
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()
        
    def closeEvent(self, event):
        """Override close event to emit signal"""
        self.window_closed.emit()
        super().closeEvent(event)


class MapPanel(QWidget):
    """Unbounded movement map with trail and orientation tracking"""
    
    def __init__(self):
        super().__init__()
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_angle = 90  # 90=Up, 0=Right, 180=Left, 270=Down
        self.movement_trail = [(self.robot_x, self.robot_y)]
        self.border_locations = []
        self.bump_locations = []  # Track bump detections separately
        self.map_window = None  # Reference to external map window
        self.init_ui()

    def init_ui(self):
        # Use absolute positioning to overlay controls on the canvas
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure (fullscreen)
        self.fig, self.ax = plt.subplots(figsize=(16, 9), facecolor='#1a1a1a')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("""
            FigureCanvas {
                background-color: #1a1a1a;
            }
        """)
        layout.addWidget(self.canvas)
        
        # Create overlay widget for controls (absolute positioning)
        overlay_widget = QWidget(self)
        overlay_widget.setAttribute(Qt.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay_widget)
        overlay_layout.setContentsMargins(15, 15, 15, 15)
        overlay_layout.addStretch()  # Push controls to bottom
        
        # Control buttons frame (semi-transparent, at bottom)
        map_control_frame = QFrame()
        map_control_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 61, 31, 200);
                border: 2px solid #4a5c23;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        map_control_layout = QHBoxLayout(map_control_frame)
        
        # Open External Map Window button
        self.open_map_btn = QPushButton("OPEN MAP WINDOW 🗗")
        self.open_map_btn.clicked.connect(self.open_map_window)
        self.open_map_btn.setStyleSheet("""
            QPushButton {
                background-color: #234a5c;
                font-size: 12px;
                min-width: 180px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #285c6c;
            }
        """)
        map_control_layout.addWidget(self.open_map_btn)
        
        self.reset_position_btn = QPushButton("RESET POSITION")
        self.reset_position_btn.clicked.connect(self.reset_robot_position)
        self.reset_position_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5c23;
                font-size: 12px;
                min-width: 150px;
                padding: 10px;
            }
        """)
        map_control_layout.addWidget(self.reset_position_btn)
        
        self.clear_trail_btn = QPushButton("CLEAR TRAIL")
        self.clear_trail_btn.clicked.connect(self.clear_movement_trail)
        self.clear_trail_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c2323;
                font-size: 12px;
                min-width: 120px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6c2828;
            }
        """)
        map_control_layout.addWidget(self.clear_trail_btn)
        
        self.clear_borders_btn = QPushButton("CLEAR BORDERS")
        self.clear_borders_btn.clicked.connect(self.clear_border_locations)
        self.clear_borders_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c4a23;
                font-size: 12px;
                min-width: 120px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6c5a28;
            }
        """)
        map_control_layout.addWidget(self.clear_borders_btn)
        
        self.clear_bumps_btn = QPushButton("CLEAR BUMPS")
        self.clear_bumps_btn.clicked.connect(self.clear_bump_locations)
        self.clear_bumps_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c234a;
                font-size: 12px;
                min-width: 120px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6c285a;
            }
        """)
        map_control_layout.addWidget(self.clear_bumps_btn)
        
        self.position_label = QLabel(f"POSITION: ({self.robot_x:.1f}, {self.robot_y:.1f})")
        self.position_label.setStyleSheet("""
            QLabel {
                color: #ffff00;
                font-weight: bold;
                padding: 8px;
                background-color: #3d3d1f;
                border: 1px solid #5c5c23;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        map_control_layout.addWidget(self.position_label)

        self.angle_label = QLabel(f"ANGLE: {self.robot_angle}°")
        self.angle_label.setStyleSheet("""
            QLabel {
                color: #00ffcc;
                font-weight: bold;
                padding: 8px;
                background-color: #1f3d3d;
                border: 1px solid #235c5c;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        map_control_layout.addWidget(self.angle_label)
        
        map_control_layout.addStretch()
        
        # Add control frame to overlay
        overlay_layout.addWidget(map_control_frame)
        
        # Position overlay widget to fill parent
        overlay_widget.setGeometry(0, 0, self.width(), self.height())
        
        # Stats label (also in overlay, below controls)
        self.movement_stats_label = QLabel("MOVEMENT STATS: 0 moves | Trail length: 1 | Distance: 0.0")
        self.movement_stats_label.setStyleSheet("""
            QLabel {
                color: #ffff00;
                font-weight: bold;
                padding: 6px 12px;
                background-color: rgba(61, 61, 31, 200);
                border: 1px solid #5c5c23;
                border-radius: 4px;
                font-size: 10px;
            }
        """)
        overlay_layout.addWidget(self.movement_stats_label)
        
        self.setup_movement_grid()
    
    def resizeEvent(self, event):
        """Handle resize to reposition overlay"""
        super().resizeEvent(event)
        # Find overlay widget and resize it
        for child in self.findChildren(QWidget):
            if child.testAttribute(Qt.WA_TranslucentBackground):
                child.setGeometry(0, 0, self.width(), self.height())
                break

    def setup_movement_grid(self):
        """Setup the unbounded movement visualization"""
        self.ax.clear()
        
        # Calculate view bounds based on movement trail
        if len(self.movement_trail) > 0:
            all_x = [pos[0] for pos in self.movement_trail]
            all_y = [pos[1] for pos in self.movement_trail]
            
            # Add border locations to bounds calculation
            if len(self.border_locations) > 0:
                all_x.extend([pos[0] for pos in self.border_locations])
                all_y.extend([pos[1] for pos in self.border_locations])
            
            # Add bump locations to bounds calculation
            if len(self.bump_locations) > 0:
                all_x.extend([pos[0] for pos in self.bump_locations])
                all_y.extend([pos[1] for pos in self.bump_locations])
            
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            
            # Add padding
            padding = max(2, (max_x - min_x) * 0.2, (max_y - min_y) * 0.2)
            min_x -= padding
            max_x += padding
            min_y -= padding
            max_y += padding
            
            # Ensure minimum view size
            if max_x - min_x < 5:
                center_x = (max_x + min_x) / 2
                min_x = center_x - 2.5
                max_x = center_x + 2.5
            if max_y - min_y < 5:
                center_y = (max_y + min_y) / 2
                min_y = center_y - 2.5
                max_y = center_y + 2.5
        else:
            min_x, max_x = -2.5, 2.5
            min_y, max_y = -2.5, 2.5
        
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)
        self.ax.set_aspect('equal')
        
        # Draw origin
        self.ax.plot(0, 0, 'w+', markersize=15, markeredgewidth=2, 
                    label='Origin (0,0)', alpha=0.5, zorder=1)
        
        # Draw axes through origin
        self.ax.axhline(0, color='#4a5c23', linewidth=1.5, alpha=0.7, linestyle='--')
        self.ax.axvline(0, color='#4a5c23', linewidth=1.5, alpha=0.7, linestyle='--')
        
        # Draw grid
        self.ax.grid(True, color='#4a5c23', alpha=0.3, linestyle=':')
        
        # Trail
        if len(self.movement_trail) > 1:
            trail_x = [pos[0] for pos in self.movement_trail]
            trail_y = [pos[1] for pos in self.movement_trail]
            self.ax.plot(trail_x, trail_y, 'g-', linewidth=2, alpha=0.6, label='Movement Trail')
            
            # Draw numbered waypoints (show every nth point if too many)
            step = max(1, len(self.movement_trail) // 20)
            for i in range(0, len(self.movement_trail) - 1, step):
                x, y = self.movement_trail[i]
                self.ax.plot(x, y, 'go', markersize=6, alpha=0.5)
                self.ax.text(x + 0.1, y + 0.1, str(i + 1), color='#00ff00', 
                           fontsize=7, weight='bold')
        
        # Robot current position with orientation - brown color
        angle_rad = np.radians(self.robot_angle)
        arrow_length = 0.5
        dx = arrow_length * np.cos(angle_rad)
        dy = arrow_length * np.sin(angle_rad)
        
        # Draw robot as brown circle with orientation arrow
        self.ax.plot(self.robot_x, self.robot_y, 'o', markersize=15, color='#8B4513',
                    label='Current Position', zorder=5)
        self.ax.arrow(self.robot_x, self.robot_y, dx, dy, 
                     head_width=0.3, head_length=0.2, fc='#8B4513', ec='#8B4513', 
                     linewidth=2, zorder=6)
        
        # Draw border locations (red X markers with connecting lines)
        if len(self.border_locations) > 0:
            border_x = [loc[0] for loc in self.border_locations]
            border_y = [loc[1] for loc in self.border_locations]
            
            # Draw red X markers for each border detection
            self.ax.scatter(border_x, border_y, marker='x', s=200, linewidths=3,
                           color='red', label='Border Detected', alpha=0.9, zorder=4)
            
            # Draw connecting lines if multiple borders detected
            if len(self.border_locations) > 1:
                self.ax.plot(border_x, border_y, 'r--', linewidth=1.5, 
                           alpha=0.4, zorder=2)
        
        # Draw bumps with triangle markers
        if len(self.bump_locations) > 0:
            bump_x = [loc[0] for loc in self.bump_locations]
            bump_y = [loc[1] for loc in self.bump_locations]
            
            # Draw magenta triangle markers for each bump detection
            self.ax.scatter(bump_x, bump_y, marker='^', s=250, linewidths=2,
                           color='magenta', edgecolors='darkmagenta', label='Bump Detected', alpha=0.9, zorder=4)
            
            # Draw connecting lines if multiple bumps detected
            if len(self.bump_locations) > 1:
                self.ax.plot(bump_x, bump_y, 'm--', linewidth=1.5, 
                           alpha=0.4, zorder=2)
        
        # Title and labels
        self.ax.set_title("CYBOT MOVEMENT MAPPING - UNBOUNDED TRACKING", 
                         color='#00ff00', fontsize=14, pad=20)
        self.ax.set_facecolor('#0a0a0a')
        
        self.ax.set_xlabel('X Coordinate', color='#00ff00', fontsize=11)
        self.ax.set_ylabel('Y Coordinate', color='#00ff00', fontsize=11)
        
        self.ax.tick_params(colors='#00ff00')
        
        self.ax.legend(loc='upper right', facecolor='#2d3d1f', edgecolor='#4a5c23', 
                      labelcolor='#00ff00', fontsize=9)
        
        # Use tight layout to maximize map area
        self.fig.tight_layout(pad=0.3)
        self.canvas.draw()

    def update_robot_position(self, direction, move_distance=1.0):
        """Update robot position based on movement direction
        
        Args:
            direction: 'w' (forward), 's' (backward), 'a' (turn left), 'd' (turn right), 't' (stop)
            move_distance: Distance to move in coordinate units (default 1.0)
        """
        old_x, old_y = self.robot_x, self.robot_y
        position_changed = False

        if direction == 'w':  # Forward
            angle_rad = np.radians(self.robot_angle)
            new_x = self.robot_x + move_distance * np.cos(angle_rad)
            new_y = self.robot_y + move_distance * np.sin(angle_rad)
            
            # Check if moving towards a hazard (within 0.3 units of any border/bump)
            hazard_detected = False
            for hazard_x, hazard_y in self.border_locations + self.bump_locations:
                distance = np.sqrt((new_x - hazard_x)**2 + (new_y - hazard_y)**2)
                if distance < 0.3:
                    hazard_detected = True
                    print(f"Movement blocked: hazard at ({hazard_x:.1f}, {hazard_y:.1f}), distance: {distance:.2f}")
                    break
            
            if not hazard_detected:
                self.robot_x = new_x
                self.robot_y = new_y
                position_changed = True
            else:
                print("Forward movement blocked by hazard!")
            
        elif direction == 's':  # Backward (always allowed)
            angle_rad = np.radians(self.robot_angle)
            self.robot_x -= move_distance * np.cos(angle_rad)
            self.robot_y -= move_distance * np.sin(angle_rad)
            position_changed = True
            
        elif direction == 'a':  # Turn Left (counterclockwise, increases angle)
            self.robot_angle = (self.robot_angle + 30) % 360
            
        elif direction == 'd':  # Turn Right (clockwise, decreases angle)
            self.robot_angle = (self.robot_angle - 30) % 360
            if self.robot_angle < 0:
                self.robot_angle += 360
            
        elif direction == 't':
            # stop does not change position
            pass

        if position_changed:
            self.movement_trail.append((self.robot_x, self.robot_y))
        
        # Update UI
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
        
        self.position_label.setText(f"POSITION: ({self.robot_x:.1f}, {self.robot_y:.1f})")
        self.angle_label.setText(f"ANGLE: {self.robot_angle}°")
        
        # Calculate total distance traveled
        total_distance = 0
        for i in range(1, len(self.movement_trail)):
            x1, y1 = self.movement_trail[i-1]
            x2, y2 = self.movement_trail[i]
            total_distance += np.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        move_count = len(self.movement_trail) - 1
        self.movement_stats_label.setText(
            f"MOVEMENT STATS: {move_count} moves | Trail length: {len(self.movement_trail)} | Distance: {total_distance:.1f}"
        )
    
    def reset_robot_position(self):
        """Reset robot to origin (0, 0)"""
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_angle = 90
        self.movement_trail = [(self.robot_x, self.robot_y)]
        
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
        
        self.position_label.setText(f"POSITION: ({self.robot_x:.1f}, {self.robot_y:.1f})")
        self.angle_label.setText(f"ANGLE: {self.robot_angle}°")
        self.movement_stats_label.setText("MOVEMENT STATS: 0 moves | Trail length: 1 | Distance: 0.0")
    
    def clear_movement_trail(self):
        """Clear the movement trail but keep current position"""
        self.movement_trail = [(self.robot_x, self.robot_y)]
        
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
        
        self.movement_stats_label.setText("MOVEMENT STATS: 0 moves | Trail length: 1 | Distance: 0.0")
    
    def update_border_location(self, x=None, y=None):
        """
        Update the detected border location on the map and back up the robot
        Args:
            x: X coordinate of border (if None, uses current robot position)
            y: Y coordinate of border (if None, uses current robot position)
        """
        # Use current position if not specified
        if x is None:
            x = self.robot_x
        if y is None:
            y = self.robot_y
        
        # Check if this location is already marked (within 0.2 units) to avoid duplicates
        for existing_x, existing_y in self.border_locations:
            distance = np.sqrt((x - existing_x)**2 + (y - existing_y)**2)
            if distance < 0.2:
                print(f"Border already marked at ({existing_x:.1f}, {existing_y:.1f}), skipping duplicate")
                return  # Skip duplicate marking
        
        # Add border location at current position (before backing up)
        self.border_locations.append((x, y))
        
        # Keep only last 100 border points to avoid clutter
        if len(self.border_locations) > 100:
            self.border_locations.pop(0)
        
        # Back up the robot by 0.5 units
        self.backup_robot(0.5)
        
        # Redraw the grid with border markers
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
    
    def update_bump_location(self, x=None, y=None):
        """
        Update the detected bump location on the map and back up the robot
        Args:
            x: X coordinate of bump (if None, uses current robot position)
            y: Y coordinate of bump (if None, uses current robot position)
        """
        # Use current position if not specified
        if x is None:
            x = self.robot_x
        if y is None:
            y = self.robot_y
        
        # Check if this location is already marked (within 0.2 units) to avoid duplicates
        for existing_x, existing_y in self.bump_locations:
            distance = np.sqrt((x - existing_x)**2 + (y - existing_y)**2)
            if distance < 0.2:
                print(f"Bump already marked at ({existing_x:.1f}, {existing_y:.1f}), skipping duplicate")
                return  # Skip duplicate marking
        
        # Add bump location at current position (before backing up)
        self.bump_locations.append((x, y))
        
        # Keep only last 100 bump points to avoid clutter
        if len(self.bump_locations) > 100:
            self.bump_locations.pop(0)
        
        # Back up the robot by 0.5 units
        self.backup_robot(0.5)
        
        # Redraw the grid with bump markers
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
    
    def backup_robot(self, distance=0.5):
        """
        Back up the robot by the specified distance
        Args:
            distance: Distance to back up (default 0.5 units)
        """
        # Move backward in the opposite direction of current orientation
        angle_rad = np.radians(self.robot_angle)
        self.robot_x -= distance * np.cos(angle_rad)
        self.robot_y -= distance * np.sin(angle_rad)
        
        # Add the new position to the trail
        self.movement_trail.append((self.robot_x, self.robot_y))
        
        # Update position labels
        self.position_label.setText(f"POSITION: ({self.robot_x:.1f}, {self.robot_y:.1f})")
        
        # Calculate total distance traveled
        total_distance = 0
        for i in range(1, len(self.movement_trail)):
            x1, y1 = self.movement_trail[i-1]
            x2, y2 = self.movement_trail[i]
            total_distance += np.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        move_count = len(self.movement_trail) - 1
        self.movement_stats_label.setText(
            f"MOVEMENT STATS: {move_count} moves | Trail length: {len(self.movement_trail)} | Distance: {total_distance:.1f}"
        )
    
    def clear_border_locations(self):
        """Clear all detected border locations"""
        self.border_locations = []
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
    
    def clear_bump_locations(self):
        """Clear all detected bump locations"""
        self.bump_locations = []
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
    
    def clear_all_map_data(self):
        """Clear all map data: trail, borders, bumps, and reset robot position"""
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_angle = 90
        self.movement_trail = [(self.robot_x, self.robot_y)]
        self.border_locations = []
        self.bump_locations = []
        
        self.setup_movement_grid()
        
        # Update external map window if open
        if self.map_window:
            self.map_window.update_map()
        
        self.position_label.setText(f"POSITION: ({self.robot_x:.1f}, {self.robot_y:.1f})")
        self.angle_label.setText(f"ANGLE: {self.robot_angle}°")
        self.movement_stats_label.setText("MOVEMENT STATS: 0 moves | Trail length: 1 | Distance: 0.0")
    
    def open_map_window(self):
        """Open or bring to front the external map window"""
        if self.map_window is None:
            # Create new window
            self.map_window = MapWindow(self)
            self.map_window.window_closed.connect(self.on_map_window_closed)
            self.map_window.show()
            self.map_window.update_map()
            
            # Update button to show window is open
            self.open_map_btn.setText("MAP WINDOW OPEN ✓")
            self.open_map_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a5c23;
                    font-size: 12px;
                    min-width: 180px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6c33;
                }
            """)
        else:
            # Window exists, bring to front
            self.map_window.raise_()
            self.map_window.activateWindow()
            self.map_window.update_map()
    
    def on_map_window_closed(self):
        """Handle external map window being closed"""
        self.map_window = None
        
        # Update button to show window is closed
        self.open_map_btn.setText("OPEN MAP WINDOW 🗗")
        self.open_map_btn.setStyleSheet("""
            QPushButton {
                background-color: #234a5c;
                font-size: 12px;
                min-width: 180px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #285c6c;
            }
        """)