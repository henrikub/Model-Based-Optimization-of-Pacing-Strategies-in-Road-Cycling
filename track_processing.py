import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import utils.utils as u

activity = ActivityReader("Legends_and_lava.tcx")
activity.remove_unactive_period(400)

# dist = [elem for elem in activity.distance if elem < 25000]
# elev = activity.elevation[0:len(dist)]

# sigma = 20
# smoothed_elev = gaussian_filter1d(elev, sigma)
# plt.plot(dist, elev)
# plt.plot(dist, smoothed_elev)
# plt.legend(["Original elevation profile", f"Smoothed elevation profile with SD = {sigma}"])
# plt.show()

# plt.plot(dist, np.gradient(smoothed_elev)*100)
# plt.show()
print(activity.distance[0], activity.distance[-1])
dist = u.remove_every_other_value(activity.distance)
dist = u.remove_every_other_value(dist)

dist = u.remove_every_other_value(dist)
print(dist[0], dist[-1])

print(activity.distance)
print(dist)