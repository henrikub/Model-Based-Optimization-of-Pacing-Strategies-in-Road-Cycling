import casadi as ca
from scipy.ndimage import gaussian_filter1d
import utils.utils as utils

def solve_opt(distance, elevation, params, optimization_opts, initialization):
    N = optimization_opts.get("N")
    opti = ca.Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

    # Mechanical model params
    mass_rider = params.get("mass_rider")
    mass_bike = params.get("mass_bike")
    m = mass_bike + mass_rider
    g = params.get("g")
    mu = params.get("mu")
    b0 = params.get("b0")
    b1 = params.get("b1")
    Iw = params.get("Iw")
    r = params.get("r")
    Cd = params.get("Cd")
    rho = params.get("rho")
    A = params.get("A")
    eta = params.get("eta")

    # Physiological model params
    w_prime = params.get("w_prime")
    cp = params.get("cp")

    sigma = 2
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)
    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)

    interpolated_friction = ca.interpolant('Friction', 'bspline', [distance], mu)

    if optimization_opts.get("w_bal_model") == "ODE":  
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - interpolated_friction(x[0])*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    utils.smooth_w_balance_ode_derivative(u, cp, x, w_prime))     
    elif optimization_opts.get("w_bal_model") == "Simple":
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - interpolated_friction(x[0])*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    else:
        raise ValueError()

    dt = T/N
    if optimization_opts.get("integration_method") == "Euler":
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "Midpoint":
        for k in range(N):
            k1 = f(X[:,k], U[:,k])
            x_next = X[:,k] + dt*f(X[:,k] + dt/2*k1, U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "RK4":
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    else:
        raise ValueError()
    
    if optimization_opts.get("smooth_power_constraint"):
        opti.minimize(T + 0.00005 * ca.sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    # Max power constraint params
    alpha = params.get("alpha")
    # alpha_c = params.get("alpha_c")
    # c_max = params.get("c_max")
    # c = params.get("c")
    #U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))
    U_max = alpha*w_bal + cp

    # Set the path constraints
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    if optimization_opts.get('negative_split'):
        w_bal_start = optimization_opts.get("w_bal_start")
        w_bal_end = optimization_opts.get("w_bal_end")
        x = ca.linspace(0,T,N+1)
        opti.subject_to(w_bal > (w_bal_end-w_bal_start)/T *ca.transpose(x) + w_bal_start)

    # Set boundary conditions
    opti.subject_to(pos[0]==distance[0]) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(opti.bounded(0, T, distance[-1]/1000*180)) 

    # Provide an initial guess
    opti.set_initial(T, initialization.get('time_init'))
    opti.set_initial(pos, initialization.get('pos_init'))
    opti.set_initial(speed, initialization.get('speed_init'))
    opti.set_initial(w_bal, initialization.get('w_bal_init'))
    opti.set_initial(U, initialization.get('power_init'))

    p_opts = {"expand": False}
    s_opts = {"max_iter": 20000}
    opti.solver(optimization_opts.get('solver'), p_opts, s_opts) 
    sol = opti.solve()
    return sol, opti, T, U, X


def solve_opt_warmstart(distance, elevation, params, optimization_opts, initialization):
    N = optimization_opts.get("N")
    opti = ca.Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

    # Mechanical model params
    mass_rider = params.get("mass_rider")
    mass_bike = params.get("mass_bike")
    m = mass_bike + mass_rider
    g = params.get("g")
    mu = params.get("mu")
    b0 = params.get("b0")
    b1 = params.get("b1")
    Iw = params.get("Iw")
    r = params.get("r")
    Cd = params.get("Cd")
    rho = params.get("rho")
    A = params.get("A")
    eta = params.get("eta")

    # Physiological model params
    w_prime = params.get("w_prime")
    cp = params.get("cp")

    sigma = 4
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)
    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)

    if optimization_opts.get("w_bal_model") == "ODE":  
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    utils.smooth_w_balance_ode_derivative(u, cp, x, w_prime))     
    elif optimization_opts.get("w_bal_model") == "Simple":
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    else:
        raise ValueError()

    dt = T/N
    if optimization_opts.get("integration_method") == "Euler":
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "Midpoint":
        for k in range(N):
            k1 = f(X[:,k], U[:,k])
            x_next = X[:,k] + dt*f(X[:,k] + dt/2*k1, U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "RK4":
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    else:
        raise ValueError()
    
    if optimization_opts.get("smooth_power_constraint"):
        opti.minimize(T + 0.00005 * ca.sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    # Max power constraint params
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(opti.bounded(0, T, distance[-1]/1000*180)) 

    # Provide an initial guess
    opti.set_initial(T, initialization.get('time_init'))
    opti.set_initial(pos, initialization.get('pos_init'))
    opti.set_initial(speed, initialization.get('speed_init'))
    opti.set_initial(w_bal, initialization.get('w_bal_init'))
    opti.set_initial(U, initialization.get('power_init'))
    opti.set_initial(opti.lam_g, initialization.get('lam_g_init'))

    p_opts = {"expand": False}
    s_opts = {"max_iter": 20000, 
              'warm_start_init_point': 'yes'}
    opti.solver(optimization_opts.get('solver'), p_opts, s_opts) 
    sol = opti.solve()
    return sol, opti, T, U, X


def solve_opt_warmstart_sim(distance, elevation, params, optimization_opts, initialization):
    N = optimization_opts.get("N")
    opti = ca.Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

    # Mechanical model params
    mass_rider = params.get("mass_rider")
    mass_bike = params.get("mass_bike")
    m = mass_bike + mass_rider
    g = params.get("g")
    mu = params.get("mu")
    b0 = params.get("b0")
    b1 = params.get("b1")
    Iw = params.get("Iw")
    r = params.get("r")
    Cd = params.get("Cd")
    rho = params.get("rho")
    A = params.get("A")
    eta = params.get("eta")

    # Physiological model params
    w_prime = params.get("w_prime")
    cp = params.get("cp")

    sigma = 4
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)
    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)

    if optimization_opts.get("w_bal_model") == "ODE":  
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    utils.smooth_w_balance_ode_derivative(u, cp, x, w_prime))     
    elif optimization_opts.get("w_bal_model") == "Simple":
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    else:
        raise ValueError()

    dt = T/N
    if optimization_opts.get("integration_method") == "Euler":
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "Midpoint":
        for k in range(N):
            k1 = f(X[:,k], U[:,k])
            x_next = X[:,k] + dt*f(X[:,k] + dt/2*k1, U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "RK4":
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    else:
        raise ValueError()
    
    if optimization_opts.get("smooth_power_constraint"):
        opti.minimize(T + 0.00005 * ca.sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    # Max power constraint params
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) 
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(opti.bounded(0, T, distance[-1]/1000*180)) 

    # Provide an initial guess
    opti.set_initial(T, initialization.get('time_init'))
    opti.set_initial(pos, initialization.get('pos_init'))
    opti.set_initial(speed, initialization.get('speed_init'))
    opti.set_initial(w_bal, initialization.get('w_bal_init'))
    opti.set_initial(U, initialization.get('power_init'))

    p_opts = {"expand": False}
    s_opts = {"max_iter": 20000}
    opti.solver(optimization_opts.get('solver'), p_opts, s_opts) 
    sol = opti.solve()
    return sol, opti, T, U, X


def reoptimize(distance, elevation, X0, params, optimization_opts, initialization):
    N = optimization_opts.get("N")
    opti = ca.Opti()
    X = opti.variable(3, N+1)
    pos = X[0,:]
    speed = X[1,:]
    w_bal = X[2,:]
    U = opti.variable(1,N+1)
    T = opti.variable()

    # Mechanical model params
    mass_rider = params.get("mass_rider")
    mass_bike = params.get("mass_bike")
    m = mass_bike + mass_rider
    g = params.get("g")
    mu = params.get("mu")
    b0 = params.get("b0")
    b1 = params.get("b1")
    Iw = params.get("Iw")
    r = params.get("r")
    Cd = params.get("Cd")
    rho = params.get("rho")
    A = params.get("A")
    eta = params.get("eta")

    # Physiological model params
    w_prime = params.get("w_prime")
    cp = params.get("cp")

    sigma = 4
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)
    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)

    if optimization_opts.get("w_bal_model") == "ODE":  
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3),
                    utils.smooth_w_balance_ode_derivative(u, cp, x, w_prime))     
    elif optimization_opts.get("w_bal_model") == "Simple":
        f = lambda x,u: ca.vertcat(x[1], 
                    (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                    -(u-cp))
    else:
        raise ValueError()

    dt = T/N
    if optimization_opts.get("integration_method") == "Euler":
        for k in range(N):
            x_next = X[:,k] + dt*f(X[:,k], U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "Midpoint":
        for k in range(N):
            k1 = f(X[:,k], U[:,k])
            x_next = X[:,k] + dt*f(X[:,k] + dt/2*k1, U[:,k])
            opti.subject_to(X[:,k+1] == x_next)
    elif optimization_opts.get("integration_method") == "RK4":
        for k in range(N): 
            k1 = f(X[:,k], U[:,k])
            k2 = f(X[:,k] + dt/2*k1, U[:,k])
            k3 = f(X[:,k] + dt/2*k2, U[:,k])
            k4 = f(X[:,k] + dt*k3, U[:,k])
            x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
    else:
        raise ValueError()
    
    if optimization_opts.get("smooth_power_constraint"):
        opti.minimize(T + 0.00005 * ca.sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 


    # Max power constraint params
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(pos[0]==X0[0]) 
    opti.subject_to(speed[0]==X0[1]) 
    opti.subject_to(pos[-1]==distance[-1])
    opti.subject_to(w_bal[0]==X0[2])

    opti.subject_to(opti.bounded(0, T, distance[-1]/1000*180)) 

    # Provide an initial guess
    opti.set_initial(T, initialization.get('time_init'))
    opti.set_initial(pos, initialization.get('pos_init'))
    opti.set_initial(speed, initialization.get('speed_init'))
    opti.set_initial(w_bal, initialization.get('w_bal_init'))
    opti.set_initial(U, initialization.get('power_init'))

    p_opts = {"expand": False}
    s_opts = {"max_iter": 20000}
    opti.solver(optimization_opts.get('solver'), p_opts, s_opts) 
    sol = opti.solve()
    return sol, opti, T, U, X


def solve_opt_pos_discretized(distance, elevation, params, optimization_opts):
    N = optimization_opts.get("N")
    opti = ca.Opti()
    X = opti.variable(2, N)
    speed = X[0,:]
    w_bal = X[1,:]
    U = opti.variable(1,N)
    T = opti.variable()

    # Mechanical model params
    mass_rider = params.get("mass_rider")
    mass_bike = params.get("mass_bike")
    m = mass_bike + mass_rider
    g = params.get("g")
    mu = params.get("mu")
    b0 = params.get("b0")
    b1 = params.get("b1")
    Iw = params.get("Iw")
    r = params.get("r")
    Cd = params.get("Cd")
    rho = params.get("rho")
    A = params.get("A")
    eta = params.get("eta")

    # Physiological model params
    w_prime = params.get("w_prime")
    cp = params.get("cp")

    sigma = 4
    smoothed_elev = gaussian_filter1d(elevation, sigma)

    slope = utils.calculate_gradient(distance, smoothed_elev)
    interpolated_slope = ca.interpolant('Slope', 'bspline', [distance], slope)

    if optimization_opts.get("w_bal_model") == "ODE": 
        f = lambda x,u,pos: ca.vertcat((1/x[0] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[0] - m*g*interpolated_slope(pos)*x[0] - b0*x[0] - b1*x[0]**2 - 0.5*Cd*rho*A*x[0]**3),
                    utils.smooth_w_balance_ode_derivative(u, cp, x, w_prime)) 
    elif optimization_opts.get("w_bal_model") == "Simple":
        f = lambda x,u,pos,dt: ca.vertcat((1/x[0] * 1/(m + Iw/r**2)) * (eta*u - mu*m*g*x[0] - m*g*interpolated_slope(pos)*x[0] - b0*x[0] - b1*x[0]**2 - 0.5*Cd*rho*A*x[0]**3), 
                    -(u-cp)/dt)
    else:
        raise ValueError()
    
    dt = lambda pos, speed, k: pos[k+1]/speed[k+1] - pos[k]/speed[k]
    dt_arr = []
    pos = ca.linspace(0,distance[-1], N)
    
    if optimization_opts.get("integration_method") == "Euler":
        for k in range(N-1):
            x_next = X[:,k] + dt(pos, speed, k)*f(X[:,k], U[:,k], pos[k], dt(pos, speed, k))
            opti.subject_to(X[:,k+1] == x_next)
            dt_arr.append(dt(pos, speed, k))
    elif optimization_opts.get("integration_method") == "RK4":
        for k in range(N-1): 
            k1 = f(X[:,k], U[:,k], pos[k])
            k2 = f(X[:,k] + dt(pos, speed, k)/2*k1, U[:,k], pos[k], dt(pos, speed, k))
            k3 = f(X[:,k] + dt(pos, speed, k)/2*k2, U[:,k], pos[k], dt(pos, speed, k))
            k4 = f(X[:,k] + dt(pos, speed, k)*k3, U[:,k], pos[k], dt(pos, speed, k))
            x_next = X[:,k] + dt(pos, speed, k)/6*(k1+2*k2+2*k3+k4)
            opti.subject_to(X[:,k+1] == x_next)
            dt_arr.append(dt(pos, speed, k))
    else:
        raise ValueError()
    
    if optimization_opts.get("smooth_power_constraint"):
        opti.minimize(T + 0.00005 * ca.sumsqr(U[:,1:] - U[:,:-1]))
    else:
        opti.minimize(T) 

    # Max power constraint params
    alpha = params.get("alpha")
    alpha_c = params.get("alpha_c")
    c_max = params.get("c_max")
    c = params.get("c")
    U_max = 4*(alpha*w_bal + cp)*(c/(alpha_c*w_bal + c_max)*(1-c/(alpha_c*w_bal + c_max)))

    # Set the path constraints
    opti.subject_to(U <= U_max)
    opti.subject_to(U >= 0)
    opti.subject_to(opti.bounded(0, w_bal, w_prime))
    opti.subject_to(opti.bounded(1, speed, 25))

    # Set boundary conditions
    opti.subject_to(speed[0]==1) 
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(sum(dt_arr) == T)
    opti.subject_to(opti.bounded(0, T, pos[-1]/1000*180)) 

    # Provide an initial guess
    opti.set_initial(T, optimization_opts.get("time_initial_guess"))
    opti.set_initial(speed, 10)
    opti.set_initial(U, optimization_opts.get("power_initial_guess"))
    
    p_opts = {"expand": False}
    s_opts = {"max_iter": 20000}
    opti.solver(optimization_opts.get('solver'), p_opts, s_opts)
    try:
        sol = opti.solve()
    except RuntimeError:
        print("Solver failed")
        return -1, opti, T, U, X 
    return sol, opti, T, U, X