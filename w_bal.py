import math
import numpy as np

def get_tau_method(power, cp, tau_dynamic, tau_value):
    if tau_dynamic:
        tau_dynamic = [tau_w_prime_balance(power, cp, i) for i in range(len(power))]
        tau = lambda t: tau_dynamic[t]

    elif tau_value is None:
        static_tau = tau_w_prime_balance(power, cp)
        tau = lambda t: static_tau

    else:
        tau = lambda t: tau_value

    return tau


def get_bi_exp_tau_method(power, cp, tau_dynamic, tau_value, fast_component):
    if tau_dynamic:
        if fast_component:
            tau_dynamic = [tau_fc(power, cp, i) for i in range(len(power))]
            tau = lambda t: tau_dynamic[t]
        else:
            tau_dynamic = [tau_sc(power, cp, i) for i in range(len(power))]
            tau = lambda t: tau_dynamic[t]

    elif tau_value is None:
        if fast_component:
            static_tau = tau_fc(power, cp)
            tau = lambda t: static_tau
        else:
            static_tau = tau_sc(power, cp)
            tau = lambda t: static_tau

    else:
        tau = lambda t: tau_value

    return tau


def tau_w_prime_balance(power, cp, untill=None):
    if untill is None:
        untill = len(power)

    avg_power_below_cp = power[:untill][power[:untill] < cp].mean()
    if math.isnan(avg_power_below_cp):
        avg_power_below_cp = 0
    delta_cp = cp - avg_power_below_cp

    return 546 * math.e ** (-0.01 * delta_cp) + 316


def tau_fc(power, cp, untill = None):
    if untill is None:
        untill = len(power)

    avg_power_below_cp = power[:untill][power[:untill] < cp].mean()
    if math.isnan(avg_power_below_cp):
        avg_power_below_cp = 0
    d_cp = avg_power_below_cp/cp *100

    return 45 * math.e ** (-0.014 * d_cp) + 9999 * math.e ** (-0.811 * d_cp)


def tau_sc(power, cp, untill = None):
    if untill is None:
        untill = len(power)

    avg_power_below_cp = power[:untill][power[:untill] < cp].mean()
    if math.isnan(avg_power_below_cp):
        avg_power_below_cp = 0
    d_cp = avg_power_below_cp/cp *100

    return 9999* math.e ** (-0.098 * d_cp) + 429


def w_prime_balance_integral(power, cp, w_prime, tau_dynamic=False, tau_value=None, *args, **kwargs):
    w_prime_balance = []
    tau = get_tau_method(power, cp, tau_dynamic, tau_value)

    for t in range(len(power)):
        w_prime_exp_sum = 0

        for u, p in enumerate(power[: t + 1]):
            w_prime_exp = max(0, p - cp)
            w_prime_exp_sum += w_prime_exp * np.power(np.e, (u - t) / tau(t))

        w_prime_balance.append(w_prime - w_prime_exp_sum)

    return w_prime_balance


def w_prime_balance_ode(power, cp, w_prime):

    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -(cp - p)/w_prime)
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new

    return w_prime_balance


def w_prime_balance_bartram(power, cp, w_prime):

    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -1/(2287.2*(cp-p)**-0.688))
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new
    return w_prime_balance


# The functions for W'balance that use regression and fitted parameters
def w_prime_balance_bi_exp_regression(power, cp, w_prime, fc, sc):

    w_prime_balance = []
    FC_balance = []
    SC_balance = []
    FC_amp = 0.365*w_prime
    SC_amp = 0.635*w_prime
    tau_fc = get_bi_exp_tau_method(power, cp, True, None, fast_component=True)
    tau_sc = get_bi_exp_tau_method(power, cp, True, None, fast_component=False)

    for t in range(len(power)):
        w_prime_exp_sum = 0
        FC_exp_sum = 0
        SC_exp_sum = 0

        for u, p in enumerate(power[: t + 1]):
            w_prime_exp = max(0, p - cp)
            FC_exp_sum += w_prime_exp * (fc * np.power(np.e, (u - t) / tau_fc(t)))
            SC_exp_sum += w_prime_exp * (sc * np.power(np.e, (u - t) / tau_sc(t)))
        
        w_prime_exp_sum = FC_exp_sum + SC_exp_sum
        w_prime_balance.append(w_prime - w_prime_exp_sum)
        FC_balance.append(FC_amp-FC_exp_sum)
        SC_balance.append(SC_amp-SC_exp_sum)

    return w_prime_balance, FC_balance, SC_balance

def tau_regression(power, cp, a, b, c, untill=None):
    if untill is None:
        untill = len(power)

    avg_power_below_cp = power[:untill][power[:untill] < cp].mean()
    if math.isnan(avg_power_below_cp):
        avg_power_below_cp = 0
    delta_cp = cp - avg_power_below_cp

    return a * math.e ** (b * delta_cp) + c

def w_prime_balance_integral_regression(power, cp, w_prime, a, b, c):
    w_prime_balance = []
    tau_dyn = [tau_regression(power, cp, a, b, c) for i in range(len(power))]
    tau = lambda t: tau_dyn[t]

    for t in range(len(power)):
        w_prime_exp_sum = 0

        for u, p in enumerate(power[: t + 1]):
            w_prime_exp = max(0, p - cp)
            w_prime_exp_sum += w_prime_exp * np.power(np.e, (u - t) / tau(t))

        w_prime_balance.append(w_prime - w_prime_exp_sum)

    return w_prime_balance

def w_prime_balance_ode_regression(power, cp, w_prime, d, e):
    last = w_prime
    w_prime_balance = []

    for p in power:
        if p < cp:
            new = w_prime - (w_prime - last) * np.power(np.e, -1/(d*(cp-p)**e))
        else:
            new = last - (p - cp)

        w_prime_balance.append(new)
        last = new
    return w_prime_balance