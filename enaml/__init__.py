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
    #: The framework-wide importers in use. The None will be 
    #: replaced with the default importer upon first use in 
    #: order to avoid a circular import.
    __importers = [None]

    @classmethod
    def get_importers(cls):
        """ Returns the currently active importers in use for the 
        framework.

        """
        importers = cls.__importers
        if importers[0] is None:
            # This avoid a circular import between the compiler, this
            # module, and the import hooks, and makes sure we always
            # have at least one importer . 
            from .import_hooks import EnamlImporter
            importers[0] = EnamlImporter
        return importers

    @classmethod
    def append_importer(cls, importer):
        """ Appends an importer to the list of importers for use with 
        the framework. It must be a subclass of AbstractEnamlImporter.
        The most recently appended importer is used first when 
        attempting to import.

        """
        # This avoid a circular import between the compiler, this
        # module, and the import hooks.
        from .import_hooks import AbstractEnamlImporter
        if not issubclass(importer, AbstractEnamlImporter):
            msg = ('An Enaml importer must be a subclass of '
                   'AbstractEnamlImporter. Got %s instead.')
            raise TypeError(msg % importer)
        cls.__importers.append(importer)
    
    @classmethod
    def remove_importer(cls, importer):
        """ Removes the importer from the list of active importers. 
        If the importer is not in the list, this is a no-op.

        """
        importers = cls.__importers
        if importer in importers:
            importers.remove(importer)

    def __init__(self):
        """ Initializes an Enaml import context.

        """
        # We create a copy of the importers list, so can make sure
        # to uninstall them at the end of the context, even if 
        # they were removed from the importers list during operation.
        self.importers = list(self.get_importers())

    def __enter__(self):
        """ Installs the current importer upon entering the context.

        """
        # Install the importers reversed so that the newest ones 
        # get first crack at the import on sys.meta_path.
        for importer in reversed(self.importers):
            importer.install()
    
    def __exit__(self, *args, **kwargs):
        """ Uninstalls the current importer when leaving the context.

        """
        # We removed in standard order since thats a more efficient
        # operation on sys.meta_path.
        for importer in self.importers:
            importer.uninstall()

