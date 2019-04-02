#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic executable.

This documentation defines how the program is run; see http://docopt.org/.

Commands:

Usage:

Options:

"""

from docopt import docopt
from bonsai_seeder.loader import load

import argparse
import sys


def main():
    try:
        # @Chris what is this used for?
        # args = docopt(__doc__, version='Version number for *this* CLI')

        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('-i','--import', nargs='+',
                            dest='ifiles',
                            help='<Required> list of files to read', required=True)

        args = parser.parse_args()

        for ifile in args.ifiles:
            load(ifile)


    except KeyboardInterrupt:
        print("Terminating CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
