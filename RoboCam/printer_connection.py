"""
Module that sets up 3D Printer with Serial connection and sends GCode

Changelog

27 Apr 2022: Added in get_serial_data2() that loops x times to get
             serial data that isn't empty. Different from get_serial_data(),
             so made a different version.
"""

# import libraries
# camera, serial, time, yaml
import os
import pandas as pd
import picamera
import serial
import time
import yaml

from datetime import datetime

# Import module that loads up 3D Printer settings and such
# Note: Bring over YAML files for 3D Printer Settings, and Path List
import settings as C

# Setup camera and printer
# Create printer/camera variables
# camera = picamera.PiCamera()

# MHT: 270
# camera.rotation = 270

# Cell Sensor, at home, 90
# camera.rotation = 90

printer = serial.Serial(C.DEVICE_PATH, baudrate=C.BAUDRATE, timeout=C.TIMEOUT_TIME)


# User Defined Functions

# Define initial_setup() function for 3D printer
def initial_setup(path_list):
    global printer
    FIRST_LOCATION = 0
    X = 0
    Y = 1
    Z = 2

    # Check if 3D printer is connected
    if printer.isOpen():
        print('Connected to printer')

    # starting_location_x = path_list[0][X]
    # starting_location_y = path_list[FIRST_LOCATION][Y]
    starting_location_z = path_list[FIRST_LOCATION][Z]

    starting_location_x = 0
    starting_location_y = 200

    # Wait for Printer to Finish Rebooting
    print('Printer is rebooting...\n')
    print("Waiting for", C.REBOOT_WAIT_TIME, "seconds")
    time.sleep(C.REBOOT_WAIT_TIME)
    print("Done Waiting, Moving Extruder and Build Plate to Origin/Home\n")
    # printer.write(b'G28\n')
    go_home()
    time.sleep(C.REBOOT_WAIT_TIME)
    # time.sleep(10)
    
    # move_extruder_out_of_the_way(x=starting_location_x, y=starting_location_y, z=starting_location_z)
    # start_position_z = "G0Z{}".format(starting_location_z)
    # run_gcode(start_position_z)
    # time.sleep(8)
    # start_position = "G0X{}Y{}".format(starting_location_x, starting_location_y)
    # run_gcode(start_position)
    # time.sleep(8)


def move_extruder_out_of_the_way(x, y, z):
    WAIT_TIME = 1
    
    start_position_z = "G0Z{}".format(z)
    run_gcode(start_position_z)
    time.sleep(WAIT_TIME)
    start_position = "G0X{}Y{}".format(x, y)
    run_gcode(start_position)
    time.sleep(WAIT_TIME)
    

# Function: Make Extruder and Build Plate Go to Origin/Home.
def go_home():
    run_gcode(C.HOME)


# Define Function That Runs Relative Coordinates
# Inputs, cartesian direction (x, y, or z), and the amount (float, can be positive or negative)
# Runs G91 GCode first
# Converts direction and amount into a gcode string, sends to run_gcode.

# Define function, run_gcode_ that runs a GCode string
# Function: Convert String to binary/Gcode, write to serial
def run_gcode(gcode_string):
    # Converts String to Binary UTF-8 Format for GCode Strings
    #  Adds new line character at the end.

    # GCode_string examples:
    #  G28
    #  G1X100Y100

    # Call the global printer variable
    global printer
    # Add new line character at the end of the string
    print(gcode_string)
    gcode_string = gcode_string + "\n"

    # Convert to Binary with UTF-8 encoding for string, write to serial
    # printer.write(bytes(gcode_string, "utf-8"))
    printer.write(str.encode(gcode_string))

    # camera.start_preview(fullscreen=False, window=(30, 30, 500, 500))
    # time.sleep(5)
    # camera.stop_preview()


# define function go_home() to go to home coordinates


# Define function to open YAML paths file, then extracts/returns paths list
def get_path_list(yaml_file):
    # TODO: Convert this to CSV grabber, then convert to a list.
    with open(yaml_file) as file:
        path_list = yaml.load(file, Loader=yaml.FullLoader)
        # print(path_list)
        return path_list


# Get path list from CSV file
def get_path_list_csv(csv_filename):
    # Setup Constants for Function
    X = 0
    Y = 1
    Z = 2

    # Use Pandas to open up CSV File
    # index_col is 0, meaning no column label for index column
    dataframe = pd.read_csv(csv_filename, index_col=0, dtype="float")
    # print(dataframe)

    # Create empty path_list variable
    path_list = []

    # Use iterows to go through each row to extract x, y, and z
    for row_index, row in dataframe.iterrows():
        # Place x, y, z values into a temp_list
        temp_list = [row[X], row[Y], row[Z]]

        # Append temp list to path_list
        path_list.append(temp_list)
        # TODO: Consider converting to GCODE list here, output float list and gcode list?

    return path_list


# Function that takes in a path list (not an array or matrix), but a list of lists,
# returns a similar dimension list of gcode formatted strings
def convert_list_to_gcode_strings(path_list):
    X = 0;
    Y = 1;
    Z = 2

    # print("convert_list_to_gcode_strings")
    # print(path_list)
    position = "G0"
    gcode_string_list = []
    number_of_locations = len(path_list)

    for location in path_list:
        x = location[X]
        y = location[Y]
        z = location[Z]
        # print(x, y, z)
        gcode_string = "{}X{}Y{}Z{}".format(position, x, y, z)
        # print(gcode_string)
        gcode_string_list.append(gcode_string)
    # print(gcode_string_list)

    # TODO: Can I achieve this with a list comprehension?
    return gcode_string_list
    pass


# Define function, start_experiment with flag isPreviewModeOn, isRecordingModeOn
# def start_experiment(gcode_string_list):
    # #   If isPreviewModeOn is true, no pictures/video taken, but camera stays on to show location movements
    # #   else take picture or video (check isRecordingModeOn flag)

    # # Create Folder (based on conditions)
    # if C.isPreviewModeOn == False:
        # folder_path = create_and_get_folder_path()

    # # Go into Absolute Positioning Mode
    # run_gcode(C.ABSOLUTE_POS)

    # while True:
        # # Use for loop to go through each gcode string list
        # well_number = 1
        # for gcode_string in gcode_string_list:
            # # print(gcode_string)
            # run_gcode(gcode_string)
            # time.sleep(4)
            # if C.isPreviewModeOn == True:
                # print("Preview Mode is On, only showing preview camera")
                # camera.start_preview(fullscreen=False, window=(30, 30, 500, 500))
                # time.sleep(5)

                # # camera.stop_preview()
            # elif C.isVideoCaptureModeOn == True:
                # print("Recording Video Footage")
                # file_full_path = get_file_full_path(folder_path, well_number)
                # # TODO: Change to Video Captures
                # # camera.capture(file_full_path)
            # elif C.isPictureCaptureModeOn == True:
                # print("Taking Pictures Only")
                # file_full_path = get_file_full_path(folder_path, well_number)
                # print(file_full_path)
                # camera.capture(file_full_path)
                # # TODO: Look up Camera settings to remove white balance (to deal with increasing brightness)

                # camera.capture(file_full_path)
            # well_number += 1

    # if C.isPreviewModeOn == True:
        # camera.stop_preview()


# Define function that creates folder for experiment if VideoCapture or PictureCapture is on
# returns folder path too
# Creates a unique folder name using current date and time
def create_and_get_folder_path():
    # Get Folder Path
    folder_path = "{}{}".format(C.FOLDERPATH, C.FOLDERNAME_PREFIX)
    # print(folder_path)
    current_time = datetime.now()
    folder_name_suffix = current_time.strftime("%Y-%m-%d_%H%M%S")
    # print(folder_name_suffix)

    folder_path_complete = ""

    if C.isVideoCaptureModeOn == True:
        print("Recording Video Footage")
        folder_path_complete = "{}_Videos_{}".format(folder_path, folder_name_suffix)
        print(folder_path_complete)
    elif C.isPictureCaptureModeOn == True:
        folder_path_complete = "{}_Pictures_{}".format(folder_path, folder_name_suffix)
        print("Taking Pictures Only")

    # Check if folder exists, if not, create it
    if not os.path.isdir(folder_path_complete):
        print("Folder Does NOT exist! Making New Folder")
        os.mkdir(folder_path_complete)
    else:
        print("Folder Exists")

    # Return Folder Path
    return folder_path_complete


# Define function that creates the full file path to save video or pictures (folder and file name)
# Creates a unique file name using current date and time
def get_file_full_path(folder_path, well_number):
    current_time = datetime.now()
    # file_name_suffix = current_time.strftime("%Y-%m-%d_%H%M%S_%f")
    file_name_suffix = current_time.strftime("%Y-%m-%d_%H%M%S")
    file_name_full = "well{}_{}.jpg".format(well_number, file_name_suffix)
    file_full_path = "{}/{}".format(folder_path, file_name_full)
    # print(file_full_path)
    return file_full_path


# Define function that checks status of extruder
# TODO: Future feature


# Define menu function to ask to start experiment
def menu(gcode_string_list):
    # Ask user if they want to start the experiment (yes/no) in a while loop
    # if yes, run start_experiment
    # if no, exit
    # else, invalid input

    while True:
        user_input = input("Start experiment (y/n)? ")

        user_input = user_input.lower()

        if user_input == "y":
            start_experiment(gcode_string_list)
        elif user_input == "n":
            print("Exiting Programm...")
            break
        else:
            print("Invalid Input. Please Try Again.")
            continue

    pass


# Function: Listen on Serial Port, print results
def output_serial_data():
    global printer
    
    # output = printer.readline()
    printer.flush()
    bytesToRead = printer.inWaiting()
    print("bytesToRead:", bytesToRead)
    output = printer.read(bytesToRead)
    # output = printer.read(512)
    # output = str(output)
    output = output.decode("utf-8")
    print("Serial Says:", output)

def get_serial_data():
    global printer
    
    # output = printer.readline()
    printer.flush()
    bytesToRead = printer.inWaiting()
    print("bytesToRead:", bytesToRead)
    output = printer.read(bytesToRead)
    # output = printer.read(512)
    # output = str(output)
    output = output.decode("utf-8")
    # print("Serial Says:", output)
    return output

def get_serial_data2():
    global printer
    
    # init default output
    output = ""
    
    # Number of attempts to get bytes > 0
    num_tries = 20
    
    # output = printer.readline()
    # init bytesToRead to 0 so while loop fires
    bytesToRead = 0
    for i in range(num_tries):
    # while bytesToRead == 0:
        printer.flush()
        bytesToRead = printer.inWaiting()
        # If no serial data found, start loop again.
        if bytesToRead == 0:
            # if no bytes found, then maybe too many requests.
            # Sleep for a second to let 3D printer "relax"
            time.sleep(1)
            continue
        else:
            # bytesToRead > 0, capture it and break the loop
            # print("bytesToRead:", bytesToRead)
            output = printer.read(bytesToRead)
            # output = printer.read(512)
            # output = str(output)
            output = output.decode("utf-8")
            # print("Serial Says:", output)
            break
    return output
