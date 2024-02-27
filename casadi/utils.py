import numpy as np

def calculate_elevation_profile(slopes, lengths):
    angles =  []
    for i, s in enumerate(slopes):
        angles += lengths[i]*[np.arctan(s)]

    elevation = np.zeros(sum(lengths))
    elevation[0] = 0
    for i in range(1,len(elevation)):
        elevation[i] = elevation[i-1] + np.sin(angles[i])
    return elevation
