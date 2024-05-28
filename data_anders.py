import matplotlib.pyplot as plt
from activity_reader_tcx.activity_reader import *
import numpy as np
import datetime
from scipy.ndimage import gaussian_filter1d
from utils.utils import normalized_power

unpaced_tt = ActivityReader("Anders_paced_tt.tcx", garmin=False)
unpaced_tt.remove_period_before(170)
unpaced_tt.remove_period_after(14410)
unpaced_tt.distance = np.array(unpaced_tt.distance) - unpaced_tt.distance[0]
unpaced_tt.time = np.array(unpaced_tt.time) - unpaced_tt.time[0]
unpaced_power = gaussian_filter1d(unpaced_tt.power, 4)

paced_tt = ActivityReader("Anders_unpaced_tt.tcx", garmin=False)
paced_tt.remove_period_before(7170)
paced_tt.remove_period_after(21130)
paced_tt.distance = np.array(paced_tt.distance) - paced_tt.distance[0]
paced_tt.time = np.array(paced_tt.time) - paced_tt.time[0]
paced_power = gaussian_filter1d(paced_tt.power, 4)

#plt.plot(paced_tt.distance, paced_tt.elevation)
plt.plot(unpaced_tt.distance, unpaced_tt.elevation)
plt.legend(["Paced TT", "Unpaced TT"])
plt.show()

# plt.plot(paced_tt.distance, paced_tt.time)
# plt.plot(unpaced_tt.distance, unpaced_tt.time)
# plt.legend(["Paced TT", "Unpaced TT"])
# plt.show()

# plt.plot(paced_tt.distance, paced_power)
# plt.plot(unpaced_tt.distance, unpaced_power)
# plt.legend(["Paced TT", "Unpaced TT"])
# plt.show()

print(f"Unpaced Time: {datetime.timedelta(seconds=unpaced_tt.time[-1])}, AP = {round(np.mean(unpaced_tt.power))}W, NP = {round(normalized_power(unpaced_tt.power))}W")
print(f"Paced Time: {datetime.timedelta(seconds=paced_tt.time[-1])}, AP = {round(np.mean(paced_tt.power))}W, NP = {round(normalized_power(paced_tt.power))}W")