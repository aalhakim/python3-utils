#!python3

"""
Example code to print a box using zprinter.py.
"""

# Standard library imports
import sys

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

    # Printing of different sized boxes
    STROKE_WIDTH = 0.125
    X_ALIGN = "left"
    Y_ALIGN = "top"

    quantity = SCROLL_COLUMNS
    for n in range(quantity):

        # Print the labels. If the last label printed out is not in the
        # last column, the override_exit feature must be used.
        last_label = n == quantity - 1
        max_column = SCROLL_COLUMNS - 1

        if last_label is True and n % SCROLL_COLUMNS != max_column:
            zebraPrinter.print_box(
                width_mm=LABEL_WIDTH_MM / (n + 1),
                length_mm=LABEL_LENGTH_MM / (n + 1),
                stroke_mm=STROKE_WIDTH,
                x_align=X_ALIGN,
                y_align=Y_ALIGN,
                quantity=1,
                override_exit=False,
            )

        else:
            zebraPrinter.print_box(
                width_mm=LABEL_WIDTH_MM / (n + 1),
                length_mm=LABEL_LENGTH_MM / (n + 1),
                stroke_mm=STROKE_WIDTH,
                x_align=X_ALIGN,
                y_align=Y_ALIGN,
                quantity=1,
                override_exit=True,
            )
