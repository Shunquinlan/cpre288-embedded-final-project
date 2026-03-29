"""CyBot connection management"""
import socket
import time
from PySide6.QtCore import QObject, Signal, QThread, QEventLoop, QTimer


class ReceiverWorker(QObject):
    """Background worker that reads from the socket and emits messages."""
    message = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        try:
            while self._running:
                try:
                    self.sock.settimeout(0.5)
                    data = self.sock.recv(4096)
                    if not data:
                        # Remote end closed
                        self.error.emit('Remote closed connection')
                        break
                    text = data.decode(errors='ignore').strip()
                    for line in text.splitlines():
                        line = line.strip()
                        if line:
                            self.message.emit(line)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.error.emit(str(e))
                    break
        finally:
            self.finished.emit()


class ConnectionManager(QObject):
    """Manages socket connection to CyBot"""

    # Signals
    connected_signal = Signal(bool)
    message_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.socket = None
        self.is_connected = False
        self._recv_thread = None
        self._recv_worker = None

    def _start_receiver(self):
        if not self.socket:
            return
        # Avoid starting multiple receivers
        if self._recv_thread and self._recv_thread.isRunning():
            return
        self._recv_thread = QThread()
        self._recv_worker = ReceiverWorker(self.socket)
        self._recv_worker.moveToThread(self._recv_thread)
        self._recv_thread.started.connect(self._recv_worker.run)
        self._recv_worker.message.connect(self.message_received.emit)
        self._recv_worker.error.connect(self.error_occurred.emit)
        self._recv_worker.finished.connect(self._recv_thread.quit)
        self._recv_worker.finished.connect(self._recv_worker.deleteLater)
        self._recv_thread.finished.connect(self._recv_thread.deleteLater)
        self._recv_thread.start()

    def _stop_receiver(self):
        try:
            if self._recv_worker:
                self._recv_worker.stop()
            if self._recv_thread:
                self._recv_thread.quit()
                self._recv_thread.wait(1000)
        except Exception:
            pass
        finally:
            self._recv_worker = None
            self._recv_thread = None

    def connect(self, ip, port):
        """Connect to CyBot"""
        try:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)

            start_time = time.time()
            self.socket.connect((ip, int(port)))
            connect_time = int((time.time() - start_time) * 1000)

            self.is_connected = True
            self.connected_signal.emit(True)

            # Start background receiver to emit incoming messages
            self._start_receiver()

            return True, f"Connected in {connect_time}ms"

        except Exception as e:
            self.is_connected = False
            self.connected_signal.emit(False)
            return False, str(e)

    def disconnect(self):
        """Disconnect from CyBot"""
        # Stop receiver first
        self._stop_receiver()
        # Inside disconnect() method, after self.connected = False
        if hasattr(self, 'sound_panel'):
            self.sound_panel._on_connection_changed(False)
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.is_connected = False
        self.connected_signal.emit(False)
    

    def send_command(self, command, timeout=3, wait_for_response=True):
        """Send command and optionally wait for a single response."""
        if not self.is_connected or not self.socket:
            return False, "Not connected"

        try:
            self.socket.send((command + '\n').encode())

            if wait_for_response:
                # Use the running receiver thread to capture incoming messages
                # without performing a second blocking recv() on the socket.
                loop = QEventLoop()
                response_holder = {'resp': None}

                def _on_message(msg):
                    # store the first incoming message and quit event loop
                    response_holder['resp'] = msg
                    loop.quit()

                # Connect temporary listener
                self.message_received.connect(_on_message)

                # Timeout guard
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(loop.quit)
                timer.start(int(timeout * 1000))

                # Run local event loop until a message arrives or timeout
                loop.exec()

                # Cleanup connection and timer
                try:
                    self.message_received.disconnect(_on_message)
                except Exception:
                    pass
                if timer.isActive():
                    timer.stop()

                if response_holder['resp'] is None:
                    return False, "Timeout"
                return True, response_holder['resp']
            else:
                return True, ""

        except Exception as e:
            self.is_connected = False
            self.connected_signal.emit(False)
            self.error_occurred.emit(str(e))
            return False, str(e)
