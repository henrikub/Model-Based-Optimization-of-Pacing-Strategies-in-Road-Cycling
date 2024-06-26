import matplotlib.pyplot as plt
from utils.utils import normalized_power
import datetime
import numpy as np

def plot_optimization_results(sol, U, X, T, distance, elevation, params, opt_details, streamlit=False, baseline_activity = None, baseline_power = None):
    cp = params.get("cp")
    alpha = params.get("alpha")
    optimal_power = sol.value(U)
    optimal_time = sol.value(T)
    pos = sol.value(X[0,:])
    velocity = sol.value(X[1,:])
    w_bal = sol.value(X[2,:])

    max_power = alpha*w_bal + cp
    fig, ax = plt.subplots(3,1, figsize=(15,10))

    ax[0].set_title(f"The optimal time is {str(datetime.timedelta(seconds=round(optimal_time)))}")
    ax[0].set_ylabel("Power [W]")
    ax[0].set_ylim(0,max(max_power)+50)
    ax[0].plot(pos, max_power, zorder=3)
    ax[0].plot(pos, optimal_power, zorder=4)
    ax[0].plot(round(pos[-1])*[cp], color='tab:gray', linestyle='dashed', zorder=2)
    if baseline_activity != None:
        ax[0].plot(baseline_activity.distance, baseline_power)
        ax[0].legend(["Maximum attainable power", "Optimal power output", "CP", "Intuitive pacing power output"], loc='upper right')
    else:
        ax[0].legend(["Maximum attainable power", "Optimal power output", "CP"], loc='upper right')
    ax1_twin = ax[0].twinx()
    ax1_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax1_twin.plot(distance, elevation, color='tab:red', zorder=1)
    ax1_twin.tick_params(axis='y', labelcolor='tab:red')
    ax1_twin.legend(["Elevation Profile"], loc='lower left')

    ax[1].set_ylabel("Velocity [m/s]")
    ax[1].set_ylim(0,20)
    ax[1].plot(pos, velocity, zorder=2)
    ax[1].legend(["Velocity"], loc='upper right')
    ax2_twin = ax[1].twinx()
    ax2_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax2_twin.plot(distance, elevation, color='tab:red', zorder=1)
    ax2_twin.tick_params(axis='y', labelcolor='tab:red')
    ax2_twin.legend(["Elevation Profile"], loc='lower left')

    ax[2].set_ylabel("W'balance [J]")
    ax[2].set_xlabel("Position [m]")
    ax[2].set_ylim(0, max(w_bal) + 1000)
    ax[2].plot(pos, w_bal, zorder=2)
    if opt_details.get("negative_split"):
        w_bal_start = opt_details.get("w_bal_start")
        w_bal_end = opt_details.get("w_bal_end")
        x = np.linspace(0, optimal_time, len(pos))
        bound =  (w_bal_end-w_bal_start)/optimal_time *x + w_bal_start
        ax[2].plot(pos, bound)
        ax[2].legend(["W'balance", "Lower bound on W'balance"], loc='upper right')
    else:
        ax[2].legend(["W'balance"], loc='upper right')
    ax3_twin = ax[2].twinx()
    ax3_twin.set_ylabel('Elevation [m]', color='tab:red')
    ax3_twin.plot(distance, elevation, color='tab:red', zorder=1)
    ax3_twin.tick_params(axis='y', labelcolor='tab:red')
    ax3_twin.legend(["Elevation Profile"], loc='lower left')

    ax[0].set_zorder(ax1_twin.get_zorder()+1)
    ax[1].set_zorder(ax2_twin.get_zorder()+1)
    ax[2].set_zorder(ax3_twin.get_zorder()+1)
    ax[0].patch.set_visible(False)
    ax[1].patch.set_visible(False)
    ax[2].patch.set_visible(False)

    plt.show()