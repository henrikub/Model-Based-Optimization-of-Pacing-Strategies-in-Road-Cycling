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


fig, ax = plt.subplots(3, 1, figsize=(10, 12))

bar_width = 1
bar_padding = 0.2
speeds_shift = np.arange(len(speeds)) - 3 * bar_width - bar_padding

for i, (forces, title) in enumerate(zip([forces_flat, forces_incline, forces_decline], ['Flat Road', 'Incline', 'Decline'])):
    for j, force_label in enumerate(force_labels):
        ax[i].bar(speeds + j * (bar_width + bar_padding), [force[j] for force in forces], width=bar_width, label=force_label)

    ax[i].set_title(title)
    ax[i].set_xlabel('Speed (km/h)')
    ax[i].set_ylabel('Force (N)')
    ax[i].set_xticks(speeds)
    ax[i].legend()

plt.tight_layout()

# Adjust spacing between subplots
plt.subplots_adjust(hspace=0.5)

plt.show()
