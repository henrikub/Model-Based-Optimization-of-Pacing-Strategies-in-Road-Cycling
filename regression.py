import numpy as np
from scipy.optimize import curve_fit

def linear_p(t, AWC, CP):
    return AWC*(1/t) + CP


def linear_tw(t, AWC, CP):
    return AWC + CP*t


def nonlinear_2(P, AWC, CP):
    return AWC/(P-CP)


def nonlinear_3(P, W_prime, CP):
    return (W_prime/(P-CP))-(W_prime/(933-CP))


def nonlinear_4(P, AWC, CP, P_max, tau):
    return AWC/(P-CP) + AWC/(P_max-CP) - CP*tau*(P-CP)


def regression(function, power, time):
    """Performs regression with the scipy function curve_fit for five regression models.
    Bounds and initial guesses are also provided to speed up convergence
    """
    if function == linear_p:
        initial_guess = (20000, 300)
        return curve_fit(linear_p, time, power, p0=initial_guess, bounds=(0,[50000, 1000]))

    if function == linear_tw:
        initial_guess = (20000, 300)
        return curve_fit(linear_tw, time, time*power, p0=initial_guess, bounds=(0, [50000, 1000]))
 
    if function == nonlinear_2:
        initial_guess = (20000, 300)
        return curve_fit(nonlinear_2, power, time, bounds=(0,[50000, 500]))

    if function == nonlinear_3:
        initial_guess = (26000, 280)
        return curve_fit(nonlinear_3, power, time, p0=initial_guess, bounds = ([10000, 200], [50000, 500]))
    
    if function == nonlinear_4:
        initial_guess = (20000, 250, 1000, 0.1)
        return curve_fit(nonlinear_4, power, time, p0=initial_guess, bounds=([0, 200, 500, 0], [50000, 500, 5000, 10]))
    

def r_squared(y_points, x_points, fitted_model):
    ssr = np.sum((y_points - [fitted_model[x_points]])**2)
    sst = np.sum((y_points - np.mean(y_points))**2)

    return 1 - (ssr / sst)


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