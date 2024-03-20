"""
Graphical User Interface for using the 3D Printer to take picture/video samples
Author: Johnny Duong, Center for Cellular Construction
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, 
Center for Cellular Construction. Disclaimer:  Any opinions, findings and conclusions 
or recommendations expressed in this material are those of the authors and do not 
necessarily reflect the views of the National Science Foundation.
San Francisco State University

Current Features:
-Has Camera Feed
-Can move X, Y, Z of 3D Printer in various relative direction and increments
-Can get Current Location of Extruder Nozzle
-Input Custom GCode

Future Features:
-Smart Movement: Only take a picture or video if current location is
                 the destination (+/- 1 mm)
-Be able to take picture/video without interferring with camera feed
-Save/Open CSV Option for locations
-Preview Sample Locations
-Run Experiment (photo or video, maybe use a radio button)
   -Run for x iterations
-Camera Settings (white balance, sharpness, and so on)
-Display Current Location in GUI

Current TODO List:
-Get Current Location Mananger (runs it twice to get location)
-Put GUI Keys/Text as Constants
-Experiment with Tabs
 Source: https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Tabs_Simple.py
         https://csveda.com/creating-tabbed-interface-using-pysimplegui/

Changelog
24 Aug 2022: User can choose where to save experiment folder (CAM tab)
16 May 2022: Removed PiRGBArray Camera Preview and implemented PiCamera Preview + hacks for window control!
25 Apr 2022: Fixed restart bug, can now run multiple experiments without restarting GUI!
             Solution: Use flag to make experiment function end and make forever while loop.
21 Apr 2022: Added in Z Stack Creator
13 Apr 2022: Added Camera Tab to adjust picture capture resolution for "Pic" button and will show resize image.
06 Jun 2021: Can take pictures in Experiment Thread. No video yet. Can't change resolution, bugs out. Buffer issue?
05 Jun 2021: Added in Experiment Thread, can now run GUI and Experiment at the same time.
28 Apr 2021: Changed Experiment variables into CONSTANTS
26 Apr 2021: Added in 2 Tabs: Start Experiment and Movement
18 Apr 2021: Started Changelog, Allow user to input their own GCode.

"""

# Import PySimpleGUI, cv2, numpy, time libraries
# Import picamera libraries

from datetime import datetime
from picamera.array import PiRGBArray, PiBayerArray
from picamera import PiCamera
from Xlib.display import Display
import csv
import PySimpleGUI as sg
import cv2
import numpy as np
import os
import time
import threading
import random

# Import modules
import settings as C
import get_current_location_m114 as GCL
import printer_connection as printer
import prepare_experiment as P
import module_get_cam_settings as GCS
import module_experiment_timer as ET
import module_well_location_helper as WL

# ==== USER CONSTANTS - GUI ====
# TODO: Put these in a YAML GUI Settings File?

# ---- EXPERIMENT CONSTANTS ----
OPEN_CSV_PROMPT = "Open CSV:"
OPEN_CSV_FILEBROWSE_KEY = "-CSV_INPUT-"
START_EXPERIMENT = "Start Experiment"
STOP_EXPERIMENT = "Stop Experiment"
MAX_NUMBER_EXPERIMENTAL_RUNS = 1

# ---- RADIO GUI KEYS AND TEXT ----
EXP_RADIO_PIC_KEY = "-RADIO_PIC-"
EXP_RADIO_VID_KEY = "-RADIO_VID-"
EXP_RADIO_PREVIEW_KEY = "-RADIO_PREVIEW-"
EXP_RADIO_GROUP = "RADIO_EXP"
EXP_RADIO_PIC_TEXT = "Picture"
EXP_RADIO_VID_TEXT = "Video"
EXP_RADIO_PREVIEW_TEXT = "Preview"
EXP_RADIO_PROMPT = "For the experiment, choose to take Pictures, Videos, or Preview Only"

# ---- CAMERA TAB ----
# CONSTANTS
PIC_SAVE_FOLDER = r"/home/pi/Projects/3dprinter_sampling"

# Video Streaming:
# Old = 640x480
"""
VID_WIDTH = 640
VID_HEIGHT = 480
"""
VID_WIDTH = 960
VID_HEIGHT = 720
VID_RES = (VID_WIDTH, VID_HEIGHT)

# Image Capture Resolution
# Take a Picture, 12MP: 4056x3040
PIC_WIDTH = 4056
PIC_HEIGHT = 3040
PIC_RES = (PIC_WIDTH, PIC_HEIGHT)

# Monitor Resolution (The one you're using to look at this)
MON_WIDTH = 1920
MON_HEIGHT = 1080
MON_RES = (MON_WIDTH, MON_HEIGHT)

# GUI CONSTANTS
# Button Labels:
UPDATE_CAMERA_TEXT = "Update Camera Settings"

# Camera GUI Keys
CAMERA_ROTATION_KEY = "-ROTATION_INPUT-"
PIC_WIDTH_KEY = "-PIC_WIDTH_INPUT-"
PIC_HEIGHT_KEY = "-PIC_HEIGHT_INPUT-"
PIC_SAVE_FOLDER_KEY = "-PIC_SAVE_FOLDER_INPUT-"


# --- MOVEMENT CONSTANTS ----
# Radio Keys
RELATIVE_TENTH_KEY = "-REL_TENTH-"
RELATIVE_ONE_KEY = "-REL_ONE-"
RELATIVE_TEN_KEY = "-REL_TEN-"
RADIO_GROUP = "RADIO1"
RELATIVE_TENTH_TEXT = "0.10mm"
RELATIVE_ONE_TEXT = "1.00mm"
RELATIVE_TEN_TEXT = "10.00mm"
DEFAULT_DISTANCE = "0.00"

# X+, X-, Y+, Y-, Z+, or Z-
X_PLUS = "X+"
X_MINUS = "X-"
Y_PLUS = "Y+"
Y_MINUS = "Y-"
Z_PLUS = "Z+"
Z_MINUS = "Z-"
# WINDOW_GUI_TIMEOUT
WINDOW_GUI_TIMEOUT = 10 # in ms
# TODO: Put in Constants for GCODE Input

# --- Z Stack Constants ----
# INPUT Z STACK PARAMETERS Keys
Z_START_KEY = "-Z_START_KEY-"
Z_END_KEY = "-Z_END_KEY-"
Z_INC_KEY = "-Z_INC_KEY-"

SAVE_FOLDER_KEY = "-SAVE_FOLDER_KEY-"

# Button Text
START_Z_STACK_CREATION_TEXT = "Start Z Stack Creation"


# --- Save a Location Constants ---
SAVE_LOC_BUTTON = "Save Loc Button"

# Create Temp file to store locations into
TEMP_FOLDER = r"/home/pi/Projects/3dprinter_sampling/temp"
TEMP_FILE = r"temp_loc.csv"
TEMP_FULL_PATH = os.path.join(TEMP_FOLDER, TEMP_FILE)

# --- Camera Preview Settings ---
# GUI KEYS
PREVIEW_LOC_X_KEY = "-PREVIEW LOC X KEY-"
PREVIEW_LOC_Y_KEY = "-PREVIEW LOC Y KEY-"
PREVIEW_WIDTH_KEY = "-PREVIEW WIDTH KEY-"
PREVIEW_HEIGHT_KEY = "-PREVIEW HEIGHT KEY-"
ALPHA_KEY = "-ALPHA KEY-"
PREVIEW_KEY_LIST = [PREVIEW_LOC_X_KEY, PREVIEW_LOC_Y_KEY, PREVIEW_WIDTH_KEY, PREVIEW_HEIGHT_KEY, ALPHA_KEY]

# Button Text
START_PREVIEW = "Start Preview"
STOP_PREVIEW = "Stop Preview"

PREVIEW_LOC_X = 0
PREVIEW_LOC_Y = 0
PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
PREVIEW_ALPHA = 255
# Opacity, or Alpha (range 0 (invisible) to 255 (opaque))

PREVIOUS_CAMERA_PREVIEW_X = 0
PREVIOUS_CAMERA_PREVIEW_Y = 0

# Displace Pseudo Window to make it easier to grab/see (in pixels?)
PREVIEW_WINDOW_OFFSET = 30

# Xlib Constants
# Default Screen Index, 0 here.
# Assumes one monitor is connected to Raspberry Pi
DEFAULT_SCREEN_INDEX = 0

# EXPOSURE MODE CONSTANTS
EXPOSURE_MODE = "auto"
# Possible modes: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, fireworks
EXPOSURE_MODE_KEY = "-EXPOSURE MODE-"
EXPO_SETTLE_TIME = 2 # in seconds
EXPO_SETTLE_TIME_KEY = "-EXPO SETTLE TIME-"
SET_EXPOSURE_MODE = "Set Expo"

is_running_experiment = False

# ==== USER DEFINED FUNCTIONS =====

# Define function, run_relative(direction, values)
def run_relative(direction, values):
    # Converts input buttons (direction) into GCODE String,
    #  then calls run_gcode from printer module (not implemented in this demo)
    # Inputs: takes string direction (X+, X-, Y+, Y-, Z+, or Z-)
    #         values from window.read()

    # For debugging, uncomment to see if the direction (event) and values are being passed correctly
    # print("direction:", direction)
    # print("values:", values)

    # Initialize move_amount to 0.00
    move_amount = DEFAULT_DISTANCE

    # Initialize relative_coordinates variable to direction and 0.00 (example: G0X0.00, no movements)
    relative_coordinates = "{}{}".format(direction, move_amount)

    # For debugging, uncomment to see if the formatting matches the example
    # print("relative_coordinates:", relative_coordinates)

    # For debugging, uncomment to see the move_amount before the if/elif chain
    # print("move_amount (before):", move_amount)

    # Use if/elif chain to check which radio button is true (0.1, 1, or 10)
    # If values[-REL_TENTH-] == True
    #  Example If 0.1 true, change relative coordinates to X-0.10
    # else if the values of relative one is True
    #  Make movement amount into 1.00
    # else if the values of relative ten is True
    #  Make movement amount into 1.00
    if values[RELATIVE_TENTH_KEY] == True:
        # print(RELATIVE_TENTH_KEY, "is active")
        # Extract only the float number, ignoring the "mm"
        move_amount = RELATIVE_TENTH_TEXT[0:-2]
    elif values[RELATIVE_ONE_KEY] == True:
        # print(RELATIVE_ONE_KEY, "is active")
        move_amount = RELATIVE_ONE_TEXT[0:-2]
    elif values[RELATIVE_TEN_KEY] == True:
        # print(RELATIVE_TEN_KEY, "is active")
        move_amount = RELATIVE_TEN_TEXT[0:-2]

    # For debugging, uncomment to see the move_amount after the if/elif chain. Did it change?
    # print("move_amount (after):", move_amount)

    #  Use string formatting to create GCode string (example: G0X-1.00)
    relative_coordinates = "G0{}{}".format(direction, move_amount)

    print("relative_coordinates:", relative_coordinates)

    # This is where you would run the GCode
    # Run Relative Mode
    printer.run_gcode("G91")
            
    # Run relative_coordinates GCODE created in this function
    printer.run_gcode(relative_coordinates)
#   TODO: Extruder Speed Adjustment


# define get_current_location_manager()
# print("===================================")
# print("You pressed Get Current Location!")
# printer.run_gcode("M114")
# serial_string = printer.get_serial_data()
# if GCL.does_location_exist_m114(serial_string) == True:
    # current_location_dictionary, is_location_found = GCL.parse_m114(serial_string)
    # print(current_location_dictionary)
    # printer.printer.flush()
# else:
    # print("Location Not Found, Try Again")
    # printer.printer.flush()
# TODO: Test out flush, then M114, will this prevent having to do it twice?
#       Update: No, it doesn't help.
# Algorithm:
#  Flush, run M114, set serial data, check, make it run twice
#   if location not found, run again?

# TODO: Include picamera settings

# Thread version
# Define function start_experiment(event, values)
def run_experiment(event, values, thread_event, camera, preview_win_id):
    """
    Description: Runs experiment to take a picture, video, or preview (do nothing)
    
    Input: PySimpleGUI window event and values
    """
    # global camera
    print("run_experiment")
    
    if camera.preview:
        camera.stop_preview()
        
    
    
    # Get CSV Filename
    csv_filename = values[OPEN_CSV_FILEBROWSE_KEY]
    
    # Get Path List from CSV
    path_list = P.get_path_list_csv(csv_filename)
    
    # Get GCODE Location List from path_list
    gcode_string_list = P.convert_list_to_gcode_strings(path_list)
    
    # Go into Absolute Positioning Mode
    printer.run_gcode(C.ABSOLUTE_POS)
    
    # Create New Folder If not in "Preview" Mode
    if values[EXP_RADIO_PREVIEW_KEY] == False:
        folder_path = P.create_and_get_folder_path()
        print("Not in Preview Mode, creating folder:", folder_path)
        
    # Get Camera Settings Module
    # Initialize unique CSV camera settings file
    GCS.SAVE_CSV_FOLDER = folder_path
    GCS.init_csv_file()
    
    # Create While loop to check if thread_event is not set (closing)
    count_run = 0
    # while not thread_event.isSet():
    # while True:
    while is_running_experiment:
        
        # TODO: Put in the rest of the code for Pic, Video, Preview from 3dprinter_start_experiment or prepare_experiment
        print("=========================")
        print("Run #", count_run)
        
        well_number = 1
        for location in gcode_string_list:
            # print(gcode_string)
            printer.run_gcode(location)
            print("Going to Well Number:", well_number)
            time.sleep(4)
            if values[EXP_RADIO_PREVIEW_KEY] == True:
                print("Preview Mode is On, only showing preview camera \n")
                # camera.start_preview(fullscreen=False, window=(30, 30, 500, 500))
                # time.sleep(5)
                
                # camera.stop_preview()
            elif values[EXP_RADIO_VID_KEY] == True:
                print("Recording Video Footage")
                file_full_path = P.get_file_full_path(folder_path, well_number)
                # TODO: Change to Video Captures
                # camera.capture(file_full_path)
            elif values[EXP_RADIO_PIC_KEY] == True:
                print("Taking Pictures Only")
                file_full_path = P.get_file_full_path(folder_path, well_number)
                # print(file_full_path)
                
                # Change Image Capture Resolution
                # pic_width = PIC_WIDTH
                # pic_height = PIC_HEIGHT
                
                #camera.stop_preview()
                #camera.resolution = (pic_width, pic_height)
                # time.sleep(.1)
                #camera.capture(file_full_path)
                # camera.start_preview()
                #start_camera_preview(event, values, camera, preview_win_id)
                
                
                get_well_picture(camera, file_full_path)
                
                data_row = GCS.gen_cam_data(file_full_path, camera)
                GCS.append_to_csv_file(data_row)
                
                # Return to streaming resolution: 640 x 480 (or it will crash)
                # Bug: Crashes anyway because of threading
                #camera.resolution = (VID_WIDTH, VID_HEIGHT)
                # TODO: Look up Camera settings to remove white balance (to deal with increasing brightness)
            # May implement the following to break out of loop first. Helpful for lots of wells
            """    
            if is_running_experiment == False:
                print("Stopping Experiment...")
                return
            """
            well_number += 1
        
        count_run += 1
        
        # Use For Loop to go through each location
        # TODO: Preview doesn't show preview camera
        # Original
        # for location in gcode_string_list:
            # # print(location)
            # printer.run_gcode(location)
            # time.sleep(5)
        
        
    print("=========================")
    print("Experiment Stopped")
    print("=========================")


def run_experiment2(event, values, thread_event, camera, preview_win_id):
    """
    Description: Runs experiment to take a picture, video, or preview (do nothing)
    
    Input: PySimpleGUI window event and values
    """
    # global camera
    global is_running_experiment
    print("run_experiment with timer")
    
    if camera.preview:
        camera.stop_preview()
    
    # Get Timer Values
    total_seconds, run_seconds = ET.get_hour_min(event, values)
    
    # Dummy Data for faster code testing, delete when ready
    # total_seconds = 40
    # run_seconds = 10
        
    start_time = time.monotonic()
    
    elapsed_seconds = -1
    
    run_start = time.monotonic()
    run_time_left = 0
    run_elapsed = -1
    
    # Get CSV Filename
    csv_filename = values[OPEN_CSV_FILEBROWSE_KEY]
    
    # Get Path List from CSV
    path_list = P.get_path_list_csv(csv_filename)
    
    # Get GCODE Location List from path_list
    gcode_string_list = P.convert_list_to_gcode_strings(path_list)
    
    # Go into Absolute Positioning Mode
    printer.run_gcode(C.ABSOLUTE_POS)
    
    # Create New Folder If not in "Preview" Mode
    if values[EXP_RADIO_PREVIEW_KEY] == False:
        dest_folder = PIC_SAVE_FOLDER
        # folder_path = P.create_and_get_folder_path(dest_folder)
        folder_path = P.create_and_get_folder_path2(dest_folder)
        print("Not in Preview Mode, creating folder:", folder_path)
        
    # Get Camera Settings Module
    # Initialize unique CSV camera settings file
    GCS.SAVE_CSV_FOLDER = folder_path
    GCS.init_csv_file()
    
    # Create While loop to check if thread_event is not set (closing)
    count_run = 0
    # while not thread_event.isSet():
    # while True:
    while is_running_experiment:
        
        # TODO: Put in the rest of the code for Pic, Video, Preview from 3dprinter_start_experiment or prepare_experiment
        
        
        
        
        if run_time_left <= 0:
            print("=========================")
            print("Run #", count_run)
            well_number = 1
            
            for location in gcode_string_list:
                # print(gcode_string)
                printer.run_gcode(location)
                print("Going to Well Number:", well_number)
                time.sleep(4)
                if values[EXP_RADIO_PREVIEW_KEY] == True:
                    print("Preview Mode is On, only showing preview camera \n")
                    # camera.start_preview(fullscreen=False, window=(30, 30, 500, 500))
                    # time.sleep(5)
                    
                    # camera.stop_preview()
                elif values[EXP_RADIO_VID_KEY] == True:
                    print("Recording Video Footage")
                    file_full_path = P.get_file_full_path(folder_path, well_number)
                    # TODO: Change to Video Captures
                    # camera.capture(file_full_path)
                elif values[EXP_RADIO_PIC_KEY] == True:
                    print("Taking Pictures Only")
                    file_full_path = P.get_file_full_path(folder_path, well_number)
                    # print(file_full_path)
                    
                    # Change Image Capture Resolution
                    # pic_width = PIC_WIDTH
                    # pic_height = PIC_HEIGHT
                    
                    #camera.stop_preview()
                    #camera.resolution = (pic_width, pic_height)
                    # time.sleep(.1)
                    #camera.capture(file_full_path)
                    # camera.start_preview()
                    #start_camera_preview(event, values, camera, preview_win_id)
                    
                    
                    get_well_picture(camera, file_full_path)
                    
                    data_row = GCS.gen_cam_data(file_full_path, camera)
                    GCS.append_to_csv_file(data_row)
                    
                    # Return to streaming resolution: 640 x 480 (or it will crash)
                    # Bug: Crashes anyway because of threading
                    #camera.resolution = (VID_WIDTH, VID_HEIGHT)
                    # TODO: Look up Camera settings to remove white balance (to deal with increasing brightness)
                # Outside if/elif chain
                well_number += 1
            # Outside of location for loop
            count_run += 1
            # Reset run_time_left
            run_time_left = run_seconds

            # Reset run_start
            run_start = time.monotonic()

            print(f"Will wait {run_seconds} sec before doing next run.")

            # Display time left until end of experiment
            print(f"Time left until end of experiment: {(total_seconds - elapsed_seconds):.1f} sec")
            # May implement the following to break out of loop first. Helpful for lots of wells
            """    
            if is_running_experiment == False:
                print("Stopping Experiment...")
                return
            """
            
        # Out of if run_time < 0 statement
        
        
        current_time = time.monotonic()
        elapsed_seconds = current_time - start_time
        
        run_elapsed = current_time - run_start
        run_time_left = run_seconds - run_elapsed
        
        # if elapsed_seconds + run_seconds < total_seconds:
            # print(f"Will wait {run_seconds} seconds until collecting data again")
            # time.sleep(run_seconds)
        if elapsed_seconds + run_seconds > total_seconds:
            print(f"Doing another run will go over set time limit, stopping experiment.")
            is_running_experiment = False
            break
        
        
        # Use For Loop to go through each location
        # TODO: Preview doesn't show preview camera
        # Original
        # for location in gcode_string_list:
            # # print(location)
            # printer.run_gcode(location)
            # time.sleep(5)
        
        
    print("=========================")
    print("Experiment Stopped")
    print("=========================")

# Takes in event and values to check for radio selection (Pictures, Videos, or Preview)
# Takes in CSV filename or location list generated from opening CSV file
#    Use get_path_list_csv(csv_filename) and convert_list_to_gcode_strings(path_list) from prepare_experiment module
# Create section for camera setup (or create another function to set camera settings)
#  Create function to return camera settings to default (for preview?)
# Create section for video camera setup (length of time to record)
# Goes to each location in list and takes picture, video, or nothing
#   Use for loop to go through each location list
#     Use if statement chain for radio buttons
#       If Picture, take picture. If Video, take video. If Preview, only go there.
# TODO: Include input for number of runs or length of time to run? (Use my Arduino strategy, put in the camera for loop
#       Recommend number of runs first, then implement countdown algorithm?
# TODO: Test picture/video capabilities while camera feed is running. Update, picture works


# Non-thread version
def run_experiment_gui(main_values, camera):
    # Inputs: values or csv_filename?
    
    global is_running_experiment
    
    # Get paths from CSV file
    print("run_experiment")
    
    camera.stop_preview()
    
    
    # Get CSV Filename
    csv_filename = main_values[OPEN_CSV_FILEBROWSE_KEY]
    
    # Get Path List from CSV
    path_list = P.get_path_list_csv(csv_filename)
    
    # Get GCODE Location List from path_list
    gcode_string_list = P.convert_list_to_gcode_strings(path_list)
    gcode_string_list_len = len(gcode_string_list)
    print(f"gcode_string_list_len: {gcode_string_list_len}")
    
    # Go into Absolute Positioning Mode
    printer.run_gcode(C.ABSOLUTE_POS)
    
    # Move to first well
    print("Moving to first well and waiting a few seconds")
    printer.run_gcode(gcode_string_list[0])
    
    # Wait to go to well
    time.sleep(2)
    print("Done waiting to go to WELL")
    
    
    # setup_picture_camera_settings(camera)
    # setup_default_camera_settings(camera)
    
    
    # Change camera resolution
    # Sensor resolution (Pi Camera 2, 3280x2464)
    # Change resolution to largest resolution for taking pictures
    # Change Image Capture Resolution
    pic_width = PIC_WIDTH
    pic_height = PIC_HEIGHT

    camera.resolution = (pic_width, pic_height)
    
    # Sleep time for exposure mode
    # time.sleep(expo_wait_time)
    
    
    # Setup separate GUI
    # setup theme
    sg.theme("Light Brown 3")
    
    # setup layout of new GUI (one window with a single button)
    layout_exp = [[sg.Button("Stop Experiment", size=(20,20))]]

    # setup window for new GUI
    window_exp = sg.Window("Experiment GUI Window", layout_exp, finalize=True)
    
    # Create New Folder If not in "Preview" Mode
    if main_values[EXP_RADIO_PREVIEW_KEY] == False:
        folder_path = P.create_and_get_folder_path()
        print("Not in Preview Mode, creating folder:", folder_path)
    
    # Setup how long to wait before moving to next well (and GUI loop)
    time_to_wait = 2000 # in millisec
    
    # Initialize index for going through gcode_string_list
    index = 0
    # ---- EVENT LOOP ----
    while True:
        event, values = window_exp.read(timeout=time_to_wait)
        
        # Run Experiment
        # print(f"Index: {index}")
        # print(gcode_string_list[index])
        
        well_number = index + 1
        print(f"Well Number: {well_number}")
        
        printer.run_gcode(gcode_string_list[index])
        # Wait to go to well
        time.sleep(2)
        
        if main_values[EXP_RADIO_PREVIEW_KEY] == True:
            print("Preview Mode is On, only showing preview camera \n")
            # camera.start_preview(fullscreen=False, window=(30, 30, 500, 500))
            # time.sleep(5)
            
            # camera.stop_preview()
        elif main_values[EXP_RADIO_VID_KEY] == True:
            print("Recording Video Footage")
            file_full_path = P.get_file_full_path(folder_path, well_number)
            # TODO: Change to Video Captures
            # camera.capture(file_full_path)
        elif main_values[EXP_RADIO_PIC_KEY] == True:
            print("Taking Pictures Only")
            file_full_path = P.get_file_full_path(folder_path, well_number)
            # print(file_full_path)
            
            get_well_picture(camera, file_full_path)
            
            # camera.capture(file_full_path)
            # TODO: Look up Camera settings to remove white balance (to deal with increasing brightness)
            time.sleep(2)
            
            
        
        
        # If index is at the end of the list, reset it. else increment it.
        if index == (gcode_string_list_len - 1):
            index = 0
        else:
            index += 1
            
        
        
        if event.startswith("Stop"):
            print("You pressed Stop. Stopping experiment")
            break
    
    window_exp.close()
    
    # Change resolution back to video stream
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    # time.sleep(expo_wait_time)
    
    # setup_default_camera_settings(camera)
    
    is_running_experiment = False

    
    # 
    pass


# Define function get_gcode_string_list(values)

def get_gcode_string_list(values):
    """
    Description: Takes CSV File from values (GUI Data), returns gcode_string_list
    Input: values, a dictionary from PySimpleGUI Window Reads
    Return/Output: GCode String List for well location.
    """
    # Get CSV Filename
    csv_filename = values[OPEN_CSV_FILEBROWSE_KEY]
    
    # Get Path List from CSV
    path_list = P.get_path_list_csv(csv_filename)
    
    # Get GCODE Location List from path_list
    gcode_string_list = P.convert_list_to_gcode_strings(path_list)
    
    # Return gcode_string_list
    
    pass


# Define function, get_sample(folder_path_sample, values)

def get_sample(folder_path_sample, well_number, values):
    """
    Description: Takes Pic/Vid/Preview Radio Values, then takes a
                 picture, video, or preview (do nothing), stores into
                 folder_path_sample
    Inputs:
      - values, a dictionary from PySimpleGUI Window Reads. The main focus are the Radio values for the Pic/Vid/Preview.
      - folder_path_sample, a string holding the unique folder path for the samples (prevents accidental overwrite)
    Return/Output: Doesn't return anything. TODO: Return True/False if failed or successful?
    """
    
    # Create Unique Filename, call get_file_full_path(folder_path, well_number)
    # Check Experiment Radio Buttons
    #  If Picture is True, take a picture. Save with unique filename
    #  If Video is True, take a video. Save with unique filename
    #  If Preview is True, do nothing or print "Preview Mode"
    
    pass


def get_video(camera):
    
    # Create Unique Filename
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d_%H%M%S")
    filename = f"video_{current_time_str}.h264"
    
    # Set Recording Time (in seconds)
    recording_time = int(1 * 5)
    
    camera.start_recording(filename)
    camera.wait_recording(recording_time)
    camera.stop_recording()
    
    print(f"Recorded Video: {filename}")


def get_picture(camera):
    # TODO: Change variables here to Global to match changes in Camera Tab
    # Take a Picture, 12MP: 4056x3040
    pic_width = PIC_WIDTH
    pic_height = PIC_HEIGHT
    unique_id = get_unique_id()
    pic_save_name = f"test_{unique_id}_{pic_width}x{pic_height}.jpg"
    
    camera.resolution = (pic_width, pic_height)
    # camera.resolution = (2592, 1944)
    
    pic_save_full_path = f"{PIC_SAVE_FOLDER}/{pic_save_name}"
    
    camera.capture(pic_save_full_path)
    
    print(f"Saved Image: {pic_save_full_path}")
    
    # Return to streaming resolution: 640 x 480 (or it will crash)
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    pass


def get_well_picture(camera, file_full_path):
    # TODO: Change variables here to Global to match changes in Camera Tab
    # Take a Picture, 12MP: 4056x3040
    pic_width = PIC_WIDTH
    pic_height = PIC_HEIGHT
    # unique_id = get_unique_id()
    # pic_save_name = f"well{well_number}_{unique_id}_{pic_width}x{pic_height}.jpg"
    
    camera.resolution = (pic_width, pic_height)
    # camera.resolution = (2592, 1944)
    
    # pic_save_full_path = f"{PIC_SAVE_FOLDER}/{pic_save_name}"
    
    camera.capture(file_full_path)
    
    print(f"Saved Image: {file_full_path}")
    
    # Return to streaming resolution: 640 x 480 (or it will crash)
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    pass



def get_x_pictures(x, delay_seconds, camera):
    
    # Set Camera Resolution
    pic_width = PIC_WIDTH
    pic_height = PIC_HEIGHT
    camera.resolution = (pic_width, pic_height)
    
    # Stop Preview?
    camera.stop_preview()
    
    # Run loop x times
    for i in range(x):
    
        # Create Unique ID
        unique_id = get_unique_id()
        # Create Save Name from Unique ID
        pic_save_name = f"test_{unique_id}_{pic_width}x{pic_height}.jpg"
        # Create Full Save Path using Save Name and Save Folder
        pic_save_full_path = f"{PIC_SAVE_FOLDER}/{pic_save_name}"
        # Capture Image
        camera.capture(pic_save_full_path)
        # Print that picture was saved
        print(f"Saved Image: {pic_save_full_path}")
        # Wait Delay Amount
        time.sleep(delay_seconds)
    
    print(f"Done taking {x} pictures.")
    # Return Camera Resolution?
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    
    pass

# Define function to create unique text string using date and time.
def get_unique_id():
    current_time = datetime.now()
    unique_id = current_time.strftime("%Y-%m-%d_%H%M%S")
    # print(f"unique_id: {unique_id}")
    return unique_id


# Define function to check an InputText key for digits only
def check_for_digits_in_key(key_str, window, event, values):
    
    if event == key_str and len(values[key_str]) and values[key_str][-1] not in ('0123456789'):
            # delete last char from input
            # print("Found a letter instead of a number")
            window[key_str].update(values[key_str][:-1])


def create_z_stack(z_start, z_end, z_increment, save_folder_location, camera):
    # Assumes all inputs are floating or integers, no letters!
    print("create_z_stack")
    print("Pausing Video Stream")

    # GCODE Position, goes fastest
    position = "G0"

    # Go into Absolute Mode, "G90"
    # Run GCODE to go into Absolute Mode
    printer.run_gcode(C.ABSOLUTE_POS)

    # Will use absolute location mode to go to each z
    # Alternative, you could use relative and get current location to get z value.
    # Test: Use Get Current Location to compare expected vs actual z.

    # Create Unique folder to save into save_folder_location
    save_folder_path = f"{save_folder_location}/z_stack_{get_unique_id()}"
    
    # Check if folder exists, if not, create it
    if not os.path.isdir(save_folder_path):
        print("Folder Does NOT exist! Making New Folder")
        os.mkdir(save_folder_path)
    else:
        print("Folder Exists")
    
    # print(f"save_folder_path: {save_folder_path}")
    
    # Go to first location, wait x seconds?

    # Mark where we think z_focus is?

    for z in np.arange(z_start, z_end+z_increment, z_increment):
        print(f"z: {z}")
        # Make sure number gets rounded to 2 decimal places (ex: 25.23)

        # Round z to 2 decimal places
        z_rounded = round(z, 2)
        # Fill out with zeroes until 5 characters long, example: 1.2 becomes 01.20
        # For easier viewing purposes depending on OS.
        z_rounded_str = f"{z_rounded}".zfill(5) 

        # Convert z to GCODE
        # GCODE Format: G0Z2.34
        gcode_str = f"{position}Z{z_rounded}"

        print(f"gcode_str: {gcode_str}")

        # Go to z location using printer_connection module's run_gcode
        # Possible bug, could this module be used elsewhere? This code may have to run in the same location as the GUI.
        printer.run_gcode(gcode_str)
        # Wait x seconds for extruder to get to location.
        time.sleep(2)


        # Take Picture and save to folder location
        save_file_name = f"_image_{z_rounded_str}_.jpg"
        save_full_path = f"{save_folder_path}/{save_file_name}"
        
        # Change to max resolution
        camera.resolution = PIC_RES
        
        
        camera.capture(save_full_path)
        
        # Change back to streaming resolution
        camera.resolution = VID_RES

    
    print(f"Done Creating Z Stack at {save_folder_path}")

    pass


# Define function to get current location
def get_current_location():
    printer.run_gcode("M114")
    serial_string = printer.get_serial_data()
    if GCL.does_location_exist_m114(serial_string) == True:
        current_location_dictionary, is_location_found = GCL.parse_m114(serial_string)
        print(current_location_dictionary)
        # printer.printer.flush()
    else:
        print("Location Not Found, Try Again")
    pass
    

def get_current_location2():
    print("Getting Current Location...")
    
    # Init result with negative values for error checking
    # If negative value, then location was not found
    result = {"X": -1.00, "Y": -1.00, "Z": -1.00}
    
    # Number of attempts to check for location (how many times to run for loop)
    num_location_checks = 10
    
    # Number of location grabs until that one is accepted (in case of outdated location)
    num_until_location_accepted = 1
    
    # Init location_found_counter (want loc to be found at least once since old one is stored)
    location_found_counter = 0
    
    num_searches = 0
    for i in range(num_location_checks):
        num_searches += 1
        # Uncomment print statement for debugging
        # print(f"Location Search Attempt: {i}")
        # Run M114 GCODE
        printer.run_gcode("M114")
        # Make GUI wait for 3D printer to receive and process command.
        # May need to make this adjustable in the future.
        time.sleep(1)
        serial_string = printer.get_serial_data2()
        if GCL.does_location_exist_m114(serial_string) == True:
            
            current_location_dictionary, is_location_found = GCL.parse_m114(serial_string)
            
            if location_found_counter == 0:
                location_found_counter += 1
                # Uncomment print statement for debugging
                # print("Location Found, but might be outdated. Trying again")
                continue
            elif location_found_counter >= num_until_location_accepted:
                result = current_location_dictionary
                print("Location Found, Stopping Search.")
                break
        else:
            print("Location Not Found, Trying Again...")
            # If location not found, wait a second in case there is a buffer issue?
            # If no data found, get_serial_data2 ran at least 20 times, so used default empty string
            #   Should try again
            """
            print(f"Data Found: {serial_string}")
            if len(serial_string) == 0:
                print("No data found")
            """
            time.sleep(1)
            continue
        
        # Get Serial Data
        # If location exist in serial string, increment location_found_counter by 1, start while loop again
        #   If loc exist and counter is 1, save location
        # If location does not exist, don't increment, start while loop again
    
    print(f"Number of Location Retrieval Attempts: {num_searches}")
    print("**Note: If all coord are -1.00, then location was not found")
    print(f"Location: {result}")
    return result


# Save current location
# Alt: Save to List instead, then have "Save" button?
# Ask user to choose file name and location first?
# Can only save loc if filename is chosen?
def save_current_location():
    print("save_current_location")
    cur_loc_dict = get_current_location2()
    print(f"cur_loc_dict: {cur_loc_dict}")

    # Make newline be blank, prevents extra empty lines from happening
    f = open(TEMP_FULL_PATH, 'a', newline="")
    writer = csv.writer(f)

    # Possible to check for headers row?
    # headers = ["X", "Y", "Z"]
    row = [0]

    for key, value in cur_loc_dict.items():
        print(key, value)
        row.append(value)

    print(row)

    # writer.writerow(headers)
    writer.writerow(row)

    f.close()
    print("File Saved")


# === Start Camera Preview Window Functions ===
def get_max_screen_resolution():
    """
    Gets Max Screen Resolution,
    returns max_screen_width, max_screen_height in pixels
    """
    max_screen_width = 0
    max_screen_height = 0
    
    d = Display()
    
    info = d.screen(DEFAULT_SCREEN_INDEX)
    
    max_screen_width = info.width_in_pixels
    max_screen_height = info.height_in_pixels
    
    # print(f"Width: {max_screen_width}, height: {max_screen_height}")
    """
    for screen in range(0,screen_count):
        info = d.screen(screen)
        print("Screen: %s. Default: %s" % (screen, screen==default_screen))
        print("Width: %s, height: %s" % (info.width_in_pixels,info.height_in_pixels))
    """
    
    d.close()
    
    return max_screen_width, max_screen_height


def get_xy_loc_of_all_windows():
    disp = Display()
    root = disp.screen().root
    children = root.query_tree().children
    
    loc_x_list = []
    loc_y_list = []
    
    for win in children:
        winName = win.get_wm_name()
        pid = win.id
        x, y, width, height = get_absolute_geometry(win, root)
        
        loc_x_list.append(x)
        loc_y_list.append(y)
    
    disp.close()
    
    return loc_x_list, loc_y_list


def get_unique_xy_loc():
    loc_x_list, loc_y_list = get_xy_loc_of_all_windows()
    
    # Get unique values from list only, remove negatives
    x_exclude_list = list(set(loc_x_list))
    y_exclude_list = list(set(loc_y_list))
    
    # print("After Set Stuff")
    # print(f"x_exclude_list: {x_exclude_list}")
    # print(f"y_exclude_list: {y_exclude_list}")
    
    # Random Int selection for x and y, exclude unique values above,
    # max would be max screen resolution
    
    # Get max screen width and height
    max_screen_width, max_screen_height = get_max_screen_resolution()
    
    # Use set subtraction to create list of integers for random choice
    # (is faster than using a for loop to remove numbers)
    
    x_start = random.choice(list(set([x for x in range(0, max_screen_width)]) - set(x_exclude_list)))
    y_start = random.choice(list(set([y for y in range(0, max_screen_height)]) - set(y_exclude_list)))
    # print(f"x_start: {x_start}")
    # print(f"y_start: {y_start}")
    
    return x_start, y_start


def get_window_pid(x_start, y_start):
    print("***get_window_pid()***")
    disp = Display()
    root = disp.screen().root
    children = root.query_tree().children
    
    result_pid = 0
    
    for win in children:
        winName = win.get_wm_name()
        pid = win.id
        x, y, width, height = get_absolute_geometry(win, root)
        
        if x == x_start and y == y_start:
            """
            print("======Children=======")
            print(f"winName: {winName}, pid: {pid}")
            print(f"x:{x}, y:{y}, width:{width}, height:{height}")
            """
            # print(f"wm: {win.get_window_title()}")
            
            # Move Window x = 50, y = 20
            # win.configure(x=x+50)
            # win.configure(x=400, y=36)
            
            # Set Window Name to "Camera Preview Window"
            # win.set_wm_name("Camera Preview Window")
            
            result_pid = pid
            break
    
    disp.close()
    
    return result_pid


def get_window_location_from_pid(search_pid):
    # print("get_window_location_from_pid")
    # print(f"search_pid: {search_pid}")
    
    disp = Display()
    root = disp.screen().root
    children = root.query_tree().children
    
    x_win, y_win = 0, 0
    
    for win in children:
        winName = win.get_wm_name()
        pid = win.id
        x, y, width, height = get_absolute_geometry(win, root)
        
        if pid == search_pid:
            """
            print("======Children=======")
            print(f"winName: {winName}, pid: {pid}")
            print(f"x:{x}, y:{y}, width:{width}, height:{height}")
            """
            
            x_win = x
            y_win = y
            
            break
    
    # print(f"x_win:{x_win}, y_win:{y_win}")
    return x_win, y_win
    disp.close()


def move_window_pid(search_pid, x_new, y_new):
    print("***move_window_pid()***")
    # print(f"search_pid: {search_pid}")
    disp = Display()
    root = disp.screen().root
    children = root.query_tree().children
    
    for win in children:
        winName = win.get_wm_name()
        pid = win.id
        x, y, width, height = get_absolute_geometry(win, root)
        
        if pid == search_pid:
            """
            print("======Children=======")
            print(f"winName: {winName}, pid: {pid}")
            print(f"x:{x}, y:{y}, width:{width}, height:{height}")
            """
            
            print(f"Moving Window Name: {winName}, pid: {pid}")
            win.configure(x=x_new, y=y_new)
            
            break
    
    disp.close()


def change_window_name(search_pid, new_window_name):
    print("***change_window_name()***")
    # Change Window Name of Specific PID
    # print(f"search_pid: {search_pid}")
    disp = Display()
    root = disp.screen().root
    children = root.query_tree().children
    
    for win in children:
        winName = win.get_wm_name()
        pid = win.id
        x, y, width, height = get_absolute_geometry(win, root)
        
        if pid == search_pid:
            """
            print("======Children=======")
            print(f"winName: {winName}, pid: {pid}")
            print(f"x:{x}, y:{y}, width:{width}, height:{height}")
            """
            
            win.set_wm_name(new_window_name)
            
            break
    disp.close()


def get_absolute_geometry(win, root):
    """
    Returns the (x, y, height, width) of a window relative to the
    top-left of the screen.
    """
    geom = win.get_geometry()
    (x, y) = (geom.x, geom.y)
    
    # print("Start")
    # print(f"x: {x}, y: {y}")
    
    while True:
        parent = win.query_tree().parent
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        
        if parent.id == root.id:
            # print("parent id matches root id. Breaking...")
            break
        win = parent
    
    # print("End")
    # print(f"x: {x}, y: {y}")
    return x, y, geom.width, geom.height
# === End Camera Preview Window Functions ===


# === Start Camera Settings Functions ===

def setup_picture_camera_settings(camera):
    print("Setting up picture camera settings")
    
    # Turn Exposure mode back on so camera can adjust to new light
    camera.exposure_mode = "auto"
    
    # Turn off camera led
    camera.led = False
    
    # Camera Framerate
    camera.framerate = 30
    time.sleep(1)
    
    # Setup default resolution
    # Sensor resolution (Pi Camera 2, 3280x2464)
    # width = 640
    # height = 480
    camera.resolution = VID_RES
    
    # ISO: Image Brightness
    # 100-200 (daytime), 400-800 (low light)
    iso_number = 100
    camera.iso = iso_number
    
    time.sleep(10)
    
    # Contrast
    # Takes values between 0-100
    contrast_number = 50
    camera.contrast = contrast_number
    
    # Automatic White Balance
    camera.awb_mode = "off"
    red_gain = 1.5
    blue_gain = 1.8
    camera.awb_gains = (red_gain, blue_gain)
    
    
    
    # Exposure Mode
    # camera.framerate = 30
    # camera.shutter_speed = 33164
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = "off"
    # Must let camera sleep so exposure mode can settle on certain values, else black screen happens
    time.sleep(2)
    print("Done setting picture camera settings")
    

def setup_default_camera_settings(camera):
    print("Setting default camera settings")
    
    # Turn Exposure mode back on so camera can adjust to new light
    camera.exposure_mode = "auto"
    
    # Turn off camera led
    camera.led = False
    
    # Camera Framerate
    camera.framerate = 30
    time.sleep(1)
    
    # Setup default resolution
    # Sensor resolution (Pi Camera 2, 3280x2464)
    width = 640
    height = 480
    camera.resolution = (width, height)
    
    # ISO: Image Brightness
    # 100-200 (daytime), 400-800 (low light)
    iso_number = 100
    camera.iso = iso_number
    
    time.sleep(10)
    
    # Contrast
    # Takes values between 0-100
    contrast_number = 50
    camera.contrast = contrast_number
    
    # Automatic White Balance
    camera.awb_mode = "off"
    red_gain = 1.5
    blue_gain = 1.8
    camera.awb_gains = (red_gain, blue_gain)
    
    
    
    # Exposure Mode
    # camera.framerate = 30
    # camera.shutter_speed = 33164
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = "off"
    # Must let camera sleep so exposure mode can settle on certain values, else black screen happens
    time.sleep(2)
    
    print("Done setting default camera settings")
    
    pass


def set_exposure_mode(event, values, window, camera):
    
    # Extract Values
    
    expo_mode = values[EXPOSURE_MODE_KEY]
    print(f"expo_mode: {expo_mode}")
    settle_time = int(values[EXPO_SETTLE_TIME_KEY])
    print(f"settle_time: {settle_time}")
    
    # Turn Exposure mode back on so camera can adjust to new light
    camera.exposure_mode = "auto"
    camera.awb_mode = 'auto'
    
    # Set ISO to desired value
    camera.iso = 400
    
    # Wait for Automatic Gain Control to settle
    time.sleep(settle_time)
    
    # Now fix the values
    
    # Exposure Mode
    # camera.framerate = 30
    # camera.shutter_speed = 30901
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    # Must let camera sleep so exposure mode can settle on certain values, else black screen happens
    # time.sleep(settle_time)
    
    
    pass

def set_white_balance(camera, red_gain=1.5, blue_gain=1.8, isAutoWhiteBalanceOn=False):
    # Automatic White Balance
    camera.awb_mode = "off"
    red_gain = 1.5
    blue_gain = 1.8
    camera.awb_gains = (red_gain, blue_gain)
    pass
# === End Camera Settings Functions ===


def start_camera_preview(event, values, camera, preview_win_id):
    print("Starting Preview With Settings")
    if camera.preview:
        camera.stop_preview()
    prev_width = int(values[PREVIEW_WIDTH_KEY])
    prev_height = int(values[PREVIEW_HEIGHT_KEY])
    prev_loc_x = int(values[PREVIEW_LOC_X_KEY])
    prev_loc_y = int(values[PREVIEW_LOC_Y_KEY])
    alpha_val = int(values[ALPHA_KEY])
    
    # Update Global Variables so Pseudo Window has Control
    PREVIEW_LOC_X = prev_loc_x
    PREVIEW_LOC_Y = prev_loc_y
    PREVIEW_WIDTH = prev_width
    PREVIEW_HEIGHT = prev_height
    PREVIEW_ALPHA = alpha_val
    
    # Move Pseudo Window to input location too
    move_window_pid(preview_win_id, prev_loc_x, prev_loc_y - PREVIEW_WINDOW_OFFSET)
    
    camera.start_preview(alpha=alpha_val, fullscreen=False, window=(prev_loc_x, prev_loc_y, prev_width, prev_height))
    
    x_win, y_win = get_window_location_from_pid(preview_win_id)
    print(f"x_win:{x_win}, y_win:{y_win}")


# define main function
def main():
    
    # Temporary Solution: Make pic res/save globally accessible for modification
    global PIC_WIDTH, PIC_HEIGHT, PIC_SAVE_FOLDER, is_running_experiment

    # Setup Camera
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    camera.framerate = 32
    # MHT: 270
    # camera.rotation = 270

    # Cell Sensor, at home, 90
    # camera.rotation = 90
    
    # MHT: 270, Cell Sensor: 90
    # camera.rotation = C.CAMERA_ROTATION_ANGLE
    # Lab stuff
    camera.rotation = 270
    
    # Set Camera Settings:
    # Set Exposure mode
    # camera.exposure_mode = 'fireworks'
    
    # Set AWB Mode
    # camera.awb_mode = 'tungsten'
    
    # Let Camera Settings Settle:
    pre_value = camera.digital_gain
    cur_value = -1
    # for i in range(20):
    # Wait for digital gain values to settle, then break out of loop
    while pre_value != cur_value:
        pre_value = cur_value
        # pre gets cur 
        # cur get new
        
        cur_value = camera.digital_gain
        #if pre_value != cur_value:
        #    pre_value = cur_value
        
        print(f"digital_gain: {cur_value}")
        time.sleep(0.5)
    
    
    # rawCapture = PiRGBArray(camera, size=(VID_WIDTH, VID_HEIGHT))
    
    #
    # allow the camera to warmup
    time.sleep(0.1)
    
    # Setup 3D Printer
    csv_filename = "testing/file2.csv"
    path_list = printer.get_path_list_csv(csv_filename)
    printer.initial_setup(path_list)
    
    
    # Move Extruder Out Of The Way
    x_start = 0
    y_start = C.Y_MAX
    z_start = 50
    # printer.move_extruder_out_of_the_way(x_start, y_start, z_start)
    
    # Create Temp file to store locations into

    if not os.path.isdir(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)
        print(f"Folder does not exist, making directory: {TEMP_FOLDER}")

    # Make newline be blank, prevents extra empty lines from happening
    f = open(TEMP_FULL_PATH, 'w', newline="")
    writer = csv.writer(f)

    # Create headers
    headers = ["X", "Y", "Z"]
    writer.writerow(headers)
    f.close()
    
    # === Camera Preview Startup ===
    global PREVIOUS_CAMERA_PREVIEW_X, PREVIOUS_CAMERA_PREVIEW_Y
    global PREVIEW_LOC_X, PREVIEW_LOC_Y, PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_ALPHA
    # Initialize preview_win_id to store it when GUI is up.
    preview_win_id = 0
    
    # Initialize is_initial_startup flag as True
    is_initial_startup = True
    
    # Preview Window Creation and Tracking
    # Get random/unique x/y window starting position (top-left)
    # loc_x_list, loc_y_list = get_xy_loc_of_all_windows()
    x_start, y_start = get_unique_xy_loc()
    print(f"x_start: {x_start}")
    print(f"y_start: {y_start}")
    # ===  
    
    sg.theme("LightGreen")

    # Create tabs layout:
    # Tab 1: Start Experiment (Pic, vid, or Preview), Open CSV File. Disable Start Experiment if no CSV loaded
    # Tab 2: Movement Tab, with input GCODE (temp), Future: Move specific coordinates
    #
    
    # Tab 1: Start Experiment Tab
    # TODO: Create 3 Radio Buttons for Picture, Video, Preview (Default), and Prompt "Choose to take Pictures, Video, or only preview locations"
    # TODO: Create User Input for number of Trials (use placeholder)
    time_layout = ET.get_time_layout()
    tab_1_layout = [ [sg.Text(OPEN_CSV_PROMPT), sg.Input(), sg.FileBrowse(key=OPEN_CSV_FILEBROWSE_KEY)],
                     time_layout[0], time_layout[1], time_layout[2], time_layout[3], time_layout[4],
                     [sg.Text(EXP_RADIO_PROMPT)],
                     [sg.Radio(EXP_RADIO_PIC_TEXT, EXP_RADIO_GROUP, default=False, key=EXP_RADIO_PIC_KEY),
                        sg.Radio(EXP_RADIO_VID_TEXT, EXP_RADIO_GROUP, default=False, key=EXP_RADIO_VID_KEY),
                        sg.Radio(EXP_RADIO_PREVIEW_TEXT, EXP_RADIO_GROUP, default=True, key=EXP_RADIO_PREVIEW_KEY)],
                     [sg.Button(START_EXPERIMENT, disabled=True), sg.Button(STOP_EXPERIMENT, disabled=True)]
                   ]
    
    # Tab 2: Movement Tab
    tab_2_layout = [ [sg.Text("", size=(3, 1)), sg.Button("Get Current Location", size=(20, 1)), sg.Button(SAVE_LOC_BUTTON)],
                     [sg.Radio(RELATIVE_TENTH_TEXT, RADIO_GROUP, default=False, key=RELATIVE_TENTH_KEY),
                        sg.Radio(RELATIVE_ONE_TEXT, RADIO_GROUP, default=True, key=RELATIVE_ONE_KEY),
                        sg.Radio(RELATIVE_TEN_TEXT, RADIO_GROUP, default=False, key=RELATIVE_TEN_KEY)
                     ],
                     [sg.Text("", size=(5, 1)), sg.Button(Y_PLUS, size=(10, 1)), sg.Text("", size=(5, 1)), sg.Button(Z_MINUS, size=(5, 1))],
                     [sg.Button(X_MINUS, size=(10, 1)), sg.Button(X_PLUS, size=(10, 1))],
                     [sg.Text("", size=(5, 1)), sg.Button(Y_MINUS, size=(10, 1)), sg.Text("", size=(5, 1)), sg.Button(Z_PLUS, size=(5, 1))],
                     [sg.HorizontalSeparator()],
                     [sg.Text("Input GCODE (e.g. G0X0Y50):")],
                     [sg.InputText(size=(30, 1), key="-GCODE_INPUT-"), sg.Button("Run", size=(5, 1)), sg.Button("Clear", size=(5, 1))]
                   ]
    
    # Setup Tab/GUI Layout
    # Camera Rotation: []
    # Set Still Picture Resolution (Actually changes the constant variables)
    # Width
    # Height
    # Set Camera Settings Button
    # TODO: Change default Camera Rotation to settings file if it exists.
    tab_3_layout = [ [sg.Text("Camera Rotation (in Degrees):"), sg.InputText("270", size=(10, 1), enable_events=True, key=CAMERA_ROTATION_KEY)],
                     [sg.Text("Set Image Capture Resolution:")],
                     [sg.Text("Pic Width (in pixels):"), sg.InputText(PIC_WIDTH, size=(10, 1), enable_events=True, key=PIC_WIDTH_KEY)],
                     [sg.Text("Pic Height (in pixels):"),sg.InputText(PIC_HEIGHT, size=(10, 1), enable_events=True, key=PIC_HEIGHT_KEY)],
                     [sg.Button(UPDATE_CAMERA_TEXT)],
                     [sg.Text("Save Images to Folder:"), sg.In(size=(25,1), enable_events=True, key=PIC_SAVE_FOLDER_KEY), sg.FolderBrowse()],
                     [sg.Text("Exposure Mode:"),sg.InputText(EXPOSURE_MODE, size=(10, 1), enable_events=True, key=EXPOSURE_MODE_KEY),
                      sg.Text("Expo Settle Time (in sec):"), sg.InputText(EXPO_SETTLE_TIME, size=(5, 1),key=EXPO_SETTLE_TIME_KEY), sg.Button(SET_EXPOSURE_MODE)]
                   ]
    
    # Z Stack Tab
    tab_4_layout = [ [sg.Text("Input Z Stack Parameters (Units are in mm):")],
                       [sg.Text("Z Start:"), sg.InputText("0", size=(7, 1), enable_events=True, key=Z_START_KEY),
                        sg.Text("Z End:"),sg.InputText("2", size=(7, 1), enable_events=True, key=Z_END_KEY),
                        sg.Text("Z Inc:"),sg.InputText("0.5", size=(7, 1), enable_events=True, key=Z_INC_KEY)],
                       [sg.Text("Save Folder Location:"), sg.In(size=(25,1), enable_events=True, key=SAVE_FOLDER_KEY), sg.FolderBrowse()],
                       [sg.Button(START_Z_STACK_CREATION_TEXT)]
                   ]
    
    # Camera Preview Tab
    tab_5_layout = [ [sg.Text("Preview Location (e.g. x = 0, y = 0):")],
                     [sg.Text("x:"), sg.InputText("0", size=(8, 1), enable_events=True, key=PREVIEW_LOC_X_KEY),
                      sg.Text("y:"), sg.InputText("36", size=(8, 1), enable_events=True, key=PREVIEW_LOC_Y_KEY)],
                     [sg.Text("Preview Video Size (e.g. width = 640, height = 480):")],
                     [sg.Text("width:"), sg.InputText("640", size=(8, 1), enable_events=True, key=PREVIEW_WIDTH_KEY),
                      sg.Text("height:"), sg.InputText("480", size=(8, 1), enable_events=True, key=PREVIEW_HEIGHT_KEY)],
                     [sg.Text("Opacity, or Alpha (range 0 (invisible) to 255 (opaque)):"), sg.InputText("255", size=(5, 1), enable_events=True, key=ALPHA_KEY)],
                     [sg.Button(START_PREVIEW), sg.Button(STOP_PREVIEW)]
                   ]
    
    tab_6_layout = WL.get_cross_hair_layout()
    
    # TABs Layout (New, Experimental
    # TODO: Put in Pic/Video Button, test them out.
    layout = [ [sg.Image(filename='', key='-IMAGE-')],
               [sg.TabGroup([[sg.Tab("Tab 1 (Exp)", tab_1_layout, key="-TAB_1_KEY"),
                              sg.Tab("Tab 2 (Mvmt)", tab_2_layout),
                              sg.Tab("Tab 3 (CAM)", tab_3_layout),
                              sg.Tab("Tab 4 (Z Stack)", tab_4_layout),
                              sg.Tab("Tab 5 (Camera Preview)", tab_5_layout),
                              sg.Tab("Tab 6 (Loc Helper)", tab_6_layout)]])
               ],
               [sg.Button("Pic"), sg.Button("Vid"), sg.Button("Pic x 10")]
             ]
    
    # Setup Camera Preview Pseudo Window
    layout_p = [[sg.Text("Preview Window. Click and Drag me around to move window!", size=(55, 10))]]
    window_p = sg.Window("Camera Preview Pseudo Window", layout_p, grab_anywhere=True, location=(x_start, y_start))
    
    # Define Window Layout (Original)
    # layout = [
        # [sg.Image(filename='', key='-IMAGE-')],
        # [sg.Text("", size=(3, 1)), sg.Button("Get Current Location", size=(20, 1))],
        # [sg.Radio(RELATIVE_TENTH_TEXT, RADIO_GROUP, default=False, key=RELATIVE_TENTH_KEY),
            # sg.Radio(RELATIVE_ONE_TEXT, RADIO_GROUP, default=True, key=RELATIVE_ONE_KEY),
            # sg.Radio(RELATIVE_TEN_TEXT, RADIO_GROUP, default=False, key=RELATIVE_TEN_KEY)],
        # [sg.Text("", size=(5, 1)), sg.Button(Y_PLUS, size=(10, 1)), sg.Text("", size=(5, 1)), sg.Button(Z_MINUS, size=(5, 1))],
        # [sg.Button(X_MINUS, size=(10, 1)), sg.Button(X_PLUS, size=(10, 1))],
        # [sg.Text("", size=(5, 1)), sg.Button(Y_MINUS, size=(10, 1)), sg.Text("", size=(5, 1)), sg.Button(Z_PLUS, size=(5, 1))],
        # [sg.HorizontalSeparator()],
        # [sg.Text("Input GCODE (e.g. G0X0Y50):")],
        # [sg.InputText(size=(30, 1), key="-GCODE_INPUT-"), sg.Button("Run", size=(5, 1)), sg.Button("Clear", size=(5, 1))]
    # ]
    # Have Camera Feed Window
    # To the right, xy, and z
    # Below camera Feed: Show Current Location, Get Current Location Button
    
    # Threading Setup
    # Initialize empty experiment_thread object, will be used with "Start Experiment" is pushed
    experiment_thread = threading.Thread()
    
    # Initialize threading event (Allows you to stop the thread)
    thread_event = threading.Event()
    

    # Create window and show it without plot
    window = sg.Window("3D Printer GUI Test", layout, location=(640, 36))
    
    
    # Create experiment_run_counter
    experiment_run_counter = 0
    # Create Boolean is_running_experiment, default False
    is_running_experiment = False
    # Initialize well_counter to 0 (used for running experiment, going through GCode location list)
    
    # Initialize current_location_dictionary to X=0, Y=0, Z=0
    
    # Initialize folder_path_sample to "" ("Start Experiment" will create unique folder name)
    # **** Note: This for loop may cause problems if the camera feed dies, it will close everything? ****
    # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    while True:
        event, values = window.read(timeout=0)
        event_p, values_p = window_p.read(timeout=0)
        
        # Camera Preview Initial Startup
        # Setup if/else initial_startup condition
        # If initial startup,
        if is_initial_startup == True:
            # print(f"is_initial_startup: {is_initial_startup}")
            # Get PID of Preview Window
            preview_win_id = get_window_pid(x_start, y_start)
            
            # Change Camera Preview Window Name
            new_window_name = "Camera Preview Window"
            change_window_name(preview_win_id, new_window_name)
            # Move This Window to where I want it (0,0)?
            x_new = 0
            y_new = 36
            move_window_pid(preview_win_id, x_new, y_new)
            
            # Start Camera Too PREVIEW_LOC_X, PREVIEW_LOC_Y, PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_ALPHA
            camera.start_preview(alpha=PREVIEW_ALPHA, fullscreen=False, window=(PREVIEW_LOC_X, y_new + PREVIEW_WINDOW_OFFSET, PREVIEW_WIDTH, PREVIEW_HEIGHT))
            
            # Change is_initial_startup to False
            is_initial_startup = False
        else:
            # print(f"is_initial_startup: {is_initial_startup}")
            # get location of Preview Window using PID
            x_win_preview, y_win_preview = get_window_location_from_pid(preview_win_id)
            # print(f"x_win_preview:{x_win_preview}, y_win_preview:{y_win_preview}")
            # camera.start_preview(alpha=255, fullscreen=False, window=(x_win_preview, y_win_preview, 640, 480))
            
            # If previous camera preview x/y is different, update them and call camera.start_preview
            # (Prevents flickering if camera is still)
            # TODO: How to slow down flickering while moving preview window?
            if PREVIOUS_CAMERA_PREVIEW_X != x_win_preview and PREVIOUS_CAMERA_PREVIEW_Y != y_win_preview:
                PREVIOUS_CAMERA_PREVIEW_X = x_win_preview
                PREVIOUS_CAMERA_PREVIEW_Y = y_win_preview
            
                if camera.preview:
                    camera.start_preview(alpha=PREVIEW_ALPHA, fullscreen=False, window=(x_win_preview, y_win_preview + PREVIEW_WINDOW_OFFSET, PREVIEW_WIDTH, PREVIEW_HEIGHT))
        
        # Check Input Text for integers only
        
        for preview_key in PREVIEW_KEY_LIST:
            check_for_digits_in_key(preview_key, window, event, values)
        
        # Call Get Current Location Manager Function
        # Print Current Location
        
        # TODO: Create new thread for Current Location display?
        
        # Convert captured frame to array format, then overwrite frame variable (temporary solution)
        # frame = frame.array
        
        # If in experiment mode, resize image if it is larger than when rawCapture was created
        # if is_running_experiment == True:
            # Resize frame to size of window, maybe
            # rawCapture = PiRGBArray(camera, size=(VID_WIDTH, VID_HEIGHT))
            # frame = cv2.resize(frame, (VID_WIDTH, VID_HEIGHT))
        
        # TODO: Add in image resizer if in experiment mode. Temp fix to allow for max image resolution while running experiment.
        
        # ---- CSV File Checker and "Start Experiment" Enable/Disable If/Else logic
        # Check if CSV file Exists (length is 0 if CSV not loaded)
        #  Enable "Start Experiment" if true, else disable "Start Experiment"
        if len(values[OPEN_CSV_FILEBROWSE_KEY]) != 0 and is_running_experiment == False:
            # print("CSV File Exists")
            # Enable "Start Experiment" button
            window[START_EXPERIMENT].update(disabled=False)
            # print("values[OPEN_CSV_FILEBROWSE_KEY]:", values[OPEN_CSV_FILEBROWSE_KEY])
            # print(len(values[OPEN_CSV_FILEBROWSE_KEY]))
            # Disable "Stop Experiment" button
            window[STOP_EXPERIMENT].update(disabled=True)
        else:
            # print("CSV File Does Not Exist")
            # Disable "Start Experiment" button
            window[START_EXPERIMENT].update(disabled=True)
        
        # ---- Main GUI Window If/elif chain ----
        if event == sg.WIN_CLOSED:
            break
        # Tab 1 (Experiment):
        elif event == START_EXPERIMENT:
            print("You pressed Start Experiment")
            
            # Set is_running_experiment to True, we are now running an experiment
            is_running_experiment = True
            
            # Uncomment to see your CSV File (is it the correct path?)
            # print("CSV File:", values[OPEN_CSV_FILEBROWSE_KEY])
            
            # Disable "Start Experiment" Button
            window[START_EXPERIMENT].update(disabled=True)
            # Enable "Stop Experiment" Button
            window[STOP_EXPERIMENT].update(disabled=False)
            
            # Create actual experiment_thread
            experiment_thread = threading.Thread(target=run_experiment2, args=(event, values, thread_event, camera, preview_win_id), daemon=True)
            experiment_thread.start()
            
            # Create Unique Folder, Get that Unique Folder's Name
            
            # Non-Thread Version of Running Experiment
            # run_experiment_gui(values, camera)
            
        elif event == STOP_EXPERIMENT:
            print("You pressed Stop Experiment")
            print("Ending experiment after current run")
            experiment_run_counter = 0
            is_running_experiment = False
            # Enable "Start Experiment" Button
            window[START_EXPERIMENT].update(disabled=False)
            # Disable "Stop Experiment" Button
            window[STOP_EXPERIMENT].update(disabled=True)
            
            # Stop thread, set prepares stopping
            thread_event.set()
            
            # Stop experiemnt_thread
            experiment_thread.join(timeout=1)
            
        elif event == "Pic":
            print("You Pushed Pic Button")
            get_picture(camera)
            # TODO: Change variables here to Global to match changes in Camera Tab
            # Take a Picture, 12MP: 4056x3040
            
            """
            # Display image with OpenCV (Keeps Crashing)
            pic_capture = cv2.imread(pic_save_full_path, cv2.IMREAD_COLOR)
            pic_resize = cv2.resize(pic_capture, MON_RES)
            pic_window_tite = "pic_resize"
            cv2.imshow(pic_window_tite, pic_resize)
            print("Press 'q' to close picture")
            key=cv2.waitKey(0)
            if key == ord("q"):
                cv2.destroyAllWindows()
            
            """
            
            #with PiBayerArray(camera) as stream:
                # camera.capture(stream, 'jpeg', bayer=True)
                # Demosaic data and write to output (just use stream.array if you
                # want to skip the demosaic step)
                # output = (stream.demosaic() >> 2).astype(np.uint8)
                #with open('image.data', 'wb') as f:
                    # output.tofile(f)
                    # output.tofile(f)
        elif event == "Pic x 10":
            print("Pic x 10")
            x = 10
            delay_seconds = 5
            get_x_pictures(x, delay_seconds, camera)
            
        elif event == "Vid":
            print("You Pushed Vid Button")
            # Take a Video
            get_video(camera)
            
        # Tab 2 (Movement)
        elif event == "Get Current Location":
            print("===================================")
            print("You pressed Get Current Location!")
            get_current_location2()
            """
            printer.run_gcode("M114")
            serial_string = printer.get_serial_data()
            if GCL.does_location_exist_m114(serial_string) == True:
                current_location_dictionary, is_location_found = GCL.parse_m114(serial_string)
                print(current_location_dictionary)
                # printer.printer.flush()
            else:
                print("Location Not Found, Try Again")
                # printer.printer.flush()
            """
        elif event in [X_PLUS, X_MINUS, Y_PLUS, Y_MINUS, Z_PLUS, Z_MINUS]:
            # If any of the direction buttons are pressed, move extruder
            #  in that direction using the increment radio amounts
            run_relative(event, values)
        elif event == "Run":
            # Run GCODE found in the GCode  InputText box
            printer.run_gcode(values["-GCODE_INPUT-"])
        elif event == "Clear":
            # Clear GCode InputText box
            window.FindElement("-GCODE_INPUT-").Update("")
        elif event == UPDATE_CAMERA_TEXT:
            # TAB 3 elif statements
            print("Updating Camera Settings...")
            
            # Update Camera Rotation Angle
            camera_rotation_value = values[CAMERA_ROTATION_KEY]
            camera_rotation_angle = int(camera_rotation_value)
            
            #print(f"Cam Rotation: {camera_rotation_angle}")
            camera.rotation = camera_rotation_angle
            
            # Update Still Image Capture Resolution:
            # global PIC_WIDTH, PIC_HEIGHT
            
            new_pic_width = int(values[PIC_WIDTH_KEY])
            new_pic_height = int(values[PIC_HEIGHT_KEY])
            print(f"New Still Image Resolution: {new_pic_width, new_pic_height}")
            PIC_WIDTH = new_pic_width
            PIC_HEIGHT = new_pic_height
            #print(f"Global: {PIC_WIDTH, PIC_HEIGHT}")
        elif event == START_Z_STACK_CREATION_TEXT:
            print(f"You pressed button: {START_Z_STACK_CREATION_TEXT}")
            z_start = float(values[Z_START_KEY])
            z_end = float(values[Z_END_KEY])
            z_inc = float(values[Z_INC_KEY])
            
            # If nothing chosen, use default folder location:
            if len(values[SAVE_FOLDER_KEY]) == 0:
                save_folder_location = PIC_SAVE_FOLDER
            else:
                save_folder_location = values[SAVE_FOLDER_KEY]
            print(f"save_folder_location: {save_folder_location}")
            create_z_stack(z_start, z_end, z_inc, save_folder_location, camera)
        elif event == SAVE_LOC_BUTTON:
            print(f"You pressed: {SAVE_LOC_BUTTON}")
            save_current_location()
        elif event == START_PREVIEW:
            
            start_camera_preview(event, values, camera, preview_win_id)
            """
            print("Starting Preview With Settings")
            if camera.preview:
                camera.stop_preview()
            prev_width = int(values[PREVIEW_WIDTH_KEY])
            prev_height = int(values[PREVIEW_HEIGHT_KEY])
            prev_loc_x = int(values[PREVIEW_LOC_X_KEY])
            prev_loc_y = int(values[PREVIEW_LOC_Y_KEY])
            alpha_val = int(values[ALPHA_KEY])
            
            # Update Global Variables so Pseudo Window has Control
            PREVIEW_LOC_X = prev_loc_x
            PREVIEW_LOC_Y = prev_loc_y
            PREVIEW_WIDTH = prev_width
            PREVIEW_HEIGHT = prev_height
            PREVIEW_ALPHA = alpha_val
            
            # Move Pseudo Window to input location too
            move_window_pid(preview_win_id, prev_loc_x, prev_loc_y - PREVIEW_WINDOW_OFFSET)
            
            camera.start_preview(alpha=alpha_val, fullscreen=False, window=(prev_loc_x, prev_loc_y, prev_width, prev_height))
            
            x_win, y_win = get_window_location_from_pid(preview_win_id)
            print(f"x_win:{x_win}, y_win:{y_win}")
            """
            
        elif event == STOP_PREVIEW:
            print("Stopping Preview")
            camera.stop_preview()
        elif event == SET_EXPOSURE_MODE:
            set_exposure_mode(event, values, window, camera)
            # setup_picture_camera_settings(camera)
        if event == PIC_SAVE_FOLDER_KEY:
            save_folder = values[PIC_SAVE_FOLDER_KEY]
            print(f"Save folder: {save_folder}")
            PIC_SAVE_FOLDER = save_folder

        
        if event in WL.ALL_CROSS_HAIR_EVENTS:
            WL.event_manager(event, values, window, camera)
        
        # print("You entered ", values[0])
        
        # Original
        # imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        
        # Update GUI Window with new image
        # window['-IMAGE-'].update(data=imgbytes)
        
        # clear the stream in preparation for the next frame
        # Must do this, else it won't work
        # rawCapture.truncate(0)

    # Out of While Loop
    camera.stop_preview()
    
    # Closing Window
    window.close()
    
    # Closing 3D Printer Serial Connection
    printer.printer.close()
    
    # For loop to show camera feed
    pass

main()
# call main function
