#!python3

"""
Example code to print out a binary encoded image using printer.py
"""

# Standard library imports
import sys
import os

# Add parent directory to sys.path to allow example code to import
# modules placed higher up in the directory hierarchy.
repo = "zebra_printer"
pkg_dir = __file__[0 : __file__.find(repo) + len(repo)]
sys.path.append(pkg_dir)

# Local library imports
import zprinter
from zpconfig import *


#######################################################################
if __name__ == "__main__":

    """
    +------------------------------------------------------------------
    | Where 1 Dot = 1 Pixel = 0.125mm we can work out how large
    | an image can be for a label by wokring out how many dots
    | a label can fit in.
    |
    | For example, an 11.0 mm x 11.0 mm label should be able to fit
    | an image of 88 pixels x 88 pixels
    |
    | Use https://www.dcode.fr/binary-image to convert a JPEG image
    | into a binary text representation.
    +------------------------------------------------------------------
    """

    # Detect the zebra printer
    zp = zprinter.ZebraPrinter()

    # Create a Zebra Printer handler
    zebraPrinter = zprinter.Printer(
        zp,
        LABEL_WIDTH_MM,
        LABEL_LENGTH_MM,
        LENGTH_ADJUST_MM,
        SCROLL_COLUMNS,
        LABEL_GAP_MM,
        X_OFFSET_MM,
        Y_OFFSET_MM,
    )

    # Obtain the binary image data stream.
    # The binary image should only contain only the characters: '1', '0', '\n'
    binary_image = os.path.join(os.path.dirname(__file__), "qcpass_88x88.txt")
    with open(binary_image, "r") as rf:
        binary_data = rf.readlines()

    # Print the image to a label
    zebraPrinter.print_binary_image(
        binary_data, quantity=SCROLL_COLUMNS, centre=True, override_exit=False
    )
