"""
Bidirectional Flyback Converter Calculations.
"""

# Add parent directory to sys.path to allow this script to import local modules.
if __name__ == "__main__":
    import sys

    module_name = "python3-utils"
    pkg_dir = __file__[0 : __file__.find(module_name) + len(module_name)]
    sys.path.append(pkg_dir)

# Local library imports
from utils.flyback import *


###############################################################################
# Modes
class FlybackConfig:
    LEFT_TO_RIGHT = "LEFT -> RIGHT"
    RIGHT_TO_LEFT = "RIGHT -> LEFT"


MODE = FlybackConfig.RIGHT_TO_LEFT

INCLUDE_TOLERANCE = True


###############################################################################
# Functions
kMinDiodeConductionTimeSecs = 700e-9
kMinCurrentSenseValueVolts = 33e-3
kMaxCurrentSenseValueVolts = 160e-3


def mp6005_minimum_inductance_H(vsec, npri, nsec, rsense):
    """Calculate minimum inductance requirement based on output diode
    conduction time requirement. See equation 12.
    """
    iin = rsense / kMinCurrentSenseValueVolts
    return vsec * (npri / nsec) * kMinDiodeConductionTimeSecs * iin


def mp6005_max_sense_resistor_full_scale_ohms(ipri_peak):
    """Calculate max sense resistor limit based sense voltage max limit.

    See equation 7 of MP6005 datasheet.
    """
    return 0.8 * kMaxCurrentSenseValueVolts / ipri_peak


def mp6005_max_sense_resistor_tcon_ohms(vsec, lpri, npri, nsec):
    """Calculate minimum sense resistor limit.

    See equation 12 of MP6005 datasheet.
    """
    return lpri * (nsec / npri) * kMinCurrentSenseValueVolts / (vsec * kMinDiodeConductionTimeSecs)


###############################################################################
# Main

# --- Mode specific properties
if MODE == FlybackConfig.RIGHT_TO_LEFT:
    VIN_MIN = 36
    VIN_MAX = 60
    VOUT = 16
    POUT_MAX = 3.5
    NPRI = 2
    NSEC = 1
    VAK = 0.5
    RDSON = 52e-3
    RSENSE = 120e-3  # Else 100e-3

elif MODE == FlybackConfig.LEFT_TO_RIGHT:
    VIN_MIN = 11.5
    VIN_MAX = 26.4
    VOUT = 24
    POUT_MAX = 4
    NPRI = 1
    NSEC = 2
    VAK = 0.5
    RDSON = 69e-3
    RSENSE = 68e-3

else:
    print(f"No specifications given for mode: {MODE}")
    exit(1)

# -----------------------------------------------------------------------------
# --- Misc properties
TURNS_RATIO = NSEC / NPRI

EST_EFFICIENCY = 0.7

FSW = 250_000
FSW_TOL = 0.1  # %
FSW_MIN = FSW * (1 - FSW_TOL)
FSW_MAX = FSW * (1 + FSW_TOL)

# --- Transformer Inductance
LBASE = 21e-6
L_TOL = 0.1  # %

LPRI = LBASE * NPRI * NPRI
LPRI_MIN = LPRI * (1 - L_TOL)
LPRI_MAX = LPRI * (1 + L_TOL)

LSEC = LBASE * NSEC * NSEC
LSEC_MIN = LSEC * (1 - L_TOL)
LSEC_MAX = LSEC * (1 + L_TOL)

VSEC = VOUT + VAK
VPRI = VIN_MIN

# -----------------------------------------------------------------------------
# fmt: off
print(f"\n Mode Of Operation: {MODE}")

print("\n-----------------------------")
print("--- OUTPUT SPECIFICATIONS ---")
print("-----------------------------")
IOUT_MAX = POUT_MAX / VOUT
LOAD_MAX = VOUT / IOUT_MAX
print(f" Output Voltage: {VOUT:.1f} V")
print(f" Output Current: {IOUT_MAX:.3f} A")
print(f"    Output Load: {LOAD_MAX:.3f} Ohms")

# -----------------------------------------------------------------------------
print("\n----------------------------")
print("--- INPUT SPECIFICATIONS ---")
print("----------------------------")
PIN_MAX = POUT_MAX / EST_EFFICIENCY
print(f" Input Voltage: {VIN_MIN:.1f} to {VIN_MAX:.1f} V")
print(f" Input Current: {PIN_MAX / VIN_MIN:.3f} A (for Vin={VIN_MIN}V)")
print(f"              : {PIN_MAX / VIN_MAX:.3f} A (for Vin={VIN_MAX}V)")

# -----------------------------------------------------------------------------
print("\n----------------------------")
print("--- OTHER SPECIFICATIONS ---")
print("----------------------------")
print(f"      Primary Coil Inductance: {1E6 * LPRI:.1f} +/- {1E6 * (LPRI_MAX - LPRI):.1f} uH")
print(f"    Secondary Coil Inductance: {1E6 * LSEC:.1f} +/- {1E6 * (LSEC_MAX - LSEC):.1f} uH")
print()
print(f"         Estimated Efficiency: {100 * EST_EFFICIENCY:.1f} %")
print(f"      Turns Ratio (NPRI:NSEC): {NPRI}:{NSEC}")
print(f"          Switching Frequency: {1E-3 * FSW:.1f} +/- {1E-3 * (FSW_MAX - FSW):.1f} kHz")
print()
print(f" Output Diode Forward Voltage: {VAK:.2f} V")
print(f"       Current Sense Resistor: {1E3 * RSENSE:.2f} mOhms")

print(f"\n CALCULATIONS ACCOUNT FOR TOLERANCE: {INCLUDE_TOLERANCE}")
# fmt: on

# -----------------------------------------------------------------------------
print("\n---------------------------------")
print("--- PRIMARY INDUCTANCE LIMITS ---")
print("---------------------------------")

duty_ccm_min = duty_cycle_ccm(VIN_MAX, VSEC, NPRI, NSEC)
duty_ccm_max = duty_cycle_ccm(VIN_MIN, VSEC, NPRI, NSEC)
print(f" Duty Cycle (CCM): {100 * duty_ccm_min:.2f} to {100 * duty_ccm_max:.2f} %")

# fmt: off
P_CRIT_MIN = POUT_MAX / EST_EFFICIENCY
lpri_max_lim = maximum_primary_inductance_H(VIN_MIN, VSEC, NPRI, NSEC, P_CRIT_MIN, FSW_MIN)
lpri_min_lim = mp6005_minimum_inductance_H(VSEC, NPRI, NSEC, RSENSE)

print()
print(f" +-------------------+")
print(f" | INDUCTANCE LIMITS |")
print(f" +-------+-----------+")
print(f" |  Min  | {1e6 * lpri_min_lim:>6.2f} uH | (based on MP6005 700ns diode conduction time)")
print(f" |  Max  | {1e6 * lpri_max_lim:>6.2f} uH | (based on requirement to stay in DCM at Pout,max)")
print(f" +-------+-----------+")
# fmt: on

if LPRI < lpri_min_lim:
    print(f"\n !! WARNING: Primary coil inductance too small.")
elif LPRI_MIN < lpri_min_lim:
    print(f"\n !! WARNING: Primary coil inductance too small (including tolerance).")

if LPRI > lpri_max_lim:
    print(f"\n !! WARNING: Primary coil inductance too large.")
elif LPRI_MAX > lpri_max_lim:
    print(f"\n !! WARNING: Primary coil inductance too large (including tolerance).")


# -----------------------------------------------------------------------------
if INCLUDE_TOLERANCE is True:
    lpri_max = LPRI_MAX
    lpri_min = LPRI_MIN
    fsw_max = FSW_MAX
    fsw_min = FSW_MIN
else:
    lpri_max = LPRI
    lpri_min = LPRI
    fsw_max = FSW
    fsw_min = FSW

duty_dcm = {
    VIN_MIN: duty_cycle_dcm(VOUT, VIN_MIN, lpri_max, fsw_max, LOAD_MAX),
    VIN_MAX: duty_cycle_dcm(VOUT, VIN_MAX, lpri_min, fsw_min, LOAD_MAX),
}

# fmt: off
ipri_peak = {
    VIN_MIN: peak_primary_current_dcm_amps(VIN_MIN, lpri_max, duty_dcm[VIN_MIN], fsw_max),
    VIN_MAX: peak_primary_current_dcm_amps(VIN_MAX, lpri_min, duty_dcm[VIN_MAX], fsw_min)
}
# fmt: on

isec_peak = {
    VIN_MIN: ipri_peak[VIN_MIN] * (NPRI / NSEC),
    VIN_MAX: ipri_peak[VIN_MAX] * (NPRI / NSEC),
}

# -----------------------------------------------------------------------------
pcrit_min = {
    VIN_MIN: boundary_power_watts(VIN_MIN, VSEC, NPRI, NSEC, lpri_max, fsw_max),
    VIN_MAX: boundary_power_watts(VIN_MAX, VSEC, NPRI, NSEC, lpri_max, fsw_max),
}

print()
print(f" +------------------------+")
print(f" |   CCM POWER BOUNDARY   |")
print(f" +--------+---------------+")
print(f" |   Vin  |   Pcrit,min   | Occurs for fsw,max and lpri,max")
print(f" +--------+---------------+")
print(f" | {VIN_MIN:.1f} V |    {pcrit_min[VIN_MIN]:>5.2f} W    |")
print(f" | {VIN_MAX:.1f} V |    {pcrit_min[VIN_MAX]:>5.2f} W    |")
print(f" +--------+---------------+")

# -----------------------------------------------------------------------------
# fmt: off
print()
print(f" +-------------------------------------------------------------------+")
print(f" |                     DUTY CYCLE & PEAK CURRENTS                    |")
print(f" +--------+----------+----------+------------+-----------+-----------+")
print(f" |   Vin  |    Fsw   |   Lpri   | Duty Cycle | Primary   | Secondary |")
print(f" +--------+----------+----------+------------+-----------+-----------+")
vin = VIN_MIN
print(f" | {vin:.1f} V |  {1e-3 * fsw_max:.0f} kHz |  {1e6 * lpri_max:>4.1f} uH |   {100 * duty_dcm[vin]:.2f} %  |  {ipri_peak[vin]:.3f} A  |  {isec_peak[vin]:.3f} A  |")
vin = VIN_MAX
print(f" | {vin:.1f} V |  {1e-3 * fsw_min:.0f} kHz |  {1e6 * lpri_min:>4.1f} uH |   {100 * duty_dcm[vin]:.2f} %  |  {ipri_peak[vin]:.3f} A  |  {isec_peak[vin]:.3f} A  |")
print(f" +--------+----------+----------+------------+-----------+-----------+")
# fmt: on

ipri_peak_max = ipri_peak[VIN_MIN]
isec_peak_max = isec_peak[VIN_MIN]

# -----------------------------------------------------------------------------

# During switch conduction (on-time)
vdson = RDSON * ipri_peak_max
vrs = RSENSE * ipri_peak_max
vsw_pri_on = vdson + vrs
vsw_sec_on = VSEC + ((VIN_MAX - vdson - vrs) * (NSEC / NPRI))
# During diode conduction
vsw_pri_off = VIN_MAX + ((VOUT + VAK) * (NPRI / NSEC))
vsw_sec_off = -VAK

print()
print(f"                +-----------------------+")
print(f"                |     PEAK VOLTAGES     |")
print(f" +--------------+-----------+-----------+")
print(f" |              | Primary   | Secondary |")
print(f" +--------------+-----------+-----------+")
print(f" |   Switch On  | {vsw_pri_on:>6.1f} V  | {vsw_sec_on:>6.1f} V  |")
print(f" |   Switch Off | {vsw_pri_off:>6.1f} V  | {vsw_sec_off:>6.1f} V  |")
print(f" +--------------+-----------+-----------+")


# -----------------------------------------------------------------------------
print("\n---------------------------------------")
print("--- CURRENT SENSE RESISTOR (in DCM) ---")
print("---------------------------------------")

# Critical Conduction Mode

rsense_max_lim1 = mp6005_max_sense_resistor_full_scale_ohms(ipri_peak_max)
rsense_max_lim2 = mp6005_max_sense_resistor_tcon_ohms(VSEC, lpri_min, NPRI, NSEC)
# fmt: off
print(f" Max Rsense 1: {rsense_max_lim1*1E3:>6.2f} mOhm (based on MP6005 equation 7)")
print(f" Max Rsense 2: {rsense_max_lim2*1E3:>6.2f} mOhm (based on MP6005 equation 12)")
# fmt: on

if RSENSE > rsense_max_lim1 or RSENSE > rsense_max_lim2:
    print(f"\n !! WARNING: Current sense resistor is too large.")


# -----------------------------------------------------------------------------
print("\n------------------")
print("--- DCM TIMING ---")
print("------------------")
period_secs = 1 / FSW
ton_switch_secs = duty_dcm[VIN_MIN] * period_secs
ton_diode_secs = diode_conduction_time_dcm_sec(VSEC, isec_peak[VIN_MIN], LSEC)
tdead_secs = period_secs - ton_switch_secs - ton_diode_secs
print(f"    Full Period: {1e6 * period_secs:>6.3f} us")
print()
print(f" Switch On Time: {1e6 * ton_switch_secs:>6.3f} us (when Vin={VIN_MIN}V)")
print(f"  Diode On Time: {1e6 * ton_diode_secs:>6.3f} us")
print(f"      Dead Time: {1e6 * tdead_secs:>6.3f} us")

ton_switch_secs = duty_dcm[VIN_MAX] * period_secs
ton_diode_secs = diode_conduction_time_dcm_sec(VSEC, isec_peak[VIN_MAX], LSEC)
tdead_secs = period_secs - ton_switch_secs - ton_diode_secs
print()
print(f" Switch On Time: {1e6 * ton_switch_secs:>6.3f} us (when Vin={VIN_MAX}V)")
print(f"  Diode On Time: {1e6 * ton_diode_secs:>6.3f} us")
print(f"      Dead Time: {1e6 * tdead_secs:>6.3f} us")

print()
