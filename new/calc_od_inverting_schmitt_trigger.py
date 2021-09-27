"""
Calculations for a Schmitt Trigger using a comparator with
an Open-Drain output.


"""

def pot_div(vin, rtop, rbot):
    return vin*rbot/(rtop+rbot)

def reverse_pot_div(vref, rtop, rbot):
    return vref*(rtop+rbot)/rbot

def noninv_schmitt_vminus(vin, vout, r1, r2, r3):
    num1 = vin * r2 * r3
    num2 = vout * r1 * r2
    den1 = r1*r2 + r2*r3 + r1*r3
    return (num1 + num2) / den1

def noninv_schmitt_vinput(vplus, vout, r1, r2, r3):
    num1 = vplus*(r1*r2 + r2*r3 + r1*r3)
    num2 = vout * r1 * r2
    den1 = r2 * r3
    return (num1 - num2) / den1

def noninv_schmitt_r_feedback(vout_hi, vout_lo, vref, vdd, r4):
    """
    Calculate the value of the positive feedback resistor from
    KCL analysis at the vout node of the non-inverting, open-drain
    comparator with hysteresis circuit.

    General Equation
    ================
    R3 = R4 * (Vref - Vout) / (Vout - Vdd)

    """
    for vout in [vout_lo, vout_hi]:
        print(r4)
        print((vref - vout))
        print((vout - vdd))
        print(r4 * (vref - vout) / (vout - vdd))

########################################################################
# Potential divider resistors for input voltage
r1 = 910.0
r2 = 51.0

# The output pull-up resistor
r4 = 4.7

# The comparator power supply level
vdd = 3.3

vref = pot_div(10.8, r1, r2)
print("  VREF = {:2.4f}".format(vref))

R3_OVERRIDE = True
r3_selected = 200000.0


# Input voltage turn off/on levels
vin_lo = 10.5
vin_hi = 10.8

# Comparator output levels
vout_lo = 0.0
vout_hi = 3.3

vplus_lo = pot_div(vin_lo, r1, r2)
vplus_hi = pot_div(vin_hi, r1, r2)


r3_num = vref * r1 * r2
r3_den = (vin_lo*r2) + vref*(r1 + r2)
r3 = r3_num/r3_den
print(r3)

# if R3_OVERRIDE:
#     r3 = r3_selected
# else:
#     r3 = r1*(vout_hi-vout_lo)/(vplus_hi-vplus_lo)

# print("  R1 = {:3.2f}".format(r1))
# print("  R2 = {:3.2f}".format(r2))
# print("  R3 = {:3.2f}".format(r3))


# vplus_hilo = noninv_schmitt_vminus(vin_hi, vout_lo, r1, r2, r3)
# vplus_hihi = noninv_schmitt_vminus(vin_hi, vout_hi, r1, r2, r3)
# print()
# print("  VREF1 = {:2.4f}".format(vplus_hilo))
# print("  VREF2 = {:2.4f}".format(vplus_hihi))

# vplus_lohi = noninv_schmitt_vminus(vin_lo, vout_hi, r1, r2, r3)
# vplus_lolo = noninv_schmitt_vminus(vin_lo, vout_lo, r1, r2, r3)
# print()
# print("  VREF1 = {:2.4f}".format(vplus_lohi))
# print("  VREF2 = {:2.4f}".format(vplus_lolo))

# print()
# print("  VIN_LO = {:2.4f}".format(noninv_schmitt_vinput(vplus_lo, vout_hi, r1, r2, r3)))
# print("  VIN_HI = {:2.4f}".format(noninv_schmitt_vinput(vplus_hi, vout_lo, r1, r2, r3)))


## INCORRECT CALCULATIONS
# def inv_schmitt_vin_threshold(r1, r2, r3, vref, vout):
#     num1 = vref*(r1*r2 + r2*r3 + r1*r3)
#     num2 = vout*r1*r2
#     den1 = r2*r3
#     return (num1-num2)/den1

# def inv_schmitt_od_output(r3, r4, vpu, vminus, enabled):
#     return enabled * (vpu*r3 + vminus*r4) / (r3 + r4)

# def inv_schmitt_input_minus(r1, r2, r3, vin, vout):
#     num1 = vin*r2*r3
#     num2 = vout*r1*r2
#     den1 = r1*r2 + r2*r3 + r1*r3
#     return (num1-num2)/den1

# ########################################################################
# # The input voltage potential divider resistors
# r1 = 910.0
# r2 = 51.0

# # The comparator feedback resistor
# r3 = 9100.0

# # The output pull-up resistor
# r4 = 4.7

# # The op-amp supply voltage
# vdd = 3.3

# # Op-amp input offset voltage
# vio = 0.002 # V

# # The reference voltage potential divider resistors
# r5 = 62.0 # top
# r6 = 13.0  # bottom

# # The comparator high and low possible output values.
# vout_hi = vdd
# vout_lo = 0.0

# # The maximum expected supply voltage
# vin_max = 60

# ########################################################################
# vref = pot_div(vdd, r5, r6)
# vminus_max = inv_schmitt_input_minus(r1, r2, r3, vin_max, vout_hi)
# vth_nom = reverse_pot_div(vref, r1, r2)
# print()
# print("  VIN_MAX = {:.1f} V --> Vth = {:.3f} V".format(vin_max, vminus_max))
# print("  VREF = {:.4f} V --> Vth = {:.3f} V".format(vref+vio, vth_nom))

# for i in range(100):
#     vin_lo = inv_schmitt_vin_threshold(r1, r2, r3, vref=vref+vio, vout=vout_hi)
#     print(vin_lo, end=" ")
#     vminus = inv_schmitt_input_minus(r1, r2, r3, vin=vin_lo, vout=vout_hi)
#     print(vminus, end=" ")
#     vout_hi = inv_schmitt_od_output(r3, r4, vpu=vdd, vminus=vminus, enabled=vminus>vref+vio)
#     print(vout_hi)

# print()
# for i in range(100):
#     vin_hi = inv_schmitt_vin_threshold(r1, r2, r3, vref=vref+vio, vout=vout_lo)
#     print(vin_hi, end=" ")
#     vminus = inv_schmitt_input_minus(r1, r2, r3, vin=vin_hi, vout=vout_lo)
#     print(vminus, end=" ")
#     vout_lo = inv_schmitt_od_output(r3, r4, vpu=vdd, vminus=vminus, enabled=vminus>vref+vio)
#     print(vout_lo)

# #vin_lo = inv_schmitt_vin_threshold(r1, r2, r3, vref+vio, vout_hi)
# #vin_hi = inv_schmitt_vin_threshold(r1, r2, r3, vref+vio, vout_lo)

# print()
# print("  VOUT = 3.3V when VIN > {:.2f}".format(vin_hi))
# print("  VOUT = 0.0V when VIN < {:.2f}".format(vin_lo))
