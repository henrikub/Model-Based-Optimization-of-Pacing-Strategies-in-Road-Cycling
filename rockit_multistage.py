from rockit import *
import numpy as np
import matplotlib.pyplot as plt

# Hyperparams
N1 = 10
N2 = 10

N = (N1, N2)
dT1guess = 150              # Might need to change this
dT2guess = 200
T1guess = dT1guess
T2guess = T1guess + dT2guess

# Params
mass_rider = 78
mass_bike = 8
m = mass_rider + mass_bike
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
stage1_length= 1000
slope1 = 0.0

stage2_length= 1000
slope2 = -0.0

# Limits
u_min = 0
u_max = 500
v_min = 0.5
v_max = 30

def sigmoid(x, x0, a):
    return 1/(1 + np.power(np.e, (-(x-x0)/a)))


def create_stage(ocp, t0, T, N, length, slope):
    """Create a rockit stage
    """
    stage = ocp.stage(t0=t0, T=T)

    p = stage.state()
    v = stage.state()
    w = stage.state()
    u = stage.control()
    
    stage.set_der(p, v)
    stage.set_der(v, 1/((v)*(m + Iw/r**2)) * (eta*u - m*g*v*slope - my*m*g*v - b0*v - b1*v**2 - 0.5*Cd*rho*A*v**3))
    stage.set_der(w, -(u-cp))
    #stage.set_der(w, -(u-cp)*(1-sigmoid(u, cp, 3)) + (1-w/w_prime)*(cp-u)*sigmoid(u, cp, 3))

    stage.subject_to(stage.at_tf(p) == length)

    stage.subject_to(0 <= (u <= 500))
    stage.subject_to(0.5 <= (v <= 30))
    stage.subject_to(0 <= (w <= w_prime))
    #stage.subject_to(0 <= w)
    #stage.subject_to(0 <= (ocp.T <= 400))
    
    stage.method(MultipleShooting(N=N, intg='rk'))
    stage.add_objective(stage.T)

    return stage, p, v, w 


def stitch_stages(ocp, stage1, stage2):
    # Stitch time
    ocp.subject_to(stage1.tf == stage2.t0)

    # Stich states
    for i in range(len(stage1.states)):
        ocp.subject_to(stage2.at_t0(stage2.states[i]) == stage2.at_tf(stage2.states[i]))


# Main - Setting up OCP
ocp = Ocp()

# Stage 1
stage1, p1, v1, w1 = create_stage(ocp, FreeTime(0), FreeTime(T1guess), N1, stage1_length, slope1)

ocp.subject_to(stage1.t0 == 0)
ocp.subject_to(stage1.at_t0(p1) == 0)
ocp.subject_to(stage1.at_t0(v1) == 1)
ocp.subject_to(stage1.at_t0(w1) == w_prime)

# Stage 2
stage2, p2, v2, w2 = create_stage(ocp, FreeTime(T1guess), FreeTime(T2guess), N2, stage2_length, slope2)

stitch_stages(ocp, stage1, stage2)

# Terminal Conditions
#ocp.subject_to(stage2.at_tf(p2) == stage1_length + stage2_length)

# Solver options 
opts = {"expand": True,
        "verbose": False,
        "print_time": True,
        "error_on_fail": True,
        "ipopt": {"linear_solver": "ma57",  # "ma57" is faster!
                  "max_iter": 5000,
                  'print_level': 5,
                  'sb': 'yes',  # Suppress IPOPT banner
                  'tol': 1e-4,
                  'hessian_approximation': 'limited-memory'
                  }}
ocp.solver("ipopt", opts)

sampler1 = stage1.sampler([p1, v1, w1])
sampler2 = stage2.sampler([p2, v2, w2])
samplers = (sampler1, sampler2)

dT1 = ocp.value(stage1.T)
dT2 = ocp.value(stage2.T)

T1 = dT1
T2 = T1 + dT2

# Create a casadi function
solve_ocp = ocp.to_function('solve_ocp', [ocp._method.opti.x], [T1, T2, ocp._method.opti.x, ocp.gist])

# Solve the OCP
prev_sol = 0
T1, T2, prev_sol, gist = solve_ocp(prev_sol)
# Solve again using previous solution
# T1, T2, prev_sol, gist = solve_ocp(prev_sol)