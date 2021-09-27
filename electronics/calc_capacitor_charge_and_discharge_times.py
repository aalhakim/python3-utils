#!python3
"""
Calculate capacitor charge and discharge times using the RC time
constant method
"""
import math


########################################################################
def micro(num):
    return num*1e-6

def milli(num):
    return num*1e-3

def kilo(num):
    return num*1e+3

def mega(num):
    return num*1e+6

def charge_voltage(vsup, tc_count):
    return vsup * (1 - math.exp(-1*tc_count))

def discharge_voltage(vsup, tc_count):
    return vsup * (math.exp(-1*tc_count))

def charge_current(vsup, tc_count, res):
    return (vsup/res) * math.exp(-1*tc_count)

def discharge_current(vsup, tc_count, res):
    return (vsup/res) * math.exp(-1*tc_count)


########################################################################
# Create (or clear) a file to write the results to for easy graphing
with open("./rc_curves.csv", "w") as wf:
    wf.write("")

def append_to_file(string):
    with open("./rc_curves.csv", "a") as wf:
        wf.write(string)


########################################################################

vsup = 5.0  # Volts

res = mega(1.5)  # Ohms
cap = micro(2 * 4.7)  # Farads

tau = res*cap  # time constant


print()
print("  Res = {:.3f} Ohms, Cap = {:.6f} micro-Farads".format(res, cap*1e+6))
print("  Time Constant = {:.4f} seconds".format(tau))

append_to_file("Resistor,{:.3f}, Ohms\n".format(res))
append_to_file("Capacitor, {:.6f}, micro-Farads\n".format(cap*1e+6))
append_to_file("Time Constant, {:.4f}\n".format(tau))


print()
print("  CHARGING from 0.0V to {:2.2f}V".format(vsup))
append_to_file("\nCharge from 0V to {:2.2f}V\n".format(vsup))
append_to_file("{},{},{},{},{}\n".format("RC", "TIME", "VOLTAGE", "CURRENT", "RES POWER"))
title = "| {: ^5s} | {: ^8s} | {: ^8s} | {: ^8s} | {: ^12s} |".format("RC", "TIME", "VOLTAGE", "CURRENT", "RES POWER")
print("  {}".format("-"*len(title)))
print("  {}".format(title))
print("  {}".format("-"*len(title)))


# Calculate metrics at different time constants
tc_counts = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0]
for tc_count in tc_counts:
    time = str("{:2.2f} s".format(tau*tc_count))
    voltage = str("{:3.2f} V".format(charge_voltage(vsup, tc_count)))
    current_ = charge_current(vsup, tc_count, res)
    current = str("{:3.2f} A".format(current_))
    power = str("{:3.2f} W".format(current_ * current_ * res))

    # Output results
    print("  | {: <5s} | {: >8s} | {: ^8s} | {: ^8s} | {: ^12s} |".format(str(tc_count), time, voltage, current, power))
    append_to_file("{},{},{},{},{}\n".format(str(tc_count), time[:-2], voltage[:-2], current[:-2], power[:-2]))
print("  {}".format("-"*len(title)))


print("")
print("  DISCHARGING FROM {:2.2f} to 0.0V".format(vsup))
append_to_file("\nDischarge from {:2.2f} to 0V\n".format(vsup))
append_to_file("{},{},{},{},{}\n".format("RC", "TIME", "VOLTAGE", "CURRENT", "RES POWER"))
print("  {}".format("-"*len(title)))
print("  {}".format(title))
print("  {}".format("-"*len(title)))

# Calculate metrics at different time constants
tc_counts = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0]
for tc_count in tc_counts:
    time = str("{:2.2f} s".format(tau*tc_count))
    voltage = str("{:3.2f} V".format(discharge_voltage(vsup, tc_count)))
    current_ = discharge_current(vsup, tc_count, res)
    current = str("{:3.2f} A".format(current_))
    power = str("{:3.2f} W".format(current_ * current_ * res))

    # Output results
    print("  | {: <5s} | {: >8s} | {: ^8s} | {: ^8s} | {: ^12s} |".format(str(tc_count), time, voltage, current, power))
    append_to_file("{},{},{},{},{}\n".format(str(tc_count), time[:-2], voltage[:-2], current[:-2], power[:-2]))
print("  {}".format("-"*len(title)))
