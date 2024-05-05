from regression import regression, nonlinear_3, nonlinear_2
import numpy as np
import matplotlib.pyplot as plt
import simulator.simulator as sim
import casadi as ca
from w_bal.w_bal import w_prime_balance_ode

# power_points = np.array([352, 423, 328])
# time_points = np.array([417, 195, 610])

# params_nl3, covariance_nl3 = regression(nonlinear_3, power_points, time_points)
# w_prime_nl3, cp_nl3 = params_nl3
# print(params_nl3)

# fitted_nl3 = nonlinear_3(power_points, w_prime_nl3, cp_nl3)

# params_nl2, covariance_nl2 = regression(nonlinear_2, power_points, time_points)
# w_prime_nl2, cp_nl2 = params_nl2
# print(params_nl2)


cp = 250
w_prime = 20000

def smoothing_tanh(p, cp, steepness):
    return 0.5 + 0.5*ca.tanh((p-cp)/steepness)

def above_cp(p, cp):
    return -(p-cp)

def below_cp(p, cp, w_bal, w_prime):
    return (1-w_bal/w_prime)*(cp-p)

def smooth_derivative(w_bal, p):
    cp = 250
    w_prime = 20000

    transition = smoothing_tanh(p, cp, steepness)
    return (1-transition) * below_cp(p, cp, w_bal, w_prime) + transition * above_cp(p, cp)

p = np.arange(0,400)
steepness = 10
w_bal = 10000


x = np.linspace(-50,50,1000)
ax = plt.gca()
ax.plot(x, np.tanh(x), label=r'$\tanh(x)$')
ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/0.1), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(\frac{x}{0.1})$')
ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/1), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(x)$')
ax.plot(x, 0.5 + 0.5*np.tanh((x-0)/10), label=r'$\frac{1}{2} + \frac{1}{2}\tanh(\frac{x}{10})$')
plt.title("Smooth transition function")
ax.legend()
plt.show()

power = 1000*[200] + 1000*[251] 
time = np.arange(0,len(power))
N = len(power) 

dt = time[-1]/N  
x = ca.MX.sym('x', 1) 
u = ca.MX.sym('u', 1) 
f = smooth_derivative(x, u) 
ode = {'x': x, 'p': u, 'ode': f}  
opts = {'tf': dt} 
F = ca.integrator('F', 'rk', ode, opts)  

X = np.zeros(N)
U = power

X[0] = w_prime
for k in range(N-1):
    res = F(x0=X[k], p=U[k])  
    X[k+1] = res['xf'].full().flatten()  

w_bal_ode = w_prime_balance_ode(power, cp, w_prime)

plt.plot(time, X)
plt.plot(time, w_bal_ode)
plt.legend(["Integrated smooth W'bal", "Actual W'bal"])
plt.show()