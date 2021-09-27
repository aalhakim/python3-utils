# Standard library imports
import sys
import os

# Add parent directory to sys.path to allow example code to import
# modules placed higher up in the directory hierarchy.
repo = os.path.dirname(__file__)
pkg_dir = __file__[0 : __file__.find(repo) + len(repo)]
sys.path.append(pkg_dir)
