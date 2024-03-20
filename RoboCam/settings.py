"""
Load Settings YAML files for 3dprinter_start_experiment
Author: Johnny Duong, Center for Cellular Construction
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, 
Center for Cellular Construction. Disclaimer:  Any opinions, findings and conclusions 
or recommendations expressed in this material are those of the authors and do not 
necessarily reflect the views of the National Science Foundation.
San Francisco State University
Purpose: Replaces Common Python file, allows for future GUI usage where the YAML files can be edited and reloaded
"""

# Import libraries, yaml
import yaml
# Create Constants Variables, like in Common file

# Load YAML files, store into constants
# Load YAML Settings

# Placeholder Constants
# Monoprice Maker Select 3D Printer V2, Lab 3D Printer
DEVICE_PATH = '/dev/ttyUSB0'
BAUDRATE = 115200     # 115200: for Marlin Firmware
TIMEOUT_TIME = 1      # Wait 1 second
REBOOT_WAIT_TIME = 5  # 5 seconds

# Maximum Values
X_MAX = 200; Y_MAX = 200; Z_MAX = 175
MAX_SPEED = 300  # In mm/sec, max speed of extruder in X/Y direction

# Preview/Picture/Video Flags
isPreviewModeOn = False
isVideoCaptureModeOn = False
isPictureCaptureModeOn = True

# Camera Rotation
CAMERA_ROTATION_ANGLE = 0

# File and Folder Names
# TODO: Put in a settings file?
FOLDERNAME_PREFIX = "Code"
FILENAME_PREFIX = "well"
FILENAME_VIDEO_EXTENSION = ".h264"
FILENAME_PICTURE_EXTENSION = ".jpg"

# RPi Path
FOLDERPATH = "/home/pi/"

# Windows Path (Save in current directory
# FOLDERPATH = ""

# Load GCODE Strings, or put them here temporarily
# GCode Strings
HOME = "G28"
ABSOLUTE_POS = "G90"
RELATIVE_POS = "G91"

# Which Project? Will influence which settings are loaded
# PROJECT = "mht"
PROJECT = "cell_sensor"

# Load YAML Settings
with open("connection_settings.yaml") as file:
    # The fullloader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    connection_settings_dict = yaml.load(file, Loader=yaml.FullLoader)
    # How to access dict items
    # print(connection_settings_dict["cell_sensor"]["monoprice"]["device_path"])
    DEVICE_PATH = connection_settings_dict[PROJECT]["monoprice"]["device_path"]
    BAUDRATE = connection_settings_dict[PROJECT]["monoprice"]["baudrate"]
    TIMEOUT_TIME = connection_settings_dict[PROJECT]["monoprice"]["timeout_time"]
    REBOOT_WAIT_TIME = connection_settings_dict[PROJECT]["monoprice"]["reboot_wait_time"]
    X_MAX = connection_settings_dict[PROJECT]["monoprice"]["max"]["x"]
    Y_MAX = connection_settings_dict[PROJECT]["monoprice"]["max"]["y"]
    Z_MAX = connection_settings_dict[PROJECT]["monoprice"]["max"]["z"]
    MAX_SPEED = connection_settings_dict[PROJECT]["monoprice"]["max"]["speed"]
    CAMERA_ROTATION_ANGLE = connection_settings_dict[PROJECT]["monoprice"]["camera_rotation"]
    print("Loaded Settings for:", connection_settings_dict[PROJECT]["monoprice"]["name"])
    print("Project:", PROJECT)
    # print("CAMERA_ROTATION_ANGLE", CAMERA_ROTATION_ANGLE)

# User Defined function that can change Constants by having user load up a YAML file and choosing a different 3D printer
# TODO: Later feature
# TODO: Research project structure for GUI and Settings file

