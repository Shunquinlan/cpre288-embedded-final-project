# #!/usr/bin/env python3

# import sys
# import socket
# import time
# import os
# import math
# import numpy as np

# # Import modular panels
# from control_panel import ControlPanel
# from scan_panel import ScanPanel
# from plot_panel import PlotPanel
# from map_panel import MapPanel
# from sound_panel import SoundPanel
# from response_panel import ResponsePanel
# from connection_manager import ConnectionManager
# from pathlib import Path
# from utils import get_base_stylesheet, format_log_message, COLORS

# # Configure matplotlib to work with PySide6
# os.environ['QT_API'] = 'pyside6'
# import matplotlib
# matplotlib.use('QtAgg')
# import matplotlib.pyplot as plt

# from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                                QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
#                                QPushButton, QPlainTextEdit, QFrame, QSizePolicy, QTabWidget,
#                                QMessageBox, QSplitter)
# from PySide6.QtCore import Qt, QTimer
# from PySide6.QtGui import QFont, QKeySequence, QShortcut


# class UltraSimpleCyBotGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
        
#         # Use ConnectionManager instead of direct socket
#         self.connection_manager = ConnectionManager()
        
#         # Create modular panels
#         self.control_panel = ControlPanel()
#         self.scan_panel = ScanPanel()
#         self.plot_panel = PlotPanel()
#         self.map_panel = MapPanel()
#         self.sound_panel = SoundPanel()
#         self.response_panel = ResponsePanel()
        
#         self.init_ui()
#         self.setup_connections()
#         self.setup_shortcuts()
        
#     def init_ui(self):
#         """Initialize the user interface"""
#         self.setWindowTitle("CyBot Military Command Center - Movement & Reconnaissance")
#         self.setGeometry(100, 100, 1400, 900)
#         self.setMinimumSize(1200, 800)
        
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
        
#         main_layout = QVBoxLayout(central_widget)
#         main_layout.setSpacing(10)
        
#         # Header
#         header_frame = QFrame()
#         header_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #1a1a1a;
#                 border: 2px solid #4a5c23;
#                 border-radius: 8px;
#                 padding: 8px;
#             }
#         """)
#         header_layout = QHBoxLayout(header_frame)
        
#         title_label = QLabel("CYBOT MILITARY COMMAND CENTER")
#         title_font = QFont("Arial", 14, QFont.Bold)
#         title_label.setFont(title_font)
#         title_label.setStyleSheet(f"color: {COLORS['text_green']}; margin: 5px;")
#         header_layout.addWidget(title_label)
        
#         header_layout.addStretch()
        
#         self.create_header_connection_controls(header_layout)
        
#         main_layout.addWidget(header_frame)
        
#         # View mode controls
#         view_control_frame = QFrame()
#         view_control_frame.setStyleSheet("""
#             QFrame {
#                 background-color: #2d3d1f;
#                 border: 2px solid #4a5c23;
#                 border-radius: 8px;
#                 padding: 10px;
#             }
#         """)
        
#         view_control_layout = QHBoxLayout(view_control_frame)
        
#         view_label = QLabel("VIEW MODE:")
#         view_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold;")
#         view_control_layout.addWidget(view_label)
        
#         self.single_view_btn = QPushButton("SINGLE VIEW")
#         self.single_view_btn.clicked.connect(self.set_single_view)
#         self.single_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #4a5c23;
#                 min-width: 100px;
#                 padding: 8px;
#             }
#         """)
#         view_control_layout.addWidget(self.single_view_btn)
        
#         self.dual_view_btn = QPushButton("DUAL VIEW")
#         self.dual_view_btn.clicked.connect(self.set_dual_view)
#         self.dual_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #3a4f2a;
#                 min-width: 100px;
#                 padding: 8px;
#             }
#         """)
#         view_control_layout.addWidget(self.dual_view_btn)
        
#         view_control_layout.addStretch()
#         main_layout.addWidget(view_control_frame)
        
#         # Create splitter for dual view
#         self.main_splitter = QSplitter(Qt.Horizontal)
#         self.main_splitter.setStyleSheet("""
#             QSplitter {
#                 background-color: #1a1a1a;
#             }
#             QSplitter::handle {
#                 background-color: #4a5c23;
#                 width: 3px;
#             }
#             QSplitter::handle:hover {
#                 background-color: #5a6c33;
#             }
#         """)
        
#         self.left_tab_widget = QTabWidget()
#         self.right_tab_widget = QTabWidget()
        
#         tab_style = """
#             QTabWidget::pane {
#                 border: 2px solid #4a5c23;
#                 background-color: #2d3d1f;
#             }
#             QTabBar::tab {
#                 background-color: #3a4f2a;
#                 color: #00ff00;
#                 padding: 8px 16px;
#                 margin: 2px;
#                 border: 1px solid #4a5c23;
#                 font-weight: bold;
#             }
#             QTabBar::tab:selected {
#                 background-color: #4a5c23;
#                 color: #ffffff;
#             }
#             QTabBar::tab:hover {
#                 background-color: #556b3d;
#             }
#         """
        
#         self.left_tab_widget.setStyleSheet(tab_style)
#         self.right_tab_widget.setStyleSheet(tab_style)
        
#         self.single_tab_widget = QTabWidget()
#         self.single_tab_widget.setStyleSheet(tab_style)
        
#         # Create tabs using modular panels
#         self.control_tab = self.create_control_tab()
#         self.plot_tab = self.plot_panel  # Use modular PlotPanel directly
#         self.map_tab = self.map_panel    # Use modular MapPanel directly
#         self.sound_tab = self.sound_panel  # Use modular SoundPanel directly
        
#         self.current_view_mode = "single"
#         self.setup_single_view()
        
#         self.content_container = QWidget()
#         self.content_layout = QVBoxLayout(self.content_container)
#         self.content_layout.addWidget(self.single_tab_widget)
#         main_layout.addWidget(self.content_container)
        
#         # Apply styling
#         self.setStyleSheet(get_base_stylesheet())

        
#     def create_control_tab(self):
#         """Create the control tab with modular ControlPanel, ScanPanel and ResponsePanel"""
#         control_widget = QWidget()
        
#         main_splitter = QSplitter(Qt.Horizontal)
#         main_splitter.setStyleSheet("""
#             QSplitter {
#                 background-color: #1a1a1a;
#             }
#             QSplitter::handle {
#                 background-color: #4a5c23;
#                 width: 3px;
#             }
#             QSplitter::handle:hover {
#                 background-color: #5a6c33;
#             }
#         """)
        
#         # LEFT PANEL - Controls (ControlPanel + ScanPanel)
#         left_panel = QWidget()
#         left_layout = QVBoxLayout(left_panel)
#         left_layout.setSpacing(10)
#         left_layout.setContentsMargins(10, 10, 10, 10)
        
#         # Status label
#         self.status_label = QLabel("UNIT NOT CONNECTED")
#         self.status_label.setAlignment(Qt.AlignCenter)
#         self.status_label.setStyleSheet("""
#             QLabel {
#                 color: #ff0000;
#                 font-weight: bold;
#                 padding: 10px;
#                 background-color: #3d1f1f;
#                 border: 2px solid #5c2323;
#                 border-radius: 5px;
#                 font-size: 12px;
#             }
#         """)
#         left_layout.addWidget(self.status_label)
        
#         # Add ControlPanel
#         left_layout.addWidget(self.control_panel)
        
#         # Add ScanPanel
#         left_layout.addWidget(self.scan_panel)
        
#         left_layout.addStretch()
        
#         # RIGHT PANEL - ResponsePanel
#         right_panel = QWidget()
#         right_layout = QVBoxLayout(right_panel)
#         right_layout.setSpacing(10)
#         right_layout.setContentsMargins(10, 10, 10, 10)
        
#         right_layout.addWidget(self.response_panel)
        
#         main_splitter.addWidget(left_panel)
#         main_splitter.addWidget(right_panel)
        
#         main_splitter.setSizes([350, 650])
        
#         left_panel.setMinimumWidth(300)
#         right_panel.setMinimumWidth(400)
        
#         control_layout = QVBoxLayout(control_widget)
#         control_layout.setContentsMargins(0, 0, 0, 0)
#         control_layout.addWidget(main_splitter)
        
#         return control_widget

#     def setup_connections(self):
#         """Wire up all panel signals to handlers"""
#         # ConnectionManager signals
#         self.connection_manager.connected_signal.connect(self.on_connection_changed)
#         self.connection_manager.message_received.connect(self._on_message_received)
        
#         # ControlPanel signals
#         self.control_panel.command_requested.connect(self._send_movement_command)
        
#         # ScanPanel signals
#         self.scan_panel.scan_requested.connect(self._send_scan_command)
#         self.scan_panel.scan_data_ready.connect(self._on_scan_data_ready)
#         self.scan_panel.set_connection_manager(self.connection_manager)
#         self.scan_panel.set_loggers(self.response_panel.log, self.response_panel.scan_log)
        
#         # PlotPanel signals
#         self.plot_panel.clear_radar_requested.connect(self.scan_panel.clear_live_scan)
        
#         # SoundPanel signals
#         self.sound_panel.song_play_requested.connect(self._play_song_slot)
#         self.sound_panel.song_clear_requested.connect(self._clear_song_slot)
#         self.sound_panel.set_connection_manager(self.connection_manager)
#         self.sound_panel.set_loggers(self.response_panel.log)
    
#     def _send_movement_command(self, cmd):
#         """Handle movement commands from ControlPanel"""
#         if not self.connection_manager.is_connected:
#             self.response_panel.log("✗ ERROR: No connection established", self.connection_manager.connected)
#             return
        
#         cmd_descriptions = {
#             'w': 'ADVANCE FORWARD',
#             'a': 'TURN LEFT',
#             's': 'RETREAT BACKWARD',
#             'd': 'TURN RIGHT',
#             't': 'HALT/STOP'
#         }
        
#         cmd_desc = cmd_descriptions.get(cmd.lower(), f"UNKNOWN CMD '{cmd}'")
#         self.response_panel.log(f"→ EXECUTING: {cmd_desc} [{cmd.upper()}]", self.connection_manager.connected)
        
#         # Update map visualization
#         if cmd.lower() in ['w', 'a', 's', 'd', 't']:
#             self.map_panel.update_robot_position(cmd.lower())
        
#         # Send command
#         success, response = self.connection_manager.send_command(cmd, wait_for_response=True)
#         if success and response:
#             self.response_panel.log(f"← SUCCESS: {response}", self.connection_manager.connected)
#         elif not success:
#             self.response_panel.log(f"← ERROR: {response}", self.connection_manager.connected)
    
#     def _send_scan_command(self, cmd):
#         """Handle scan commands from ScanPanel"""
#         # The ScanPanel handles the command internally via ConnectionManager
#         pass
    
#     def _on_scan_data_ready(self, angles, distances):
#         """Handle scan data from ScanPanel"""
#         # Update PlotPanel with new scan data
#         self.plot_panel.update_scan_data(angles, distances, self.scan_panel.live_scan_ir_distances if hasattr(self.scan_panel, 'live_scan_ir_distances') else None)
    
#     def _on_message_received(self, message):
#         """Handle messages from ConnectionManager"""
#         # Forward to response panel
#         if self.connection_manager.connected:
#             self.response_panel.log(f"← {message}", self.connection_manager.connected)
    
#     def on_connection_changed(self, connected):
#         """Handle connection state changes"""
#         self.connection_manager.connected = connected
#         if connected:
#             self.status_label.setText("UNIT CONNECTED - READY FOR ORDERS")
#             self.status_label.setStyleSheet("""
#                 QLabel {
#                     color: #00ff00;
#                     font-weight: bold;
#                     padding: 10px;
#                     background-color: #1f3d1f;
#                     border: 2px solid #23c523;
#                     border-radius: 5px;
#                     font-size: 12px;
#                 }
#             """)
#             self.connect_btn.setText("DISCONNECT")
#             self.connection_status_label.setText("●")
#             self.connection_status_label.setStyleSheet("color: #00ff00; font-size: 16px; font-weight: bold;")
#         else:
#             self.status_label.setText("UNIT NOT CONNECTED")
#             self.status_label.setStyleSheet("""
#                 QLabel {
#                     color: #ff0000;
#                     font-weight: bold;
#                     padding: 10px;
#                     background-color: #3d1f1f;
#                     border: 2px solid #5c2323;
#                     border-radius: 5px;
#                     font-size: 12px;
#                 }
#             """)
#             self.connect_btn.setText("CONNECT")
#             self.connection_status_label.setText("●")
#             self.connection_status_label.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
    
#     def _play_song_slot(self, slot):
#         """Play a song from the specified slot"""
#         if not self.connection_manager.is_connected:
#             self.response_panel.log("✗ ERROR: No connection established", self.connection_manager.connected)
#             return
        
#         self.response_panel.log(f"→ PLAYING SONG: Slot {slot}", self.connection_manager.connected)
#         cmd = str(slot + 5)  # Map to commands: slot 0->5, slot 1->6, etc.
        
#         success, response = self.connection_manager.send_command(cmd, wait_for_response=True)
#         if success and response:
#             self.response_panel.log(f"← SONG PLAYBACK: {response}", self.connection_manager.connected)
    
#     def _clear_song_slot(self, slot):
#         """Clear a song from the specified slot"""
#         if not self.connection_manager.is_connected:
#             self.response_panel.log("✗ ERROR: No connection established", self.connection_manager.connected)
#             return
        
#         self.response_panel.log(f"→ CLEARING SONG: Slot {slot}", self.connection_manager.connected)
#         cmd = 'x' if slot == 2 else 'z'  # x=clear slot 2, z=clear slot 3
        
#         success, response = self.connection_manager.send_command(cmd, wait_for_response=True)
#         if success and response:
#             self.response_panel.log(f"← SONG CLEARED: {response}", self.connection_manager.connected)

#     def clear_radar_display(self):
#         """Clear the radar display"""
#         self.scan_panel.clear_live_scan()
#         self.response_panel.scan_log("Radar display cleared")
        
#     def create_plot_tab(self):
#     def setup_movement_grid(self):
#         """Setup the initial movement grid visualization"""
#         self.map_ax.clear()
        
#         self.map_ax.set_xlim(-0.5, self.grid_width - 0.5)
#         self.map_ax.set_ylim(-0.5, self.grid_height - 0.5)
#         self.map_ax.set_aspect('equal')
        
#         for x in range(self.grid_width + 1):
#             self.map_ax.axvline(x - 0.5, color='#4a5c23', linewidth=1, alpha=0.7)
#         for y in range(self.grid_height + 1):
#             self.map_ax.axhline(y - 0.5, color='#4a5c23', linewidth=1, alpha=0.7)
        
#         if len(self.movement_trail) > 1:
#             trail_x = [pos[0] for pos in self.movement_trail]
#             trail_y = [pos[1] for pos in self.movement_trail]
#             self.map_ax.plot(trail_x, trail_y, 'g-', linewidth=2, alpha=0.6, label='Movement Trail')
            
#             for i, (x, y) in enumerate(self.movement_trail[:-1]):
#                 self.map_ax.plot(x, y, 'go', markersize=8, alpha=0.5)
#                 self.map_ax.text(x + 0.1, y + 0.1, str(i + 1), color='#00ff00', 
#                                fontsize=8, weight='bold')
        
#         self.map_ax.plot(self.robot_x, self.robot_y, 'ro', markersize=15, 
#                         label='Current Position', zorder=5)
        
#         self.map_ax.text(self.robot_x, self.robot_y, 'R', fontsize=20, 
#                         ha='center', va='center', zorder=6, color='white', weight='bold')
        
#         grid_desc = f"{self.grid_width}x{self.grid_height}"
#         self.map_ax.set_title(f"CYBOT MOVEMENT MAPPING - {grid_desc} GRID", 
#                              color='#00ff00', fontsize=14, pad=20)
#         self.map_ax.set_facecolor('#0a0a0a')
#         self.map_ax.grid(True, color='#4a5c23', alpha=0.3)
        
#         self.map_ax.set_xticks(range(self.grid_width))
#         self.map_ax.set_yticks(range(self.grid_height))
#         self.map_ax.set_xticklabels([f'X{i}' for i in range(self.grid_width)], 
#                                    color='#00ff00', fontsize=10)
#         self.map_ax.set_yticklabels([f'Y{i}' for i in range(self.grid_height)], 
#                                    color='#00ff00', fontsize=10)
        
#         self.map_ax.legend(loc='upper right', facecolor='#2d3d1f', edgecolor='#4a5c23', 
#                           labelcolor='#00ff00')
        
#         self.map_canvas.draw()
        
#     def update_robot_position(self, direction):
#         """Update robot position based on movement direction"""
#         old_x, old_y = self.robot_x, self.robot_y
        
#         if direction == 'w':
#             new_y = min(self.robot_y + 1, self.grid_height - 1)
#             new_x = self.robot_x
#         elif direction == 's':
#             new_y = max(self.robot_y - 1, 0)
#             new_x = self.robot_x
#         elif direction == 'a':
#             new_x = max(self.robot_x - 1, 0)
#             new_y = self.robot_y
#         elif direction == 'd':
#             new_x = min(self.robot_x + 1, self.grid_width - 1)
#             new_y = self.robot_y
#         elif direction == 't':
#             return
#         else:
#             return
            
#         if new_x != old_x or new_y != old_y:
#             self.robot_x = new_x
#             self.robot_y = new_y
#             self.movement_trail.append((self.robot_x, self.robot_y))
            
#             self.setup_movement_grid()
            
#             position_name = self.get_position_name(self.robot_x, self.robot_y)
#             self.position_label.setText(f"CURRENT POSITION: ({self.robot_x}, {self.robot_y}) - {position_name}")
            
#             move_count = len(self.movement_trail) - 1
#             self.movement_stats_label.setText(f"MOVEMENT STATS: {move_count} moves | Trail length: {len(self.movement_trail)}")
            
#             self.log(f"✓ Robot moved {direction.upper()} to position ({self.robot_x}, {self.robot_y})")
#         else:
#             self.log(f"⚠ Cannot move {direction.upper()} - boundary reached")
            
#     def get_position_name(self, x, y):
#         """Get a descriptive name for the current position"""
#         center_x = self.grid_width // 2
#         center_y = self.grid_height // 2
        
#         if x == center_x and y == center_y:
#             return "CENTER"
#         elif x == 0 and y == 0:
#             return "BOTTOM-LEFT CORNER"
#         elif x == self.grid_width - 1 and y == 0:
#             return "BOTTOM-RIGHT CORNER"
#         elif x == 0 and y == self.grid_height - 1:
#             return "TOP-LEFT CORNER"
#         elif x == self.grid_width - 1 and y == self.grid_height - 1:
#             return "TOP-RIGHT CORNER"
#         elif x == 0:
#             return "LEFT EDGE"
#         elif x == self.grid_width - 1:
#             return "RIGHT EDGE"
#         elif y == 0:
#             return "BOTTOM EDGE"
#         elif y == self.grid_height - 1:
#             return "TOP EDGE"
#         else:
#             return "FIELD"
            
#     def reset_robot_position(self):
#         """Reset robot to center position"""
#         self.robot_x = self.grid_width // 2
#         self.robot_y = self.grid_height // 2
#         self.movement_trail = [(self.robot_x, self.robot_y)]
        
#         self.setup_movement_grid()
#         position_name = self.get_position_name(self.robot_x, self.robot_y)
#         self.position_label.setText(f"CURRENT POSITION: ({self.robot_x}, {self.robot_y}) - {position_name}")
#         self.movement_stats_label.setText("MOVEMENT STATS: 0 moves | Trail length: 1")
        
#         self.log(f"✓ Robot position reset to center ({self.robot_x}, {self.robot_y})")
        
#     def clear_movement_trail(self):
#         """Clear the movement trail but keep current position"""
#         self.movement_trail = [(self.robot_x, self.robot_y)]
        
#         self.setup_movement_grid()
#         self.movement_stats_label.setText("MOVEMENT STATS: 0 moves | Trail length: 1")
        
#         self.log("✓ Movement trail cleared")
        
#     def flip_grid_orientation(self):
#         """Flip grid between 7x4 and 4x7"""
#         if not self.is_flipped:
#             self.grid_width = 4
#             self.grid_height = 7
#             self.is_flipped = True
#             self.flip_grid_btn.setText("FLIP TO 7x4")
#             self.grid_label.setText("MOVEMENT MAPPING GRID (4x7):")
#             self.robot_x = min(self.robot_x, self.grid_width - 1)
#             self.robot_y = min(self.robot_y, self.grid_height - 1)
#         else:
#             self.grid_width = 7
#             self.grid_height = 4
#             self.is_flipped = False
#             self.flip_grid_btn.setText("FLIP TO 4x7")
#             self.grid_label.setText("MOVEMENT MAPPING GRID (7x4):")
#             self.robot_x = min(self.robot_x, self.grid_width - 1)
#             self.robot_y = min(self.robot_y, self.grid_height - 1)
        
#         self.movement_trail = [(min(x, self.grid_width - 1), min(y, self.grid_height - 1)) 
#                               for x, y in self.movement_trail]
        
#         self.setup_movement_grid()
        
#         position_name = self.get_position_name(self.robot_x, self.robot_y)
#         self.position_label.setText(f"CURRENT POSITION: ({self.robot_x}, {self.robot_y}) - {position_name}")
        
#         grid_desc = f"{self.grid_width}x{self.grid_height}"
#         self.log(f"✓ Grid flipped to {grid_desc} orientation")
        
#     def on_grid_click(self, event):
#         """Handle mouse clicks on the grid"""
#         if event.inaxes != self.map_ax:
#             return
            
#         if event.xdata is None or event.ydata is None:
#             return
            
#         new_x = int(round(event.xdata))
#         new_y = int(round(event.ydata))
        
#         if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
#             old_x, old_y = self.robot_x, self.robot_y
            
#             self.robot_x = new_x
#             self.robot_y = new_y
#             self.movement_trail.append((self.robot_x, self.robot_y))
            
#             self.setup_movement_grid()
            
#             position_name = self.get_position_name(self.robot_x, self.robot_y)
#             self.position_label.setText(f"CURRENT POSITION: ({self.robot_x}, {self.robot_y}) - {position_name}")
            
#             move_count = len(self.movement_trail) - 1
#             self.movement_stats_label.setText(f"MOVEMENT STATS: {move_count} moves | Trail length: {len(self.movement_trail)}")
            
#             self.log(f"✓ Robot moved from ({old_x}, {old_y}) to ({self.robot_x}, {self.robot_y}) via drag")
#         else:
#             self.log("⚠ Cannot move robot outside grid boundaries")
        
#     def create_header_connection_controls(self, header_layout):
#         """Create compact connection controls for the header"""
#         ip_label = QLabel("TARGET:")
#         ip_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         ip_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold; font-size: 11px;")
#         header_layout.addWidget(ip_label)
        
#         self.ip_entry = QLineEdit("192.168.1.1")
#         self.ip_entry.setFixedWidth(110)
#         self.ip_entry.setStyleSheet("""
#             QLineEdit {
#                 background-color: #2d3d1f;
#                 color: #00ff00;
#                 border: 1px solid #4a5c23;
#                 padding: 4px;
#                 font-size: 11px;
#             }
#         """)
#         header_layout.addWidget(self.ip_entry)
        
#         port_label = QLabel("PORT:")
#         port_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         port_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold; font-size: 11px;")
#         header_layout.addWidget(port_label)
        
#         self.port_entry = QLineEdit("288")
#         self.port_entry.setFixedWidth(50)
#         self.port_entry.setStyleSheet("""
#             QLineEdit {
#                 background-color: #2d3d1f;
#                 color: #00ff00;
#                 border: 1px solid #4a5c23;
#                 padding: 4px;
#                 font-size: 11px;
#             }
#         """)
#         header_layout.addWidget(self.port_entry)
        
#         self.connect_btn = QPushButton("CONNECT")
#         self.connect_btn.clicked.connect(self.connect)
#         self.connect_btn.setFixedWidth(80)
#         self.connect_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #4a5c23;
#                 color: #ffffff;
#                 border: 1px solid #5a6c33;
#                 font-size: 11px;
#                 font-weight: bold;
#                 padding: 6px;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #5a6c33;
#             }
#         """)
#         header_layout.addWidget(self.connect_btn)
        
#         self.connection_status_label = QLabel("●")
#         self.connection_status_label.setStyleSheet("color: #ff0000; font-size: 16px; font-weight: bold;")
#         self.connection_status_label.setToolTip("Connection Status: Disconnected")
#         header_layout.addWidget(self.connection_status_label)
        
#     def create_movement_section(self, parent_layout):
#     def setup_shortcuts(self):
#         """Setup keyboard shortcuts"""
#         movement_shortcuts = {
#             'W': lambda: self.send_cmd('w'),
#             'A': lambda: self.send_cmd('a'), 
#             'S': lambda: self.send_cmd('s'),
#             'D': lambda: self.send_cmd('d'),
#             'T': lambda: self.send_cmd('t')
#         }
        
#         scan_shortcuts = {
#             'R': lambda: self.send_scan_cmd('r'),
#             'Q': lambda: self.send_scan_cmd('q'),
#             'O': lambda: self.send_scan_cmd('o'),
#             'C': lambda: self.send_scan_cmd('c'),
#             'F': lambda: self.send_scan_cmd('f'),
#             'M': lambda: self.send_scan_cmd('m')
#         }
        
#         all_shortcuts = {**movement_shortcuts, **scan_shortcuts}
#         for key, func in all_shortcuts.items():
#             shortcut = QShortcut(QKeySequence(key), self)
#             shortcut.activated.connect(func)
            
#     def setup_single_view(self):
#         """Setup single view mode"""
#         self.single_tab_widget.clear()
#         self.single_tab_widget.addTab(self.control_tab, "CONTROLS")
#         self.single_tab_widget.addTab(self.plot_tab, "SENSOR PLOT")
#         self.single_tab_widget.addTab(self.map_tab, "MOVEMENT MAP")
#         self.single_tab_widget.addTab(self.sound_tab, "SOUND CONTROL")
        
#     def setup_dual_view(self):
#         """Setup dual view mode"""
#         self.left_tab_widget.clear()
#         self.right_tab_widget.clear()
        
#         self.left_tab_widget.addTab(self.control_tab, "MOVEMENT CONTROL")
        
#         self.right_tab_widget.addTab(self.plot_tab, "SENSOR PLOT")
#         self.right_tab_widget.addTab(self.map_tab, "MOVEMENT MAP")
#         self.right_tab_widget.addTab(self.sound_tab, "SOUND CONTROL")
        
#         self.main_splitter.setSizes([500, 500])
        
#     def set_single_view(self):
#         """Switch to single view mode"""
#         if self.current_view_mode == "single":
#             return
            
#         self.current_view_mode = "single"
        
#         if self.main_splitter.parent():
#             self.content_layout.removeWidget(self.main_splitter)
#             self.main_splitter.setParent(None)
        
#         self.setup_single_view()
#         self.content_layout.addWidget(self.single_tab_widget)
        
#         self.single_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #4a5c23;
#                 min-width: 100px;
#                 padding: 8px;
#                 color: #ffffff;
#             }
#         """)
#         self.dual_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #3a4f2a;
#                 min-width: 100px;
#                 padding: 8px;
#             }
#         """)
        
#         self.log("✓ Switched to single view mode")
        
#     def set_dual_view(self):
#         """Switch to dual view mode"""
#         if self.current_view_mode == "dual":
#             return
            
#         self.current_view_mode = "dual"
        
#         if self.single_tab_widget.parent():
#             self.content_layout.removeWidget(self.single_tab_widget)
#             self.single_tab_widget.setParent(None)
        
#         self.setup_dual_view()
#         self.main_splitter.addWidget(self.left_tab_widget)
#         self.main_splitter.addWidget(self.right_tab_widget)
#         self.content_layout.addWidget(self.main_splitter)
        
#         self.dual_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #4a5c23;
#                 min-width: 100px;
#                 padding: 8px;
#                 color: #ffffff;
#             }
#         """)
#         self.single_view_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #3a4f2a;
#                 min-width: 100px;
#                 padding: 8px;
#             }
#         """)
        
#         self.log("✓ Switched to dual view mode")
        
#     def connect(self):
#         """Connect to CyBot using ConnectionManager"""
#         if self.connection_manager.connected:
#             self.disconnect()
#             return
            
#         ip = self.ip_entry.text().strip()
#         port = self.port_entry.text().strip()
        
#         self.response_panel.log(f"→ ATTEMPTING CONNECTION to {ip}:{port}", False)
        
#         success, message = self.connection_manager.connect(ip, port)
        
#         if success:
#             self.response_panel.log(f"✓ CONNECTION ESTABLISHED: {message}", True)
#             self.response_panel.log(f"← CyBot unit is online and ready for commands", True)
#         else:
#             self.response_panel.log(f"✗ CONNECTION FAILED: {message}", False)
#             self.response_panel.log(f"← Check network, IP address, and CyBot power status", False)
#             QMessageBox.warning(self, "Connection Error", f"Failed to connect: {message}")
            
#     def disconnect(self):
#         """Disconnect from CyBot"""
#         self.response_panel.log("→ DISCONNECTING from CyBot...", self.connection_manager.connected)
#         self.connection_manager.disconnect()
#         self.response_panel.log("✓ DISCONNECTED: Ready for new connection", False)
        
#     def send_cmd(self, cmd):
#         """Send command to CyBot using ConnectionManager"""
#         cmd_descriptions = {
#             'w': 'ADVANCE FORWARD',
#             'a': 'TURN LEFT', 
#             's': 'RETREAT BACKWARD',
#             'd': 'TURN RIGHT',
#             't': 'HALT/STOP',
#             'm': 'STATUS CHECK'
#         }
        
#         cmd_desc = cmd_descriptions.get(cmd.lower(), f"UNKNOWN CMD '{cmd}'")
#         self.response_panel.log(f"→ EXECUTING: {cmd_desc} [{cmd.upper()}]", self.connection_manager.connected)
        
#         if cmd.lower() in ['w', 'a', 's', 'd', 't']:
#             self.update_robot_position(cmd.lower())
        
#         start_time = time.time()
#         response = self.connection_manager.send_command(cmd, timeout=3)
#         response_time = int((time.time() - start_time) * 1000)
        
#         if response:
#             self.response_panel.log(f"← SUCCESS: {response} ({response_time}ms)", self.connection_manager.connected)
#         else:
#             self.response_panel.log(f"← TIMEOUT: CyBot didn't respond within 3s", False)
#             self.connect_btn.setText("CONNECT")
            
#     def send_scan_cmd(self, cmd):
#         """Send scan command to CyBot with radar updates"""
#         if not self.connection_manager.connected:
#             self.response_panel.log("✗ ERROR: No connection established", False)
#             return
        
#         scan_descriptions = {
#             'r': 'ENHANCED FULL RANGE SCAN (180° Sweep)',
#             'q': 'QUICK 3-POINT SCAN (L/F/R)',
#             'o': 'ENHANCED OBJECT DETECTION SCAN',
#             'c': 'CENTER SERVO TO 90°',
#             'f': 'FORWARD SENSOR READING',
#             'm': 'SYSTEM STATUS CHECK'
#         }
        
#         cmd_desc = scan_descriptions.get(cmd.lower(), f"UNKNOWN SCAN CMD '{cmd}'")
#         self.log(f"→ INITIATING: {cmd_desc} [{cmd.upper()}]")
#         self.scan_log(f"╔═══ {cmd_desc} INITIATED ═════╗")
        
#         # Reset scan data for new scan
#         self.live_scan_angles = []
#         self.live_scan_ping_distances = []
#         self.live_scan_ir_distances = []
        
#         # Clear the radar display visually before starting new scan
#         if self.radar_widget:
#             self.radar_widget.clear_scan()
        
#         # Update radar info
#         if self.radar_widget:
#             self.radar_info.setText(f"🔄 Scanning... ({cmd.upper()} command)")
        
#         start_time = time.time()
        
#         if cmd in ['r', 'o']:
#             timeout = 15  
#             self.scan_panel.scan_log("⚡ EXTENDED SCAN: Servo sweep in progress...")
#         elif cmd == 'q':
#             timeout = 8
#             self.scan_panel.scan_log("⚡ QUICK RECON: Checking 3 positions...")
#         elif cmd == 'f':
#             timeout = 5
#             self.scan_panel.scan_log("⚡ FORWARD SENSOR: Reading distance...")
#         elif cmd == 'c':
#             timeout = 3
#             self.scan_panel.scan_log("⚡ SERVO CENTER: Moving to 90°...")
#         else:
#             timeout = 5
        
#         try:
#             responses = self.connection_manager.send_command_streaming(cmd, timeout=timeout)
            
#             for response in responses:
#                 if any(keyword in response for keyword in 
#                        ['SCAN', 'PING', 'IR', 'OBJECT', 'STATUS', 'SERVO']):
#                     self.parse_and_log_scan_data(response, collect_for_plot=True)
#                 else:
#                     self.response_panel.log(f"← RESPONSE: {response}", self.connection_manager.connected)
            
#             total_time = int((time.time() - start_time) * 1000)
            
#             if responses:
#                 self.scan_log(f"✓ SCAN COMPLETE: {len(responses)} data packets received ({total_time}ms)")
#                 self.log(f"← SUCCESS: Scan completed in {total_time}ms")
                
#                 # Update radar info
#                 if self.radar_widget and self.live_scan_angles:
#                     point_count = len(self.live_scan_angles)
#                     self.radar_info.setText(f"✓ Scan complete: {point_count} points detected")
                
#                 if self.live_scan_angles and self.live_scan_ping_distances and cmd in ['r', 'q', 'f', 'o']:
#                     self.update_sensor_map_from_scan()
                    
#             else:
#                 self.scan_log(f"❌ NO DATA: No sensor data received ({total_time}ms)")
#                 self.log(f"← WARNING: No scan response received")
#                 if self.radar_widget:
#                     self.radar_info.setText("⚠ Scan complete: No data received")
                
#         except Exception as e:
#             total_time = int((time.time() - start_time) * 1000)
#             self.log(f"✗ SCAN ERROR: {e} (after {total_time}ms)")
#             self.scan_log(f"❌ SCAN FAILED: {e}")
#             if self.radar_widget:
#                 self.radar_info.setText(f"❌ Scan failed: {e}")
            
#     def parse_and_log_scan_data(self, response, collect_for_plot=False):
#         """Parse scan response and update radar in real-time with both PING and IR"""
#         try:
#             if "PING=" in response and "IR=" in response:
#                 parts = response.split()
#                 direction = parts[0].replace(":", "")
                
#                 ping_val = None
#                 ir_val = None
#                 angle_deg = None
                
#                 if direction.startswith("ANGLE="):
#                     try:
#                         angle_deg = float(direction.split("=")[1])
#                     except ValueError:
#                         angle_deg = None
#                 elif direction == "LEFT":
#                     angle_deg = 100.0
#                 elif direction in ("FORWARD", "CENTER"):
#                     angle_deg = 90.0
#                 elif direction == "RIGHT":
#                     angle_deg = 80.0
                
#                 for part in parts:
#                     if part.startswith("PING="):
#                         try:
#                             ping_val = float(part.split("=")[1])
#                         except ValueError:
#                             ping_val = None
#                     elif part.startswith("IR="):
#                         try:
#                             ir_val = float(part.split("=")[1])
#                         except ValueError:
#                             ir_val = None
                
#                 if ping_val is not None and ir_val is not None:
#                     if collect_for_plot and angle_deg is not None:
#                         angle_rad = np.radians(angle_deg)
#                         self.live_scan_angles.append(angle_rad)
#                         self.live_scan_ping_distances.append(ping_val)
#                         self.live_scan_ir_distances.append(ir_val)
                        
#                         # Update radar display in real-time with both PING and IR
#                         if self.radar_widget:
#                             self.radar_widget.update_scan_data(self.live_scan_angles, 
#                                                               self.live_scan_ping_distances,
#                                                               self.live_scan_ir_distances)
#                             self.radar_info.setText(f"📡 Collecting: {len(self.live_scan_angles)} points")
                        
#                         self.scan_log(f"📍 PLOT DATA: angle={angle_deg:.1f}° PING={ping_val:.1f}cm IR={ir_val:.1f}cm (points: {len(self.live_scan_angles)})")
                    
#                     ping_status = "CLEAR" if ping_val > 30 else "OBSTACLE" if ping_val > 10 else "BLOCKED"
#                     ir_status = "CLEAR" if ir_val > 40 else "OBJECT" if ir_val > 15 else "CLOSE"
                    
#                     angle_info = f" @{angle_deg:3.0f}°" if angle_deg is not None else ""
#                     self.scan_log(f"📊 {direction:>8}{angle_info}: PING={ping_val:5.1f}cm [{ping_status:>8}] | IR={ir_val:5.1f}cm [{ir_status:>6}]")
#                 else:
#                     self.scan_log(f"📡 {response}")
                    
#             elif "OBJECTS_FOUND:" in response:
#                 count = response.split(":")[1].strip()
#                 self.scan_log(f"🎯 DETECTION RESULT: {count} objects identified")
                
#             elif "STATUS:" in response:
#                 self.scan_log(f"🔧 SYSTEM STATUS: {response.split(':', 1)[1].strip()}")
                
#             else:
#                 self.scan_log(f"📡 {response}")
                
#         except Exception as e:
#             self.scan_log(f"📡 {response}")
            
#     def update_sensor_map_from_scan(self):
#         """Update the sensor plot with live scan data (both PING and IR)"""
#         try:
#             self.scan_log(f"📊 UPDATE CHECK: angles={len(self.live_scan_angles)}, ping={len(self.live_scan_ping_distances)}, ir={len(self.live_scan_ir_distances)}")
            
#             if not self.live_scan_angles or not self.live_scan_ping_distances:
#                 self.scan_log("⚠️ No scan data collected for plotting")
#                 return
                
#             self.sensor_angles = self.live_scan_angles.copy()
#             self.sensor_ping_distances = self.live_scan_ping_distances.copy()
#             self.sensor_ir_distances = self.live_scan_ir_distances.copy()
            
#             self.scan_log(f"📊 RAW DATA: {len(self.sensor_angles)} points copied")
            
#             if len(self.sensor_angles) == len(self.sensor_ping_distances):
#                 combined = list(zip(self.sensor_angles, self.sensor_ping_distances, self.sensor_ir_distances))
#                 combined.sort(key=lambda x: x[0])
#                 self.sensor_angles, self.sensor_ping_distances, self.sensor_ir_distances = zip(*combined)
#                 self.sensor_angles = list(self.sensor_angles)
#                 self.sensor_ping_distances = list(self.sensor_ping_distances)
#                 self.sensor_ir_distances = list(self.sensor_ir_distances)
            
#             self.plot_data_btn.setEnabled(True)
#             self.plot_sensor_data()
            
#             max_ping = max(self.sensor_ping_distances) if self.sensor_ping_distances else 0
#             min_ping = min(self.sensor_ping_distances) if self.sensor_ping_distances else 0
#             avg_ping = sum(self.sensor_ping_distances) / len(self.sensor_ping_distances) if self.sensor_ping_distances else 0
#             angle_range = max(self.sensor_angles) - min(self.sensor_angles) if len(self.sensor_angles) > 1 else 0
            
#             live_info = (f"LIVE SCAN DATA | Points: {len(self.sensor_angles)} | "
#                         f"PING Range: {min_ping:.1f}-{max_ping:.1f}cm | "
#                         f"Avg: {avg_ping:.1f}cm | "
#                         f"Sweep: {np.degrees(angle_range):.0f}°")
            
#             self.file_info_label.setText(live_info)
#             self.loaded_filename = "LIVE_SCAN_DATA"
            
#             self.scan_log(f"✓ SENSOR MAP UPDATED: {len(self.sensor_angles)} data points plotted")
#             self.log(f"← LIVE DATA: Sensor plot updated with {len(self.sensor_angles)} scan points")
            
#         except Exception as e:
#             self.scan_log(f"❌ PLOT UPDATE FAILED: {e}")
#             self.log(f"✗ PLOT ERROR: Failed to update sensor map - {e}")

#     def scan_log(self, message):
#         """Add message to scan results log"""
#         timestamp = time.strftime("[%H:%M:%S]")
#         line_count = self.scan_results_text.document().blockCount()
#         formatted_message = f"{timestamp} #{line_count:03d} {message}"
#         self.scan_results_text.appendPlainText(formatted_message)
#         self.scan_results_text.ensureCursorVisible()
        
#         scrollbar = self.scan_results_text.verticalScrollBar()
#         scrollbar.setValue(scrollbar.maximum())
        
#     def log(self, message):
#         """Add message to response log"""
#         line_count = self.response_text.document().blockCount()
#         formatted_message = format_log_message(f"#{line_count:03d} {message}", self.connection_manager.connected)
#         self.response_text.appendPlainText(formatted_message)
#         self.response_text.ensureCursorVisible()
        
#         scrollbar = self.response_text.verticalScrollBar()
#         scrollbar.setValue(scrollbar.maximum())

#     def plot_sensor_data(self):
#         """Generate polar plot of sensor data with both PING and IR"""
#         if not self.sensor_angles or not self.sensor_ping_distances:
#             self.log("⚠ Plot Warning: No sensor data available")
#             return
            
#         try:
#             self.ax.clear()
            
#             # Plot PING data (BLUE)
#             max_ping = max(self.sensor_ping_distances) if self.sensor_ping_distances else 100
#             line_ping, = self.ax.plot(self.sensor_angles, self.sensor_ping_distances, 'b-', 
#                                linewidth=2, markersize=6, label='PING Sensor', 
#                                picker=True, pickradius=10)
#             self.ax.plot(self.sensor_angles, self.sensor_ping_distances, 'bo', markersize=4)
            
#             # Plot IR data (RED)
#             if self.sensor_ir_distances:
#                 line_ir, = self.ax.plot(self.sensor_angles, self.sensor_ir_distances, 'r-', 
#                                    linewidth=2, markersize=6, label='IR Sensor', 
#                                    picker=True, pickradius=10)
#                 self.ax.plot(self.sensor_angles, self.sensor_ir_distances, 'ro', markersize=4)
            
#             title_text = f"CYBOT SENSOR SCAN\nMax PING: {max_ping:.2f}cm | Points: {len(self.sensor_angles)}"
#             self.ax.set_title(title_text, color='#00ff00', fontsize=11, pad=15)
#             self.ax.set_facecolor('#0a0a0a')
#             self.ax.grid(True, color='#4a5c23', alpha=0.7)
            
#             self.ax.set_ylim(0, max_ping * 1.15)
            
#             self.ax.legend(loc='upper right', bbox_to_anchor=(1.12, 1.0), 
#                           facecolor='#2d3d1f', edgecolor='#4a5c23', 
#                           labelcolor='#00ff00', fontsize=9)
            
#             self.canvas.draw()
            
#             self.log(f"✓ Generated polar plot with {len(self.sensor_angles)} data points")
            
#         except Exception as e:
#             self.log(f"✗ Failed to generate plot: {e}")
            
#     def clear_plot(self):
#         """Clear the sensor plot"""
#         self.ax.clear()
#         self.ax.set_title("CYBOT SENSOR SCAN", color='#00ff00', fontsize=12, pad=15)
#         self.ax.set_facecolor('#0a0a0a')
#         self.ax.grid(True, color='#4a5c23', alpha=0.7)
#         self.canvas.draw()
        
#         self.sensor_angles = []
#         self.sensor_ping_distances = []
#         self.sensor_ir_distances = []
#         self.file_info_label.setText("SENSOR DATA: Use scan commands to collect data for plotting")
#         self.plot_data_btn.setEnabled(False)
        
#         self.log("✓ Plot cleared")

#     def closeEvent(self, event):
#         """Handle window close event"""
#         if self.connection_manager.connected:
#             self.disconnect()
#         event.accept()
        
#     def play_song_slot(self, slot):
#         """Play a song from the specified slot"""
#         if not self.connection_manager.connected:
#             self.response_panel.log("✗ ERROR: No connection established", False)
#             return
        
#         self.response_panel.log(f"→ PLAYING SONG: Slot {slot}", self.connection_manager.connected)
#         cmd = str(slot + 5)  # Map to commands: slot 0->5, slot 1->6, etc.
        
#         response = self.connection_manager.send_command(cmd, timeout=2)
#         if response:
#             self.response_panel.log(f"← SONG PLAYBACK: {response}", self.connection_manager.connected)

#     def clear_song_slot(self, slot):
#         """Clear a song from the specified slot"""
#         if not self.connection_manager.connected:
#             self.response_panel.log("✗ ERROR: No connection established", False)
#             return
        
#         self.response_panel.log(f"→ CLEARING SONG: Slot {slot}", self.connection_manager.connected)
#         cmd = 'x' if slot == 2 else 'z'  # x=clear slot 2, z=clear slot 3
        
#         response = self.connection_manager.send_command(cmd, timeout=2)
#         if response:
#             self.response_panel.log(f"← SONG CLEARED: {response}", self.connection_manager.connected)

#     def sound_log(self, message, connected=False):
#         """Log message for sound panel"""
#         self.log(message)

#     def set_sound_status(self, text):
#         """Update sound panel status"""
#         if hasattr(self, 'sound_panel'):
#             self.sound_panel.sound_control_status_label.setText(text)


# def main():
#     """Main function to run the application"""
#     app = QApplication(sys.argv)
#     app.setApplicationName("CyBot Military Command Center")
    
#     window = UltraSimpleCyBotGUI()
#     window.show()
    
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main()
