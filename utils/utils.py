import numpy as np
import casadi as ca


def sigmoid(x, x0, a):
    return 1/(1 + np.power(np.e, (-(x-x0)/a)))

def casadi_sigmoid(x, x0, a):
    return 1/(1 + ca.exp(-(x-x0)/a))

def calculate_gradient(distance, elevation):
    gradient = []
    for i in range(len(distance)-1):
        delta_elevation = elevation[i] - elevation[i+1]
        delta_distance = distance[i] - distance[i+1]
        if delta_distance != 0:
            gradient.append(delta_elevation/delta_distance)
        else:
            gradient.append(0)
    gradient.append(0)
    return gradient

def w_prime_balance_ode(power, time, cp, w_prime):
    last = w_prime
    w_prime_balance = []
    w_prime_balance.append(w_prime)
    for i in range(len(power)-1):
        delta_t = time[i+1] - time[i]
        if power[i] < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -(cp - power[i])*delta_t/w_prime)
        else:
            new = last - (power[i] - cp)*delta_t

        w_prime_balance.append(new)
        last = new

    return w_prime_balance

def remove_every_other_value(arr):
    return arr[:1] + arr[1:-1:2] + arr[-1:]

def simplify_track(distance, elevation):
    for _ in range(4):
        distance = remove_every_other_value(distance)
        elevation = remove_every_other_value(elevation)
    return distance, elevation

def w_prime_balance_simple(power, time, cp, w_prime):
    last = w_prime
    w_prime_balance = []
    w_prime_balance.append(w_prime)
    for i in range(len(power)-1):
        delta_t = time[i+1]-time[i]
        new = last - (power[i] - cp)*delta_t
        w_prime_balance.append(new)
        last = new
    return w_prime_balance

def smooth_w_balance_ode_derivative(u, cp, x, w_prime, smooth_factor=0.1):
    transition = ca.tanh(smooth_factor * (u - cp))
    transition = 0.5 * (transition + 1)
    
    return transition * (-(u - cp)) + (1 - transition) * ((1 - x[2]/w_prime)*(cp - u))