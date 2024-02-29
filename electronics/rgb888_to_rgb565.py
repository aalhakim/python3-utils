#!python2
"""
Convert an RGB888 value to an RGB565 value
"""


R8 = 0
G8 = 12
B8 = 243


###############################################################################

R5 = int((31.0 * R8 / 255.0) + 0.5)
G6 = int((63.0 * G8 / 255.0) + 0.5)
B5 = int((31.0 * B8 / 255.0) + 0.5)

R8N = int((255.0 * R5 / 31.0) + 0.5)
G8N = int((255.0 * G6 / 63.0) + 0.5)
B8N = int((255.0 * B5 / 31.0) + 0.5)

print("RGB888")
print("  {}, {}, {}".format(R8, G8, B8))
print("")
print("RGB565")
print("  {}, {}, {}".format(R5, G6, B5))
print("")
print("RGB888 -- CLOSER EQUIVALENT OF RGB565 (Maybe?)")
print("  {}, {}, {}".format(R8N, G8N, B8N))
print("")
