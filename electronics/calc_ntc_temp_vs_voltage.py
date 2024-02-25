"""
Calculate NTC resistance versus temperature, and the effects on a potential
divider network.


    ^ VSUP   ^                  NTC_POS = "top"
    |        |
    R RTOP   N NTC
    R        N
    |________|___ VTEMP
    |
    R RBOT
    R
    |
    v


    ^ VSUP                      NTC_POS = "bot"
    |
    R RTOP
    R
    |____________ VTEMP
    |        |
    R RBOT   N NTC
    R        N
    |        |
    v        v

"""

import math

########################################################################
NTC_POS = "bot"  # Use 'bot' or 'top'

RTOP_TEMP_SENSOR = 100e3  # The NTC network top resistor, in Ohms
RBOT_TEMP_SENSOR = 10e12  # The NTC network bottom resistor, in Ohms

VSUP_TEMP_SENSOR = 5.0  # The NTC network voltage reference, in Volts

# NTC Properties
# 25/85 Beta Values:
#   + 3977: Vishay NTCLE100E3103JB0 (10k)
#   + 3434: Murata NCP03XH103F (10k)
#   + 3434: Murata NCU18XH103F60RB (10k)
#   + 4250: Murata NCU18WF104F6SRB (100k)
NTC_R25 = 100000  # The NTC resistance at 25degC, in Ohms
NTC_BETA_2585 = 4250  # The NTC temperature coefficient (beta)

NTC_PROPERTY_A1 = 3.354016e-3
NTC_PROPERTY_B1 = 2.569850e-4
NTC_PROPERTY_C1 = 2.620131e-6
NTC_PROPERTY_D1 = 6.383091e-8

kZERO_CELSIUS_IN_KELVIN = 273.15  # Used to calculate NTC temperature


########################################################################
def calc_ntc_resistance_from_volts(vMeas, ntcPos="bot"):
    """
    The thermistor resistance can be calculated from the standard
    potential divider equation where we know Vref, Vout and Rbalance
    """

    # This equation is the equation of the NTC potential divider
    # network with NTC resistance as the subject
    if ntcPos == "bot":
        rThermistor = (vMeas * RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR) / (
            (VSUP_TEMP_SENSOR * RBOT_TEMP_SENSOR)
            - (vMeas * (RTOP_TEMP_SENSOR + RBOT_TEMP_SENSOR))
        )
    elif ntcPos == "top":
        rThermistor = (
            RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR * (VSUP_TEMP_SENSOR - vMeas)
        ) / (
            (vMeas * (RTOP_TEMP_SENSOR + RBOT_TEMP_SENSOR))
            - (VSUP_TEMP_SENSOR * RBOT_TEMP_SENSOR)
        )
    else:
        raise RuntimeError(f"Unknown value of ntcPos: '{ntcPos}'.")

    return rThermistor


def calc_ntc_resistance_from_celsius(tCelsius):
    """
    Calculate the expected resistance of the thermistor for a given
    temperature in degrees celsius
    """

    # This is Thermistor Beta Equation with NTC resistance as the subject
    exponent = NTC_BETA_2585 * (
        (1 / (kZERO_CELSIUS_IN_KELVIN + tCelsius))
        - (1 / (kZERO_CELSIUS_IN_KELVIN + 25.0))
    )
    rThermistor = NTC_R25 * math.exp(exponent)
    return rThermistor


def convert_temp_volts_to_celsius_shh(tVolts):
    """
    Convert the voltage reading from the external NTC temperature sensor
    to a degrees Celsius value using the Steinhart-Hart Equations method.
    """

    # Find out the NTC resistance at the current temperature
    rThermistorOhms = calc_ntc_resistance_from_volts(tVolts, NTC_POS)

    # The temperature in Kelvin can then be calculated using the
    # Steinhart-Hart equation. The below version is taken from the
    # Vishay NTCLE100E3 datasheet.
    tKelvin = 1 / (
        (NTC_PROPERTY_A1)
        + (NTC_PROPERTY_B1 * math.log(rThermistorOhms / NTC_R25))
        + (NTC_PROPERTY_C1 * pow(math.log(rThermistorOhms / NTC_R25), 2.0))
        + (NTC_PROPERTY_D1 * pow(math.log(rThermistorOhms / NTC_R25), 3.0))
    )

    # Converter the result from Kelvin to Celsius
    tCelsius = tKelvin - kZERO_CELSIUS_IN_KELVIN
    return tCelsius


def convert_temp_volts_to_celsius_beta(tVolts):
    """
    Convert the voltage reading from the external NTC temperature sensor
    to a degrees Celsius value using the Beta Equation method.
    """

    # Find out the NTC resistance at the current temperature
    rThermistorOhms = calc_ntc_resistance_from_volts(tVolts, NTC_POS)

    # This is Thermistor Beta Equation with current temperature as the subject
    tKelvin = 1 / (
        (math.log(rThermistorOhms / NTC_R25) / NTC_BETA_2585)
        + (1 / (kZERO_CELSIUS_IN_KELVIN + 25.0))
    )
    tCelsius = tKelvin - kZERO_CELSIUS_IN_KELVIN
    return tCelsius


def convert_temp_celsius_to_volts(tCelsius, ntcPos="bot"):
    """
    Calculate what the expected NTC potential divider network output
    is expected to be for a given temperature value.
    """

    rThermistorOhms = calc_ntc_resistance_from_celsius(tCelsius)

    # This equation is the equation of the NTC potential divider
    # network with the output voltage as the subject
    if ntcPos == "bot":
        tVolts = VSUP_TEMP_SENSOR * (
            (RBOT_TEMP_SENSOR * rThermistorOhms)
            / (
                RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR
                + RTOP_TEMP_SENSOR * rThermistorOhms
                + RBOT_TEMP_SENSOR * rThermistorOhms
            )
        )
    elif ntcPos == "top":
        tVolts = VSUP_TEMP_SENSOR * (
            (RBOT_TEMP_SENSOR * rThermistorOhms + RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR)
            / (
                RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR
                + RTOP_TEMP_SENSOR * rThermistorOhms
                + RBOT_TEMP_SENSOR * rThermistorOhms
            )
        )
    else:
        raise RuntimeError(f"Unknown value of ntcPos: '{ntcPos}'.")

    return tVolts


########################################################################
if __name__ == "__main__":
    pass

    print("")
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
    print(
        "  | {0: ^14s} | {1: ^14s} | {2: ^14s} | {3: ^7s} |".format(
            "RESISTANCE", "STEINHART-HART", "BETA", "VOLTAGE"
        )
    )
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))

    # Calculate NTC resistance and estimated temperature based on voltage
    # The voltage range is limited to 0 V and vrange V.
    vrange = VSUP_TEMP_SENSOR - 0.01
    increment = 0.05
    voltage = increment
    voltage_range = []
    while voltage < min(vrange, VSUP_TEMP_SENSOR) - increment:
        voltage_range.append(voltage)
        voltage += increment

    for temp_volts in voltage_range:
        r_thermistor = calc_ntc_resistance_from_volts(temp_volts, NTC_POS)

        try:
            temp_celsius_shh = convert_temp_volts_to_celsius_shh(temp_volts)
        except ValueError:
            # ValueError: error with log calculation
            temp_celsius_shh = "ERR"
        else:
            temp_celsius_shh = "{:+.2f}".format(temp_celsius_shh) + " degC"
        try:
            temp_celsius_beta = convert_temp_volts_to_celsius_beta(temp_volts)
        except ValueError:
            # ValueError: error with log calculation
            temp_celsius_beta = "ERR"
        else:
            temp_celsius_beta = "{:+.2f}".format(temp_celsius_beta) + " degC"

        print(
            "  | {: >14s} | {: >14s} | {: >14s} | {: >7s} |".format(
                "{: .0f}".format(r_thermistor) + " Ohms",
                temp_celsius_shh,
                temp_celsius_beta,
                "{: .2f}".format(temp_volts) + " V",
            )
        )
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))

    print("")
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
    print(
        "  | {0: ^14s} | {1: ^14s} | {2: ^7s} |".format(
            "TEMPERATURE", "RESISTANCE", "VOLTAGE"
        )
    )
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))

    # Calculate expected NTC resistance and NTC potential divider voltages
    # for a given temperature.
    temp_range = range(-55, 155, 5)
    for temp_celsius in temp_range:
        r_thermistor = calc_ntc_resistance_from_celsius(temp_celsius)
        temp_volts = convert_temp_celsius_to_volts(temp_celsius, NTC_POS)
        print(
            "  | {: >14s} | {: >14s} | {: >7s} |".format(
                "{:+.0f}".format(temp_celsius) + " degC",
                "{: .0f}".format(r_thermistor) + " Ohms",
                "{:.3f}".format(temp_volts) + " V",
            )
        )

    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
