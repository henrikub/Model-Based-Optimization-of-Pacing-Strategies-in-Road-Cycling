import numpy as np
import json
import optimization.optimal_pacing as opt
import plotting.optimization_plots as opt_plt
import simulator.simulator as sim
from activity_reader_tcx.activity_reader import *
from scipy.ndimage import gaussian_filter1d
import casadi as ca

route_name = "Cobbled Climbs"
num_laps = 2
integration_method = "RK4"
negative_split = True
w_bal_start = 90/100*25000
w_bal_end = 0

height = 1.80
mass = 78
w_prime = 25000
cp = 290
max_power = 933

routes_dict = {}
with open('routes.json', 'r') as file:
    routes_dict = json.load(file)

distance = routes_dict[route_name]['distance']
elevation = routes_dict[route_name]['elevation']
friction = routes_dict[route_name]['friction']
lead_in = routes_dict[route_name]['lead_in']

# Baseline intuitive pacing
activity = ActivityReader("cobbled_climbs_intuitive_pacing.tcx")
activity.remove_period_after(18748)
activity.remove_period_before(lead_in)
activity.time = np.array(activity.time) - activity.time[0]
activity.distance = np.array(activity.distance) - activity.distance[0]
smoothed_power = gaussian_filter1d(activity.power,4)

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

# Params
params = {
    'mass_rider': mass,
    'mass_bike': 8.4,
    'g': 9.81,
    'mu': friction,
    'b0': 0.091,
    'b1': 0.0087,
    'Iw': 0.14,
    'r': 0.33,
    'Cd': 0.7,
    'rho': 1.2,
    'A': 0.4,
    'eta': 1,
    'w_prime': w_prime,
    'cp': cp,
    'alpha': (max_power-cp)/w_prime
}
N = round(distance[-1]/5)
timegrid = np.linspace(0,round(distance[-1]/1000*150), N)

X, power, t_grid = sim.create_initialization(timegrid, [distance[0], 1, params.get('w_prime')], distance, elevation, params)
N = len(power)-1
optimization_opts = {
    "N": N,
    "time_initial_guess": t_grid[-1],
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": integration_method,
    "solver": "ipopt",
    "negative_split": negative_split,
    "w_bal_start": w_bal_start,
    "w_bal_end": w_bal_end
}
initialization = {
    'pos_init': X[0],
    'speed_init': X[1],
    'w_bal_init': X[2],
    'power_init': power,
    'time_init': timegrid[-1],
}
sol_rk4, opti_rk4, T_rk4, U_rk4, X_rk4 = opt.solve_opt(distance, elevation, params, optimization_opts, initialization)
stats = sol_rk4.stats()
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
    "iterations": stats['iter_count'],
    "opt_time": stats['t_wall_total'],
    "negative_split": optimization_opts.get("negative_split"),
    "w_bal_start": optimization_opts.get("w_bal_start"),
    "w_bal_end": optimization_opts.get("w_bal_end")
}
opt_plt.plot_optimization_results(sol_rk4, U_rk4, X_rk4, T_rk4, distance, elevation, params, opt_details, False)