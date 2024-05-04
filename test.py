from regression import regression, nonlinear_3, nonlinear_2
import numpy as np

power_points = np.array([352, 423, 328])
time_points = np.array([417, 195, 610])

params_nl3, covariance_nl3 = regression(nonlinear_3, power_points, time_points)
w_prime_nl3, cp_nl3 = params_nl3
print(params_nl3)

fitted_nl3 = nonlinear_3(power_points, w_prime_nl3, cp_nl3)

params_nl2, covariance_nl2 = regression(nonlinear_2, power_points, time_points)
w_prime_nl2, cp_nl2 = params_nl2
print(params_nl2)