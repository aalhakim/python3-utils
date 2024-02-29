#!/usr/bin/env python3

"""
Calculate error in resistor potential divider networks.
"""


###############################################################################
# --- User Inputs
###############################################################################

# Top resistor value (in kOhms)
RTOP = 150.0

# Bottom resistor value (in kOhms)
RBOT = 36.0

# Input voltage (in Volts)
VIN = 3.3

# Ground reference voltage (in Volts), typically 0.0 V
VGND = 0.00

# Set to True to calculate VFB from VIN.
# Set to False to calculate VIN values from VFB
CALCULATE_VFB_FROM_VIN = True

# Feedback voltage level(s)
#  VFB_MIN/MAX are relevant for DC-DC converters where the feedback reference
#  has some error which may affect DC-DC regulation accuracy under some
# conditions.
VFB = 0.6
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
    print(f"  RTOP = {RTOP} Ohms")
    print(f"  RBOT = {RBOT} Ohms")

    vfb_string = "\n"
    if VFB_MIN is not None:
        vfb_string += f"  VFB_MIN = {round(VFB_MIN, 3)} V\n"
    vfb_string += f"  VFB_NOM = {round(VFB, 3)} V"
    if VFB_MAX is not None:
        vfb_string += f"\n  VFB_MAX = {round(VFB_MAX, 3)} V"

    if CALCULATE_VFB_FROM_VIN:
        print(f"\n   VIN = {VIN} V")
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
            print(f"    VFB_MAX = {round(max_gain * VIN, 4)} V")
            print(f"    VFB_NOM = {round(nom_gain * VIN, 4)} V")
            print(f"    VFB_MIN = {round(min_gain * VIN, 4)} V")

        else:
            vin_max = (1 / min_gain) * VFB_MAX - ((1 / min_gain) - 1) * VGND
            vin_nom = (1 / nom_gain) * VFB - ((1 / nom_gain) - 1) * VGND
            vin_min = (1 / max_gain) * VFB_MIN - ((1 / max_gain) - 1) * VGND
            print(f"    VIN_MAX = {round(vin_max, 4)} V")
            print(f"    VIN_NOM = {round(vin_nom, 4)} V")
            print(f"    VIN_MIN = {round(vin_min, 4)} V")

    print()
