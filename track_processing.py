from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
import simulator.simulator as sim
import w_bal.w_bal as w_bal

# activity = ActivityReader("Tempus_fugit.tcx")
# activity.remove_unactive_period(900)

# x0 = [activity.distance[0], activity.speed[0], 26630]
# X, t = sim.simulate_sys(activity.power, activity.time, x0, activity.distance, activity.elevation, True)

# plt.plot(activity.distance, [elem*3.6 for elem in activity.speed])
# plt.plot(X[0], X[1]*3.6)
# plt.legend(["Speed from activity", "Speed from integrator"])
# plt.show()

cp = 265
w_prime = 26630

bologna = ActivityReader("Mech_isle_loop_time_trial.tcx")
bologna.remove_unactive_period(1000)
w_balance_ode_old = w_bal.w_prime_balance_ode(bologna.power, cp, w_prime)
w_balance_ode_gc = w_bal.w_prime_balance_ode(bologna.power, 279, 18500)
w_balance_ode_int = w_bal.w_prime_balance_ode(bologna.power, 269, 24836)
w_balance_ode_hn = w_bal.w_prime_balance_ode(bologna.power, 272, 20900)
w_balance_ode_reg = w_bal.w_prime_balance_ode(bologna.power, 271, 24463)
plt.plot(w_balance_ode_old)
plt.plot(w_balance_ode_gc)
plt.plot(w_balance_ode_int)
plt.plot(w_balance_ode_hn)
plt.plot(w_balance_ode_reg)
plt.legend(["Old", "Golden cheetah", "intervals.icu", "Highnorth", "Regression"])
plt.show()