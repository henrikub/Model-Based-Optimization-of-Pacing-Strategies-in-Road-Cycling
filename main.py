import optimization.optimal_pacing as opt
import utils.utils as utils
import activity_reader_tcx.activity_reader as act
import plotting.optimization_plots as optimization_plots
import matplotlib.pyplot as plt
import casadi as ca

activity = act.ActivityReader("Mech_isle_loop_time_trial.tcx")
activity.remove_period_after(4170)
                                
# activity = act.ActivityReader("Greater_london_flat_race.tcx")
# activity.remove_period_after(17500)

# activity = act.ActivityReader("Canopies_and_coastlines_time_trial.tcx")
# activity.remove_period_after(27800)

# activity = act.ActivityReader("Richmond_UCI_worlds.tcx")
# activity.remove_period_after(16200)
                                
# activity = act.ActivityReader("Hilly_route.tcx")
# activity.remove_period_after(9600)

# activity = act.ActivityReader("Bologna_tt.tcx")
# activity.remove_period_after(8000)

# activity = act.ActivityReader("Downtown_titans.tcx")
# activity.remove_period_after(24600)

distance_simplified, elevation_simplified = utils.simplify_track(activity.distance, activity.elevation)

# Params
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

time_initial_guess = round(activity.distance[-1]/1000*120)
N = round(activity.distance[-1]/10)

optimization_opts = {
    "N": N,
    "time_initial_guess": time_initial_guess,
    "power_initial_guess": params.get('cp'),
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": "Euler",
    "solver": "ipopt"
}

init_sol, opti, T, U, X = opt.solve_opt(distance_simplified, elevation_simplified, params, optimization_opts)
init_stats = init_sol.stats()
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
    "iterations": init_stats['iter_count'],
    "opt_time": init_stats['t_wall_total']
}
optimization_plots.plot_optimization_results(init_sol, U, X, T, distance_simplified, elevation_simplified, params, opt_details)

initialization = {
    'pos_init': init_sol.value(X[0,:]),
    'speed_init': init_sol.value(X[1,:]),
    'w_bal_init': init_sol.value(X[2,:]),
    'power_init': init_sol.value(U),
    'time_init': init_sol.value(T)
}

sol, opti, T, U, X = opt.solve_opt_warmstart(activity.distance, activity.elevation, params, optimization_opts, initialization)
stats = sol.stats()
opt_details["iterations"] = stats['iter_count']
opt_details["opt_time"] = stats['t_wall_total']
optimization_plots.plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation, params, opt_details)

t_grid = ca.linspace(0, sol.value(T), N+1)

utils.write_json(sol.value(U), t_grid.full().flatten(), sol.value(X[0,:]))

res = utils.read_json('optimal_power.json')




# w_bal_actual = utils.w_prime_balance_ode(sol.value(U),t_grid, params.get('cp'), params.get('w_prime'))
# w_bal_casadi = sol.value(X[2,:])
# w_bal_actual = [float(elem) for elem in w_bal_actual]

# fig, ax = plt.subplots()

# ax.plot(sol.value(X[0,:]), w_bal_actual)
# ax.plot(sol.value(X[0,:]), w_bal_casadi)
# ax.legend(["Actual w_bal", "Casadi w_bal"])

# ax2 = ax.twinx()
# ax2.plot(activity.distance, activity.elevation, color='tab:red')
# ax2.set_ylabel('Elevation [m]', color='tab:red')
# ax.set_ylabel("W'balance [J]")
# ax.set_xlabel("Distance [m]")
# plt.show()

# plt.plot(t_grid, w_bal_actual)
# plt.plot(t_grid, w_bal_casadi)
# plt.legend(["Actual W'bal", "Casadi W'bal"])
# plt.ylabel("W'balance [J]")
# plt.xlabel("Time [s]") 
# plt.show()