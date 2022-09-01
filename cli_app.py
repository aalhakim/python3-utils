#!/usr/bin/env python3

"""
CLI Application Base Class

Adds a simple base class to create and run a simple looping command
line application with options to run different actions based on user
input.
"""
# Standard library imports
import traceback

# Local library imports
from consoleprinter import dprint


########################################################################
class CommandInUseError(Exception):
    """New option uses a command string already in use."""


class CliAppIgnoreError(Exception):
    """Error which is caught and ignored by the CLI app."""


########################################################################
class CliApp(object):
    """Base class to create a looped command-line application."""

    quit = False

    def __init__(self):
        """Constructor for CliApp."""
        self.menu = {}
        self.display_order = []
        self.add_option("q", "Quit application", self.stop)

    def add_option(self, cmd, desc, func, argnames=[], override=False):
        """Add new command option to app.

        Arguments:
            cmd {str} -- The string a user must submit to call this option.
            desc {str} -- A brief explanation about what this option does.
            func {func} -- The function to be called.

        Keyword Arguments:
            argnames {list<str>} -- Names of arguments required by
                func and which will be displayed in the description.
                (default: {[]})
            override {bool} -- Set to True to override an option
                using the same command string. (default: {False})
        """
        # Sanitise the command
        cmd = cmd.upper().strip()

        # Check if the command ios already in use
        cmd_is_used = cmd in self.menu.keys()
        if cmd_is_used and override is False:
            raise CommandInUseError(
                "Command already in use. Pass in argument override=True to "
                + f" override the command:\n  {cmd} -- {self.menu[cmd]['desc']}"
            )

        elif cmd_is_used:
            self.display_order.remove(cmd)

        # Add the new command
        self.menu[cmd] = {"func": func, "desc": desc, "args": argnames}

        # Update the display order list
        self.display_order.append(cmd)

    def print_menu(self):
        """Display list of command options and their descriptions."""
        # Process argument fields
        arg_list = {}
        for key, val in self.menu.items():
            arg_list[key] = ""
            for arg in val["args"]:
                arg_list[key] += f"<{arg}> "
            arg_list[key].strip()  # Remove extra whitespace

        for cmd in self.display_order:
            desc = self.menu[cmd]["desc"]
            dprint("MENU", f"{cmd} {arg_list[cmd]} -- {desc}")

    def stop(self):
        """Stop the application loop."""
        self.quit = True

    def start(self, sort_menu=False):
        """Start the application loop.

        Keyword Arguments:
            sort_menu {bool} -- Set True to sort the menu, else the
                menu will be displayed in the order the options were
                added. (default: {False})
        """
        if sort_menu is True:
            self.display_order.sort()

        while self.quit is False:
            self.print_menu()
            user_input = input("Choose an options: ").strip()

            if user_input == "":
                continue

            inputs = user_input.split()
            cmd = inputs[0].upper()
            args = inputs[1:]

            if cmd in self.menu.keys():
                try:
                    self.menu[cmd]["func"](*args)
                except CliAppIgnoreError:
                    pass
                except TypeError as err:
                    # Unknown TypeError which should be re-raised.
                    if "positional argument" not in str(err):
                        raise
                    # Wrong number of arguments passed to called function.
                    dprint("ERROR", f"{str(err)}: {args}")
                except KeyboardInterrupt:
                    self.stop()
                except Exception as err:
                    traceback.print_tb(err.__traceback__)
                    print(err)
                    self.stop()

            print()  # Print end-loop newline.


########################################################################
# --- Example Use Case
########################################################################

if __name__ == "__main__":

    import random

    # Example functions
    def get_dinner(food):
        dprint("", f"You recieve a {food}.")

    def get_fish():
        adj = random.choice(["blue", "green", "red", "yellow", "rainbow"])
        return f"{adj}-fish"

    # Create an instance of CliApp
    app = CliApp()

    # Add a command option which accepts 1 argument
    app.add_option("1", "What do you want to eat?", get_dinner, ["food"])

    # Add a command option which calls a lambda function. This is useful
    # when trying to call a functioun with a pre-defined argument. In
    # this case you will recieve a potato dinner for cmd="2".
    app.add_option("2", "Get random dinner", lambda: get_dinner(get_fish()))

    # Override an existing command using the override=True argument.
    app.add_option("Q", "Do nothing", lambda: 1, override=True)
    app.add_option("E", "Exit application", app.stop)

    # Start the application.
    # Choose to sort the menu else the order in which you called the
    # app.add_option method will be used.
    app.start(sort_menu=True)
