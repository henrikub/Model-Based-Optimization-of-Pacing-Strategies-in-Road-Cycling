import numpy as np
import matplotlib.pyplot as plt


# Parameters
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

def forces_pot(s):
    vec = []
    for v in range(5, 45, 5):
        vec.append(m*g*s*v/3.6)
    return vec

def forces_roll():
    vec = []
    for v in range(5, 45, 5):
        vec.append(my*m*g*v/3.6)
    return vec

def forces_bearing():
    vec = []
    for v in range(5, 45, 5):
        vec.append((b0*v + b1*v**2)/3.6)
    return vec

def forces_drag():
    vec = []
    for v in range(5, 45, 5):
        vec.append((0.5*Cd*rho*A*(v/3.6)**3))
    return vec

def forces(v, s):
    v = v/3.6
    P_pot = m*g*s*v
    P_roll = my*m*g*v
    P_bear = b0*v + b1*v**2
    P_drag = 0.5*Cd*rho*A*v**3
    return [P_pot, P_roll, P_bear, P_drag]

def get_forces_vec(s):
    vec = []
    for i in range(5, 45, 5):
        vec.append(forces(i, s))
    return vec

forces_flat = get_forces_vec(0)
forces_incline = get_forces_vec(0.05)
forces_decline = get_forces_vec(-0.05)

speeds = np.arange(5, 45, 5)
force_labels = ['Potential', 'Rolling', 'Bearing', 'Drag']

potential_forces_incline = np.array(forces_pot(0.05))
potential_forces_flat = np.array(forces_pot(0))
potential_forces_decline = np.array(forces_pot(-0.05))
rolling_forces = np.array(forces_roll())
bearing_forces = np.array(forces_bearing())
drag_forces = np.array(forces_drag())

print(potential_forces_incline+rolling_forces)

N = 8
index = np.arange(N)
width = 0.35
#fig, ax = plt.subplots(3, 1, figsize=(10, 12), sharex=True, sharey=True)
print(forces_pot(0.05))
print(forces_roll())
plt.bar(index, potential_forces_incline, width)
plt.bar(index, drag_forces, width, bottom=potential_forces_incline)
plt.bar(index, rolling_forces, width, bottom=potential_forces_incline+drag_forces)
plt.bar(index, bearing_forces, width, bottom=potential_forces_incline+rolling_forces+drag_forces)

plt.xlabel("Velocity [km/h]")
plt.ylabel("Power [W]")
plt.title("Force components at different velocities and gradients")
plt.xticks(index, [5, 10, 15, 20, 25, 30, 35, 40])
plt.legend(['Potential', 'Drag', 'Rolling', 'Bearing'])
plt.show()