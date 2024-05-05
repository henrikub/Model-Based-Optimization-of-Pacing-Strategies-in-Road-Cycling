import numpy as np
import casadi as ca
import json

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

def simplify_track(distance, elevation, factor):
    for _ in range(factor):
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

def smooth_w_balance_ode_derivative(u, cp, x, w_prime, smoothness=10):
    transition = 0.5 + 0.5*ca.tanh((u - cp)/smoothness)
    
    return (1-transition)*(1-x[2]/w_prime)*(cp-u) + transition*(cp-u)

def write_json(power, time, distance, w_bal):
    power_dict = {
        'power': power.tolist(),
        'time': time.tolist(),
        'distance': distance.tolist(),
        'w_bal': w_bal.tolist()
    }
    with open('optimal_power.json','w') as file:
        json.dump(power_dict, file)

def read_json(filename):
    obj = {}
    with open(filename, 'r') as file:
        obj = json.load(file)
    return obj

def find_optimal_wbal(distance):
    opt_results = {}
    with open('optimal_power.json', 'r') as file:
        opt_results = json.load(file)
    index = int(np.argwhere(opt_results['distance'] >= distance)[0])
    return opt_results['w_bal'][index]
