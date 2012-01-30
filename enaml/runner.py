#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
import optparse
import sys
import types

from enaml import imports, default_toolkit, wx_toolkit, qt_toolkit
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


toolkits = {
    'default': default_toolkit, 'wx': wx_toolkit, 'qt': qt_toolkit,
}


def main():
    usage = 'usage: %prog [options] enaml_file'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.add_option('-c', '--component', default='Main',
                      help='The component to view')
    parser.add_option('-t', '--toolkit', default='default',
                      choices=['default', 'wx', 'qt'],
                      help='The toolkit backend to use')
    
    options, args = parser.parse_args()

    if len(args) == 0:
        print 'No .enaml file specified'
        sys.exit()
    elif len(args) > 1:
        print 'Too many files specified'
        sys.exit()
    else:
        enaml_file = args[0]

    with open(enaml_file) as f:
        enaml_code = f.read()
    
    # Parse and compile the Enaml source into a code object    
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    module = types.ModuleType('__main__')
    module.__file__ = enaml_file
    ns = module.__dict__

    with imports():
        exec code in ns

    with toolkits[options.toolkit]():
        requested = options.component
        if requested in ns:
            component = ns[requested]
            window = component()
            window.show()
        elif 'main' in ns:
            ns['main']()
        else:
            msg = "Could not find component '%s'" % options.component
            print msg


if __name__ == '__main__':
    main()

