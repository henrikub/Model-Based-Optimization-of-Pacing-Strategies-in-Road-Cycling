import numpy as np
from activity_reader_tcx.activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
#activity = ActivityReader("Greater_london_flat_race.tcx")
activity.remove_unactive_period(100)

def w_prime_balance_ode_fitted(power, cp, w_prime):

    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -1/(765373*(cp-p)**-1.847))
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new
    return w_prime_balance

def w_prime_balance_ode(power, cp, w_prime):

    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -(cp - p)/w_prime)
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new

    return w_prime_balance

def w_prime_balance_bartram(power, cp, w_prime):

    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -1/(2287.2*(cp-p)**-0.688))
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new
    return w_prime_balance


def sigmoid(x, x0, a):
    return 1/(1 + np.power(np.e, (-(x-x0)/a)))

def w_prime_balance_ode_smooth(power, cp, w_prime):
    w_prime_balance = []
    last = w_prime

    for p in power:
        sig = 1 - sigmoid(p, cp, 5)
        new_below_cp = w_prime - (w_prime - last) * np.exp(-(cp - p) / w_prime)
        new_above_cp = last - (p - cp)
        new = sig*new_below_cp + (1-sig)*new_above_cp

        w_prime_balance.append(new)
        last = new

    return w_prime_balance



cp = 276
w_prime = 13684

w_bal_ode = w_prime_balance_ode(activity.power, cp, w_prime)
w_bal_ode_smooth = w_prime_balance_ode_smooth(activity.power, cp, w_prime)

# sigma = 4
# w_bal_ode_smooth = gaussian_filter1d(w_bal_ode, sigma)

# w_bal_ode = w_prime_balance_ode(activity.power, cp, w_prime)
# w_bal_ode_fitted = w_prime_balance_ode_fitted(activity.power, cp, w_prime)
# w_bal_bartram = w_prime_balance_bartram(activity.power, cp, w_prime)

# plt.plot(w_bal_ode)
# plt.plot(w_bal_ode_fitted)
# plt.plot(w_bal_bartram)
# plt.legend(["W'bal ODE", "W'bal ODE fitted", "W'bal bartram"])
# plt.show()

plt.plot(w_bal_ode)
plt.plot(w_bal_ode_smooth)
plt.legend(["W'bal ODE", "W'bal ODE smooth"])
plt.show()


def calculate_gradient(distance, elevation):
    gradient = []
    for i in range(len(distance)-1):
        delta_elevation = elevation[i] - elevation[i+1]
        delta_distance = distance[i] - distance[i+1]
        if delta_distance != 0:
            gradient.append(delta_elevation/delta_distance)
        else:
            gradient.append(0)
    gradient.append(0)
    return gradient

activity = ActivityReader("Mech_isle_loop_time_trial.tcx")
activity.remove_unactive_period(200)

sigma = 4
smoothed_elev = gaussian_filter1d(activity.elevation, sigma)

slope = calculate_gradient(activity.distance, smoothed_elev)
print(slope)
plt.plot(slope)
plt.show()