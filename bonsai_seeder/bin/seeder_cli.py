#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic executable.

This documentation defines how the program is run; see http://docopt.org/.

Commands:

Usage:

Options:

"""

from docopt import docopt
from bonsai_seeder.loader import Loader, ACTION_CONTINUE, ACTION_DELETE, ACTION_SKIP

import argparse
import glob
import sys
import os



def main():
    try:
        # @Chris what is this used for?
        # args = docopt(__doc__, version='Version number for *this* CLI')

        parser = argparse.ArgumentParser(description="Sync RDF to some remote jena/fuseki server\nRequires config.ini file")
        parser.add_argument('-i','--import', nargs='+',
                            dest='ifiles',
                            help='list of files to read')

        parser.add_argument('--ifexists',
                            choices=('skip', 'delete', 'continue'),
                            default='skip',
                            dest='mode',
                            help='What to do in case data is already present')


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
            ifexists = ACTION_SKIP
            if args.mode == 'continue' :
                ifexists = ACTION_CONTINUE
            if args.mode == 'delete' :
                ifexists = ACTION_DELETE

            targets = []
            while len(args.ifiles) > 0:
                path = args.ifiles.pop(0)
                if os.path.isfile(path):
                    targets.add(path)
                elif os.path.isdir(path):
                    args.ifiles += glob.glob(path + '/*')
                else :
                    args.ifiles += glob.glob(path)

            for ifile in targets:
                response, msg = loader.load(ifile, ifexists)
                if not response:
                    print("Error {} . Aborting".format(msg), file=sys.stderr)
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
