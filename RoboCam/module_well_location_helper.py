"""
Module: Well Location Helper
aka Cross Hair
Author: Johnny Duong

Description: Draws cross hairs on image for easier centering.
Cross hair is made up of horizontal and vertical lines intersecting the center of the image,
and a circle with an adjustable radius. Line and circle thickness can be changed (filled circle disabled for now).
GUI will check for numbers only in the input boxes for line and circle thickness.
User can change color for circle and line.

Future Ideas
-How to auto-update crosshair preview when moving around 3D printer in MVMT tab
-Ellipse instead of circle?

Changelog:
8-27-2022: Started changelog. Working Cross hair GUI. Create dummy PiCamera class for easier RPi transfer.

"""
import cv2
import PySimpleGUI as sg

from os import remove
from os.path import join
from PIL import ImageColor


# For Testing Code when not connected to a Raspberry Pi Camera and 3D printer
# ==========================================================================================================
# ======== IMPORTANT: TURN USE_DUMMY_DATA TO False if testing on Raspberry Pi with connected Camera ========
# ==========================================================================================================
USE_DUMMY_DATA = True

# Events
LOAD_IMAGE = "Update/Load Image"

# Circle Cross Hair Default Values
CIRCLE_RADIUS = 100
CIRCLE_COLOR = (0, 0, 255) # BGR
CIRCLE_THICKNESS = 1

# Circle Events
CIRCLE_THICKNESS_KEY = "-=CIRCLE THICKNESS KEY=-"

RAD_KEY = "-RADIUS-"
RAD_MINUS_TEN = "-RAD MINUS_TEN-"
RAD_MINUS_ONE = "-RAD MINUS_ONE-"
RAD_PLUS_ONE = "-RAD PLUS ONE-"
RAD_PLUS_TEN = "-RAD PLUS TEN-"

CIRCLE_EVENT_LIST = [RAD_MINUS_TEN, RAD_MINUS_ONE, RAD_PLUS_ONE, RAD_PLUS_TEN]

# Line Events and Default Value
LINE_THICKNESS_KEY = "-=LINE THICKNESS KEY=-"
LINE_THICKNESS = 1

# Color Choose Event
COLOR_CHOOSER_KEY = "-= COLOR CHOOSER KEY =-"

# PREVIEW_ON_KEY = "-=PREVIEW ON=-"

# Checking for numbers only in Line/Circle Input Texts Event
DIGIT_EVENTS = [CIRCLE_THICKNESS_KEY, LINE_THICKNESS_KEY]

# All events for the event manager to fire
ALL_CROSS_HAIR_EVENTS = [LOAD_IMAGE, RAD_MINUS_TEN, RAD_MINUS_ONE, RAD_PLUS_ONE, RAD_PLUS_TEN, COLOR_CHOOSER_KEY]

# Camera Hacks, capture to a temp file to quick loading
# TODO: Capture image to byte
temp_filename = "temp.jpg"


def get_dummy_image():
    # Dummy Image as placeholder

    # Windows
    image_folder = r'D:\Documents\SF State\Dr. E Lab\Spring 2022\RoboCam\7-25-2022\Code_Pictures_2022-07-25_171105_auto'
    image_file = r'well1_2022-07-25_171110.jpg'

    # RPi
    # image_folder = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/8-24-2022'
    # image_file = r'test_2022-08-24_161919_640x480.jpg'

    # image_location
    image_path = join(image_folder, image_file)
    # Dummy resize to 640, 480
    image = cv2.imread(image_path)
    image_resize = cv2.resize(image, (640, 480))

    return image_resize


def update_circle(event, values, window):
    global CIRCLE_RADIUS, CIRCLE_THICKNESS

    if event == LOAD_IMAGE:
        CIRCLE_RADIUS = int(values[RAD_KEY])

    if event == RAD_MINUS_TEN:
        CIRCLE_RADIUS -= 10
    elif event == RAD_MINUS_ONE:
        CIRCLE_RADIUS -= 1
    elif event == RAD_PLUS_ONE:
        CIRCLE_RADIUS += 1
    elif event == RAD_PLUS_TEN:
        CIRCLE_RADIUS += 10

    # Update Circle Thickness
    circle_thick_number = int(values[CIRCLE_THICKNESS_KEY])
    CIRCLE_THICKNESS = circle_thick_number

    # Update Window Values for Circle Radius
    window[RAD_KEY].update(CIRCLE_RADIUS)
    pass


def update_line_thickness(values):
    global LINE_THICKNESS

    # Update LINE_THICKNESS global variable
    thick_number = int(values[LINE_THICKNESS_KEY])
    LINE_THICKNESS = thick_number
    pass


def draw_on_image(camera):

    # Temp image get
    # image = get_dummy_image()
    # image_edit = image.copy()
    
    # Get image from camera
    # temp_filename = "temp.jpg"
    camera.capture(temp_filename)
    image = cv2.imread(temp_filename)
    image_edit = image.copy()

    # Get dimensions of image
    # print(image.shape)
    height, width, ch = image.shape
    # Get center x, center y.
    center_x = int(width / 2)
    center_y = int(height / 2)
    # print(f"Center: {center_x, center_y}")

    image_edit = draw_cross_hairs(image)

    # On copy, Draw circle at center x/y with radius
    center_coordinates = (center_x, center_y)
    image_edit = cv2.circle(image_edit, center_coordinates, CIRCLE_RADIUS, CIRCLE_COLOR, CIRCLE_THICKNESS)

    # Display Image
    cv2.imshow("Cross Hair Preview", image_edit)
    cv2.waitKey(100)
    pass


def draw_cross_hairs(image):
    # Make a copy of the image
    image_edit = image.copy()

    # Get dimensions of image
    # print(image.shape)
    height, width, ch = image.shape
    # Get center x, center y.
    center_x = int(width / 2)
    center_y = int(height / 2)
    # print(f"Center: {center_x, center_y}")

    # Draw Center Horizontal Line
    start_point = (0, center_y)
    end_point = (width, center_y)
    image_edit = cv2.line(image_edit, start_point, end_point, CIRCLE_COLOR, LINE_THICKNESS)

    # Draw Center Vertical Line
    start_point = (center_x, 0)
    end_point = (center_x, height)
    image_edit = cv2.line(image_edit, start_point, end_point, CIRCLE_COLOR, LINE_THICKNESS)

    return image_edit


def update_color(event, values, window):
    global CIRCLE_COLOR
    # print("Updating Circle and Line Colors")
    # print(f"New Color: {values[event]}")
    rgb_color = ImageColor.getcolor(values[event], "RGB")
    # print(f"RGB: {rgb_color}")
    bgr_color = (rgb_color[2], rgb_color[1], rgb_color[0])
    # print(f"BGR: {bgr_color}")
    CIRCLE_COLOR = bgr_color
    print(f"Updating Circle and Line Colors to RGB: {rgb_color}")
    pass


def event_manager(event, values, window, camera):
    
    # if event in CIRCLE_EVENT_LIST:
    #     # print("Circle event detected")
    #     # update_circle(event, values, window, camera)
    #     update_line_thickness(values)
    #     update_circle(event, values, window)
    #
    # if event == LOAD_IMAGE:
    #     # print(f"Pressed: {LOAD_IMAGE}")
    #
    #     # Update Line Thickness
    #     update_line_thickness(values)
    #
    #     update_circle(event, values, window)
    #
    #     # Preview On/Off Test
    #     # window[PREVIEW_ON_KEY].update(True)
    #     # draw_on_image()

    # if event in CIRCLE_EVENT_LIST or event == LOAD_IMAGE:
    #     update_line_thickness(values)
    #     update_circle(event, values, window)

    if event == COLOR_CHOOSER_KEY:
        update_color(event, values, window)

    # Event manager only fires if Cross Hair Events are triggered,
    # So update line and circle value, then draw on the image.
    update_line_thickness(values)
    update_circle(event, values, window)
    draw_on_image(camera)

    # if values[PREVIEW_ON_KEY] == True:
    #     draw_on_image()
    pass


# ==== Get GUI Layout ====
def get_cross_hair_layout():

    layout = [[sg.Button(LOAD_IMAGE)],
              [sg.Text("Circle Radius:"),
               sg.Button("-10", key=RAD_MINUS_TEN), sg.Button("-1", key=RAD_MINUS_ONE),
               sg.Input(CIRCLE_RADIUS, size=(4, 1), key=RAD_KEY),
               sg.Button("+1", key=RAD_PLUS_ONE), sg.Button("+10", key=RAD_PLUS_TEN)],
              [sg.Text("Circle Thickness:"), sg.Input(CIRCLE_THICKNESS, size=(4, 1), key=CIRCLE_THICKNESS_KEY)],
              [sg.Text("Line Thickness:"), sg.Input(LINE_THICKNESS, size=(4, 1), key=LINE_THICKNESS_KEY)],
              [sg.Input(size=(8, 1), key=COLOR_CHOOSER_KEY, enable_events=True),
               sg.ColorChooserButton("Change Line/Circle Color", target=COLOR_CHOOSER_KEY)]]

    # Radio Button layout, thinking about how to implement this
    # sg.Text("Cross Hair Preview:"),
    # sg.Radio("On", group_id="PREVIEW_RADIO", default=False, key=PREVIEW_ON_KEY),
    # sg.Radio("Off", group_id="PREVIEW_RADIO", default=True)

    return layout


# ==== DIGIT CHECK FUNCTIONS START ====
def check_for_digits(event, values, window):

    for key_str in DIGIT_EVENTS:
        # print(key_str)
        check_for_digits_in_key(key_str, event, values, window)

    pass


def does_string_have_non_digit(input_string):
    # Return True if there is at least one non-digit in string, assumes at least 1 char in string
    result = False

    for char in input_string:
        if not char.isdigit():
            result = True
            break
    return result


# Define function to check an InputText key for digits only
def check_for_digits_in_key(key_str, event, values, window):
    # print("check_for_digits_in_key")

    # Go through each character, only return digits
    digit_only_str = ""
    # Only run this if the values[key_str] has at least 1 character in there.
    if len(values[key_str]):
        # Check if at least one non-digit exists in values[key_str]
        #   If it exists, only allow digits in string
        if does_string_have_non_digit(values[key_str]):
            for char in values[key_str]:
                if char.isdigit():
                    # Concatenate
                    digit_only_str = digit_only_str + char
            # Update that InputText with removed letters

            if len(digit_only_str) == 0:
                # If accidentally replacing all with a letter, replace with a zero
                # TODO: Figure out how to replace with previous value
                window[key_str].update("1")
            else:
                window[key_str].update(digit_only_str)

# ==== DIGIT CHECK FUNCTIONS END ====


# ==== MAIN ====
# For testing the Cross Hair GUI and functions without being on the Raspberry Pi
def main():
    print("Main")

    # Setup Camera (dummy if not Raspberry Pi)
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32

    # Setup sg theme
    sg.theme("LightGreen")

    # Setup layout
    layout = get_cross_hair_layout()
    
    # Setup window
    window = sg.Window("Cross Hair Test", layout=layout)

    # Start while loop for GUI
    while True:
        event, values = window.read(timeout=1)

        # Uncomment to check what event and values are displayed. Useful for Color Picker.
        # print(event, values)

        if event == sg.WIN_CLOSED:
            break
            
        if event in ALL_CROSS_HAIR_EVENTS:
            # event_manager(event, values, window, camera)
            event_manager(event, values, window, camera)

        # If not closing, check for digits. Prevents code from crashing when closing GUI.
        if event != sg.WIN_CLOSED:
            check_for_digits(event, values, window)

    print("Closing GUI...")
    # Delete temp.jpg
    print(f"Deleting {temp_filename}")
    remove(temp_filename)
    pass


# Sanity Test, does OpenCV actually load the image?
def main2():
    print("main2")

    image_folder = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/8-24-2022'
    image_file = r'test_2022-08-24_161919_640x480.jpg'
    image_path = join(image_folder, image_file)
    # Dummy resize to 640, 480
    image = cv2.imread(image_path)
    cv2.imshow("image", image)
    cv2.waitKey(10000)
    pass


if __name__ == "__main__":
    # Load PiCamera Library
    # from picamera import PiCamera

    # main()
    # main2()
    if USE_DUMMY_DATA == False:
        # Load PiCamera Library
        from picamera import PiCamera
    else:
        print("Do use Dummy Data")

        # Create dummy PiCamera class to make transferring to RPi easier
        class PiCamera:
            resolution = (640, 480)
            framerate = 32

            def capture(self, save_filename):
                # print("capture called")

                # Get dummy image
                image = get_dummy_image()
                # Save dummy image as save_filename
                cv2.imwrite(save_filename, image)
                pass

    # Out of if/else statement, call the main function
    main()
    # main2()

