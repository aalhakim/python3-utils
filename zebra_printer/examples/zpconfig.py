#!python3

"""
Scroll and Label configuration data for zprinter.py
"""

#######################################################################
"""
Define MM values is 0.125 mm increments for the Zebra ZDesigner GK420t.
"""

# The width of the label being printed on.
LABEL_WIDTH_MM = 50.000

# The length (i.e. height) of the label being printed on.
LABEL_LENGTH_MM = 20.000

# Use this to adjust the perceived label length by the Zebra
# printer. This will shift the (0,0) position of the printer which
# can be on printers where the default (0,0) position seems far
# from the label edges. WARNING: Making this value too high may
# cause some odd printer behaviour. Try to keep the value small.
LENGTH_ADJUST_MM = 1.75

# The number of columns on the label scroll.
SCROLL_COLUMNS = 1

# The gap between label columns and label rows (currently both
# are assumed to be equal).
LABEL_GAP_MM = 2.000

# Offet all barcode objects in the x direction (positive will move
# objects right, and negative left).
X_OFFSET_MM = 0.875

# Offet all barcode objects in the y direction (positive will move
# objects up, and negative down).
Y_OFFSET_MM = 0.000
