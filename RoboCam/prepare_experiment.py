"""
Module has functions that prepares experiment,
called by the 3D Printer Sampler Program
Author: Johnny Duong

Functions:
-Open CSV file holding locations of wells, returns list
-Convert Locations List to GCode String List
-Create/Get Folder and File Path

Notes:
-Takes the functions from 3dprinter_start_experiment.py because that
 module uses the camera, but only one instance of the camera can be run.

TODO:
-Implement GUI Ability to Choose Base Folder to Save To
-Choose or create file/folder name prefix and suffix

Changelog
27 April 2021: Started Document Creation, put in 4 functions, test code

"""
# ==== LIBRARIES ====
import os
import pandas as pd

from datetime import datetime

# ==== MODULES ====
import settings as C


# ==== USER DEFINED FUNCTIONS ====

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
    X = 0; Y = 1; Z = 2

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


def create_and_get_folder_path2(dest_folder):
    # Get Folder Path
    #folder_path = "{}{}".format(C.FOLDERPATH, C.FOLDERNAME_PREFIX)
    folder_path = os.path.join(dest_folder, C.FOLDERNAME_PREFIX)
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


# ==== TEST CODE ====

def main():
	# Test Code, showing the functions work.
	# TODO: Create Test.csv file, get path_list, then convert to gcode list
	csv_filename = "mht_2plates.csv"
	path_list = get_path_list_csv(csv_filename)
	gcode_string_list = convert_list_to_gcode_strings(path_list)
	print("gcode_string_list:", gcode_string_list)
	
	# Test Folder/File Path
	well_number = 1
	
	
	folder_path_complete = create_and_get_folder_path()
	print("folder_path_complete:", folder_path_complete)
	
	file_full_path = get_file_full_path(folder_path_complete, well_number)
	print("file_full_path:", file_full_path)
	
	# dest_folder = "/home/pi"
	dest_folder = r'/media/pi/Seagate Portable Drive'
	folder_path_complete = create_and_get_folder_path2(dest_folder)
	print("folder_path_complete v2:", folder_path_complete)


# Test Code, will only run main() if run independently and not as a module
# Source: www.freeecodecamp.org/news/if-name-main-python-example/
if __name__ == "__main__":
	main()


