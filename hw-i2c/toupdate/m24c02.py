"""
Python driver module for the ST M24C02 Serial I2C Bus EEPROM

The M24C02 is a 2 Kbit (256 * 8 bits) device.  Each byte can be
read/write to individually or a page of 16 bytes can be written to.
There are 16 pages.

(Apr 2017)
Product Page: http://www.st.com/en/memories/m24c02-r.html
Datasheet: http://www.st.com/content/ccc/resource/technical/document/datasheet/b0/d8/50/40/5a/85/49/6f/DM00071904.pdf/files/DM00071904.pdf/jcr:content/translations/en.DM00071904.pdf
"""
from adafruit_i2c import Adafruit_I2C
import time

########################################################################
M24C02_DEV_ADDRESS = 0x50  # 0x50 in some cases?

WRITE_DELAY = 0.005  # seconds


class M24C02_EEPROM(object):
    """ This class allows interaction with the serial EEPROM on 
    M24C02 devices.
    """
    def __init__(self, address=M24C02_DEV_ADDRESS, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

    def _valid_byte_address(self, address):
        valid_address = True
        if address not in range(0, 256, 1):
            valid_address = False
        return valid_address

    def _valid_page_address(self, address):
        valid_address = True
        if address not in range(0, 256, 16):
            valid_address = False
        return valid_address
    
    def _valid_page_number(self, page_number):
        valid_number = True
        if page_number not in range(0, 16, 1):
            valid_number = False
        return valid_number

    def _write_byte_int(self, byte_address, data):
        # Validate the size of the data
        if data < -128 or data > 256:
            raise ValueError("'data={}' must be smaller than 1 byte".format(data))

        # Write to memory
        self.i2c.write8(byte_address, data)
        time.sleep(WRITE_DELAY)

    def _write_byte_str(self, byte_address, data):
        # Validate the size of the data
        bin_string = "".join("{:08b}".format(ord(x)) for x in str(data))
        if len(bin_string) > 8:
            raise ValueError("'data={}' must be smaller than 1 byte".format(data))
        
        # Write to memory
        data = int(bin_string, 2)
        self.i2c.write8(byte_address, data)
        time.sleep(WRITE_DELAY)


    def write_byte(self, byte_address, data):
        """ Write a byte of data to the byte address `byte_address`
        
        PARAMETERS
        ==========
        byte_address: <int>
            A integer address value between 0 (first location in memory)
            and 255 (last location) [for 2kb device].

        data: <str/+int, 8-bit>
            An 8-bit value of data to be stored in the desired memory
            location.

        RETURNS
        =======
        Nothing.

        RAISES
        ======
        ValueError: Invalid value- `data` is larger than 1 byte, or 
                    not a string or integer.
        TypeError: Invalid byte address in memory

        """
        # Validate the memory address
        if not self._valid_byte_address(byte_address):
            raise ValueError("'{}' is not a valid 8-bit byte-address ".format(byte_address))

        datatype = type(data)
        if datatype == str:
            self._write_byte_str(byte_address, data)
        elif datatype == int:
            self._write_byte_int(byte_address, data)
        else:
            raise TypeError("'data={}' should be <str> or <int>".format(data))

    def write_str_to_page(self, page_number, data):
        """ Write up to a page of data to a page

        DESCRIPTION
        ===========
        `data` can be any length although it should ideally be less than
        or equal to the length of a page (16 bytes). If data is greater
        than 16-bytes, then the M24C02 address counter will rollover to
        the start of the same page. That is, only one page can be
        written to in a single operation.
        
        PARAMETERS
        ==========
        data: <list of [str]>
            A list of ASCII characters, with a maximum length of 16.

        page_number: <int>
            The page number to write to as an integer multiple of 16 
            between 0 and 255 (because there are 16 pages available).
            Valid page addresses are:
            [
                  0,  16,  32,  48,  64,  80,  96, 112,
                128, 144, 160, 176, 192, 208, 224, 240
            ]
            Therefore, valid page numbers are:
            [
                 0,  1,  2,  3,  4,  5,  6, 7,
                 8,  9, 10, 11, 12, 13, 14, 15
            ]

        RETURNS
        =======
        Nothing.
        """
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        # Validate the memory address
        if not self._valid_page_address(page_address):
            raise ValueError(
                "'{}' is not a valid page-address. It should be a multiple of 16 from 0 to 240."
                .format(page_address)
                )

        # Check that data is a string
        data_type = type(data)
        if data_type != str:
            raise TypeError("'data={}' must be <str>".format(data))
        
        # Convert the character string to a list of bytes
        bin_string = " ".join("{:08b}".format(ord(x)) for x in str(data))
        bin_list = [int(byte, 2) for byte in bin_string.split(" ")]
                   
        # Check the number of bytes will fit within the available space
        if len(bin_list) > 16:
            raise IOError("'data={}' must be smaller than 16 bytes (1char=1byte)".format(data))

        # Write to EEPROM
        self.i2c.writeList(page_address, bin_list)
        time.sleep(WRITE_DELAY)

    def read_byte(self, byte_address):
        # Validate the memory address
        if not self._valid_byte_address(byte_address):
            raise TypeError("'0b{0:08b}' is not a valid 8-bit byte address ".format(byte_address))
        # Read the byte
        return self.i2c.readU8(byte_address)

    def read_page(self, page_number):
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        # Validate the memory address
        if not self._valid_byte_address(page_address):
            raise TypeError("'0b{0:08b}' is not a valid page address ".format(page_address))
        # Read the page data
        return self.i2c.readList(page_address, 16)

    def clear_page(self, page_number):
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        self.i2c.writeList(page_address, [0xFF]*16)
        time.sleep(WRITE_DELAY)

    def clear_memory(self):
        for page_address in range(0, 16):
            self.clear_page(page_address)

    def _print(self, message):
        if self.debug is True:
            print message
