#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Atom


class Resource(Atom):
    """ A base class to use for creating resource objects.

    """
    def class_name(self):
        """ Get the class name of this resource.

        """
        return type(self).__name__

    def base_names(self):
        """ Get the base class names of this resource.

        """
        names = []
        for base in type(self).mro()[1:]:
            if base is Resource:
                names.append(base.__name__)
                break
            names.append(base.__name__)
        return names

    def snapshot(self):
        """ Get a snapshot dictionary for this resource.

        Subclass should reimplement this method to add more metadata
        to the snapshot dictionary.

        """
        return {'class': self.class_name(), 'bases': self.base_names()}

