import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils
from w_bal.w_bal import *

activity = ActivityReader("Hilly_route_tt_v2.tcx")
activity.remove_period_after(9600)

# activity = ActivityReader("Mech_isle_loop_time_trial.tcx")
# activity.remove_period_after(4170)


# smooth_power = gaussian_filter1d(activity.power, 4)

# optimization = utils.read_json('optimal_power.json')

# plt.plot(activity.distance, smooth_power)
# plt.plot(optimization['distance'], optimization['power'])
# plt.legend(["Smoothed actual power", "Optimal power"])
# plt.xlabel("Distance [m]")
# plt.ylabel("Power [W]")
# plt.show()

# w_bal_ode_actual = utils.w_prime_balance_ode(np.array(activity.power), np.arange(0,len(activity.power)), cp=265, w_prime=26630)
# w_bal_ode_opt = utils.w_prime_balance_ode(optimization['power'], optimization['time'], cp=265, w_prime=26630)
# plt.plot(activity.distance, w_bal_ode_actual)
# plt.plot(optimization['distance'], w_bal_ode_opt)
# plt.legend(["Actual W'balance", "Optimal W'balance"])
# plt.xlabel("Distance [m]")
# plt.ylabel("W'balance [J]")
# plt.show()

print(activity.elevation[0], activity.elevation[-40])
# activity.elevation = activity.elevation[:-40]
# activity.distance = activity.distance[:-40]
num_laps = 4
elevation = []
distance = []
if num_laps != 1:
    new_elevation = []
    new_distance = []
    for i in range(num_laps):
        new_elevation.extend(activity.elevation)
        new_distance.extend([elem + i*max(activity.distance) for elem in activity.distance])
    elevation = new_elevation
    distance = new_distance


plt.plot(distance, elevation)
plt.show()