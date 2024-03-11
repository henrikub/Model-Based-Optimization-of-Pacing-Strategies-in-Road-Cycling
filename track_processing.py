from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
import simulator.simulator as sim

activity = ActivityReader("Tempus_fugit.tcx")
activity.remove_unactive_period(900)

x0 = [activity.distance[0], activity.speed[0], 26630]
X, t = sim.simulate_sys(activity.power, activity.time, x0, activity.distance, activity.elevation, True)

plt.plot(activity.distance, [elem*3.6 for elem in activity.speed])
plt.plot(X[0], X[1]*3.6)
plt.legend(["Speed from activity", "Speed from integrator"])
plt.show()