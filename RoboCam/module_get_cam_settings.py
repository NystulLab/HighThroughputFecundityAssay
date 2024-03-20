"""
Sim Code to practice getting camera setting values:

Exposure: Digital/Analog Gain
AWB: Red/Blue Gains
Shutterspeed

Things to do:
-Change Metering Mode, view values above. Are they consistent?
-Get a consistent black image, get the above values.

Collect the above data in a CSV file?
Headers: Filename, digital gain, analog gain, red gain, blue gain, shutter speed



"""

import csv
import os
import random
import time

from datetime import datetime
from picamera import PiCamera

# Preview Resolution
VID_WIDTH = 640
VID_HEIGHT = 480
VID_RES = (VID_WIDTH, VID_HEIGHT)

# Image Capture Resolution
# Take a Picture, 12MP: 4056x3040
PIC_WIDTH = 4056
PIC_HEIGHT = 3040
PIC_RES = (PIC_WIDTH, PIC_HEIGHT)

# Save CSV Headers
HEADERS = ["file_name", "iso", "analog_gain", "digital_gain", "red_gain", "blue_gain", "shutter_speed (microseconds)"]

# Change this folder for your system
SAVE_CSV_FOLDER = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/7-18-2022/Camera_Tests'
# SAVE_CSV_FILE gets updated by init_csv_file() (is temporary solution)
SAVE_CSV_FILE = ''

SAVE_IMAGE_FOLDER = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/7-18-2022/Camera_Tests'


def get_unique_id():
    current_time = datetime.now()
    unique_id = current_time.strftime("%Y-%m-%d_%H%M%S")
    # print(f"unique_id: {unique_id}")
    return unique_id


def gen_cam_data(image_file_name, camera):
    
    # Simulated Version
    # Get Exposure Mode, Digital and Analog Gains
    # analog_gain = random.random()
    # digital_gain = random.random()

    # Get AWB, red and blue gains
    # red_gain = random.random()
    # blue_gain = random.random()

    # Get Shutterspeed
    # shutter_speed = random.uniform(10.0, 35.0)
    
    # Real Version:
    # ISO version
    iso_value = camera.iso
    
    # Get Analog and Digital Gains
    #analog_gain = camera.analog_gain # Gets Fraction DataType
    #digital_gain = camera.digital_gain # Gets Fraction DataType
    
    analog_gain = camera.analog_gain.__float__() # Gets Fraction DataType, convert to float
    digital_gain = camera.digital_gain.__float__() # Gets Fraction DataType, convert to float
    
    # Get AWB Gains, red and blue
    red_gain, blue_gain = camera.awb_gains   # Gets a tuple (red, blue)
    
    # Convert Fraction to float
    red_gain = red_gain.__float__()
    blue_gain = blue_gain.__float__()
    
    # Get Shutterspeed
    # If shutter_speed is set to 0 (auto), then exposure_speed will return actual shutterspeed
    shutter_speed = camera.exposure_speed    # Gets value in microseconds
    
    data_row = [image_file_name, iso_value, analog_gain, digital_gain, red_gain, blue_gain, shutter_speed]

    return data_row


def init_csv_file():

    global SAVE_CSV_FILE

    csv_file_name = f"cam_values_{get_unique_id()}.csv"

    SAVE_CSV_FILE = csv_file_name

    full_path = os.path.join(SAVE_CSV_FOLDER, csv_file_name)

    f = open(full_path, 'w', newline="")
    writer = csv.writer(f)
    writer.writerow(HEADERS)
    f.close()


def append_to_csv_file(data_row):

    full_path = os.path.join(SAVE_CSV_FOLDER, SAVE_CSV_FILE)

    # Append to existing CSV File
    f = open(full_path, 'a', newline="")

    writer = csv.writer(f)

    writer.writerow(data_row)

    f.close()
    print(f"File Updated: {full_path}")


def setup_camera():
    camera = PiCamera()
    # camera.resolution = PIC_RES
    camera.resolution = (VID_WIDTH, VID_HEIGHT)
    camera.framerate = 32
    
    # Set Exposure mode
    # camera.exposure_mode = 'fireworks'
    
    # Set AWB Mode
    # camera.awb_mode = 'cloudy'
    
    #time.sleep(2)
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
        
        print(f"cur_value: {cur_value}")
        time.sleep(0.5)
    
    
    return camera



def set_exposure_mode(camera):
    
    # Extract Values
    # camera.resolution = PIC_RES
    
    # Turn Exposure mode back on so camera can adjust to new light
    # camera.exposure_mode = "auto"
    # camera.awb_mode = 'auto'
    
    
    camera.exposure_mode = 'fireworks'
    camera.awb_mode = 'cloudy'
    
    # Set ISO to desired value
    camera.iso = 0
    
    # Wait for Automatic Gain Control to settle
    # time.sleep(2)
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
    
    # Now fix the values
    
    # Exposure Mode
    # camera.framerate = 30
    camera.shutter_speed = 30901
    # camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    # Must let camera sleep so exposure mode can settle on certain values, else black screen happens
    # time.sleep(settle_time)
    


def get_picture(camera):
    
    image_file_name = f"image_{get_unique_id()}.jpg"
    image_full_path = os.path.join(SAVE_IMAGE_FOLDER, image_file_name)
    
    # datarow = gen_cam_data(image_file_name, camera)
    
    camera.resolution = PIC_RES
    
    time.sleep(2)
    
    # New way to sleep
    # seconds_to_wait = 2
    # sleep2(seconds_to_wait)
    
    camera.capture(image_full_path)
    #time.sleep(2)
    
    datarow = gen_cam_data(image_file_name, camera)
    
    print(f"Picture Saved: {image_full_path}")
    return datarow
    

def sleep2(seconds_to_wait):
    
    start = time.monotonic()
    elapsed_time = 0
    # for i in range(10):
    while elapsed_time < seconds_to_wait:
        # print(i)
        current_time = time.monotonic()
        elapsed_time = current_time - start
        # print(f"elapsed_time: {elapsed_time}")
    print(f"Waited {elapsed_time} seconds")
    pass


def main():
    # seconds_to_wait = 2
    # sleep2(seconds_to_wait)
    
    init_csv_file()
    # image_file_name = f"image_{get_unique_id()}.jpg"
    
    camera = setup_camera()
    set_exposure_mode(camera)
    
    # gen_cam_data(image_file_name, camera)
    # data_row = get_picture(camera)
    
    # data_row = gen_cam_data(image_file_name, camera)
    
    # print(f"data_row:\n {data_row}")
    # append_to_csv_file(data_row)

    for i in range(100):
        data_row = get_picture(camera)
        append_to_csv_file(data_row)
    
    camera.close()

    pass


if __name__ == "__main__":
    main()
