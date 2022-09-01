"""
Zebra Printer barcode and label printing code using EPL2.
Tested with Zebra GK420t only

Contributed by: Kyle McInnes, Ali H Al-Hakim
Last Updated: 22 October 2018
"""

# Standard Library Imports
from __future__ import print_function
import os

# Third-Party Library Imports
from zebra import zebra


########################################################################
PI_PRINTER_SELECTION = 1


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


########################################################################
def detect_printer():
    """Basic automated check to see if a printer is connected or not.

    This code has been tested on a Windows machine and a Raspberry Pi
    (Ubuntu).
    """
    z = zebra()

    # Identify which operating system is being used and find the printer
    printer_present = False
    system_name = os.name
    if system_name == "nt":
        print("Running on Windows...", end=" ")
        from infi.devicemanager import DeviceManager
        import win32print

        # Identify if a Zebra printer is connected and available
        printer_queues = []
        for (a, b, name, d) in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printer_queues.append(name)

        dm = DeviceManager()
        devices = dm.all_devices
        for dev in devices:
            if "ZDesigner" in dev.description:
                if dev.children[0].friendly_name in printer_queues:
                    print("found printer: {}".format(dev.children[0].friendly_name))
                    z.setqueue(dev.children[0].friendly_name)
                    printer_present = True
                    break

    elif system_name == "posix":
        print("Running on Raspberry Pi... configure printer setting:")
        try:
            printers = [device for device in z.getqueues() if "GK420" in device]
            print("")
            for i, printer in enumerate(printers):
                print("  {}: {}".format(i, printer))

            z.setqueue(printers[PI_PRINTER_SELECTION])
            print("Connected to: {}".format(printers[PI_PRINTER_SELECTION]))
            printer_present = True
        except:
            print("Check that 'PI_PRINTER_SELECTION' is correctly configured.")
            printer_present = False

    return z


########################################################################
class EplCommand(object):
    def __init__(
        self,
        printer,
        width_mm,
        length_mm,
        columns=1,
        label_gap_mm=0,
        x_offset_mm=0.0,
        y_offset_mm=0.0,
    ):
        assert int(
            columns
        ), "Invalid_setting (columns of {}): columns must be an integer >= 1".format(
            columns
        )
        self.printer = printer
        self.columns = columns
        self.active_column = 0
        self.array_gap_dot = int(label_gap_mm / DOT_MM)

        self.ribbon_width_dot = (columns * int(width_mm / DOT_MM)) + (
            (columns - 1) * self.array_gap_dot
        )
        self.label_width_dot = int(width_mm / DOT_MM)
        self.label_length_dot = int(length_mm / DOT_MM)
        self.x_offset = int(x_offset_mm / DOT_MM)
        self.y_offset = int(y_offset_mm / DOT_MM)

        self.command_clear_buffer = "N\n"
        self.command_print_label = "P1\n"
        self.command = self.command_clear_buffer

        self.set_codepage()
        self.set_label_width()
        self.set_print_speed()
        self.set_darkness_level()
        self.set_form_length(gap_length=self.array_gap_dot)
        # self.auto_sense()
        self.configure()
        self.send_command()

    def send_command(self, command=None):
        if command is None:
            command = self.command
        # print(command)
        self.printer.output(command)
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

    def set_codepage(self, lang="1"):
        """
        'I' Command: Set codepgae / language support.
        """
        assert (
            0 <= int(lang) <= 15
        ), "Invalid_setting (lang of {}): 18 <= lang <= 240".format(lang)
        self.codepage = "I8,{},044\n".format(lang)
        pass

    def set_form_length(self, gap_length):
        """
        'Q' Command: Set label length.
        """
        assert (
            16 <= gap_length <= 240
        ), "Invalid setting (gap_length of {}): 16 <= gap_length <= 240".format(
            gap_length
        )
        self.label_length = "Q{},{}\n".format(self.label_length_dot, gap_length)

    def set_label_width(self):
        """
        'q' Command: Set label width.
        """
        self.label_width = "q{}\n".format(self.ribbon_width_dot)

    def set_print_speed(self, speed=3):
        """
        'S' Command: Set printer output speed
            2=50mm/s, 3=75mm/2, 4=100mm/s, 5=125mm/s
        """
        assert 2 <= speed <= 5, "Invalid setting (speed of {}): 2 <= speed <= 5".format(
            speed
        )
        self.print_speed = "S{}\n".format(speed)

    def set_darkness_level(self, level=15):
        """
        'D' Command: Set printer burn-rate, thus darkness level
            0 Lightest to 15 Darkest  (default is 8 for GK420)
        """
        self.darkness_level = "D{}\n".format(level)

    def encode_barcode_c128(self, string, start_x=0, start_y=0, height=10):
        """
        'B' Command: Encode a barcode
            string = what the barcode should represent
            start_x = horizontal start position, in dots
            start_y = vertical start position, in dots
            height = bar code height, in dots
        """
        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.array_gap_dot) * self.active_column)
            + self.x_offset
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: barcode x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset
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
            start_x, start_y, narrow_bar, wide_bar, height, string
        )
        self.command += barcode

    def encode_text(
        self,
        string,
        start_x,
        start_y,
        font_size=3,
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

        start_x = (
            int(start_x)
            + ((self.label_width_dot + self.array_gap_dot) * self.active_column)
            + self.x_offset
        )
        if start_x < 0:
            start_x = 0
            # print("WARNING: text x position can't be negative so it has been forced to 0")

        # The offset is negative because the printer origin is top-left
        # whereas most users will intuitively expect bottom-left. If
        # negative, a positive offset will actually shift the object up.
        start_y = int(start_y) - self.y_offset
        if start_y < 0:
            start_y = 0
            # print("WARNING: text y position can't be negative so it has been forced to 0")
        expand_x = int(expand_x)
        expand_y = int(expand_y)

        # start_x (in dots)
        # start_y (in dots)
        # rotation = 0: 0 degrees
        # font_size
        # expand_x
        # expand_y
        # reverse colour image (R) or normal (N)
        text = 'A{},{},0,{},{},{},{},"{}"\n'.format(
            start_x, start_y, font_size, expand_x, expand_y, invert, string
        )
        self.command += text

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
          + label_width
          + print_speed
          + darkness_level
        """
        command = self.command_clear_buffer
        command += self.codepage
        command += self.label_length
        command += self.label_width
        command += self.print_speed
        command += self.darkness_level
        self.send_command(command)


class Barcode(object):
    def __init__(self, text, label_width_mm, qzones=True, x_offset_dot=0.0):
        self.label_width_dot = int(label_width_mm / DOT_MM)

        self.text, self.width_dot = self.get_width(text, qzones)
        self.start_pos = int((self.label_width_dot - self.width_dot) / 2) + x_offset_dot

    def width(self, unit="DOT"):
        if unit.upper() == "DOT":
            return self.width_dot
        elif unit.upper() == "MM":
            return self.width_dot * DOT_MM
        else:
            raise RuntimeError(
                "ERROR: Unknown unit used: {}. 'DOT' or 'MM' only allowed.".format(unit)
            )

    def get_width(self, string, enforce_quiet_zones=True):
        """
        Try to determine the length of a barcode from the Code 128 format
        """
        index = 0
        mode = None
        barcode_length = len(string)
        barcode_width = 2 * SYMBOL  # Checksum and Stop character widths
        max_width = self.label_width_dot

        if enforce_quiet_zones is True:
            max_width -= 2 * QUIET_ZONE
        else:
            # A minimal quiet zone of 10 on each side is enforced at all
            # times. It may not be possible to scan this.
            max_width -= 20

        while index < barcode_length:
            # Extract the next two consecutive characters
            char1 = string[index]
            try:
                char2 = string[index + 1]
            except IndexError:
                # IndexError: index+1 is out of range
                char2 = ""

            # Check if the consecutive characters can be combined into a
            # Code Set C symbol.
            if char1 in ALPHA_RANGE and char2 in ALPHA_RANGE:
                pair = True
                index += 2
            else:
                pair = False
                index += 1

            # If the scanner is not using Code Set C but `char1` and `char2`
            # are a numeric pair the cost is two character widths for the
            # code set transition and character pair.
            if mode != "C" and pair is True:
                delta_width = 2 * SYMBOL
                mode = "C"

            # If the scanner is using Code Set C and `char1` and `char2` are
            # a numeric pair the cost is a single character width.
            elif pair is True:
                delta_width = SYMBOL

            # If the scanner is not using Code Set A or Code Set B and
            # `char1` and `char2` are not a numeric pair the cost is two
            # character widths for the code set transition and `char1` only.
            elif mode != "AB":
                delta_width = 2 * SYMBOL
                mode = "AB"

            # If the scanner is using Code Set A or Code Set B and `char1`
            # and `char2` are not a numeric pair the cost is a single
            # character width for `char1` only.
            else:
                delta_width = SYMBOL

            new_barcode_width = barcode_width + delta_width
            if new_barcode_width == max_width and index >= barcode_length:
                barcode_width = new_barcode_width
                break
            elif new_barcode_width >= max_width:
                # print("WARNING: '{}' is too long so has been shortened.".format(string))
                string = string[: index - (delta_width / SYMBOL)]
                break

            barcode_width = new_barcode_width

        return string, barcode_width


class Text(object):
    def __init__(self, text, label_width_mm, font_size=3, x_offset_dot=0.0):
        self.label_width_dot = int(label_width_mm / DOT_MM)
        self.font_size = font_size
        self.text = text[: int(self.label_width_dot / self.width("C"))]
        self.start_pos = int((self.label_width_dot - self.width()) / 2) + x_offset_dot

    def width(self, text=None, unit="DOT"):
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

    def height(self, unit="DOT"):
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


class Printer(object):
    def __init__(
        self,
        printer,
        width,
        length,
        columns,
        gap_size,
        x_offset_mm=0.0,
        y_offset_mm=0.0,
    ):
        self.printer = printer
        self.label_width = width
        self.label_length = length
        self.columns = columns
        self.commander = EplCommand(
            printer, width, length, columns, gap_size, x_offset_mm, y_offset_mm
        )

    def print_title(self, text_list, override_exit=False):
        if type(text_list) == str:
            text_list = [text_list]

        for i, string in enumerate(text_list, start=1):
            text = Text(string, self.label_width, font_size=5)
            self.commander.encode_text(
                text.text, start_x=text.start_pos, start_y=5, font_size=text.font_size
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and i % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()

    def print_text(self, text_list, font_size=3, centre=False, override_exit=False):
        """Print some text on a barcode.

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
            text = Text(string, self.label_width, font_size=font_size)
            start_y_pos = ((i - 1) % line_limit) * (text.height() + row_spacer) + 2

            start_x_pos = 16
            if centre:
                start_x_pos = text.start_pos
            self.commander.encode_text(
                text.text,
                start_x=start_x_pos,
                start_y=start_y_pos,
                font_size=text.font_size,
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

    def print_barcode(
        self, text, quantity=1, invert=False, override_exit=False, bc_height_mm=None
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
        barcode = Barcode(text, self.label_width)

        # Set a default value for barcode height if None is given
        if bc_height_mm is None:
            bc_height_mm = self.label_length / 2
        bc_height_dot = int(bc_height_mm / DOT_MM)
        # print(bc_height_dot)

        # Identify what size font to use based off the barcode length
        # by checking what will fit in the available space.
        for font_size in reversed(range(1, 4)):
            _text = Text(
                barcode.text, self.label_width, font_size=font_size, x_offset_dot=2
            )
            # If the text length is almost longer than the label width
            # Change the size of the font.
            if _text.width(unit="MM") < self.label_width - 2.0:
                break

        # Define a gap between the barcode and the text as a proportion
        # of the text height
        text_start_pos = bc_height_dot + int(
            (4 - font_size) * 0.2 * _text.height("DOT")
        )
        for n in range(1, quantity + 1):
            self.commander.encode_barcode_c128(
                barcode.text, start_x=barcode.start_pos, start_y=0, height=bc_height_dot
            )
            self.commander.encode_text(
                _text.text,
                start_x=_text.start_pos,
                start_y=text_start_pos,
                font_size=_text.font_size,
                invert=invert,
            )
            self.commander.next_label()

        # If next_label has not been issued 'self.columns' times, then
        # force the printer to move to the next row.
        if not override_exit and n % self.columns != 0:
            self.commander.encode_print_label()
            self.commander.send_command()


if __name__ == "__main__":
    zprinter = detect_printer()

    # The width of the label being printed on
    width = 30.00

    # The height of the label being printed on
    height = 10.00

    # Use this to adjust the perceived label height by the Zebra
    # printer. This will shift the (0,0) position of the printer which
    # can be on printers where the default (0,0) position seems far
    # from the label edges. WARNING: Making this value too high may
    # cause some odd printer behaviour. Try to keep the value small.
    height_adjust_mm = 1.0

    # The number of columns on the label scroll
    columns = 3

    # The gap between label columns and label rows (currently both
    # are assumed to be equal)
    label_gap_mm = 2

    # Offet all barcode objects in the y direction (positive will move
    # objects up and negative down)
    y_offset_mm = 0.0

    # Offet all barcode objects in the x direction (positive will move
    # objects right and negative left)
    x_offset_mm = 0.0

    # The height of the barcode from the (0,0) origin
    barcode_height_mm = 6.0

    ####################################################################
    ## TEST CORE EPLCOMMAND METHODS                                   ##
    ####################################################################

    # # The size of the font printed on the label
    # font_size = 2

    # EPL = EplCommand(
    #     width_mm=width, length_mm=height+height_adjust_mm,
    #     columns=columns, label_gap_mm=label_gap_mm,
    #     x_offset_mm=x_offset_mm, y_offset_mm=y_offset_mm
    #     )
    # EPL.clear_command()
    # EPL.send_command()
    # for i in range(3):

    #     x_offset_dot = x_offset_mm / DOT_MM
    #     sn = "S/N: {:06d}".format(i)
    #     barcode = Barcode(sn, label_width_mm=width)
    #     text = Text(sn, font_size=font_size, label_width_mm=width, x_offset_dot=2)

    #     EPL.encode_barcode_c128(barcode.text, start_x=barcode.start_pos, start_y=0, height=38)
    #     EPL.encode_text(text.text, start_x=text.start_pos, start_y=40, font_size=text.font_size, invert=True)
    #     EPL.next_label()
    #     new_row = i%columns == columns-1

    # if not new_row:
    #     EPL.encode_print_label()
    #     EPL.send_command()

    ####################################################################
    ## TEST ABSTRACTED PRINTER CLASS SYSTEM                           ##
    ####################################################################
    zebraPrinter = Printer(
        zprinter,
        width,
        height + height_adjust_mm,
        columns,
        label_gap_mm,
        x_offset_mm,
        y_offset_mm,
    )

    # An example of a large text barcode.
    zebraPrinter.print_barcode(
        "S/N:00000001", 1, bc_height_mm=barcode_height_mm, override_exit=True
    )

    # An example of a medium text barcode.
    zebraPrinter.print_barcode(
        "S/N:0000000000001", 1, bc_height_mm=barcode_height_mm, override_exit=True
    )

    # An example of a small text barcode.
    zebraPrinter.print_barcode(
        "S/N:000000000000000001", 1, bc_height_mm=barcode_height_mm, override_exit=True
    )

    # An example of multi-label message printing.
    # zebraPrinter.print_text(['Line 1'], font_size=2)
    # zebraPrinter.print_text(
    #     ["It's possible to write", "messages as a list of", "strings although it",
    #     "would be better if any", "length string could be", "given and it would be",
    #     "split up automatically.", "We're not there yet."], font_size=1, override_exit=True)

    # An example of a very large font title label.
    zebraPrinter.print_title(
        "BEGIN", override_exit=True
    )  # The necessity for the final override exit is a bug.
