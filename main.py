import optimization.optimal_pacing as opt
import utils.utils as utils
import activity_reader_tcx.activity_reader as act
from plotting import optimization_plots


activity = act.ActivityReader("Mech_isle_loop_time_trial.tcx")
#activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
#activity = ActivityReader("Hilly_route.tcx")
activity.remove_unactive_period(200)

print(len(activity.distance))
activity.distance = utils.remove_every_other_value(activity.distance)
activity.time = utils.remove_every_other_value(activity.time)
activity.elevation = utils.remove_every_other_value(activity.elevation)
activity.power = utils.remove_every_other_value(activity.power)

activity.distance = utils.remove_every_other_value(activity.distance)
activity.time = utils.remove_every_other_value(activity.time)
activity.elevation = utils.remove_every_other_value(activity.elevation)
activity.power = utils.remove_every_other_value(activity.power)
activity.distance = utils.remove_every_other_value(activity.distance)
activity.time = utils.remove_every_other_value(activity.time)
activity.elevation = utils.remove_every_other_value(activity.elevation)
activity.power = utils.remove_every_other_value(activity.power)

print(len(activity.distance))


distance = activity.distance
elevation = activity.elevation

# UCI Worlds course
# distance = [0, 1400, 2700, 4800, 6100, 6400, 8000, 9200, 10100, 10300, 10500, 11900, 12600, 12900, 13400, 13700, 13900, 14300, 14900, 15700, 16200]
# elevation = [55, 54, 64, 63, 58, 52, 55, 8, 6, 10, 5, 7, 47, 46, 19, 46, 43, 13, 8, 50, 54]

time_initial_guess = round(distance[-1]/1000*120)
N = round(distance[-1]/20)
sol, T, U, X = opt.solve_opt(distance, elevation, time_initial_guess, N, smooth_power_constraint=True, w_bal_ode=True, euler_method=False)

#optimization_plots.plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation)
optimization_plots.plot_optimization_results(sol, U, X, T, distance, elevation)
