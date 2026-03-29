"""Main window that combines all panels"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QTabWidget, QMenuBar, QMessageBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame, QGridLayout, QSplitter, QSizePolicy)
from PySide6.QtGui import QAction, QFont, QPixmap, QKeyEvent
from PySide6.QtCore import Qt
from pathlib import Path

from controls_panel import ControlsPanel
from radar_panel import RadarPanel
from scan_panel import ScanPanel
from map_panel import MapPanel
from sound_panel import SoundPanel
from response_panel import ResponsePanel
from log_window import LogWindow
from connection_manager import ConnectionManager
from utils import get_base_stylesheet, COLORS


class CyBotMainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager()
        self.current_view_mode = "single"  # Track current view mode
        self.log_window = None  # Separate log window (created on demand)
        self.init_ui()
        self.setup_connections()
        
        # Auto-open log window on startup
        self.show_log_window()

    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("CyBot Military Command Center")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(get_base_stylesheet())

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)

        # Header frame with fixed height
        header_frame = QFrame()
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_frame.setMaximumHeight(70)
        header_frame.setMinimumHeight(70)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #4a5c23;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Title
        title_label = QLabel("CYBOT COMMAND TERMINAL")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['text_green']}; margin: 5px;")
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # View mode controls
        view_label = QLabel("VIEW MODE:")
        view_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold;")
        view_label.setFixedHeight(32)
        header_layout.addWidget(view_label)

        self.single_view_btn = QPushButton("SINGLE VIEW")
        self.single_view_btn.setFixedSize(110, 32)
        self.single_view_btn.clicked.connect(self.set_single_view)
        header_layout.addWidget(self.single_view_btn)

        self.dual_view_btn = QPushButton("DUAL VIEW")
        self.dual_view_btn.setFixedSize(110, 32)
        self.dual_view_btn.clicked.connect(self.set_dual_view)
        header_layout.addWidget(self.dual_view_btn)

        header_layout.addStretch()

        # Connection controls
        ip_label = QLabel("TARGET:")
        ip_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold; font-size: 11px;")
        ip_label.setFixedHeight(28)
        header_layout.addWidget(ip_label)

        self.conn_ip = QLineEdit("192.168.1.1")
        self.conn_ip.setFixedSize(130, 28)
        header_layout.addWidget(self.conn_ip)

        port_label = QLabel("PORT:")
        port_label.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold; font-size: 11px;")
        port_label.setFixedHeight(28)
        header_layout.addWidget(port_label)

        self.conn_port = QLineEdit("288")
        self.conn_port.setFixedSize(60, 28)
        header_layout.addWidget(port_label)

        self.conn_btn = QPushButton("Connect")
        self.conn_btn.setFixedSize(90, 32)
        header_layout.addWidget(self.conn_btn)
        # Ensure connect button is wired to the connection toggle handler
        self.conn_btn.clicked.connect(self._toggle_connection)

        self.conn_status = QLabel("● Disconnected")
        self.conn_status.setStyleSheet("color: #ff0000; font-weight: bold;")
        self.conn_status.setFixedHeight(32)
        header_layout.addWidget(self.conn_status)

        main_layout.addWidget(header_frame)

        # Create tab widgets for both single and dual view
        self.single_tab_widget = QTabWidget()
        self.left_tab_widget = QTabWidget()
        self.right_tab_widget = QTabWidget()
        
        # Enable tab movability and set tab bar to allow dragging between widgets
        self.left_tab_widget.setMovable(True)
        self.right_tab_widget.setMovable(True)
        self.left_tab_widget.setTabsClosable(False)
        self.right_tab_widget.setTabsClosable(False)
        
        # Style all tab widgets
        tab_style = """
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
        """
        
        self.single_tab_widget.setStyleSheet(tab_style)
        self.left_tab_widget.setStyleSheet(tab_style)
        self.right_tab_widget.setStyleSheet(tab_style)

        # Create panels (single instances will be reused in both views)
        self.controls_panel = ControlsPanel()
        self.radar_panel = RadarPanel()
        self.scan_panel = ScanPanel()
        self.map_panel = MapPanel()
        self.sound_panel = SoundPanel()
        self.response_panel = ResponsePanel()

        # Link controls panel to map panel for position updates
        self.controls_panel.set_map_panel(self.map_panel)

        # Create splitter for dual view
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setStyleSheet("""
            QSplitter {
                background-color: #1a1a1a;
            }
            QSplitter::handle {
                background-color: #4a5c23;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #5a6c33;
            }
        """)

        # Content container that will switch between single/dual view
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Start in single view mode
        self.setup_single_view()
        self.content_layout.addWidget(self.single_tab_widget)
        
        main_layout.addWidget(self.content_container)

        # Create application menus
        self.create_menus()

    def setup_single_view(self):
        """Setup single view mode with all tabs in one widget"""
        self.single_tab_widget.clear()
        self.single_tab_widget.addTab(self.controls_panel, "CONTROLS")
        self.single_tab_widget.addTab(self.radar_panel, "RADAR")
        self.single_tab_widget.addTab(self.map_panel, "MAP")
        self.single_tab_widget.addTab(self.sound_panel, "SOUND")
        self.single_tab_widget.addTab(self.response_panel, "LOGS")
        
    def setup_dual_view(self):
        """Setup dual view mode with tabs split between two widgets (tabs are movable)"""
        # Clear both tab widgets
        self.left_tab_widget.clear()
        self.right_tab_widget.clear()
        
        # Default setup: Controls on left, others on right
        # Note: Tabs can be reordered by dragging within their widget
        self.left_tab_widget.addTab(self.controls_panel, "CONTROLS")
        
        self.right_tab_widget.addTab(self.radar_panel, "RADAR")
        self.right_tab_widget.addTab(self.map_panel, "MAP")
        self.right_tab_widget.addTab(self.sound_panel, "SOUND")
        self.right_tab_widget.addTab(self.response_panel, "LOGS")
        
        # Set splitter sizes (50% left, 50% right)
        self.main_splitter.setSizes([600, 600])

    def set_single_view(self):
        """Switch to single view mode"""
        if self.current_view_mode == "single":
            return
            
        self.current_view_mode = "single"
        
        # Clear content layout
        if self.main_splitter.parent():
            self.content_layout.removeWidget(self.main_splitter)
            self.main_splitter.setParent(None)
        
        # Setup single view
        self.setup_single_view()
        self.content_layout.addWidget(self.single_tab_widget)
        
        # Update button styles
        self.single_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5c23;
                color: #ffffff;
                min-width: 100px;
                padding: 8px;
            }
        """)
        self.dual_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4f2a;
                min-width: 100px;
                padding: 8px;
            }
        """)
        
        try:
            self.response_panel.log("✓ Switched to single view mode", connected=self.connection_manager.is_connected)
        except:
            pass
        
    def set_dual_view(self):
        """Switch to dual view mode"""
        if self.current_view_mode == "dual":
            return
            
        self.current_view_mode = "dual"
        
        # Clear content layout
        if self.single_tab_widget.parent():
            self.content_layout.removeWidget(self.single_tab_widget)
            self.single_tab_widget.setParent(None)
        
        # Setup dual view
        self.setup_dual_view()
        
        # Clear and rebuild splitter using replaceWidget
        while self.main_splitter.count() > 0:
            widget = self.main_splitter.widget(0)
            self.main_splitter.replaceWidget(0, QWidget())  # Replace with an empty widget
            widget.setParent(None)
            
        self.main_splitter.addWidget(self.left_tab_widget)
        self.main_splitter.addWidget(self.right_tab_widget)
        self.content_layout.addWidget(self.main_splitter)
        
        # Update button styles
        self.dual_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5c23;
                color: #ffffff;
                min-width: 100px;
                padding: 8px;
            }
        """)
        self.single_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4f2a;
                min-width: 100px;
                padding: 8px;
            }
        """)
        
        try:
            self.response_panel.log("✓ Switched to dual view mode", connected=self.connection_manager.is_connected)
        except:
            pass

    def setup_connections(self):
        """Connect signals between components"""
        # Attach connection manager and loggers to scan panel
        self.scan_panel.set_connection_manager(self.connection_manager)
        self.scan_panel.set_loggers(self.response_panel.log, self.response_panel.scan_log)

        # Attach connection manager and loggers to sound panel so it can update status and upload
        self.sound_panel.set_connection_manager(self.connection_manager)
        # Pass response panel logger and the sound panel's own status setter
        self.sound_panel.set_loggers(self.response_panel.log, self.sound_panel._set_status_text)
        
        # Radar panel IMU calibration button -> send calibration command
        self.radar_panel.calibrate_imu_requested.connect(self._on_imu_calibrate_requested)
        
        # Radar panel set north button -> send set north command
        self.radar_panel.set_north_requested.connect(self._on_set_north_requested)
        
        # Radar panel refresh button -> request compass update
        self.radar_panel.refresh_compass_requested.connect(self._on_refresh_compass_requested)

        # Controls panel movement commands -> connection manager
        self.controls_panel.movement_requested.connect(
            lambda cmd: self._send_command(cmd)
        )
        
        # Controls panel scan commands -> scan panel
        self.controls_panel.scan_requested.connect(
            lambda cmd: self.scan_panel.start_scan(cmd)
        )
        
        # Scan panel data updates -> radar panel
        self.scan_panel.scan_data_ready.connect(
            lambda angles, distances: self._update_radar_display(angles, distances)
        )
        
        # Update radar info when scanning status changes
        def update_radar_status():
            if hasattr(self.scan_panel, 'radar_info') and self.scan_panel.radar_info:
                text = self.scan_panel.radar_info.text()
                self.radar_panel.set_info_text(text)
        
        # Periodically sync radar info (simple approach)
        from PySide6.QtCore import QTimer
        self.radar_sync_timer = QTimer()
        self.radar_sync_timer.timeout.connect(update_radar_status)
        self.radar_sync_timer.start(500)  # Update every 500ms
        
        # Manual compass updates only - no automatic polling
        # Compass is only updated when:
        # 1. Initial connection (see on_connection_changed)
        # 2. After SET NORTH command
        # 3. After movement commands (if implemented)
        
        # Track calibration state
        self._calibrating = False

        # Sound panel upload_requested -> connection manager (non-blocking)
        self.sound_panel.upload_requested.connect(lambda path: (
            self.response_panel.log(f"🔊 Upload requested: {path}", connected=self.connection_manager.is_connected),
            self.connection_manager.send_command(f"upload:{path}", wait_for_response=False)
        ))

        # Sound panel song_play_requested -> connection manager (handled by helper)
        self.sound_panel.song_play_requested.connect(self._on_song_play_requested)

        # Sound panel song_clear_requested -> connection manager
        self.sound_panel.song_clear_requested.connect(self._on_song_clear_requested)

        # Connection message routing
        self.connection_manager.message_received.connect(self._on_message_received)
        self.connection_manager.error_occurred.connect(lambda e: self.response_panel.log(f"✗ CONNECTION ERROR: {e}", connected=self.connection_manager.is_connected))

        # Connection status updates
        self.connection_manager.connected_signal.connect(self.on_connection_changed)

    def _send_command(self, cmd):
        """Wrapper to send command via ConnectionManager and handle result"""
        # Log the command being sent with human-readable description
        self._log_command(cmd)
        
        success, response = self.connection_manager.send_command(cmd)
        if not success:
            # Show basic feedback in console for now
            print(f"Command failed: {response}")
            self.response_panel.log(f"✗ COMMAND FAILED: {response}", connected=self.connection_manager.is_connected)
        else:
            print(f"Command response: {response}")
            
        # Update map for movement commands (both single char and custom format)
        # Extract base command - handle both 'w' and 'f:50' formats
        base_cmd = cmd[0].lower() if cmd else ''
        if base_cmd in ['w', 'a', 's', 'd', 'f']:
            # Map 'f' (custom forward) to 'w' for visualization
            display_cmd = 'w' if base_cmd == 'f' else base_cmd
            self.controls_panel.update_robot_position(display_cmd)
    
    def _log_command(self, cmd):
        """Log command with human-readable description"""
        cmd_lower = cmd.lower()
        
        # Parse and format custom commands (e.g., "f:50", "l:45", "r:90")
        if ':' in cmd:
            parts = cmd.split(':')
            cmd_char = parts[0]
            value = parts[1] if len(parts) > 1 else '?'
            
            if cmd_char == 'f':
                log_msg = f"➜ MOVE FORWARD: {value} cm (custom distance)"
            elif cmd_char == 'l':
                log_msg = f"➜ TURN LEFT: {value}° (custom angle)"
            elif cmd_char == 'r':
                log_msg = f"➜ TURN RIGHT: {value}° (custom angle)"
            elif cmd_char == 'b':
                log_msg = f"➜ MOVE BACKWARD: {value} cm (custom distance)"
            else:
                log_msg = f"➜ COMMAND: {cmd}"
        else:
            # Standard single-character commands
            cmd_map = {
                'w': "➜ MOVE FORWARD: 10 cm",
                'a': "➜ TURN LEFT: 30°",
                's': "➜ MOVE BACKWARD: 10 cm",
                'd': "➜ TURN RIGHT: 30°",
                't': "➜ STOP",
                'e': "🚪 MANUAL EXIT STEP: Move forward ignoring borders (10 cm)",
                'x': "🚪 AUTO EXIT FIELD: Automatic 2-border crossing",
                'z': "🛑 HALT AUTO EXIT: Stop automatic exit mode",
                'p': "➜ SCAN: Point scan at 90°",
                'b': "➜ SCAN: Basic 0-180°",
                'o': "➜ SCAN: Object detection",
                'k': "➜ SCAN: Tape detection at 90°",
                'c': "🧭 IMU: Calibrate sensors (move in figure-8)",
                'n': "🧭 IMU: Set North reference heading",
                'g': "🧭 IMU: Get current compass heading",
                'h': "➜ HELP: Show available commands"
            }
            log_msg = cmd_map.get(cmd_lower, f"➜ COMMAND: {cmd}")
        
        self.response_panel.log(log_msg, connected=self.connection_manager.is_connected)
    
    def _update_radar_display(self, angles, distances):
        """Update radar panel with scan data"""
        ir_distances = self.scan_panel.live_scan_ir_distances if hasattr(self.scan_panel, 'live_scan_ir_distances') else None
        self.radar_panel.update_scan_data(angles, distances, ir_distances)
    
    def _on_imu_calibrate_requested(self):
        """Handle IMU calibration request from radar panel"""
        self.response_panel.log("🧭 IMU CALIBRATION: Starting calibration process...", connected=self.connection_manager.is_connected)
        
        # Set calibrating flag to prevent compass updates during calibration
        self._calibrating = True
        
        # Send calibration command to the embedded device (uppercase C)
        # The embedded code should handle the calibration procedure
        success, response = self.connection_manager.send_command('C', wait_for_response=True)
        
        if success:
            self.response_panel.log("🧭 IMU CALIBRATION: Command sent - move robot in figure-8 pattern", connected=self.connection_manager.is_connected)
        else:
            self.response_panel.log(f"🧭 IMU CALIBRATION: Failed - {response}", connected=self.connection_manager.is_connected)
        
        # Clear calibrating flag (will be cleared by completion message too)
        self._calibrating = False
    
    def _on_set_north_requested(self):
        """Handle set north reference request from radar panel"""
        self.response_panel.log("🧭 SET NORTH: Setting current heading as North reference...", connected=self.connection_manager.is_connected)
        
        # Send set north command to the embedded device
        success, response = self.connection_manager.send_command('n', wait_for_response=True)
        
        if success:
            self.response_panel.log("🧭 SET NORTH: Reference heading set - compass now shows 0° at this direction", connected=self.connection_manager.is_connected)
            
            # Reset the initial heading reference in radar panel
            self.radar_panel.initial_heading = None
            
            # Request updated compass data to refresh display
            import time
            time.sleep(0.1)  # Brief delay to let device process
            self.connection_manager.send_command('g', wait_for_response=False)
        else:
            self.response_panel.log(f"🧭 SET NORTH: Failed - {response}", connected=self.connection_manager.is_connected)

    def _on_refresh_compass_requested(self):
        """Handle compass refresh request from radar panel"""
        if self.connection_manager.is_connected and not self._calibrating:
            self.connection_manager.send_command('g', wait_for_response=False)

    def _toggle_connection(self):
        """Connect or disconnect using the ConnectionManager"""
        if self.connection_manager.is_connected:
            self.connection_manager.disconnect()
            return
        ip = self.conn_ip.text().strip()
        port = self.conn_port.text().strip()
        try:
            ok, msg = self.connection_manager.connect(ip, int(port))
            self.response_panel.log(f"→ CONNECT: {msg}", connected=self.connection_manager.is_connected)
            if not ok:
                QMessageBox.warning(self, "Connection Failed", f"{msg}")
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", str(e))

    def create_menus(self):
        """Create the application menus"""
        menubar = self.menuBar()
        try:
            # File menu
            file_menu = menubar.addMenu("File")
            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # View menu
            view_menu = menubar.addMenu("View")
            show_logs = QAction("Show Logs Tab", self)
            show_logs.triggered.connect(lambda: self.single_tab_widget.setCurrentWidget(self.response_panel) if self.current_view_mode == "single" else self.right_tab_widget.setCurrentWidget(self.response_panel))
            view_menu.addAction(show_logs)
            
            # Open separate log window
            open_log_window = QAction("Open Log Window", self)
            open_log_window.setShortcut("Ctrl+L")
            open_log_window.triggered.connect(self.show_log_window)
            view_menu.addAction(open_log_window)

            # Help menu
            help_menu = menubar.addMenu("Help")
            
            # Keyboard shortcuts help
            shortcuts_action = QAction("Keyboard Shortcuts", self)
            shortcuts_action.setShortcut("F1")
            shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
            help_menu.addAction(shortcuts_action)
            
            about_action = QAction("About", self)
            about_action.triggered.connect(lambda: QMessageBox.information(self, "About", "CyBot Control Center\nModular UI"))
            help_menu.addAction(about_action)
        except Exception:
            # Safely ignore if menus cannot be created in headless/test environments
            pass
    
    def show_keyboard_shortcuts(self):
        """Display keyboard shortcuts help dialog"""
        shortcuts_text = """
KEYBOARD SHORTCUTS
═══════════════════════════════════════

MOVEMENT CONTROLS:
  W - Move Forward (10 cm)
  A - Turn Left (30°)
  S - Move Backward (10 cm)
  D - Turn Right (30°)

SCAN CONTROLS:
  Q - Basic Scan (0-180° sweep)
  E - Object Detect (find objects + tape)
  F - Tape Detect (check for tape @90°)

OTHER:
  F1 - Show this help
  Ctrl+L - Open Log Window
  Ctrl+Q - Exit Application

TIP: Click on the main window to activate keyboard controls.
Avoid typing in text fields when using shortcuts.
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text.strip())

    def on_connection_changed(self, connected):
        """Handle UI updates on connection changes"""
        # Log connection change
        try:
            self.response_panel.log(f"✓ CONNECTION {'ESTABLISHED' if connected else 'CLOSED'}", connected=connected)
        except Exception:
            pass
        # Update connection controls
        try:
            if connected:
                self.conn_btn.setText("Disconnect")
                self.conn_status.setText("● Connected")
                self.conn_status.setStyleSheet(f"color: {COLORS['text_green']}; font-weight: bold;")
                
                # Request initial compass reading when connected
                import time
                time.sleep(0.5)  # Give device time to settle
                self.connection_manager.send_command('g', wait_for_response=False)
                self.response_panel.log("🧭 Requesting initial compass reading...", connected=True)
            else:
                self.conn_btn.setText("Connect")
                self.conn_status.setText("● Disconnected")
                self.conn_status.setStyleSheet(f"color: {COLORS['text_red']}; font-weight: bold;")
        except Exception:
            pass

    def _on_message_received(self, message):
        """Route incoming messages to log and scan parser"""
        # Always log raw message
        try:
            self.response_panel.log(f"← {message}", connected=self.connection_manager.is_connected)
        except Exception as e:
            print(f"Error logging message: {e}")

    def _on_message_received(self, message):
        """Route incoming messages to log and scan parser"""
        # Always log raw message
        try:
            self.response_panel.log(f"← {message}", connected=self.connection_manager.is_connected)
        except Exception as e:
            print(f"Error logging message: {e}")

        # Check for structured hazard message first (HZ,TYPE,SIDE)
        try:
            if message.startswith("HZ,"):
                # Process structured hazard message
                self.controls_panel.process_hazard_message(message)
                
                # Parse for logging
                parts = message.strip().split(',')
                if len(parts) >= 3:
                    hazard_type = parts[1].upper()
                    side = parts[2].upper()
                    
                    # Update map for border and bump detections
                    try:
                        if hazard_type == "BUMP":
                            self.map_panel.update_bump_location()
                            print("Map bump location updated for structured message")
                        elif hazard_type == "BORDER" or hazard_type == "EDGE":
                            self.map_panel.update_border_location()
                            print("Map border location updated for structured message")
                    except Exception as e:
                        print(f"Error updating map for structured hazard: {e}")
                    
                    alert_message = f"⚠️ HAZARD ALERT: {hazard_type} DETECTED"
                    if side != "NA" and side != "NONE":
                        alert_message += f" ({side} side)"
                    alert_message += "! Robot stopped and backed up."
                    
                    self.response_panel.log(alert_message, connected=self.connection_manager.is_connected)
                return  # Don't process as legacy hazard message
        except Exception as e:
            print(f"Error processing structured hazard message: {e}")

        # Legacy hazard detection indicators for controls and map (for backward compatibility)
        # ONLY process legacy hazards if the message starts with "HAZARD:" to avoid false positives from scan data
        # Skip legacy BUMP messages as they are handled by structured format (HZ,BUMP,SIDE)
        try:
            if "HAZARD:" in message.upper():
                # Skip bump detection in legacy format - it's handled by structured messages
                if "BUMP" in message.upper():
                    print(f"Legacy bump message detected but skipped (already handled by structured format): {message}")
                    return  # Skip processing to avoid double detection
                
                # Skip border/edge detection in legacy format - it's handled by structured messages
                if "BORDER" in message.upper() or "WHITE_TAPE" in message.upper() or "EDGE" in message.upper():
                    print(f"Legacy border/edge message detected but skipped (already handled by structured format): {message}")
                    return  # Skip processing to avoid double detection
                
                if "HOLE" in message.upper() or "CLIFF" in message.upper():
                    print(f"Hole/cliff detected in legacy message: {message}")
                    
                    # Parse cliff side from message
                    cliff_side = ""
                    if "LEFT" in message.upper():
                        cliff_side = "LEFT"
                    elif "RIGHT" in message.upper():
                        cliff_side = "RIGHT"
                    elif "CENTER" in message.upper():
                        cliff_side = "CENTER"
                    elif "BOTH" in message.upper():
                        cliff_side = "BOTH"
                    
                    try:
                        self.controls_panel.set_hole_detected(True, cliff_side)
                        print(f"Hole/cliff indicator updated successfully with side: {cliff_side}")
                    except Exception as e:
                        print(f"Error setting hole/cliff indicator: {e}")
                    # Log hazard detection
                    try:
                        side_text = f" ({cliff_side} side)" if cliff_side else ""
                        self.response_panel.log(f"⚠️ HAZARD ALERT: HOLE/CLIFF DETECTED{side_text}! Robot stopped and backed up.", connected=self.connection_manager.is_connected)
                    except Exception as e:
                        print(f"Error logging hole/cliff alert: {e}")
        except Exception as e:
            print(f"Error in hazard detection handler: {e}")
            import traceback
            traceback.print_exc()

        # If message looks like scan data, parse and log into scan log
        try:
            if any(keyword in message for keyword in ['PING=', 'IR=', 'SCAN', 'OBJECT', 'SMALLEST', 'STATUS:']):
                # parse with scan_panel, collect_for_plot True
                try:
                    self.scan_panel.parse_and_log_scan_data(message, collect_for_plot=True, logger=lambda m: self.response_panel.log(m, connected=self.connection_manager.is_connected), scan_logger=self.response_panel.scan_log)
                except Exception:
                    pass
        except Exception:
            pass
        
        # Handle IMU calibration status messages
        try:
            if "IMU_CALIBRATION_START" in message:
                self._calibrating = True
                self.response_panel.log("🧭 Calibration started - move robot in figure-8 pattern", connected=self.connection_manager.is_connected)
            elif "IMU_CALIBRATION_COMPLETE" in message:
                self._calibrating = False
                self.response_panel.log("🧭 Calibration complete!", connected=self.connection_manager.is_connected)
                # Request fresh compass data after calibration
                import time
                time.sleep(0.1)
                self.connection_manager.send_command('g', wait_for_response=False)
            elif "IMU_CALIB:" in message:
                # Log calibration progress
                self._calibrating = True
                # Don't log every update to avoid spam
        except Exception as e:
            print(f"Error handling IMU calibration message: {e}")
        
        # Parse compass data (format: "COMPASS: 123.4 N CAL:3,2")
        try:
            if "COMPASS:" in message:
                # Skip logging if it's just a routine compass update (starts with "COMPASS: " followed by a number)
                if message.startswith("COMPASS:") and len(message.split()) >= 4 and message.split()[1].replace('.','').replace('-','').isdigit():
                    # This is a routine compass reading - update display but don't log
                    parts = message.split()
                    heading_str = parts[1]
                    cardinal = parts[2]
                    cal_str = parts[3] if len(parts) > 3 else "CAL:0,0"
                    
                    try:
                        heading = float(heading_str)
                        
                        # Parse calibration values
                        sys_cal = 0
                        mag_cal = 0
                        if cal_str.startswith("CAL:"):
                            cal_values = cal_str[4:].split(',')
                            if len(cal_values) >= 2:
                                sys_cal = int(cal_values[0])
                                mag_cal = int(cal_values[1])
                        
                        # Update radar panel with compass data (silently)
                        self.radar_panel.update_compass_heading(heading, cardinal, sys_cal, mag_cal)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing compass data: {e}")
                    return  # Don't continue to raw message logging
                else:
                    # This is a compass status message (not a reading) - log it
                    self.response_panel.log(f"🧭 {message}", connected=self.connection_manager.is_connected)
                    return  # Don't continue to raw message logging
        except Exception as e:
            print(f"Error in compass message handler: {e}")

    def _on_song_play_requested(self, slot):
        """Handle play requests from the SoundPanel, match legacy behavior."""
        try:
            self.response_panel.log(f"🔊 Play requested: slot {slot}", connected=self.connection_manager.is_connected)
            # Use legacy commands: slot 2 -> '5', slot 3 -> '6', others map to builtins
            if slot == 2:
                cmd = '5'
            elif slot == 3:
                cmd = '6'
            elif slot == 0:
                cmd = 'k'  # OK beep
            elif slot == 1:
                cmd = 'n'  # ERROR beep
            else:
                cmd = 'p'  # system test
            success, resp = self.connection_manager.send_command(cmd, wait_for_response=False)
            # Update UI like legacy client
            if slot in (2, 3):
                self.sound_panel._set_status_text(f"SOUND CONTROL: ♪ Playing Slot {slot}", color="#00ddff")
        except Exception:
            pass

    def _on_song_clear_requested(self, slot):
        try:
            self.response_panel.log(f"🔊 Clear requested: slot {slot}", connected=self.connection_manager.is_connected)
            cmd = 'x' if slot == 2 else 'z'
            self.connection_manager.send_command(cmd, wait_for_response=False)
            # Update UI
            self.sound_panel._set_status_text(f"SOUND CONTROL: 🗑️ Cleared Slot {slot}", color="#ffaa00")
        except Exception:
            pass

    def show_log_window(self):
        """Show or create the separate log window"""
        if self.log_window is None:
            # Create new log window
            self.log_window = LogWindow(self)
            
            # Connect response panel logs to the log window
            self.response_panel.log_signal.connect(self.log_window.append_log)
            
            # Connect connection status updates
            self.connection_manager.connected_signal.connect(self.log_window.update_connection_status)
            
            # Handle window close
            self.log_window.window_closed.connect(self._on_log_window_closed)
            
            # Set initial connection status
            self.log_window.update_connection_status(self.connection_manager.is_connected)
        
        # Show and raise the window
        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()
    
    def _on_log_window_closed(self):
        """Handle log window being closed"""
        if self.log_window:
            # Disconnect signals
            try:
                self.response_panel.log_signal.disconnect(self.log_window.append_log)
                self.connection_manager.connected_signal.disconnect(self.log_window.update_connection_status)
            except:
                pass
            
            # Clear reference
            self.log_window = None

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for WASD movement controls and QEF scan controls"""
        # Only process if not typing in a text field
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QLineEdit):
            # Let text input fields handle their own keys
            super().keyPressEvent(event)
            return
        
        key = event.key()
        
        # Map WASD keys to movement commands
        if key == Qt.Key_W:
            self.response_panel.log("⌨️ KEY: W - FORWARD", connected=self.connection_manager.is_connected)
            self._send_command('w')
        elif key == Qt.Key_A:
            self.response_panel.log("⌨️ KEY: A - LEFT", connected=self.connection_manager.is_connected)
            self._send_command('a')
        elif key == Qt.Key_S:
            self.response_panel.log("⌨️ KEY: S - BACKWARD", connected=self.connection_manager.is_connected)
            self._send_command('s')
        elif key == Qt.Key_D:
            self.response_panel.log("⌨️ KEY: D - RIGHT", connected=self.connection_manager.is_connected)
            self._send_command('d')
        # Map QEF keys to scan commands
        elif key == Qt.Key_Q:
            self.response_panel.log("⌨️ KEY: Q - BASIC SCAN", connected=self.connection_manager.is_connected)
            self.scan_panel.start_scan('b')
        elif key == Qt.Key_E:
            self.response_panel.log("⌨️ KEY: E - OBJECT DETECT", connected=self.connection_manager.is_connected)
            self.scan_panel.start_scan('o')
        elif key == Qt.Key_F:
            # Trigger tape check button click (which handles continuous mode)
            self.response_panel.log("⌨️ KEY: F - TAPE CHECK", connected=self.connection_manager.is_connected)
            self.controls_panel._on_tape_check_clicked()
        elif key == Qt.Key_G:
            # Stop continuous tape check
            self.response_panel.log("⌨️ KEY: G - STOP CONTINUOUS", connected=self.connection_manager.is_connected)
            self.controls_panel._on_stop_continuous_clicked()
        else:
            # Pass other keys to default handler
            super().keyPressEvent(event)