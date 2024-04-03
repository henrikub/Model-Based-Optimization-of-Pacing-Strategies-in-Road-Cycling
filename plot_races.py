import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils
from w_bal.w_bal import *

activity = ActivityReader("Hilly_route_paced_tt.tcx")
activity.remove_period_after(9600)

smooth_power = gaussian_filter1d(activity.power, 4)

optimization = utils.read_json('opt_results_json/hilly_route.json')
print(optimization['distance'])

plt.plot(activity.distance, smooth_power)
plt.plot(optimization['distance'], optimization['power'])
plt.legend(["Smoothed actual power", "Optimal power"])
plt.xlabel("Distance [m]")
plt.ylabel("Power [W]")
plt.show()

w_bal_ode_actual = w_prime_balance_ode(np.array(activity.power), cp=265, w_prime=26630)
w_bal_ode_opt = utils.w_prime_balance_ode(optimization['power'], optimization['time'], cp=265, w_prime=26630)
plt.plot(activity.distance, w_bal_ode_actual)
plt.plot(optimization['distance'], w_bal_ode_opt)
plt.legend(["Actual W'balance", "Optimal W'balance"])
plt.xlabel("Distance [m]")
plt.ylabel("W'balance [J]")
plt.show()