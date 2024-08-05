#next version _ timing the program.
# Import required libraries
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import imghdr
import math
from skimage.filters import gabor_kernel
from scipy import ndimage as ndi

scale = 1  # Initialize scale as a global variable

def convolve(image, kernel):
    filtered = ndi.convolve(image, kernel, mode='wrap')
    feat = filtered.var()
    return feat

def gabor_metric(fileName):
    sigma=1
    frequency=0.35
    grayIM=cv2.imread(fileName,0)
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
    parts = filename.split('_')
    try:
        return float(parts[2])
    except (ValueError, IndexError):
        return None

def normalize_list(input_list):
    min_value = np.min(input_list)
    max_value = np.max(input_list)
    return [(i - min_value) / (max_value - min_value) for i in input_list]

def measure_focus_metrics(img, image_path):
    laplacian = cv2.Laplacian(img, cv2.CV_64F).var()
    sobel_x = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5).var()
    sobel_y = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5).var()
    canny_edges = cv2.Canny(img,100,200).var()
    gabor_measure = gabor_metric(image_path)
    return [laplacian, sobel_x, sobel_y, canny_edges, gabor_measure]

def auto_focus(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f'Could not open or find the image: {image_path}')
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    return measure_focus_metrics(gray, image_path)

def resize_image_to_screen(image, screen_res):
    global scale
    scale = min(screen_res[0] / image.shape[1], screen_res[1] / image.shape[0])
    width, height = int(image.shape[1] * scale), int(image.shape[0] * scale)
    return cv2.resize(image, (width, height))

directory_path = r'/Users/Ray/Desktop/AutoFocus-main/04-27-2023_zstacking/z_stack_2023-04-27_132316_D4_Z5'

files = [file for file in os.listdir(directory_path) if imghdr.what(os.path.join(directory_path, file))]

metrics = ['Laplacian', 'Sobel_X', 'Sobel_Y', 'Canny', 'Gabor']

best_focus_measure = [0] * 5
best_image = [None] * 5

focus_measures = [[] for _ in range(5)]
focal_lengths = []

screen_res = 1280, 720

for file in files:
    file_path = os.path.join(directory_path, file)
    focus_measure = auto_focus(file_path)
    focal_length = extract_float_from_filename(file)
    if focus_measure and focal_length is not None:
        for i in range(5):
            if focus_measure[i] > best_focus_measure[i]:
                best_focus_measure[i] = focus_measure[i]
                best_image[i] = file_path
            focus_measures[i].append(focus_measure[i])
        focal_lengths.append(focal_length)

focus_measures = [normalize_list(measure) for measure in focus_measures]

sort_indices = np.argsort(focal_lengths)
focal_lengths = np.array(focal_lengths)[sort_indices]
focus_measures = [np.array(measure)[sort_indices] for measure in focus_measures]

results_array = np.column_stack((focal_lengths, np.array(focus_measures).T))

np.savetxt("focus_metrics.csv", results_array, delimiter=",")

for i, metric in enumerate(metrics):
    print(f'The image with the best focus ({metric}) is: {best_image[i]}')
    best_img = cv2.imread(best_image[i])
    best_img_resized = resize_image_to_screen(best_img, screen_res)
    cv2.imshow(f"Best focus ({metric})", best_img_resized)
    cv2.waitKey(0)

for i in range(1, results_array.shape[1]):
    plt.plot(results_array[:, 0], results_array[:, i], label=f"{metrics[i-1]} focus measure")

plt.legend()
plt.xlabel('Focal length')
plt.ylabel('Normalized focus measure')
plt.title('Focus measure over image sequence')
plt.savefig('focus_measure_plot.png')
plt.show()

cv2.destroyAllWindows()




