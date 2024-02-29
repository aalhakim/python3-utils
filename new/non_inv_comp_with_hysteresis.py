"""
Analysis of non-inverting comparator with hysteresis.

https://www.ti.com/lit/an/sboa313a/sboa313a.pdf

"""

from math import sqrt

# Feedback Loop
R1 = 100e3
R2 = 1000e3
R3 = 10e3

# Reference Circuit
R4 = 100e3
R5 = 100e3

# Hysteresis thresholds
VL = 3.2
VH = 3.8

# Supply
VSUP = 5


def calc_ideal_r1(r2, r3, vsup, vl, vh):
    """
    Based on solving quadratic equation for R1

    Where ax^2 +bx + c = 0

        a = VSUP
        b = VSUP*R2 + VL*(R2+R3) - VH*R2
        c = (VL-VH)(R2*R3 + R2^2)

    Then r1 = [-b + sqrt(b^2 - 4ac)] / 2a
    """

    a = vsup
    b = (vsup * r2) + (vl * (r2 + r3)) - (vh * r2)
    c = (vl - vh) * ((r2 * r3) + (r2 * r2))

    # Solution is obtained for [-b + sqrt(b^2 - 4ac)] / 2a
    return (-b + sqrt((b * b) - (4 * a * c))) / (2 * a)


def calc_ideal_r4(r5, vsup, vth):
    """
    This assumes the reference potential divider if fed from the vsup rail.

    r4 = r5 * (vs - vth) / vth
    """
    return r5 * (vsup - vth) / vth


def calc_vth_for_vin_eq_vsup(r1, r2, vh):
    """
    Based on the equation when VIN=VSUP, VOUT=GND

    vth = (vh * r2) / (r1 + r2)
    """
    return (vh * r2) / (r1 + r2)


def calc_vth_for_vin_eq_gnd(r1, r2, r3, vl, vsup):
    """
    Based on the equation when VIN=VSUP, VOUT=GND

    vth = [ vl*(r2+r3) + vsup*r1 ] / (r1 + r2 + r3)
    """
    return (vl * (r2 + r3) + (vsup * r1)) / (r1 + r2 + r3)


def calc_vth_actual(r4, r5, vsup):
    return vsup * r5 / (r4 + r5)


def calc_low_threshold(r1, r2, r3, vth, vsup):
    return (vth * (r1 + r2 + r3) - vsup * r1) / (r1 + r2)


def calc_high_threshold(r1, r2, vth):
    return vth * (r1 + r2) / r2


###############################################################################

print(f" R1 (IDEAL) = {calc_ideal_r1(R2, R3, VSUP, VL, VH) / 1000:.2f} kΩ")

vth = calc_vth_for_vin_eq_vsup(R1, R2, VH)
print(f" R4 (IDEAL) = {calc_ideal_r4(R5, VSUP, vth) / 1000:.2f} kΩ")

vth_act = calc_vth_actual(R4, R5, VSUP)
print()
print(f" VREF = {vth_act:.2f} V")
print(f" VL = {calc_low_threshold(R1, R2, R3, vth_act, VSUP):.2f} V")
print(f" VH = {calc_high_threshold(R1, R2, vth_act):.2f} V")

print()
# print(calc_vth_for_vin_eq_vsup(R1, R2, VH))
# print(calc_vth_for_vin_eq_gnd(R1, R2, R3, VL, VSUP))
