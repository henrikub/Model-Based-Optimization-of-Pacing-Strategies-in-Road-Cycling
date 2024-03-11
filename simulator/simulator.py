import casadi as ca
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils
import numpy as np

def simulate_sys(power, time, x0, distance, elevation, w_bal_ode):
    mass_rider = 78
    mass_bike = 8
    m = mass_bike + mass_rider
    g = 9.81
    my = 0.004
    b0 = 0.091
    b1 = 0.0087
    Iw = 0.14
    r = 0.33
    Cd = 0.7
    rho = 1.2
    A = 0.4
    eta = 1
    w_prime = 26630
    cp = 265

    sigma = 4
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)

    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)
        


    def system_dynamics(x, u):
        return ca.vertcat(x[1], 
                (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                utils.smooth_derivative(u, cp, x, w_prime)) 

    tf = time[-1]
    N = len(time)
    t_grid = np.linspace(0,tf,N)


    dt = tf/N  
    x = ca.MX.sym('x', 3) 
    u = ca.MX.sym('u', 1)  
    f = system_dynamics(x, u)  
    ode = {'x': x, 'p': u, 'ode': f}  
    opts = {'tf': dt} 
    F = ca.integrator('F', 'rk', ode, opts)  

    X = np.zeros((3, N))
    U = power

    X[:,0] = x0
    for k in range(N-1):
        res = F(x0=X[:,k], p=U[k])  
        X[:,k+1] = res['xf'].full().flatten()  
    
    return X, t_grid