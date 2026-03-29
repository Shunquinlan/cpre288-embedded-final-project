"""Combined controls panel with movement and scan operations"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QPushButton, QLabel, QFrame, QSplitter, QSpinBox, QCheckBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from utils import COLORS


class ControlsPanel(QWidget):
    """Combined widget for movement and scan controls"""

    # Signals
    movement_requested = Signal(str)  # Emits movement commands like 'w', 'a', 's', 'd'
    scan_requested = Signal(str)      # Emits scan commands like 'p', 'b', 'o', 'k'

    def __init__(self):
        super().__init__()
        self.map_panel = None
        self.init_ui()

    def init_ui(self):
        """Initialize the controls panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main title
        main_title = QLabel("◈ CYBOT CONTROL CENTER ◈")
        main_title.setFont(QFont("Courier New", 12, QFont.Bold))
        main_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_green']};
                background-color: {COLORS['bg_dark']};
                padding: 10px;
                border: 2px solid {COLORS['text_green']};
                border-radius: 5px;
            }}
        """)
        main_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(main_title)

        # Create horizontal splitter for movement and scan controls
        controls_splitter = QSplitter(Qt.Horizontal)
        controls_splitter.setStyleSheet("""
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

        # LEFT SIDE: Movement Controls
        movement_frame = self._create_movement_controls()
        controls_splitter.addWidget(movement_frame)

        # RIGHT SIDE: Scan Controls
        scan_frame = self._create_scan_controls()
        controls_splitter.addWidget(scan_frame)

        # Set initial sizes (40% movement, 60% scan)
        controls_splitter.setSizes([400, 600])

        layout.addWidget(controls_splitter)

    def _create_movement_controls(self):
        """Create movement control section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d3d1f;
                border: 2px solid #4a5c23;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("TACTICAL MOVEMENT")
        title.setFont(QFont("Courier New", 10, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_green']}; margin-top: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        # Movement parameters display
        params_label = QLabel("Distance: 10 cm | Turn: 30°")
        params_label.setFont(QFont("Courier New", 9, QFont.Bold))
        params_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_yellow']};
                background-color: rgba(74, 92, 35, 0.3);
                padding: 5px;
                border: 1px solid {COLORS['text_yellow']};
                border-radius: 4px;
                margin-bottom: 10px;
            }}
        """)
        params_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(params_label)

        # Movement buttons in grid (keyboard layout)
        btn_grid = QGridLayout()
        btn_grid.setSpacing(10)

        # Create buttons
        self.forward_btn = self._create_movement_button("ADVANCE (W)\n10 cm")
        self.forward_btn.clicked.connect(lambda: self.movement_requested.emit('w'))

        self.left_btn = self._create_movement_button("LEFT (A)\n30°")
        self.left_btn.clicked.connect(lambda: self.movement_requested.emit('a'))

        self.backward_btn = self._create_movement_button("RETREAT (S)\n10 cm")
        self.backward_btn.clicked.connect(lambda: self.movement_requested.emit('s'))

        self.right_btn = self._create_movement_button("RIGHT (D)\n30°")
        self.right_btn.clicked.connect(lambda: self.movement_requested.emit('d'))

        # Add to grid in keyboard pattern (W on top, A-S-D in one row)
        btn_grid.addWidget(self.forward_btn, 0, 1)
        btn_grid.addWidget(self.left_btn, 1, 0)
        btn_grid.addWidget(self.backward_btn, 1, 1)
        btn_grid.addWidget(self.right_btn, 1, 2)

        layout.addLayout(btn_grid)
        
        # ===== CUSTOM DISTANCE CONTROL SECTION =====
        custom_frame = QFrame()
        custom_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #5a5c23;
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        custom_layout = QVBoxLayout(custom_frame)
        custom_layout.setSpacing(8)
        
        # Custom control title
        custom_title = QLabel("◈ CUSTOM DISTANCE MODE ◈")
        custom_title.setFont(QFont("Courier New", 9, QFont.Bold))
        custom_title.setStyleSheet(f"color: {COLORS['text_cyan']}; border: none; padding: 2px;")
        custom_title.setAlignment(Qt.AlignCenter)
        custom_layout.addWidget(custom_title)
        
        # Distance input
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        
        distance_label = QLabel("Distance (cm):")
        distance_label.setFont(QFont("Courier New", 9, QFont.Bold))
        distance_label.setStyleSheet(f"color: {COLORS['text_yellow']}; border: none;")
        input_row.addWidget(distance_label)
        
        self.custom_distance_input = QSpinBox()
        self.custom_distance_input.setRange(1, 200)
        self.custom_distance_input.setValue(25)
        self.custom_distance_input.setSuffix(" cm")
        self.custom_distance_input.setFont(QFont("Courier New", 10, QFont.Bold))
        self.custom_distance_input.setStyleSheet("""
            QSpinBox {
                background-color: #2a2a1a;
                color: #00ff00;
                border: 2px solid #4a5c23;
                padding: 5px;
                border-radius: 4px;
                min-width: 80px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #3a4f2a;
                border: 1px solid #4a5c23;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4a5c23;
            }
        """)
        input_row.addWidget(self.custom_distance_input)
        input_row.addStretch()
        
        custom_layout.addLayout(input_row)
        
        # Custom move forward button
        self.custom_move_btn = QPushButton("VARIABLE MOVE FORWARD (SAFE)")
        self.custom_move_btn.setFont(QFont("Courier New", 10, QFont.Bold))
        self.custom_move_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a6a6a, stop:1 #3a5a5a);
                color: #00ffff;
                border: 2px solid #00ffff;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a7a7a, stop:1 #4a6a6a);
                border: 2px solid #ffffff;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a5a5a, stop:1 #2a4a4a);
            }
        """)
        self.custom_move_btn.clicked.connect(self._on_custom_move_clicked)
        custom_layout.addWidget(self.custom_move_btn)
        
        
        layout.addWidget(custom_frame)
        
        # ===== END CUSTOM DISTANCE SECTION =====
        
        # ===== EXIT MODE CONTROL SECTION =====
        exit_frame = QFrame()
        exit_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2a1a;
                border: 2px solid #5a7c23;
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        exit_layout = QVBoxLayout(exit_frame)
        exit_layout.setSpacing(8)
        
        # Exit control title
        exit_title = QLabel("◈ FIELD EXIT MODE ◈")
        exit_title.setFont(QFont("Courier New", 9, QFont.Bold))
        exit_title.setStyleSheet(f"color: #00ff00; border: none; padding: 2px;")
        exit_title.setAlignment(Qt.AlignCenter)
        exit_layout.addWidget(exit_title)
        
        # Exit mode description
        exit_desc = QLabel("Ignores white borders while\navoiding bumps & cliffs")
        exit_desc.setFont(QFont("Courier New", 8))
        exit_desc.setStyleSheet(f"color: {COLORS['text_yellow']}; border: none; padding: 2px;")
        exit_desc.setAlignment(Qt.AlignCenter)
        exit_layout.addWidget(exit_desc)
        
        # Manual Exit button (move_forward_exit)
        self.manual_exit_btn = QPushButton("MANUAL EXIT STEP (E)")
        self.manual_exit_btn.setFont(QFont("Courier New", 10, QFont.Bold))
        self.manual_exit_btn.setToolTip("Manual exit mode - move forward ignoring white borders.\nTracks border crossings across multiple presses.\nPress E key.")
        self.manual_exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a6a2a, stop:1 #1a5a1a);
                color: #00ff00;
                border: 2px solid #00ff00;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7a3a, stop:1 #2a6a2a);
                border: 2px solid #00ffff;
                color: #00ffff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a5a1a, stop:1 #0a4a0a);
            }
        """)
        self.manual_exit_btn.clicked.connect(lambda: self.movement_requested.emit('e'))
        exit_layout.addWidget(self.manual_exit_btn)
        
        # Auto Exit button (auto_exit_field)
        self.auto_exit_btn = QPushButton("AUTO EXIT FIELD (X)")
        self.auto_exit_btn.setFont(QFont("Courier New", 10, QFont.Bold))
        self.auto_exit_btn.setToolTip("Automatic field exit - drives forward ignoring white borders.\nAutomatically counts 2 border crossings and completes exit.\nPress X key or 'h' to halt.")
        self.auto_exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a6a2a, stop:1 #5a5a1a);
                color: #ffff00;
                border: 2px solid #ffff00;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7a7a3a, stop:1 #6a6a2a);
                border: 2px solid #ffffff;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a1a, stop:1 #4a4a0a);
            }
        """)
        self.auto_exit_btn.clicked.connect(lambda: self.movement_requested.emit('x'))
        exit_layout.addWidget(self.auto_exit_btn)
        
        # Halt auto exit button
        self.halt_exit_btn = QPushButton("HALT AUTO EXIT (Z)")
        self.halt_exit_btn.setFont(QFont("Courier New", 9, QFont.Bold))
        self.halt_exit_btn.setToolTip("Stop automatic exit and return to manual control.\nPress Z key.")
        self.halt_exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a2a2a;
                color: #ff6666;
                border: 2px solid #ff6666;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7a3a3a;
                border: 2px solid #ff8888;
                color: #ff8888;
            }
            QPushButton:pressed {
                background-color: #5a1a1a;
            }
        """)
        self.halt_exit_btn.clicked.connect(lambda: self.movement_requested.emit('z'))
        exit_layout.addWidget(self.halt_exit_btn)
        
        layout.addWidget(exit_frame)
        
        # ===== END EXIT MODE SECTION =====
        
        # Hazard Detection Indicators
        indicators_frame = QFrame()
        indicators_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #4a5c23;
                border-radius: 6px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        indicators_layout = QVBoxLayout(indicators_frame)
        indicators_layout.setSpacing(5)
        
        # Indicator title
        indicator_title = QLabel("HAZARD DETECTION")
        indicator_title.setFont(QFont("Courier New", 9, QFont.Bold))
        indicator_title.setStyleSheet(f"color: {COLORS['text_yellow']}; border: none; padding: 2px;")
        indicator_title.setAlignment(Qt.AlignCenter)
        indicators_layout.addWidget(indicator_title)
        
        # Bump indicator
        self.bump_indicator = QLabel("● BUMP: CLEAR")
        self.bump_indicator.setFont(QFont("Courier New", 8, QFont.Bold))
        self.bump_indicator.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #0a0a0a;
                padding: 5px;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
        """)
        self.bump_indicator.setAlignment(Qt.AlignCenter)
        indicators_layout.addWidget(self.bump_indicator)
        
        # Border indicator
        self.border_indicator = QLabel("● BORDER: CLEAR")
        self.border_indicator.setFont(QFont("Courier New", 8, QFont.Bold))
        self.border_indicator.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #0a0a0a;
                padding: 5px;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
        """)
        self.border_indicator.setAlignment(Qt.AlignCenter)
        indicators_layout.addWidget(self.border_indicator)
        
        # Hole/cliff indicator
        self.hole_indicator = QLabel("● HOLE/CLIFF: CLEAR")
        self.hole_indicator.setFont(QFont("Courier New", 8, QFont.Bold))
        self.hole_indicator.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #0a0a0a;
                padding: 5px;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
        """)
        self.hole_indicator.setAlignment(Qt.AlignCenter)
        indicators_layout.addWidget(self.hole_indicator)
        
        # Reset indicators button
        reset_indicators_btn = QPushButton("CLEAR ALERTS")
        reset_indicators_btn.setFont(QFont("Courier New", 8, QFont.Bold))
        reset_indicators_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a1a;
                color: #ffff00;
                border: 1px solid #5a5a2a;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a2a;
                border: 1px solid #6a6a3a;
            }
            QPushButton:pressed {
                background-color: #2a2a1a;
            }
        """)
        reset_indicators_btn.clicked.connect(self.reset_hazard_indicators)
        indicators_layout.addWidget(reset_indicators_btn)
        
        layout.addWidget(indicators_frame)
        layout.addStretch()

        return frame

    def _create_scan_controls(self):
        """Create scan control section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d3d1f;
                border: 2px solid #4a5c23;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("SCAN OPERATIONS")
        title.setFont(QFont("Courier New", 10, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_green']}; margin-top: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Basic Scan and Object Detect buttons ---
        btn_map = [
            ("BASIC SCAN (Q)", 'b', "Simple 0-180°\nIR distance scan\nPress Q key"),
            ("OBJECT DETECT (E)", 'o', "Advanced object\ndetection + PING\nPress E key"),
        ]

        for text, cmd, tooltip in btn_map:
            btn = self._create_scan_button(text, tooltip)
            btn.clicked.connect(lambda _, x=cmd: self.scan_requested.emit(x))
            layout.addWidget(btn)

        # --- Tape Detect at Angle Control ---
        tape_frame = QFrame()
        tape_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #5a5c23;
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        tape_layout = QVBoxLayout(tape_frame)
        tape_layout.setSpacing(8)

        tape_title = QLabel("◈ TAPE CHECK AT ANGLE ◈")
        tape_title.setFont(QFont("Courier New", 9, QFont.Bold))
        tape_title.setStyleSheet(f"color: {COLORS['text_cyan']}; border: none; padding: 2px;")
        tape_title.setAlignment(Qt.AlignCenter)
        tape_layout.addWidget(tape_title)

        tape_input_row = QHBoxLayout()
        tape_input_row.setSpacing(10)

        angle_label = QLabel("Angle (0-180):")
        angle_label.setFont(QFont("Courier New", 9, QFont.Bold))
        angle_label.setStyleSheet(f"color: {COLORS['text_yellow']}; border: none;")
        tape_input_row.addWidget(angle_label)

        self.tape_angle_input = QSpinBox()
        self.tape_angle_input.setRange(0, 180)
        self.tape_angle_input.setValue(90)
        self.tape_angle_input.setSuffix("°")
        self.tape_angle_input.setFont(QFont("Courier New", 10, QFont.Bold))
        self.tape_angle_input.setStyleSheet("""
            QSpinBox {
                background-color: #2a2a1a;
                color: #00ff00;
                border: 2px solid #4a5c23;
                padding: 5px;
                border-radius: 4px;
                min-width: 70px;
            }
        """)
        tape_input_row.addWidget(self.tape_angle_input)
        tape_input_row.addStretch()
        tape_layout.addLayout(tape_input_row)

        # Continuous mode checkbox
        self.continuous_tape_check = QCheckBox("Continuous Mode")
        self.continuous_tape_check.setFont(QFont("Courier New", 9, QFont.Bold))
        self.continuous_tape_check.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_yellow']};
                spacing: 8px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #4a5c23;
                border-radius: 3px;
                background-color: #2a2a1a;
            }}
            QCheckBox::indicator:checked {{
                background-color: #00ff00;
                border: 2px solid #00ff00;
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid #00ffff;
            }}
        """)
        self.continuous_tape_check.setToolTip("When enabled, tape check will run continuously at the specified angle.")
        tape_layout.addWidget(self.continuous_tape_check)

        self.tape_check_btn = QPushButton("CHECK TAPE (F)")
        self.tape_check_btn.setFont(QFont("Courier New", 10, QFont.Bold))
        self.tape_check_btn.setToolTip("Checks for tape at the specified angle using PING and IR sensors.\nPress F key.\nEnable Continuous Mode for repeated checking.")
        self.tape_check_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a6a6a, stop:1 #3a5a5a);
                color: #00ffff;
                border: 2px solid #00ffff;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a7a7a, stop:1 #4a6a6a);
            }
        """)
        self.tape_check_btn.clicked.connect(self._on_tape_check_clicked)
        tape_layout.addWidget(self.tape_check_btn)
        
        # Stop continuous button
        self.stop_continuous_btn = QPushButton("STOP CONTINUOUS (G)")
        self.stop_continuous_btn.setFont(QFont("Courier New", 9, QFont.Bold))
        self.stop_continuous_btn.setToolTip("Stop continuous tape checking.\nPress G key.")
        self.stop_continuous_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a2a2a;
                color: #ff6666;
                border: 2px solid #ff6666;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7a3a3a;
                border: 2px solid #ff8888;
                color: #ff8888;
            }
            QPushButton:pressed {
                background-color: #5a1a1a;
            }
        """)
        self.stop_continuous_btn.clicked.connect(self._on_stop_continuous_clicked)
        self.stop_continuous_btn.setVisible(False)  # Hidden until continuous mode starts
        tape_layout.addWidget(self.stop_continuous_btn)
        
        layout.addWidget(tape_frame)
        layout.addStretch()

        return frame

    def _create_movement_button(self, text):
        """Create a styled movement button"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4f2a;
                color: #00ff00;
                border: 2px solid #4a5c23;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                font-family: 'Courier New', monospace;
                min-width: 100px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #4a5c23;
                color: #ffffff;
                border: 2px solid #00ffff;
            }
            QPushButton:pressed {
                background-color: #2a3f1a;
            }
        """)
        return btn

    def _create_scan_button(self, text, tooltip):
        """Create a styled scan button"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
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
                min-height: 50px;
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
        """)
        return btn

    def set_map_panel(self, map_panel):
        """Optional: link to map panel for visual updates"""
        self.map_panel = map_panel

    def update_robot_position(self, direction):
        """Update robot position based on movement direction and update map panel if set."""
        if self.map_panel:
            self.map_panel.update_robot_position(direction)

    def reset_robot_position(self):
        if self.map_panel:
            self.map_panel.reset_robot_position()

    def clear_movement_trail(self):
        if self.map_panel:
            self.map_panel.clear_movement_trail()
    
    def set_bump_detected(self, detected=True, side=""):
        """Update bump indicator status with specific side information"""
        if detected:
            if side:
                self.bump_indicator.setText(f"● BUMP: {side} HIT!")
            else:
                self.bump_indicator.setText("● BUMP: DETECTED!")
            self.bump_indicator.setStyleSheet("""
                QLabel {
                    color: #ff6600;
                    background-color: #3a1a0a;
                    padding: 5px;
                    border: 2px solid #ff6600;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.bump_indicator.setText("● BUMP: CLEAR")
            self.bump_indicator.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    background-color: #0a0a0a;
                    padding: 5px;
                    border: 1px solid #00ff00;
                    border-radius: 4px;
                }
            """)
    
    def set_border_detected(self, detected=True, side=""):
        """Update border indicator status with specific side information"""
        if detected:
            if side:
                self.border_indicator.setText(f"● BORDER: {side} DETECTED!")
            else:
                self.border_indicator.setText("● BORDER: DETECTED!")
            self.border_indicator.setStyleSheet("""
                QLabel {
                    color: #ff00ff;
                    background-color: #3a0a3a;
                    padding: 5px;
                    border: 2px solid #ff00ff;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.border_indicator.setText("● BORDER: CLEAR")
            self.border_indicator.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    background-color: #0a0a0a;
                    padding: 5px;
                    border: 1px solid #00ff00;
                    border-radius: 4px;
                }
            """)
    
    def set_hole_detected(self, detected=True, side=""):
        """Update hole/cliff indicator status with specific side information"""
        if detected:
            if side:
                self.hole_indicator.setText(f"● HOLE/CLIFF: {side} DETECTED!")
            else:
                self.hole_indicator.setText("● HOLE/CLIFF: DETECTED!")
            self.hole_indicator.setStyleSheet("""
                QLabel {
                    color: #ff4444;
                    background-color: #3a1a1a;
                    padding: 5px;
                    border: 2px solid #ff4444;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.hole_indicator.setText("● HOLE/CLIFF: CLEAR")
            self.hole_indicator.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    background-color: #0a0a0a;
                    padding: 5px;
                    border: 1px solid #00ff00;
                    border-radius: 4px;
                }
            """)
    
    def reset_hazard_indicators(self):
        """Clear all hazard indicators"""
        self.set_bump_detected(False)
        self.set_border_detected(False)
        self.set_hole_detected(False)
    
    def _on_custom_move_clicked(self):
        distance = self.custom_distance_input.value()
        command = f"m{distance}"  # e.g., "m50"
        self.movement_requested.emit(command)

    def _on_tape_check_clicked(self):
        angle = self.tape_angle_input.value()
        
        # Check if continuous mode is enabled
        if self.continuous_tape_check.isChecked():
            # Send continuous tape check command with 'K' prefix (uppercase)
            command = f"K{angle}"  # e.g., "K90" for continuous mode
            print(f"Starting continuous tape check at {angle}°")
            self.stop_continuous_btn.setVisible(True)
            self.tape_check_btn.setEnabled(False)
        else:
            # Send single tape check command with 'k' prefix (lowercase)
            command = f"k{angle}"  # e.g., "k90" for single check
            print(f"Single tape check at {angle}°")
        
        self.scan_requested.emit(command)
    
    def _on_stop_continuous_clicked(self):
        """Stop continuous tape checking"""
        # Send stop command (lowercase 'g')
        self.scan_requested.emit('g')
        print("Stopping continuous tape check")
        self.stop_continuous_btn.setVisible(False)
        self.tape_check_btn.setEnabled(True)
        self.continuous_tape_check.setChecked(False)
    
    def test_indicators(self):
        """Test all hazard indicators with different side scenarios"""
        import time
        from PySide6.QtCore import QThread
        
        print("Testing hazard indicators with side information...")
        
        # Test bump detection with different sides
        print("Testing LEFT bump...")
        self.set_bump_detected(True, "LEFT")
        QThread.msleep(1500)
        
        print("Testing RIGHT bump...")
        self.set_bump_detected(True, "RIGHT")
        QThread.msleep(1500)
        
        print("Testing CENTER bump...")
        self.set_bump_detected(True, "CENTER")
        QThread.msleep(1500)
        
        # Test border detection with sides
        print("Testing LEFT border...")
        self.set_border_detected(True, "LEFT")
        QThread.msleep(1500)
        
        print("Testing RIGHT border...")
        self.set_border_detected(True, "RIGHT")
        QThread.msleep(1500)
        
        print("Testing BOTH border...")
        self.set_border_detected(True, "BOTH")
        QThread.msleep(1500)
        
        # Test hole/cliff detection with sides
        print("Testing LEFT cliff...")
        self.set_hole_detected(True, "LEFT")
        QThread.msleep(1500)
        
        print("Testing CENTER cliff...")
        self.set_hole_detected(True, "CENTER")
        QThread.msleep(1500)
        
        # Test structured hazard messages
        print("Testing structured hazard messages...")
        self.process_hazard_message("HZ,BUMP,LEFT")
        QThread.msleep(1500)
        
        self.process_hazard_message("HZ,BORDER,RIGHT")
        QThread.msleep(1500)
        
        self.process_hazard_message("HZ,CLIFF,CENTER")
        QThread.msleep(1500)
        
        # Clear all indicators
        print("Clearing all indicators...")
        self.reset_hazard_indicators()
        
        print("Indicator test complete!")
        
        print("Testing border indicator...")
        self.set_border_detected(True)
        QThread.sleep(1)
        self.set_border_detected(False)
        
        print("Testing hole indicator...")
        self.set_hole_detected(True)
        QThread.sleep(1)
        self.set_hole_detected(False)
        
        print("Testing completed.")
    
    def process_hazard_message(self, message):
        """Process hazard message from CyBot (format: HZ,TYPE,SIDE or legacy HAZARD format)"""
        try:
            # Handle new structured format (HZ,TYPE,SIDE)
            if message.startswith("HZ,"):
                parts = message.strip().split(',')
                if len(parts) >= 3 and parts[0] == "HZ":
                    hazard_type = parts[1].upper()
                    side = parts[2].upper()
                    
                    print(f"Processing structured hazard: Type={hazard_type}, Side={side}")
                    
                    # Clear all indicators first
                    self.reset_hazard_indicators()
                    
                    # Set the appropriate indicator based on type
                    if hazard_type == "BUMP":
                        print(f"Setting BUMP indicator for side: {side}")
                        self.set_bump_detected(True, side)
                    elif hazard_type == "BORDER" or hazard_type == "EDGE":
                        print(f"Setting BORDER indicator for side: {side}")
                        self.set_border_detected(True, side)
                    elif hazard_type == "CLIFF" or hazard_type == "HOLE":
                        print(f"Setting HOLE indicator for side: {side}")
                        self.set_hole_detected(True, side)
                    else:
                        print(f"Unknown hazard type: {hazard_type}")
                        
            # Handle legacy format (HAZARD: TYPE detected)
            elif "HAZARD:" in message:
                print(f"Processing legacy hazard message: {message}")
                # Only process legacy messages if they're not contradicting recent structured messages
                # This is a fallback for compatibility, but structured messages take priority
                if "BUMPER" in message.upper() or "BUMP" in message.upper():
                    # Only set bump if we haven't just processed an EDGE/BORDER message
                    print("Legacy bump message detected - ignoring if recent EDGE/BORDER was processed")
                    # Don't process legacy bump messages as they may be false positives
                    return
                    
            else:
                print(f"Unknown message format: {message}")
                    
        except Exception as e:
            print(f"Error processing hazard message: {e}")
