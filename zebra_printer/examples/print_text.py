#!python3

"""
Example code to print out text using zprinter.py.
"""

# Standard library imports
import sys
import random

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

    # An example of multi-label message printing.
    zebraPrinter.print_text(
        [
            "It's possible to write",
            "messages as a list of",
            "strings although it",
            "would be better if any",
            "length string could be",
            "given and it would be",
            "split up automatically.",
            "We're not there yet.",
        ],
        font_size=1,
        override_exit=True,
    )

    # An example of a very large font title label.
    # The necessity for the final override exit is effectivelt a bug, FYI.
    zebraPrinter.print_title("BEGIN", override_exit=True)
