#!python3

"""
Example on using pyqrcode module to generate a QR Code data object.
"""

import pyqrcode


#######################################################################
# What to encode in the QR Code.
SERIAL_NUMBER = "LLRRRRMvMi-BnYnWn-AAA-C"

# Select by how much to enlarge the QR Code.
SCALE = 1

# Choose whether to invert the QR Code
#    True: 1 = white space, 0 = black space
#    False: 0 = black space, 1 = white space
INVERT = False

# The default quietzone scale is 4 modules. If set to False this scale
# is maintained. If set to True, the quietzone scale will be 1 module.
REDUCE_QUIETZONE = False


#######################################################################
# Create a QR code object
qr = pyqrcode.create(SERIAL_NUMBER, error="H")

# Obtain a binary representation of the QR code
qr_text = qr.text()

# Remove leading or trailing line breaks and spaces
qr_text = qr_text.strip()

# Invert the image
if INVERT is True:
    qr_text = qr_text.replace("1", "A").replace("0", "1").replace("A", "0")

# Break up into a list of rows for post processing
qr_text = qr_text.split("\n")


# Increase the size of the barcode as  Do not scale the pre-defined quiet zones.
if INVERT is True:
    darkspace_symbol = "0"
else:
    darkspace_symbol = "1"

# Scale the QR code by a multipler of SCALE. `pyqrcode` generates a
# codes with 1x1 modules by default.
binary_data = []
if REDUCE_QUIETZONE is True:
    skip_count = 0
    for row in qr_text:
        if darkspace_symbol not in row:
            skip_count += 1
    qz_index = int((skip_count / 2) - 1)

    for row in qr_text[qz_index:-qz_index]:
        new_row = ""
        for char in row[qz_index:-qz_index]:
            new_row += char * SCALE
        for n in range(SCALE):
            binary_data.append(new_row)

else:
    for row in qr_text:
        new_row = ""
        for char in row:
            new_row += char * SCALE
        for n in range(SCALE):
            binary_data.append(new_row)

# Print the binary image to the console
for row in binary_data:
    print(row)
