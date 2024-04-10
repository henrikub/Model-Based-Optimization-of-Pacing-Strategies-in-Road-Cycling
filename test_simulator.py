from simulator.simulator import *
from activity_reader_tcx.activity_reader import *
import numpy as np
import matplotlib.pyplot as plt
from optimization.optimal_pacing import *
from plotting.optimization_plots import *

# activity = ActivityReader("Richmond_rollercoaster.tcx")
# activity.remove_period_after(17100)

# activity = ActivityReader("Richmond_UCI_worlds.tcx")
# activity.remove_period_after(16200)

# activity = ActivityReader("Downtown_titans.tcx")
# activity.remove_period_after(24600)

# activity = ActivityReader("Mech_isle_loop_time_trial.tcx")
# activity.remove_period_after(4170)

# activity = ActivityReader("Bologna_tt.tcx")
# activity.remove_period_after(8000)

activity = ActivityReader("Hilly_route.tcx")
activity.remove_period_after(9600)

# activity = ActivityReader("Greater_london_flat_race.tcx")
# activity.remove_period_after(17500)

# activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
# activity.remove_period_after(27800)

# activity = ActivityReader("Cobbled_climbs.tcx")
# activity.remove_period_after(18400)

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
N = round(activity.distance[-1]/5)
timegrid = np.linspace(0,round(activity.distance[-1]/1000*150), N)

# X, t_grid = simulate_sys([270]*len(timegrid), timegrid, [activity.distance[0], activity.speed[0], 26630], activity.distance, activity.elevation, params)
X, power, t_grid = create_initialization(timegrid, [activity.distance[0], activity.speed[0], params.get('w_prime')], activity.distance, activity.elevation, params)



plt.plot(X[0], X[1])
plt.plot(activity.distance, activity.speed)
plt.legend(["integrated velocity", "activity velocity"])
plt.show()

plt.plot(X[0], X[2])
plt.show()

fig, ax = plt.subplots()
ax.plot(X[0], power)
ax.legend(["simulated power"])
ax2 = ax.twinx()
ax2.plot(activity.distance, activity.elevation, color='tab:red')
plt.show()


optimization_opts = {
    "N": len(t_grid)-1,
    "time_initial_guess": timegrid[-1],
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": "Euler",
    "solver": "ipopt"
}

initialization = {
    'pos_init': X[0],
    'speed_init': X[1],
    'w_bal_init': X[2],
    'power_init': power,
    'time_init': timegrid[-1],
}

sol, opti, T, U, X = solve_opt_warmstart_sim(activity.distance, activity.elevation, params, optimization_opts, initialization)
stats = sol.stats()
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
    "iterations": stats['iter_count'],
    "opt_time": stats['t_wall_total']
}

plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation, params, opt_details)

# t_grid = ca.linspace(0, sol.value(T), N+1)

# utils.write_json(sol.value(U), t_grid.full().flatten(), sol.value(X[0,:]), sol.value(X[2,:]))

# w_bal = sol.value(X[2,:])
# dist = 7000
# index = np.argwhere(sol.value(X[0,:]) >= dist)[0][0]
# print(index)
# print(w_bal[index])


# Reoptimizing!
X0 = [5000, 15, 20000]
index = np.argwhere(np.array(activity.distance) > X0[0])[0][0]
dist = activity.distance[index:]
dist = [elem - activity.distance[index] for elem in dist]
elev = activity.elevation[index:]
N = round(dist[-1]/5)
timegrid = np.linspace(0,round(dist[-1]/1000*150), N)

sim_X, power, t_grid = create_initialization(timegrid, [dist[0], X0[1], X0[2]], dist, elev, params)


optimization_opts = {
    "N": len(t_grid)-1,
    "time_initial_guess": t_grid[-1],
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": "Euler",
    "solver": "ipopt"
}

initialization = {
    'pos_init': sim_X[0],
    'speed_init': sim_X[1],
    'w_bal_init': sim_X[2],
    'power_init': power,
    'time_init': t_grid[-1],
}
X0[0]=0
reopt_sol, reopt_opti, reopt_T, reopt_U, reopt_X = reoptimize(dist, elev, X0, params, optimization_opts, initialization)
stats = sol.stats()
opt_details = {
    "N": N,
    "w_bal_model": optimization_opts.get("w_bal_model"),
    "integration_method": optimization_opts.get("integration_method"),
    "time_init_guess": optimization_opts.get("time_initial_guess"),
    "iterations": stats['iter_count'],
    "opt_time": stats['t_wall_total']
}
pos = np.array(reopt_sol.value(reopt_X[0,:])) + activity.distance[index]
dist = [elem + activity.distance[index] for elem in dist]
print(pos)
reopt_X[0,:] = pos

plot_optimization_results(reopt_sol, reopt_U, reopt_X, reopt_T, dist, elev, params, opt_details)

plt.plot(sol.value(X[0,:]), sol.value(U))
plt.plot(np.array(pos), np.array(reopt_sol.value(reopt_U)))
plt.legend(["Initial opt", "Reopt"])
plt.show()
