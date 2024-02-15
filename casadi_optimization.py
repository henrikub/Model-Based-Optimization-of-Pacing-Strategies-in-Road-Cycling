from casadi import *
import matplotlib.pyplot as plt


# Set up the problem
N = 50 # number of control intervals
opti = Opti() # optimization problem


# Declare the decision variables
X = opti.variable(3, N+1) # State trajectory
pos = X[0,:]
speed = X[1,:]
w_bal = X[2,:]
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
s = 0.05
track_length = 1000

def sigmoid(x, x0, a):
    return 1/(1 + np.power(np.e, (-(x-x0)/a)))

# Set up the objective
opti.minimize(T) # race in minimal time

# System dynamics (excluding slope/gravity effect)
f = lambda x,u: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp)) 

#f = lambda x,u: vertcat(x[1], 
#                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
#                        -(u-cp)*(1-sigmoid(u, cp, 3)) + (1-w_bal/w_prime)*(cp-u)*sigmoid(u, cp, 3)) 

dt = T/N # Control interval
for k in range(N): # Loop over control intervals
    k1 = f(X[:,k], U[:,k])
    k2 = f(X[:,k] + dt/2*k1, U[:,k])
    k3 = f(X[:,k] + dt/2*k2, U[:,k])
    k4 = f(X[:,k] + dt*k3, U[:,k])
    x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
    opti.subject_to(X[:,k+1] == x_next)



# Set the path constraints
opti.subject_to(opti.bounded(0,U,500)) # control is limited
opti.subject_to(opti.bounded(0,w_bal,w_prime))

# Set boundary conditions
opti.subject_to(pos[0]==0) # start at position 0
opti.subject_to(speed[0]==1) 
opti.subject_to(pos[-1]==track_length)
opti.subject_to(w_bal[0]==w_prime)

# One extra constraint
opti.subject_to(T>=0) # time must be positive
opti.subject_to(speed > 1)

# Provide an initial guess for the solver
opti.set_initial(T, 300)
opti.set_initial(speed, 15)

p_opts = {"expand": True, "print_time": False}
s_opts = {"print_level": 3, 
	    "tol": 5e-1, 
        "max_iter": 10000,
	    "dual_inf_tol": 5.0, 
	    "constr_viol_tol": 1e-1,
	    "compl_inf_tol": 1e-1, 
	    "acceptable_tol": 1e-2, 
		"acceptable_constr_viol_tol": 0.01, 
		"acceptable_dual_inf_tol": 1e10,
		"acceptable_compl_inf_tol": 0.01,
		"acceptable_obj_change_tol": 1e20,
		"diverging_iterates_tol": 1e20}


opti.solver('ipopt', p_opts, s_opts) # set numerical backend
try:
    sol = opti.solve() # actual solve
except RuntimeError:
    print(opti.debug.g_describe(3))
    print(opti.debug.x_describe(3))


plt.subplot(3,1,1)
plt.ylim(0,550)
plt.plot(sol.value(U))

plt.subplot(3,1,2)
plt.ylim(0,20)
plt.plot(sol.value(speed))

plt.subplot(3,1,3)
plt.ylim(0, 27000)
plt.plot(sol.value(w_bal))
plt.show()
