from casadi import *
import matplotlib.pyplot as plt

stages_steps = [15, 15, 15]
N = sum(stages_steps)
opti = Opti()
X = opti.variable(3, N+1)
pos = X[0,:]
speed = X[1,:]
w_bal = X[2,:]
U = opti.variable(1,N+1)
T = opti.variable()


# Parameters:
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
s1 = 0.05
s2 = -0.00
s3 = -0.05
track_length = 2000
f = lambda x,u,s: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*s*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp))


dt = T/N # Control interval
for k in range(N): # Loop over control intervals
    if k < stages_steps[0]:
        s = s1
    elif k < stages_steps[0] + stages_steps[1]:
        s = s2
    else:
        s = s3
    k1 = f(X[:,k], U[:,k], s)
    k2 = f(X[:,k] + dt/2*k1, U[:,k], s)
    k3 = f(X[:,k] + dt/2*k2, U[:,k], s)
    k4 = f(X[:,k] + dt*k3, U[:,k], s)
    x_next = X[:,k] + dt/6*(k1+2*k2+2*k3+k4)
    opti.subject_to(X[:,k+1] == x_next)

# Set up the objective
opti.minimize(T) 
#opti.minimize(T + 0.05 * sumsqr(U[:,1:] - U[:,:-1])) 

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
opti.set_initial(speed, 10)
opti.set_initial(U, cp)

opti.solver('ipopt') # set numerical backend
try:
    sol = opti.solve() # actual solve
except RuntimeError:
    print(opti.debug.g_describe(3))
    print(opti.debug.x_describe(3))


plt.subplot(3,1,1)
plt.ylabel("Power [W]")
plt.ylim(0,550)
plt.plot(sol.value(pos), sol.value(U))

plt.subplot(3,1,2)
plt.ylabel("Velocity [m/s]")
plt.ylim(0,20)
plt.plot(sol.value(pos), sol.value(speed))

plt.subplot(3,1,3)
plt.ylabel("W'balance [J]")
plt.xlabel("Position [m]")
plt.ylim(0, 27000)
plt.plot(sol.value(pos), sol.value(w_bal))
plt.show()
