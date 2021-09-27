#!python3

"""
Example code to print out an Aztec 2D Barcode using zprinter.py
"""

# Standard library imports
import sys
import random

# Add parent directory to sys.path to allow example code to import
# modules placed higher up in the directory hierarchy.
from module_name import MODULE_NAME

pkg_dir = __file__[0 : __file__.find(MODULE_NAME) + len(MODULE_NAME)]
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

    """
    +------------------------------------------------------------------
    | BBOXX Supply Chain Serial Number Formats (Jan 2020)
    +------------------------------------------------------------------
    | According to: Confluence -> Stock Tracking -> Serial Numbers Format
    |  + Appliances: LLRRRRMvMi-BnYnWn-AAA-C  -- created from Production Order
    |  +   Products: LLRRRRMvMi-BnYnWn-AAA-C  -- created from Assembly Order
    |  +      PCBAs: PLNNRRVVSS-BnYnWn-AAA-C  -- created from Production Order
    |
    | Where:
    |  [A] L = Product type/family
    |  [N] R = Radical (version) of product type/family in the ERP
    |  [N] Mv = Model number with visible difference (directly obserable)
    |  [N] Mi = Model number with invisible difference
    |  [N] Bn = Production batch number - resets when Wn increments
    |  [N] Yn = Production year number
    |  [N] Wn = Production week number
    |  [A] AAA = Serial number units - resets when Bn changes
    |  [A] C = Checksum digit
    |
    | Special codes for PCBAs
    |  [A] P = Prefix for PCBAs
    |  [A] L = PCB type alphanumeric incrementer
    |  [N] NN = PCB type numeric only incrementer
    |   - LNN can range from A01 to Z99 to 999
    |  [N] RR = PCBA revision ID (this does not relate to the PCB revision)
    |  [N] VV = PCBA variation ID
    |  [N] SS = SIM variation ID (based off a SIM lookup list)
    |
    | A = Alphanumeric
    | N = Numeric Only
    +------------------------------------------------------------------
    """

    # --------------------------------------------
    # PCBA Serial Number Example
    #  Format: PLNNRRVVSS-BnYnWn-AAA-C
    ERPCODE_TIGER_12G_AR_V03 = "PA02010202"
    BATCH_NUMBER = "01"
    YEAR_NUMBER = "20"
    WEEK_NUMBER = "02"
    CHECKSUM = "C"

    # --------------------------------------------
    quantity = SCROLL_COLUMNS
    for n in range(quantity):

        # Create the serial number
        NUMERIC_VALUE = "{:03d}".format(random.randrange(0, 999))
        serial_number = "{}-{}{}{}-{}-{}".format(
            ERPCODE_TIGER_12G_AR_V03,
            BATCH_NUMBER,
            YEAR_NUMBER,
            WEEK_NUMBER,
            NUMERIC_VALUE,
            CHECKSUM,
        )
        print("Serial Number: '{}'".format(serial_number))

        # Print the labels. If the last label printed out is not in the
        # last column, the override_exit feature must be used.
        last_label = n == quantity - 1
        max_column = SCROLL_COLUMNS - 1

        if last_label is True and (n % SCROLL_COLUMNS != max_column) is False:
            # This shouldn't work for non-Japanese licensed printers
            zebraPrinter.commander.encode_qr_code(
                serial_number, start_x=(n * 80) + 10, start_y=10
            )
        else:
            zebraPrinter.commander.encode_aztec_code(
                serial_number, start_x=(n * 80) + 10, start_y=10
            )

    zebraPrinter.commander.encode_print_label()
    zebraPrinter.commander.send_command()
