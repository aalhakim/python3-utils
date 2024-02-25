"""
A collection of functions named after standard engineering magnitudes
which simply multiply an inserted number by the magnitude implied by the
function name.
"""


def femto(num: int | float) -> int | float:
    """Multiply argument by 1e-15"""
    return num * 1e-15


def pico(num: int | float) -> int | float:
    """Multiply argument by 1e-12"""
    return num * 1e-12


def nano(num: int | float) -> int | float:
    """Multiply argument by 1e-9"""
    return num * 1e-9


def micro(num: int | float) -> int | float:
    """Multiply argument by 1e-6"""
    return num * 1e-6


def milli(num: int | float) -> int | float:
    """Multiply argument by 1e-3"""
    return num * 1e-3


def kilo(num: int | float) -> int | float:
    """Multiply argument by 1e+3"""
    return num * 1e3


def mega(num: int | float) -> int | float:
    """Multiply argument by 1e+6"""
    return num * 1e6


def giga(num: int | float) -> int | float:
    """Multiply argument by 1e+9"""
    return num * 1e9


def tera(num: int | float) -> int | float:
    """Multiply argument by 1e+12"""
    return num * 1e12
