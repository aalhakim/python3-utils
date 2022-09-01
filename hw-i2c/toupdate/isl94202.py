from adafruit_i2c import Adafruit_I2C
import math
import time

########################################################################
DEFAULT_ADDRESS = 0x28 # 0x50 in normal format
EEPROM_DELAY = 0.03

# Registers
ISL_OVL        = 0x00    # Overvoltage level
ISL_OVR        = 0x02    # Overvoltage recovery
ISL_UVL        = 0x04    # Undervoltage level
ISL_UVR        = 0x06    # Undervoltage recovery
ISL_OVLO       = 0x08
ISL_UVLO       = 0x0A
ISL_EOC        = 0x0C    # End of charge threshold
ISL_LVCH       = 0x0E    # Precharge level
ISL_OCD        = 0x16    # Discharge overcurrent timeout/level
ISL_OCC        = 0x18    # Charge overcurrent timeout/level
ISL_SCD        = 0x1A    # Discharge short timeout/level
ISL_CBVL       = 0x1C    # Cell balance minimum voltage
ISL_CBVU       = 0x1E    # Cell balance maximum voltage
ISL_CBDL       = 0x20    # Cell balance min difference
ISL_CBDU       = 0x22    # Cell balance max difference
ISL_CBON       = 0x24    # Cell balance on time
ISL_CBOF       = 0x26    # Cell balance off time
ISL_COTS       = 0x30    # Chg overtemp
ISL_COTR       = 0x32    # Chg overtemp recovery
ISL_CUTS       = 0x34    # Chg undertemp
ISL_CUTR       = 0x36    # Chg undertemp recovery
ISL_DOTS       = 0x38    # Dischg overtemp
ISL_DOTR       = 0x3A    # Dischg overtemp recovery
ISL_DUTS       = 0x3C    # Dischg undertemp
ISL_DUTR       = 0x3E    # Dischg undertemp recovery
ISL_IOTS       = 0x40    # Internal overtemp
ISL_IOTR       = 0x42    # Internal overtemp recovery
ISL_CELLSCFG   = 0x49    # Connected cell layout
ISL_FEATURES1  = 0x4A
ISL_FEATURES2  = 0x4B

# RAM
ISL_STATUS1    = 0x80
ISL_STATUS2    = 0x81
ISL_STATUS3    = 0x82
ISL_STATUS4    = 0x83
ISL_BALANCING  = 0x84
ISL_EEEN       = 0x89
ISL_ISENSE     = 0x8E
ISL_CELL1      = 0x90
ISL_CELL2      = 0x92
ISL_CELL7      = 0x9C
ISL_CELL8      = 0x9E
ISL_TEMP_INT   = 0xA0
ISL_TEMP_EXT1  = 0xA2
ISL_TEMP_EXT2  = 0xA4


########################################################################
class ISL94202():
    def __init__(self, address=DEFAULT_ADDRESS, shunt_ohms=0.004, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.debug = debug
        self.shunt_ohms = shunt_ohms
        self._write8(ISL_EEEN, 0)

    def _write8(self, addr, data):
        self.i2c.write8(addr, data)
        time.sleep(EEPROM_DELAY) # Delay required for EEPROM writes
        if (addr & 0x03 == 0x00):
            # First byte in a page must be written twice
            self.i2c.write8(addr, data)
            time.sleep(EEPROM_DELAY)

    def _write16(self, addr, data):
        self._write8(addr, data & 0xFF)
        self._write8(addr+1, data >> 8)

    def read_temp_internal(self):
        return reg2inttemp(self.i2c.readU16(ISL_TEMP_INT))

    def read_temp_ext1(self):
        return reg2exttemp(self.i2c.readU16(ISL_TEMP_EXT1))

    def read_temp_ext2(self):
        return reg2exttemp(self.i2c.readU16(ISL_TEMP_EXT2))

    def read_current(self, gain=50, averaging=1):
        if gain == 50:
            gainbyte = 0x09
        elif gain == 500:
            gainbyte = 0x29
        else:
            return ValueError, "Gain must be 50 or 500"

        self._write8(0x85, gainbyte)
        current16 = self.i2c.readU16(ISL_ISENSE)
        negative = self.i2c.readU16(ISL_STATUS3) & 0x04

        current = current16 * 1.8 / (4095 * gain * self.shunt_ohms)
        if negative: current = -current
        return current

    def read_cell_voltages(self):
        cell1 = reg2volt(self.i2c.readU16(ISL_CELL1))
        cell2 = reg2volt(self.i2c.readU16(ISL_CELL2))
        cell3 = reg2volt(self.i2c.readU16(ISL_CELL7))
        cell4 = reg2volt(self.i2c.readU16(ISL_CELL8))
        return (cell1, cell2, cell3, cell4)

    def read_status(self):
        stat1 = self.i2c.readU8(ISL_STATUS1)
        stat2 = self.i2c.readU8(ISL_STATUS2)
        stat3 = self.i2c.readU8(ISL_STATUS3)
        stat4 = self.i2c.readU8(ISL_STATUS4)
        return (stat1, stat2, stat3, stat4)

    # Read configuration from the IC.
    # Returns an ISLConfig object.
    def read_config(self):
        cfg = ISLConfig()

        # Voltage
        cfg.overvoltage_threshold  = reg2volt(self.i2c.readU16(ISL_OVL))
        cfg.overvoltage_recovery   = reg2volt(self.i2c.readU16(ISL_OVR))
        cfg.undervoltage_threshold = reg2volt(self.i2c.readU16(ISL_UVL))
        cfg.undervoltage_recovery  = reg2volt(self.i2c.readU16(ISL_UVR))
        cfg.overvoltage_lockout    = reg2volt(self.i2c.readU16(ISL_OVLO))
        cfg.undervoltage_lockout   = reg2volt(self.i2c.readU16(ISL_UVLO))
        cfg.eoc_threshold          = reg2volt(self.i2c.readU16(ISL_EOC))
        cfg.precharge_threshold    = reg2volt(self.i2c.readU16(ISL_LVCH))

        # Current
        cfg.discharge_overcurrent_millivolts = OCD_to_mv(self.i2c.readU16(ISL_OCD))
        cfg.charge_overcurrent_millivolts = OCC_to_mv(self.i2c.readU16(ISL_OCC))
        cfg.discharge_short_millivolts = SCD_to_mv(self.i2c.readU16(ISL_SCD))

        # Cell balancing
        cfg.balance_min_voltage = reg2volt(self.i2c.readU16(ISL_CBVL))
        cfg.balance_max_voltage = reg2volt(self.i2c.readU16(ISL_CBVU))
        cfg.balance_min_diff    = reg2volt(self.i2c.readU16(ISL_CBDL))
        cfg.balance_max_diff    = reg2volt(self.i2c.readU16(ISL_CBDU))

        reg = self.i2c.readU16(ISL_CBON)
        cfg.balance_on_sec = reg & 0x3FF
        if (reg & 0x0C00 != 0x800):
            raise ValueError, "Balance ON timebase is not in seconds"
        reg = self.i2c.readU16(ISL_CBOF)
        cfg.balance_off_sec = reg & 0x3FF
        if (reg & 0x0C00 != 0x800):
            raise ValueError, "Balance OFF timebase is not in seconds"

        # Temperature
        cfg.overtemp            = reg2exttemp(self.i2c.readU16(ISL_DOTS))
        cfg.overtemp_recovery   = reg2exttemp(self.i2c.readU16(ISL_DOTR))
        cfg.undertemp           = reg2exttemp(self.i2c.readU16(ISL_DUTS))
        cfg.undertemp_recovery  = reg2exttemp(self.i2c.readU16(ISL_DUTR))
        cfg.internal_overtemp   = reg2inttemp(self.i2c.readU16(ISL_IOTS))
        cfg.internal_overtemp_recovery = reg2inttemp(self.i2c.readU16(ISL_IOTR))

        return cfg

    # Write the given ISLConfig object to the IC.
    def write_config(self, cfg):
        if not isinstance(cfg, ISLConfig):
            raise TypeError

        # Write to both EEPROM and RAM
        for mode in [1, 0]:
            self._write8(ISL_EEEN, mode)

            # Voltage
            self._write8(ISL_CELLSCFG, 0xC3) # Connected cells (fixed 1,2,7,8)
            self._write16(ISL_OVL,  volt2reg(cfg.overvoltage_threshold))
            self._write16(ISL_OVR,  volt2reg(cfg.overvoltage_recovery))
            self._write16(ISL_UVL,  volt2reg(cfg.undervoltage_threshold))
            self._write16(ISL_UVR,  volt2reg(cfg.undervoltage_recovery))
            self._write16(ISL_OVLO, volt2reg(cfg.overvoltage_lockout))
            self._write16(ISL_UVLO, volt2reg(cfg.undervoltage_lockout))
            self._write16(ISL_EOC,  volt2reg(cfg.eoc_threshold))
            self._write16(ISL_LVCH, volt2reg(cfg.precharge_threshold))

            # Current
            self._write16(ISL_OCD, mv_to_OCD(cfg.discharge_overcurrent_millivolts))
            self._write16(ISL_OCC, mv_to_OCC(cfg.charge_overcurrent_millivolts))
            self._write16(ISL_SCD, mv_to_SCD(cfg.discharge_short_millivolts))

            # Balancing
            self._write16(ISL_CBVL, volt2reg(cfg.balance_min_voltage))
            self._write16(ISL_CBVU, volt2reg(cfg.balance_max_voltage))
            self._write16(ISL_CBDL, volt2reg(cfg.balance_min_diff))
            self._write16(ISL_CBDU, volt2reg(cfg.balance_max_diff))
            self._write16(ISL_CBON, 0x0800 | (cfg.balance_on_sec & 0x03FF))
            self._write16(ISL_CBOF, 0x0800 | (cfg.balance_off_sec & 0x03FF))
            self._write8(ISL_FEATURES2, 0x01) # Balance at EOC only

            # Temperature
            val = exttemp2reg(cfg.overtemp)
            self._write16(ISL_COTS, val) # Charge
            self._write16(ISL_DOTS, val) # Discharge

            val = exttemp2reg(cfg.overtemp_recovery)
            self._write16(ISL_COTR, val) # Charge
            self._write16(ISL_DOTR, val) # Discharge

            val = exttemp2reg(cfg.undertemp)
            self._write16(ISL_CUTS, val) # Charge
            self._write16(ISL_DUTS, val) # Discharge

            val = exttemp2reg(cfg.undertemp_recovery)
            self._write16(ISL_CUTR, val) # Charge
            self._write16(ISL_DUTR, val) # Discharge

            self._write16(ISL_IOTS, 0x0664) # Internal Over-Temperature: +115
            self._write16(ISL_IOTR, 0x0610) # Internal Over-Temperature Recovery: +95 degC


# Class for holding IC configuration.
# read_config() returns one of these.
# One of these is passed to write_config().
class ISLConfig():
    __slots__ = ['overvoltage_lockout', 'overvoltage_threshold', 'overvoltage_recovery',
                'undervoltage_recovery', 'undervoltage_threshold', 'undervoltage_lockout',
                'eoc_threshold', 'precharge_threshold',
                'discharge_overcurrent_millivolts', 'charge_overcurrent_millivolts', 'discharge_short_millivolts',
                'balance_max_voltage', 'balance_min_voltage', 'balance_min_diff', 'balance_max_diff',
                'balance_on_sec', 'balance_off_sec',
                'overtemp', 'overtemp_recovery', 'undertemp_recovery', 'undertemp',
                'internal_overtemp', 'internal_overtemp_recovery']

    # Pretty-printer for config
    def __repr__(self):
        out = ''
        for attr in self.__slots__:
            value = getattr(self, attr)
            if type(value) is float:
                out += '{:22s} = {:.2f}\n'.format(attr, value)
            else:
                out += '{:22s} = {}\n'.format(attr, value)
        return out


# Conversions between register values and real-world values:
# ---
# Convert between voltage (0-4.8) and a register value
# Used for cell voltage thresholds.
def volt2reg(voltage):
    return int(4095 * (voltage / 4.8))


def reg2volt(reg):
    return 4.8 * (reg & 0xFFF) / 4095.0

TGAIN = 0
NTC_R25 = 10000.0
NTC_BETA_2585  = 3977.0     # The NTC temperature coefficient
VREF_TEMP_SENSOR = 2.5      # The NTC network voltage reference, in Volts
RTOP_TEMP_SENSOR = 22000.0  # The NTC network top resistor, in Ohms
RBOT_TEMP_SENSOR = 10000.0  # The NTC network bottom resistor, in Ohms
ZERO_CELSIUS_IN_KELVIN = 273.15


# Convert between degrees Celsius and a register value
# for external temperature sensors
def exttemp2reg(celsius):
    volts = exttemp_celsius_to_volts(celsius)
    return int(4095 * (volts / 1.8))


def reg2exttemp(reg):
    volts = 1.8 * reg / 4095.0
    return exttemp_volts_to_celsius(volts)

# Convert between degrees Celsius and a register value
# for *internal* temperature sensors
def inttemp2reg(celsius):
    raise NotImplementedError


def reg2inttemp(reg):
    volts = 1.8 * reg / 4095.0
    if TGAIN == 0:
        degrees = ((volts * 1000.0) / 1.85270) - ZERO_CELSIUS_IN_KELVIN
    else:
        degrees = ((volts * 1000.0) / 0.92635) - ZERO_CELSIUS_IN_KELVIN
    return degrees


def volts_to_ntc_resistance(volts):
    vmax = VREF_TEMP_SENSOR * (RBOT_TEMP_SENSOR) / (RTOP_TEMP_SENSOR + RBOT_TEMP_SENSOR)
    if volts > vmax:
        volts = vmax - 0.001
    ntc_ohms = (volts * RTOP_TEMP_SENSOR * RBOT_TEMP_SENSOR) / ((VREF_TEMP_SENSOR * RBOT_TEMP_SENSOR) - (volts * (RTOP_TEMP_SENSOR + RBOT_TEMP_SENSOR)))
    return ntc_ohms


def celsius_to_ntc_resistance(celsius):
    ntc_ohms = NTC_R25 * math.exp(NTC_BETA_2585 * ((1.0/(ZERO_CELSIUS_IN_KELVIN+celsius)) - (1.0/(ZERO_CELSIUS_IN_KELVIN+25.0))))
    return ntc_ohms


def exttemp_volts_to_celsius(volts):
    if TGAIN == 0: volts = volts / 2.0
    ntc_ohms = volts_to_ntc_resistance(volts)
    kelvin = 1.0 / ((math.log(ntc_ohms / NTC_R25) / NTC_BETA_2585) + (1.0 / (ZERO_CELSIUS_IN_KELVIN + 25.0)))
    celsius = kelvin - ZERO_CELSIUS_IN_KELVIN
    return celsius


def exttemp_celsius_to_volts(celsius):
    ntc_ohms = celsius_to_ntc_resistance(celsius)

    if TGAIN == 0:
        gain = 2
    else:
        gain = 1

    volts = gain * VREF_TEMP_SENSOR * ((ntc_ohms * RBOT_TEMP_SENSOR) / (ntc_ohms*RTOP_TEMP_SENSOR + ntc_ohms*RBOT_TEMP_SENSOR + RTOP_TEMP_SENSOR*RBOT_TEMP_SENSOR))
    return volts


# Allowable overcurrent/short-circuit thresholds in millivolts
OCD_settings = [4, 8, 16, 24, 32, 48, 64, 96]
OCC_settings = [1, 2, 4, 6, 8, 12, 16, 24]
SCD_settings = [16, 24, 32, 48, 64, 96, 128, 256]


def OCD_to_mv(reg):
    reg = reg >> 12
    return OCD_settings[reg]


def OCC_to_mv(reg):
    reg = reg >> 12
    return OCC_settings[reg]


def SCD_to_mv(reg):
    reg = reg >> 12
    return SCD_settings[reg]


def mv_to_OCD(mv):
    val = OCD_settings.index(mv)
    return 0x04A0 | (val << 12)


def mv_to_OCC(mv):
    val = OCC_settings.index(mv)
    return 0x04A0 | (val << 12)


def mv_to_SCD(mv):
    val = SCD_settings.index(mv)
    return 0x04A0 | (val << 12)
