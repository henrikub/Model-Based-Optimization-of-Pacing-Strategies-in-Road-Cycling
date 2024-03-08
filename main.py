import optimization.optimal_pacing as opt
import utils.utils as utils
import activity_reader_tcx.activity_reader as act
from plotting import optimization_plots
import matplotlib.pyplot as plt
import casadi as ca

# activity = act.ActivityReader("Mech_isle_loop_time_trial.tcx")
# activity.remove_unactive_period(200)
                                
# activity = act.ActivityReader("Greater_london_flat_race.tcx")
# activity.remove_unactive_period(1200)

# activity = act.ActivityReader("Canopies_and_coastlines_time_trial.tcx")
# activity.remove_period_after(27800)

activity = act.ActivityReader("Richmond_UCI_worlds.tcx")
activity.remove_period_after(16200)
                                

# activity = act.ActivityReader("Hilly_route.tcx")

# activity = act.ActivityReader("Downtown_titans.tcx")
# activity.remove_period_after(24600)


distance = activity.distance
elevation = activity.elevation
time = activity.time
power = activity.power

print(len(distance))
for i in range(4):
    distance = utils.remove_every_other_value(distance)
    time = utils.remove_every_other_value(time)
    elevation = utils.remove_every_other_value(elevation)
    power = utils.remove_every_other_value(power)

print(len(distance)) 

# UCI Worlds course
# distance = [0, 1400, 2700, 4800, 6100, 6400, 8000, 9200, 10100, 10300, 10500, 11900, 12600, 12900, 13400, 13700, 13900, 14300, 14900, 15700, 16200]
# elevation = [55, 54, 64, 63, 58, 52, 55, 8, 6, 10, 5, 7, 47, 46, 19, 46, 43, 13, 8, 50, 54]

time_initial_guess = round(distance[-1]/1000*120)
N = round(distance[-1]/5)
cp = 265
w_prime = 26630

init_sol, opti, T, U, X = opt.solve_opt(distance, elevation, N, time_initial_guess, cp, solver='ipopt', 
                                        smooth_power_constraint=True, w_bal_ode=False, euler_method=True)
optimization_plots.plot_optimization_results(init_sol, U, X, T, distance, elevation)
print(len(init_sol.value(U)))

sol, opti, T, U, X = opt.solve_opt_warmstart(activity.distance, activity.elevation, N, 
                                             init_sol.value(T), init_sol.value(U), init_sol.value(X[0,:]), 
                                             init_sol.value(X[1,:]), init_sol.value(X[2,:]), solver='ipopt', 
                                             smooth_power_constraint=True, w_bal_ode=False, euler_method=True)
optimization_plots.plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation)
print(len(sol.value(U)))

t_grid = ca.linspace(0, sol.value(T), N+1)

w_bal_actual = utils.w_prime_balance_simple(sol.value(U),t_grid, cp, w_prime)
w_bal_casadi = sol.value(X[2,:])
w_bal_actual = [float(elem) for elem in w_bal_actual]

print(w_bal_actual[-1]-w_bal_casadi[-1])

fig, ax = plt.subplots()

ax.plot(sol.value(X[0,:]), w_bal_actual)
ax.plot(sol.value(X[0,:]), w_bal_casadi)
ax.legend(["Actual w_bal", "Casadi w_bal"])

ax2 = ax.twinx()
ax2.plot(activity.distance, activity.elevation, color='tab:red')
ax2.set_ylabel('Elevation [m]', color='tab:red')
plt.show()
