#!/usr/bin/env python3
"""
FastTargetPred - Fast target prediction tool for molecular compounds.

This is the new entry point that provides a more modern interface
and supports both SDF files and SMILES strings as input.
"""

__version__ = "2.0.0"

import sys
import time

# Check Python version using modern syntax
if sys.version_info < (3, 8):
    print(
        "This program requires Python 3.8 or higher. Please upgrade your Python version."
    )
    sys.exit(1)

# Local packages
from . import texts
from .misc import system_verification, clean_up
from .workflow import start


def main() -> None:
    """Main entry point for FastTargetPred."""
    print(texts.app_header.format(__version__))
    print(texts.check_system, end="")
    system_ok, messages = system_verification()
    if system_ok:
        print(texts.checked)
        start()
    else:
        print(texts.system_not_ok + "\n\t".join(messages))
    clean_up()


if __name__ == "__main__":
    begin_time = time.time()
    main()
    end_time = time.time()
    print(f"Elapsed time for the entire script: {end_time - begin_time:.2f} seconds.")
