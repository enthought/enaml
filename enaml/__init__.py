#-----------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def test_collector():
    """ Discover and collect tests for the Enaml Package.

        .. note :: addapted from the unittest2
    """
    import os
    import sys
    from unittest import TestLoader

    # import __main__ triggers code re-execution
    __main__ = sys.modules['__main__']
    setupDir = os.path.abspath(os.path.dirname(__main__.__file__))

    return TestLoader().discover(setupDir)


class imports(object):
    """ A context manager that hooks/unhooks the enaml meta path
    importer for the duration of the block. The helps user avoid
    unintended consequences of a having a meta path importer slow
    down all of their other imports.

    """
    def __enter__(self):
        from .import_hooks import EnamlImporter
        EnamlImporter.install()
    
    def __exit__(self, *args, **kwargs):
        from .import_hooks import EnamlImporter
        EnamlImporter.uninstall()
