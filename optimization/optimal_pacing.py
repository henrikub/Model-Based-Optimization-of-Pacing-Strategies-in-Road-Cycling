from casadi import *
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils

def solve_opt(distance, elevation, num_steps, final_time_guess, power_init_guess, solver, smooth_power_constraint, w_bal_ode, euler_method):
    N = num_steps
    opti = Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

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

    interpolated_slope = interpolant('Slope', 'bspline', [distance], slope)

    if w_bal_ode:
        f = lambda x,u: vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    if_else(u >= cp, -(u-cp), (1 - x[2]/w_prime)*(cp-u))) 
    else:
        f = lambda x,u: vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    

    dt = T/N
    if euler_method:
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    else:
        # Runge Kutta 4 method
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    
    if smooth_power_constraint:
        opti.minimize(T + 0.000005 * sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    alpha = 0.03
    alpha_c = 0.01
    c_max = 150
    c = 80
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    #opti.subject_to(U <= 0.04 * w_bal + cp)
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(T>=0) 

    # Provide an initial guess
    opti.set_initial(T, final_time_guess)
    opti.set_initial(speed, 10)
    opti.set_initial(U, power_init_guess)
    
    p_opts = {"expand": False}
    s_opts = {"max_iter": 6000}
    opti.solver(solver) 
    sol = opti.solve()
    return sol, opti, T, U, X


def solve_opt_warmstart(distance, elevation, num_steps, final_time_guess, power_init, pos_init, speed_init, w_bal_init, solver, smooth_power_constraint, w_bal_ode, euler_method):
    N = num_steps
    opti = Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

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

    interpolated_slope = interpolant('Slope', 'bspline', [distance], slope)

    if w_bal_ode:
        f = lambda x,u: vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    if_else(u >= cp, -(u-cp), (1 - x[2]/w_prime)*(cp-u))) 
    else:
        f = lambda x,u: vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    

    dt = T/N
    if euler_method:
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    else:
        # Runge Kutta 4 method
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    
    if smooth_power_constraint:
        opti.minimize(T + 0.000005 * sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    alpha = 0.03
    alpha_c = 0.01
    c_max = 150
    c = 80
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    #opti.subject_to(U <= 0.04 * w_bal + cp)
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(T>=0) 

    # Provide an initial guess
    opti.set_initial(T, final_time_guess)
    opti.set_initial(pos, pos_init)
    opti.set_initial(speed, speed_init)
    opti.set_initial(w_bal, w_bal_init)
    opti.set_initial(U, power_init)
    
    p_opts = {"expand": False}
    s_opts = {"max_iter": 6000}
    opti.solver(solver) 
    sol = opti.solve()
    return sol, opti, T, U, X