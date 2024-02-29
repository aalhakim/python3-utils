"""
Equations for Flyback Converter Design
"""

from math import sqrt


###############################################################################
def duty_cycle_ccm(vpri: float, vsec: float, npri: float, nsec: float) -> float:
    """Calculate the duty cycle in CCM.

    Args:
        vpri (float): Primary coil voltage, in V
        vsec (float): Secondary coil voltage, in V
        npri (float): Number of turns on the primary coil
        nsec (float): Number of turns on the secondary coil

    Returns:
        float: CCM duty cycle
    """
    turns_ratio = npri / nsec
    return (vsec * turns_ratio) / ((vsec * turns_ratio) + vpri)


def duty_cycle_dcm(vout: float, vin: float, lpri: float, fsw: float, rload: float) -> float:
    """Calculate the duty cycle in DCM

    Args:
        vout (float): Output voltage, in V
        vin (float): Input voltage, in V
        lpri (float): Primary coil inductance, in H
        fsw (float): Switching frequency, in Hz
        rload (float): Load resistance, in Ohms

    Returns:
        float: DCM duty cycle
    """
    return (vout / vin) * sqrt(2 * lpri * fsw / rload)


def boundary_power_watts(
    vpri: float, vsec: float, npri: float, nsec: float, lpri: float, fsw: float
) -> float:
    """Calculate how much power the converter will transfer at the DCM/CCM boundary.

    Args:
        vpri (float): Primary coil voltage, in V (use minimum)
        vsec (float): Secondary coil voltage, in V
        npri (float): Number of turns on the primary coil
        nsec (float): Number of turns on the secondary coil
        lpri (float): Primary coil inductance, in H (use maximum)
        fsw (float): Switching frequency, in Hz (use maximum)

    Returns:
        float: The amount of power that will be transferred at the DCM/CCM
            boundary, in W.
    """
    duty_ccm = duty_cycle_ccm(vpri, vsec, npri, nsec)
    return vpri * vpri * duty_ccm * duty_ccm / (2 * lpri * fsw)


def maximum_primary_inductance_H(
    vpri: float, vsec: float, npri: float, nsec: float, pcrit: float, fsw: float
) -> float:
    """Calculate maximum allowable inductance to remain in DCM mode for a given load.

    Args:
        vpri (float): Primary coil voltage, in V
        vsec (float): Secondary coil voltage, in V
        npri (float): Number of turns on the primary coil
        nsec (float): Number of turns on the secondary coil
        pout_max (float): Power level at which critical conduction starts, in W
        fsw (float): Switching frequency, in Hz (use minimum)

    Returns:
        float: Inductance value, in uH
    """
    duty_ccm = duty_cycle_ccm(vpri, vsec, npri, nsec)
    return vpri * vpri * duty_ccm * duty_ccm / (2 * pcrit * fsw)


def peak_primary_current_dcm_amps(
    vpri: float, lpri: float, duty_cycle: float, fsw: float
) -> float:
    """Calculate peak current through the primary side during DCM.

    Args:
        ipri (float): Primary coil current, in A
        lpri (float): Primary coil inductance, in H
        duty_cycle (float): Duty cycle
        fsw (float): Switching frequency, in Hz

    Returns:
        float: Peak current through the primary coil, in A
    """
    return vpri * duty_cycle / (lpri * fsw)


def peak_secondary_current_dcm_amps(ipri_peak: float, npri: float, nsec: float) -> float:
    """Calculate peak current through the secondary side during DCM.

    Args:
        ipri_peak (float): Primary coil peak current, in A
        npri (float): Number of turns on primary coil
        nsec (float): Number of turns on secondary coil

    Returns:
        float: Peak current through the primary coil, in A
    """
    return ipri_peak * (npri / nsec)


def peak_primary_current_ccm_amps(ipri: float, duty_cycle: float) -> float:
    """Calculate peak current through the primary side during CCM.

    Args:
        ipri (float): Primary coil current, in A
        duty_cycle (float): Duty cycle

    Returns:
        float: Peak current through the primary coil, in A
    """
    return 2 * ipri / duty_cycle


def peak_secondary_current_ccm_amps(isec: float, duty_cycle: float) -> float:
    """Calculate peak current through the secondary side.

    Args:
        isec (float): Secondary coil current, in A
        duty_cycle (float): Duty cycle

    Returns:
        float: Peak current through the secondary coil, in A
    """
    return 2 * isec / (1 - duty_cycle)


def diode_conduction_time_dcm_sec(vsec: float, isec_peak: float, lsec: float) -> float:
    return lsec * isec_peak / vsec
