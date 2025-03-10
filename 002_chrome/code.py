import cv2
import numpy as np
import mss
from pynput.keyboard import Controller
# chrome://network-error/-106
# Initialize the keyboard controller
keyboard = Controller()

# Define the object detection function for multiple objects
def detect_objects(frame, template, threshold=0.8):
    """
    Detect multiple objects in the frame using template matching and return their positions.
    :param frame: The current screen frame.
    :param template: The template image of the object to detect.
    :param threshold: Detection threshold.
    :return: List of positions (x, y) of detected objects.
    """
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    return list(zip(locations[1], locations[0]))  # Convert to (x, y) format

# Load the object template (replace 'object_template.png' with your template image)
template_path = "object_template.png"
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
template_path2 = "object_template2.png"
template2 = cv2.imread(template_path2, cv2.IMREAD_GRAYSCALE)
mirrored_template = cv2.flip(template, 1)
if template is None:
    print(f"Error: Could not load template from {template_path}")
    exit()

# Define the screen region to monitor (top, left, width, height)
region = {
    "top": 200,  # Starting y-coordinate
    "left": 500,  # Starting x-coordinate
    "width": 800,  # Width of the region
    "height": 300,  # Height of the region
}

# Define the trigger zone (pixels from the left of the region)
trigger_zone_x = 400  # Trigger if the object is within 50 pixels of the left
speed_factor = 1.0
last_x = -1 
# Capture the screen
with mss.mss() as sct:
    print("Monitoring the screen. Press Ctrl+C to exit.")
    
    try:
        while True:
            # Capture the defined region
            screenshot = np.array(sct.grab(region))

            # Convert the screenshot to grayscale
            gray_frame = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            # Detect multiple objects and their positions
            positions = detect_objects(gray_frame, template)
            positions+= detect_objects(gray_frame,mirrored_template)
            positions+= detect_objects(gray_frame,template2)
            if positions:
                # Find the object closest to the left
                leftmost_object = min(positions, key=lambda pos: pos[0])
                x, y = leftmost_object
                # print(f"Leftmost object detected at position: {leftmost_object}")
                if last_x > 0:
                    speed_factor = max(1,(last_x-x)/70)
                    print(f"speed factor {speed_factor}")
                    
                # Check if the leftmost object is in the trigger zone
                if x <= trigger_zone_x * speed_factor:
                    print("Object is close to the left! Pressing space...")
                    keyboard.press(' ')
                    keyboard.release(' ')
                last_x = x 
            # Optional: Draw rectangles around detected objects (for debugging)
            h, w = template.shape  # Height and width of the template
            for pos in positions:
                cv2.rectangle(screenshot, pos, (pos[0] + w, pos[1] + h), (0, 255, 0), 2)

            # Optional: Show the screen with detection visualization
            cv2.imshow("Screen Region", screenshot)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Stopped monitoring.")
    finally:
        cv2.destroyAllWindows()
 # type: ignore