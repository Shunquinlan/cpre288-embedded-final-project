# CyBot Military Command Center - GUI Overview

## Table of Contents
1. [GUI Overview](#gui-overview)
2. [Technology Stack](#technology-stack)
3. [GUI Architecture](#gui-architecture)
4. [Main Window](#main-window)
5. [Control Panels](#control-panels)
6. [Visualization Panels](#visualization-panels)
7. [Communication System](#communication-system)
8. [User Interaction Flow](#user-interaction-flow)
9. [Running the GUI](#running-the-gui)

---

## GUI Overview

**Application Name:** CyBot Military Command Center GUI  
**Purpose:** Remote control and monitoring interface for CyBot robot  
**Framework:** PySide6 (Qt for Python)  
**Team Members:** Adrian Thongsavath, Noah Gratz, Deraj Balamurugan, Shun Quinlan, Lex Marshall

The GUI is a comprehensive desktop application that provides:
- **Real-time remote control** via WiFi socket connection
- **Live data visualization** including radar displays and object maps
- **Environmental scanning control** with multiple sensor modes
- **MIDI sound playback** system
- **Command/response logging** and monitoring
- **Dual-view and single-view modes** for flexible layouts

---

## Technology Stack

### Core Technologies
- **PySide6 (Qt 6):** Cross-platform GUI framework providing widgets, layouts, and event handling
- **Python 3.x:** Programming language for application logic
- **Socket (TCP/IP):** Network communication with the CyBot
- **Threading (QThread):** Non-blocking background operations for network I/O
- **Signals and Slots:** Qt's event system for component communication

### Key Python Libraries
- `PySide6.QtWidgets` - UI components (buttons, panels, layouts)
- `PySide6.QtCore` - Core functionality (threads, signals, timers)
- `PySide6.QtGui` - Graphics and fonts
- `socket` - TCP socket communication
- `pathlib` - File system operations
- Custom MIDI parser for sound file processing

---

## GUI Architecture

### Application Structure

```
┌───────────────────────────────────────────────────────────────┐
│                   CyBotMainWindow                             │
│  ┌─────────────────────────────────────────────────────┐     │
│  │           Header (Connection Controls)               │     │
│  │  - IP Address / Port Input                          │     │
│  │  - Connect/Disconnect Buttons                       │     │
│  │  - View Mode Toggle (Single/Dual)                   │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              Main Content Area                       │     │
│  │                                                      │     │
│  │  Single View Mode:                                  │     │
│  │  ┌────────────────────────────────────────┐        │     │
│  │  │          Tab Widget                    │        │     │
│  │  │  • Controls Tab                        │        │     │
│  │  │  • Radar Tab                           │        │     │
│  │  │  • Scan Data Tab                       │        │     │
│  │  │  • Map Tab                             │        │     │
│  │  │  • Sound Tab                           │        │     │
│  │  │  • Response Tab                        │        │     │
│  │  └────────────────────────────────────────┘        │     │
│  │                                                      │     │
│  │  Dual View Mode:                                    │     │
│  │  ┌──────────────┬──────────────────────────┐       │     │
│  │  │   Controls   │    Visualization Panel   │       │     │
│  │  │    Panel     │    (Radar/Map/Scan)      │       │     │
│  │  └──────────────┴──────────────────────────┘       │     │
│  └─────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                   Log Window (Separate)                       │
│  • Command history                                            │
│  • Response messages from CyBot                               │
│  • System logs and errors                                     │
│  • Color-coded message types                                  │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│              Connection Manager (Background)                  │
│  • TCP Socket Management                                      │
│  • Receiver Worker Thread                                     │
│  • Signal Emission for GUI Updates                            │
└───────────────────────────────────────────────────────────────┘
```

### Component Organization

**Main Components:**
1. **Main Window** (`main_window.py`) - Application container and layout manager
2. **Controls Panel** (`controls_panel.py`) - Movement and scan command interface
3. **Radar Panel** (`radar_panel.py`) - Polar plot visualization
4. **Map Panel** (`map_panel.py`) - 2D overhead object map
5. **Scan Panel** (`scan_panel.py`) - Tabular data display
6. **Sound Panel** (`sound_panel.py`) - MIDI player and sound controls
7. **Response Panel** (`response_panel.py`) - Command response viewer
8. **Log Window** (`log_window.py`) - Separate window for detailed logging
9. **Connection Manager** (`connection_manager.py`) - Network communication handler

**Supporting Modules:**
- **Utils** (`utils.py`) - Shared styling, colors, and utility functions
- **MIDI Parser** (`midi_parser.py`) - MIDI file processing
- **GUI Client** (`gui_client.py`) - Legacy client interface

---

## Main Window

### File: `main_window.py`

**Purpose:** Top-level application window that serves as the container for all GUI panels and manages the overall layout.

**Key Responsibilities:**
- Create and organize all child panels
- Manage connection to CyBot (IP/port configuration)
- Handle view mode switching (single vs. dual view)
- Coordinate signal/slot connections between components
- Provide menu bar for file operations
- Launch and manage the log window

**Main Features:**

#### Connection Controls
Located in the header section:
```python
# IP and Port inputs
self.conn_ip = QLineEdit("192.168.1.1")
self.conn_port = QLineEdit("288")

# Connect/Disconnect buttons
self.conn_connect_btn = QPushButton("CONNECT")
self.conn_disconnect_btn = QPushButton("DISCONNECT")
```

**Connection Flow:**
1. User enters target IP address and port number
2. User clicks "CONNECT" button
3. Main window calls `connection_manager.connect(ip, port)`
4. Status indicator updates to show connection state
5. All panels are enabled and ready for interaction

#### View Mode Switching

**Single View Mode:**
- All panels organized in tabs
- One panel visible at a time
- Clean, focused interface
- Good for smaller screens

**Dual View Mode:**
- Split-screen layout
- Controls on left, visualization on right
- Multiple panels visible simultaneously
- Better for large displays

```python
def set_single_view(self):
    """Switch to tabbed single-view layout"""
    # Reorganize panels into tab widget
    
def set_dual_view(self):
    """Switch to split-screen dual-view layout"""
    # Reorganize panels into splitter widget
```

#### Menu Bar
Provides file operations and settings:
- **File Menu:** Open, Save, Export data
- **View Menu:** Toggle panels, view mode selection
- **Tools Menu:** Settings, calibration options
- **Help Menu:** About, documentation

#### Signal Connections
Connects all components together:
```python
# Movement commands from controls → connection manager
self.controls_panel.movement_requested.connect(
    self.connection_manager.send_command
)

# Scan commands from controls → connection manager
self.controls_panel.scan_requested.connect(
    self.connection_manager.send_command
)

# Incoming messages → all display panels
self.connection_manager.message_received.connect(
    self.radar_panel.process_message
)
self.connection_manager.message_received.connect(
    self.map_panel.process_message
)
```

---

## Control Panels

### Controls Panel (`controls_panel.py`)

**Purpose:** Primary user interface for sending commands to the CyBot.

**Layout:** Split into two main sections - Movement Controls and Scan Controls

#### Movement Controls Section

**Directional Buttons:**
- **Forward (W):** Move robot forward
- **Left (A):** Turn robot left
- **Backward (S):** Move robot backward  
- **Right (D):** Turn robot right
- **Stop (T):** Emergency stop

**Configuration Controls:**
- **Distance Spinbox:** Set movement distance (1-999 cm)
- **Angle Spinbox:** Set turn angle (1-360°)
- **Speed Selector:** Choose movement speed (if supported)

**Button Layout:**
```
        ┌───┐
        │ W │  Forward
        └───┘
  ┌───┐ ┌───┐ ┌───┐
  │ A │ │ S │ │ D │  Left, Back, Right
  └───┘ └───┘ └───┘
        ┌───┐
        │ T │  Stop
        └───┘
```

**Implementation:**
```python
def on_forward_clicked(self):
    distance = self.distance_spinbox.value()
    command = f"w{distance}"
    self.movement_requested.emit(command)

def on_left_clicked(self):
    angle = self.angle_spinbox.value()
    command = f"a{angle}"
    self.movement_requested.emit(command)
```

**Keyboard Shortcuts:**
- Press `W` key for forward
- Press `A` key for left
- Press `S` key for backward
- Press `D` key for right
- Press `T` key for stop

#### Scan Controls Section

**Scan Modes:**

1. **Basic PING Scan (p)**
   - 180° sweep using PING sensor only
   - Returns distance measurements
   - Fastest scan mode

2. **Object Detection (o)**
   - Complete scan with object identification
   - Uses PING, IR, and tape sensors
   - Automatically detects discrete objects
   - Calculates object positions and dimensions

3. **Compass Scan (k)**
   - Includes IMU heading data
   - Shows cardinal directions
   - Useful for orientation tracking

4. **Advanced Scans**
   - IR-only scan
   - Combined sensor scan
   - Custom angle ranges

**Scan Configuration:**
```python
# Scan options
self.scan_angle_start = QSpinBox()  # Start angle (default: 0°)
self.scan_angle_end = QSpinBox()    # End angle (default: 180°)
self.scan_step = QSpinBox()         # Step size (default: 2°)
```

**Implementation:**
```python
def on_object_scan_clicked(self):
    """Trigger object detection scan"""
    command = "o"
    self.scan_requested.emit(command)
    self.status_label.setText("Scanning...")
```

#### Visual Feedback

- **Button Highlighting:** Pressed buttons show visual feedback
- **Status Labels:** Display current operation
- **Progress Indicators:** Show scan progress
- **Command History:** Recent commands displayed

---

## Visualization Panels

### Radar Panel (`radar_panel.py`)

**Purpose:** Real-time polar plot visualization of distance sensor data.

**Display Type:** Polar coordinate system (angle vs. distance)

**How It Works:**

1. **Initialization:**
   - Creates polar plot with 180° range (0° to 180°)
   - Sets up distance rings (concentric circles)
   - Configures angle labels

2. **Data Reception:**
   - Listens for messages in format: `P:angle,distance`
   - Example: `P:90,45.5` means 45.5 cm at 90°

3. **Plotting:**
   - Converts angle/distance to polar coordinates
   - Plots point in real-time as data arrives
   - Updates sweep line to show current scan position

4. **Visualization Features:**
   - Green radar sweep line
   - Distance rings (e.g., 25cm, 50cm, 75cm, 100cm)
   - Angle markers (0°, 45°, 90°, 135°, 180°)
   - Real-time point plotting
   - Military-style green-on-black theme

**Coordinate System:**
```
        90° (Forward)
           │
           │
           │
0° ────────●──────── 180°
  (Right) Robot (Left)
```

**Implementation:**
```python
def process_message(self, message):
    """Process incoming scan data"""
    if message.startswith("P:"):
        parts = message[2:].split(',')
        angle = int(parts[0])
        distance = float(parts[1])
        self.plot_point(angle, distance)
        
def plot_point(self, angle, distance):
    """Add point to polar plot"""
    # Convert to radians for plotting
    theta = math.radians(angle)
    self.scan_data.append((theta, distance))
    self.update_plot()
```

**User Interactions:**
- Clear button: Reset the radar display
- Export button: Save scan data to file
- Zoom controls: Adjust distance scale

### Map Panel (`map_panel.py`)

**Purpose:** 2D overhead view showing detected objects in Cartesian coordinates.

**Display Type:** Top-down map with robot at center

**How It Works:**

1. **Coordinate System:**
   - Robot positioned at origin (0, 0)
   - X-axis: left (-) to right (+)
   - Y-axis: backward (-) to forward (+)
   - Grid overlay for scale reference

2. **Data Reception:**
   - Listens for messages in format: `OBJECT:angle,width,distance,linWidth`
   - Example: `OBJECT:45,12,50.3,10.5`
     - Object at 45° angle
     - 12° angular width
     - 50.3 cm distance
     - 10.5 cm linear width

3. **Coordinate Conversion:**
   ```python
   # Polar to Cartesian conversion
   x = distance * cos(angle)
   y = distance * sin(angle)
   ```

4. **Rendering:**
   - Draws robot as circle/triangle at center
   - Renders objects as rectangles at calculated positions
   - Shows object dimensions
   - Color-codes objects by type (if detected)

**Map Features:**
- Grid lines every 10 cm
- Distance scale indicator
- Object labels with measurements
- Robot orientation indicator
- Clear/reset button
- Export map as image

**Implementation:**
```python
def process_message(self, message):
    """Process object detection data"""
    if message.startswith("OBJECT:"):
        data = message[7:].split(',')
        angle = float(data[0])
        width = float(data[1])
        distance = float(data[2])
        lin_width = float(data[3])
        
        self.add_object(angle, width, distance, lin_width)
        
def add_object(self, angle, width, distance, lin_width):
    """Add object to map"""
    # Convert polar to Cartesian
    angle_rad = math.radians(angle)
    x = distance * math.cos(angle_rad)
    y = distance * math.sin(angle_rad)
    
    # Create object representation
    obj = ObjectRect(x, y, lin_width, angle)
    self.objects.append(obj)
    self.update()
```

### Scan Panel (`scan_panel.py`)

**Purpose:** Detailed tabular view of all scan data points.

**Display Type:** Spreadsheet-style table with columns

**Table Columns:**
1. **Angle (°):** Servo angle position
2. **PING (cm):** PING sensor distance reading
3. **IR (cm):** IR sensor distance reading
4. **Tape:** Boolean flag for tape detection
5. **Notes:** Additional information or flags

**Data Population:**
```python
def process_message(self, message):
    """Add scan data to table"""
    if message.startswith("P:"):
        angle, distance = self.parse_ping_data(message)
        self.update_row(angle, ping_dist=distance)
        
    elif message.startswith("I:"):
        angle, distance = self.parse_ir_data(message)
        self.update_row(angle, ir_dist=distance)
        
    elif message.startswith("T:"):
        angle, has_tape = self.parse_tape_data(message)
        self.update_row(angle, tape=has_tape)
```

**Features:**
- Sortable columns
- Export to CSV
- Highlight anomalies (sudden distance changes)
- Filter by criteria
- Statistics summary (min, max, average distances)

### Sound Panel (`sound_panel.py`)

**Purpose:** MIDI file player for uploading and playing custom sounds on the robot.

**Features:**

#### MIDI File Selection
```python
def load_midi_file(self):
    """Open file dialog to select MIDI file"""
    file_path = QFileDialog.getOpenFileName(
        self, "Select MIDI File", "", "MIDI Files (*.mid *.midi)"
    )
    if file_path:
        self.parse_and_display(file_path)
```

#### MIDI Parsing
Uses `midi_parser.py` to extract:
- Note numbers (MIDI standard 0-127)
- Note durations (converted to 1/64 second units)
- Tempo information

**Limitations:**
- Maximum 16 notes per song (iRobot limitation)
- Only melody line (no chords)
- Songs stored in slots 0-3 (slot 4 reserved for system)

#### Sound Controls

**Upload Section:**
```
┌─────────────────────────────┐
│  [Select MIDI File]         │
│  File: darude-sandstorm.mid │
│  Notes: 16 | Duration: 8s   │
│  [Upload to Slot 0] [Play]  │
└─────────────────────────────┘
```

**Predefined Sounds:**
- OK Beep
- Error Tone
- Soldier Found Alarm
- End Mission Theme

**Implementation:**
```python
def upload_song(self):
    """Upload parsed MIDI to robot"""
    slot = self.slot_selector.currentIndex()
    notes = self.parsed_notes
    durations = self.parsed_durations
    
    # Format command
    notes_str = ','.join(map(str, notes))
    durs_str = ','.join(map(str, durations))
    command = f"SOUND_LOAD:{slot},{notes_str};{durs_str}"
    
    self.send_command.emit(command)
    
def play_song(self):
    """Play uploaded song"""
    slot = self.slot_selector.currentIndex()
    command = f"SOUND_PLAY:{slot}"
    self.send_command.emit(command)
```

**Slot Management:**
- View which slots are occupied
- Clear individual slots
- Preview note sequences

### Response Panel (`response_panel.py`)

**Purpose:** Display real-time responses and status messages from the CyBot.

**Message Types:**

1. **Status Messages:** `OK`, `DONE`, `READY`
2. **Error Messages:** `ERROR:description`
3. **Hazard Reports:** `HAZARD:type,sensor,value`
4. **Compass Data:** `COMPASS:heading,cardinal`
5. **System Logs:** `SYSTEM_INIT:message`

**Color Coding:**
- Green: Success messages (OK, DONE)
- Red: Errors and hazards
- Yellow: Warnings
- Cyan: Information and data
- White: General responses

**Features:**
- Auto-scroll to newest message
- Timestamp for each message
- Filter by message type
- Export log to file
- Clear display button

**Implementation:**
```python
def process_message(self, message):
    """Display formatted message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Determine message type and color
    if message.startswith("ERROR"):
        color = "red"
        prefix = "❌"
    elif message in ["OK", "DONE"]:
        color = "green"
        prefix = "✓"
    elif message.startswith("HAZARD"):
        color = "orange"
        prefix = "⚠"
    else:
        color = "white"
        prefix = "→"
    
    formatted = f"[{timestamp}] {prefix} {message}"
    self.append_colored_text(formatted, color)
```

---

## Communication System

### Connection Manager (`connection_manager.py`)

**Purpose:** Handle all network communication between the GUI and CyBot.

**Architecture:** Uses threaded socket communication for non-blocking I/O

#### Components

**1. ConnectionManager (Main Class)**
- Creates and manages TCP socket
- Provides `connect()` and `disconnect()` methods
- Provides `send_command()` method for transmitting
- Emits Qt signals for connection events

**2. ReceiverWorker (Background Thread)**
- Runs in separate QThread
- Continuously reads from socket
- Emits signals when data arrives
- Handles socket errors gracefully

#### Connection Flow

```python
class ConnectionManager(QObject):
    # Signals
    connected_signal = Signal(bool)
    message_received = Signal(str)
    error_occurred = Signal(str)
    
    def connect(self, ip, port):
        """Establish connection to CyBot"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((ip, int(port)))
            self.is_connected = True
            self._start_receiver()
            self.connected_signal.emit(True)
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {e}")
            self.connected_signal.emit(False)
```

#### Receiver Thread

```python
class ReceiverWorker(QObject):
    message = Signal(str)
    error = Signal(str)
    finished = Signal()
    
    def run(self):
        """Background receive loop"""
        while self._running:
            try:
                data = self.sock.recv(4096)
                if data:
                    text = data.decode('utf-8', errors='ignore')
                    for line in text.splitlines():
                        if line.strip():
                            self.message.emit(line.strip())
            except socket.timeout:
                continue
            except Exception as e:
                self.error.emit(str(e))
                break
```

#### Sending Commands

```python
def send_command(self, command):
    """Send command to CyBot"""
    if not self.is_connected:
        self.error_occurred.emit("Not connected")
        return
        
    try:
        # Ensure command ends with newline
        if not command.endswith('\n'):
            command += '\n'
        
        self.socket.sendall(command.encode('utf-8'))
        
    except Exception as e:
        self.error_occurred.emit(f"Send failed: {e}")
        self.disconnect()
```

#### Threading Model

```
Main GUI Thread (Qt Event Loop)
    ├─ User clicks button
    ├─ Emit signal with command
    └─ ConnectionManager.send_command()
        └─ socket.sendall() [blocking, but fast]

Receiver Thread (Background)
    ├─ Continuous socket.recv() loop
    ├─ Emit signal when data arrives
    └─ Main thread receives signal
        └─ Update GUI displays
```

**Thread Safety:**
- Qt Signals are thread-safe
- Socket operations isolated to appropriate threads
- No shared mutable state between threads

---

## User Interaction Flow

### Complete Usage Scenario

#### Scenario 1: Moving the Robot Forward

**Step-by-Step:**

1. **User launches GUI:**
   ```bash
   python run_gui.py
   ```

2. **User connects to CyBot:**
   - Enter IP: `192.168.1.1`
   - Enter Port: `288`
   - Click `CONNECT` button
   - Status shows: "CONNECTED"

3. **User sets movement parameters:**
   - Set distance spinbox to `50` cm
   - Click on Controls Panel tab

4. **User clicks FORWARD button (W):**
   - Button shows visual feedback (highlighted)
   - Controls Panel emits signal: `movement_requested("w50")`

5. **GUI sends command:**
   - Connection Manager receives signal
   - Sends: `"w50\n"` via TCP socket

6. **GUI receives responses:**
   - Receiver thread gets: `"OK\n"`
   - Response Panel shows: "✓ OK"
   - Receiver thread gets: `"DONE\n"`
   - Response Panel shows: "✓ DONE"
   - Button returns to normal state

7. **User sees confirmation:**
   - Green checkmark in response panel
   - Log window records: `[14:23:15] → w50` and `[14:23:16] ✓ OK`

#### Scenario 2: Object Detection Scan

**Step-by-Step:**

1. **User switches to Dual View mode:**
   - Click `DUAL VIEW` button in header
   - Layout changes to split screen
   - Controls on left, visualizations on right

2. **User initiates scan:**
   - Click `OBJECT DETECTION` button in Scan Controls
   - Status label shows: "Scanning..."
   - Controls Panel emits: `scan_requested("o")`

3. **GUI receives scan data (real-time):**
   
   **Messages arriving:**
   ```
   OK
   SCAN_START
   P:0,52.3
   I:0,54.1
   T:0,0
   P:2,52.1
   I:2,53.9
   T:2,0
   ... (continues for each angle)
   P:180,67.8
   SCAN_DONE
   ```

4. **Visualizations update in real-time:**
   - **Radar Panel:**
     - Plots each `P:angle,distance` point as it arrives
     - Sweep line rotates from 0° to 180°
     - Green dots appear showing detected distances
   
   - **Scan Panel:**
     - Table fills with rows of data
     - Each row shows angle, PING, IR, tape values
   
   - **Response Panel:**
     - Shows status messages
     - Displays "SCAN_START" → "SCAN_DONE"

5. **Object detection results:**
   
   **Messages arriving:**
   ```
   OBJECT:45,12,50.3,10.5
   OBJECT:120,8,65.2,9.1
   DONE
   ```

6. **Map Panel updates:**
   - Converts polar to Cartesian coordinates
   - Renders two rectangles representing objects:
     - Object 1: 45° angle, 50.3 cm away, 10.5 cm wide
     - Object 2: 120° angle, 65.2 cm away, 9.1 cm wide
   - Shows robot at center

7. **User analyzes results:**
   - Radar shows distance profile
   - Map shows object positions and sizes
   - Scan table provides detailed numerical data
   - Can export data for further analysis

#### Scenario 3: Playing Custom Sound

**Step-by-Step:**

1. **User switches to Sound Panel tab**

2. **User loads MIDI file:**
   - Click `Select MIDI File` button
   - File dialog opens
   - Navigate to `sounds/custom/mario_coin.mid`
   - Click `Open`

3. **MIDI parsing:**
   - MIDI Parser extracts notes and durations
   - Sound Panel displays:
     - File: `mario_coin.mid`
     - Notes: 8
     - Duration: ~2 seconds
     - Preview: Note sequence shown

4. **User selects upload slot:**
   - Choose Slot 0 from dropdown
   - Click `Upload to Slot 0` button

5. **GUI uploads song:**
   - Formats command: `SOUND_LOAD:0,64,66,68,69,71,73,75,76;16,16,16,32,16,16,16,32`
   - Connection Manager sends command
   - Response Panel shows: "✓ Sound loaded to slot 0"

6. **User plays sound:**
   - Click `Play` button
   - GUI sends: `SOUND_PLAY:0`
   - Robot speaker plays the Mario coin sound
   - Response Panel shows: "✓ Playing sound 0"

---

## Running the GUI

### Installation and Setup

**Prerequisites:**
- Python 3.8 or higher
- PySide6 library

**Install Dependencies:**
```bash
pip install PySide6
```

**Launch the GUI:**
```bash
cd protocue-2880-project/gui
python run_gui.py
```

### First-Time Setup

1. **Launch Application:**
   - Double-click `run_gui.py` or run from terminal
   - Main window appears with default settings

2. **Configure Connection:**
   - Default IP: `192.168.1.1`
   - Default Port: `288`
   - Modify if your CyBot uses different settings

3. **Connect to CyBot:**
   - Ensure CyBot is powered on and WiFi bridge is active
   - Click `CONNECT` button
   - Wait for "CONNECTED" status (green indicator)
   - Log window automatically opens showing connection status

4. **Test Basic Commands:**
   - Try emergency stop (`T` button) to verify communication
   - Move forward 10 cm to test movement
   - Perform a basic scan to test sensors

### Troubleshooting

**Connection Issues:**
- Verify IP address and port are correct
- Check that CyBot is on the same network
- Ensure WiFi bridge is properly configured
- Check firewall settings on PC

**GUI Not Responding:**
- Check log window for error messages
- Restart the application
- Verify Python and PySide6 are installed correctly

**Scan Data Not Displaying:**
- Ensure correct view mode (Dual View recommended for scans)
- Check that radar/map panels are visible
- Verify CyBot is sending data (check response panel)

---

## File Structure

```
gui/
├── run_gui.py                # Application launcher
├── main_window.py            # Main window container (876 lines)
├── controls_panel.py         # Movement and scan controls (904 lines)
├── radar_panel.py            # Polar plot visualization
├── map_panel.py              # 2D object map
├── scan_panel.py             # Tabular scan data
├── sound_panel.py            # MIDI player and sound controls
├── response_panel.py         # Response message viewer
├── log_window.py             # Separate logging window
├── connection_manager.py     # Socket communication handler (187 lines)
├── midi_parser.py            # MIDI file processor
├── utils.py                  # Styling and utility functions
├── gui_client.py             # Legacy client interface
├── __pycache__/              # Python bytecode cache
└── deprecated/               # Old/unused components
    ├── control_panel.py
    └── plot_panel.py
```

---

## Design Philosophy

### Military Command Center Theme

The GUI adopts a military command center aesthetic:

**Color Scheme:**
- **Background:** Dark grays and blacks (`#1a1a1a`, `#2a2a2a`)
- **Primary Text:** Military green (`#4a5c23`, `#7cfc00`)
- **Accents:** Olive drab borders and highlights
- **Alerts:** Red for errors, yellow for warnings, green for success

**Typography:**
- Monospace fonts (Courier New) for data displays
- Bold fonts for headers and important information
- Clear hierarchy for readability

**Visual Style:**
- Tactical/military terminology (e.g., "CYBOT COMMAND TERMINAL")
- Grid-based layouts resembling radar displays
- Dark theme reduces eye strain during extended use
- High contrast for visibility

### Modularity and Extensibility

**Independent Panels:**
Each panel is a self-contained `QWidget` that can be:
- Developed independently
- Tested in isolation
- Reused in different layouts
- Extended with new features

**Signal-Slot Architecture:**
Loose coupling between components through Qt signals:
```python
# Panels don't call each other directly
# They emit signals that main window routes
self.movement_requested.emit("w100")  # Panel emits
# Main window connects signals to appropriate handlers
```

**Benefits:**
- Easy to add new panels
- Changes to one panel don't break others
- Clear data flow and event handling
- Testable components

### User Experience Considerations

**Real-Time Feedback:**
- Immediate visual response to button clicks
- Live status updates during operations
- Progress indicators for long-running scans
- Color-coded message types

**Keyboard Shortcuts:**
- WASD for movement (familiar to users)
- Quick access to common commands
- No need to click buttons for basic operations

**Flexible Layouts:**
- Single view for focused work
- Dual view for monitoring multiple data sources
- Resizable panels and windows
- Persistent window positions

**Error Handling:**
- Clear error messages in response panel
- Connection status always visible
- Graceful degradation when features unavailable
- Helpful troubleshooting messages

---

## Advanced Features

### Log Window

**Purpose:** Comprehensive logging and debugging tool

**Features:**
- **Separate Window:** Can be moved to second monitor
- **Color Coding:** Different colors for different message types
- **Timestamps:** Every message includes time of arrival
- **Filtering:** Show/hide specific message categories
- **Export:** Save log to text file for analysis
- **Auto-scroll:** Automatically scrolls to newest messages
- **Clear Function:** Reset log without closing window

**Usage Scenarios:**
- Debug communication issues
- Monitor command execution
- Record scan sessions
- Troubleshoot errors

### View Mode System

**Single View Mode:**
```
┌─────────────────────────┐
│   [Tab1] [Tab2] [Tab3]  │
│  ┌───────────────────┐  │
│  │                   │  │
│  │   Active Panel    │  │
│  │                   │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

**Dual View Mode:**
```
┌─────────────────────────────┐
│  Controls  │  Visualization │
│    Panel   │     Panel      │
│            │                │
│  [Buttons] │  [Radar/Map]   │
│  [Config]  │  [Data View]   │
└─────────────────────────────┘
```

**Dynamic Switching:**
- Preserves panel state when switching
- Remembers splitter positions
- Smooth transitions
- No data loss

### MIDI Integration

**Supported MIDI Features:**
- Note-on events (melody extraction)
- Tempo detection
- Duration calculation
- Multiple track support (melody track selected)

**Limitations:**
- 16-note maximum (iRobot hardware limitation)
- No polyphony (single notes only)
- No pitch bending or modulation
- Fixed tempo scaling

**Conversion Process:**
1. Load MIDI file
2. Parse track 0 or specified melody track
3. Extract note numbers (0-127)
4. Calculate durations in 1/64 second units
5. Truncate to 16 notes if needed
6. Format for iRobot protocol
7. Upload to robot

### Custom Styling System

**Utils Module (`utils.py`):**

Provides centralized styling:

```python
# Color palette
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#2a2a2a',
    'bg_light': '#3a3a3a',
    'text_green': '#7cfc00',
    'accent': '#4a5c23',
    'error': '#ff4444',
    'warning': '#ffaa00',
    'success': '#44ff44'
}

# Base stylesheet
def get_base_stylesheet():
    return f"""
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
        color: {COLORS['text_green']};
    }}
    QPushButton {{
        background-color: {COLORS['bg_medium']};
        border: 2px solid {COLORS['accent']};
        ...
    }}
    """
```

**Benefits:**
- Consistent look across all panels
- Easy theme modifications
- Centralized color management
- Reusable style components

---

## Future Enhancements

### Planned Features

1. **Map Persistence:**
   - Save/load map data
   - Build cumulative maps over multiple scans
   - Export map as image or 3D model

2. **Autonomous Mission Planning:**
   - Click-to-navigate on map
   - Waypoint system
   - Obstacle avoidance path planning

3. **Video Feed Integration:**
   - Camera panel for live video
   - Object recognition overlay
   - Recording and playback

4. **Multi-Robot Support:**
   - Connect to multiple CyBots
   - Coordinate movements
   - Swarm behavior controls

5. **Advanced Visualization:**
   - 3D view of environment
   - Heat maps
   - Path history overlay

6. **Data Analysis Tools:**
   - Statistical analysis of scans
   - Object tracking over time
   - Performance metrics

### Extensibility Points

**Adding a New Panel:**

1. Create new panel class:
```python
from PySide6.QtWidgets import QWidget

class MyNewPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def process_message(self, message):
        # Handle incoming data
        pass
```

2. Add to main window:
```python
self.my_panel = MyNewPanel()
self.tab_widget.addTab(self.my_panel, "My Panel")
```

3. Connect signals:
```python
self.connection_manager.message_received.connect(
    self.my_panel.process_message
)
```

**Adding a New Command:**

1. Add button in controls panel:
```python
self.new_cmd_btn = QPushButton("NEW COMMAND")
self.new_cmd_btn.clicked.connect(self.on_new_command)
```

2. Implement handler:
```python
def on_new_command(self):
    command = "new_cmd_string"
    self.scan_requested.emit(command)
```

3. Update CyBot firmware to handle new command

---

## Summary

The CyBot Military Command Center GUI is a professional-grade desktop application that provides:

✅ **Intuitive Control:** Easy-to-use interface for robot operations  
✅ **Real-Time Visualization:** Live radar and map displays  
✅ **Flexible Layout:** Single and dual view modes  
✅ **Robust Communication:** Threaded socket handling  
✅ **Advanced Features:** MIDI playback, logging, data export  
✅ **Extensible Design:** Modular architecture for future enhancements  
✅ **Military Aesthetic:** Professional command center styling  

**Key Technologies:**
- PySide6 (Qt 6) for GUI framework
- Socket programming for network communication
- Threading for responsive UI
- Custom MIDI parser for sound features
- Signal-slot pattern for component communication

**Perfect for:**
- Remote robot control
- Environmental scanning and mapping
- Data collection and analysis
- Educational demonstrations
- Research and development

---

**Document Version:** 1.0  
**Last Updated:** December 9, 2025  

