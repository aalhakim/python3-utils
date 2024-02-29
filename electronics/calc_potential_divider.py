#!/usr/bin/env python3

"""
Suggest E24/E48 resistor values for a potential divider circuit. Provides VOUT
for a given VIN or VIN for a given VOUT (useful for DC-DC converter feedback
circuits).
"""

# Add parent directory to sys.path to allow this script to import all local modules.
if __name__ == "__main__":
    import sys

    module_name = "python3-utils"
    pkg_dir = __file__[0 : __file__.find(module_name) + len(module_name)]
    sys.path.append(pkg_dir)


# Local library imports
from utils.resistors import E12, E24, E48, E96, ALL


###############################################################################
# --- User Inputs
###############################################################################

# The input voltage to the potential divider
VSRC = 3.3  # V

# The desired output voltage from the potential divider.
VREF = 0.6  # V


###############################################################################
# --- Functions
###############################################################################
def list_multiply(list1, list2):
    """
    Return a list containing the results of multiplying every value in
    list1 with every value in list 2.
    """
    product = []
    for y in list2:
        for x in list1:
            product.append(x * y)

    return product


MULTIPLIER = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]

E12_SET = list_multiply(E12, MULTIPLIER)
E24_SET = list_multiply(E24, MULTIPLIER)
E48_SET = list_multiply(E48, MULTIPLIER)
E96_SET = list_multiply(E96, MULTIPLIER)
FULL_SET = list(set(E12_SET + E24_SET + E48_SET + E96_SET))


def calculate_rtop_e24(vsrc, vref, error_target=10):
    # rtop = rbot*(vsrc - vref) / vref
    success = False
    for rbot in E24:
        rtop = float(rbot) * (vsrc - vref) / vref
        for value in E24_SET:
            error = abs(rtop - value)
            if error <= error_target:
                _vout = calculate_vout(vref, value, rbot)
                _vref = calculate_vref(vsrc, value, rbot)
                _rbot = "{: ^6.1f}".format(rbot)
                _rtop = "{: ^6.1f}".format(value)
                print(
                    " | {: ^5d} | {: ^8s} | {: ^8s} | {: ^.3f}V  OR  {: ^.3f}V |".format(
                        error_target, _rtop, _rbot, _vref, _vout
                    )
                )
                success = True

    return success


def calculate_rtop_e96(vsrc, vref, error_target=10):
    # rtop = rbot*(vsrc - vref) / vref
    success = False
    for rbot in ALL:
        rtop = float(rbot) * (vsrc - vref) / vref
        for value in FULL_SET:
            error = abs(rtop - value)
            if error <= error_target:
                _vout = calculate_vout(vref, value, rbot)
                _vref = calculate_vref(vsrc, value, rbot)
                _rbot = "{: ^6.1f}".format(rbot)
                _rtop = "{: ^6.1f}".format(value)
                print(
                    " | {: ^5d} | {: ^8s} | {: ^8s} | {: ^.3f}V  OR  {: ^.3f}V |".format(
                        error_target, _rtop, _rbot, _vref, _vout
                    )
                )
                success = True

    return success


def calculate_rbot(vsrc, vref, series=E24):
    # rbot = vref*rtop / (vsrc - vref)
    for rtop in series:
        rbot = vsrc * float(rtop) / (vsrc - vref)
        print(rbot, rtop)


def calculate_vout(vref, rtop, rbot):
    # vsrc = vref*(rbot + rtop) / rbot
    return vref * (rbot + rtop) / rbot


def calculate_vref(vsrc, rtop, rbot):
    # vref = vsrc*rbot / (rbot + rtop)
    return vsrc * rbot / (rbot + rtop)


def print_table_divider():
    print(" |-{0:-^5s}-|-{0:-^8s}---{0:-^8s}-|--{0:-^7s}----{0:-^7s}-|".format("-"))


def print_table_header():
    headings = ["ERR", "RTOP", "RBOT", "VREF", "VOUT"]
    print_table_divider()
    print(" | {: ^5s} | {: ^8s} | {: ^8s} |  {:^7s} |  {:^7s} |".format(*headings))
    print_table_divider()


###############################################################################
# --- Main Code
###############################################################################
if __name__ == "__main__":

    print("\nE24 VALUES ONLY")
    print_table_header()
    success = False
    error_target = 0
    error_max = 0
    while not success:  # error_target <= error_max:
        success = calculate_rtop_e24(VSRC, VREF, error_target)
        error_target += 1
    print_table_divider()

    # -------------------------------------------------------------------------
    print("\nE24 and E96 VALUES")
    print_table_header()
    success = False
    error_target = 0
    error_max = 1
    while error_target <= error_max:
        success = calculate_rtop_e96(VSRC, VREF, error_target)
        error_target += 1
    print_table_divider()
