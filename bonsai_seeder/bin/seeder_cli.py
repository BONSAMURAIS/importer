#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic executable.

This documentation defines how the program is run; see http://docopt.org/.

Commands:

Usage:

Options:

"""

from docopt import docopt
from bonsai_seeder.loader import Loader

import argparse
import sys


def main():
    try:
        # @Chris what is this used for?
        # args = docopt(__doc__, version='Version number for *this* CLI')

        parser = argparse.ArgumentParser(description='Sync RDF to http://db.bonsai.uno')
        parser.add_argument('-i','--import', nargs='+',
                            dest='ifiles',
                            help='list of files to read')

        parser.add_argument('--clean', dest='clean', action='store_true',
                            help='Clean: delete triples that are not in a named graph')

        parser.add_argument('--delete', nargs='+',
                            dest='delete',
                            help='Delete the specified named graph')

        args = parser.parse_args()

        loader = Loader()

        if args.clean:
            success, message = loader.clean()
            if success:
                print("Cleaned triples not stored in named graphs")
            else :
                print("Error. Aborting", file=sys.stderr)
                print(message, file=sys.stderr)
                sys.exit(2)

        if args.ifiles is not None:
            for ifile in args.ifiles:
                if not loader.load(ifile):
                    print("Error. Aborting", file=sys.stderr)
                    sys.exit(2)

        if args.delete is not None:
            for uri in  args.delete:
                print("Deleting <{}>".format(uri))
                if not loader.delete(uri):
                    print("Error. Aborting", file=sys.stderr)
                    sys.exit(2)

        print("Completed")


    except KeyboardInterrupt:
        print("Terminating CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
