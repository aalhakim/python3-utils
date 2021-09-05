"""
Calculate temperature from the NTCLE100E3 NTC from Vishay
The equation is taken from the component datasheet
"""
import math

########################################################################
ISL94202_TGAIN_BIT = 0    # The TGain bit setting of the ISL94202

RTOP_TEMP_SENSOR = 22000    # The NTC network top resistor, in Ohms
RBOT_TEMP_SENSOR = 10000    # The NTC network bottom resistor, in Ohms
VREF_TEMP_SENSOR = 2.5      # The NTC network voltage reference, in Volts

# NTC Properties
# 25/85 Beta Values:
#   + 3977: Vishay NTCLE100E3103JB0
#   + 3434: Murata NCP03XH103F
NTC_R25 = 10000             # The NTC resistance at 25degC, in Ohms
NTC_BETA_2585 = 3977        # The NTC temperature coefficient (beta)
NTC_PROPERTY_A1 = 3.354016e-3
NTC_PROPERTY_B1 = 2.569850e-4
NTC_PROPERTY_C1 = 2.620131e-6
NTC_PROPERTY_D1 = 6.383091e-8

ZERO_CELSIUS_IN_KELVIN = 273.15 # Used to calculate NTC temperature


########################################################################
def calc_ntc_resistance_from_volts(vMeas):
    """
    The thermistor resistance can be calculated from the standard
    potential divider equation where we know Vref, Vout and Rbalance
    """

    # This equation is the equation of the NTC potential divider
    # network with NTC resistance as the subject
    rThermistor = (
        (vMeas * RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR) /
        ((VREF_TEMP_SENSOR * RBOT_TEMP_SENSOR) - (vMeas * (RTOP_TEMP_SENSOR + RBOT_TEMP_SENSOR)))
    )
    return rThermistor


def calc_ntc_resistance_from_celsius(tCelsius):
    """
    Calculate the expected resistance of the thermistor for a given
    temperature in degrees celsius
    """

    # This is Thermistor Beta Equation with NTC resistance as the subject
    exponent = NTC_BETA_2585 * ((1/(ZERO_CELSIUS_IN_KELVIN+tCelsius)) - (1/(ZERO_CELSIUS_IN_KELVIN+25.0)))
    rThermistor = NTC_R25 * math.exp(exponent)
    return rThermistor


def convert_temp_volts_to_celsius_shh(tVolts):
    """
    Convert the voltage reading from the external NTC temperature sensor
    to a degrees Celsius value using the Steinhart-Hart Equations method.
    """

    # Find out the NTC resistance at the current temperature
    rThermistorOhms = calc_ntc_resistance_from_volts(tVolts)

    # The temperature in Kelvin can then be calculated using the
    # Steinhart-Hart equation. The below version is taken from the
    # Vishay NTCLE100E3 datasheet.
    tKelvin = (1 / (
        (NTC_PROPERTY_A1) +
        (NTC_PROPERTY_B1 * math.log(rThermistorOhms/NTC_R25)) +
        (NTC_PROPERTY_C1 * pow(math.log(rThermistorOhms/NTC_R25), 2.0)) +
        (NTC_PROPERTY_D1 * pow(math.log(rThermistorOhms/NTC_R25), 3.0))
    ))

    # Converter the result from Kelvin to Celsius
    tCelsius = tKelvin - ZERO_CELSIUS_IN_KELVIN
    return tCelsius



def convert_temp_volts_to_celsius_beta(tVolts):
    """
    Convert the voltage reading from the external NTC temperature sensor
    to a degrees Celsius value using the Beta Equation method.
    """

    # Find out the NTC resistance at the current temperature
    rThermistorOhms = calc_ntc_resistance_from_volts(tVolts)

    # This is Thermistor Beta Equation with current temperature as the subject
    tKelvin = 1 / ((math.log(rThermistorOhms / NTC_R25) / NTC_BETA_2585) + (1 / (ZERO_CELSIUS_IN_KELVIN + 25.0)))
    tCelsius = tKelvin - ZERO_CELSIUS_IN_KELVIN
    return tCelsius



def convert_temp_celsius_to_volts(tCelsius):
    """
    Calculate what the expected NTC potential divider network output
    is expected to be for a given temperature value.
    """

    rThermistorOhms = calc_ntc_resistance_from_celsius(tCelsius)

    # Work out what gain is applied to the measured voltage
    if   (ISL94202_TGAIN_BIT == 0): gain = 2
    elif (ISL94202_TGAIN_BIT == 1): gain = 1
    else:                           raise(RuntimeError)

    # This equation is the equation of the NTC potential divider
    # network with the output voltage as the subject
    tVolts = gain * VREF_TEMP_SENSOR * (
        (rThermistorOhms * RBOT_TEMP_SENSOR) /
        (rThermistorOhms*RTOP_TEMP_SENSOR + rThermistorOhms*RBOT_TEMP_SENSOR + RTOP_TEMP_SENSOR*RBOT_TEMP_SENSOR)
    )
    return tVolts


########################################################################
if __name__ == "__main__":
    pass

    print("")
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
    print("  | {0: ^14s} | {1: ^14s} | {2: ^14s} | {3: ^7s} |".format("RESISTANCE", "STEINHART-HART", "BETA", "VOLTAGE"))
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))

    # Calculate NTC resistance and estimated temperature based on voltage
    # The voltage range is limited to 0V and 0.8V.
    increment = 0.01
    voltage = increment
    voltage_range = []
    while voltage < 0.80-increment:
        voltage_range.append(voltage)
        voltage += increment

    for temp_volts in voltage_range:
        r_thermistor = calc_ntc_resistance_from_volts(temp_volts)
        temp_celsius_shh = convert_temp_volts_to_celsius_shh(temp_volts)
        temp_celsius_beta = convert_temp_volts_to_celsius_beta(temp_volts)
        print("  | {: >14s} | {: >14s} | {: >14s} | {: >7s} |".format(
            "{: .0f}".format(r_thermistor) + " Ohms",
            "{:+.2f}".format(temp_celsius_shh) + " degC",
            "{:+.2f}".format(temp_celsius_beta) + " degC",
            "{: .2f}".format(temp_volts) + " V"
        ))
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))


    print("")
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
    print("  | {0: ^14s} | {1: ^14s} | {2: ^7s} |".format("TEMPERATURE", "RESISTANCE", "VOLTAGE"))
    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))

    # Calculate expected NTC resistance and NTC potential divider voltages
    # for a given temperature.
    temp_range = range(-55, 155, 5)
    for temp_celsius in temp_range:
        r_thermistor = calc_ntc_resistance_from_celsius(temp_celsius)
        temp_volts = convert_temp_celsius_to_volts(temp_celsius)
        print("  | {: >14s} | {: >14s} | {: >7s} |".format(
            "{:+.0f}".format(temp_celsius) + " degC",
            "{: .0f}".format(r_thermistor) + " Ohms",
            "{:.3f}".format(temp_volts) + " V"
        ))

    print("  +-{0:-^14s}-|-{0:-^14s}-|-{0:-^7s}-+".format(""))
