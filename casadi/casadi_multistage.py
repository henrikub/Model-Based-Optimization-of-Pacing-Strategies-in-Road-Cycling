from casadi import *
import matplotlib.pyplot as plt
import utils

def create_multistage_optimization(gradients, stage_distances, num_steps, smooth_power_constraint = False):
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
    

    f = lambda x,u,s: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp))


    total_distance = sum(stage_distances)
    steps_per_stage = [int(stage/total_distance*N) for stage in stage_distances]
    start = 0

    s = np.zeros(num_steps)
    for grade, steps in zip(gradients, steps_per_stage):
        s[start:start+steps] = grade
        start += steps

    dt = T/N 
    for k in range(N): 
        k1 = f(X[:,k], U[:,k], s[k])
        k2 = f(X[:,k] + dt/2*k1, U[:,k], s[k])
        k3 = f(X[:,k] + dt/2*k2, U[:,k], s[k])
        k4 = f(X[:,k] + dt*k3, U[:,k], s[k])
        x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
        opti.subject_to(X[:,k+1] == x_next)

    
    if smooth_power_constraint:
        opti.minimize(T + 0.005 * sumsqr(U[:,1:] - U[:,:-1])) 
    else:
        opti.minimize(T) 

    # Set the path constraints
    opti.subject_to(opti.bounded(0,U,500)) # control is limited
    opti.subject_to(opti.bounded(0,w_bal,w_prime))

    # Set boundary conditions
    opti.subject_to(pos[0]==0) # start at position 0
    opti.subject_to(speed[0]==1) 
    opti.subject_to(pos[-1]==total_distance)
    opti.subject_to(w_bal[0]==w_prime)

    opti.subject_to(T>=0) # time must be positive
    opti.subject_to(speed > 1)

    # Provide an initial guess for the solver
    opti.set_initial(T, 300)
    opti.set_initial(speed, 10)
    opti.set_initial(U, cp)

    opti.solver('ipopt') # set numerical backend
    return opti, T, U, X


def solve_multistage_optimization(gradients, stage_distances, max_attempts, smooth_power_constraint):
    attempt = 0
    sol = 0
    done = False

    while attempt < max_attempts and done == False:
        N = round(sum(stage_distances)/50) + attempt*3
        opti, T, U, X = create_multistage_optimization(gradients, stage_distances, N, smooth_power_constraint)
        try:
            sol = opti.solve() # actual solve
            done = True
            print(" ************************* Done found the solution!! ***************************")
        except RuntimeError:
            done = False
        finally:
            attempt += 1
    return sol, T, U, X
        

gradients = [0.05, -0.03, 0.05]
distances = [1000, 1000, 1500]
sol, T, U, X = solve_multistage_optimization(gradients, distances, 3, False)
cp = 265

power_output = sol.value(U)
optimal_time = sol.value(T)
pos = sol.value(X[0,:])
velocity = sol.value(X[1,:])
w_bal = sol.value(X[2,:])

elevation = utils.calculate_elevation_profile(gradients, distances)
plt.plot(elevation)
plt.show()

plt.subplot(3,1,1)
plt.ylabel("Power [W]")
plt.ylim(0,550)
plt.plot(pos, power_output)
plt.plot(round(pos[-1])*[cp])
plt.legend(["Optimal power output", "CP"])

plt.subplot(3,1,2)
plt.ylabel("Velocity [m/s]")
plt.ylim(0,20)
plt.plot(pos, velocity)

plt.subplot(3,1,3)
plt.ylabel("W'balance [J]")
plt.xlabel("Position [m]")
plt.ylim(0, 27000)
plt.plot(pos, w_bal)
plt.show()