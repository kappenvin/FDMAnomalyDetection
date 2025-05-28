import picamera2
import time
from libcamera import controls
import io
from datetime import datetime
from pathlib import Path


class Pizero_Camera:
    def __init__(self, resolution=(1920, 1080)):
        """Initialize camera with default settings."""
        self.camera = None
        self.resolution = resolution
        self.is_started = False
        self.image_bytes = None
        
    def start(self):
        """Start the camera with configuration."""
        if not self.camera:
            self.camera = picamera2.Picamera2()
            config = self.camera.create_still_configuration(main={"size": self.resolution})
            self.camera.configure(config)
        
        if not self.is_started:
            self.camera.start()
            time.sleep(1)  # Allow camera to initialize
            self.is_started = True
    
    def stop(self):
        """Stop the camera."""
        if self.camera and self.is_started:
            self.camera.stop()
            self.is_started = False
    
    def set_resolution(self, width, height):
        """Set camera resolution."""
        self.resolution = (width, height)
        if self.camera:
            self.stop()
            config = self.camera.create_still_configuration(main={"size": self.resolution})
            self.camera.configure(config)
            if not self.is_started:
                self.start()
    
    def save_image(self, filepath=None, format="jpeg"):
        """Capture image and save to file."""
        if not self.camera or not self.is_started:
            raise RuntimeError("Camera not started")
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = Path(f"image_{timestamp}.{format}")
        
        self.camera.capture_file(filepath, format=format)
        
        return filepath


    def capture_image(self, filepath=None, format="jpeg"):
        """Capture image and save to file or return bytes."""
        if not self.camera or not self.is_started:
            raise RuntimeError("Camera not started")
        else:
            # Return bytes
            image_stream = io.BytesIO()
            self.camera.capture_file(image_stream, format=format)
            self.image_bytes = image_stream.getvalue()
            return self.image_bytes
    
    def set_exposure(self, exposure_time):
        """Set camera exposure time."""
        if self.camera:
            self.camera.set_controls({"ExposureTime": exposure_time})
            time.sleep(1)

    def get_metadata(self):
        """Get camera metadata from last capture."""
        if self.camera:
            return self.camera.capture_metadata()
        return None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
