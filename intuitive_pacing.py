import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils
import casadi as ca
from w_bal.w_bal import *
from simulator.simulator import simulate_sys
import json
import datetime 

route_name = 'Cobbled Climbs'
num_laps = 2
routes_dict = {}
with open('routes.json', 'r') as file:
    routes_dict = json.load(file)

activity = ActivityReader("cobbled_climbs_intuitive_pacing.tcx")

activity.remove_period_after(18748)
activity.remove_period_before(routes_dict[route_name]['lead_in'])
activity.time = np.array(activity.time) - activity.time[0]
activity.distance = np.array(activity.distance) - activity.distance[0]
smoothed_power = gaussian_filter1d(activity.power,4)

print("Normalized power:", utils.normalized_power(activity.power))

cp = 288
w_prime = 23600
max_power = 933
alpha = (max_power-cp)/w_prime

w_bal_hn = w_prime_balance_ode(activity.power, 286, 26900)
w_bal_i = w_prime_balance_ode(activity.power, 274, 35000)
w_bal_gc = w_prime_balance_ode(activity.power, 288, 23600)
w_bal_r = w_prime_balance_ode(activity.power, 290, 25000)
w_bal_gc_peak = w_prime_balance_ode(activity.power, 306, 20000)

plt.plot(activity.distance, w_bal_hn)
plt.plot(activity.distance, w_bal_i)
plt.plot(activity.distance, w_bal_gc)
plt.plot(activity.distance, w_bal_r)
plt.plot(activity.distance, w_bal_gc_peak)
plt.legend(["HighNorth", "intervals.icu", "GoldenCheetah", "Regression", "Golden Cheetah Peak estimate"])
plt.xlabel("Distance [m]")
plt.ylabel("W'balance [J]")
plt.show()


distance = routes_dict[route_name]['distance']
friction = routes_dict[route_name]['friction']
elevation = routes_dict[route_name]['elevation']
if num_laps != 1:
    new_elevation = []
    new_distance = []
    new_friction = []
    for i in range(num_laps):
        new_elevation.extend(elevation)
        new_friction.extend(friction)
        new_distance.extend([elem + i*max(distance) for elem in distance])
    elevation = new_elevation
    distance = new_distance
    friction = new_friction
    for i in range(len(distance)-10):
        if distance[i+1] - distance[i] < 0.5:
            distance.pop(i+1)
            elevation.pop(i+1)
            friction.pop(i+1)

mu = ca.interpolant('Friction', 'bspline', [distance], friction)

params = {
    'mass_rider': 78,
    'mass_bike': 8.4,
    'g': 9.81,
    'mu': mu,
    'b0': 0.091,
    'b1': 0.0087,
    'Iw': 0.14,
    'r': 0.33,
    'Cd': 0.7,
    'rho': 1.2,
    # 'A': 0.0293*1.8**(0.725)*78**(0.441) + 0.0604,
    'A': 0.4,
    'eta': 1,
    'w_prime': w_prime,
    'cp': cp,
    'alpha': (940-cp)/w_prime
    # 'alpha_c': 0.01,
    # 'c_max': 150,
    # 'c': 80
}
X, t_grid = simulate_sys(activity.power, [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
plt.title(f"The simulated finish time is {str(datetime.timedelta(seconds=round(t_grid[-1])))}, and the actual finish time was {str(datetime.timedelta(seconds=round(activity.time[-1])))}")

# plt.plot(activity.time, activity.speed)
# plt.plot(t_grid, X[1])

plt.plot(activity.distance, activity.speed)
plt.plot(X[0], X[1])

plt.legend(["Actual velocity", "Simulated velocity"])
plt.xlabel("Time [s]")
plt.ylabel("Velocity [m/s]")
plt.show()


# simulate holding a constant power equal to the avg power of the activity
# avg_power = np.mean(activity.power)
# print("Average power: ", avg_power)
# X, t_grid = simulate_sys(len(activity.power)*[avg_power], [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
# plt.plot(X[0], X[1])
# plt.plot(activity.distance, activity.speed)
# plt.legend(["Simulated velocity for constant power", "Activity velocity"])
# plt.title(f"The simulated finish time for constant power is {str(datetime.timedelta(seconds=round(t_grid[-1])))}")
# plt.xlabel("Distance [m]")
# plt.ylabel("Velocity [m/s]")
# plt.show()

w_bal_ode = w_prime_balance_ode(activity.power, cp, w_prime)
max_power_constraint = alpha*np.array(w_bal_ode) + cp
fig, ax = plt.subplots(3,1)
ax[0].set_title("Intuitive pacing attempt")
ax[0].plot(activity.distance, smoothed_power)
ax[0].plot(activity.distance, max_power_constraint)
ax[0].plot(activity.distance, len(activity.distance)*[cp], color='gray', linestyle='dashed')
ax[0].legend(["Smoothed power", "Maximum attainable power"], loc='upper right')
ax[0].set_ylabel("Power [W]")
ax0_twin = ax[0].twinx()
ax0_twin.plot(activity.distance, activity.elevation, color='red')
ax0_twin.set_ylabel('Elevation [m]', color='tab:red')
ax0_twin.tick_params(axis='y', labelcolor='tab:red')
ax0_twin.legend(["Elevation Profile"], loc='lower left')

ax[1].plot(activity.distance, w_bal_ode)
ax[1].set_ylabel("W'balance [J]")
ax[1].legend(["W'balance"], loc='upper right')
ax1_twin = ax[1].twinx()
ax1_twin.plot(activity.distance, activity.elevation, color='red')
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"], loc='lower left')

ax[2].plot(activity.distance, activity.heart_rate)
ax[2].set_ylabel("Heart Rate [bpm]")
ax[2].legend(["Heart Rate"], loc='upper right')
ax2_twin = ax[2].twinx()
ax2_twin.plot(activity.distance, activity.elevation, color='red')
ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
ax2_twin.tick_params(axis='y', labelcolor='tab:red')
ax2_twin.legend(["Elevation Profile"], loc='lower left')
ax[2].set_xlabel("Distance [m]")
plt.show()