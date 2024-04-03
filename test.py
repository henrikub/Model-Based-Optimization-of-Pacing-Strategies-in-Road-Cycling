import utils.utils as utils
import numpy as np
from optimization import optimal_pacing as opt
from plotting import optimization_plots as optimization_plots
from activity_reader_tcx import activity_reader as act

activity = act.ActivityReader("Mech_isle_loop_time_trial.tcx")
activity.remove_period_after(4170)

# distance = np.linspace(0, 5000, 5000)
# elevation = 1000*[0] + 1000*[1] + 1000*[2] + 2000*[0]

distance = activity.distance
elevation = activity.elevation

params = {
    'mass_rider': 78,
    'mass_bike': 8,
    'g': 9.81,
    'mu': 0.004,
    'b0': 0.091,
    'b1': 0.0087,
    'Iw': 0.14,
    'r': 0.33,
    'Cd': 0.7,
    'rho': 1.2,
    'A': 0.4,
    'eta': 1,
    'w_prime': 26630,
    'cp': 265,
    'alpha': 0.03,
    'alpha_c': 0.01,
    'c_max': 150,
    'c': 80
}

time_initial_guess = round(distance[-1]/1000*120)
N = 391

optimization_opts = {
    "N": N,
    "time_initial_guess": time_initial_guess,
    "power_initial_guess": params.get('cp'),
    "smooth_power_constraint": True,
    "w_bal_model": "Simple",
    "integration_method": "Euler",
    "solver": "ipopt"
}

sol, opti, T, U, X = opt.solve_opt_pos_discretized(distance, elevation, params, optimization_opts)
print("X = ", opti.debug.value(X))
print("U = ", opti.debug.value(U))
print("T = ", opti.debug.value(T))
init_stats = sol.stats()
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
    "iterations": init_stats['iter_count'],
    "opt_time": init_stats['t_wall_total']
}
optimization_plots.plot_optimization_results2(sol, U, X, T, distance, elevation, params, opt_details)