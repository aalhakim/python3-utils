#!/usr/bin/env python3

"""
Linux command line actions
"""

# Standard library import
import subprocess as sp

# Local library import
from consoleprinter import dprint


########################################################################
def send_command(cmd, format="str", debug=False):
    """Send shell command and return the response.

    Arguments:
        cmd {str} -- Shell command being submitted.

    Keyword Arguments:
        format {str} -- 'str' or 'list' to indicated returned data format. (default: {"str"})
        debug {bool} -- Set True to display additional debug information. (default: {False})

    Returns:
        (str|[str], bool) -- Tuple of (response, is_error). The response
        is either a string or a list of strings depending on what was
        passed by the `format` argument.

    """
    is_error = False
    try:
        response = sp.check_output(cmd, shell=True, sterr=sp.STDOUT).decode("utf-8")
    except sp.CalledProcessError as err:
        response = err.output.decode("utf-8")
        is_error = True
    response = response.strip()

    if debug is True:
        dprint("DEBUG", f"CMD {cmd}".rstrip())
        dprint("DEBUG", f"OUT: {response}".rstrip())

    if format == "list":
        response = [line for line in response.split("\n") if line != ""]

    return (response, is_error)
