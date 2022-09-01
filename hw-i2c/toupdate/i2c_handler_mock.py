#!python3
"""
Mock I2C Bus Handler

####################################################################
#                                                                  #
#  All of the below code is mocked from the adafruit_i2c.py module #
#  (obtained around 2016) with some slight modification in places  #
#  and also converted to be Python 3.x compatible.                 #
#                                                                  #
####################################################################

"""

# Standard library imports
import time
import random
import logging

debugLogger = logging.getLogger(__name__)

# >>-------- CONFIGURE CONSOLE LOGGING FROM DIRECT EXECUTION --------<<
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)7s | %(name)s.%(funcName)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
# >>-----------------------------------------------------------------<<


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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

        debugLogger.info(
            "Wrote 0x{:02X}, 0x{:02X} to {} 0x{:02X}.".format(
                msbyte, lsbyte, debug_note, self.address
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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

        result = random.randint(0, 255)

        if signed is True and result > 127:
            result -= 256

        debugLogger.info(
            "Read 0x{:02X} from {} 0x{:02X}.".format(result, debug_note, self.address)
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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

        result = random.randint(0, 65535)

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
            debug_note = "device"
        else:
            debug_note = "register 0x{:02X} of device".format(register)

        result = []
        for i in range(length):
            result.append(random.randint(0, 255))

        debugLogger.info(
            "Read {} from {} 0x{:02X}.".format(result, debug_note, self.address)
        )

        return result


########################################################################
if __name__ == "__main__":

    DEVICE_ADDRESS = 0x70
    READ_REGISTER = 0x00

    i2c = I2CHandler(address=DEVICE_ADDRESS, debug=True)
    i2c.readWord(little_endian=False)
