#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Command-line tool to run .enaml files.
"""

import enaml
from enaml.parsing.parser import parse
from enaml.parsing.enaml_compiler import EnamlCompiler


def main():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__,
    )
    parser.add_argument('-c', '--component', default='MainWindow',
        help="The component to view.")
    parser.add_argument('enaml_file', help='The .enaml file to show.')

    args = parser.parse_args()

    with open(args.enaml_file) as f:
        enaml_code = f.read()
    ast = parse(enaml_code)
    ns = {}

    with enaml.imports():
        EnamlCompiler.compile(ast, ns)
    component = ns[args.component]
    window = component()
    window.show()

if __name__ == '__main__':
    main()

