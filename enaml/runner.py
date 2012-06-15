#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Command-line tool to run .enaml files.

"""
import optparse
import os
import sys
import types

from enaml import imports, default_toolkit, wx_toolkit, qt_toolkit
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


# Acceptable enaml toolkit options for enaml-run
ENAML_TOOLKITS = {
    'default': default_toolkit, 'wx': wx_toolkit, 'qt': qt_toolkit,
    'qt.agg': qt_toolkit}

# Mapping of enaml toolkits to the ETS_TOOLKIT value
ENAML_TO_ETS = {'default': 'qt4', 'wx': 'wx', 'qt': 'qt4','qt.agg': 'qt4.agg'}

# Resulting ETS_TOOLKIT value when combining the original ETS_TOOLKIT value
# with the toolkit that enaml is going to use. Enaml alsways wins, but
# the kiva backend ussualy survives.
TOOLKIT_COMBINATIONS = {
    ('wx','default'): 'wx',
    ('wx','qt'): 'qt4',
    ('wx','qt.agg'): 'qt4.agg',
    ('wx','wx'): 'wx',
    ('qt4','default'): 'qt4',
    ('qt4','qt'): 'qt4',
    ('qt4','qt.agg'): 'qt4.agg',
    ('qt4','wx'): 'wx',
    ('qt4.agg','default'): 'qt4.agg',
    ('qt4.agg','qt'): 'qt4.agg',
    ('qt4.agg','qt.agg'): 'qt4.agg',
    ('qt4.agg','wx'): 'wx',
}

def set_common_toolkit(toolkit_option):
    """ Set the ETS_TOOLKIT variable for the ets ui components.

    ETS gui components default to WX while enaml defaults to WX
    We set the ETS_TOOLKIT enviroment for the process and it's childern
    to make sure that ets amd enaml will use the same toolkit at all times.

    """
    if os.environ.has_key('ETS_TOOLKIT'):
        ets_toolkit = os.environ.get('ETS_TOOLKIT').lower()
        # Depending on the toolkit option we might need to override
        toolkit_name = TOOLKIT_COMBINATIONS[(ets_toolkit,toolkit_option)]
    else:
        toolkit_name = ENAML_TO_ETS[toolkit_option]
    os.environ['ETS_TOOLKIT'] = toolkit_name

def main():
    usage = 'usage: %prog [options] enaml_file [script arguments]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.allow_interspersed_args = False
    parser.add_option('-c', '--component', default='Main',
                      help='The component to view')
    parser.add_option('-t', '--toolkit', default='default',
                      choices=['default', 'wx', 'qt'],
                      help='The toolkit backend to use')

    options, args = parser.parse_args()


    # Preapare the toolkit
    toolkit = ENAML_TOOLKITS[options.toolkit]
    set_common_toolkit(options.toolkit)

    if len(args) == 0:
        print 'No .enaml file specified'
        sys.exit()
    else:
        enaml_file = args[0]
        script_argv = args[1:]

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

    # Put the directory of the Enaml file first in the path so relative imports
    # can work.
    sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
    # Bung in the command line arguments.
    sys.argv = [enaml_file] + script_argv
    with imports():
        exec code in ns

    with toolkit():
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

