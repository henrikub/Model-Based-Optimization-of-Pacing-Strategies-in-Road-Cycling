import numpy as np
import matplotlib.pyplot as plt

from activity_reader_tcx.activity_reader import ActivityReader
from plotting_reg import *
from regression import *
from w_bal.w_bal import *

# Read the constant power tests
# test1_activity = ActivityReader("300W_test.tcx")
# test2_activity = ActivityReader("350W_test.tcx")
# test3_activity = ActivityReader("400W_test.tcx")
# test4_activity = ActivityReader("290W_test.tcx")
# retest_activity = ActivityReader("300W_retest.tcx")

# activities = [test1_activity, test2_activity, test3_activity, test4_activity]

# Remove the unactive periods from the end of the tests
# test1_activity.remove_unactive_period(600)
# test2_activity.remove_unactive_period(200)
# test3_activity.remove_unactive_period(100)
# test4_activity.remove_unactive_period(800)
# retest_activity.remove_unactive_period(600)

# Print some statistics from each test
# for i, act in enumerate(activities):
#     act.avg_power = round(np.average(act.power))
#     act.total_time = act.time[-1]
#     print(f"Statistics for test {i+1}:")
#     print(f"Average power is {act.avg_power}W")
#     print(f"Average cadence is {round(np.average(act.cadence))}rpm")
#     print(f"Max heartrate is {np.max(act.heart_rate)}bpm")
#     print(f"Total time is {act.total_time}\n")
    
# Perform regression
# power_points = np.array([int(test1_activity.avg_power), int(test2_activity.avg_power), int(test3_activity.avg_power), int(test4_activity.avg_power)])
# time_points = np.array([int(test1_activity.total_time), int(test2_activity.total_time), int(test3_activity.total_time), int(test4_activity.total_time)])

power_points = np.array([352, 423, 328, 897])
time_points = np.array([417, 195, 610, 15])

params_lp, covariance_lp = regression(linear_p, power_points, time_points)
w_prime_lp, cp_lp = params_lp

params_ltw, covariance_ltw = regression(linear_tw, power_points, time_points)
w_prime_ltw, cp_ltw = params_ltw

params_nl2, covariance_nl2 = regression(nonlinear_2, power_points, time_points)
w_prime_nl2, cp_nl2 = params_nl2

params_nl3, covariance_nl3 = regression(nonlinear_3, power_points, time_points)
w_prime_nl3, cp_nl3, p_max_nl3 = params_nl3

params_nl4, covariance_nl4 = regression(nonlinear_4, power_points, time_points)
w_prime_nl4, cp_nl4, p_max_nl4, tau_nl4 = params_nl4

# Create the fitted models
time = np.arange(1,1200)
power = np.arange(0,500)
fitted_linear_p = linear_p(time, w_prime_lp, cp_lp)
fitted_linear_tw = linear_tw(time, w_prime_ltw, cp_ltw)
fitted_nl2 = nonlinear_2(power, w_prime_nl2, cp_nl2)
fitted_nl3 = nonlinear_3(power, w_prime_nl3, cp_nl3, p_max_nl3)
fitted_nl4 = nonlinear_4(power, w_prime_nl4, cp_nl4, p_max_nl4, tau_nl4)

print("Params nonlinear 2: CP = ", cp_nl2, " w': ", w_prime_nl2)
print("Params nonlinear 3: CP = ", cp_nl3, " w': ", w_prime_nl3, " P_max: ", p_max_nl3)

# Include time points from the first workbouts of the validation tests
# val_power_points = [359, 349]
# val_time_points = [248, 282]

# retest_power = round(np.average(retest_activity.power))
# retest_time = retest_activity.time[-1]

# Plot the fitted models 
plot_regression(power_points, time_points, fitted_linear_tw, params_ltw, fitted_linear_p, params_lp, 
                fitted_nl2, params_nl2, fitted_nl3, params_nl3, fitted_nl4, params_nl4)

# # Calculate R-squared
# r_squared_ltw = r_squared(power_points*time_points, time_points, fitted_linear_tw)
# r_squared_lp = r_squared(power_points, time_points, fitted_linear_p)
# r_squared_nl2 = r_squared(time_points, power_points, fitted_nl2)
# r_squared_nl3 = r_squared(time_points, power_points, fitted_nl3)
# r_squared_nl4 = r_squared(time_points, power_points, fitted_nl4)

# print(f"R-squared for the Linear-TW model is {round(r_squared_ltw,3)}")
# print(f"R-squared for the Linear-P model is {round(r_squared_lp,3)}")
# print(f"R-squared for the Nonlinear-2 model is {round(r_squared_nl2,3)}")
# print(f"R-squared for the Nonlinear-3 model is {round(r_squared_nl3,3)}")
# print(f"R-squared for the Nonlinear-4 model is {round(r_squared_nl4,3)}\n")

# # Find mean and SD for CP and W'
# print(f"Mean and SD for CP is {round(np.mean([cp_lp, cp_ltw, cp_nl2, cp_nl3, cp_nl4]))}W and {round(np.std([cp_lp, cp_ltw, cp_nl2, cp_nl3, cp_nl4]), 2)}")
# print(f"Mean and SD for W' is {round(np.mean([w_prime_lp, w_prime_ltw, w_prime_nl2, w_prime_nl3, w_prime_nl4]))}W and {round(np.std([w_prime_lp, w_prime_ltw, w_prime_nl2, w_prime_nl3, w_prime_nl4]), 2)}")

# Plot the w'bal for the constant tests
# w_bal_test1 = w_prime_balance_ode(test1_activity.power, cp_nl3, w_prime_nl3)
# w_bal_test2 = w_prime_balance_ode(test2_activity.power, cp_nl3, w_prime_nl3)
# w_bal_test3 = w_prime_balance_ode(test3_activity.power, cp_nl3, w_prime_nl3)
# w_bal_test4 = w_prime_balance_ode(test4_activity.power, cp_nl3, w_prime_nl3)
# w_bal_retest = w_prime_balance_ode(retest_activity.power, cp_nl3, w_prime_nl3)

# plt.title("W'bal constant power output tests")
# plt.plot(w_bal_test1)
# plt.plot(w_bal_test2)
# plt.plot(w_bal_test3)
# plt.plot(w_bal_test4)
# plt.plot(w_bal_retest)
# plt.legend([f'298W: {round(w_bal_test1[-1])}J remaining', f'345W: {round(w_bal_test2[-1])}J remaining', 
#             f'392W: {round(w_bal_test3[-1])}J remaining', f'289W: {round(w_bal_test4[-1])}J remaining', 
#             f'299W(retest): {round(w_bal_retest[-1])}J remaining'], loc='upper right')
# plt.ylabel("W'bal [J]")
# plt.xlabel("Time [s]")
# plt.show()
