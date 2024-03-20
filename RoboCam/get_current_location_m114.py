"""
Helper Functions for the "Current Location Manager" 3D printer Gcode M114,
searches string for current location,
parses string for current location
Author: Johnny Duong
Date: 1 Apr 2021


Possible Future Updates:
-Requires separate printer serial connection module created, then this module will have manager function.


Things to think about:
-Not using the Parse library, create functions that search for the variable, gets digits afterwards until a non-digit
 or period is found
"""

# import parse library
from parse import search
import parse

# CONSTANTS
SEARCH_KEYWORDS = ["X:{:.2f}", "Y:{:.2f}", "Z:{:.2f}"]
X = "X"
Y = "Y"
Z = "Z"
# TODO: get_current_location_manager_m114()


# Define function does_location_exist_m114(serial_string)
#   Searches serial string for "X:{}", "Y:{}", and "Z:{}"
#      Returns True if all 3 are found, else returns False
def does_location_exist_m114(serial_string):
    # Intialize is_location_found as False, this will be returned
    is_location_found = False

    # Search Keywords
    # TODO: Phrase might be a better term
    # search_keywords = ["X:{}", "Y:{}", "Z:{}"]
    # search_keywords = ["X:{:.2f}", "Y:{:.2f}", "Z:{:.2f}"]

    # TODO: Figure out how to search all 3 Coordinates, maybe a list to a generic function?

    # Initialize true_counter to keep track of how many True search results are received (should be 3)
    true_counter = 0

    # Go through each keyword and search for them in the serial_string
    for keyword in SEARCH_KEYWORDS:

        # Search for keyword in the serial_string
        search_result = parse.search(keyword, serial_string)

        # If search_result has a hit, then increment true_counter
        if search_result is not None:
            true_counter += 1

    # If the true_counter matches the number of keywords, all 3 were found in serial_string.
    if true_counter == len(SEARCH_KEYWORDS):
        # Uncomment to check if function works
        # print("X, Y, and Z found!")
        is_location_found = True
    else:
        # TODO: Consider removing this print statements or leaving them for debugging purposes
        # Uncomment to check if function works
        # print("Not Found! X, Y, and Z could NOT be found!")
        pass

    return is_location_found



# Define function parse_m114(serial_string)
def parse_m114(serial_string):
    # Function assumes x, y, and z exist in the serial string, but does have backup solution if it doesn't

    # Initialize search_keywords for Findall

    # Initialize current_location_dictionary placeholder, and is_location_found
    current_location_dictionary = {"X": 0.00, "Y": 0.00, "Z": 0.00}
    is_location_found = False
    if does_location_exist_m114(serial_string) == False:
        return current_location_dictionary, is_location_found

    # Use for loop to go through each element of SEARCH_KEYWORDS
    # Assumes iterator is finite
    for keyword in SEARCH_KEYWORDS:
        # Uncomment to debug and see keywords
        # print("===================")
        # print("keyword:", keyword)

        # Use findall to search for keyword
        search_result = parse.findall(keyword, serial_string)

        # Initialize counter variable to count number of hits
        count = 0
        # Go through each result (r) of search_result
        for r in search_result:
            # Uncomment to see first element of r, this is the search result
            # print("r:", r[0])

            # Grab first character of the keyword, should be X, Y, or Z
            coordinate_letter = keyword[0]

            # Use that coordinate letter to store the result, r
            # Captures the last search result with this method
            # TODO: Think of another way that doesn't require going through all elements of the iterator.
            current_location_dictionary[coordinate_letter] = r[0]
            count += 1

        # If count is not zero (then that means there is a search result!)
        if count != 0:
            # Uncomment to debug
            # print("All X, Y, and Z coordinates have been found!")
            # If there is a search result, set is_location_found to True
            is_location_found = True

    return current_location_dictionary, is_location_found


# Future Functions:
# Define Manager Function that calls the above 2 functions and interacts with printer module

# Define call_m114() function that runs the M114 GCODE to the printer serial connection


def main():
    # serial_string = "X:1.45Y:2.67Z:100.09E:3.00 Count X: 4.01Y:5.02Z:102.03\nok"
    # serial_string = "wait\nwait\nok\nX:1.23 Y:3.45 Z:5.678 E:0.0000"
    # serial_string = "blah"
    serial_string = "X:1.45Y:2.67"

    # is_location_found = does_location_exist_m114(serial_string)
    # print("is_location_found:", is_location_found)

    # current_location_dictionary, is_location_found = parse_m114(serial_string)
    # print("current_location_dictionary:", current_location_dictionary, "\nis_location_found:", is_location_found)

    is_location_found = does_location_exist_m114(serial_string)
    if is_location_found == True:
        current_location_dictionary, is_location_found = parse_m114(serial_string)
        print("current_location_dictionary:", current_location_dictionary, "\nis_location_found:", is_location_found)
    else:
        print("nothing Found, should search again")

    pass


# main()

