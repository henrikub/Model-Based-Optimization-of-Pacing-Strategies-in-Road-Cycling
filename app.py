import streamlit as st
import subprocess
import optimization.optimal_pacing as opt
import activity_reader_tcx.activity_reader as act
import utils.utils as utils
import matplotlib.pyplot as plt
from plotting.optimization_plots import *
import casadi as ca
from simulator.simulator import *

st.title("Optimization settings")

cp = st.number_input('CP', value=265)
w_prime = st.number_input("W'", value=26630, min_value=1)
route_name = st.selectbox('Select route', ['Mech Isle Loop', 'Hilly Route', 'Downtown Titans', 'Richmond Rollercoaster', 'Greater London Flat'])
integration_method = st.selectbox('Select integration method', ['Euler', 'RK4', 'Midpoint'])

route_filename = {
    'Mech Isle Loop': 'Mech_isle_loop_time_trial.tcx',
    'Hilly Route': 'Hilly_route.tcx',
    'Downtown Titans': 'Downtown_titans.tcx',
    'Richmond Rollercoaster': 'Richmond_rollercoaster.tcx',
    'Greater London Flat': 'Greater_london_flat_race.tcx'
    
}
end_of_route = {
    'Mech Isle Loop': 4170,
    'Hilly Route': 9600,
    'Downtown Titans': 24600,
    'Richmond Rollercoaster': 17100,
    'Greater London Flat': 17500
}


activity = act.ActivityReader(route_filename[route_name])
activity.remove_period_after(end_of_route[route_name])

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





if st.button("Run optimization"):
    message = st.text("This could take several minutes..")
    N = round(activity.distance[-1]/5)
    timegrid = np.linspace(0,round(activity.distance[-1]/1000*150), N)

    X, power, t_grid = create_initialization(timegrid, [activity.distance[0], activity.speed[0], params.get('w_prime')], activity.distance, activity.elevation, params)
    
    optimization_opts = {
        "N": len(t_grid)-1,
        "time_initial_guess": t_grid[-1],
        "smooth_power_constraint": True,
        "w_bal_model": "ODE",
        "integration_method": integration_method,
        "solver": "ipopt"
    }
    
    initialization = {
        'pos_init': X[0],
        'speed_init': X[1],
        'w_bal_init': X[2],
        'power_init': power,
        'time_init': timegrid[-1],
    }
    sol, opti, T, U, X = opt.solve_opt_warmstart_sim(activity.distance, activity.elevation, params, optimization_opts, initialization)
    stats = sol.stats()
    opt_details = {
        "N": N,
        "w_bal_model": optimization_opts.get("w_bal_model"),
        "integration_method": optimization_opts.get("integration_method"),
        "time_init_guess": optimization_opts.get("time_initial_guess"),
        "iterations": stats['iter_count'],
        "opt_time": stats['t_wall_total']
    }

    message.empty()

    fig2 = plot_optimization_results(sol, U, X, T, activity.distance, activity.elevation, params, opt_details, True)
    st.header("Optimization Results")
    st.pyplot(fig2)

    if st.button("Save result"):
        t_grid = ca.linspace(0, sol.value(T), N+1)
        try: utils.write_json(sol.value(U), t_grid.full().flatten(), sol.value(X[0,:]))
        except:
            print("error")
