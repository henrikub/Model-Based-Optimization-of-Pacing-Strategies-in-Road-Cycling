import numpy as np
from activity_reader import *
import matplotlib.pyplot as plt

#activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
activity = ActivityReader("Flat_is_fast_race.tcx")
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



cp = 261
w_prime = 17800

w_bal_ode = w_prime_balance_ode(activity.power, cp, w_prime)
w_bal_ode_fitted = w_prime_balance_ode_fitted(activity.power, cp, w_prime)
w_bal_bartram = w_prime_balance_bartram(activity.power, cp, w_prime)

plt.plot(w_bal_ode)
plt.plot(w_bal_ode_fitted)
plt.plot(w_bal_bartram)
plt.legend(["W'bal ODE", "W'bal ODE fitted", "W'bal bartram"])
plt.show()