import numpy as np
from activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

activity = ActivityReader("Legends_and_lava.tcx")

dist = [elem for elem in activity.distance if elem < 25000]
elev = activity.elevation[0:len(dist)]

sigma = 20
smoothed_elev = gaussian_filter1d(elev, sigma)
plt.plot(dist, elev)
plt.plot(dist, smoothed_elev)
plt.legend(["Original elevation profile", f"Smoothed elevation profile with SD = {sigma}"])
plt.show()

plt.plot(dist, np.gradient(smoothed_elev)*100)
plt.show()