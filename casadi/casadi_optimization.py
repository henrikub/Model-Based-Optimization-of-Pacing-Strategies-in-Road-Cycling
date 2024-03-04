from casadi import *
import matplotlib.pyplot as plt
from utils.utils import *
from activity_reader import ActivityReader
from scipy.ndimage import gaussian_filter1d

activity = ActivityReader("Mech_isle_loop_time_trial.tcx")
activity.remove_unactive_period(200)

sigma = 4
smoothed_elev = gaussian_filter1d(activity.elevation, sigma)

slope = calculate_gradient(activity.distance, smoothed_elev)

# Set up the problem
N = 400 # number of control intervals
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
#s = [0.05, 0]
track_length = activity.distance[-1]

interpolated_slope = interpolant('Slope', 'bspline', [activity.distance], slope)
# Set up the objective
opti.minimize(T) # race in minimal time
#opti.minimize(T + 0.0005 * sumsqr(U[:,1:] - U[:,:-1]))

#slope = if_else(X[0] <= 2000, 0.07, -0.06)
#slope = get_slope_arr(s, track_length)

f = lambda x,u: vertcat(x[1], 
                        (1/x[1] * 1/(m + Iw/r**2)) * (eta*u - my*m*g*x[1] - m*g*interpolated_slope(x[0])*x[1] - b0*x[1] - b1*x[1]**2 - 0.5*Cd*rho*A*x[1]**3), 
                        -(u-cp)) 

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
opti.set_initial(U, cp)

opti.solver('ipopt') # set numerical backend
try:
    sol = opti.solve() # actual solve
except RuntimeError:
    print(opti.debug.g_describe(3))
    print(opti.debug.x_describe(3))


fig, ax = plt.subplots(3,1)
ax[0].set_title(f"The optimal time is {round(sol.value(T)/60, 2)} min")
ax[0].set_ylim(0,550)
ax[0].plot(sol.value(pos)[:-1], sol.value(U))
ax1_twin = ax[0].twinx()
ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
ax1_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax1_twin.tick_params(axis='y', labelcolor='tab:red')
ax1_twin.legend(["Elevation Profile"])

ax[1].set_ylim(0,20)
ax[1].plot(sol.value(pos), sol.value(speed))
ax2_twin = ax[1].twinx()
ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
ax2_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax2_twin.tick_params(axis='y', labelcolor='tab:red')
ax2_twin.legend(["Elevation Profile"])

ax[2].set_ylim(0, 27000)
ax[2].plot(sol.value(pos), sol.value(w_bal))
ax3_twin = ax[2].twinx()
ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
ax3_twin.plot(activity.distance, activity.elevation, color='tab:red')
ax3_twin.tick_params(axis='y', labelcolor='tab:red')
ax3_twin.legend(["Elevation Profile"])
plt.show()
