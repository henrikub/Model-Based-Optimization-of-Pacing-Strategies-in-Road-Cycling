import casadi as ca
from scipy.ndimage import gaussian_filter1d
import utils

def simulate_sys(x0, U, t, distance, elevation, w_bal_ode):
    X = ca.sym('x', 3)

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

    if w_bal_ode:
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    ca.if_else(u >= cp, -(u-cp), (1 - x[2]/w_prime)*(cp-u))) 
    else:
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
        
    F = ca.integrator('F', 'cvodes', )