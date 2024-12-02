import socket
import pyaudio
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder

kv = """
MainWidget:

<MainWidget>:
    orientation: "vertical"
    padding: 20
    spacing: 20

    canvas.before:
        Color:
            rgba: 1, 1, 1, 1  # White background
        Rectangle:
            pos: self.pos
            size: self.size

    # Status Label with Circular Background
    BoxLayout:
        size_hint: None, None
        size: 100, 100
        pos_hint: {"center_x": 0.5}
        canvas.before:
            Color:
                rgba: 0.9, 0.9, 0.9, 1  # Light gray for circle
            Ellipse:
                pos: self.pos
                size: self.size
        Label:
            id: connection_label
            text: "Disconnected"
            color: 1, 0, 0, 1  # Red text for disconnected
            halign: "center"
            valign: "middle"
            text_size: self.size

    # IP Address Input
    BoxLayout:
        orientation: "vertical"
        spacing: 10
        size_hint: None, None
        size: 250, 100
        pos_hint: {"center_x": 0.5}

        Label:
            text: "IP Address"
            color: 0, 0, 0, 1
            font_size: 16
            halign: "center"

        Label:
            id: IP_address
            text: "IP address pending"
            color: 0, 0, 0, 1
            font_size: 16
            halign: "center"

    # Port Display
    BoxLayout:
        orientation: "vertical"
        spacing: 10
        size_hint: None, None
        size: 250, 100
        pos_hint: {"center_x": 0.5}

        Label:
            text: "Port"
            color: 0, 0, 0, 1
            font_size: 16
            halign: "center"

        Label:
            text: root.port_val
            color: 0, 0, 0, 1
            size_hint_y: None
            height: 40

    # Buttons for Start and Stop
    BoxLayout:
        orientation: "horizontal"
        spacing: 20
        size_hint: None, None
        size: 300, 50
        pos_hint: {"center_x": 0.5}

        Button:
            text: "Start Streaming"
            on_press: root.start_streaming()
            background_color: 0.3, 0.6, 1, 1  # Blue for start

        Button:
            text: "Stop Streaming"
            on_press: root.stop_streaming()
            background_color: 1, 0.3, 0.3, 1  # Red for stop

    # Error Label
    Label:
        id: error_label
        text: ""
        color: 1, 0, 0, 1
        size_hint: 1, None
        height: 40
"""
class MainWidget(BoxLayout):
    port_val = StringProperty("4982")  # Default port value
    status = StringProperty("Disconnected")  # Initial connection status

    def start_streaming(self):
        """Starts the audio streaming thread."""
        ip_address = socket.gethostbyname(socket.gethostname())
        self.ids.IP_address.text = ip_address
        self.stop_thread = False
        self.audio_thread = Thread(target=self.threaded_function, args=(ip_address,))
        self.audio_thread.start()
        self.ids.connection_label.text = f"Waiting for client"
        self.ids.connection_label.color = (0, 1, 0, 1)  # Green for connected
        print(f"Started streaming to {ip_address}:{self.port_val}")

    def threaded_function(self, ip_address):
        """Handles the audio streaming functionality."""
        try:
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 512

            # Initialize PyAudio and socket
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = int(self.port_val)
            server_socket.bind((ip_address, port))
            server_socket.listen(5)
            print(f"Server is listening on {ip_address}:{port}")

            client_socket, addr = server_socket.accept()
            print(f"Connected by {addr}")
            self.ids.connection_label.text = f"Connected"
            # Streaming loop
            while not self.stop_thread:
                data = stream.read(CHUNK, exception_on_overflow=False)
                client_socket.sendall(data)

        except Exception as e:
            self.ids.error_label.text = f"Error: {e}"
            self.start_streaming()

        finally:
            # Clean up resources
            stream.stop_stream()
            stream.close()
            p.terminate()
            server_socket.close()
            print("Server connection closed.")

    def stop_streaming(self):
        """Stops the audio streaming thread."""
        try:
            if hasattr(self, "audio_thread") and self.audio_thread.is_alive():
                self.stop_thread = True
                self.audio_thread.join()
                self.ids.connection_label.text = "Disconnected"
                self.ids.connection_label.color = (1, 0, 0, 1)  # Red for disconnected
                print("Streaming stopped.")
        except Exception as e:
            print("Error stopping thread:", e)


class OpenMicServer(App):
    def build(self):
        return Builder.load_string(kv)


if __name__ == "__main__":
    OpenMicServer().run()
