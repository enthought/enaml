#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
import argparse

import enaml
from enaml.parsing.parser import parse
from enaml.parsing.enaml_compiler import EnamlCompiler
from enaml.toolkit import default_toolkit, wx_toolkit, qt_toolkit


toolkits = {
    'default': default_toolkit, 'wx': wx_toolkit, 'qt': qt_toolkit,
}


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__,
    )
    parser.add_argument('-c', '--component', default='Main',
        help="The component to view.")
    parser.add_argument('-t', '--toolkit', default='default',
        choices=['default', 'wx', 'qt'],
        help='The toolkit backend to use')
    parser.add_argument('enaml_file', help='The .enaml file to show.')

    args = parser.parse_args()

    with open(args.enaml_file) as f:
        enaml_code = f.read()
    ast = parse(enaml_code, filename=args.enaml_file)
    ns = {}

    with enaml.imports():
        EnamlCompiler.compile(ast, ns)

    with toolkits[args.toolkit]():
        requested = args.component
        if requested in ns:
            component = ns[requested]
            window = component()
            window.show()
        elif 'main' in ns:
            ns['main']()
        else:
            msg = "Could not find component '%s'" % args.component
            print msg

if __name__ == '__main__':
    main()
