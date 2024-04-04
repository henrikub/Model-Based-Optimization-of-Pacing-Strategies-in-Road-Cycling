import streamlit as st
import subprocess
import optimization.optimal_pacing as opt
import activity_reader_tcx.activity_reader as act
import utils.utils as utils
import matplotlib.pyplot as plt
from plotting.optimization_plots import *
import casadi as ca

st.title("Optimization settings")

cp = st.number_input('CP', value=265)
w_prime = st.number_input("W'", value=26630, min_value=1)
route_name = st.selectbox('Select route', ['Mech Isle Loop', 'Hilly Route', 'Downtown Titans'])
integration_method = st.selectbox('Select integration method', ['Euler', 'RK4', 'Midpoint'])

route_filename = {
    'Mech Isle Loop': 'Mech_isle_loop_time_trial.tcx',
    'Hilly Route': 'Hilly_route.tcx',
    'Downtown Titans': 'Downtown_titans.tcx'
}
end_of_route = {
    'Mech Isle Loop': 4170,
    'Hilly Route': 9600,
    'Downtown Titans': 24600
}

def run_main_func(path):
    result = subprocess.run(['python', path], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


activity = act.ActivityReader(route_filename[route_name])
activity.remove_period_after(end_of_route[route_name])

distance_simplified, elevation_simplified = utils.simplify_track(activity.distance, activity.elevation, 4)

# Params
params = {
    'mass_rider': 78,
    'mass_bike': 8,
    'g': 9.81,
    'mu': 0.004,
    'b0': 0.091,
    'b1': 0.0087,
    'Iw': 0.14,
    'r': 0.33,
    'Cd': 0.7,
    'rho': 1.2,
    'A': 0.4,
    'eta': 1,
    'w_prime': w_prime,
    'cp': cp,
    'alpha': 0.03,
    'alpha_c': 0.01,
    'c_max': 150,
    'c': 80
}

time_initial_guess = round(activity.distance[-1]/1000*120)
N = round(activity.distance[-1]/10)

optimization_opts = {
    "N": N,
    "time_initial_guess": time_initial_guess,
    "power_initial_guess": params.get('cp'),
    "smooth_power_constraint": True,
    "w_bal_model": "ODE",
    "integration_method": integration_method,
    "solver": "ipopt"
}
init_sol = 0
if st.button("Run optimization"):
    init_sol, opti, T, U, X = opt.solve_opt(distance_simplified, elevation_simplified, params, optimization_opts)
    init_stats = init_sol.stats()
    opt_details = {
        "N": N,
        "w_bal_model": optimization_opts.get("w_bal_model"),
        "integration_method": optimization_opts.get("integration_method"),
        "time_init_guess": optimization_opts.get("time_initial_guess"),
        "iterations": init_stats['iter_count'],
        "opt_time": init_stats['t_wall_total']
    }
    fig1 = plot_optimization_results(init_sol, U, X, T, distance_simplified, elevation_simplified, params, opt_details, True)
    st.header("Initial Optimization")
    st.pyplot(fig1)
    initialization = {
    'pos_init': init_sol.value(X[0,:]),
    'speed_init': init_sol.value(X[1,:]),
    'w_bal_init': init_sol.value(X[2,:]),
    'power_init': init_sol.value(U),
    'time_init': init_sol.value(T)
    }

    sol, opti, T, U, X = opt.solve_opt_warmstart(activity.distance, activity.elevation, params, optimization_opts, initialization)
    stats = sol.stats()
    opt_details["iterations"] = stats['iter_count']
    opt_details["opt_time"] = stats['t_wall_total']
    fig2 = plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation, params, opt_details, True)
    st.header("Full optimization")
    st.pyplot(fig2)

    if st.button("Save result"):
        t_grid = ca.linspace(0, sol.value(T), N+1)
        try: utils.write_json(sol.value(U), t_grid.full().flatten(), sol.value(X[0,:]))
        except:
            print("error")


# if st.button('Run Optimization'):
#     output = run_main_func('main.py')
#     st.text_area("output:", value=output, height=200, max_chars=None)