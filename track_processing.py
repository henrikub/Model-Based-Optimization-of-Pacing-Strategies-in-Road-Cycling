from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
import simulator.simulator as sim
import w_bal.w_bal as w_bal
import numpy as np
import optimization.optimal_pacing as opt
import plotting.optimization_plots as optimization_plots



# cp = 265
# w_prime = 26630

# bologna = ActivityReader("Bologna_tt.tcx")
# bologna.remove_unactive_period(1000)
# w_balance_ode_old = w_bal.w_prime_balance_ode(bologna.power, cp, w_prime)
# w_balance_ode_gc = w_bal.w_prime_balance_ode(bologna.power, 279, 18500)
# w_balance_ode_int = w_bal.w_prime_balance_ode(bologna.power, 269, 24836)
# w_balance_ode_hn = w_bal.w_prime_balance_ode(bologna.power, 272, 20900)
# w_balance_ode_reg = w_bal.w_prime_balance_ode(bologna.power, 271, 24463)
# plt.plot(w_balance_ode_old)
# plt.plot(w_balance_ode_gc)
# plt.plot(w_balance_ode_int)
# plt.plot(w_balance_ode_hn)
# plt.plot(w_balance_ode_reg)
# plt.legend(["Old", "Golden cheetah", "intervals.icu", "Highnorth", "Regression"])
# plt.show()

activity = ActivityReader("Downtown_titans.tcx")
activity.remove_period_after(24600)
dist = activity.distance
elev = activity.elevation

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
N = round(dist[-1]/5)
time_guess = dist[-1]/1000*100
time_grid = np.arange(0, time_guess, N)
power = len(time_grid)*[params.get("w_prime")/time_guess + params.get("cp")]

x0 = [0, 1, params.get("w_prime")]
X, t_grid = sim.simulate_sys(power, time_grid, x0, dist, elev, params)

optimization_opts = {
    "N": N,
    "time_initial_guess": time_guess,
    "power_initial_guess": params.get('cp'),
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": "Euler",
    "solver": "ipopt"
}
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
}
initialization = {
    'pos_init': X[0,:],
    'speed_init': X[1,:],
    'w_bal_init': X[2,:],
    'power_init': power,
    'time_init': time_guess
}
sol, opti, T, U, X = opt.solve_opt_warmstart(activity.distance, activity.elevation, params, optimization_opts, initialization)
stats = sol.stats()
opt_details["iterations"] = stats['iter_count']
opt_details["opt_time"] = stats['t_wall_total']
optimization_plots.plot_optimization_results(sol, U, X, T, dist, elev, params, opt_details)
