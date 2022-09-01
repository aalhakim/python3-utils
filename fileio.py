#!/usr/bin/env python3
""" Common file actions.
"""

# Standard library imports
import os


def read_csv(filepath):
    result = []
    with open(filepath, "r") as rf:
        for i, line in enumerate(rf):
            result.append(line.replace("\n", ""))
    return result


def create_dir(dir_path):
    """Create a directory if it doesn't already exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print("New directory '{}' created.".format(dir_path))
    return dir_path


def create_file(file_path):
    """Create a file if it doesn't already exist."""
    if not os.path.exists(file_path):
        with open(file_path, "wb") as wf:
            pass
        print("New file '{}' created.".format(file_path))
    return file_path
