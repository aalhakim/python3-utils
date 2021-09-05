#!python2

"""
Calculate error in resistor potential divider networks.
"""

RTOP = 10000.0
RBOT = 10000.0

VIN = 4.2
VGND = 0.00

VFB  = 0.430435  # Relevant for DC/DC feedback pins


#######################################################################
def pot_div_gain(rtop, rtop_tol, rbot, rbot_tol, gain):
    rtop_min = rtop * (1 - (rtop_tol/100.0))
    rtop_max = rtop * (1 + (rtop_tol/100.0))
    rbot_min = rbot * (1 - (rbot_tol/100.0))
    rbot_max = rbot * (1 + (rbot_tol/100.0))

    if gain == 'nom':
        return rbot_min / (rbot_min + rtop_min)
    elif gain == 'max':
        return rbot_max / (rbot_max + rtop_min)
    elif gain == 'min':
        return rbot_min / (rbot_min + rtop_max)


#######################################################################
min_gain = pot_div_gain(RTOP, 5, RBOT, 5, 'min')
max_gain = pot_div_gain(RTOP, 5, RBOT, 5, 'max')
nom_gain = pot_div_gain(RTOP, 5, RBOT, 5, 'nom')

print("VIN  = {} V".format(VIN))
print("RTOP = {} Ohms".format(RTOP))
print("RBOT = {} Ohms".format(RBOT))

print("\nRESISTOR TOLERANCE 5%\n------------------------")
print("  OUTPUT VOLTAGE for VIN=%0.02f" % VIN)
print("    MAX = %0.06f V" % (min_gain * VIN))
print("    NOM = %0.06f V" % (nom_gain * VIN))
print("    MIN = %0.06f V" % (max_gain * VIN))

print("\n  INPUT VOLTAGE for VFB=%0.02f" % VFB)
print("    MAX = %0.06f V" % ((1/min_gain)*VFB - ((1/min_gain)-1)*VGND))
print("    NOM = %0.06f V" % ((1/nom_gain)*VFB - ((1/nom_gain)-1)*VGND))
print("    MIN = %0.06f V" % ((1/max_gain)*VFB - ((1/max_gain)-1)*VGND))


#######################################################################
min_gain = pot_div_gain(RTOP, 1, RBOT, 1, 'min')
max_gain = pot_div_gain(RTOP, 1, RBOT, 1, 'max')
nom_gain = pot_div_gain(RTOP, 1, RBOT, 1, 'nom')

print("\n\nRESISTOR TOLERANCE 1%\n------------------------")
print("  OUTPUT VOLTAGE for VIN=%0.02f" % VIN)
print("    MAX = %0.06f V" % (min_gain * VIN))
print("    NOM = %0.06f V" % (nom_gain * VIN))
print("    MIN = %0.06f V" % (max_gain * VIN))

print("\n  INPUT VOLTAGE for VFB=%0.02f" % VFB)
print("    MAX = %0.06f V" % ((1/min_gain)*VFB - ((1/min_gain)-1)*VGND))
print("    NOM = %0.06f V" % ((1/nom_gain)*VFB - ((1/nom_gain)-1)*VGND))
print("    MIN = %0.06f V" % ((1/max_gain)*VFB - ((1/max_gain)-1)*VGND))


#######################################################################
min_gain = pot_div_gain(RTOP, 0.1, RBOT, 0.1, 'min')
max_gain = pot_div_gain(RTOP, 0.1, RBOT, 0.1, 'max')
nom_gain = pot_div_gain(RTOP, 0.1, RBOT, 0.1, 'nom')

print("\n\nRESISTOR TOLERANCE 0.1%\n------------------------")
print("  OUTPUT VOLTAGE for VIN=%0.02f" % VIN)
print("    MAX = %0.06f V" % (min_gain * VIN))
print("    NOM = %0.06f V" % (nom_gain * VIN))
print("    MIN = %0.06f V" % (max_gain * VIN))

print("\n  INPUT VOLTAGE for VFB=%0.02f" % VFB)
print("    MAX = %0.06f V" % ((1/min_gain)*VFB - ((1/min_gain)-1)*VGND))
print("    NOM = %0.06f V" % ((1/nom_gain)*VFB - ((1/nom_gain)-1)*VGND))
print("    MIN = %0.06f V" % ((1/max_gain)*VFB - ((1/max_gain)-1)*VGND))
