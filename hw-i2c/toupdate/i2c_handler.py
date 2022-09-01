#!python3
"""
I2C Bus Handler for Raspberry Pi Devices

####################################################################
#                                                                  #
#  All of the below code is taken from the adafruit_i2c.py module  #
#  (obtained around 2016) with some slight modification in places  #
#  and also converted to be Python 3.x compatible.                 #
#                                                                  #
#  Changes include:                                                #
#    - Raspberry Pi revision and bus auto-detection not ported.    #
#    - Converted to be Python3.x compatible.                       #
#    - read/write8 methods renamed to read/writeByte.              #
#    - read/write16 methods renamed to read/writeWord.             #
#    - read/writeList method renamed to read/writeBlock.           #
#    - Above mentioned methods can be called with or without a     #
#      command register defined.                                   #
#                                                                  #
####################################################################

"""

# Standard library imports
import time
import logging

debugLogger = logging.getLogger(__name__)

# Third-party library imports
import smbus2


########################################################################
DEFAULT_PI_I2C_BUS = 1


########################################################################
class I2CHandler(object):
    def __init__(self, address, debug=False):
        """Initialise an I2C Handler object.

        Args
        ====
        address: <int> (8-bits)
            I2C address value of device.
            Most conveniently inserted in hex format e.g. 0x70.

        debug: <boolean>
            Set to true to print some debug statements - using logging
            module.
        """
        self.bus = smbus2.SMBus(DEFAULT_PI_I2C_BUS)
        self.set_address(address)
        self.debug = debug

    def set_address(self, address):
        """Change the target address.

        Args
        ====
        address: <int> (8-bits)
            I2C address value of device.
            Most conveniently inserted in hex format e.g. 0x70.

        """
        self.address = address

    def reverseByteOrder(self, data):
        """Reverse the byte order of an int (16-bit) or long (32-bit)
            value.

        Args
        ====
        data: <int> or <long>
            A dataset of n-bytes in numerical format.
        """
        # Courtesy Vishal Sapre
        byteCount = len(hex(data)[2:].replace("L", "")[::2])
        val = 0
        for i in range(byteCount):
            val = (val << 8) | (data & 0xFF)
            data >>= 8

        return val

    def error(self, err=""):
        """Re-raise the IOError along with a useful error message.

        Args
        ====
        err: <string>
            An error message to be raised with the IOError exception.

        Raises
        ======
            IOError: The target I2C device could not be found at the
            given address.
        """
        raise IOError("I2C error: 0x{:02X}: {}".format(self.address, err))

    def writeByte(self, value, register=None):
        """Write an 8-bit value to the specified register/address.

        Args
        ====
        value: byte
            The data to write to the device.

        register: byte
            Address of the command register to write into.

        Raises
        ======
            IOError: Device not found.
        """
        if register is None:
            write_byte = lambda: self.bus.write_byte(self.address, value)
            debug_note = "device"
        else:
            write_byte = lambda: self.bus.write_byte_data(self.address, register, value)
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            write_byte()
        except IOError as err:
            return self.error(err)

        if self.debug:
            debugLogger.info(
                "Wrote 0x{:02X} to {} 0x{:02X}.".format(value, debug_note, self.address)
            )

    def writeWord(self, value, register=None):
        """Write a 16-bit value to the specified register.

        Args
        ====
        value: byte (x2)
            The data to write to the device.

        register: byte
            Address of the command register to write into.

        Raises
        ======
            IOError: Device not found.
        """
        msbyte = 0xFF & (value >> 8)
        lsbyte = 0xFF & value

        if register is None:
            # Takes advantage of the fact a SMBus.write_byte_data()
            # call is simply an address->write->write operation.
            write_word = lambda: self.bus.write_byte_data(self.address, msbyte, lsbyte)
            debug_note = "device"
        else:
            write_word = lambda: self.bus.write_word_data(self.address, register, value)
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            write_word()
        except IOError as err:
            return self.error(err)

        if self.debug:
            debugLogger.info(
                "Wrote 0x{:02X}, 0x{:02X} to {} 0x{:02X}.".format(
                    msb, lsb, debug_note, self.address
                )
            )

    def writeBlock(self, byte_list, register=None):
        """Write an array of bytes using I2C format.

        Args
        ====
        byte_list: [list of bytes]
            A list of bytes that will be written to the defined register.

        register: byte
            Address of the command register to write into.

        Raises
        ======
            IOError: Device not found.
        """
        if register is None:
            # Takes advantage of the fact a SMBus.write_byte_data()
            # call is simply an address->write->write operation.
            write_block = lambda: self.bus.write_i2c_block_data(
                self.address, byte_list[0], byte_list[1:]
            )
            debug_note = "device"
        else:
            write_block = lambda: self.bus.write_i2c_block_data(
                self.address, register, byte_list
            )
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            write_block()
        except IOError as err:
            return self.error(err)

        if self.debug:
            debugLogger.info(
                "Wrote {} to {} 0x{:02X}.".format(byte_list, debug_note, self.address)
            )

    def readByte(self, register=None, signed=False):
        """Read a byte from the I2C device.

        Args
        ====
        register: byte
            Address of the command register to write into.

        signed: <boolean>
            Set True to process the readback data as if it is signed.

        Returns
        =======
            An <integer>. The magnitude of the result should not exceed
            255 for unsigned results or 127 for signed results e.g. it
            is an 8-bit number.

        Raises
        ======
            IOError: Device not found.
        """
        if register is None:
            read_byte = lambda: self.bus.read_byte(self.address)
            debug_note = "device"
        else:
            read_byte = lambda: self.bus.read_byte_data(self.address, register)
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            result = read_byte()
        except IOError as err:
            return self.error(err)

        if signed is True and result > 127:
            result -= 256

        if self.debug:
            debugLogger.info(
                "Read 0x{:02X} from {} 0x{:02X}.".format(
                    result, debug_note, self.address
                )
            )

        return result

    def readWord(self, register=None, signed=False, little_endian=True):
        """Read 2 bytes from the I2C device.

        Args
        ====
        register: byte
            Address of the command register to write into.

        signed: <boolean>
            Set True to process the readback data as if it is signed.

        little_endian: <boolean>
            Define whether the readback data is little-endian or
            big-endian, and therefore how the readback data should be
            processed before being returned.

        Returns
        =======
            An <integer>. The magnitude of the result should not exceed
            65535 for unsigned results or 32767 for signed results e.g.
            it is a 16-bit number.

        Raises
        ======
            IOError: Device not found.
        """
        if register is None:
            read_word = lambda: self.bus.read_word_data(self.address, 0)
            debug_note = "device"
        else:
            read_word = lambda: self.bus.read_word_data(self.address, register)
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            result = read_word()
        except IOError as err:
            return self.error(err)

        # Swap bytes if using big endian because SMBus.read_word_data()
        # assumes little endian on ARM (little endian) systems.
        if not little_endian:
            msbyte = 0x00FF & result
            lsbyte = (0xFF00 & result) >> 8
            result = (msbyte << 8) | lsbyte
        else:
            msbyte = (0xFF00 & result) >> 8
            lsbyte = 0x00FF & result

        if signed is True and result > 32767:
            result -= 65536

        if self.debug:
            debugLogger.info(
                "Read 0x{:02X}, 0x{:02X} from {} 0x{:02X}.".format(
                    msbyte, lsbyte, debug_note, self.address
                )
            )

        return result

    def readBlock(self, length, register=None):
        """Read a list of bytes from the I2C device.

        Args
        ====
        length: <int>
            The number of bytes expecting to be received.

        register: byte
            Address of the command register to write into.

        Returns
        =======
            A list of <integers>. The magnitude of the integer values
            should not exceed 255 for unsigned results or 127 for
            signed results e.g. each item is 8-bit.

        Raises
        ======
            IOError: Device not found.
        """
        if register is None:
            read_block = lambda: self.bus.read_i2c_block_data(self.address, 0, length)
            debug_note = "device"
        else:
            read_block = lambda: self.bus.read_i2c_block_data(
                self.address, register, length
            )
            debug_note = "register 0x{:02X} of device".format(register)

        try:
            result = read_block()
        except IOError as err:
            return self.error(err)

        if self.debug:
            debugLogger.info(
                "Read {} from {} 0x{:02X}.".format(result, debug_note, self.address)
            )

        return result


# Added by AHA
def detect_devices():
    """Scan the I2C bus with all valid I2C addresses to find what
    devices are on the bus.
    """
    address_list = []
    for address in range(0x03, 0x78):
        i2c = I2CHandler(address)
        start = time.time()
        try:
            i2c.readRaw8()
        except IOError:
            # IOError: No I2C device with this address present
            pass
        else:
            address_list.append(address)
        end = time.time()

        # End the detection early if the I2C bus seems to be locked up
        # Device detection should typically takes 200us-500ms per address
        if end - start > 0.1:
            raise BusError("There is a faulty device on the I2C bus")

    return address_list


########################################################################
class BusError(Exception):
    """
    Raised when an I2C bus is locked due to a faulty device
    """

    pass


########################################################################
if __name__ == "__main__":

    print("Found devices on I2C bus: {}".format(detect_devices()))

    DEVICE_ADDRESS = 0x70
    READ_REGISTER = 0x00

    i2c = I2CHandler(address=DEVICE_ADDRESS, debug=True)
    i2c.readU16(READ_REGISTER, little_endian=False)
