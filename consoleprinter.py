#!/usr/bin/env python3

"""
Functions to print lists and dicts neatly to a console.
"""

# Standard library imports
from __future__ import print_function
from collections import OrderedDict
import time


########################################################################
def dprint(mode="", msg="", start="", end=None):
    """Print a formatted message to terminal.

    Args:
        mode <str>: "", "INFO", "ERROR", "WARN", "DEBUG", "PASS", FAIL", etc
        msg <str>: The message to display
        start <str>: A string to insert at the start of `msg`
        end - A string to insert at the end of `msg`
    """
    # Break message up into printable chunks with a max line length
    # of around 60 charactrers.
    lines = []
    msg = msg.replace("\n", " \n ").replace("  ", " ")
    words = msg.split(" ")
    newline = ""
    for word in words:
        if word != "\n":
            newline += word + " "
        if ((word == "\n") or len(newline) > 60) and (newline != ""):
            lines.append(newline)
            newline = ""
    lines.append(newline)

    # Print to terminal with prefic and start/end blcoks where needed.
    num_lines = len(lines)
    for i, line in enumerate(lines):
        is_first_line = i == 0
        is_last_line = i + 1 == num_lines

        _start = ""
        _end = None
        if is_first_line and is_last_line:
            _start = start
            _end = end
        elif is_first_line:
            _start = start
        elif is_last_line:
            _end = end

        print(_start + f"  > {mode: >5} : " + line, end=_end)


########################################################################
def print_countdown(delay_s, msg):
    """Display terminal coundown timer with message and spinner.

    Arguments:
        delay_s {int} -- Number of seconds to count down from.
        msg {str} -- A message to displayt with the countdown. Include
            {} in the string to represent where the remaining time
            value should be displayed.
    """
    spin_icons = "|/-\\"
    period_s = 0.2
    ticks = int(delay_s / period_s)
    for i in range(ticks):
        remaining_time = int(delay_s - (i * period_s) + 0.5)
        spinner = " [{}] ".format(spin_icons[(i % 4)])
        print("\r" + msg.format(remaining_time) + spinner, end="")
        time.sleep(period_s)


########################################################################
def print_list(list, line_length=88, sort=False):
    """Print a list to the console with limited row length.

    Args:
        list <list>: The list to be printed.
        line_length <int>: The maximum length of a printed row.
        sort <bool>: Apply list sort to `list` if True.
    """
    string_length = line_length
    if list != []:

        # Sort list if requsted.
        if sort is True:
            list.sort()

        for i in range(len(list)):
            string_length += len(str(list[i])) + 2

            # Start a new line when the line length exceeds line_length
            if string_length > line_length + 2:
                print("\n  ", end="")
                string_length = 3

            print("{}, ".format(list[i]), end="")

    else:
        print("\n  Nothing to print.", end="")
    print("\n")


########################################################################
def print_header(columns):
    """Print a table header."""
    print_seperator(columns)
    print("\n  |", end="")
    for column in columns:
        title, width, align = columns[column]
        config = "{: ^" + str(width) + "}"
        print(" {} |".format(config.format(title.upper())), end="")
    print_seperator(columns)


def print_seperator(columns):
    """Print a table separater."""
    print("\n  -".format(""), end="")
    for column in columns:
        title, width, align = columns[column]
        config = "{:-^" + str(width) + "}"
        print("-{}--".format(config.format("")), end="")


def print_dict(data, columns):
    """Print a dict in a table format."""
    print("\n  |", end="")
    for column in columns:
        title, width, align = columns[column]
        config = "{:" + align + str(width) + "}"
        print(" {} |".format(config.format(data[column])), end="")


########################################################################
if __name__ == "__main__":

    # -------------------------------------------------------------------
    print("-------------------------")
    print(" -- PRINT LIST EXAMPLE --")
    print("-------------------------")

    # fmt: off
    data = [
        1990, 1996, 1999, 1992, 2001, 1995, 1993, 2007, 1997, 1991,
        2008, 2003, 2002,1994, 2004, 2005, 2006, 1998, 2000, 2009,
    ]

    print("Unsorted, Line length <= 60")
    print_list(data, line_length=60, sort=False)
    print("Sorted, Line length <= 45")
    print_list(data, line_length=45, sort=True)
    print("Sorted, Line length <= 30")
    print_list(data, line_length=30, sort=True)
    print()

    # -------------------------------------------------------------------
    print("----------------------------------")
    print(" -- PRINT DICT AS TABLE EXAMPLE --")
    print("----------------------------------")

    # Define some data
    data = [
        {"name": "Geralt",    "of": "Rivia",      "nationality": "",        "race": "Witcher",  "gender": "Male",},
        {"name": "Triss",     "of": "Maribor",    "nationality": "Redania", "race": "Human",    "gender": "Female"},
        {"name": "Dandelion", "of": "",           "nationality": "Redania", "race": "Human",    "gender": "Male"},
        {"name": "Zoltan",    "of": "",           "nationality": "Mahakam", "race": "Dwarf",    "gender": "Male"},
        {"name": "Renfri",    "of": "",           "nationality": "Creyden", "race": "Human",    "gender": "Female"},
        {"name": "Yennefer",  "of": "Vengerberg", "nationality": "Aedirn",  "race": "Quadroon", "gender": "Female"},
        {"name": "Cirilla",   "of": "",           "nationality": "Cintra",  "race": "Human",    "gender": "Female"},
    ]

    # Define a table configuration
    _columns = {
        # Header : (Column Name, Width, Alignment)
        "name": ("Name", 10, " <"),
        "of": ("Of", 10, " <"),
        "nationality": ("Nationality", 15, " <"),
        "race": ("Race", 10, " <"),
        "gender": ("Gender", 9, " >"),
    }

    # Order the table configuration
    headers = ["name", "of", "nationality", "race", "gender"]
    columns = OrderedDict()
    for header in headers:
        columns[header] = _columns[header]

    # Print the table
    print_header(columns)
    for row in data:
        print_dict(row, columns)
    print_header(columns)
    print()
