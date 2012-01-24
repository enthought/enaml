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
    #: The framework-wide importer in use for importing Enaml modules
    __importer = None

    @classmethod
    def get_importer(cls):
        """ Returns the currently active importer in use for the 
        framework.

        """
        importer = cls.__importer
        if importer is None:
            # This avoid a circular import between the compiler, this
            # module, and the import hooks.
            from .import_hooks import EnamlImporter
            cls.__importer = importer = EnamlImporter
        return importer

    @classmethod
    def set_importer(cls, importer):
        """ Sets the framework-wide importer to use for importing
        Enaml modules. It must be a subclass of AbstractEnamlImporter.

        """
        # This avoid a circular import between the compiler, this
        # module, and the import hooks.
        from .import_hooks import AbstractEnamlImporter
        if not issubclass(importer, AbstractEnamlImporter):
            msg = ('An Enaml importer must be a subclass of '
                   'AbstractEnamlImporter. Got %s instead.')
            raise TypeError(msg % importer)
        cls.__importer = importer
    
    @classmethod
    def reset_importer(cls):
        """ Resets any custom installed enaml importer to the default.

        """
        cls.__importer = None

    def __init__(self):
        """ Initializes an Enaml import context.

        """
        self.importer = self.get_importer()

    def __enter__(self):
        """ Installs the current importer upon entering the context.

        """
        self.importer.install()
    
    def __exit__(self, *args, **kwargs):
        """ Uninstalls the current importer when leaving the context.

        """
        self.importer.uninstall()

