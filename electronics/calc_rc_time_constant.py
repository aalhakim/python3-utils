#!python3
"""
Calculate capacitor charge and discharge times using the RC time
constant method
"""

# Standard library imports
import sys
import math
import pathlib

# Add parent directory to sys.path to allow this script to import modules
# placed higher up in the directory hierarchy.
module_name = "python3-utils"
pkg_dir = __file__[0 : __file__.find(module_name) + len(module_name)]
sys.path.append(pkg_dir)


# Local library imports
from utils.eng_multipliers import *


###############################################################################
# --- User Inputs
###############################################################################

# Supply voltage, in voltage
V_SUP = 3.3  # Volts

# RC resistor and capacitor values
RES_OHMS = kilo(36.0)  # Ohms

CAP_FARADS = nano(100)  # Farads

# Write results to a CSV file for easy plotting.
EXPORT_TO_CSV = False
CSV_FILE_NAME = "rc_curves.csv"


###############################################################################
# --- Constants
###############################################################################

# The RC time constant
TAU = RES_OHMS * CAP_FARADS  # time constant

# A list of time (in seconds)
# fmt: off
TIME_CONSTANT_MULTIPLIERS = [
    0.001, 0.01, 0.1,
    0.2, 0.3, 0.4, 0.5, 0.7,
    1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0
]
# fmt: on

# Table formatting constants
COL_NAMES = ["TAU", "TIME", "VOLTAGE", "CURRENT", "RES POWER"]
HEADER = "| {: ^5s} | {: ^8s} | {: ^8s} | {: ^8s} | {: ^12s} |".format(*COL_NAMES)
SPACER = "-" * len(HEADER)


###############################################################################
# --- Functions
###############################################################################
def charge_voltage(vsup, tc_count):
    return vsup * (1 - math.exp(-1 * tc_count))


def discharge_voltage(vsup, tc_count):
    return vsup * (math.exp(-1 * tc_count))


def charge_current(vsup, tc_count, res):
    return (vsup / res) * math.exp(-1 * tc_count)


def discharge_current(vsup, tc_count, res):
    return (vsup / res) * math.exp(-1 * tc_count)


def print_data(type: str) -> None:
    """Print charge or discharge curve data to terminal (and file if enabled).

    Args:
        type (str): Indicate whether to generate charge or discharge curve data.
    """
    if type == "charge":
        vfunc = charge_voltage
        ifunc = charge_current
    elif type == "discharge":
        vfunc = discharge_voltage
        ifunc = discharge_current
    else:
        raise RuntimeError("Invalid print_data type: Must be 'charge' or 'discharge' only.")

    for tcm in TIME_CONSTANT_MULTIPLIERS:
        time = TAU * tcm
        voltage = vfunc(V_SUP, tcm)
        current = ifunc(V_SUP, tcm, RES_OHMS)
        power = current * current * RES_OHMS

        tstr = f"{time:2.2f} s"
        vstr = f"{voltage:3.2f} V"
        istr = f"{current:3.2f} A"
        pstr = f"{power:3.2f} W"

        # Output results to terminal
        print(f"  | {str(tcm): <5s} | {tstr: >8s} | {vstr: ^8s} | {istr: ^8s} | {pstr: ^12s} |")

        # Output results to file
        append_to_file(f"{str(tcm)},{time},{voltage},{current},{power}\n")


# Convenience functions to clean up main code.
def print_header():
    print(f"  {SPACER}")
    print(f"  {HEADER}")
    print(f"  {SPACER}")


def print_spacer():
    print(f"  {SPACER}")


# -----------------------------------------------------------------------------
csv_file = pathlib.Path(__file__).parent / CSV_FILE_NAME

if EXPORT_TO_CSV:
    with open(csv_file, "w") as wf:
        wf.write("")


def append_to_file(string):
    if EXPORT_TO_CSV:
        with open(csv_file, "a") as wf:
            wf.write(string)


###############################################################################
# --- Main Code
###############################################################################
if __name__ == "__main__":
    print()
    print(f"  Res = {RES_OHMS:.3f} Ohms, Cap = {CAP_FARADS * 1e6:.6f} micro-Farads")
    print(f"  Time Constant = {TAU:.4f} seconds")
    print()
    print(f"  CHARGING from 0.0V to {V_SUP:2.2f}V")

    append_to_file(f"Resistor,{RES_OHMS:.3f}, Ohms\n")
    append_to_file(f"Capacitor, {CAP_FARADS * 1e6:.6f}, micro-Farads\n")
    append_to_file(f"Time Constant, {TAU:.4f}, seconds\n")
    append_to_file(f"\nCharge from 0V to {V_SUP:2.2f}V\n")
    append_to_file("{},{},{},{},{}\n".format(*COL_NAMES))

    print_header()
    print_data("charge")
    print_spacer()

    # -------------------------------------------------------------------------
    # Calculate discharge data
    print("")
    print(f"  DISCHARGING FROM {V_SUP:2.2f} to 0.0V")

    append_to_file(f"\nDischarge from {V_SUP:2.2f} to 0V\n")
    append_to_file("{},{},{},{},{}\n".format(*COL_NAMES))

    print_header()
    print_data("discharge")
    print_spacer()
