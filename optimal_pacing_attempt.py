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
from scipy.interpolate import interp1d

route_name = 'Cobbled Climbs'
num_laps = 2
routes_dict = {}
with open('routes.json', 'r') as file:
    routes_dict = json.load(file)

opt_result = {}
with open('opt_results_json/optimal_pacing_attempt.json', 'r') as f:
    opt_result = json.load(f)


activity = ActivityReader("cobbled_climbs_optimal_pacing.tcx")

activity.remove_period_after(18750)
activity.remove_period_before(380)
activity.time = np.array(activity.time) - activity.time[0]
activity.distance = np.array(activity.distance) - activity.distance[0]
smoothed_power = gaussian_filter1d(activity.power,4)

height = 1.8
mass = 78
cp = 290
w_prime = 25000
max_power = 933
alpha = (max_power-cp)/w_prime

print("average power: ", round(np.mean(activity.power)))
print("Normalized power: ", round(utils.normalized_power(activity.power)))

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
    'alpha': alpha
    # 'alpha_c': 0.01,
    # 'c_max': 150,
    # 'c': 80
}

# X_general_A, t_grid_general_A = simulate_sys(activity.power, [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
# params['A'] = 0.0293*height**(0.725)*mass**(0.441) + 0.0604
# print(params['A'])
# sim_time_general_A = datetime.timedelta(seconds=round(t_grid_general_A[-1]))

# X_personal_A, t_grid_personal_A = simulate_sys(activity.power, [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
# sim_time_personal_A = datetime.timedelta(seconds=round(t_grid_personal_A[-1]))
# actual_time = datetime.timedelta(seconds=round(activity.time[-1]))

# fig, ax = plt.subplots()
# ax.plot(activity.distance, activity.speed, label="Actual velocity")
# ax.plot(X_general_A[0], X_general_A[1], label= r'Simulated velocity with $A = 0.4$')
# ax.set_xlabel("Distance [m]")
# ax.set_ylabel("Velocity [m/s]")
# ax.legend()
# fig.text(0.4, 0.02, f"Simulated time = {str(sim_time_general_A)}, actual time = {str(actual_time)}")
# plt.show()

# fig, ax = plt.subplots()
# ax.plot(activity.distance, activity.speed, label="Actual velocity")
# ax.plot(X_personal_A[0], X_personal_A[1], label=r'Simulated velocity with $A_{TT}$')
# ax.set_xlabel("Distance [m]")
# ax.set_ylabel("Velocity [m/s]")
# ax.legend()
# fig.text(0.4, 0.02, f"Simulated time = {str(sim_time_personal_A)}, actual time = {str(actual_time)}")
# plt.show()


# Simulate constant power 
# const_power = 292
# X_const_power, t_grid_const_power = simulate_sys(len(activity.power)*[const_power], [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
# finish_time_const_power = datetime.timedelta(seconds=round(t_grid_const_power[-1]))
# w_bal_const_power = utils.w_prime_balance_ode([const_power]*len(t_grid_const_power), t_grid_const_power, params.get('cp'), params.get('w_prime'))

# max_const_power = 303
# X_max_const_power, t_grid_max_const_power = simulate_sys(len(activity.power)*[max_const_power], [activity.distance[0], activity.speed[0], w_prime], activity.distance, activity.elevation, params)
# finish_time_max_const_power = datetime.timedelta(seconds=round(t_grid_max_const_power[-1]))
# w_bal_max_const_power = utils.w_prime_balance_ode([max_const_power]*len(t_grid_max_const_power), t_grid_max_const_power, params.get('cp'), params.get('w_prime'))


# fig, ax = plt.subplots(2,1)
# ax[0].plot(X_const_power[0], X_const_power[1])
# ax[0].plot(X_max_const_power[0], X_max_const_power[1])
# ax[0].legend([f"Simulated velocity for P = {const_power}W", f"Simulated velocity for P = {max_const_power}W"])
# ax[0].set_ylabel("Velocity [m/s]")

# ax[1].plot(X_const_power[0], w_bal_const_power)
# ax[1].plot(X_max_const_power[0], w_bal_max_const_power)
# ax[1].legend([f"W'balance for P = {const_power}W", f"W'balance for P = {max_const_power}W"])
# ax[1].set_ylabel("W'balance [J]")
# ax[1].set_xlabel("Distance [m]")

# fig.text(0.4, 0.03, f"Finish time for P = {const_power}W is {str(finish_time_const_power)}")
# fig.text(0.4, 0.01, f"Finish time for P = {max_const_power}W is {str(finish_time_max_const_power)}")
# plt.show()

# Plot the optimal pacing attempt
w_bal_ode = w_prime_balance_ode(activity.power, cp, w_prime)
max_power_constraint = alpha*np.array(w_bal_ode) + cp
fig, ax = plt.subplots(3,1)
ax[0].set_title("Optimal pacing attempt")
ax[0].plot(activity.distance, max_power_constraint, zorder=3)
ax[0].plot(opt_result['distance'], opt_result['power'], zorder=2)
ax[0].plot(activity.distance, smoothed_power, zorder=4)
ax[0].plot(activity.distance, len(activity.distance)*[cp], color='gray', linestyle='dashed', zorder=1)
ax[0].legend(["Maximum attainable power", "Optimal power", "Smoothed power", "CP"], loc='upper right')
ax[0].set_ylabel("Power [W]")
ax0_twin = ax[0].twinx()
ax0_twin.plot(activity.distance, activity.elevation, color='red')
ax0_twin.set_ylabel('Elevation [m]', color='tab:red')
ax0_twin.tick_params(axis='y', labelcolor='tab:red')
ax0_twin.legend(["Elevation Profile"], loc='lower left')

ax[1].plot(activity.distance, w_bal_ode, zorder=2)
ax[1].plot(opt_result['distance'], opt_result['w_bal'])
ax[1].set_ylabel("W'balance [J]")
ax[1].legend(["W'balance", "Optimal W'balance"], loc='upper right')
ax1_twin = ax[1].twinx()
ax1_twin.plot(activity.distance, activity.elevation, color='red')
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"], loc='lower left')

ax[2].plot(activity.distance, activity.heart_rate, zorder=2)
ax[2].set_ylabel("Heart Rate [bpm]")
ax[2].legend(["Heart Rate"], loc='lower right')
ax2_twin = ax[2].twinx()
ax2_twin.plot(activity.distance, activity.elevation, color='red')
ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
ax2_twin.tick_params(axis='y', labelcolor='tab:red')
ax2_twin.legend(["Elevation Profile"], loc='lower left')
ax[2].set_xlabel("Distance [m]")

ax[0].set_zorder(ax0_twin.get_zorder()+1)
ax[1].set_zorder(ax0_twin.get_zorder()+1)
ax[2].set_zorder(ax0_twin.get_zorder()+1)
ax[0].patch.set_visible(False)
ax[1].patch.set_visible(False)
ax[2].patch.set_visible(False)
plt.show()

# Calculate RMSE
interpolator_power = interp1d(opt_result["distance"], opt_result["power"])
opt_power_interp = interpolator_power(activity.distance[1:])
opt_power_interp = np.insert(opt_power_interp,0,0)
mse = np.mean(opt_power_interp - activity.power)**2
rmse = np.sqrt(mse)
print("RMSE is ", round(rmse,2))


# Plot difference in velocity and time
interpolator_time = interp1d(opt_result["distance"], opt_result["time"], kind='linear')
opt_time_interp = interpolator_time(activity.distance[1:])
opt_time_interp = np.insert(opt_time_interp,0,0)
time_difference = [activity.time[i] - opt_time_interp[i] for i in range(len(activity.time))]


fig, ax = plt.subplots(2,1)
ax[0].plot(activity.distance, activity.speed)
ax[0].plot(opt_result["distance"], opt_result["velocity"])
ax[0].legend(["Recorded velocity", "Optimal velocity"], loc='upper right')
ax[0].set_ylabel("Velocity [m/s]")
ax0_twin = ax[0].twinx()
ax0_twin.plot(activity.distance, activity.elevation, color='red')
ax0_twin.set_ylabel('Elevation [m]', color='tab:red')
ax0_twin.tick_params(axis='y', labelcolor='tab:red')
ax0_twin.legend(["Elevation Profile"], loc='lower left')

ax[1].plot(activity.distance, time_difference)
ax[1].legend(["Time difference"], loc='lower right')
ax[1].set_ylabel("Time [s]")
ax[1].set_xlabel("Distance [m]")
ax1_twin = ax[1].twinx()
ax1_twin.plot(activity.distance, activity.elevation, color='red')
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"], loc='upper left')

ax[0].set_zorder(ax0_twin.get_zorder()+1)
ax[1].set_zorder(ax0_twin.get_zorder()+1)
ax[0].patch.set_visible(False)
ax[1].patch.set_visible(False)
plt.show()
