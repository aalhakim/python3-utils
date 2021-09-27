#!python3

"""
Print Text, Barcodes and more on a Zebra GK420t label printer using
EPL2. Tested with Zebra GK420t only.

On Linux systems - such as the raspberry Pi - the printer can only be
used by configureing the value PRINTER_QUEUE_POSITION to the position of
the printer in the Linux printer list.

To find the position of the printer, simply run this script once, and
the list will be printed out. Then edit the value of
PRINTER_QUEUE_POSITION and run the script again.

Contributed by: Kyle McInnes, Ali H Al-Hakim
Last Updated: 21 April 2020
"""

# Standard Library Imports
from __future__ import print_function
import binascii
import sys

# Third-Party Library Imports
# from zebra import zebra
import pyqrcode

# Local Library Import
from zebra_latin1 import zebra


if sys.platform.lower().startswith("win"):
    IS_WINDOWS = True
    from infi.devicemanager import DeviceManager
    import win32print
else:
    IS_WINDOWS = False
    import subprocess


########################################################################
# Select which position the desired printer is in in the printer queue
# for Unix devices.
PRINTER_QUEUE_POSITION = 0

# Choose whether to auto-calibrate the printer for a new label scroll.
AUTOCALIBRATE = False


########################################################################
# The size of a dot printed by the Zebra GK420t label printer.
# DO NOT CHANGE
DOT_MM = 0.125  # mm

# How thick a single module should be. Typically this should be set to
# 1 or 2
DOTS_PER_MODULE = 1

# The size of modules (black or white barcode features)
MODULE = DOTS_PER_MODULE
NARROW_BAR = MODULE
WIDE_BAR = NARROW_BAR * 3
SYMBOL = NARROW_BAR * 11

# The amount of whitespace that should be provided to the left and right
# of a barcode to ensure readability by a scanner.
QUIET_ZONE = NARROW_BAR * 11

# A symbol set used to help the below code calculate if two characters
# are numeric and therefore can be combined into a single symbol (used
# for Code-128 encoding).
# DO NOT CHANGE
ALPHA_RANGE = ["{:1d}".format(charpair) for charpair in range(0, 10)]


BINARY_TO_HEX = {
    "0000": "0",
    "0001": "1",
    "0010": "2",
    "0011": "3",
    "0100": "4",
    "0101": "5",
    "0110": "6",
    "0111": "7",
    "1000": "8",
    "1001": "9",
    "1010": "A",
    "1011": "B",
    "1100": "C",
    "1101": "D",
    "1110": "E",
    "1111": "F",
}


# ######################################################################


class ZebraPrinter(zebra):
    def __init__(self, queue=None):
        super(ZebraPrinter, self).__init__(queue)

        self.keywords = ["GK420", "GX420"]
        self._find_printer()

    def _find_printer(self, keywords=None):
        """Find a printer with `keyword` in the name."""
        if keywords is not None:
            self.keywords = keywords

        print("Looking for printer...", end=" ")
        if IS_WINDOWS:
            self.printer = self._find_printer_win()
        else:
            self.printer = self._find_printer_unix()

        return self.printer is not None

    def _find_printer_win(self):
        # Obtain a list of previously attached devices from the system
        # printer device lists
        installed_printers = self.getqueues()

        # Obtain a list of all currently attached devices
        attached_devices = self._get_device_list()

        # Check if A ZDesigner GK420 printer is available.
        found_printer = None
        for device in attached_devices:
            for keyword in self.keywords:
                if keyword in device.description:
                    if device.children[0].friendly_name in installed_printers:
                        found_printer = device  # has type <DeviceManager object>
                        self.setqueue(device.children[0].friendly_name)
                        break

        if found_printer is not None:
            print("found '{}'".format(found_printer.children[0].friendly_name))
        else:
            print("failed.")

        return found_printer

    def _find_printer_unix(self):
        # Obtain a list of previously attached devices from the system
        # printer device lists
        installed_printers = self.getqueues()

        # Obtain a list of all currently attached devices
        attached_devices = self._get_device_list()

        # Look through the list of attached devices to see if any of
        # them contain the keywords. If True a suitable printer may be
        # available
        found_device = None
        for device in attached_devices:
            for keyword in self.keywords:
                if keyword in device:
                    found_device = device
                    break

            if found_device:
                break

        # If a possible match is found look through the installed
        # printer list to check if this device is setup here too.
        found_printer = None
        for printer in installed_printers:
            # Only the keyword which matched the avaialble device is used.
            if keyword in printer:
                found_printer = printer  # has type: <str>
                self.setqueue(printer)
                break

        if found_printer is not None:
            print("found '{}'".format(found_printer))
        elif found_device is not None:
            print(
                "found '{}' but it is not setup at localhost:631/admin".format(
                    found_device
                )
            )
        else:
            print("failed.")

        return found_printer

    def _get_device_list(self):
        """
        Return a list of attached devices.
        """
        if IS_WINDOWS:
            dm = DeviceManager()
            devices = dm.all_devices
        else:
            try:
                usblist = subprocess.check_output(["lsusb"], universal_newlines=True)
            except subprocess.CalledProcessError:
                devices = []
            else:
                devices = usblist.split("\n")

        return devices

    def is_available(self):
        """Indicate if printer is available."""
        if self.printer is None:
            result = self._find_printer()

        else:
            if IS_WINDOWS:
                result = self._is_available_win()
            else:
                result = self._is_available_unix()

        return result

    def _is_available_win(self):
        """Find a previously discovered printer, for Windows."""
        devices = self._get_device_list()
        is_available = False
        for device in devices:
            if device.description == self.printer.description:
                is_available = True

        return is_available

    def _is_available_unix(self):
        """Find a previously discovered printer, for Unix.

        This method is far from perfect. It's just seeing what devices
        are attached on the USB port but isn't actually confirming
        any devices found are properly set up with the CUPS server.

        However, it is assumed that if the device has been attached via
        USB, it probably was also setup with CUPS.

        Another possible issue will occur if two similar printers are
        used or attached at the same time. This code is not able to
        distinguish one similarly named printer from another - although
        (TODO) a future developer may wantr to see if the lsusb ID
        information can be used to manage this.
        """
        devices = self._get_device_list()
        is_available = False
        for line in devices:
            for keyword in self.keywords:
                if keyword in line:
                    is_available = True

        return is_available


def detect_printer():
    """Look for 'GK420' tags in printer list.

    This code has been tested on a Windows machine and a Raspberry Pi
    (Ubuntu).
    """
    SEARCH_STRING = "GK420"
    z = zebra()

    # Identify which operating system is being used and find the printer
    # printer_present = False
    if IS_WINDOWS:
        print("Running on Windows...", end=" ")

        # Obtain a list of previously attached devices from the system
        # printer device lists
        printer_queues = z._getqueues_win()

        # Obtain a list of all currently attached devices
        dm = DeviceManager()
        devices = dm.all_devices

        # Check if A ZDesigner GK420 printer is available.
        for dev in devices:
            if SEARCH_STRING in dev.description:
                if dev.children[0].friendly_name in printer_queues:
                    print("found printer: {}".format(dev.children[0].friendly_name))
                    z.setqueue(dev.children[0].friendly_name)
                    printer_present = dev.children[0].friendly_name
                    break
            else:
                printer_present = False

    else:
        print("Running on Unix... configure printer setting:")
        try:
            printers = [device for device in z.getqueues() if SEARCH_STRING in device]
            print("")
            for i, printer in enumerate(printers):
                print("  {}: {}".format(i, printer))

            printer_present = printers[PRINTER_QUEUE_POSITION]
            z.setqueue(printer_present)

        except Exception:
            print("Check that 'PRINTER_QUEUE_POSITION' is correctly configured.")
            printer_present = False

    if printer_present:
        print("Attached to: {}".format(printers[PRINTER_QUEUE_POSITION]))
    else:
        print("Unable to find '{}' printer.".format(SEARCH_STRING))

    return z


# ######################################################################
def binary_string_to_hex_string(binary_string, debug=False):
    """
    binary_string is an object of type string but representing 1s and 0s
    only. e.g.  binary_string = 00110011001100110011

    If the string is not provided in chunks of 8 (e.g. a byte) then the
    string will be 1-padded from the front. e.g. 11 -> 00000011
    """
    binary_string = binary_string.replace("\x0D", "").replace("\x0A", "")
    len_binstr = len(binary_string)
    remainder = len_binstr % 8
    if remainder != 0:
        binary_string = ("1" * (8 - remainder)) + binary_string
        len_binstr = len(binary_string)

    hex_string = ""
    for n in range(0, len_binstr, 4):
        nibble = binary_string[n : n + 4]
        hex_string += BINARY_TO_HEX[nibble]
        # print("Nibble: ", n, nibble)
        if debug is True:
            print(nibble, end="")

    if debug is True:
        print(" = " + hex_string)

    return hex_string


def hex_string_to_latin1_string(hex_string):
    """Convert a hexadecimal string into a latin1 encoded string."""
    byte_string = binascii.unhexlify(hex_string)
    return byte_string.decode("latin-1")


def binary_to_byte_string(binary_data, debug=False):
    """Convert a binary data block into a byte string."""
    hex_string = ""
    for row in binary_data:
        hex_string += binary_string_to_hex_string(row, debug)
    byte_string = hex_string_to_latin1_string(hex_string)

    return byte_string


def create_binary_qr(data, scale, version=None, include_qz=True, debug=False):
    """Create a binary image of a QR code

    Args:
        data <str>: Information to be encoded into a QR code.
        scale <int>: A multiplier to scale the size of the QR code.
        version <None> or <int>: If None then pyqrcode will determine
            the minimum required QR code version. If an integer, a
            QR code of this version will be called. Version must be
            between 1 and 40.
        include_qz <boolean>: If set to False the quiet zone will be
            removed. This option can be used if you want to position the
            QR code manually and dictate your own quiet zone size.

    Raises:

    """
    qr = pyqrcode.create(data, error="H", version=version)

    # Obtain a binary representation of the QR code
    qr_text = qr.text()
    # Remove leading or trailing line breaks and spaces
    qr_text = qr_text.strip()
    # Invert the image
    qr_text = qr_text.replace("1", "A").replace("0", "1").replace("A", "0")
    # Break up into a list of rows
    qr_text = qr_text.split("\n")

    # Increase the size of the barcode as pyqrcode provides a binary
    # version with 1x1 modules. However, do not scale the quiet
    # zones.
    skip_count = 0
    for row in qr_text:
        if "0" not in row:
            skip_count += 1

    if include_qz:
        qz_index = int((skip_count / 2) - 1)
    else:
        qz_index = int(skip_count / 2)

    binary_data = []
    for row in qr_text[qz_index:-qz_index]:
        new_row = ""
        for char in row[qz_index:-qz_index]:
            new_row += char * scale
        for n in range(scale):
            binary_data.append(new_row)

    # Convert the QR Code data into a format compatible with the
    # 'GW' EPL2 command binary image printing method.
    byte_string = binary_to_byte_string(binary_data, debug)

    return (binary_data, byte_string)


########################################################################
def mm2dot(size_mm):
    """Convert a mm value into a dot value.

    Args
    ----
    size_mm: <float>
        Size in mm.
    """
    return int(size_mm / DOT_MM)


def dot2mm(size_dot):
    """Convert a dot value into a mm value.
    Args
    ----
    size_dot: <int>
        Size in dots.
    """
    return size_dot * DOT_MM


########################################################################
class EplCommand(object):
    def __init__(
        self,
        printer,
        width_mm,
        length_mm,
        columns=1,
        gap_mm=2,
        x_offset_mm=0.0,
        y_offset_mm=0.0,
    ):
        assert int(
            columns
        ), "Invalid_setting (columns of {}): columns must be an integer >= 1".format(
            columns
        )
        self.printer = printer
        self.active_column = 0

        self.set_x_offset(x_offset_mm)
        self.set_y_offset(y_offset_mm)

        self.command_clear_buffer = "N\n"
        self.command_print_label = "P1\n"
        self.command = self.command_clear_buffer

        self.set_codepage()
        self.set_size_properties(
            width_mm, length_mm, columns, gap_mm, force_configure=False
        )
        self.set_print_speed()
        self.set_darkness_level()
        self.set_print_direction()

        if AUTOCALIBRATE:
            self.auto_sense()

        self.configure()
        # self.send_command()

    def send_command(self, command=None):
        if command is None:
            command = self.command

        # print("Command:\n{}".format(command))

        if self.printer.is_available():
            self.printer.output(command)
        else:
            print("  >> ERROR: printer not available")

        self.active_column = 0
        self.clear_command()

    def clear_command(self):
        self.command = self.command_clear_buffer

    def auto_sense(self):
        self.send_command("xa\n")

    def set_reference(self, pos_x, pos_y):
        """
        'R' Command: Moves the reference point for the X and Y axes.
        """
        self.send_command("R{},{}\n".format(pos_x, pos_y))

    def next_label(self):
        self.active_column += 1
        if self.active_column == self.columns:
            self.encode_print_label()
            self.send_command(self.command)

    def set_size_properties(
        self,
        label_width_mm,
        label_length_mm,
        columns,
        label_gap_mm,
        force_configure=True,
    ):
        """Define core dimensional properties of the label reel."""
        self._set_columns_and_gap_size(columns, label_gap_mm)
        self._set_label_width(label_width_mm, columns)
        self._set_label_length(label_length_mm)

        if force_configure is True:
            self.configure()

    def _set_columns_and_gap_size(self, columns, label_gap_mm):
        """Define the number of columns of labels on the reel, and the
        size of the gap between columns.
        """
        self.columns = columns
        self.label_gap_mm = label_gap_mm
        self.label_gap_dot = int(label_gap_mm / DOT_MM)

    def set_codepage(self, lang="1"):
        """
        'I' Command: Set codepage / language support.
        """
        assert (
            0 <= int(lang) <= 15
        ), "Invalid_setting (lang of {}): 18 <= lang <= 240".format(lang)
        self._codepage = "I8,{},044\n".format(lang)
        pass

    def _set_label_length(self, label_length_mm):
        """
        'Q' Command: Set label length.

        To work correctly, make sure self.set_columns_and_gap_size() has
        been called first.
        """
        self.label_length_mm = label_length_mm
        self.label_length_dot = int(label_length_mm / DOT_MM)

        assert (
            16 <= self.label_gap_dot <= 240
        ), "Invalid setting (gap_length of {}): 16 <= gap_length <= 240".format(
            self.label_gap_dot
        )
        self._form_length = "Q{},{}\n".format(self.label_length_dot, self.label_gap_dot)

    def _set_label_width(self, label_width_mm, columns):
        """
        'q' Command: Set reel width.

        To work correctly, make sure self.set_columns_and_gap_size() has
        been called first.
        """
        self.label_width_mm = label_width_mm
        self.label_width_dot = int(label_width_mm / DOT_MM)

        reel_width_dot = int(
            (columns * self.label_width_dot) + ((columns - 1) * self.label_gap_dot)
        )
        self._reel_width = "q{}\n".format(reel_width_dot)

    def set_print_speed(self, speed=3):
        """
        'S' Command: Set printer output speed.
            2=50mm/s, 3=75mm/2, 4=100mm/s, 5=125mm/s
        """
        assert 2 <= speed <= 5, "Invalid setting (speed of {}): 2 <= speed <= 5".format(
            speed
        )
        self._print_speed = "S{}\n".format(speed)

    def set_darkness_level(self, level=13):
        """
        'D' Command: Set printer burn-rate, thus darkness level
            0 Lightest to 15 Darkest  (default is 8 for GK420)
        """
        self._darkness_level = "D{}\n".format(level)

    def set_cut(self, status=True, quantity=1):
        """
        'OC' Command: Enable or disable cut after print functionality,
        for printers that have the cutter accessory.
        """
        if status is True:
            # Enables the cutter to cut after 0 prints.
            self.command += "OC{}\n".format(quantity)
        else:
            # Resets all options to disabled
            self.command += "O\n"

    def set_print_direction(self, direction="B"):
        """
        'Z' Command: Select whether to print from the top or bottom of
                     the image buffer, and therefore what orientation
                     the print should come out at.
            T: Print from the top of the image buffer
            B: Bring from the bottom of the image buffer
        """
        self.orientation = "Z{}\n".format(direction)

    def set_x_offset(self, offset_mm):
        """Change the x_offset value."""
        self.x_offset_mm = offset_mm
        self.x_offset_dot = int(offset_mm / DOT_MM)

    def set_y_offset(self, offset_mm):
        """Change the y_offset value."""
        self.y_offset_mm = offset_mm
        self.y_offset_dot = int(offset_mm / DOT_MM)

    def encode_barcode_c128(self, string, start_x=0, start_y=0, height_dot=10):
        """
        'B' Command: Encode a barcode
            string = what the barcode should represent
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
            height_dot = bar code height, in dots
        """
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: barcode x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: barcode y position can't be negative so it has been forced to 0")

        narrow_bar = 1
        wide_bar = 3
        # start_x (in dots)
        # start_y (in dots)
        # rotation = 0: 0 degrees
        # barcode code type = 1: Code-128(ABC)
        # narrow bar width
        # wide bar width
        # barcode height (in dots)
        # print human readable code (B) or not (N)
        barcode = 'B{},{},0,1,{},{},{},N,"{}"\n'.format(
            start_x, start_y, narrow_bar, wide_bar, height_dot, string
        )
        self.command += barcode

    def encode_qr_code(self, data, start_x=0, start_y=0):
        """
        'b' Command: Encode a 2D barcode (QR format)
            data = what data the QR should encode
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
        """
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: barcode x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: barcode y position can't be negative so it has been forced to 0")

        byte_size = 0
        scale_factor = 3  # 3 is printer default. Options [1-99]
        error_correction = "M"  # Options L, M, Q, H
        # b{}: 2D barcode + 4-digit number specifying number of bytes to encode
        # {}: start_x (in dots)
        # {}: start_y (in dots)
        # Q: QR code format
        # m2: Code model - default: Model 2
        # s{}: Scale factor
        # e{}: Error correction level
        # iA: Data input mode - default: Automatic data select
        # "{}": Data for encoding
        barcode = 'b{},{},{},Q,m2,s{},e{},iA,"{}"\n'.format(
            byte_size, start_x, start_y, scale_factor, error_correction, data
        )
        self.command += barcode

    def encode_aztec_code(self, data, start_x=0, start_y=0):
        """
        'b' Command: Encode a 2D barcode (Aztec format)
            data = what data the QR should encode
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
        """
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: barcode x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: barcode y position can't be negative so it has been forced to 0")

        scale_factor = 3
        error_correction = 0
        # b{}: 2D barcode +  start_x (in dots)
        # {}: start_y (in dots)
        # A: Aztec bar code format
        # d{}: Symbol scaling
        # e{}: Symbol layer and/or error correction
        # "{}": Data for encoding.
        barcode = 'b{},{},A,d{},e{},"{}"\n'.format(
            start_x, start_y, scale_factor, error_correction, data
        )
        self.command += barcode

    def encode_binary_image(
        self, byte_string, width_dot, length_dot, start_x=0, start_y=0
    ):
        """
        'GW' Command: Direct graphic write. Send the printer a string
                      of bytes where 0 represents black and 1 represents
                      white.
            binary_data = A list of strings, where each string is a
                          binary number of equal length to each other.
                          The length of each string will translate to
                          the width of the image. The number of rows in
                          the list translates to the height of the
                          image.
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
        """
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: barcode x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: barcode y position can't be negative so it has been forced to 0")

        width_bytes = int(width_dot / 8)

        # Format: GW<start_x>,<start_y>,<width>,<length>\data\n
        # start_x (in dots)
        # start_y (in dots)
        # width (in bytes)
        # length (in dots)
        # data = A continuous string of raw bytes represented in hex
        #   e.g. 'F0F6F6F0' with width=2 will draw a (very small) box.
        #        However, the hex string must represented raw bytes.
        #        when sent to the printer e.g b'\xf0\xf6\xf6\xf0'
        image = "GW{},{},{},{}\n{}\n".format(
            start_x, start_y, width_bytes, length_dot, byte_string
        )
        self.command += image

    def encode_text(
        self,
        string,
        start_x,
        start_y,
        font_size=3,
        rotate=0,
        expand_x=1,
        expand_y=1,
        invert=False,
    ):
        """
        'A' Command: Encode text
            string = what text to display
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
            font_size = size of the font to display:
                1:6pt, 2:7pt, 3:10pt, 4:12pt, 5:24pt
            rotate = rotate font in 90 degree increments:
                0, 90, 180, 270
            expand_x = expand text horizontally (1-6)
            expand_y = expand text vertically (1-9)
            invert = print black on white (False) or white on black (True)
        """
        assert (
            1 <= font_size <= 5
        ), "Invalid setting (font_size of {}): 1 <= font_size <= 5".format(font_size)
        assert (
            invert == True or invert == False
        ), "Invalid setting: (invert of {}): invert can only be True or False".format(
            invert
        )
        if invert:
            invert = "R"
        else:
            invert = "N"

        # Validate start position, manage column position and apply offsets.
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: text x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: text y position can't be negative so it has been forced to 0")

        expand_x = int(expand_x)
        expand_y = int(expand_y)

        # Process rotation data
        if rotate == 0:
            rotate_id = 0
        elif rotate == 90:
            rotate_id = 1
        elif rotate == 180:
            rotate_id = 2
        elif rotate == 270:
            rotate_id = 3
        else:
            print("  >> WARN: Unknown rotation '{}' so 0 degrees used.".format(rotate))
            rotate_id = 0

        # start_x (in dots)
        # start_y (in dots)
        # rotation = 0: 0 degrees
        # font_size
        # expand_x
        # expand_y
        # reverse colour image (R) or normal (N)
        text = 'A{},{},{},{},{},{},{},"{}"\n'.format(
            start_x, start_y, rotate_id, font_size, expand_x, expand_y, invert, string
        )
        self.command += text

    def encode_line(self, start_x, start_y, width_dot, length_dot):
        """
        'LO' Command: Draw a line with specified thickness

        Args:
            start_x <int>: X position of top-left corner of the box.
            start_y <int> Y position of top-left corner of the box.
            width_dot <int>: The width of the box, in dots.
            length_dot <int>: The length of the box, in dots.
        """
        # Validate start position, manage column position and apply offsets.
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: text x position can't be negative so it has been forced to 0")

        # The offset is negated because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. This
        # means a positive offset will shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: text y position can't be negative so it has been forced to 0")

        width_dot = int(width_dot)
        length_dot = int(length_dot)

        line = "LO{0},{1},{2},{3}\n".format(start_x, start_y, width_dot, length_dot)
        self.command += line

    def encode_box(self, width_dot, length_dot, stroke_dot, start_x, start_y):
        """
        Draw 4 lines to draw a box using the 'LO' command.

        Args:
            width_dot <int>: The width of the box, in dots.
            length_dot <int>: The length of the box, in dots.
            stroke_dot <int>: The thickness of the box lines, in dots.
            start_x <int>: X position of top-left corner of the box.
            start_y <int> Y position of top-left corner of the box.
        """
        # Validate start position, manage column position and apply offsets.
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.label_gap_dot) * self.active_column)
            + self.x_offset_dot
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: text x position can't be negative so it has been forced to 0")

        # The offset is negated because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. This
        # means a positive offset will shift the object up.
        start_y = int(start_y) - self.y_offset_dot
        if start_y < 0:
            start_y = 0
            # print("WARNING: text y position can't be negative so it has been forced to 0")

        stroke_dot = int(stroke_dot)

        end_x = int(start_x + width_dot - stroke_dot)
        end_y = int(start_y + length_dot - stroke_dot)

        box = (
            "LO{0},{1},{2},{3}\n"  # Top horizontal line
            "LO{0},{1},{3},{4}\n"  # Left vertical line
            "LO{0},{5},{2},{3}\n"  # Bottom horizontal line
            "LO{6},{1},{3},{4}\n".format(  # Right vertical line
                start_x,
                start_y,  # 0, 1
                width_dot,
                stroke_dot,
                length_dot,  # 2, 3, 4
                end_y,
                end_x,
            )  # 5, 6
        )
        self.command += box

    def encode_print_label(self):
        """
        Encode the print label command into self.command
        """
        self.command += self.command_print_label

    def configure(self):
        """
        Configure the fixed printer settings.
        This requires the following settings to be set:
          + codepage
          + label_length
          + reel_width
          + print_speed
          + darkness_level
        """
        command = self.command_clear_buffer
        command += self._codepage
        command += self._form_length
        command += self._reel_width
        command += self._print_speed
        command += self._darkness_level
        self.send_command(command)


class Printer(object):
    def __init__(
        self,
        printer,
        label_width_mm,
        label_length_mm,
        label_length_adjust_mm,
        columns,
        gap_size_mm,
        x_offset_mm=0.0,
        y_offset_mm=0.0,
    ):
        """
        Args:
            printer <obj>: A system printer handler object- obtained
                from detect_printer().
            label_width_mm <float>: The width of a label, in mm.
            label_length_mm <float>: the length of a label, in mm.
            columns <int>: The number of columns in a scroll.
            gap_size_mm <float>: The size of the gap between labels on
                a scroll, in mm.
            x_offset_mm <float>: Offset any printed items by this
                amount along the x-axis, in mm.
            y_offset_mm <float>: Offset and printed items by this
                amount along the y-axis, in mm.
        """
        self.printer = printer
        self.label = Label(label_width_mm, label_length_mm)
        self.columns = columns
        self.commander = EplCommand(
            printer,
            label_width_mm,
            label_length_mm + label_length_adjust_mm,
            columns,
            gap_size_mm,
            x_offset_mm,
            y_offset_mm,
        )

    def align(self, obj, x_align, y_align):
        """
        Return alignment locations (in dot position) for the given
        object.

        Args:
            obj <obj>: An printable object instance, such as Text()
                Barcode(), BinaryImage(), e.t.c.
            x_align <str>/<int>: "L"eft, "C"entre, "R"ight, or an
                integer representing in dots where the object should be
                printed from.
            y_align <str>/<int>: "T"op, "M"iddle, "B"ottom, or an
                integer representing in dots where the object should be
                printed from.

        Returns:
            Returns two integers for x_pos and y_pos. If there is an
            error, the returned co-ordinates will be (0, 0) which is
            the same as top-left positioning.
        """
        if type(x_align) == str:
            x_align = x_align.upper()
            if x_align == "C" or x_align == "CENTRE":
                x_pos_dot = int((self.label.width_dot - obj.width_dot) / 2.0)
            elif x_align == "R" or x_align == "RIGHT":
                x_pos_dot = int(self.label.width_dot - obj.width_dot)
            elif x_align == "L" or x_align == "LEFT":
                x_pos_dot = int(0)
            else:
                print("WARN: Incorrect x-alignment input. Left alignment returned.")
                x_pos_dot = int(0)

        elif type(x_align) == int:
            xpos_dot = int(x_align)

        else:
            print("WARN: Incorrect x-alignment input. Left alignment returned.")
            x_pos_dot = int(0)

        if type(y_align) == str:
            # For nicer interpretation, some objects use 'height' or some
            # objects use 'length' to represent y-direction dimensions.
            try:
                ydim = obj.length_dot
            except AttributeError:
                # AttributeError: 'X' object has no attribute 'length_dot'
                ydim = obj.height_dot

            y_align = y_align.upper()
            if y_align == "M" or y_align == "MID" or y_align == "MIDDLE":
                y_pos_dot = int((self.label.length_dot - ydim) / 2.0)
            elif y_align == "B" or y_align == "BOT" or y_align == "BOTTOM":
                y_pos_dot = int(self.label.length_dot - ydim)
            elif y_align == "T" or y_align == "TOP":
                y_pos_dot = int(0)
            else:
                print("WARN: Incorrect y-alignment input. Top alignment returned.")
                y_pos_dot = int(0)

        elif type(y_align) == int:
            ypos_dot = int(y_align)

        else:
            print("WARN: Incorrect y-alignment input. Top alignment returned.")
            ypos_dot = int(0)

        return (x_pos_dot, y_pos_dot)

    def cut(self, status, quantity=1):
        """
        If a cutter is available, cut the scroll.
        """
        self.commander.set_cut(status, quantity)
        self.commander.send_command()

    def print_calibrator(self):
        # Draw a box almost equal to the label size, starting from the
        # top-left corner. This should provide a visual indication of
        # where the origin and full print zone is.
        objBox = Box(
            self.label.width_mm - 1.0, self.label.length_mm - 1.0, stroke_mm=0.125
        )
        xpos, ypos = self.align(objBox, x_align="left", y_align="top")

        # Write some information to help the user calibrate the
        # software commands.
        objText_text1 = Text("Increase", font_size=1)
        text1_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text1_xpos += int(5)
        text1_ypos = ypos + int(5)

        objText_text2 = Text("LENGTH_ADJUST", font_size=1)
        text2_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text2_xpos += int(5)
        text2_ypos = ypos + int(20)

        objText_text3 = Text("to move up", font_size=1)
        text3_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text3_xpos += int(5)
        text3_ypos = ypos + int(35)

        objText_text4 = Text("Decrease", font_size=1)
        text4_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text4_xpos += int(5)
        text4_ypos = ypos + int(60)

        objText_text5 = Text("X_OFFSET", font_size=1)
        text5_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text5_xpos += int(5)
        text5_ypos = ypos + int(75)

        objText_text6 = Text("to move left", font_size=1)
        text6_xpos, _ = self.align(objText_text1, x_align="left", y_align="top")
        text6_xpos += int(5)
        text6_ypos = ypos + int(90)

        # Submit the print command.
        for n in range(1, self.columns + 1):
            self.commander.encode_box(
                width_dot=objBox.width_dot,
                length_dot=objBox.length_dot,
                stroke_dot=objBox.stroke_dot,
                start_x=xpos,
                start_y=ypos,
            )

            self.commander.encode_text(
                objText_text1.text, start_x=text1_xpos, start_y=text1_ypos, font_size=1
            )

            self.commander.encode_text(
                objText_text2.text, start_x=text2_xpos, start_y=text2_ypos, font_size=1
            )

            self.commander.encode_text(
                objText_text3.text, start_x=text3_xpos, start_y=text3_ypos, font_size=1
            )

            self.commander.encode_text(
                objText_text4.text, start_x=text4_xpos, start_y=text4_ypos, font_size=1
            )

            self.commander.encode_text(
                objText_text5.text, start_x=text5_xpos, start_y=text5_ypos, font_size=1
            )

            self.commander.encode_text(
                objText_text6.text, start_x=text6_xpos, start_y=text6_ypos, font_size=1
            )

            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_barcode(
        self, text, quantity=1, bc_height_mm=None, invert=False, override_exit=False
    ):
        """Print a barcode with some text below it.

        Args:
            text: The string the barcode and text should display.
            quantity: How many barcodes that should be consecutively
                printer.
            invert: Set to True to display the text as white on a black
                background. Set to False to display the text as normal.
            override_exit: Set to True to stop the printer processing a
                row. This is necessary if there are multiple labels per
                row.
            bc_height_mm: Define how tall the barcode portion of the
                label should be.

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        # Determine a height for the barcode if none is given.
        if bc_height_mm is None:
            bc_height_mm = self.label.height_mm / 2.0

        # Create the Barcode object. The barcode object may crop the
        # text if it is too long to fit on the label. Therefore, the
        # string may be shorted.
        objBarcode = Barcode(
            text, height_mm=bc_height_mm, max_width_mm=self.label.width_mm
        )
        barcode_text = objBarcode.text

        # Align the barcode to top-centre.
        bc_xpos, bc_ypos = self.align(objBarcode, x_align="centre", y_align="top")

        # Identify what font size to use by checking what will fit in
        # the available width.
        for font_size in reversed(range(1, 4)):
            objText = Text(barcode_text, font_size=font_size)
            # If the text length is almost longer than the label width
            # change the size of the font.
            if objText.width_mm < self.label.width_mm - 2.0:
                break
            else:
                print("WARN: Text '{}' will not fit on the label".format(barcode_text))

        # Align the text to be central below the barcode. Define the
        # gap between the barcode and the text as a proportion of the
        # text height.
        text_xpos, _ = self.align(objText, x_align="centre", y_align="top")
        text_ypos = objBarcode.height_dot + int(
            (4 - font_size) * 0.2 * objText.height_dot
        )

        # Submit the print command.
        for n in range(1, quantity + 1):
            self.commander.encode_barcode_c128(
                objBarcode.text,
                start_x=bc_xpos,
                start_y=bc_ypos,
                height_dot=objBarcode.height_dot,
            )

            self.commander.encode_text(
                objText.text,
                start_x=text_xpos,
                start_y=text_ypos,
                font_size=objText.font_size,
                invert=invert,
            )

            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_binary_image(
        self, binary_data, quantity=1, centre=True, override_exit=False
    ):
        """Print a barcode with some text below it.

        Args:
            binary_data <str>: A string of binary information (only 1,
                0 and \n allowed) which will be converted to black or
                white space on the label.
            quantity <int>: How many barcodes that should be
                consecutively printed.
            centre <bool>: Set True to centre the graphics on the label
                else the graphics will be drawn from the top-right
                (i.e. the origin).

        Returns:
            Nothing.

        Raises:
            Nothing.
        """

        hex_string = ""
        for row in binary_data:
            hex_string += binary_string_to_hex_string(row)
        byte_string = hex_string_to_latin1_string(hex_string)

        image = BinaryImage(binary_data)

        if centre is True:
            xpos, ypos = self.align(image, x_align="centre", y_align="middle")
        else:
            xpos, ypos = self.align(image, x_align="left", y_align="top")

        for n in range(1, quantity + 1):
            self.commander.encode_binary_image(
                byte_string,
                width_dot=image.width_dot,
                length_dot=image.length_dot,
                start_x=xpos,
                start_y=ypos,
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_box(
        self,
        width_mm,
        length_mm,
        stroke_mm,
        x_align="C",
        y_align="M",
        quantity=1,
        override_exit=False,
    ):
        """Print a box of specified height and length.

        Args:
            width_mm <float>: The length of the box, in mm
            length_mm <float>: The height of the box, in mm
            stroke_mm <float>: The thickness of the lines, in mm
            x_align <str>/<int>: "L"eft, "C"entre, "R"ight, or an
                integer representing in dots where the object should be
                printed from.
            y_align <str>/<int>: "T"op, "M"iddle, "B"ottom, or an
                integer representing in dots where the object should be
                printed from.
        """
        objBox = Box(width_mm, length_mm, stroke_mm)
        xpos, ypos = self.align(objBox, x_align=x_align, y_align=y_align)

        # Submit the print command.
        for n in range(1, quantity + 1):
            self.commander.encode_box(
                width_dot=objBox.width_dot,
                length_dot=objBox.length_dot,
                stroke_dot=objBox.stroke_dot,
                start_x=xpos,
                start_y=ypos,
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_title(self, text_list, override_exit=False):
        """Print maximum size text on a label."""
        if type(text_list) == str:
            text_list = [text_list]

        font_size = 5
        for i, string in enumerate(text_list, start=1):

            # Crop text to what will fit on the label
            character = Text("C", font_size=font_size)
            string = string[: int(self.label.width_dot / character.width_dot)]

            objText = Text(string, font_size=font_size)

            # Position the title in the centre
            xpos, ypos = self.align(objText, x_align="centre", y_align="middle")

            self.commander.encode_text(
                objText.text, start_x=xpos, start_y=ypos, font_size=objText.font_size
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and i % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_text(self, text_list, font_size=3, centre=False, override_exit=False):
        """Print some text on a label.

        Args:
            text_list: A list of strings, where each item in the list
                will be printed on a new line.
            font_size: The Zebra EPL2 font size setting which can only
                be 1, 2, 3, or 4.
            centre: Set to True to centre the text on the label.
            override_exit: Set to True to stop the printer processing a
                row. This is necessary if there are multiple labels per
                row.

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        if type(text_list) == str:
            text_list = [text_list]

        row_spacer = 5
        if font_size == 1:
            line_limit = 4
        elif font_size == 2:
            line_limit = 3
        elif font_size == 3:
            line_limit = 3
            row_spacer = 2
        elif font_size == 4:
            line_limit = 2

        for i, string in enumerate(text_list, start=1):
            new_row = False
            objText = Text(string, font_size=font_size)

            if centre is True:
                xpos, _ = self.align(objText, x_align="centre", y_align="top")
            else:
                xpos, _ = self.align(objText, x_align="left", y_align="top")

            ypos = ((i - 1) % line_limit) * (objText.height_dot + row_spacer) + 2

            self.commander.encode_text(
                objText.text, start_x=xpos, start_y=ypos, font_size=objText.font_size
            )

            # Limit number of lines per label
            if i % line_limit == 0:
                # print(self.commander.active_column)
                if self.commander.active_column == self.columns - 1:
                    new_row = True
                self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if (
            not override_exit and new_row is False
        ):  # i % (line_limit * self.columns) != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_qr(self, data, quantity=1, scale=3, centre=True, override_exit=False):
        """Print a QR code.

        Args:
            data: A string containing the data of interest.
            quantity: How many barcodes that should be consecutively
                      printer.
            scale: An integer to scale the size of the QR code.
            centre <bool>: Set True to centre the graphics on the label
                else the graphics will be drawn from the top-right
                (i.e. the origin).

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        binary_data, byte_string = create_binary_qr(data, scale)
        image = BinaryImage(binary_data)

        if centre is True:
            xpos, ypos = self.align(image, x_align="centre", y_align="middle")
        else:
            xpos, ypos = self.align(image, x_align="left", y_align="top")

        # Configure the printer
        for n in range(1, quantity + 1):
            self.commander.encode_binary_image(
                byte_string,
                width_dot=image.width_dot,
                length_dot=image.length_dot,
                start_x=xpos,
                start_y=ypos,
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_qr_with_text(self, text, quantity=1, scale=3, override_exit=False):
        """Print a QR code with some text wrapped around it.

        !! This function is designed with the PCBA 2019 Serial Number !!
        !! in mind and is therefore not very practically implemented  !!
        !! for a more general application.                            !!

        Args:
            text: A string containing the data of interest.
            quantity: How many barcodes that should be consecutively
                      printer.
            scale: An integer to scale the size of the QR code.

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        binary_data, byte_string = create_binary_qr(text, scale)
        image = BinaryImage(binary_data)

        # Position the QR code to be centre top of the label
        qr_xpos, qr_ypos = self.align(image, x_align="centre", y_align="top")

        # Identify what size font to use based off the label length
        # by checking what will fit in the available space.
        erp_code = text[:11]
        for erp_font_size in reversed(range(1, 4)):
            objText_erp = Text(erp_code, font_size=erp_font_size)
            # If the text length is almost longer than the label width
            # Change the size of the font.
            if objText_erp.width_mm < self.label.width_mm - 2.0:
                break

        unique_id = text[11:]
        for uid_font_size in reversed(range(1, 4)):
            objText_uid = Text(unique_id, font_size=uid_font_size)
            # If the text length is almost longer than the label width
            # Change the size of the font.
            if objText_uid.width_mm < self.label.width_mm - 2.0:
                break

        # Define a gap between the QR code and the text as a proportion
        # of the text height. Each item is positioned below the item
        # above it.
        erp_xpos, _ = self.align(objText_erp, x_align="centre", y_align="top")
        uid_xpos, _ = self.align(objText_uid, x_align="centre", y_align="top")

        erp_ypos = (qr_ypos + image.length_dot) + int(
            (4 - erp_font_size) * 0.2 * objText_erp.height_dot
        )
        uid_ypos = (
            erp_ypos + int((4 - uid_font_size) * 0.2 * objText_uid.height_dot) + 15
        )

        # Configure the printer
        for n in range(1, quantity + 1):
            self.commander.encode_binary_image(
                byte_string,
                width_dot=image.width_dot,
                length_dot=image.length_dot,
                start_x=qr_xpos,
                start_y=qr_ypos,
            )

            self.commander.encode_text(
                objText_erp.text,
                start_x=erp_xpos,
                start_y=erp_ypos,
                font_size=objText_erp.font_size,
                invert=False,
            )

            self.commander.encode_text(
                objText_uid.text,
                start_x=uid_xpos,
                start_y=uid_ypos,
                font_size=objText_uid.font_size,
                invert=False,
            )

            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()


#######################################################################
class Barcode(object):
    def __init__(self, text, height_mm, max_width_mm, qzones=True):
        self.text, self.width_dot = self._get_width(text, max_width_mm, qzones)
        self.width_mm = self.width_dot * DOT_MM

        self.height_mm = height_mm
        self.height_dot = int(height_mm / DOT_MM)

    def _get_width(self, string, max_width_mm, enforce_quiet_zones=True):
        """
        Try to determine the length of a barcode from the Code 128 format
        """
        index = 0
        mode = None
        barcode_length_char = len(string)
        barcode_width_dot = 2 * SYMBOL  # Checksum and Stop character widths
        max_width_dot = int(max_width_mm / DOT_MM)

        if enforce_quiet_zones is True:
            max_width_dot -= 2 * QUIET_ZONE
        else:
            # A minimal quiet zone of 10 on each side is enforced at all
            # times. It may not be possible to scan this.
            max_width_dot -= 20

        while index < barcode_length_char:
            # Extract the next two consecutive characters
            char1 = string[index]
            try:
                char2 = string[index + 1]
            except IndexError:
                # IndexError: index+1 is out of range
                char2 = ""

            # Check if the consecutive characters can be combined into
            # a Code Set C symbol.
            if char1 in ALPHA_RANGE and char2 in ALPHA_RANGE:
                pair = True
                index += 2
            else:
                pair = False
                index += 1

            # If the scanner is not using Code Set C but `char1` and
            # `char2` are a numeric pair the cost is two character
            # widths for the code set transition and character pair.
            if mode != "C" and pair is True:
                delta_width_dot = 2 * SYMBOL
                mode = "C"

            # If the scanner is using Code Set C and `char1` and `char2`
            # are a numeric pair the cost is a single character width.
            elif pair is True:
                delta_width_dot = SYMBOL

            # If the scanner is not using Code Set A or Code Set B and
            # `char1` and `char2` are not a numeric pair the cost is two
            # character widths for the code set transition and `char1`
            # only.
            elif mode != "AB":
                delta_width_dot = 2 * SYMBOL
                mode = "AB"

            # If the scanner is using Code Set A or Code Set B and
            # `char1` and `char2` are not a numeric pair the cost is a
            # single character width for `char1` only.
            else:
                delta_width_dot = SYMBOL

            # Update the determined barcode width
            new_barcode_width_dot = barcode_width_dot + delta_width_dot

            if new_barcode_width_dot == max_width_dot and index >= barcode_length_char:
                barcode_width_dot = new_barcode_width_dot
                break
            elif new_barcode_width_dot >= max_width_dot:
                # print("WARNING: '{}' is too long so has been shortened.".format(string))
                string = string[: int(index - (delta_width_dot / SYMBOL))]
                break

            barcode_width_dot = new_barcode_width_dot

        return (string, barcode_width_dot)


class BinaryImage(object):
    def __init__(self, binary_data):
        """
        Args:
            binary_data: A list of binary strings, where each string
                         represents a row in the image, and each item
                         in the list translates into the length of the
                         image.
        """
        self.width_dot = self._get_width(binary_data[0])
        self.width_mm = self.width_dot * DOT_MM

        self.length_dot = len(binary_data)
        self.length_mm = self.length_dot * DOT_MM

    def _get_width(self, binary_data_row):
        """
        Try to determine the width of the binary image.

        The image will be managed to ensure it has a valid integer
        number of bytes, so the length must be divisible by 8.
        """
        row_length = len(binary_data_row.replace("\x0D", "").replace("\x0A", ""))
        r = row_length % 8
        if r != 0:
            row_length += 8 - r

        return row_length


class Box(object):
    def __init__(self, width_mm, length_mm, stroke_mm=0.125):
        self.width_mm = width_mm
        self.width_dot = int(width_mm / DOT_MM)

        self.length_mm = length_mm
        self.length_dot = int(length_mm / DOT_MM)

        self.stroke_mm = stroke_mm
        self.stroke_dot = int(stroke_mm / DOT_MM)


class Label(object):
    """A container for label properties."""

    def __init__(self, width_mm, length_mm):
        self.width_mm = width_mm
        self.width_dot = int(width_mm / DOT_MM)

        self.length_mm = length_mm
        self.length_dot = int(length_mm / DOT_MM)


class Line(object):
    def __init__(self, width_mm, length_mm):
        self.width_mm = width_mm
        self.width_dot = int(width_mm / DOT_MM)

        self.length_mm = length_mm
        self.length_dot = int(length_mm / DOT_MM)

        if width_mm < length_mm:
            self.stroke_mm = self.width_mm
            self.stroke_dot = self.width_dot
            self.direction = "V"  # Vertical
        elif length_mm < width_mm:
            self.stroke_mm = self.length_mm
            self.stroke_dot = self.length_dot
            self.direction = "H"  # Horizontal
        else:
            self.stroke_mm = self.length_mm
            self.stroke_dot = self.length_dot
            self.direction = "S"  # Square


class Text(object):
    def __init__(self, text, font_size=3):
        self.text = text
        self.font_size = font_size

        self.width_mm = self._get_width(unit="MM")
        self.width_dot = self._get_width(unit="DOT")

        self.height_mm = self._get_height(unit="MM")
        self.height_dot = self._get_height(unit="DOT")

    def _get_width(self, text=None, unit="DOT"):
        """
        According to EPL2 Programmers Manual the WIDTH for each font
        size is as follows:
            +-------+-----+------+
            | SIZE | DOTS |  MM  |
            +-------+-----+------+
            |   1  |   8  | 1.00 |  + 2 for character spacing
            |   2  |  10  | 1.25 |  + 2 for character spacing
            |   3  |  12  | 1.50 |  + 2 for character spacing
            |   4  |  14  | 1.75 |  + 2 for character spacing
            |   5  |  32  | 4.00 |  + 2? for character spacing
            +-------+-----+------+
        """
        if text is None:
            text = self.text

        font_size = self.font_size
        if font_size in [1, 2, 3, 4]:
            char_width = 8 + (2 * font_size)
        elif font_size == 5:
            char_width = 34
        else:
            raise ValueError("ERROR: Unknown font size {}".format(font_size))

        if unit.upper() == "DOT":
            return char_width * len(text)
        elif unit.upper() == "MM":
            return char_width * DOT_MM * len(text)
        else:
            raise RuntimeError(
                "ERROR: Unknown unit used: {}. 'DOT' or 'MM' only allowed.".format(unit)
            )

    def _get_height(self, unit="DOT"):
        """
        According to EPL2 Programmers Manual the HEIGHT for each font
        size is as follows:
            +-------+-----+------+
            | SIZE | DOTS |  MM  |
            +-------+-----+------+
            |   1  |  12  | 1.50 |
            |   2  |  16  | 2.00 |
            |   3  |  20  | 2.50 |
            |   4  |  24  | 3.00 |
            |   5  |  48  | 6.00 |
            +-------+-----+------+
        """
        font_size = self.font_size
        if font_size in [1, 2, 3, 4]:
            char_height = 8 + (4 * font_size)
        elif font_size == 5:
            char_height = 48
        else:
            raise ValueError("ERROR: Unknown font size {}".format(font_size))

        if unit.upper() == "DOT":
            return char_height
        elif unit.upper() == "MM":
            return char_height * DOT_MM
        else:
            raise RuntimeError(
                "ERROR: Unknown unit used: {}. 'DOT' or 'MM' only allowed.".format(unit)
            )


#######################################################################
if __name__ == "__main__":

    # Detect the zebra printer
    zp = ZebraPrinter()  # detect_printer()

    # Create a Zebra Printer handler
    from examples.zpconfig import *

    zebraPrinter = Printer(
        zp,
        LABEL_WIDTH_MM,
        LABEL_LENGTH_MM,
        LENGTH_ADJUST_MM,
        SCROLL_COLUMNS,
        LABEL_GAP_MM,
        X_OFFSET_MM,
        Y_OFFSET_MM,
    )

    # ------------------------------------------------------------------
    # Print a calibration label in the centre column.
    zebraPrinter.print_calibrator()

    # ------------------------------------------------------------------
    # barcode_height_mm = 6.0
    # # An example of a large text barcode.
    # zebraPrinter.print_barcode("S/N:00000001", 1,
    #                            bc_height_mm=barcode_height_mm,
    #                            override_exit=True)

    # # An example of a medium text barcode.
    # zebraPrinter.print_barcode("S/N:0000000000001", 1,
    #                            bc_height_mm=barcode_height_mm,
    #                            override_exit=True)

    # # An example of a small text barcode.
    # zebraPrinter.print_barcode("S/N:000000000000000001", 1,
    #                            bc_height_mm=barcode_height_mm,
    #                            override_exit=True)

    # ##################################################################
    # # TEST CORE EPL COMMAND METHODS                                  ##
    # ##################################################################

    # # The size of the font printed on the label
    # font_size = 2

    # EPL = EplCommand(
    #     width_mm=LABEL_WIDTH_MM, length_mm=LABEL_LENGTH_MM+LENGTH_ADJUST_MM,
    #     columns=SCROLL_COLUMNS, label_gap_mm=LABEL_GAP_MM,
    #     x_offset_mm=X_OFFSET_MM, y_offset_mm=Y_OFFSET_MM
    #     )
    # EPL.clear_command()
    # EPL.send_command()
    # for i in range(3):

    #     sn = "S/N: {:06d}".format(i)
    #     objBarcode = Barcode(sn, height_mm=LABEL_WIDTH_MM/2, max_width_mm=LABEL_WIDTH_MM)
    #     objText = Text(sn, font_size=font_size)

    #     EPL.encode_barcode_c128(objBarcode.text, start_x=10, start_y=0, height_dot=38)
    #     EPL.encode_text(objText.text, start_x=10, start_y=40, font_size=objText.font_size, invert=True)
    #     EPL.next_label()
    #     new_row = i%columns == columns-1

    # if not new_row:
    #     EPL.encode_print_label()
    #     EPL.send_command()
