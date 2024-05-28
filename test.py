from regression import regression, nonlinear_3, nonlinear_2
import numpy as np
import matplotlib.pyplot as plt
import simulator.simulator as sim
import casadi as ca
from utils.utils import w_prime_balance_ode_notstart

# power_points = np.array([352, 423, 328])
# time_points = np.array([417, 195, 610])

# params_nl3, covariance_nl3 = regression(nonlinear_3, power_points, time_points)
# w_prime_nl3, cp_nl3 = params_nl3
# print(params_nl3)

# fitted_nl3 = nonlinear_3(power_points, w_prime_nl3, cp_nl3)

# params_nl2, covariance_nl2 = regression(nonlinear_2, power_points, time_points)
# w_prime_nl2, cp_nl2 = params_nl2
# print(params_nl2)


# cp = 250
# w_prime = 20000

# def smoothing_tanh(p, cp, steepness):
#     return 0.5 + 0.5*ca.tanh((p-cp)/steepness)

# def above_cp(p, cp):
#     return -(p-cp)

# def below_cp(p, cp, w_bal, w_prime):
#     return (1-w_bal/w_prime)*(cp-p)

# def smooth_derivative(w_bal, p):
#     cp = 250
#     w_prime = 20000

#     transition = smoothing_tanh(p, cp, steepness)
#     return (1-transition) * below_cp(p, cp, w_bal, w_prime) + transition * above_cp(p, cp)

# p = np.arange(0,400)
# steepness = 10
# w_bal = 10000


# x = np.linspace(-50,50,1000)
# ax = plt.gca()
# ax.plot(x, np.tanh(x), label=r'$\tanh(x)$')
# ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/0.1), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(\frac{x}{0.1})$')
# ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/1), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(x)$')
# ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/10), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(\frac{x}{10})$')
# plt.title("Smooth transition function")
# ax.legend()
# plt.show()

power = np.linspace(0, 290, 100)
w_bal = np.linspace(0, 25000, 100)

w_bal_X, power_Y = np.meshgrid(w_bal, power)

def dwbal_ode(power, w_bal):
    cp = 290
    w_prime = 25000
    d_wbal = 0
    if power >= cp:
        d_wbal = - (power - cp)
    else:
        d_wbal = (1 - w_bal/w_prime)*(cp-power)
    return d_wbal

v_dwbal = np.vectorize(dwbal_ode)
dwbal_Z = v_dwbal(power_Y, w_bal_X)

contour = plt.contourf(w_bal_X, power_Y, dwbal_Z, levels=15)
plt.ylabel("Power [W]")
plt.xlabel("W'balance [J]")
cbar = plt.colorbar(contour)
cbar.set_label('dw_bal/dt')
plt.yticks(np.append(plt.yticks()[0], max(power)))
plt.xticks(np.append(plt.xticks()[0], max(w_bal)))
plt.show()