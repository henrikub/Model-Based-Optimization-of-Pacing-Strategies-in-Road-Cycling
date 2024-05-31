import numpy as np
from regression import *

power_points = np.array([352, 423, 328])
time_points = np.array([417, 195, 610])


params_ltw, covariance_ltw = regression(linear_tw, power_points, time_points)
w_prime_ltw, cp_ltw = params_ltw

params_nl3, covariance_nl3 = regression(nonlinear_3, power_points, time_points)
w_prime_nl3, cp_nl3 = params_nl3


# Create the fitted models
time = np.arange(1,1200)
power = np.arange(0,500)

fitted_linear_tw = linear_tw(time, w_prime_ltw, cp_ltw)
fitted_nl3 = nonlinear_3(power, w_prime_nl3, cp_nl3)

print("Params linear tw: CP = ", round(cp_ltw), " w': ", round(w_prime_ltw))
print("Params nonlinear 3: CP = ", round(cp_nl3), " w': ", round(w_prime_nl3))

print("r squared nonlinear 3", r_squared(time_points, power_points, fitted_nl3))