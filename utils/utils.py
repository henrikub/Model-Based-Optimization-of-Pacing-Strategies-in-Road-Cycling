import numpy as np
import casadi as ca

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


def smooth_w_balance_ode_derivative(u, cp, x, w_prime, smoothness=10):
    transition = 0.5 + 0.5*ca.tanh((u - cp)/smoothness)
    
    return (1-transition)*(1-x[2]/w_prime)*(cp-u) + transition*(cp-u)


def moving_avg(x, window_size):
    return np.convolve(x, np.ones(window_size), 'valid') / window_size


def normalized_power(power):
    ma = moving_avg(power, 30)
    ma_r = np.power(ma, 4)
    avg = np.mean(ma_r)
    return np.power(avg, 1/4)