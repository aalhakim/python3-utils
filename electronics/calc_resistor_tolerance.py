#!/usr/bin/env python3

"""
Calculate error in resistor potential divider networks.
"""

###############################################################################
# --- User Inputs
###############################################################################

# Top resistor value (in kOhms)
RTOP = 124.0

# Bottom resistor value (in kOhms)
RBOT = 40.2

# Input voltage (in Volts)
VIN = 6.8

# Ground reference voltage (in Volts), typically 0.0 V
VGND = 0.00

# Set to True to calculate VFB from VIN.
# Set to False to calculate VIN values from VFB
CALCULATE_VFB_FROM_VIN = False

# Feedback voltage level(s)
#  VFB_MIN/MAX are relevant for DC-DC converters where the feedback reference
#  has some error which may affect DC-DC regulation accuracy under some
# conditions.
VFB = 0.8
VFB_TOL = None

if VFB_TOL is not None:
    VFB_MIN = VFB - VFB_TOL  # Use value or None
    VFB_MAX = VFB + VFB_TOL  # Use value or None
else:
    VFB_MIN = None
    VFB_MAX = None


###############################################################################
# --- Functions
###############################################################################
def pot_div_gain(rtop, rtop_tol, rbot, rbot_tol, gain):
    rtop_min = rtop * (1 - (rtop_tol / 100.0))
    rtop_max = rtop * (1 + (rtop_tol / 100.0))
    rbot_min = rbot * (1 - (rbot_tol / 100.0))
    rbot_max = rbot * (1 + (rbot_tol / 100.0))

    if gain == "nom":
        return rbot_min / (rbot_min + rtop_min)
    elif gain == "max":
        return rbot_max / (rbot_max + rtop_min)
    elif gain == "min":
        return rbot_min / (rbot_min + rtop_max)


###############################################################################
# --- Main Code
###############################################################################
if __name__ == "__main__":
    print("  RTOP = {} Ohms".format(RTOP))
    print("  RBOT = {} Ohms".format(RBOT))

    vfb_string = "\n"
    if VFB_MIN is not None:
        vfb_string += f"  VFB_MIN = {VFB_MIN:0.03f} V\n"
    vfb_string += f"  VFB_NOM = {VFB:0.03f} V"
    if VFB_MAX is not None:
        vfb_string += f"\n  VFB_MAX = {VFB_MAX:0.03f} V"

    if CALCULATE_VFB_FROM_VIN:
        print("\n   VIN = {} V".format(VIN))
    else:
        print(vfb_string)

    if VFB_MIN is None:
        VFB_MIN = VFB

    if VFB_MAX is None:
        VFB_MAX = VFB

    # -------------------------------------------------------------------------
    for tolerance in [5, 1, 0.5, 0.1]:
        min_gain = pot_div_gain(RTOP, tolerance, RBOT, tolerance, "min")
        max_gain = pot_div_gain(RTOP, tolerance, RBOT, tolerance, "max")
        nom_gain = pot_div_gain(RTOP, tolerance, RBOT, tolerance, "nom")

        print(f"\n  RESISTOR TOLERANCE {tolerance}%\n ------------------------")
        if CALCULATE_VFB_FROM_VIN:
            print("    VFB_MAX = %0.06f V" % (max_gain * VIN))
            print("    VFB_NOM = %0.06f V" % (nom_gain * VIN))
            print("    VFB_MIN = %0.06f V" % (min_gain * VIN))

        else:
            print(
                "    VIN_MAX = %0.06f V" % ((1 / min_gain) * VFB_MAX - ((1 / min_gain) - 1) * VGND)
            )
            print("    VIN_NOM = %0.06f V" % ((1 / nom_gain) * VFB - ((1 / nom_gain) - 1) * VGND))
            print(
                "    VIN_MIN = %0.06f V" % ((1 / max_gain) * VFB_MIN - ((1 / max_gain) - 1) * VGND)
            )

    print()
