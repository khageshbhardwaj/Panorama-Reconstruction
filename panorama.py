# -*- coding: utf-8 -*-
"""Panorama.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_wkTK8P21jqRfpqHxIM5TPkqYbuj1MAK
"""

import pickle
import sys
import time
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
from google.colab.patches import cv2
from google.colab.patches import cv2_imshow

# fuction to strat time
def tic():
    return time.time()

#function to define Total time taken to load the data
def toc(tstart, nm=""):
  	print('%s took: %s sec.\n' % (nm,(time.time() - tstart)))

#Function to read the data from the pickle file
def read_data(fname):
    d = []
    with open(fname, 'rb') as f:
        if sys.version_info[0] < 3:
            d = pickle.load(f)
        else:
            d = pickle.load(f, encoding='latin1')  # needed for python 3

    return d

def calculate_timestamps(abs_timestamps):
    # Ensure the input array is not empty
    if len(abs_timestamps) == 0:
        return []

    inc_timestamps = abs_timestamps - abs_timestamps[0]

    return inc_timestamps

# file path location

from google.colab import drive
drive.mount('/content/drive')

dataset="8"
cfile = "/content/drive/MyDrive/data/trainset/cam/cam" + dataset + ".p"
vfile = "/content/drive/MyDrive/data/trainset/vicon/viconRot" + dataset + ".p"


ts = tic()
camd = read_data(cfile)
vicd = read_data(vfile)
toc(ts,"Data import")

# Variable containing the dictionary
cam_array = camd['cam']
cam_ts_array = camd['ts']

vic_array = vicd['rots']
vic_ts_array = vicd['ts']

# To check the shape of the arrays
print("Cam Array Shape:", cam_array.shape)
print("Timestamps Cam Array Shape:", cam_ts_array.shape)

print("VICON Array Shape:", vic_array.shape)
print("Timestamps VICON Array Shape:", vic_ts_array.shape)

# extract spherical coordinates
m, n = 320, 240
alpha = np.pi/3
d_alpha = alpha/m

beta = np.pi/4
d_beta = beta/n

centre_phi, centre_theta = m/2.0, n/2.0
phi, theta = np.meshgrid(np.arange(m), np.arange(n))
phi = (d_beta * (phi - centre_phi))
theta = (d_alpha * (theta - centre_theta)) + np.pi/2

# extract cartesian coordinates
cartesian_coords = np.stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)], axis = -1)
print(cartesian_coords.shape)

# extract the last closest-in-time rotation matrix
comparison_matrix = vic_ts_array[0, :] <= cam_ts_array.T
indices = np.argmax(~comparison_matrix, axis=1) - 1

R = vic_array[:, :, indices]
print(R.shape)

rotation_coordinates = []
for i in range(R.shape[2]):
  rotation_coordinates.append(cartesian_coords @ (R[:, :, i]))

rotation_coordinates = np.array(rotation_coordinates).transpose(1, 2, 3, 0)
print(rotation_coordinates.shape)

# extracting the spherical coordinates again
# Calculate longitude
longtd = np.arctan2(rotation_coordinates[:,:,1,:],  rotation_coordinates[:,:,0,:])

# Calculate latitude
radii = (rotation_coordinates[:,:,0,:] ** 2 + rotation_coordinates[:,:,1,:] ** 2 + rotation_coordinates[:,:,2,:] ** 2) ** 0.5
lattd = np.arccos(rotation_coordinates[:,:,2,:], radii)

# Adjust the coordinates
longtd = longtd + np.pi

# scaling the image
longtd_final = longtd/(2*np.pi) * 2000
lattd_final = lattd/(np.pi) * 1000

# clip the values
longtd_final = np.clip(longtd_final.astype(int),0,1999)
lattd_final = np.clip(lattd_final.astype(int),0,999)

# from google.colab.patches import cv2_imshow
# Specify image dimensions
height, width = 1000, 2000

# Create a blank image (black background)
blank_image = np.zeros((height, width, 3), dtype=np.uint8)

# Save the blank image to a file (optional)
cv2.imwrite('blank_image.png', blank_image)

for i in range(cam_array.shape[-1]):
    cam_image = cam_array[..., i]
    blank_image[lattd_final[...,i], longtd_final[...,i], :] = cam_image.reshape(240,320,3)

cv2_imshow(blank_image)
cv2.waitKey(0)
cv2.destroyAllWindows()