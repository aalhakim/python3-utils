# -*- coding: utf-8 -*-

import sys
print("{}".format(sys.stdout.encoding))

print("通道编号")

char = "通"
print("{} => ".format(char), end="")
for c in char:
    print("{:08b}".format(ord(c)))
