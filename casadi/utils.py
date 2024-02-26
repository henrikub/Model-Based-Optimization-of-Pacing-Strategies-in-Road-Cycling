import numpy as np

def calculate_elevation_arr(slope, distance):
    angle = np.arctan(slope)
    elevation_arr = np.zeros(len(distance))

    for i, d in enumerate(distance):
        elevation_arr[i] = d * np.tan(angle)
    return elevation_arr

def create_track(slope_arr, distance_arr):
    print(" ")