#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 13:17:29 2023

"""
# Import the necessary libraries
import cv2  # OpenCV library for image processing
import numpy as np  # NumPy for numerical operations
import os  # OS for operating system related operations
import matplotlib.pyplot as plt  # Matplotlib for data visualization
import imghdr  # imghdr to determine the type of image files
import math
from skimage.filters import gabor_kernel
from scipy import ndimage as ndi

# Initialize the center of the Region Of Interest (ROI) and its radius
roi_center = None
roi_radius = 0

# Initialize scale variable which will be used later for resizing images
scale = 1

# This function takes a filename as input, splits it by underscore, and attempts to convert the third part to a float
def convolve(image, kernel):
    filtered = ndi.convolve(image, kernel, mode='wrap')
    feat = filtered.var()
    return feat

def gabor_metric(img):
    sigma=1
    frequency=0.35
    grayIM=img
    tinyIM=cv2.resize(grayIM, (640,480)) 

    theta=0
    angle = theta / 4. * np.pi
    kernel0 = np.real(gabor_kernel(frequency, theta=angle,sigma_x=sigma, sigma_y=sigma))
    gaborValue0=convolve(tinyIM, kernel0)

    theta=90
    angle = theta / 4. * np.pi
    kernel90 = np.real(gabor_kernel(frequency, theta=angle,sigma_x=sigma, sigma_y=sigma))
    gaborValue90=convolve(tinyIM, kernel90)

    gaborValue=math.sqrt(gaborValue0**2+gaborValue90**2)

    return gaborValue


def extract_float_from_filename(filename):
    parts = filename.split('_')  # Split the filename
    try:
        return float(parts[2])  # Try to return the third part as a float
    except (ValueError, IndexError):  # If it fails, return None
        return None

# This function takes a list of numbers and normalizes them to the range [0, 1]
def normalize_list(input_list):
    min_value = np.min(input_list)  # Find the minimum value
    max_value = np.max(input_list)  # Find the maximum value
    # Normalize each value to the range [0, 1] by subtracting the minimum and dividing by the range
    return [(i - min_value) / (max_value - min_value) for i in input_list]

# This function takes an image as input, computes several focus metrics and returns them in a list
def measure_focus_metrics(img):
    # Compute the variance of the Laplacian of the image
    laplacian = cv2.Laplacian(img, cv2.CV_64F).var()
    # Compute the variance of the Sobel derivative in x direction
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5).var()
    # Compute the variance of the Sobel derivative in y direction
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5).var()
    # Compute the variance of the Canny edge detection result
    canny_edges = cv2.Canny(img, 100, 200).var()
    gabor_met = gabor_metric(img)
    # Return the computed focus metrics
    
    return [laplacian, sobel_x, sobel_y, canny_edges, gabor_met]

# This function takes an image path, ROI center and radius as input, applies several processing steps to the image
# (including optional histogram equalization and thresholding), computes the focus metrics for the ROI, and returns them
def auto_focus(image_path, roi_center, roi_radius, hist_eq=True, threshold=False, thresh_val=2):
    image = cv2.imread(image_path)  # Read the image from the file
    if image is None:  # If the image couldn't be read, print an error message and return None
        print(f'Could not open or find the image: {image_path}')
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert the image to grayscale
    
    if hist_eq:  # If hist_eq is True, equalize the histogram of the grayscale image
        gray = cv2.equalizeHist(gray)
    
    if threshold:  # If threshold is True, apply binary thresholding
        _, gray = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)

    roi_gray = circular_roi(gray, roi_center, roi_radius)  # Create a circular ROI
    focus_measures = measure_focus_metrics(roi_gray)  # Compute the focus metrics within the ROI
    
    cv2.destroyAllWindows()  # Close all OpenCV windows
    return focus_measures  # Return the focus measures

# This function handles mouse events: left button up sets the center of the ROI, and mouse wheel changes its radius
def mouse_event(event, x, y, flags, param):
    global roi_center, roi_radius
    if event == cv2.EVENT_LBUTTONUP:  # If left mouse button is released, set the ROI center
        roi_center = (x, y)
    elif event == cv2.EVENT_MOUSEWHEEL:  # If mouse wheel is scrolled, change the ROI radius
        increment = 10 if flags == cv2.EVENT_FLAG_SHIFTKEY else 1  # If SHIFT is pressed, increment by 10, else by 1
        roi_radius += increment if flags > 0 else -increment  # If scrolled up, increase radius, else decrease
        roi_radius = max(0, roi_radius)  # Ensure radius is not negative
        
    draw_circle_on_image()  # Draw the updated ROI on the image

# This function draws a circle on the image corresponding to the current ROI
def draw_circle_on_image():
    image_copy = image_resized.copy()  # Create a copy of the image to draw on
    cv2.circle(image_copy, roi_center, roi_radius, (255, 0, 0), 2)  # Draw the ROI as a red circle
    cv2.imshow("Image", image_copy)  # Show the image with the ROI

# This function creates a circular ROI on the input image centered at 'center' with radius 'radius'
def circular_roi(img, center, radius):
    y, x = np.ogrid[-center[1]:img.shape[0]-center[1], -center[0]:img.shape[1]-center[0]]  # Create a grid of distances
    mask = x*x + y*y <= radius*radius  # Create a circular mask
    img[~mask] = 0  # Set pixels outside the mask to 0
    return img  # Return the masked image

# This function resizes an image so that it fits on the screen, while maintaining its aspect ratio
def resize_image_to_screen(image, screen_res):
    global scale  # Declare scale as global so it can be modified here
    # Compute the scale factor as the minimum of the ratios of screen resolution to image dimensions
    scale = min(screen_res[0] / image.shape[1], screen_res[1] / image.shape[0])
    # Compute the dimensions of the resized image
    width, height = int(image.shape[1] * scale), int(image.shape[0] * scale)
    # Resize the image and return it
    return cv2.resize(image, (width, height))


# Define the path to the directory containing the images
directory_path = r'/Users/Ray/Desktop/AutoFocus-main/04-27-2023_zstacking/z_stack_2023-04-27_132316_D4_Z5'

# List all image files in the directory
files = [file for file in os.listdir(directory_path) if imghdr.what(os.path.join(directory_path, file))]

# Read the first image in the directory
first_image_path = os.path.join(directory_path, files[0])
image = cv2.imread(first_image_path)

# Define the screen resolution and resize the first image to fit on the screen
screen_res = 1280, 720  
image_resized = resize_image_to_screen(image, screen_res)

# Create a window named "Image" and set up a mouse callback to handle mouse events in this window
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_event)

# Enter a loop where we repeatedly draw the ROI on the image and wait for a short time
# If the user presses ESC, break the loop
while True:
    draw_circle_on_image()
    if cv2.waitKey(20) == 27:  # ESC key
        break

# After the loop, readjust the ROI center and radius to correspond to the original image size
roi_center = (int(roi_center[0] / scale), int(roi_center[1] / scale)) if roi_center else None
roi_radius = int(roi_radius / scale)

# Print the ROI center and radius
print(f"ROI_center = {roi_center} and ROI_radius = {roi_radius}")

# Initialize lists to hold the best focus measure and corresponding image for each focus metric,
# and lists to hold all focus measures, image names, and focal lengths
metrics = ['Laplacian', 'Sobel_X', 'Sobel_Y', 'Canny', 'Gabor']
best_focus_measure = [0] * 5
best_image = [None] * 5
focus_measures = [[] for _ in range(5)]
image_names = []
focal_lengths = []

# Loop over all image files
for file in files:
    # Compute the focus measure for the current image
    file_path = os.path.join(directory_path, file)
    focus_measure = auto_focus(file_path, roi_center, roi_radius)
    # Extract the focal length from the filename
    focal_length = extract_float_from_filename(file)
    # If the focus measure and focal length could be computed, add them to the corresponding lists
    if focus_measure and focal_length is not None:
        for i in range(5):
            if focus_measure[i] > best_focus_measure[i]:
                best_focus_measure[i] = focus_measure[i]
                best_image[i] = file_path
            focus_measures[i].append(focus_measure[i])
        focal_lengths.append(focal_length)
        image_names.append(file.split('_')[-1].split('.')[0])

# Normalize each list of focus measures to the range [0, 1]
focus_measures = [normalize_list(measure) for measure in focus_measures]

# Sort the focal lengths and corresponding focus measures in ascending order
sort_indices = np.argsort(focal_lengths)
focal_lengths = np.array(focal_lengths)[sort_indices]
focus_measures = [np.array(measure)[sort_indices] for measure in focus_measures]

# Create a numpy array combining the focal lengths and focus measures, and save it to a CSV file
results_array = np.column_stack((focal_lengths, np.array(focus_measures).T))
np.savetxt("focus_metrics.csv", results_array, delimiter=",")

# Loop over all focus metrics
for i, metric in enumerate(metrics):
    # Print the filename of the image with the best focus for the current metric
    print(f'The image with the best focus ({metric}) is: {best_image[i]}')
    # Load the best image
    best_img = cv2.imread(best_image[i])
    
    # Draw a circle on the best image to indicate the region of interest (ROI)
    cv2.circle(best_img, roi_center, roi_radius, (0, 255, 0), 2)  # green ROI circle
    
    # Resize the best image to fit the screen
    best_img_resized = resize_image_to_screen(best_img, screen_res)
    
    # Show the best image with the ROI highlighted
    cv2.imshow(f"Best focus ({metric})", best_img_resized)
    cv2.waitKey(0)

# Create a plot showing how the focus measure changes with focal length for each metric
for i in range(1, results_array.shape[1]):
    plt.plot(results_array[:, 0], results_array[:, i], label=f"{metrics[i-1]} focus measure")

plt.legend()  # Add a legend
plt.xlabel('Focal length')  # Add an x-label
plt.ylabel('Normalized focus measure')  # Add a y-label
plt.title('Focus measure over image sequence')  # Add a title
plt.savefig('focus_measure_plot.png')  # Save the plot to a PNG file
plt.show()  # Display the plot

cv2.destroyAllWindows()  # Close all OpenCV windows










