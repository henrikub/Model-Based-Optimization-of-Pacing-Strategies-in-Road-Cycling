import numpy as np
import control as ct 
import control.optimal as obc
import matplotlib.pyplot as plt
from activity_reader import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from w_bal import *


def bicycle_update(t, x, u, params={}):
    """Bicycle dynamics for control system.
    
    Parameters
    ----------
    x : array
            System state: [position, velocity, remaining anaerobic capacity]
    u : array
            System input: [power]

    Returns
    ----------
    float
        Bicycle acceleration 
    """
    
    # System parameters
    mass_rider = 78
    mass_bike = 8
    m = params.get('m', mass_rider + mass_bike)
    g = params.get('g', 9.81)
    my = params.get('my', 0.004)
    b0 = params.get('b0', 0.091)
    b1 = params.get('b1', 0.0087)
    Iw = params.get('Iw', 0.14)
    r = params.get('r', 0.33)
    Cd = params.get('Cd', 0.7)
    rho = params.get('rho', 1.2)
    A = params.get('A', 0.4)
    eta = params.get('eta', 1)
    w_prime = params.get('w_prime', 26630)
    cp = params.get('cp', 265)

    # Variables for states and input
    v = x[1]
    w_bal = x[2]
    power = u[0]
    dw_bal = 0
    if power < cp:
        dw_bal = (1-w_bal/w_prime)*(cp-power)
    else:
        dw_bal = -(power - cp)
    
    dv = 1/v * 1/(m + Iw/r**2) * (eta*power - m*g*v*slope[int(t)] - my*m*g*v - b0*v - b1*v**2 - 0.5*Cd*rho*A*v**3)
    
    return np.array([v, dv, dw_bal])


def bicycle_output(t, x, u, params):
    return x


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

activity = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
activity.remove_unactive_period(2000)

sigma = 4
smoothed_elev = gaussian_filter1d(activity.elevation, sigma)

slope = calculate_gradient(activity.distance, smoothed_elev)

bicycle_system = ct.NonlinearIOSystem(bicycle_update, bicycle_output, states=3, name='bicycle', inputs=('u'), outputs=('p', 'v', 'w_bal'))
u = activity.power
t = activity.time
mass_rider = 78
mass_bike = 8
params = {
    'm': mass_bike + mass_rider,
    'slope': slope,
    'g': 9.81,
    'my': 0.004,
    'b0': 0.091,
    'b1': 0.0087,
    'Iw': 0.14,
    'rw': 0.33,
    'Cd': 0.7,
    'rho': 1.2,
    'A': 0.4,
    'eta': 1
}


response = ct.input_output_response(bicycle_system,  t, u, [0, 11.11, 26630], params)
t, y, u = response.time, response.outputs, response.inputs

plt.plot(t, y[1]*3.6)
plt.plot(t, [elem*3.6 for elem in activity.speed])

plt.legend(["estimated velocity", "actual velocity"])
plt.show()


error = []
for i in range(len(activity.speed)):
    error.append(y[1][i] - activity.speed[i])

print(max(error)*3.6)
print(sum(error))
print(np.mean(error))


w_bal_ode = w_prime_balance_ode(activity.power, 265, 26630)

plt.plot(t, y[2])
plt.plot(t, w_bal_ode)
plt.legend(["Estimated w_bal", "Actual w_bal"])
plt.show()