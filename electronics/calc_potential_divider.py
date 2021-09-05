import math

########################################################################
def round_to_n(x, n):
    if not x: return 0
    power = -int(math.floor(math.log10(abs(x)))) + (n - 1)
    factor = (10 ** power)
    return round(x * factor) / factor


def list_multiply(list1, list2):
    """
    Return a list containing the results of multiplying every value in
    list1 with every value in list 2.
    """
    product = []
    for y in list2:
        for x in list1:
            product.append(x*y)

    return product


def print_table_divider():
    print(" |-{0:-^5s}-|-{0:-^8s}---{0:-^8s}-|--{0:-^7s}----{0:-^7s}-|".format("-"))


########################################################################
# RESISTORS
E12 = [100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820]

E24 = [
    100, 110, 120, 130, 150, 160, 180,
    200, 220, 240, 270,
    300, 330, 360, 390,
    430, 470,
    510, 560,
    620, 680,
    750, 820, 910
    ]

E48 = [
    100, 105, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169, 178, 187, 196,
    205, 215, 226, 237, 249, 261, 274, 287,
    301, 316, 332, 348, 365, 383,
    402, 422, 442, 464, 487,
    511, 536, 562, 590,
    619, 649, 681,
    715, 750, 787,
    825, 866,
    909, 953
    ]

E96 = [
    100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147,
    150, 154, 158, 162, 165, 169, 174, 178, 182, 187, 191, 196,
    200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294,
    301, 309, 316, 324, 332, 340, 348, 357, 365, 374, 383, 392,
    402, 412, 422, 432, 442, 453, 464, 475, 487, 499,
    511, 523, 536, 549, 562, 576, 590,
    604, 619, 634, 649, 665, 681, 698,
    715, 732, 750, 768, 787,
    806, 825, 845, 866, 887,
    909, 931, 953, 976
    ]

ALL = list(set(E12 + E24 + E48 + E96))
ALL.sort()

E12_UNIQUE = E12
E24_UNIQUE = [v for v in E24 if v not in E12]
E48_UNIQUE = [v for v in E48 if v not in E12 + E24]
E96_UNIQUE = [v for v in E96 if v not in E12 + E24 + E48]

MULTIPLIER = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]

E12_SET = list_multiply(E12, MULTIPLIER)
E24_SET = list_multiply(E24, MULTIPLIER)
E48_SET = list_multiply(E48, MULTIPLIER)
E96_SET = list_multiply(E96, MULTIPLIER)
FULL_SET = list(set(E12_SET + E24_SET + E48_SET + E96_SET))


########################################################################
def calculate_rtop_e24(vsrc, vref, error_target=10):
    # rtop = rbot*(vsrc - vref) / vref
    success = False
    for rbot in E24:
        rtop = float(rbot)*(vsrc-vref) / vref
        for value in E24_SET:
            error = abs(rtop - value)
            if error <= error_target:
                _vout = calculate_vout(vref, value, rbot)
                _vref = calculate_vref(vsrc, value, rbot)
                _rbot = "{: ^6.1f}".format(rbot)
                _rtop = "{: ^6.1f}".format(value)
                print(
                    " | {: ^5d} | {: ^8s} | {: ^8s} | {: ^.3f}V  OR  {: ^.3f}V |"
                    .format(error_target, _rtop, _rbot, _vref, _vout)
                    )
                success = True

    return success

def calculate_rtop_e96(vsrc, vref, error_target=10):
    # rtop = rbot*(vsrc - vref) / vref
    success = False
    for rbot in ALL:
        rtop = float(rbot)*(vsrc-vref) / vref
        for value in FULL_SET:
            error = abs(rtop - value)
            if error <= error_target:
                _vout = calculate_vout(vref, value, rbot)
                _vref = calculate_vref(vsrc, value, rbot)
                _rbot = "{: ^6.1f}".format(rbot)
                _rtop = "{: ^6.1f}".format(value)
                print(
                    " | {: ^5d} | {: ^8s} | {: ^8s} | {: ^.3f}V  OR  {: ^.3f}V |"
                    .format(error_target, _rtop, _rbot, _vref, _vout)
                    )
                success = True

    return success


def calculate_rbot(vsrc, vref, series=E24):
    # rbot = vref*rtop / (vsrc - vref)
    for rtop in series:
        rbot = vsrc*float(rtop) / (vsrc-vref)
        print(rbot, rtop)


def calculate_vout(vref, rtop, rbot):
    # vsrc = vref*(rbot + rtop) / rbot
    return vref*(rbot+rtop) / rbot


def calculate_vref(vsrc, rtop, rbot):
    # vref = vsrc*rbot / (rbot + rtop)
    return vsrc*rbot / (rbot+rtop)


########################################################################
if __name__ == "__main__":

    VSRC = 11.0 # V
    VREF = 1.235 # V

    print()
    print("E24 VALUES ONLY")
    print_table_divider()
    print (
        " | {: ^5s} | {: ^8s} | {: ^8s} |  {:^7s} |  {:^7s} |"
        .format("ERR", "RTOP", "RBOT", "VREF", "VOUT")
        )
    print_table_divider()
    success = False
    error_target = 0
    error_max = 0
    while not success:#error_target <= error_max:
        success = calculate_rtop_e24(VSRC, VREF, error_target)
        error_target += 1
    print_table_divider()

    print()
    print("E24 and E96 VALUES")
    print_table_divider()
    print (
        " | {: ^5s} | {: ^8s} | {: ^8s} |  {:^7s} |  {:^7s} |"
        .format("ERR", "RTOP", "RBOT", "VREF", "VOUT")
        )
    print_table_divider()
    success = False
    error_target = 0
    error_max = 1
    while error_target <= error_max:
        success = calculate_rtop_e96(VSRC, VREF, error_target)
        error_target += 1
    print_table_divider()


    print()
    print (calculate_vout(1.4, 43.0, 18.0))
    print (calculate_vref(3.3, 100000.0, 15000.0))
