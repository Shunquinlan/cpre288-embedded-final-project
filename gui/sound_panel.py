"""Sound and MIDI control panel"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QListWidget, QFileDialog, QHBoxLayout)
from pathlib import Path
from PySide6.QtCore import Signal
from utils import COLORS

# Support importing midi_parser whether this package is loaded as a package or run directly
try:
    from .midi_parser import parse_midi_file, parse_midi_text_file
except Exception:
    try:
        from midi_parser import parse_midi_file, parse_midi_text_file
    except Exception:
        # Fallback stubs: parsing will return empty list if import fails
        def parse_midi_file(path):
            return []
        def parse_midi_text_file(path):
            return []


class SoundPanel(QWidget):
    song_play_requested = Signal(int)  # slot number
    song_clear_requested = Signal(int)
    upload_requested = Signal(str)  # filepath

    def __init__(self):
        super().__init__()
        self._connection_manager = None
        self._logger = None
        self._status_setter = None
        self.init_ui()

    def set_connection_manager(self, cm):
        """Attach ConnectionManager for sending commands and listen for incoming messages."""
        self._connection_manager = cm
        # If ConnectionManager provides signals, connect to them for status updates
        try:
            cm.message_received.connect(self._on_connection_message)
            cm.connected_signal.connect(lambda connected: self._on_connection_changed(connected))
        except Exception:
            # If cm doesn't have the signals yet, ignore
            pass

    def set_loggers(self, logger_callable, status_setter_callable=None):
        """Provide logging and status setter callables.
        logger_callable(message, connected=False)
        status_setter_callable(text)
        """
        self._logger = logger_callable
        self._status_setter = status_setter_callable

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.title = QLabel('SOUND CONTROL')
        layout.addWidget(self.title)

        # Add basic sound testing buttons
        basic_sounds_layout = QHBoxLayout()
        basic_sounds_layout.setSpacing(10)
        
        self.play_ok_btn = QPushButton('🔊 Play OK Beep')
        self.play_ok_btn.setFixedHeight(35)
        self.play_ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_medium']};
                color: {COLORS['text_green']};
                border: 2px solid {COLORS['text_green']};
                border-radius: 6px;
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #1f3d1f;
                border-color: #00ff00;
            }}
        """)
        self.play_ok_btn.clicked.connect(self._play_ok_sound)
        basic_sounds_layout.addWidget(self.play_ok_btn)
        
        self.play_error_btn = QPushButton('🔊 Play Error Beep')
        self.play_error_btn.setFixedHeight(35)
        self.play_error_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_medium']};
                color: {COLORS['text_red']};
                border: 2px solid {COLORS['text_red']};
                border-radius: 6px;
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #3d1f1f;
                border-color: #ff0000;
            }}
        """)
        self.play_error_btn.clicked.connect(self._play_error_sound)
        basic_sounds_layout.addWidget(self.play_error_btn)
        
        self.play_soldier_found_btn = QPushButton('🔊 Soldier Found')
        self.play_soldier_found_btn.setFixedHeight(35)
        self.play_soldier_found_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_medium']};
                color: {COLORS['text_yellow']};
                border: 2px solid {COLORS['text_yellow']};
                border-radius: 6px;
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #3d3d1f;
                border-color: #ffff00;
            }}
        """)
        self.play_soldier_found_btn.clicked.connect(self._play_soldier_found_sound)
        basic_sounds_layout.addWidget(self.play_soldier_found_btn)
        
        layout.addLayout(basic_sounds_layout)

        self.midi_file_list = QListWidget()
        layout.addWidget(self.midi_file_list)

        btn_layout = QVBoxLayout()
        self.upload_btn = QPushButton('Load MIDI File')
        self.upload_btn.clicked.connect(self.load_midi_file)
        btn_layout.addWidget(self.upload_btn)

        # Add test/play buttons for slots 0-3 and an Upload Selected button
        test_layout = QHBoxLayout()
        test_layout.setSpacing(6)
        for n in range(4):
            b = QPushButton(f'Play Slot {n}')
            b.setFixedHeight(28)
            # capture loop variable
            b.clicked.connect(lambda _checked=False, s=n: self._request_play_slot(s))
            test_layout.addWidget(b)
        btn_layout.addLayout(test_layout)

        self.upload_selected_btn = QPushButton('Upload Selected')
        self.upload_selected_btn.clicked.connect(self.upload_selected_midi)
        btn_layout.addWidget(self.upload_selected_btn)

        layout.addLayout(btn_layout)
        self.refresh_midi_list()

        # Add status labels used by connection callbacks and main_window
        self.song_status_label = QLabel("SONG STATUS: No songs loaded")
        self.song_status_label.setStyleSheet(f"QLabel {{ color: {COLORS['text_yellow']}; font-weight: bold; padding: 6px; background-color: {COLORS['bg_medium']}; border: 1px solid {COLORS['border']}; border-radius: 4px; }}")
        layout.addWidget(self.song_status_label)

        self.sound_control_status_label = QLabel("SOUND CONTROL: Ready")
        self.sound_control_status_label.setStyleSheet(f"QLabel {{ color: {COLORS['text_green']}; font-weight: bold; padding: 8px; background-color: #1f3d1f; border: 2px solid {COLORS['border']}; border-radius: 4px; }}")
        layout.addWidget(self.sound_control_status_label)

    def refresh_midi_list(self):
        self.midi_file_list.clear()
        project_dir = Path(__file__).parent.parent
        sounds_dir = project_dir / 'sounds'
        for subdir in ['default', 'custom']:
            p = sounds_dir / subdir
            if p.exists():
                for f in p.iterdir():
                    if f.is_file() and f.suffix.lower() in ['.mid', '.midi', '.txt']:
                        rel = f.relative_to(project_dir)
                        self.midi_file_list.addItem(str(rel))

    def load_midi_file(self):
        fd = QFileDialog()
        file_path, _ = fd.getOpenFileName(self, 'Select MIDI File', '', 'MIDI Files (*.mid *.midi *.txt);;All Files (*)')
        if file_path:
            # Copy to custom sounds folder
            project_dir = Path(__file__).parent.parent
            custom_dir = project_dir / 'sounds' / 'custom'
            custom_dir.mkdir(parents=True, exist_ok=True)
            try:
                dst = custom_dir / Path(file_path).name
                import shutil
                shutil.copy(file_path, dst)
                if self._logger:
                    self._logger(f"📁 Imported file to: {dst}", connected=(self._connection_manager.is_connected if self._connection_manager else False))
                self.refresh_midi_list()
            except Exception as e:
                if self._logger:
                    self._logger(f"✗ Error importing file: {e}", connected=(self._connection_manager.is_connected if self._connection_manager else False))

    def upload_selected_midi(self):
        """Upload selected MIDI file to CyBot (default to slot 2)."""
        current_item = self.midi_file_list.currentItem()
        if not current_item:
            if self._logger:
                self._logger("❌ No MIDI file selected", connected=(self._connection_manager.is_connected if self._connection_manager else False))
            if self._status_setter:
                self._status_setter("SOUND CONTROL: ❌ No file selected")
            return

        file_path = current_item.text()
        project_dir = Path(__file__).parent.parent
        # Resolve selected item robustly. Items are stored relative to project_dir
        p = Path(file_path)
        if p.is_absolute():
            full_path = p
        else:
            # file_path is likely like 'sounds/custom/foo.mid' (relative to project_dir)
            full_path = project_dir / file_path

        # Fallback: if that doesn't exist, try assuming file_path is just the filename under sounds/custom
        if not full_path.exists():
            alt = project_dir / 'sounds' / Path(file_path).name
            if alt.exists():
                full_path = alt

        if self._logger:
            self._logger(f"🎵 PROCESSING: {file_path}", connected=(self._connection_manager.is_connected if self._connection_manager else False))
            self._logger(f"🔍 FULL PATH: {full_path}", connected=(self._connection_manager.is_connected if self._connection_manager else False))

        if not full_path.exists():
            if self._logger:
                self._logger(f"❌ FILE NOT FOUND: {full_path}", connected=(self._connection_manager.is_connected if self._connection_manager else False))
            if self._status_setter:
                self._status_setter(f"SOUND CONTROL: ❌ File not found: {file_path}")
            return

        # Parse file
        try:
            parsed = []
            suffix = full_path.suffix.lower()
            if suffix in ('.mid', '.midi'):
                parsed = parse_midi_file(full_path)
            elif suffix == '.txt':
                parsed = parse_midi_text_file(full_path)

            if not parsed:
                # Nothing parsed — inform user
                if self._logger:
                    self._logger("❌ No valid notes found in MIDI file", connected=(self._connection_manager.is_connected if self._connection_manager else False))
                if self._status_setter:
                    self._set_status_text(f"SOUND CONTROL: ❌ No valid notes found", color="#ff8080")
                return

            # Unpack notes/durations and enforce limits
            notes, durations = zip(*parsed)
            notes = list(notes)
            durations = list(durations)

            # Truncate to 16 notes (safety)
            if len(notes) > 16:
                notes = notes[:16]
                durations = durations[:16]

            # Validate ranges
            for n in notes:
                if not (31 <= n <= 127):
                    if self._logger:
                        self._logger(f"❌ Upload failed: note {n} out of range", connected=self._connection_manager.is_connected)
                    if self._status_setter:
                        self._set_status_text("SOUND CONTROL: ❌ File contained out-of-range MIDI notes", color="#ff8080")
                    return
            for d in durations:
                if not (1 <= d <= 255):
                    if self._logger:
                        self._logger(f"❌ Upload failed: duration {d} invalid", connected=self._connection_manager.is_connected)
                    if self._status_setter:
                        self._set_status_text("SOUND CONTROL: ❌ File contained invalid durations", color="#ff8080")
                    return

            # Upload to slot 2 by default
            song_slot = 2
            success = self.upload_song_to_cybot(song_slot, notes, durations)
            if success:
                if self._status_setter:
                    total_time = sum(durations) / 64.0
                    self._status_set_text = f"SOUND CONTROL: ✅ Uploaded '{file_path}' to Slot {song_slot} ({len(notes)} notes, {total_time:.1f}s)"
                    self._set_status_text(self._status_set_text)
            else:
                if self._status_setter:
                    self._set_status_text(f"SOUND CONTROL: ❌ Upload failed: {file_path}")

        except Exception as e:
            if self._logger:
                self._logger(f"❌ Error uploading MIDI: {e}", connected=(self._connection_manager.is_connected if self._connection_manager else False))

    def upload_song_to_cybot(self, slot, notes, durations):
        """Upload song data to CyBot using the load_song command."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("❌ UPLOAD FAILED: Not connected to CyBot", connected=False)
            return False

        # Validate slot
        if not (0 <= slot <= 3):
            if self._logger:
                self._logger(f"❌ UPLOAD FAILED: Invalid slot {slot}", connected=self._connection_manager.is_connected)
            return False

        # Truncate to 16 notes
        if len(notes) > 16:
            notes = notes[:16]
            durations = durations[:16]

        if not notes:
            if self._logger:
                self._logger("❌ UPLOAD FAILED: No notes to upload", connected=self._connection_manager.is_connected)
            return False

        for note in notes:
            if not (31 <= note <= 127):
                if self._logger:
                    self._logger(f"❌ UPLOAD FAILED: Note {note} outside Roomba range (31-127)", connected=self._connection_manager.is_connected)
                return False

        notes_str = ",".join(map(str, notes))
        durs_str = ",".join(map(str, durations))
        command = f"load_song_{slot}_NOTES:{notes_str};DURS:{durs_str}"

        if self._logger:
            self._logger(f"🎵 UPLOADING TO SLOT {slot}: {len(notes)} notes", connected=self._connection_manager.is_connected)
            self._logger(f"📋 COMMAND: {command}", connected=self._connection_manager.is_connected)

        # Send command and wait for a response
        success, response = self._connection_manager.send_command(command, timeout=5, wait_for_response=True)
        if not success:
            if self._logger:
                self._logger(f"❌ UPLOAD FAILED: {response}", connected=self._connection_manager.is_connected)
            return False

        if self._logger:
            self._logger(f"✅ UPLOAD COMPLETE: {len(notes)} notes uploaded to CyBot slot {slot}", connected=self._connection_manager.is_connected)
        return True

    def _request_play_slot(self, slot: int):
        """Request playback of a given slot (emits signal and logs)."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger(f"❌ Play Slot {slot} failed: Not connected", connected=False)
            if self._status_setter:
                self._status_setter(f"SOUND CONTROL: ❌ Not connected")
            return

        if self._logger:
            self._logger(f"▶ Play Slot {slot} requested", connected=self._connection_manager.is_connected)
        # Emit signal that main window listens to and forwards to connection manager
        self.song_play_requested.emit(slot)

    def _on_connection_changed(self, connected):
        """Update UI when connection state changes."""
        if connected:
            if self._status_setter:
                self._status_setter("SOUND CONTROL: Connected")
        else:
            if self._status_setter:
                self._status_setter("SOUND CONTROL: Disconnected")

    def _on_connection_message(self, message: str):
        """Handle incoming messages from the CyBot related to sound and songs.
        Updates the song status and sound control labels when relevant messages arrive.
        """
        if not message:
            return

        msg = message.strip()

        # SONG_STATUS handling
        if "SONG_STATUS=" in msg:
            try:
                status = msg.split("SONG_STATUS=", 1)[1]
            except Exception:
                status = msg
            self.song_status_label.setText(f"SONG STATUS: {status}")
            return

        # Generic sound/song messages
        lower = msg.lower()

        # Detect playing messages
        if any(k in lower for k in ("playing", "play", "song_play", "now playing")):
            # Try to detect a slot number in the message
            slot = None
            for token in msg.split():
                if token.isdigit():
                    try:
                        n = int(token)
                        if 0 <= n <= 3:
                            slot = n
                            break
                    except Exception:
                        pass
            if slot is not None:
                self._set_status_text(f"SOUND CONTROL: ♪ Playing Slot {slot}", color="#00ff00")
            else:
                self._set_status_text("SOUND CONTROL: ♪ Playing", color="#00ff00")
            return

        # Cleared/clear messages
        if any(k in lower for k in ("cleared", "clear", "deleted", "removed")):
            # Map to cleared slot message if contains slot number
            slot = None
            for token in msg.split():
                if token.isdigit():
                    try:
                        n = int(token)
                        if 0 <= n <= 3:
                            slot = n
                            break
                    except Exception:
                        pass
            if slot is not None:
                self._set_status_text(f"SOUND CONTROL: 🗑️ Cleared Slot {slot}", color="#ffaa00")
            else:
                self._set_status_text(f"SOUND CONTROL: 🗑️ Cleared", color="#ffaa00")
            return

        # Upload confirmation
        if any(k in lower for k in ("upload", "uploaded", "upload complete", "upload finished")):
            self._set_status_text(f"SOUND CONTROL: ✅ Upload confirmed", color="#00ff00")
            return

    def _set_status_text(self, text: str, color: str = None):
        """Helper to set the sound_control_status_label text and apply a minimal style tweak.
        If color provided, update the label color while preserving other styles.
        """
        self.sound_control_status_label.setText(text)
        if color:
            base = self.sound_control_status_label.styleSheet()
            # Append a small override for color to avoid replacing full style
            override = f"\nQLabel {{ color: {color}; }}"
            try:
                self.sound_control_status_label.setStyleSheet(base + override)
            except Exception:
                # Fallback to simple setStyleSheet
                self.sound_control_status_label.setStyleSheet(f"QLabel {{ color: {color}; }}")

    def _play_ok_sound(self):
        """Play the 'OK' beep sound (slot 0)."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("❌ Cannot play OK sound: Not connected", connected=False)
            if self._status_setter:
                self._set_status_text("SOUND CONTROL: ❌ Not connected", color="#ff8080")
            return
        
        # Send command 'K' (uppercase) to play OK beep - lowercase 'k' is tape detect
        success, response = self._connection_manager.send_command("K", timeout=1, wait_for_response=False)
        if success:
            if self._logger:
                self._logger("🔊 Playing OK beep", connected=True)
            self._set_status_text("SOUND CONTROL: 🔊 Playing OK beep", color="#00ff00")
        else:
            if self._logger:
                self._logger(f"❌ Failed to play OK sound: {response}", connected=True)
            self._set_status_text("SOUND CONTROL: ❌ Failed to play OK sound", color="#ff8080")

    def _play_error_sound(self):
        """Play the 'Error' beep sound (slot 1)."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("❌ Cannot play Error sound: Not connected", connected=False)
            if self._status_setter:
                self._set_status_text("SOUND CONTROL: ❌ Not connected", color="#ff8080")
            return
        
        # Send command 'N' (uppercase) to play Error beep
        success, response = self._connection_manager.send_command("N", timeout=1, wait_for_response=False)
        if success:
            if self._logger:
                self._logger("🔊 Playing Error beep", connected=True)
            self._set_status_text("SOUND CONTROL: 🔊 Playing Error beep", color="#ff8080")
        else:
            if self._logger:
                self._logger(f"❌ Failed to play Error sound: {response}", connected=True)
            self._set_status_text("SOUND CONTROL: ❌ Failed to play Error sound", color="#ff8080")

    def _play_soldier_found_sound(self):
        """Play the 'Soldier Found' alarm sound (slot 4)."""
        if not self._connection_manager or not self._connection_manager.is_connected:
            if self._logger:
                self._logger("❌ Cannot play Soldier Found sound: Not connected", connected=False)
            if self._status_setter:
                self._set_status_text("SOUND CONTROL: ❌ Not connected", color="#ff8080")
            return
        
        # Send command 'F' (uppercase) to play Soldier Found alarm
        success, response = self._connection_manager.send_command("F", timeout=1, wait_for_response=False)
        if success:
            if self._logger:
                self._logger("🔊 Playing Soldier Found alarm", connected=True)
            self._set_status_text("SOUND CONTROL: 🔊 Playing Soldier Found alarm", color="#ffff00")
        else:
            if self._logger:
                self._logger(f"❌ Failed to play Soldier Found sound: {response}", connected=True)
            self._set_status_text("SOUND CONTROL: ❌ Failed to play Soldier Found sound", color="#ff8080")
