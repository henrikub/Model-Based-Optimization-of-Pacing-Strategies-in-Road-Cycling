import numpy as np
import matplotlib.pyplot as plt

# Parameters
mass_rider = 75
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
eta = 0.975

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

potential_forces_incline = np.array(forces_pot(0.05))
potential_forces_flat = np.array(forces_pot(0))
potential_forces_decline = np.array(forces_pot(-0.05))
rolling_forces = np.array(forces_roll())
bearing_forces = np.array(forces_bearing())
drag_forces = np.array(forces_drag())

N = 8
index = np.arange(N)
width = 0.35
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
plt.xlabel("Velocity [km/h]")
ax1.set_ylabel("Power [W]")
ax2.set_ylabel("Power [W]")
ax3.set_ylabel("Power [W]")
ax1.set_title("Force components 5% incline")
ax2.set_title("Force components flat road")
ax3.set_title("Force components  5% decline")
ax1.set_xticks(index, [5, 10, 15, 20, 25, 30, 35, 40])
ax2.set_xticks(index, [5, 10, 15, 20, 25, 30, 35, 40])
ax3.set_xticks(index, [5, 10, 15, 20, 25, 30, 35, 40])

ax1.bar(index, potential_forces_incline, width)
ax1.bar(index, drag_forces, width, bottom=potential_forces_incline)
ax1.bar(index, rolling_forces, width, bottom=potential_forces_incline+drag_forces)
ax1.bar(index, bearing_forces, width, bottom=potential_forces_incline+rolling_forces+drag_forces)

ax2.bar(index, potential_forces_flat, width)
ax2.bar(index, drag_forces, width, bottom=potential_forces_flat)
ax2.bar(index, rolling_forces, width, bottom=potential_forces_flat+drag_forces)
ax2.bar(index, bearing_forces, width, bottom=potential_forces_flat+rolling_forces+drag_forces)

ax3.bar(index, potential_forces_decline, width)
ax3.bar(index, drag_forces, width, bottom=0)
ax3.bar(index, rolling_forces, width, bottom=drag_forces)
ax3.bar(index, bearing_forces, width, bottom=rolling_forces+drag_forces)

ax1.legend(['Potential', 'Drag', 'Rolling', 'Bearing'])
ax2.legend(['Potential', 'Drag', 'Rolling', 'Bearing'])
ax3.legend(['Potential', 'Drag', 'Rolling', 'Bearing'])

ax3.axhline(y=0, color='black', linestyle='-', linewidth = 0.5)
plt.subplots_adjust(hspace=0.5)

plt.show()