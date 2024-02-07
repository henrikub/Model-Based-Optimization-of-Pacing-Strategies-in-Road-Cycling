from casadi import *

# Set up the problem
N = 100 # number of control intervals
opti = Opti() # optimization problem


# Declare the decision variables
X = opti.variable(2, N+1) # State trajectory
pos = X[0,:]
speed = X[1,:]
U = opti.variable(1,N) # control trajectory (power) 
T = opti.variable() # final time

# Parameters:
mass_rider = 78
mass_bike = 8
m = opti.parameter()
opti.set_value(m, mass_rider + mass_bike)
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

# Set up the objective
opti.minimize(T) # race in minimal time

# System dynamics (excluding slope/gravity effect)
f = lambda x,u: vertcat(x[1], (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3)) # dx/dt = f(x,u)

dt = T/N # Control interval
for k in range(N): # Loop over control intervals
    k1 = f(X[:,k], U[:,k])
    k2 = f(X[:,k] + dt/2*k1, U[:,k])
    k3 = f(X[:,k] + dt/2*k2, U[:,k])
    k4 = f(X[:,k] + dt*k3, U[:,k])
    x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
    opti.subject_to(X[:,k+1] == x_next)



# Set the path constraints
opti.subject_to(opti.bounded(0,pos,1000))
opti.subject_to(opti.bounded(0,U,300)) # control is limited


# Set boundary conditions
opti.subject_to(pos[0]==0) # start at position 0
opti.subject_to(speed[0]==0.1) 
opti.subject_to(pos[-1]==1000)

# One extra constraint
opti.subject_to(T>=0) # time must be positive
opti.subject_to(speed > 0)

# Provide an initial guess for the solver
opti.set_initial(T, 300)

opti.solver('ipopt') # set numerical backend
try:
    sol = opti.solve() # actual solve
except RuntimeError:
    print(opti.debug.g_describe(1))
    print(opti.debug.x_describe(1))

