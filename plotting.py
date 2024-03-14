import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

def compare_power(power_data, time=None, legends=None, title=None):
    if time != None:
        for power in power_data:
            plt.plot(time, power)
    else:
        for power in power_data:
            plt.plot(power)
            
    plt.legend(legends)
    plt.xlabel("Time [s]")
    plt.ylabel("Power [W]")
    plt.ylim(0,500)
    plt.title(title)
    plt.show()

def plot_regression(power_points, time_points, fitted_ltw, params_ltw, fitted_lp, params_lp, fitted_nl2, 
                    params_nl2, fitted_nl3, params_nl3, fitted_nl4, params_nl4, val_power_points=None, val_time_points=None, retest_power=None, retest_time=None):
    time = np.arange(1,1200)
    power = np.arange(0,500)
    
    plt.subplot(2, 1 ,1)
    plt.plot(1/time, fitted_lp)
    plt.title("Linear-P")
    plt.xlabel("1/time [1/s]")
    plt.ylabel("Power [W]")
    text_lp = f'CP = {round(params_lp[1])}W\nW\' = {round(params_lp[0]/1000,2)}kJ'
    plt.text(0.8, 0.5, text_lp, ha='center', va='center', transform=plt.gca().transAxes, fontsize='large')
    for i in range(len(power_points)):
        plt.plot(1/time_points[i], power_points[i], marker="o", markersize=10, markeredgecolor="red", markerfacecolor="red")
    if val_power_points != None:
        for i in range(len(val_power_points)):
            plt.plot(1/val_time_points[i], val_power_points[i], marker="o", markersize=10, markeredgecolor="blue", markerfacecolor="blue")
    #plt.plot(1/retest_time, retest_power, marker="o", markersize=10, markeredgecolor="green", markerfacecolor="green")
    plt.xlim(0, 0.007)
    plt.ylim(0, 550)

    ax = plt.subplot(2,1,2)
    plt.plot(time, fitted_ltw)
    formatter = FuncFormatter(lambda x, pos: x/1000)
    ax.yaxis.set_major_formatter(formatter)
    plt.title("Linear-TW")
    plt.xlabel("Time [s]")
    plt.ylabel("Total work [kJ]")
    text_ltw = f'CP = {round(params_ltw[1])}W\nW\' = {round(params_ltw[0]/1000,2)}kJ'
    plt.text(0.8, 0.5, text_ltw, ha='center', va='center', transform=plt.gca().transAxes, fontsize='large')
    for i in range(len(power_points)):
        plt.plot(time_points[i], power_points[i]*time_points[i], marker="o", markersize=10, markeredgecolor="red", markerfacecolor="red")
    if val_power_points != None:
        for i in range(len(val_power_points)):
            plt.plot(val_time_points[i], val_power_points[i]*val_time_points[i], marker="o", markersize=10, markeredgecolor="blue", markerfacecolor="blue")
    #plt.plot(retest_time, retest_power*retest_time, marker="o", markersize=10, markeredgecolor="green", markerfacecolor="green")
    plt.xlim(0,1200)
    plt.ylim(0,400000)
    plt.subplots_adjust(hspace=0.7)
    plt.show()
    
    plt.plot(power, fitted_nl2)
    plt.plot(power, fitted_nl3)
    plt.plot(power, fitted_nl4)
    plt.xlabel("Power [W]")
    plt.ylabel("Time [s]")
    for i in range(len(power_points)):
        plt.plot(power_points[i], time_points[i], marker="o", markersize=10, markeredgecolor="red", markerfacecolor="red")
    if val_power_points != None:
        for i in range(len(val_power_points)):
            plt.plot(val_power_points[i], val_time_points[i], marker="o", markersize=10, markeredgecolor="blue", markerfacecolor="blue")
    #plt.plot(retest_power, retest_time, marker="o", markersize=10, markeredgecolor="green", markerfacecolor="green")
    plt.legend([f"Nonlinear-2: CP = {round(params_nl2[1])}W, W\' = {round(params_nl2[0]/1000,2)}kJ", 
                f"Nonlinear-3: CP = {round(params_nl3[1])}W, W\' = {round(params_nl3[0]/1000,2)}kJ, P_max = {round(params_nl3[2])}W", 
                f"Nonlinear-4: CP = {round(params_nl4[1])}W, W\' = {round(params_nl4[0]/1000,2)}kJ, P_max = {round(params_nl4[2])}W, tau = {round(params_nl4[3], 4)}"])
    plt.legend(["Nonlinear-2", "Nonlinear-3", "Nonlinear-4"])
    plt.title("The Nonlinear Models")
    plt.xlim(270,500)
    plt.ylim(0,1200)
    plt.show()