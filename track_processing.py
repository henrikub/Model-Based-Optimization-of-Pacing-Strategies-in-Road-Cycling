import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils
import simulator.simulator as sim
import casadi as ca

activity = ActivityReader("Tempus_fugit.tcx")
activity.remove_unactive_period(900)

# print(len(activity.distance), len(activity.cadence))
# activity.remove_period_after(5000)
# print(len(activity.distance), len(activity.cadence))

# dist = [elem for elem in activity.distance if elem < 25000]
# elev = activity.elevation[0:len(dist)]

# sigma = 20
# smoothed_elev = gaussian_filter1d(elev, sigma)
# plt.plot(dist, elev)
# plt.plot(dist, smoothed_elev)
# plt.legend(["Original elevation profile", f"Smoothed elevation profile with SD = {sigma}"])
# plt.show()

# plt.plot(dist, np.gradient(smoothed_elev)*100)
# plt.show()
# print(activity.distance[0], activity.distance[-1])
# dist = u.remove_every_other_value(activity.distance)
# dist = u.remove_every_other_value(dist)

# dist = u.remove_every_other_value(dist)
# print(dist[0], dist[-1])

# print(activity.distance)
# print(dist)

# integrator = sim.simulate_sys(activity.time[0], activity.time, activity.distance, activity.elevation, w_bal_ode=True)

# x0 = ca.MX([activity.distance[0], activity.speed[0], 26630])
# u0 = ca.MX([activity.power[0]])

# time_grid = activity.time

# res = []
# for i, t in enumerate(np.array(time_grid)):
#     out = integrator(x0=x0, u=activity.power[i])
#     x = out['xf']
#     print(x.full())


# state = []
# initial_state = [activity.distance[0], activity.speed[0], 26630]
# print(initial_state)
# print(sim.simulate_sys(activity.power[0], activity.time, initial_state, activity.distance, activity.elevation, w_bal_ode=True))
# for i in range(len(activity.time)): 
#     sol = sim.simulate_sys(activity.power[i], activity.time, initial_state, activity.distance, activity.elevation, w_bal_ode=True)
#     state.append(sol.full())
#     initial_state = sol

# state_values = ca.horzcat(*state)
# print(state_values)


x0 = [activity.distance[0], activity.speed[0], 26630]
X, t = sim.simulate_sys(activity.power, activity.time, x0, activity.distance, activity.elevation, True)

print(X[0])

plt.plot(activity.distance, [elem*3.6 for elem in activity.speed])
plt.plot(X[0], X[1]*3.6)
# plt.plot(activity.time, [elem*3.6 for elem in activity.speed])
# plt.plot(t_grid, X[1]*3.6)
plt.legend(["Speed from activity", "Speed from integrator"])
plt.show()