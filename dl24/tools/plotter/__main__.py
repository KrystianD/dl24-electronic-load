import argparse
import csv
import datetime
import math

from matplotlib import ticker
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


def main():
    argparser = argparse.ArgumentParser()
    argparser.set_defaults(cmd=lambda: None, cmd_args=lambda x: [])
    argparser.add_argument('path', type=str, metavar="PATH")

    args = argparser.parse_args()

    csvfile = open(args.path, 'r', newline='')
    wr = csv.reader(csvfile)

    date_series = []
    voltage_series = []
    current_series = []
    energy_series = []
    charge_series = []

    is_24v = False

    energy_start = None
    charge_start = None
    energy_end = None
    charge_end = None

    first_date = None
    entries_i = iter(wr)
    next(entries_i)
    for entry in entries_i:
        dt = datetime.datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S")
        if first_date is None:
            first_date = dt

        time_sec = (dt - first_date).total_seconds() / 60 / 60
        date_series.append(time_sec)

        voltage = float(entry[1])
        current = float(entry[2])
        energy = float(entry[4])
        charge = float(entry[5])

        if voltage > 20:
            is_24v = True

        if energy_start is None:
            energy_start = energy
        if charge_start is None:
            charge_start = charge

        energy_end = energy
        charge_end = charge

        voltage_series.append(voltage)
        current_series.append(current)
        energy_series.append((energy - energy_start) / 1000)
        charge_series.append((charge - charge_start))

    v_scale_mult = 2 if is_24v else 1
    min_voltage = 9
    max_voltage = 14
    min_current = 0
    max_current = 20
    min_charge = 0
    max_charge = math.ceil((charge_end - charge_start) / 50) * 50
    min_energy = 0
    max_energy = math.ceil((energy_end - energy_start) / 1000) * 1

    fig, (ax1_current, ax2_energy) = plt.subplots(2, 1)
    fig.set_size_inches(8.5, 7)

    ax1_current.grid(True)
    ax1_current.set_xlabel("Time [h]", color='black')
    ax1_voltage = ax1_current.twinx()

    # Voltage
    ax1_voltage.plot(date_series, voltage_series, color='green')
    ax1_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%g V'))
    # ax1_voltage.yaxis.set_minor_formatter(ticker.FormatStrFormatter('%.1f V'))
    # ax1_voltage.yaxis.set_minor_locator(AutoMinorLocator())
    ax1_voltage.set_ylim([min_voltage * v_scale_mult, max_voltage * v_scale_mult])
    ax1_voltage.set_ylabel("Voltage", color='green')
    # ax1_voltage.tick_params(axis='y', labelcolor='green')

    # Current
    ax1_current.plot(date_series, current_series, color='red')
    ax1_current.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d A'))
    ax1_current.set_ylim([min_current, max_current])
    ax1_current.set_ylabel("Current", color='red')
    ax1_current.set_yticks(range(0, max_current + 1, 2))
    # ax1_current.tick_params(axis='y', labelcolor='red')

    ax2_energy.grid(True)
    ax2_charge = ax2_energy.twinx()

    # Energy
    ax2_energy.plot(date_series, energy_series, color='orange')
    ax2_energy.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
    ax2_energy.set_ylim([min_energy, max_energy])
    ax2_energy.set_ylabel("Energy [kWh]", color='orange')
    # ax2_energy.tick_params(axis='y', labelcolor='orange')

    # Charge
    ax2_charge.plot(date_series, charge_series, color='red')
    ax2_charge.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax2_charge.set_ylim([min_charge, max_charge])
    ax2_charge.set_ylabel("Charge [Ah]", color='red')
    # ax2_charge.tick_params(axis='y', labelcolor='red')

    plt.show()


main()
