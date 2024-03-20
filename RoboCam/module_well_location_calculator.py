"""
Well Location Calculation GUI

Author: Johnny Duong
Creation Date: 8-27-2022

Description: GUI to help calculate all well plate locations and the snaking path.

Ideas:
-Probably only include snaking path.

TODO:
-Put in CSV Loc button/generator
-Put in Snake pattern generator
-Create dummy printer object
-Put in well location calculator functions
-Put in digit checker for row/col
-Test with combining layout lists
-Allow user to put in location
 -Put in X, Y, Z separate boxes?
-get layout function

Changelog:
8-27-2022: Interface is up, but not working.
"""

# Import Statements
import PySimpleGUI as sg

from datetime import datetime

# For Testing Code when not connected to a Raspberry Pi Camera and 3D printer
# ==================================================================================================================
# ======== IMPORTANT: TURN USE_DUMMY_DATA TO False if testing on Raspberry Pi with connected Camera/Printer ========
# ==================================================================================================================
USE_DUMMY_DATA = True

# Constants

# GUI Events and Default Values
# Well Plate Dimensions Layout
# Step 1: Number of Row/Column of Well Plate
ROW_KEY = "-=NUMBER OF ROWS=-"
COL_KEY = "-=NUMBER OF COLUMNS=-"
ROW_COL_SIZE = (4, 1)
WELL_NUMBER_OF_ROWS = 1
WELL_NUMBER_OF_COLS = 1

# TODO: Put in row/col variables that will be changed

# Step 2: 4 Corners
TOP_LEFT_KEY = "-=TOP LEFT=-"
BOTTOM_LEFT_KEY = "-=BOTTOM LEFT=-"
TOP_RIGHT_KEY = "-=TOP RIGHT=-"
BOTTOM_RIGHT_KEY = "-=BOTTOM RIGHT=-"

TOP_LEFT_INPUT = "-=TOP LEFT INPUT=-"
BOTTOM_LEFT_INPUT = "-=BOTTOM LEFT INPUT=-"
TOP_RIGHT_INPUT = "-=TOP RIGHT INPUT=-"
BOTTOM_RIGHT_INPUT = "-=BOTTOM RIGHT INPUT=-"

TOP_LEFT_DICT = {"X": 1.00, "Y": 1.00, "Z": 1.00}
BOTTOM_LEFT_DICT = {"X": 1.00, "Y": 1.00, "Z": 1.00}
TOP_RIGHT_DICT = {"X": 1.00, "Y": 1.00, "Z": 1.00}
BOTTOM_RIGHT_DICT = {"X": 1.00, "Y": 1.00, "Z": 1.00}

DEFAULT_LOC_DICT = {"X": 1.00, "Y": 1.00, "Z": 1.00}

# Init CORNER_LOC_DICT, use for Path Creation
CORNER_LOC_DICT = {TOP_LEFT_KEY: DEFAULT_LOC_DICT, BOTTOM_LEFT_KEY: DEFAULT_LOC_DICT,
                   TOP_RIGHT_KEY: DEFAULT_LOC_DICT, BOTTOM_RIGHT_KEY: DEFAULT_LOC_DICT}

CORNER_INPUT_SIZE = (24, 1)

CORNER_BUTTON_EVENTS = [TOP_LEFT_KEY, BOTTOM_LEFT_KEY, TOP_RIGHT_KEY, BOTTOM_RIGHT_KEY]
CORNER_INPUT_EVENTS = [TOP_LEFT_INPUT, BOTTOM_LEFT_INPUT, TOP_RIGHT_INPUT, BOTTOM_RIGHT_INPUT]

# Step 3: Save Location
SAVE_FOLDER_LOCATION = ""
SAVE_FOLDER_KEY = "-=WELL PLATE LOCATION FOLDER=-"

# Step 4: Create Location Path
BUTTON_SNAKE_PATTERN_LOCATION = "Create Well Path"

# All Well Location Events that need to be checked
WELL_LOCATION_EVENTS = [TOP_LEFT_KEY, BOTTOM_LEFT_KEY, TOP_RIGHT_KEY, BOTTOM_RIGHT_KEY, BUTTON_SNAKE_PATTERN_LOCATION]

# ==== USER DEFINED FUNCTIONS ====


def dummy_loc(event, values):

    # Init dummy result
    result = {"X": 1.00, "Y": 1.00, "Z": 1.00}

    # CORNER_BUTTON_EVENTS = [TOP_LEFT_KEY, BOTTOM_LEFT_KEY, TOP_RIGHT_KEY, BOTTOM_RIGHT_KEY]
    DUMMY_LOC = [{"X": 1.00, "Y": 30.00, "Z": 3.00}, {"X": 1.00, "Y": 2.00, "Z": 3.00},
                 {"X": 30.00, "Y": 30.00, "Z": 3.00}, {"X": 30.00, "Y": 2.00, "Z": 3.00}]

    # Go through button and associated location, then only use that location
    # For example, top-left will get first dummy_loc
    for button, loc in zip(CORNER_BUTTON_EVENTS, DUMMY_LOC):
        if event == button:
            # print(button, loc)
            result = loc

    return result


def get_loc_as_str(loc_dict):
    # print("get_loc_as_str")

    # Init return string
    result = ""

    # Go through key/val from location dictionary
    # Create sample string for display, example: X:1.00 Y:1.00 Z:1.00
    for key, val in loc_dict.items():
        # Print key and val, make sure it shows up
        # print(key, val)

        # Concatenate string, add each value at the end.
        result = result + f"{key}:{val:.2f}"

        # Add commas at the end unless it is the Z
        if key != "Z":
            result = result + ", "

    # Print result, make sure string was concatenated, example: X:1.00 Y:1.00 Z:1.00
    # print(result)

    return result

# Get Layout
# Do this after completing in main


# Event Manager
def event_manager(event, values, window):
    # print("event_manager")

    # Update num row/col input
    update_num_row_col(event, values, window)

    # If event is in step 2, 4 corners
    if event in CORNER_BUTTON_EVENTS:
        print(f"Corner Button Pressed: {event}")

        # TOOD: Need to figure out dummy vs real one. How will the real one work here? Pass printer object?
        current_location = dummy_loc(event, values)
        # print(current_location)
        display_loc = get_loc_as_str(current_location)

        # Loop through corner button and related input_key
        for button, input_key in zip(CORNER_BUTTON_EVENTS, CORNER_INPUT_EVENTS):
            # If the event is one of the "Set Loc" buttons, update the input text to the left.
            if event == button:
                # Print the button/input_key to make sure the pairs are correct, e.g. both are top-left
                # print(button, input_key)

                # Update input text
                window[input_key].update(display_loc)

                # Save to global variable
                update_location_variables(event, current_location)

                # global CORNER_LOC_DICT
                # CORNER_LOC_DICT[event] = current_location

    if event == BUTTON_SNAKE_PATTERN_LOCATION:
        print(event)
        print(CORNER_LOC_DICT)

    # Update Save Folder if chosen
    if len(values[SAVE_FOLDER_KEY]) != 0:
        # print("Updating Save Folder")
        update_save_folder(values)
        # Print save folder to see if it actually updated
        # print(f"SAVE_FOLDER_LOCATION: {SAVE_FOLDER_LOCATION}")

    pass


def update_location_variables(event, current_location):
    # print("update_location_variables")
    # print(event)

    global CORNER_LOC_DICT

    # Update global CORNER_LOC_DICT
    CORNER_LOC_DICT[event] = current_location

    # Print CORNER_LOC_DICT to make sure it works
    # print(CORNER_LOC_DICT)
    pass


def update_num_row_col(event, values, window):
    # print("update_num_row_col")
    global WELL_NUMBER_OF_ROWS, WELL_NUMBER_OF_COLS

    # Extract string num of rows, convert to int.
    num_row = int(values[ROW_KEY])
    # Change global variable
    WELL_NUMBER_OF_ROWS = num_row
    # print(f"WELL_NUMBER_OF_ROWS: {WELL_NUMBER_OF_ROWS}")

    # Extract string num of col, convert to int.
    num_col = int(values[COL_KEY])
    # Change global variable
    WELL_NUMBER_OF_COLS = num_col

    # Print num of row and col, see if it works.
    # print(f"num_row: {num_row}")
    # print(f"num_col: {num_col}")
    pass


def update_save_folder(values):
    global SAVE_FOLDER_LOCATION

    # Change global SAVE_FOLDER_LOCATION
    SAVE_FOLDER_LOCATION = values[SAVE_FOLDER_KEY]

    pass


# Well Location Calculation Functions


# Other Helper Functions

# Define function to create unique text string using date and time.
def get_unique_id():
    current_time = datetime.now()
    unique_id = current_time.strftime("%Y-%m-%d_%H%M%S")
    # print(f"unique_id: {unique_id}")
    return unique_id

# Main Function

def main():
    print("main")

    # Setup Theme
    sg.theme("LightGreen")

    # Well Plate Dimensions Layout

    # Step 1, row/column
    dim_left = [[sg.Text("Number of Rows:")],
                [sg.Text("Number of Columns:")]
                ]

    dim_right = [[sg.Input(WELL_NUMBER_OF_ROWS, size=ROW_COL_SIZE, key=ROW_KEY)],
                 [sg.Input(WELL_NUMBER_OF_COLS, size=ROW_COL_SIZE, key=COL_KEY)]
                 ]

    # Step 2: 4 Corners
    # Original
    """
    corner_left = [[sg.Text("Top-Left:")],
                   [sg.Input("X:1, Y:1, Z:1", size=CORNER_INPUT_SIZE, key=TOP_LEFT_INPUT),
                    sg.Button("Set Loc", key=TOP_LEFT_KEY)],
                   [sg.HorizontalSeparator()],
                   [sg.Text("Bottom-Left")],
                   [sg.Input("X:1, Y:1, Z:1", size=CORNER_INPUT_SIZE, key=BOTTOM_LEFT_INPUT),
                    sg.Button("Set Loc", key=BOTTOM_LEFT_KEY)]
                   ]
    corners_right = [[sg.Text("Top-Right")],
                     [sg.Input("X:1, Y:1, Z:1", size=CORNER_INPUT_SIZE, key=TOP_RIGHT_INPUT),
                      sg.Button("Set Loc", key=TOP_RIGHT_KEY)],
                     [sg.HorizontalSeparator()],
                     [sg.Text("Bottom-Right")],
                     [sg.Input("X:1, Y:1, Z:1", size=CORNER_INPUT_SIZE, key=BOTTOM_RIGHT_INPUT),
                      sg.Button("Set Loc", key=BOTTOM_RIGHT_KEY)]
                    ]
    """
    
    top_left_layout = [[sg.Text("X:"), sg.Input("1.00", size=(7,1)), sg.Text("Y:"), sg.Input("1.00", size=(7,1)), sg.Text("Z:"), sg.Input("1.00", size=(7,1)), sg.Button("Get Loc")]]
    bottom_left_layout = [[sg.Text("X:"), sg.Input("1.00", size=(7,1)), sg.Text("Y:"), sg.Input("1.00", size=(7,1)), sg.Text("Z:"), sg.Input("1.00", size=(7,1)), sg.Button("Get Loc")]]

    top_right_layout = [[sg.Text("X:"), sg.Input("1.00", size=(7,1)), sg.Text("Y:"), sg.Input("1.00", size=(7,1)), sg.Text("Z:"), sg.Input("1.00", size=(7,1)), sg.Button("Get Loc")]]
    bottom_right_layout = [[sg.Text("X:"), sg.Input("1.00", size=(7,1)), sg.Text("Y:"), sg.Input("1.00", size=(7,1)), sg.Text("Z:"), sg.Input("1.00", size=(7,1)), sg.Button("Get Loc")]]
    
    
    # Frame Version
    corners_left = [[sg.Frame("Top-Left", top_left_layout)],
                    [sg.Frame("Bottom-Left", bottom_left_layout)]
                    ]
    
    corners_right = [[sg.Frame("Top-Right", top_right_layout)],
                     [sg.Frame("Bottom-Right", bottom_right_layout)]
                     ]

    # Step 3: Save Folder Location

    # Step 4: Generate Location Files
    # BUTTON_GENERAL_LOCATION = "Create General Location File"

    # Setup Layout
    layout = [[sg.Text("Well Plate Locations Generator")],
              [sg.Text("To get all well plate locations, follow the steps below:")],
              [sg.HorizontalSeparator()],
              [sg.Text("Step 1: Input number of rows and columns of well plate.")],
              [sg.Column(dim_left), sg.Column(dim_right)],
              [sg.HorizontalSeparator()],
              [sg.Text("Step 2: Move camera around, click on 'Set Loc' at each corner of well plate.")],
              [sg.Column(corners_left), sg.Column(corners_right)],
              [sg.HorizontalSeparator()],
              [sg.Text("Step 3: Choose Folder to save Locations File.")],
              [sg.Text("Save Folder"), sg.Input(), sg.FolderBrowse(key=SAVE_FOLDER_KEY)],
              [sg.HorizontalSeparator()],
              [sg.Text("Step 4: Create Well Path File")],
              [sg.Button(BUTTON_SNAKE_PATTERN_LOCATION)]
              ]

    # [sg.Text("Number of Rows:"), sg.Input("1", size=(4, 1), key="-=NUMBER OF ROWS=-")],
    # [sg.Text("Number of Columns:"), sg.Input("1", size=(4, 1), key="-=NUMBER OF COLUMNS=-")]

    # Setup Window
    window = sg.Window("Well Plate Location Generator", layout)

    # Setup GUI While Loop
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event in WELL_LOCATION_EVENTS:
            event_manager(event, values, window)

        # if event != sg.WIN_CLOSED:
        #     check_for_digits(event, values, window)

    print("Closing GUI...")

    pass


def main2():
    print("main2")
    pass


if __name__ == "__main__":
    

    if USE_DUMMY_DATA == True:
        print("Using dummy data")

        class printer:

            def run_gcode(self, gcode_str):
                print("run_gcode: gcode_str")
                pass

            def get_serial_data2(self):
                print("get_serial_data2")
                return "Dummy Serial Data"
                pass

    main()
