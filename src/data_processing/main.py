import threading
import time
from dotenv import load_dotenv
import os
from Klipper_class import KlipperPrinter
from Camera_class import Camera
import queue

# Load environment variables from .env file
load_dotenv()

url = os.getenv("PRINTER_URL")
# Initialize global variables
interrupt = False  # Flag to control program interruption
status_lock = threading.Lock()  # Thread lock for safe access to shared variables
# printer_lock = threading.Lock()  # Thread lock for printer access
camera_lock = threading.Lock()  # Thread lock for camera access
online_lock = threading.Lock()  # Thread lock for online status
shared_status = None  # Stores the printer's current status
printer = KlipperPrinter(url)  # KlipperPrinter instance
camera = None  # Camera instance
online = False  # Flag to track printer connection status
# Printer URL from environment variable


# TODO:
# consider other thread management than daemon threads
#
def check_printer_availability(url):
    global printer  # Declare global to modify the global printer variable
    global online  # Declare global to modify the global online variable
    global interrupt
    while not interrupt:
        try:

            with online_lock:
                online = printer.check_connection()  # Check printer connection
                print(f"Printer is online {online}")
        except Exception as e:  # Catch specific exceptions for better debugging
            print(f"Printer not online: {e}")
            online = False  # Update the global online variable


def monitor_status(stop_flag):
    """
    Continuously monitors the printer's status in a separate thread
    Args:
        printer: KlipperPrinter instance
        stop_flag: Threading event to signal when to stop monitoring
    """
    global shared_status
    global interrupt
    global printer
    global online
    print(online)
    while online:
        # Check for interrupt signal
        if interrupt:
            break
        try:
            # Safely update shared status using thread lock
            with status_lock:
                shared_status = printer.query_status()

            # Handle different printer states
            if shared_status == "printing":
                print(f"Printer status: {shared_status}")

            elif shared_status != "printing":
                print("Print finished or stopped")
                stop_flag.set()  # Signal other threads to stop
            else:
                print("No status received.")
        except Exception as e:
            print(f"Error while monitoring status: {e}")

        # Pause before next status check
        time.sleep(1)


def read_camera(stop_flag):
    """
    Captures camera frames while printer is printing
    Args:
        stop_flag: Threading event to check when to stop
        camera: Camera instance for capturing frames
    """
    global shared_status
    global interrupt
    while online and not stop_flag.is_set():
        if interrupt:
            break
        try:
            # Only capture frames while printing
            if shared_status == "printing":
                # frame = camera.get_frame()
                print("Capturing frame...")
            else:
                print("No frame captured")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1.0)


# Initialize printer and threading controls
# printer = KlipperPrinter(os.getenv("PRINTER_URL"))
stop_flag = threading.Event()

# Define the threads
availability_thread = threading.Thread(
    target=check_printer_availability, args=(url,), daemon=True
)
status_thread = threading.Thread(target=monitor_status, args=(stop_flag,), daemon=True)
camera_thread = threading.Thread(target=read_camera, args=(stop_flag,), daemon=True)
# Add a third thread for another task (e.g., logging or additional monitoring)


# Start the threads
availability_thread.start()
time.sleep(1)  # Ensure printer is available before starting other threads
status_thread.start()
camera_thread.start()


# Main program loop with interrupt handling
try:
    while status_thread.is_alive() or availability_thread.is_alive():
        status_thread.join(timeout=0.1)
        camera_thread.join(timeout=0.1)
        availability_thread.join(timeout=0.1)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Stopping...")
    interrupt = True
    stop_flag.set()  # Signal all threads to stop

# Wait for all threads to finish
status_thread.join(timeout=1)
camera_thread.join(timeout=1)
availability_thread.join(timeout=1)

print("Program ended")
