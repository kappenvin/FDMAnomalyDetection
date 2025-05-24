import picamera2
import time
from libcamera import controls 
import json
from database_src.models import ImageData
from datetime import datetime
import io 
from database_src.database import Session

output_path = "captured_image.jpg"  
camera = None # Initialize camera to None so it can be checked in finally

try:
    camera = picamera2.Picamera2()
    # Optional: If you need specific configurations, you can create and apply them.
    # For example, to set resolution:
    config = camera.create_still_configuration(main={"size": (1920, 1080)})
    camera.configure(config)

    camera.start()
    time.sleep(1)  # Allow a short moment for the camera to initialize
    # Capture an image and save it to the specified path
    # Capture an image into a bytes variable
    image_stream = io.BytesIO()
    camera.capture_file(image_stream, format="jpeg")
    image_bytes = image_stream.getvalue()

    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if camera: # Only stop if camera was successfully initialized
        camera.stop()  # Ensure camera is stopped


# Get current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Timestamp: {timestamp}")

"""
image_data = ImageData(
    image=image_bytes,
    timestamp=timestamp,
    slicer_settings_id= None,  # Replace with actual slicer settings ID if available
    parts_id= None,  # Replace with actual parts ID if available
    label= None,
    layer= None,
    
)

session= Session()
session.add(image_data)
session.commit()
session.close()
"""