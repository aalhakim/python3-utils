
# Zebra Printer

* [Modules](#modules)
* [Setup](#setup)

* [Example Code](#example-code)
  * [Getting started with zprinter.Printer()](#getting-started-with-zprinterprinter)
  * [Example files using zprinter.Printer()](#example-files-using-zprinterprinter)
  * [Printing more complicated designs with zprinter.EplCommand()](#printing-more-complicated-designs)
* [Worker Classes](#worker-classes)
  * [EplCommand()](#eplcommand)
  * [Printer()](#printer)
* [Object Models](#object-models)
  * [Barcode()](#barcode)
  * [BinaryImage()](#binaryimage)
  * [Box()](#box)
  * [Label()](#label)
  * [Line()](#Line)
  * [Text()](#text)


---

## Modules

There are two modules inside the `zebra_printer` package:

### zprinter

`zprinter.py` is the main application code to print different objects using EPL2 commands and is the main file documented in this file.

This is a Python 3 file.

### zebra_latin1

`zebra_latin1.py` is a modified copy of the 'zebra' Python library which can be installed using 'pip install zebra'. It has been modified to change the string encoding to be latin1 which was necessary to allow the EPL2 'GW' command (direct graphic write) to work.

This is a Python 2 and Python 3 compatible file.

---

## Setup

You will need to install the following modules:
* For all platforms: `pip install pyqrcode`
* For Windows: `pip install pywin32`
* For Windows: `pip install infi.devicemanager`

The zebra python modules is also required. However, a local copy of this is already provided in a modified format `zebra_latin1.py`. It had to be modified to allow the use of the 'GW' EPL2 command, which allows graphic and QR code printing.

---

## Example Code

Examples of how to use the zprinter.Printer() class can be found in the `examples` sub-directory. Available examples are:

### Getting started with zprinter.Printer()

#### Step 1

You will first need to import the `zprinter` module. In addition, you may also want to define and import a configuration file for details about the printer setup and some calibration properties.

``` python
import zprinter
import zpconfig as cfg
```

#### Step 2

The first action must be to find a compatible printer. This code has been developed solely for use with a Zebra GK420t label printer right now so the `detect_printer()` function works by looking for keywords to how this printer normall installs itself on Windows and Unix machine. On Unix though some manual configuration is also needed.

For Windows:

``` python
# Detect the zebra printer 
zp = zprinter.detect_printer()
```

For Unix:

``` python
# `x` can be determined by running detect_printer() on a unix system.
# This will print a list of installed printers. Make x the position
# # the Zebra ZDesigner GK420t printer is found in.
PRINTER_QUEUE_POSITION = x

# Detect the zebra printer 
zp = zprinter.detect_printer()
```

#### Step 3

Define the printer properties. For convenience, these can be inserted into a separate file, such as `zpconfig.py`. See `./examples/zpconfig.py` for an example.

#### Step 4

Create the main printer handler.

``` python
# Create a Zebra Printer handler
zebraPrinter = zprinter.Printer(zp, LABEL_WIDTH_MM, LABEL_LENGTH_MM, LENGTH_ADJUST_MM,
                                SCROLL_COLUMNS, LABEL_GAP_MM, X_OFFSET_MM, Y_OFFSET_MM)
```

#### Step 5

Print something out using one of the existing `Printer()` methods.

``` python
string = "Cirilla, of Cintra"

# Print a QR Code
zebraPrinter.print_qr(text=string)

# Print a Code-128 barcode
zebraPrinter.print_barcode(text=string)

# Print text - a list will print across different lines
zebraPrinter.print_text(text_list=string.split(", "))
```

All of the method calls have more arguments for greater control. See `zprinter.Printer()` for more information.

---

### Example files using zprinter.Printer()

* `print_binary_image.py` - using zprinter.Printer.print_binary_image()
  * An example of how to print from a binary image file - i.e. a file which only contains 0 and 1, to represents white and black dots, respectively.The file may also contain \n characters.
* `print_box.py` - using zprinter.Printer.print_box()
  * An example of how to draw a box with defined width, length and stroke thickness.
* `print_c128_barcode.py` - using zprinter.Printer.print_barcode()
  * An example of how to print a barcode with code-128 encoding with or without text also displayed.
* `print_qr_code.py` - using zprinter.Printer.print_qr() and .print_qr_with_text()
  * An example of how to print a QR code of different sizes and with or without text also displayed.
* `print_text.py` - using zprinter.Printer.print_text() and .print_title()
  * An example of how to print multi-lines of text or large font text to a label.
* `print_calibrator.py`
  * An example of how to print a group of items to help calibrate the printer to find the correct top-left (0, 0) origin.

All of the examples require some setup of the Printer class based on the properties of the scroll and labels being used. These properties are defined in `zpconfig.py`.

---

### Printing more complicated designs with zprinter.EplCommand()

Most of the examples display funcitonal but simple printout behaviour hard-coded to the Printer function. However, if you wish to design more complicated labels you will need to explore more direct use of the `EplCommand()` class yourself.

Correct manupulation of `EplCommand()` will allow you to 'stack' different widgets together e.g. draw a box with text inside, with a small QR code in the top-right corner and a small emoticon in the bottom-right corner.

``` python
import os
import zprinter

LABEL_WIDTH_MM = 50.000
LABEL_LENGTH_MM = 20.000
LENGTH_ADJUST_MM = 0.500
SCROLL_COLUMNS = 1
LABEL_GAP_MM = 3.500
X_OFFSET_MM = 0.625
Y_OFFSET_MM = 0.000

zp = zprinter.detect_printer()
epl = zprinter.EplCommand(zp, LABEL_WIDTH_MM,
                          LABEL_LENGTH_MM + LENGTH_ADJUST_MM,
                          SCROLL_COLUMNS, LABEL_GAP_MM,
                          X_OFFSET_MM, Y_OFFSET_MM)

#-----------------------------------------------------------------------
# Define a Label object for later use
objLabel = zprinter.Label(LABEL_WIDTH_MM, LABEL_LENGTH_MM)

#----------------------------------------------------------------------
# Encode the QR Code.

# Obtain the QR code binary image data stream.
data = "SN-X092-GR-3675"
qr_binary_data, qr_byte_string = zprinter.create_binary_qr(data, scale=2)

# Create a BinaryImage object to coveniently access the object
# properties.
objQRCode = zprinter.BinaryImage(qr_binary_data)

# Determine where to print the QR code from for it to be placed in the
# top-right of the label.
qr_xpos = int(objLabel.width_dot - objQRCode.width_dot) - 30  # Offset-Right
qr_ypos = 15                                                  # Offset-Top

# Encode the QR code to be printed in the top-right corner.
epl.encode_binary_image(qr_byte_string,
                       width_dot=objQRCode.width_dot,
                       length_dot=objQRCode.length_dot,
                       start_x=qr_xpos, start_y=qr_ypos)

#----------------------------------------------------------------------
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
face_xpos = int(objLabel.width_dot - objFace.width_dot) - 15    # Offset-Right
face_ypos = int(objLabel.length_dot - objFace.length_dot) - 10  # Offset-Bottom

# Encode the barcode to be printed in the top-right corner.
epl.encode_binary_image(face_byte_string,
                       width_dot=objFace.width_dot,
                       length_dot=objFace.length_dot,
                       start_x=face_xpos, start_y=face_ypos)

#----------------------------------------------------------------------
# Encode the box.

# Define a Box object to coveniently access the object properties.
box_width = LABEL_WIDTH_MM - 15.000
box_length = LABEL_LENGTH_MM - 3.000
objBox = zprinter.Box(width_mm=box_width, length_mm=box_length, stroke_mm=0.625)

# Determine where to print the image from for it to be placed in the
# bottom-right of the label.
box_xpos = 5                                                     # Offset-Left
box_ypos = int((objLabel.length_dot - objBox.length_dot) / 2.0)  # Middle

# Encode the box to be printed middle-left.
epl.encode_box(width_dot=objBox.width_dot,
               length_dot=objBox.length_dot,
               stroke_dot=objBox.stroke_dot,
               start_x=box_xpos, start_y=box_ypos)

#----------------------------------------------------------------------
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
epl.encode_text(objText1.text, start_x=text1_xpos, start_y=text1_ypos, font_size=font_size)
epl.encode_text(objText2.text, start_x=text2_xpos, start_y=text2_ypos, font_size=font_size)

#----------------------------------------------------------------------
# Submit the EPL2 command to the printer.
epl.encode_print_label()
epl.send_command()
```

The resulting EPL2 command sent to the printer is:

``` text
N
GW319,15,7,54
ÿÿÿÿÿÿÿÿÿÿÿÿÿÿð <Ï ð <Ï óÿ3óÃ?óóÿ3óÃ?óó3003ó3003ó3Àÿ03ó3Àÿ03ó3 Ã03ó3 Ã03óÿ3ÿÏ?óóÿ3ÿÏ?óð 333 ð 333 ÿÿüÿóÿÿÿÿüÿóÿÿÿ<ðÀÿ<ðÀÿü30Ì3ÿü30Ì3ü30? ü30? ü0ÿðóÏóü0ÿðóÏóóó?Ã ?óó?Ã ?ÿÿð<ðÿÃÿÿð<ðÿÃð00<Ãð00<ÃÿÀðÃÌÿÿÀðÃÌÿð ?ó0 ð ?ó0 ÿÿð ÃðÏÿÿð ÃðÏð 0Ã0?ð 0Ã0?óÿ0 3óÃóÿ0 3óÃó?À3ó?À3ó<üó?ó<üó?ó0ðÀ<Ãó0ðÀ<Ãóÿ<Ì< 3óÿ<Ì< 3ð ?ð<ÌÃð ?ð<ÌÃÿÿÿÿÿÿÿÿÿÿÿÿÿÿ
GW310,73,10,77
ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÀÿÿÿÿÿÿÿÿÿ ?ÿÿøÿÿÿÿþ ÿÿÀÿÿÿø ÿÿÿÿÿðÿÿ ÿÿÿà?ÿþÿÿÿàÿÀüÀÿÿÿñÿàøà?ÿÿÿÿøøðÿÿÿÿÿÿüüÿÿÿÿÿÿÿÿþÿÿÿÿÿÿÿÿÿÿÿÿÿðÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ ÿÿüÿÿÿü  ÿÿðÿÿÿø  ÿÀ ÿÿÿøÀÿ ÿÿðà?ÿ  ?ÿÿàøþøÿÿàøþþÿÿàâ|ü¾ÿÿÀÀüÿÿÁøÿÿÁø>ÿÿÁÀø<ÿÿÁÀø8ÿÿÁÀø8ÿÿÀà<øÿÿàpxüÿÿàøüüÿÿðà?üüÿÿøÀþðÿÿø  ÿ  ?ÿÿü  ÿÿ ÿÿÿ ÿÿÀ ÿÿÿÿÿÿàÿÿÿÿàÿÿüÿÿÿÿÿÿÿÿÿÿÿÿÿßÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿãÿÿÿÿÿÿÿÿÃÿÿÿÿÿÿÿÿÿÿÀ?ÿÿÿÿÿÿÿÀÿÿÿÿþÿÿÀÿÿÿÿüÿÿàÿÿÿÿüÿÿðÿÿÿÿø?ÿÿøÿÿÿÿà?ÿÿþ ÿÿÿÿÀÿÿÿÿ ÿÿÿÿÿÿÿ?ÿÿþÿÿÿÿàÿÿøÿÿÿÿðÿÿàÿÿÿÿø ÿÀÿÿÿÿþ   ÿÿÿÿÿÿ   ÿÿÿÿÿÿ  ?ÿÿÿÿÿÿà  ÿÿÿÿÿÿÿø ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ
LO10,12,280,5
LO10,12,5,136
LO10,143,280,5
LO285,12,5,136
A25,26,0,5,1,1,N,"SN-X092"
A25,86,0,5,1,1,N,"GR-3675"
P1
```

---

## Worker Classes

### EplCommand

`EplCommand()` is an object for handling and processing EPL2 queries by providing functionality to combine commands before submitting them to the printer for processing.

The class currently contains methods to allow the following things:

#### Methods: Configuration

| Method | EPL2 Command | Description
| --- | --- | ---
| `set_reference` | R | move the reference point for X and Y axes.
| `set_codepage` | I | set codepage / language support.
| `set_form_length` | Q | set label length.
| `set_label_width` | q | set label width.
| `set_print_speed` | S | set printer output speed.
| `set_darkness_level` | D | set printer darkness level.
| `set_print_direction` | Z | Select what orientation the print should come out at.
| `clear_command` | N | clear the image bugger.

#### Methods: Print Object Encoding

| Method | EPL2 Command | Description
| --- | --- | ---
| `encode_barcode_c128` | B | encode a barcode
| `encode_qr_code` | b | encode a 2D barcode (QR format)
| | | ^ !! This only works for Japanese printer models, so is also not tested.
| `encode_aztec_code` | b | encode a 2D barcode (Aztec format)
| `encode_binary_image` | GW |encode a direct graphic write. Send the printer a string of bytes where 0 represents black and 1 represents white.
| `encode_text` | A | encode text
| `encode_line` | LO | draw a line with specified thickness. This is limited to straight lines.

#### Methods: Special Encoding

| Method | EPL2 Command | Description
| --- | --- | ---
| `encode_box` | | Draw a box printing 4 lines with the 'LO' command.
| `encode_print_label` | P1 | Add the print label (1 row) command to the command buffer.
| `set_cut` | OC | enable or disable cut after print functionality, for printers that have the cutter accessory.

#### Methods: Actions

| Method | EPL2 Command | Description
| --- | --- | ---
| `auto_sense` | xa | command the printer to run it's AutoSense function to detect label and gap length and set sensor levels.
| `configure` | | Configure the printer with the pre-defined settings.
| `send_command` | | Submit a pre-built command (from the command buffer) or directly send a new command through as an argument.

See documentation in the `docs` folder for more information about EPL2 commands.

### Printer

`Printer()` is mainly intended for a few purposes:

1. As an abstraction of 'EplCommand' to make basic printing requests more comfortable for a newcomer through simple function calls.
2. To automate text row management by determining a suitable y-position for text to be placed if text is going to be written over multiple lines.
3. To automate label position management if a scroll has more than 1 column of labels. If configured correctly 'Printer' will handle which label to move to next before printing out a line of labels.

Due to step 2, it's better to enhance 'Printer' with new methods to take advantage of the label management, rather than develop external 'EplCommand' instructions, although the latter is still possible and practical for single column scrolls (see ['Printing more complicated designs'](#printing-more-complicated-designs) for an example).

#### Methods: Generic(-ish) Outputs

| Method | Description
| --- | ---
| `print_barcode` | Print a code-128 encoded barcode with human-readable text displayed below the barcode.
| | ^ !! The encoding will be cropped to ensure the barcode is always readable in the available label width.
| `print_binary_image` | Print an image based off a string of bytes representing where to burn the label and where not to. Each pixel of the image maps to a dot on the label.
| `print_box` | Print a box of user-defined width, length and stroke thickness.
| `print_title` | Print text at the maximum font size of 5.
| | ^ !! The text will be cropped if it's width is wider than the label width.
| `print_text` | Print text on a label of user-defined size. Inserting a list provides the ability to print on multiple lines.
| | If a string in the list is too wide for the label it will not be cropped to size.
| | If the text list contains more items than there are available rows on the label, the next available label, either in the next column or row, will be used.
|  `print_qr` | Print a QR code with high error correction.

#### Methods: Specific Outputs

| Method | Description
| --- | ---
| `print_qr_with_text` | This method is written with the BBOXX 2020 ERP code format in mind. It will print a QR code (with high error correction) at the centre-top of the label and the text-representation of the production serial number below. The serial number is split into two parts specific to the ERP barcode format. 

#### Methods: Special Outputs

| Method | Description
| --- | ---
| `print_calibrator` | Print a square equal to the size of the label. Adjust the configurations until the square sits almost perfectly central.
| `cut` | Command the printer to cut the scroll, if a cutter accessory is attached.

---

## Object Models

These are the types of things that can be printed onto a label. The models are used to provide convenient access to object properties such as dimensions, in both mm and dots.

### Barcode

A container for 1D barcode properties, such as:

* width_mm
* width_dot
* height_mm *(equivalent to length_mm)*
* height_dot *(equivalent to length_dot)*
* text

### BinaryImage

A container for binary image properties, such as:

* width_mm
* width_dot
* length_mm
* length_dot

A binary image can be created with this tool from a PNG or JPEG file: https://www.dcode.fr/binary-image.

### Box

A container for box properties, such as:

* width_mm
* width_dot
* length_mm
* length_dot
* stroke_mm
* stroke_dot

### Label

A container for label properties, such as:

* width_mm
* width_dot
* length_mm
* length_dot

### Line

A container for line properties, such as:

* width_mm
* width_dot
* length_mm
* length_dot
* stroke_mm
* stroke_dot
* direction - 'V'ertical, 'H'orziontal, or 'S'quare

### Text

A container for text properties, such as:

* width_mm
* width_dot
* height_mm *(equivalent to length_mm)*
* height_dot *(equivalent to length_mm)*
* text
* font_size
