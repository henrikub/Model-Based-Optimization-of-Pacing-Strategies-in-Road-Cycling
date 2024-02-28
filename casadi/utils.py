import numpy as np

def calculate_elevation_profile(slopes, lengths, start_elevation):
    angles =  []
    for i, s in enumerate(slopes):
        angles += lengths[i]*[np.arctan(s)]

    elevation = np.zeros(sum(lengths))
    elevation[0] = start_elevation
    for i in range(1,len(elevation)):
        elevation[i] = elevation[i-1] + np.sin(angles[i])
    return elevation

def sigmoid(x, x0, a):
    return 1/(1 + np.power(np.e, (-(x-x0)/a)))

def get_slope_arr(slopes, lengths):
    slope_arr = []
    for i in range(len(slopes)):
        slope_arr += lengths[i]*[slopes[i]]
    return slope_arr

