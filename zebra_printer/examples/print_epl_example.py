#!python3

"""
Execute the example code used to explain how EplCommand can be used
to create custom layouts in the README.md file.
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


#######################################################################
LABEL_WIDTH_MM = 50.000
LABEL_LENGTH_MM = 20.000
LENGTH_ADJUST_MM = 0.500
SCROLL_COLUMNS = 1
LABEL_GAP_MM = 3.500
X_OFFSET_MM = 0.625
Y_OFFSET_MM = 0.000


#######################################################################
# Initialise workers objects.
zp = zprinter.detect_printer()
epl = zprinter.EplCommand(
    zp,
    LABEL_WIDTH_MM,
    LABEL_LENGTH_MM + LENGTH_ADJUST_MM,
    SCROLL_COLUMNS,
    LABEL_GAP_MM,
    X_OFFSET_MM,
    Y_OFFSET_MM,
)

# -----------------------------------------------------------------------
# Define a Label object for later use.
objLabel = zprinter.Label(LABEL_WIDTH_MM, LABEL_LENGTH_MM)

# ----------------------------------------------------------------------
# Encode the QR Code.

# Obtain the QR code binary image data stream.
data = "SN-X092-GR-3675"
qr_binary_data, qr_byte_string = zprinter.create_binary_qr(data, scale=2, version=None)

# Create a BinaryImage object to coveniently access the object
# properties.
objQRCode = zprinter.BinaryImage(qr_binary_data)

# Determine where to print the QR code from for it to be placed in the
# top-right of the label.
qr_xpos = int(objLabel.width_dot - objQRCode.width_dot) - 30  # Offset-Right
qr_ypos = 15  # Offset-Top

# Encode the QR code to be printed in the top-right corner.
epl.encode_binary_image(
    qr_byte_string,
    width_dot=objQRCode.width_dot,
    length_dot=objQRCode.length_dot,
    start_x=qr_xpos,
    start_y=qr_ypos,
)

# ----------------------------------------------------------------------
# Encode the face from a binary data file.

# Obtain the binary data stream from the image file.
binary_image = os.path.join(os.path.dirname(__file__), "face_80x80.txt")
with open(binary_image, "r") as rf:
    face_binary_data = rf.readlines()

# Create a BinaryImage object to coveniently access the object
# properties.
objFace = zprinter.BinaryImage(face_binary_data)

# Convert the binary dataset into a byte string for the printer.
hex_string = ""
for row in face_binary_data:
    hex_string += zprinter.binary_string_to_hex_string(row)
face_byte_string = zprinter.hex_string_to_latin1_string(hex_string)

# Determine where to print the image from for it to be placed in the
# bottom-right of the label.
face_xpos = int(objLabel.width_dot - objFace.width_dot) - 15  # Offset-Right
face_ypos = int(objLabel.length_dot - objFace.length_dot) - 10  # Offset-Bottom

# Encode the barcode to be printed in the top-right corner.
epl.encode_binary_image(
    face_byte_string,
    width_dot=objFace.width_dot,
    length_dot=objFace.length_dot,
    start_x=face_xpos,
    start_y=face_ypos,
)

# ----------------------------------------------------------------------
# Encode the box.

# Define a Box object to coveniently access the object properties.
box_width = LABEL_WIDTH_MM - 15.000
box_length = LABEL_LENGTH_MM - 3.000
objBox = zprinter.Box(width_mm=box_width, length_mm=box_length, stroke_mm=0.625)

# Determine where to print the image from for it to be placed in the
# bottom-right of the label.
box_xpos = 5  # Offset-Left
box_ypos = int((objLabel.length_dot - objBox.length_dot) / 2.0)  # Middle

# Encode the box to be printed middle-left.
epl.encode_box(
    width_dot=objBox.width_dot,
    length_dot=objBox.length_dot,
    stroke_dot=objBox.stroke_dot,
    start_x=box_xpos,
    start_y=box_ypos,
)

# ----------------------------------------------------------------------
# Encode the text.
font_size = 5

# Write the first half of `data` on an upper line, with custom
# positioning, where top-left is known to the the origin (0, 0).
objText1 = zprinter.Text(data[:7], font_size=font_size)
text1_xpos = 20
text1_ypos = int((objLabel.length_dot - objText1.height_dot) / 2.0) - 30

# Write the second half of `data` on the lower line, with custom
# positioning, where top-left is known to the the origin (0, 0).
objText2 = zprinter.Text(data[8:], font_size=font_size)
text2_xpos = 20
text2_ypos = int((objLabel.length_dot - objText2.height_dot) / 2.0) + 30

# Encode the text to be printed slightly offset from the middle-left
# across two lines.
epl.encode_text(
    objText1.text, start_x=text1_xpos, start_y=text1_ypos, font_size=font_size
)
epl.encode_text(
    objText2.text, start_x=text2_xpos, start_y=text2_ypos, font_size=font_size
)

# ----------------------------------------------------------------------
# Submit the EPL2 command to the printer.
epl.encode_print_label()
epl.send_command()
