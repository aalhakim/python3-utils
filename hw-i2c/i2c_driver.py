"""
High level I2C driver class for Linux systems.

Based on adafruit_i2c.py but using smbus2 library.
"""

import time
from smbus2 import SMBus


########################################################################
DEFAULT_I2C_BUS = 1


########################################################################
def handle_io_error(func):
    """Re-raise IO Errors with custom error message"""
    def inner(obj, *args, **kwargs):
        try:
            result = func(obj, *args, **kwargs)
        except IOError as err:
            raise IOError("I2C error from addr 0x{:02X}".format(args[0]))
        else:
            return result

    return inner


########################################################################
class I2C_Driver(object):

    def __init__(self, bus=1, debug=False):
        self.bus = SMBus(bus)
        self.debug = debug

    def __del__(self):
        self.bus.close()

    def set_bus(self, bus):
        """Change active I2C bus"""
        self.bus.close()
        self.bus = SMBus(bus)

    def _debug_log(self, mode, dev_addr, data=None, reg_addr=None):
        """Print debug message if self.dbg=True"""
        if self.debug is True:
            # Obtain mode-relevant terms
            modes = {"rd": ("READ", "from"), "wr": ("WROTE", "to")}
            action = modes[mode][0]
            tofrom = modes[mode][1]

            # Construct and print debug message
            msg = f"I2C: {action:>5s} 0x{data:04X} "
            if reg_addr is not None:
                msg += f"{tofrom:>4s} REG 0x{reg_addr:02X} of DEVICE 0x{dev_addr:02X}"
            else:
                msg += f"{tofrom:>4s} DEVICE 0x{dev_addr:02X}"
            print(msg)


    @handle_io_error
    def write_byte(self, dev_addr, data):
        """Write a byte directly to the device"""
        self.bus.write_byte(dev_addr, data)
        self._debug_log("wr", dev_addr, data)
        return data

    @handle_io_error
    def write_byte_to_reg(self, dev_addr, reg_addr, data):
        """Write a byte to a given register"""
        self.bus.write_byte_data(dev_addr, reg_addr, data)
        self._debug_log("wr", dev_addr, data, reg_addr)
        return data

    @handle_io_error
    def write_word_to_reg(self, dev_addr, reg_addr, data):
        """Write 2 bytes to a given register"""
        self.bus.write_word_data(dev_addr, reg_addr, data)
        self._debug_log("wr", dev_addr, data, reg_addr)
        return data

    @handle_io_error
    def read_byte(self, dev_addr):
        """Read a byte directly from the device"""
        data = self.bus.read_byte(dev_addr)
        self._debug_log("rd", dev_addr, data)
        return data

    @handle_io_error
    def read_byte_from_reg(self, dev_addr, reg_addr):
        """Read a byte from a given register"""
        data = self.bus.read_byte_data(dev_addr, reg_addr)
        self._debug_log("rd", dev_addr, data, reg_addr)
        return data

    @handle_io_error
    def read_word_from_reg(self, dev_addr, reg_addr):
        """ Read 2 bytes from a given register"""
        data = self.bus.read_word_data(dev_addr, reg_addr)
        self._debug_log("rd", dev_addr, data, reg_addr)
        return data


########################################################################
def detect_devices(i2c_bus, device_list=[], debug=False):
    """
    Contact all devices in `device_list` (else use all valid 8-bit addresses)
    and return a list of device addresses which respond.

    Args:
        i2c_bus <int>: I2C bus number
        device_list <[int]>: List of device addresses to search for

    Returns:
        List of device addresses which responded to call
    """
    i2c = I2C_Driver(i2c_bus, debug=debug)
    address_list = []

    if device_list == []:
        device_list = range(0x03, 0x78)

    for dev_addr in device_list:
        #start = time.time()  # Used to timeout non-acked addresses

        # Contact address and wait for response.
        try:
            i2c.read_byte(dev_addr)
        except IOError as err:
            print(err)
            # IOError: No I2C device with this address found
            pass
        else:
            address_list.append(dev_addr)

        #ts = time.time() - start
        #if ts > 0.1: raise BusError(address)

    return address_list


class BusError(Exception):
    """I2C bus has locked up due to a faulty device"""
    pass



########################################################################
if __name__ == "__main__":
    # Detect powered I2C devices on DEFAULT_I2C_BUS
    print(detect_devices(DEFAULT_I2C_BUS, debug=True))
