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
import warnings

from enaml import imports
from enaml.application import Application
from enaml.session import Session
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.qt.qt_local_server import QtLocalServer


def prepare_toolkit(toolkit_option):
    """ Prepares the toolkit to be used by enaml.

    The function creates the enaml toolkit and sets if necessary the
    value of ETS_TOOLKIT. ETS gui components default to WX when ETS_TOOLKIT
    is not defined, while enaml defaults to Qt. In that case we set the
    ETS_TOOLKIT enviroment for the process and it's childern to make sure
    that ets amd enaml will use the same toolkit at all times.

    If the ETS_TOOLKIT is already set a warning is raised if there is
    an incompatibility with the -t option.

    Parameters
    ----------
    toolkit_option : str
        The toolkit option provided to the enaml-run script

    Returns
    -------
    enaml_toolkit : ~enaml.core.toolkit.Toolkit
       The enaml toolkit object to be used.

    """

    # NOTE: This function is not currently used
    # the toolkit is assumed to be Qt for the time being

    # TODO: These two defines have been moved here from global scope
    # since the imports do not currently work. They will need to be
    # restored when more than just Qt is supported
    from enaml import default_toolkit, wx_toolkit, qt_toolkit
    # Acceptable enaml toolkit options for enaml-run
    ENAML_TOOLKITS = {
        'default': default_toolkit, 'wx': wx_toolkit, 'qt': qt_toolkit
    }

    # Mapping of the --toolkit option to the ETS_TOOLKIT value
    OPTION_TO_ETS = {'default': 'qt4', 'wx': 'wx', 'qt': 'qt4'}



    enaml_toolkit = ENAML_TOOLKITS[toolkit_option]

    try:
        ets_toolkit = os.environ['ETS_TOOLKIT'].lower().split('.')[0]
    except KeyError:
        compatible_toolkit = OPTION_TO_ETS[toolkit_option]
        os.environ['ETS_TOOLKIT'] = compatible_toolkit
    else:
        # if the -t option is 'default' then enaml obeys ETS_TOOLKIT
        # so there is no incompatibility.
        if toolkit_option != 'default':
            if ets_toolkit != OPTION_TO_ETS[toolkit_option]:
                msg = ('The --toolkit option is different from the '
                       'ETS_TOOLKIT enviroment variable which can '
                       'cause issues if enable or chaco components '
                       'are used.')
                warnings.warn(msg)

    return enaml_toolkit()

class MainSession(Session):
    """ Create a session using the provided component as the view
    
    """
    
    def initialize(self, component):
        self.component = component

    def on_open(self):
        return self.component()


def main():
    usage = 'usage: %prog [options] enaml_file [script arguments]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.allow_interspersed_args = False
    parser.add_option('-c', '--component', default='Main',
                      help='The component to view')

    options, args = parser.parse_args()

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

    requested = options.component
    if requested in ns:
        component = ns[requested]
        handler = MainSession.create_handler(
            name=requested,
            description='Enaml-run "%s" view' % requested,
            component=component,
        )

        app = Application([handler])
        
        server = QtLocalServer(app)
        client = server.local_client()
        
        client.start_session(requested)
        server.start()
        
    elif 'main' in ns:
        ns['main']()
    else:
        msg = "Could not find component '%s'" % options.component
        print msg


if __name__ == '__main__':
    main()
