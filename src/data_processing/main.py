import threading
import time
from dotenv import load_dotenv
import os
from Klipper_class import KlipperPrinter
from utils.camera_class import Pizero_Camera
from database_src.upload_data import upload_image_db, upload_slicer_settings_db,upload_part_db
import datetime
from utils.pwm_led import PwmLed
from utils.extract_gcode_from_string import extract_relevant_slicing_parameters_from_string

# Load environment variables from .env file
load_dotenv()

url = os.getenv("PRINTER_URL")
# Initialize global variables
interrupt = False 
shared_status = None  
slicer_settings_id = None  
parts_id = None  
stop_flag = threading.Event()  # Move this up to be available globally
layer = 0
online = False 

# initialize LED 
led = PwmLed()
led.setup()

# Initiliaze camera
camera = Pizero_Camera()  # Camera instance
camera.start()
camera.set_exposure(10000)


# start the LEDS


def upload_image(stop_flag):
    """
    Captures camera frames while printer is printing
    Args:
        stop_flag: Threading event to check when to stop
        camera: Camera instance for capturing frames
    """
    led_first = True  # Flag to check if it's the first time capturing a frame
    global shared_status
    global slicer_settings_id
    global parts_id
    global printer
    global online
    global layer
    global led
    global camera 

    while not stop_flag.is_set():

        if online and shared_status == "printing" and layer != 0:
            if led_first:
                led.on()
                led.set_brightness(80)
                print("LED turned on")
                led_first = False
            try:
                # Only capture frames while printing
                
                frame = camera.capture_image()  # Capture a frame from the camera
                current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                """
                # Save the captured frame locally for debugging
                local_filepath = f"captured_frame_{current_datetime}.jpeg"
                with open(local_filepath, "wb") as f:
                    f.write(frame)
                print(f"Saved frame locally to {local_filepath}")
                """

                # Get the current layer from the printer
                upload_image_db(frame, current_datetime, slicer_settings_id, parts_id, label=None, layer=layer)

                print("Capturing frame...")
                
            except Exception as e:
                print(f"Error: {e}")
                led.off()  # Turn off the LED if there's an error
                print("LED turned off due to error")
        else:
            print("No frame captured")
            led.off()  # Turn off the LED if not printing

        time.sleep(1.0)  # Add a delay to avoid excessive frame capture

def upload_slicer_settings():
    """
    Gets the current G-code from the printer, extracts slicer settings, 
    and uploads them to the database.
    
    Returns:
        int or None: The slicer settings ID if successful, None if failed.
    """
    global slicer_settings_id
    global printer
    global online
    global interrupt
        
    try:
        params = printer.extract_gcode_params()  # Get G-code parameters from the printer
        
        
        # Upload slicer settings to database (params, gcode_content)
        slicer_settings_id = upload_slicer_settings_db(params)  
        
        if slicer_settings_id:
            print(f"Slicer settings uploaded with ID: {slicer_settings_id}")
        else:
            print("Failed to upload slicer settings to database")
            
        return slicer_settings_id
        
    except Exception as e:
        print(f"Error uploading slicer settings: {e}")
        return None

def upload_part():
    """
    Uploads part information to the database
    
    Returns:
        int or None: The parts ID if successful, None if failed.
    """
    global parts_id
    global printer
    global online

    try:
        part_name = printer.get_part_name()  # Get the part name from the printer
        parts_id = upload_part_db(part_name)  # Upload part information to the database
        print(f"Part uploaded with ID: {parts_id}")
        return parts_id
    except Exception as e:
        print(f"Error uploading part: {e}")
        return None
    

def check_printer_availability(url):
    global printer  # Declare global to modify the global printer variable
    global online  # Declare global to modify the global online variable
    global interrupt
    while not stop_flag.is_set():
        try:
            online = printer.check_connection()  # Check printer connection
            print(f"Printer is online {online}")
        except Exception as e:  
            print(f"Printer not online: {e}")
            online = False  # Update the global online variable
        
        time.sleep(1.0)  # Add delay to avoid excessive polling


def monitor_status(stop_flag):
    """
    Continuously monitors the printer's status in a separate thread
    Args:
        printer: KlipperPrinter instance
        stop_flag: Threading event to signal when to stop monitoring
    """
    slicer_settings_uploaded = False
    parts_uploaded = False
    global shared_status
    global printer
    global online
    global layer

    
    while not stop_flag.is_set():
        # Check for interrupt signal
        if online:
            try:
                shared_status = printer.query_status()

                # Handle different printer states
                if shared_status == "printing":
                    #print(f"Printer status: {shared_status}")
                    layer = printer.get_current_layer()
                    if not slicer_settings_uploaded:
                        slicer_settings_uploaded = True
                        slicer_settings_id=upload_slicer_settings()
                        
                    if not parts_uploaded:
                        parts_uploaded = True
                        parts_id=upload_part()

                        
                elif shared_status != "printing":
                    slicer_settings_uploaded = False
                    parts_uploaded = False
                    #print("no printing")
                    
                else:
                    print("No status received.")
            except Exception as e:
                print(f"Error while monitoring status: {e}")

            # Pause before next status check
        time.sleep(0.1)

if __name__ == "__main__":
    # Start the camera and printer instances
    printer = KlipperPrinter(url)  # KlipperPrinter instance

    # Define the threads
    availability_thread = threading.Thread(
        target=check_printer_availability, args=(url,), daemon=True
    )
    status_thread = threading.Thread(target=monitor_status, args=(stop_flag,), daemon=True)
    upload_image_thread = threading.Thread(target=upload_image, args=(stop_flag,), daemon=True)
    # Add a third thread for another task (e.g., logging or additional monitoring)


    # Start the threads
    availability_thread.start()
    time.sleep(1)  
    status_thread.start()
    time.sleep(1)
    upload_image_thread.start()


    # Main program loop with interrupt handling
    try:
        while status_thread.is_alive() or availability_thread.is_alive():
            status_thread.join(timeout=0.1)
            upload_image_thread.join(timeout=0.1)
            availability_thread.join(timeout=0.1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping...")
        interrupt = True
        stop_flag.set()  # Signal all threads to stop
        camera.stop()
        led.off()
        led.cleanup()

    # Wait for all threads to finish
    status_thread.join(timeout=1)
    upload_image_thread.join(timeout=1)
    availability_thread.join(timeout=1)

    print("Program ended")
